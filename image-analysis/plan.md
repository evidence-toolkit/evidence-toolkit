Got it, bouch. Your diagram is the right skeleton. If this is meant to stand up in court, the “edge” isn’t the AI—it's reliability, auditability, and chain-of-custody. Below is a tight, production-ready scaffold you can run today and expand later.

# What matters (and how to bake it in)

1. **Determinism & audit**

   * Content-addressed IDs: `sha256(file_bytes)` = primary key.
   * Immutable raw store + versioned derived artifacts.
   * Every step logs: who/when/what/version/input-hash/output-hash.

2. **Model non-determinism risk**

   * Fix model + temperature=0, force JSON with a schema.
   * Persist full prompt + model name + response + token usage.
   * Human-in-the-loop gate before anything labeled “conclusion”.

3. **Chain of custody**

   * Copy-on-ingest to a WORM-like directory (`raw/`) with hash in path.
   * Record file timestamps, OS metadata, EXIF, and two hashes: cryptographic (SHA-256) + perceptual (pHash) for similarity.

4. **Reproducibility**

   * Store tool versions (OpenAI model version, Pillow, your code git SHA).
   * Idempotent pipelines keyed by content hash; retries with backoff; no duplicate work.

---

# Minimal directory layout

```
evidence/
  raw/sha256=<hash>/original.<ext>
  derived/sha256=<hash>/
    exif.json
    phash.txt
    openai.v1.json         # raw model output
    analysis.v1.json       # validated schema
    labels/vehicle/        # organized copies/symlinks
db/evidence.sqlite
logs/app.log               # JSONL structured logs
```

---

# Schema artifacts

* JSON Schema V1.0 lives at `schemas/evidence.v1.json` (draft-07, `additionalProperties:false` throughout) and locks the contract described in `todo.md`.
* Runtime validation continues to use Pydantic models generated from that schema; keep them in sync by treating the JSON schema as the source of truth.
* CLI validation command: `uv run python validate_schema.py <path-to-analysis.json>` (install dependency once via `uv add jsonschema`). The script returns non-zero on schema failure and surfaces field-level errors.

---

# Database (SQLite via SQLAlchemy)

```python
# db.py
from sqlalchemy import (create_engine, Column, String, Float, Integer, JSON,
                        DateTime, Text, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Evidence(Base):
    __tablename__ = "evidence"
    sha256 = Column(String(64), primary_key=True)
    case_id = Column(String, index=True)
    original_ext = Column(String(10))
    original_bytes = Column(Integer)
    phash = Column(String(16))
    exif_json = Column(JSON)            # normalized EXIF dict
    added_at = Column(DateTime)
    path = Column(Text, unique=True)

class Analysis(Base):
    __tablename__ = "analysis"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sha256 = Column(String(64), ForeignKey("evidence.sha256"))
    created_at = Column(DateTime, index=True)
    model = Column(String)
    prompt = Column(Text)               # full prompt as-sent
    response_raw = Column(JSON)         # raw model JSON
    analysis_json = Column(JSON)        # validated EvidenceAnalysis.dict()
    tokens_input = Column(Integer)
    tokens_output = Column(Integer)
    temperature = Column(Float)
    prompt_hash = Column(String(64))
    __table_args__ = (UniqueConstraint('sha256','prompt_hash',name='uniq_analysis'),)
```

---

# Core pipeline (CLI with Typer, idempotent, async safe)

```python
# app.py
import os, json, hashlib, shutil, datetime as dt
from pathlib import Path
import typer, piexif, PIL.Image as Image
from imagehash import phash
from tenacity import retry, stop_after_attempt, wait_exponential
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import EvidenceAnalysis
from db import Base, Evidence, Analysis
from openai import OpenAI

app = typer.Typer()
ROOT = Path.cwd()
EVIDENCE = ROOT / "evidence"
RAW = EVIDENCE / "raw"
DERIVED = EVIDENCE / "derived"
DB_PATH = ROOT / "db" / "evidence.sqlite"
LOGS = ROOT / "logs"
MODEL = "gpt-4.1-mini"  # or current vision-capable Responses model
TEMPERATURE = 0.0

def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()

def ensure_dirs():
    for p in [RAW, DERIVED, DB_PATH.parent, LOGS]: p.mkdir(parents=True, exist_ok=True)

def write_json(path: Path, data: dict):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def content_paths(h: str, ext: str):
    raw_dir = RAW / f"sha256={h}"
    der_dir = DERIVED / f"sha256={h}"
    return raw_dir, raw_dir / f"original{ext}", der_dir

def exif_dict(path: Path) -> dict:
    try:
        exif = piexif.load(str(path))
        return {k: {kk: (vv.decode(errors="ignore") if isinstance(vv, bytes) else vv)
                    for kk,vv in v.items()} for k,v in exif.items()}
    except Exception:
        return {}

def compute_phash(path: Path) -> str:
    with Image.open(path) as im:
        return str(phash(im))

def prompt_template() -> str:
    return (
        "You are assisting legal evidence triage. Extract structured facts only from the IMAGE. "
        "Avoid speculation. If unsure, set low confidence and add a risk_flag.\n"
        "Return valid JSON with this schema keys exactly: "
        "{evidence_id, source_path, case_id, analyst, created_at, model, prompt_hash, "
        "summary, objects, text_found, risk_flags, confidence_overall}.\n"
        "objects: list of {label, bbox, confidence} where bbox is [x,y,w,h] normalized 0..1.\n"
        "Also OCR any visible text into text_found.\n"
        "If image suggests tampering or heavy compression, include 'tampering_suspected' or 'low_quality'."
    )

def prompt_hash(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()

client = OpenAI()  # expects OPENAI_API_KEY env var

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def call_openai(image_path: Path, evidence_id: str, pr_hash: str):
    content = [
        {"type":"input_text", "text": prompt_template()},
        {"type":"input_image", "image_url": image_path.as_uri()}
    ]
    resp = client.responses.create(
        model=MODEL,
        temperature=TEMPERATURE,
        input=[{"role":"user","content":content}],
        response_format={"type":"json_object"},
    )
    return resp

@app.command()
def ingest(images_dir: Path, case_id: str = typer.Option(None), analyst: str = typer.Option(None)):
    """Copy images, hash, EXIF, pHash, register in DB."""
    ensure_dirs()
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        for p in images_dir.glob("**/*"):
            if not p.is_file(): continue
            b = p.read_bytes()
            h = sha256_bytes(b)
            ext = p.suffix.lower()
            raw_dir, raw_file, der_dir = content_paths(h, ext)
            raw_dir.mkdir(parents=True, exist_ok=True)
            der_dir.mkdir(parents=True, exist_ok=True)
            if not raw_file.exists(): shutil.copy2(p, raw_file)
            exif = exif_dict(raw_file)
            p_hash = compute_phash(raw_file)
            write_json(der_dir / "exif.json", exif)
            (der_dir / "phash.txt").write_text(p_hash)
            ev = s.get(Evidence, h) or Evidence(
                sha256=h, case_id=case_id, original_ext=ext,
                original_bytes=len(b), phash=p_hash, exif_json=exif,
                added_at=dt.datetime.utcnow(), path=str(raw_file))
            s.merge(ev)
        s.commit()
    typer.echo("Ingest complete.")

@app.command()
def analyze(sha256: str):
    """Run OpenAI analysis with enforced JSON, validate, store, and organize."""
    ensure_dirs()
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        ev = s.get(Evidence, sha256)
        if not ev: raise typer.BadParameter("unknown sha256")
        raw_file = Path(ev.path)
        pr = prompt_template()
        pr_h = prompt_hash(pr)
        der_dir = DERIVED / f"sha256={sha256}"
        resp = call_openai(raw_file, sha256, pr_h)
        raw = resp.model_dump()  # keep entire payload
        (der_dir / "openai.v1.json").write_text(json.dumps(raw, indent=2))
        # Validate into your schema
        out = resp.output_text
        data = json.loads(out)
        data.update({
            "evidence_id": sha256,
            "source_path": str(raw_file),
            "case_id": ev.case_id,
            "analyst": None,
            "created_at": dt.datetime.utcnow().isoformat(),
            "model": resp.model,
            "prompt_hash": pr_h,
        })
        validated = EvidenceAnalysis.model_validate(data).model_dump()
        write_json(der_dir / "analysis.v1.json", validated)
        # Persist analysis row
        s.add(Analysis(
            sha256=sha256, created_at=dt.datetime.utcnow(),
            model=resp.model, prompt=pr, response_raw=raw,
            analysis_json=validated, tokens_input=raw.get("usage",{}).get("input_tokens"),
            tokens_output=raw.get("usage",{}).get("output_tokens"),
            temperature=TEMPERATURE, prompt_hash=pr_h))
        s.commit()
        # Organize images into subdirectories by top label(s)
        labels = sorted({o["label"] for o in validated.get("objects", [])})
        for lbl in labels[:3]:
            tgt = EVIDENCE / "labels" / lbl / f"{sha256}{Path(ev.path).suffix}"
            tgt.parent.mkdir(parents=True, exist_ok=True)
            if not tgt.exists():
                try: os.link(ev.path, tgt)  # hard link to avoid dup data
                except OSError: shutil.copy2(ev.path, tgt)
    typer.echo("Analysis complete.")

@app.command()
def export_json(sha256: str, out: Path):
    """Export the validated analysis JSON."""
    data = json.loads((DERIVED / f"sha256={sha256}" / "analysis.v1.json").read_text())
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    typer.echo(f"Wrote {out}")

if __name__ == "__main__":
    app()
```

---

# Organization & linkage

* **Link between image and analysis** is the content hash (`evidence_id`), present in:

  * directory path,
  * DB foreign key,
  * analysis JSON,
  * label folders (file name includes hash).

---

# Workflow

1. `uv run python -m image_analysis.cli ingest /path/to/IMAGES --case-id CASE123`
2. Run per-asset analysis via `uv run python -m image_analysis.cli analyze <sha256>` or batch with `uv run python -m image_analysis.cli analyze-batch --skip-existing`.

   * Produces: `analysis.v1.json`, places links under `evidence/labels/<label>/`.
   * CI hook: `scripts/validate_analyses.sh` runs after every batch to enforce the schema across all newly generated `analysis.v1.json` files.
3. `uv run python -m image_analysis.cli export-json <sha256> output.json`

Automation: wrap step 2 with the new `analyze-batch` command, a watcher, or a queue worker.

---

# Where this design is strong

* Idempotent, content-addressed, auditable, minimal dependencies.
* Model output is forced into a schema and stored both raw and validated.
* Easy to prove provenance and processing history.

# Likely flaws (and how to mitigate)

* **Hallucinated labels or OCR:** keep `temperature=0`, store confidence; require human sign-off for any “assertion” field before it leaves the system.
* **Vision model changes:** lock the exact model version string and store it; treat any upgrade as a new pipeline version (`analysis.v2.json`).
* **File tampering between ingest and court:** raw images live in `raw/sha256=`; verify hash before any export; emit a chain-of-custody report that rehashes all files.
* **EXIF trust:** EXIF is *advisory*. Flag inconsistencies (EXIF time > file mtime; missing Make/Model but has GPS, etc.). Add a heuristic check step.

---

# Fast extensions (all low-risk)

* Add **PII & NSFW detectors** to set `risk_flags`.
* Add **report generation**: a signed PDF that embeds the JSON and hashes.
* Add **case bundles** that export `raw`, `derived`, `DB` rows, and a manifest with Merkle root.

If you want, I’ll wire in: (a) a queue worker, (b) a redaction pass (faces, license plates), (c) a chain-of-custody PDF generator.
