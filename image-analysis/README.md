# Evidence Toolkit – Image Analysis

Tooling for content-addressed evidence ingestion, deterministic AI analysis, and JSON schema validation.

## Prerequisites

- [uv](https://github.com/astral-sh/uv) for dependency management (`uv python install 3.12` if needed).
- Python 3.12+
- `OPENAI_API_KEY` exported in your shell for the Responses API.

Optional but recommended:

- Context7 MCP server configured in your IDE (`use context7` in prompts for library docs).

## Environment Setup

```bash
# inside the repository root
uv sync  # installs dependencies into .venv using pyproject.toml
```

Activate the environment if you want persistent shells:

```bash
source .venv/bin/activate
```

All examples below can also be run ad-hoc via `uv run …` without activating the venv.

## CLI Commands

The Typer application lives at `image_analysis/cli.py`.

```bash
uv run python -m image_analysis.cli --help
```

### Ingest

```bash
uv run python -m image_analysis.cli ingest /path/to/images --case-id CASE123
```

- Copies each image into `evidence/raw/sha256=<hash>/original.<ext>`.
- Writes EXIF + perceptual hash + metadata under `evidence/derived/sha256=<hash>/`.
- Seeds `chain_of_custody.json` with an ingest event.
- Upserts the SQLite catalog at `db/evidence.sqlite`.

### Analyze

```bash
uv run python -m image_analysis.cli analyze <sha256>
```

- Calls the OpenAI **Responses API** with enforced JSON (`text={"format": {"type": "json_object"}}`) and `temperature=0`.
- Stores the raw payload as `openai.v1.json` and the validated bundle as `analysis.v1.json`.
- Appends a chain-of-custody event and hard-links images into `evidence/labels/<label>/`.

Provide optional flags:

```bash
uv run python -m image_analysis.cli analyze <sha256> \
  --model gpt-4.1-mini \
  --revision 2025-09-10 \
  --actor "analyst@hq"
```

### Analyze Batch

```bash
uv run python -m image_analysis.cli analyze-batch --skip-existing --limit 10
```

- Iterates through `evidence/derived/sha256=*` and analyzes each staged artifact (respects existing `analysis.v1.json` when `--skip-existing` is left on, which is the default).
- Use `--limit` to cap how many hashes are processed per invocation.
- Disable `--fail-fast` if you want the loop to continue after an error.

### Export

```bash
uv run python -m image_analysis.cli export-json <sha256> output.json
```

Copies the validated bundle for downstream sharing/audit.

## Schema Validation

The canonical schema is `schemas/images.v1.json`. Validate any generated bundle via:

```bash
uv run python validate_schema.py evidence/derived/sha256=<hash>/analysis.v1.json
```

CI/pipeline hook:

```bash
scripts/validate_analyses.sh
```

Scans the entire `evidence/derived/` tree and fails fast if any `analysis.v1.json` drifts from the schema.

## Directory Layout

```
evidence/
  raw/sha256=<hash>/original.<ext>
  derived/sha256=<hash>/
    metadata.json
    exif.json
    phash.txt
    chain_of_custody.json
    openai.v1.json
    analysis.v1.json
  labels/<label>/<hash>.<ext>
db/evidence.sqlite
logs/app.log
```

## Troubleshooting

- **Missing OpenAI API key**: export `OPENAI_API_KEY` before running `analyze`.
- **Schema errors**: use `validate_schema.py` to inspect field-level validation failures.
- **Context7**: ensure the MCP server is installed (`npx -y @upstash/context7-mcp --api-key …`) and prompt with `use context7` to pull fresh docs.

## Testing Ideas

- Run `scripts/validate_analyses.sh` in CI after the `analyze` step.
- Add unit tests for helper functions (hashing, EXIF parsing) using `uv run pytest` once tests are authored.
