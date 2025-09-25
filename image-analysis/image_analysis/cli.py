"""Typer CLI for the image analysis pipeline."""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import shutil
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Optional

import typer
from openai import OpenAI
from sqlalchemy.orm import Session

from .db import Analysis, Evidence, init_session_factory
from .models import (
    AnalysisModelInfo,
    AnalysisParameters,
    AnalysisRecord,
    AnalysisOutputs,
    ChainOfCustodyEntry,
    EvidenceBundle,
    EvidenceCore,
)
from .paths import Layout
from .utils import (
    append_json_lines,
    compute_phash,
    ensure_directory,
    load_exif,
    now_utc,
    read_dimensions,
    sha256_bytes,
    to_naive_utc,
    write_json,
)

app = typer.Typer(help="Content-addressed evidence ingestion and analysis toolkit.")

DEFAULT_MODEL = os.environ.get("EVIDENCE_TOOLKIT_MODEL", "gpt-4.1-mini")
DEFAULT_MODEL_REVISION = os.environ.get("EVIDENCE_TOOLKIT_MODEL_REVISION", "2025-09-10")
TEMPERATURE = 0.0

layout = Layout(Path.cwd())
_SESSION_FACTORY = None
_CLIENT = None


def get_session_factory():
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        ensure_layout_directories()
        _SESSION_FACTORY = init_session_factory(layout.db)
    return _SESSION_FACTORY


def get_client():
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = OpenAI()
    return _CLIENT


def log_event(message: str, **extra):
    """Append a structured log entry."""

    record = {"ts": now_utc().isoformat(), "message": message, **extra}
    append_json_lines(layout.logs / "app.log", [record])


def prompt_template() -> str:
    return (
        "You are assisting a legal evidence analyst. Examine the IMAGE and provide factual,"
        " non-speculative observations. Output JSON only with keys: summary, objects,"
        " text_found, risk_flags, confidence_overall. Objects is a list of"
        " {label, bbox, confidence} with bbox as [x,y,width,height] normalized between 0 and 1."
        " If text is unclear, reflect uncertainty in confidence and add appropriate risk_flags."
    )


def load_chain(path: Path) -> list[dict]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def save_chain(path: Path, entries: list[dict]) -> None:
    write_json(path, entries)


def ensure_layout_directories() -> None:
    for directory in [layout.raw, layout.derived, layout.labels, layout.db.parent, layout.logs]:
        ensure_directory(directory)


def guess_mime_type(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or "application/octet-stream"


def build_analysis_id(sha: str, prompt_hash: str, revision: str) -> str:
    return f"{sha}-{prompt_hash[:8]}-{revision}"


ALLOWED_RISK_FLAGS = {
    "low_quality",
    "tampering_suspected",
    "ocr_ambiguous",
    "nsfw",
    "pii",
}


def normalize_text_found(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        return "\n".join(str(item) for item in value if item is not None)
    return None


def normalize_risk_flags(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        candidates = [value]
    elif isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        candidates = list(value)
    else:
        candidates = []

    normalized: list[str] = []
    for raw in candidates:
        if not isinstance(raw, str):
            continue
        token = raw.strip().lower().replace(" ", "_")
        if token in ALLOWED_RISK_FLAGS:
            normalized.append(token)
            continue
        if "uncertain" in token or "text" in token:
            normalized.append("ocr_ambiguous")
        elif "stain" in token or "tamper" in token or "damage" in token:
            normalized.append("tampering_suspected")
        elif "blur" in token or "low" in token or "noise" in token:
            normalized.append("low_quality")

    seen: set[str] = set()
    deduped: list[str] = []
    for item in normalized:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def call_openai(image_path: Path, prompt: str, model: str, temperature: float) -> Any:
    mime_type = guess_mime_type(image_path)
    image_bytes = image_path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("ascii")
    data_url = f"data:{mime_type};base64,{encoded}"
    content = [
        {"type": "input_text", "text": prompt},
        {"type": "input_image", "image_url": data_url, "detail": "auto"},
    ]
    client = get_client()
    return client.responses.create(
        model=model,
        input=[{"role": "user", "content": content}],
        text={"format": {"type": "json_object"}},
        temperature=temperature,
    )


@app.command()
def ingest(
    images_dir: Path = typer.Argument(Path("./inbox/"), exists=True, file_okay=False, dir_okay=True, help="Directory containing images to ingest (default: ./inbox/)"),
    case_id: Optional[str] = typer.Option(None, help="Case identifier to associate with the evidence."),
    actor: str = typer.Option("system@app", help="Actor recorded in chain-of-custody events."),
):
    """Ingest images, compute hashes/metadata, and stage for analysis."""

    ensure_layout_directories()
    session = get_session_factory()()
    processed = 0
    skipped = 0
    try:
        # Supported image extensions
        IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif'}

        for file_path in images_dir.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip non-image files
            ext = file_path.suffix.lower()
            if ext not in IMAGE_EXTENSIONS:
                continue

            contents = file_path.read_bytes()
            sha = sha256_bytes(contents)
            raw_dir, derived_dir, raw_file = layout.content_paths(sha, ext)
            ensure_directory(raw_dir)
            ensure_directory(derived_dir)

            if not raw_file.exists():
                shutil.copy2(file_path, raw_file)
            else:
                skipped += 1

            width, height = read_dimensions(raw_file)
            exif = load_exif(raw_file)
            perceptual_hash = compute_phash(raw_file)
            write_json(derived_dir / "exif.json", exif)
            (derived_dir / "phash.txt").write_text(perceptual_hash)

            evidence = session.get(Evidence, sha)
            now = now_utc()
            if not evidence:
                evidence = Evidence(
                    sha256=sha,
                    case_id=case_id,
                    original_ext=raw_file.suffix,
                    original_bytes=len(contents),
                    phash=perceptual_hash,
                    exif_json=exif,
                    added_at=to_naive_utc(now),
                    path=str(raw_file),
                )
            else:
                if case_id and evidence.case_id != case_id:
                    evidence.case_id = case_id
                evidence.original_ext = raw_file.suffix
                evidence.original_bytes = len(contents)
                evidence.phash = perceptual_hash
                evidence.exif_json = exif

            session.merge(evidence)
            session.flush()

            metadata = {
                "sha256": sha,
                "bytes": len(contents),
                "width_px": width,
                "height_px": height,
                "mime_type": guess_mime_type(raw_file),
                "phash": perceptual_hash,
                "ingested_at": evidence.added_at.replace(tzinfo=None).isoformat() + "Z",
                "source_path": str(raw_file),
                "case_id": case_id,
            }
            write_json(derived_dir / "metadata.json", metadata)

            custody_path = derived_dir / "chain_of_custody.json"
            chain = load_chain(custody_path)
            if not chain:
                chain.append(
                    ChainOfCustodyEntry(
                        ts=now,
                        actor=actor,
                        action="ingest",
                        note=str(file_path),
                    ).model_dump(mode="json", exclude_none=True)
                )
                save_chain(custody_path, chain)

            processed += 1
            log_event("ingest", sha256=sha, case_id=case_id, path=str(raw_file))

        session.commit()
    finally:
        session.close()

    typer.echo(f"Ingest complete. processed={processed} skipped={skipped}")


def process_analysis(sha256_hex: str, model: str, revision: str, actor: str) -> str:
    """Internal helper that runs analysis for a single evidence hash."""

    ensure_layout_directories()
    session: Session = get_session_factory()()
    try:
        evidence = session.get(Evidence, sha256_hex)
        if not evidence:
            raise typer.BadParameter("Unknown sha256; run ingest first")

        raw_path = Path(evidence.path)
        if not raw_path.exists():
            raise typer.BadParameter(f"Raw file missing at {raw_path}")

        derived_dir = layout.derived / f"sha256={sha256_hex}"
        metadata_path = derived_dir / "metadata.json"
        if not metadata_path.exists():
            raise typer.BadParameter("metadata.json missing; re-run ingest")

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        prompt = prompt_template()
        prompt_hash = sha256(prompt.encode("utf-8")).hexdigest()
        response = call_openai(raw_path, prompt, model, TEMPERATURE)

        payload = response.model_dump()
        output_content = response.output[0].content[0].text if response.output else "{}"
        try:
            parsed = json.loads(output_content)
        except json.JSONDecodeError as exc:
            raise typer.BadParameter(f"Model returned invalid JSON: {exc}") from exc

        analysis_id = build_analysis_id(sha256_hex, prompt_hash, revision)
        created_at = now_utc()

        outputs_payload = parsed.get("outputs")
        if isinstance(outputs_payload, dict):
            outputs_data = outputs_payload
        else:
            outputs_data = {
                key: parsed.get(key)
                for key in ["summary", "objects", "text_found", "risk_flags"]
            }
        if "text_found" in outputs_data:
            outputs_data["text_found"] = normalize_text_found(outputs_data.get("text_found"))
        if "risk_flags" in outputs_data:
            outputs_data["risk_flags"] = normalize_risk_flags(outputs_data.get("risk_flags"))
        outputs_clean = {k: v for k, v in outputs_data.items() if v is not None}
        outputs = AnalysisOutputs(**outputs_clean)

        confidence_value = parsed.get("confidence_overall")
        if confidence_value is None and isinstance(outputs_payload, dict):
            confidence_value = outputs_payload.get("confidence_overall")
        if confidence_value is None:
            confidence_value = 0.0

        analysis_record = AnalysisRecord(
            analysis_id=analysis_id,
            created_at=created_at,
            model=AnalysisModelInfo(name=model, revision=revision),
            parameters=AnalysisParameters(
                temperature=TEMPERATURE,
                prompt_hash=prompt_hash,
                token_usage_in=payload.get("usage", {}).get("input_tokens"),
                token_usage_out=payload.get("usage", {}).get("output_tokens"),
            ),
            outputs=outputs,
            confidence_overall=float(confidence_value),
        )

        custody_path = derived_dir / "chain_of_custody.json"
        chain = load_chain(custody_path)
        chain.append(
            ChainOfCustodyEntry(
                ts=created_at,
                actor=actor,
                action="analysis",
                note=f"model={model}",
            ).model_dump(mode="json", exclude_none=True)
        )
        save_chain(custody_path, chain)

        bundle = EvidenceBundle(
            case_id=evidence.case_id,
            evidence=EvidenceCore(
                evidence_id=sha256_hex,
                sha256=sha256_hex,
                mime_type=metadata.get("mime_type", "application/octet-stream"),
                bytes=metadata.get("bytes", raw_path.stat().st_size),
                width_px=metadata.get("width_px"),
                height_px=metadata.get("height_px"),
                phash=metadata.get("phash"),
                ingested_at=evidence.added_at,
                source_path=str(raw_path),
            ),
            chain_of_custody=[ChainOfCustodyEntry(**entry) for entry in chain],
            analyses=[analysis_record],
        )

        write_json(derived_dir / "openai.v1.json", payload)
        write_json(derived_dir / "analysis.v1.json", bundle.model_dump(mode="json", exclude_none=True))

        session.add(
            Analysis(
                sha256=sha256_hex,
                created_at=to_naive_utc(created_at),
                model=model,
                model_revision=revision,
                prompt=prompt,
                prompt_hash=prompt_hash,
                response_raw=payload,
                analysis_json=bundle.model_dump(mode="json", exclude_none=True),
                tokens_input=analysis_record.parameters.token_usage_in,
                tokens_output=analysis_record.parameters.token_usage_out,
                temperature=TEMPERATURE,
            )
        )
        session.commit()

        labels = {obj.label for obj in analysis_record.outputs.objects if obj.label}
        for label in list(labels)[:3]:
            target = layout.labels / label / f"{sha256_hex}{raw_path.suffix}"
            ensure_directory(target.parent)
            if not target.exists():
                try:
                    os.link(raw_path, target)
                except OSError:
                    shutil.copy2(raw_path, target)

        log_event(
            "analysis",
            sha256=sha256_hex,
            model=model,
            prompt_hash=prompt_hash,
            analysis_id=analysis_id,
        )

        return analysis_id
    finally:
        session.close()


@app.command()
def analyze(
    sha256_hex: str = typer.Argument(..., help="Evidence sha256 identifier."),
    model: str = typer.Option(DEFAULT_MODEL, help="OpenAI model to use."),
    revision: str = typer.Option(DEFAULT_MODEL_REVISION, help="Model revision tag for audit."),
    actor: str = typer.Option("analysis@app", help="Actor recorded in chain-of-custody."),
):
    """Run the OpenAI Responses API analysis for the specified evidence."""

    analysis_id = process_analysis(sha256_hex, model, revision, actor)
    typer.echo(f"Analysis complete: {analysis_id}")


@app.command("analyze-batch")
def analyze_batch(
    limit: Optional[int] = typer.Option(None, help="Process at most this many hashes."),
    model: str = typer.Option(DEFAULT_MODEL, help="OpenAI model to use."),
    revision: str = typer.Option(DEFAULT_MODEL_REVISION, help="Model revision tag for audit."),
    actor: str = typer.Option("analysis@app", help="Actor recorded in chain-of-custody."),
    skip_existing: bool = typer.Option(
        True, "--skip-existing/--no-skip-existing", help="Skip hashes that already have analysis.v1.json."
    ),
    fail_fast: bool = typer.Option(True, help="Stop on first failure."),
):
    """Analyze every staged evidence item (optionally limited to *n* hashes)."""

    ensure_layout_directories()
    derived_root = layout.derived
    if not derived_root.exists():
        typer.echo("No derived evidence directory found; run ingest first.")
        raise typer.Exit(0)

    hashes: list[str] = []
    skipped_existing = 0
    for path in sorted(derived_root.glob("sha256=*")):
        value = path.name.split("=", 1)[-1]
        if skip_existing and (path / "analysis.v1.json").exists():
            skipped_existing += 1
            continue
        hashes.append(value)

    if not hashes:
        typer.echo("Nothing to analyze (all processed or none ingested).")
        raise typer.Exit(0)

    processed = 0
    failures: list[tuple[str, Exception]] = []
    for sha_hex in hashes:
        if limit is not None and processed >= limit:
            break
        try:
            analysis_id = process_analysis(sha_hex, model, revision, actor)
            typer.echo(f"{sha_hex}: ok -> {analysis_id}")
            processed += 1
        except Exception as exc:  # noqa: BLE001 - we handle via fail_fast flag
            failures.append((sha_hex, exc))
            typer.secho(f"{sha_hex}: failed -> {exc}", fg=typer.colors.RED)
            if fail_fast:
                break

    typer.echo(
        f"Batch complete. processed={processed} skipped_existing={skipped_existing} errors={len(failures)}"
    )
    if failures:
        raise typer.Exit(1)


@app.command("export-json")
def export_json(
    sha256_hex: str = typer.Argument(..., help="Evidence sha256 identifier."),
    output: Path = typer.Argument(..., help="File path to write the JSON bundle."),
):
    """Export the validated analysis JSON for external sharing."""

    derived_dir = layout.derived / f"sha256={sha256_hex}"
    bundle_path = derived_dir / "analysis.v1.json"
    if not bundle_path.exists():
        raise typer.BadParameter("analysis.v1.json not found; run analyze first")

    data = json.loads(bundle_path.read_text(encoding="utf-8"))
    ensure_directory(output.parent)
    output.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    typer.echo(f"Wrote {output}")


def run():
    try:
        app()
    except typer.BadParameter as exc:
        typer.secho(f"Error: {exc}", err=True, fg=typer.colors.RED)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    run()
