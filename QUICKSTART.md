# Evidence Toolkit - Quick Start Guide
## 5 Minutes to Your First Client Package

**Goal**: From installation to professional evidence analysis package in under 5 minutes.

---

## Prerequisites (30 seconds)

Before you begin, ensure you have:

1. **Python 3.12+** installed
2. **OpenAI API key** (required for AI analysis)
3. **Evidence files** ready to analyze (documents, PDFs, images, or emails)

---

## Step 1: Installation (60 seconds)

### Option A: Using UV (Recommended - Fastest)

```bash
# Clone the repository
git clone https://github.com/evidence-toolkit/evidence-toolkit.git
cd evidence-toolkit

# Install with UV (fast!)
pip install uv
uv pip install -e .

# Verify installation
uv run evidence-toolkit --version
```

### Option B: Using Standard pip

```bash
# Clone the repository
git clone https://github.com/evidence-toolkit/evidence-toolkit.git
cd evidence-toolkit

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install
pip install -e .

# Verify installation
evidence-toolkit --version
```

**Expected output**: `Evidence Toolkit v3.3.0`

---

## Step 2: Configure OpenAI API Key (15 seconds)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Or create a .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

**Why?** The toolkit uses OpenAI's GPT-4.1-mini model for deterministic evidence analysis (temperature=0 for reproducibility).

---

## Step 3: Prepare Your Evidence (30 seconds)

Create a case directory and add your evidence files:

```bash
# Create case directory
mkdir -p data/cases/MY-CASE-001

# Add your evidence files
cp /path/to/your/documents/*.pdf data/cases/MY-CASE-001/
cp /path/to/your/emails/*.eml data/cases/MY-CASE-001/
cp /path/to/your/images/*.jpg data/cases/MY-CASE-001/
```

**Supported formats**:
- **Documents**: `.txt`, `.pdf`
- **Emails**: `.eml` (standard email format)
- **Images**: `.jpg`, `.jpeg`, `.png`

**Example structure**:
```
data/cases/MY-CASE-001/
├── complaint_letter.pdf
├── email_thread_001.eml
├── email_thread_002.eml
└── evidence_photo.jpg
```

---

## Step 4: Run the Analysis (3 minutes)

### Option A: One-Command Pipeline (Easiest!)

```bash
./quick-start.sh data/cases/MY-CASE-001 MY-CASE-001
```

This script will:
1. ✅ Validate your environment
2. 📥 Ingest evidence into content-addressed storage
3. 🤖 Run AI analysis on all evidence
4. 🔗 Perform cross-evidence correlation
5. 📦 Generate professional client package

### Option B: Manual Step-by-Step

```bash
# Full pipeline in one command
uv run evidence-toolkit process-case data/cases/MY-CASE-001 \
  --case-id MY-CASE-001 \
  --actor "your-name"
```

### What Happens During Processing?

**Phase 1: Ingestion (15 seconds)**
- Files hashed with SHA256 for deduplication
- Evidence stored in `data/storage/raw/sha256=<hash>/`
- Metadata extracted and saved
- Chain of custody initialized

**Phase 2: Analysis (90-120 seconds)**
- **Documents**: AI extracts entities, sentiment, legal significance
- **Emails**: Thread reconstruction, participant analysis, escalation detection
- **Images**: Vision AI performs scene analysis, OCR, object detection
- Results saved to `data/storage/derived/sha256=<hash>/analysis.v1.json`

**Phase 3: Correlation (15 seconds)**
- Entity matching across all evidence (e.g., "John Smith" in doc + email)
- Timeline reconstruction from file metadata, EXIF, email dates
- Pattern detection (temporal clusters, suspicious gaps)

**Phase 4: Package Generation (30 seconds)**
- AI-generated executive summary
- Professional reports and visualizations
- Evidence catalog with chain of custody
- ZIP archive created in `data/packages/`

---

## Step 5: View Your Results (30 seconds)

### Find Your Package

```bash
# List generated packages
ls -lh data/packages/

# Example output:
# MY-CASE-001_analysis_package_20251005_183045.zip
```

### Explore the Package

```bash
# Unzip to explore
unzip data/packages/MY-CASE-001_analysis_package_*.zip -d review/

# Package structure:
review/MY-CASE-001_analysis_package_20251005_183045/
├── reports/
│   └── executive_summary.txt          # ← Start here!
├── analysis/
│   ├── case_analysis.json
│   └── document_complaint_letter_*.json
├── correlations/
│   └── correlation_analysis.json
├── evidence_catalog/
│   └── evidence_catalog.json
├── visualizations/
│   ├── word_cloud.png
│   └── word_frequency.png
├── documentation/
│   ├── README.md
│   └── methodology.md
└── raw_evidence/
    └── [original files]
```

### Quick Preview

```bash
# Read the executive summary
cat review/*/reports/executive_summary.txt

# View correlations
cat review/*/correlations/correlation_analysis.json | jq '.entity_correlations[] | {entity: .entity_name, occurrences: .occurrence_count}'
```

---

## Understanding the Results

### Executive Summary Format

```
================================
CASE SUMMARY: MY-CASE-001
================================

CASE OVERVIEW
-------------
Evidence Analyzed: 4 pieces
  - Documents: 2
  - Emails: 1
  - Images: 1

CROSS-EVIDENCE CORRELATIONS
----------------------------
Key Entities Found Across Multiple Evidence:
  1. John Smith (person) - 3 occurrences
  2. HR Department (organization) - 2 occurrences

TIMELINE ANALYSIS
-----------------
Evidence Timespan: 2024-08-15 to 2024-10-01
Total Events: 12
Temporal Clusters: 2
Timeline Gaps: 1 suspicious gap (14 days)

AI-POWERED INSIGHTS
-------------------
[Executive summary generated by OpenAI based on all evidence]

LEGAL SIGNIFICANCE ASSESSMENT
------------------------------
Overall Assessment: HIGH
Risk Flags Identified: retaliation, harassment
Recommended Actions: [AI recommendations]
```

`★ Insight ─────────────────────────────────────`
**Why Content-Addressed Storage?** Using SHA256 hashing means:
1. **Automatic deduplication** - Same file used in multiple cases = analyzed once
2. **Integrity verification** - Hash changes if file is tampered with
3. **Multi-case support** - Evidence can belong to multiple investigations
`─────────────────────────────────────────────────`

---

## Common Commands Reference

### Individual Pipeline Steps

```bash
# 1. Ingest only
uv run evidence-toolkit ingest data/cases/MY-CASE --case-id MY-CASE

# 2. Analyze specific evidence (by SHA256)
uv run evidence-toolkit analyze <sha256> --case-id MY-CASE

# 3. Run correlation analysis
uv run evidence-toolkit correlate --case-id MY-CASE

# 4. Generate package only
uv run evidence-toolkit package --case-id MY-CASE --include-raw
```

### Storage Management

```bash
# View storage statistics
uv run evidence-toolkit storage stats

# List all cases
uv run evidence-toolkit case list

# Show specific case details
uv run evidence-toolkit case show MY-CASE

# Clean up orphaned files
uv run evidence-toolkit storage cleanup --dry-run
uv run evidence-toolkit storage cleanup --force  # Actually clean
```

### Re-analysis

```bash
# Re-analyze all evidence in a case (useful after model updates)
uv run evidence-toolkit reanalyze --case-id MY-CASE --dry-run
uv run evidence-toolkit reanalyze --case-id MY-CASE
```

---

## What Makes This Forensic-Grade?

### 1. Deterministic AI Analysis
- **Temperature = 0**: Same input = same output (reproducible)
- **Structured outputs**: Pydantic validation ensures schema compliance
- **Confidence scoring**: Every analysis includes confidence metrics

### 2. Complete Chain of Custody
```json
{
  "ts": "2024-10-05T18:30:45.123Z",
  "actor": "your-name",
  "action": "ingest",
  "note": "File ingested from data/cases/MY-CASE/document.pdf"
}
```

### 3. Content-Addressed Storage
- SHA256 hashing prevents tampering
- Immutable storage (original files never modified)
- Derived data kept separate from raw evidence

### 4. Professional Deliverables
- Executive summaries suitable for legal proceedings
- Complete evidence catalogs with metadata
- Methodology documentation for expert testimony

`★ Insight ─────────────────────────────────────`
**Multi-Case Efficiency**: Evidence analyzed once, used everywhere:
- Same document in 3 cases = 1 AI analysis (cost savings!)
- Chain of custody tracks all case associations
- Storage stats show orphaned evidence for cleanup
`─────────────────────────────────────────────────`

---

## Troubleshooting

### "OPENAI_API_KEY not set"
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Set it for this session
export OPENAI_API_KEY="your-key"

# Or permanently in .env file
echo "OPENAI_API_KEY=your-key" >> .env
```

### "No evidence found for case"
```bash
# Check case directory exists
ls -la data/cases/MY-CASE

# List ingested evidence
uv run evidence-toolkit case show MY-CASE
```

### "Analysis failed"
```bash
# Check file is readable
file data/cases/MY-CASE/document.pdf

# Check storage permissions
ls -la data/storage/

# Re-analyze with verbose output
uv run evidence-toolkit analyze <sha256> --case-id MY-CASE
```

### "Package generation failed"
```bash
# Check correlation ran successfully
uv run evidence-toolkit correlate --case-id MY-CASE

# Check output directory is writable
mkdir -p data/packages
ls -la data/packages/
```

---

## Next Steps

### 1. Explore Advanced Features

**Custom Domain Configuration**:
```python
# src/evidence_toolkit/domains/custom_config.py
DOCUMENT_ANALYSIS_PROMPT = """
You are analyzing evidence for [your specific domain].
Focus on [your specific criteria]...
"""
```

**Batch Processing**:
```bash
# Process multiple cases
for case in data/cases/*/; do
  case_id=$(basename "$case")
  ./quick-start.sh "$case" "$case_id"
done
```

### 2. Review the Architecture
- [V3_ARCHITECTURE.md](V3_ARCHITECTURE.md) - Complete design documentation
- [CLAUDE.md](CLAUDE.md) - Developer quick reference
- [V3_COMPLETE.md](V3_COMPLETE.md) - Refactor achievements

### 3. API Usage (Python)

```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.analyzers import DocumentAnalyzer, CorrelationAnalyzer
from evidence_toolkit.pipeline import PackageGenerator

# Initialize storage
storage = EvidenceStorage("data/storage")

# Ingest evidence
result = storage.ingest_file(
    file_path="path/to/evidence.pdf",
    case_id="MY-CASE",
    actor="your-name"
)

# Get analysis
analysis = storage.get_analysis(result.sha256)
print(f"Legal significance: {analysis.document_analysis.legal_significance}")

# Run correlation
analyzer = CorrelationAnalyzer(storage)
correlations = analyzer.analyze_case_correlations("MY-CASE")
print(f"Found {len(correlations.entity_correlations)} correlated entities")
```

---

## Performance & Costs

### Typical Case Processing Times
| Evidence Count | Documents | Emails | Images | Total Time |
|---------------|-----------|--------|--------|------------|
| Small (5)     | 30s       | 20s    | 15s    | ~2 min     |
| Medium (20)   | 90s       | 60s    | 45s    | ~4 min     |
| Large (50)    | 180s      | 120s   | 90s    | ~8 min     |

*Times include AI analysis with gpt-4.1-mini*

### OpenAI API Costs (Approximate)
- **Document analysis**: ~$0.001-0.003 per document
- **Email analysis**: ~$0.002-0.005 per thread
- **Image analysis**: ~$0.003-0.008 per image
- **Executive summary**: ~$0.01-0.02 per case

**Example**: 20-piece case ≈ $0.10-0.30 total

`★ Insight ─────────────────────────────────────`
**Cost Optimization with Content-Addressed Storage**:
- Evidence analyzed ONCE and cached by SHA256
- Re-using same document in 10 cases = 1× analysis cost
- Multi-case workflows save 90%+ on duplicate evidence
`─────────────────────────────────────────────────`

---

## Support & Resources

### Documentation
- **Quick Start**: You are here! (QUICKSTART.md)
- **Architecture**: [V3_ARCHITECTURE.md](V3_ARCHITECTURE.md)
- **API Reference**: [docs/api/](docs/api/)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

### Getting Help
- **Issues**: https://github.com/evidence-toolkit/evidence-toolkit/issues
- **Discussions**: GitHub Discussions
- **Documentation**: https://github.com/evidence-toolkit/evidence-toolkit#readme

### Community
- Share your use cases and workflows
- Contribute domain configurations (corporate, journalism, research)
- Report bugs and request features

---

## Summary: Your 5-Minute Workflow

```bash
# 1. Install (60 seconds)
pip install uv
uv pip install -e .

# 2. Configure (15 seconds)
export OPENAI_API_KEY="your-key"

# 3. Prepare evidence (30 seconds)
mkdir -p data/cases/MY-CASE
cp /path/to/evidence/* data/cases/MY-CASE/

# 4. Run analysis (3 minutes)
./quick-start.sh data/cases/MY-CASE MY-CASE

# 5. Review results (30 seconds)
cat data/packages/MY-CASE*/reports/executive_summary.txt
```

**Total**: ~5 minutes from zero to professional client package! 🎉

---

**Ready to analyze your evidence? Start with Step 1 above!**
