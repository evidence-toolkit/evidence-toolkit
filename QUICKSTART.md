# Quick Start Guide
## From Zero to Analysis in 5 Minutes

This guide gets you from installation to your first professional forensic analysis package.

---

## Prerequisites

- Python 3.12+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- Evidence files (documents, emails, or images)

---

## 1. Install (60 seconds)

### Using UV (Recommended - Fastest)

```bash
git clone https://github.com/your-org/evidence-toolkit.git
cd evidence-toolkit
pip install uv
uv pip install -e .
uv run evidence-toolkit --version
```

### Using pip

```bash
git clone https://github.com/your-org/evidence-toolkit.git
cd evidence-toolkit
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
evidence-toolkit --version
```

**Expected output**: `Evidence Toolkit v3.3.0`

---

## 2. Configure API Key (15 seconds)

```bash
export OPENAI_API_KEY="your-api-key-here"

# Or create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

---

## 3. Prepare Evidence (30 seconds)

```bash
# Create case directory
mkdir -p data/cases/MY-CASE

# Add your evidence files
cp /path/to/documents/*.pdf data/cases/MY-CASE/
cp /path/to/emails/*.eml data/cases/MY-CASE/
cp /path/to/images/*.jpg data/cases/MY-CASE/
```

**Supported formats**:
- Documents: `.txt`, `.pdf`
- Emails: `.eml`
- Images: `.jpg`, `.jpeg`, `.png`

---

## 4. Run Analysis (2-3 minutes)

### One-Command Pipeline

```bash
uv run evidence-toolkit process-case data/cases/MY-CASE --case-id MY-CASE
```

This will:
1. 📥 Ingest evidence (SHA256 hashing, deduplication)
2. 🤖 Run AI analysis (entities, sentiment, legal significance)
3. 🔗 Perform cross-evidence correlation
4. 📦 Generate professional client package

### What Happens During Processing

**Phase 1: Ingestion** (15s)
- Files hashed with SHA256
- Stored in `data/storage/raw/sha256=<hash>/`
- Chain of custody initialized

**Phase 2: AI Analysis** (90-120s)
- Documents: Entity extraction, sentiment, legal risk
- Emails: Thread reconstruction, power dynamics
- Images: Vision AI scene analysis, OCR

**Phase 3: Correlation** (15s)
- Entity matching across evidence
- Timeline reconstruction
- Pattern detection

**Phase 4: Package Generation** (30s)
- AI executive summary
- Professional reports
- ZIP archive created

---

## 5. View Results (30 seconds)

```bash
# Find your package
ls -lh data/packages/

# Unzip to explore
unzip data/packages/MY-CASE*.zip -d review/

# Read executive summary
cat review/*/reports/executive_summary.txt
```

### Package Structure

```
MY-CASE_analysis_package_20251009_143000/
├── reports/
│   └── executive_summary.txt          # Start here!
├── analysis/
│   ├── case_analysis.json             # Structured data
│   └── [individual analyses]          # Per-evidence details
├── correlations/
│   └── correlation_analysis.json      # Cross-evidence patterns
├── evidence_catalog/
│   └── evidence_catalog.json          # Evidence inventory
└── raw_evidence/
    └── [original files]               # Your evidence
```

---

## Understanding the Results

### Executive Summary Format

```
================================
CASE SUMMARY: MY-CASE
================================

🔍 FORENSIC SUMMARY
-------------------
[1,280-char detailed narrative analysis of the case]

💡 KEY FINDINGS
---------------
1. [Finding with evidence citations]
2. [Finding with evidence citations]
3. [Finding with evidence citations]

⚖️ LEGAL IMPLICATIONS
----------------------
1. [Risk area for case strategy]
2. [Risk area for case strategy]
...

🎯 RECOMMENDED ACTIONS
----------------------
1. [Strategic guidance]
2. [Strategic guidance]
...

CROSS-EVIDENCE CORRELATIONS
----------------------------
Key Entities:
  • John Smith (person) - 3 occurrences
  • HR Department (org) - 2 occurrences

TIMELINE ANALYSIS
-----------------
Timespan: 2024-08-15 to 2024-10-01
Events: 12
Temporal Clusters: 2
Timeline Gaps: 1 suspicious gap (14 days)
```

---

## Common Commands

### Individual Pipeline Steps

```bash
# Step-by-step workflow
uv run evidence-toolkit ingest data/cases/MY-CASE --case-id MY-CASE
uv run evidence-toolkit analyze <sha256> --case-id MY-CASE
uv run evidence-toolkit correlate --case-id MY-CASE
uv run evidence-toolkit package --case-id MY-CASE
```

### Case Management

```bash
# List all cases
uv run evidence-toolkit case list

# Show case details
uv run evidence-toolkit case show MY-CASE

# List evidence in case
uv run evidence-toolkit case evidence MY-CASE
```

### Storage Management

```bash
# View storage stats
uv run evidence-toolkit storage stats

# Clean orphaned files
uv run evidence-toolkit storage cleanup --dry-run
uv run evidence-toolkit storage cleanup --force
```

### Re-analysis

```bash
# Re-analyze with latest AI models
uv run evidence-toolkit reanalyze --case-id MY-CASE
```

---

## Advanced Features

### AI Entity Resolution (v3.2)

Context-aware name matching ("Paul" → "Paul Boucherat"):

```bash
uv run evidence-toolkit process-case data/cases/MY-CASE \
  --case-id MY-CASE \
  --ai-resolve
```

### Case Type Support (v3.2)

Domain-specific analysis prompts:

```bash
# Workplace investigation
uv run evidence-toolkit process-case data/cases/MY-CASE \
  --case-id MY-CASE \
  --case-type workplace

# Contract dispute
uv run evidence-toolkit process-case data/cases/MY-CASE \
  --case-id MY-CASE \
  --case-type contract
```

Available case types:
- `generic` (default)
- `workplace` / `employment`
- `contract`

### Multi-Case Evidence Reuse

The same evidence can belong to multiple cases without re-analysis:

```bash
# Analyze once
uv run evidence-toolkit process-case data/cases/CASE-A --case-id CASE-A

# Add same evidence to another case (no re-analysis!)
uv run evidence-toolkit ingest data/cases/CASE-A --case-id CASE-B
uv run evidence-toolkit package --case-id CASE-B
```

**Cost savings**: 5 cases sharing 10 documents = 10 analyses instead of 50.

---

## Python API Usage

```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.analyzers import DocumentAnalyzer, CorrelationAnalyzer
from evidence_toolkit.pipeline import PackageGenerator

# Initialize storage
storage = EvidenceStorage("data/storage")

# Ingest evidence
result = storage.ingest_file(
    file_path="data/cases/MY-CASE/document.pdf",
    case_id="MY-CASE",
    actor="investigator@firm.com"
)

# Get analysis
analysis = storage.get_analysis(result.sha256)
print(f"Legal significance: {analysis.document_analysis.legal_significance}")

# Run correlation
correlator = CorrelationAnalyzer(storage)
correlations = correlator.analyze_case_correlations("MY-CASE")

# Generate package
packager = PackageGenerator(storage)
package = packager.create_client_package("MY-CASE", "data/packages/")
```

---

## Forensic Features

### Deterministic AI Analysis
- **Temperature = 0**: Reproducible results
- **Structured Output**: Pydantic validation
- **Confidence Scoring**: Every finding includes metrics

### Chain of Custody
```json
{
  "ts": "2025-10-09T14:30:45.123Z",
  "actor": "investigator@firm.com",
  "action": "ingest",
  "note": "File ingested from data/cases/MY-CASE/document.pdf"
}
```

### Content-Addressed Storage
- SHA256 hashing prevents tampering
- Immutable originals
- Automatic deduplication

---

## Performance & Costs

### Processing Times

| Evidence Count | Time | Notes |
|----------------|------|-------|
| 5 files | 2-3 min | Mixed types |
| 20 files | 6-8 min | Typical case |
| 50+ files | 15-20 min | Large case |

### OpenAI API Costs

- Document: ~$0.001-0.003
- Email: ~$0.002-0.005
- Image: ~$0.003-0.008
- Summary: ~$0.01-0.02

**Example**: 20-piece case ≈ $0.10-0.30 total

---

## Troubleshooting

### "OPENAI_API_KEY not set"
```bash
echo $OPENAI_API_KEY  # Check if set
export OPENAI_API_KEY="your-key"  # Set for session
echo "OPENAI_API_KEY=your-key" >> .env  # Set permanently
```

### "No evidence found for case"
```bash
ls -la data/cases/MY-CASE  # Check directory
uv run evidence-toolkit case show MY-CASE  # Check ingestion
```

### "Analysis failed"
```bash
file data/cases/MY-CASE/document.pdf  # Check file
ls -la data/storage/  # Check permissions
```

### "Package generation failed"
```bash
uv run evidence-toolkit correlate --case-id MY-CASE  # Re-run correlation
mkdir -p data/packages  # Ensure output dir exists
```

---

## Next Steps

### Explore Documentation
- [Architecture](V3_ARCHITECTURE.md) - Complete design
- [Contributing](CONTRIBUTING.md) - Development setup
- [Case Types](docs/CASE_TYPES.md) - Domain-specific analysis

### Try Advanced Workflows

**Batch Processing**:
```bash
for case in data/cases/*/; do
  case_id=$(basename "$case")
  uv run evidence-toolkit process-case "$case" --case-id "$case_id"
done
```

**Custom Domain Configuration**:
```python
# src/evidence_toolkit/domains/custom_config.py
DOCUMENT_ANALYSIS_PROMPT = """
You are analyzing evidence for [your domain].
Focus on [your criteria]...
"""
```

---

## Summary: Your 5-Minute Workflow

```bash
# 1. Install (60s)
pip install uv && uv pip install -e .

# 2. Configure (15s)
export OPENAI_API_KEY="your-key"

# 3. Prepare evidence (30s)
mkdir -p data/cases/MY-CASE
cp /path/to/evidence/* data/cases/MY-CASE/

# 4. Run analysis (3min)
uv run evidence-toolkit process-case data/cases/MY-CASE --case-id MY-CASE

# 5. View results (30s)
cat data/packages/MY-CASE*/reports/executive_summary.txt
```

**Total**: ~5 minutes from zero to professional forensic package! 🚀

---

**Ready to analyze evidence? Start with Step 1 above!**
