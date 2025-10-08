# Quick Start Example Case

This directory contains sample evidence files for testing the Evidence Toolkit workflow.

## Ready-to-Use Test Case

We've prepared a minimal test case with sample evidence to help you verify your installation:

### Option 1: Use Pre-Made Test Case (Fastest!)

```bash
# From the evidence-toolkit root directory
./quick-start.sh examples/sample-case-quickstart QUICKSTART-TEST
```

This will process:
- 2 sample documents
- 1 sample email
- 2 sample images

**Expected output**: Client package in `data/packages/QUICKSTART-TEST_analysis_package_*.zip`

---

### Option 2: Create Your Own Test Case

```bash
# Create a new case directory
mkdir -p data/cases/MY-TEST-CASE

# Copy a few sample files
cp examples/sample-documents/investigation-invite-letter.txt data/cases/MY-TEST-CASE/
cp examples/sample-emails/Fair\ treatment\ Meeting.eml data/cases/MY-TEST-CASE/

# Run the analysis
./quick-start.sh data/cases/MY-TEST-CASE MY-TEST-CASE
```

---

## Understanding the Sample Files

### Sample Documents (`sample-documents/`)
- **investigation-invite-letter.txt**: Meeting invitation (low risk)
- **disciplianry-letter.txt.txt**: Disciplinary communication (medium risk)
- **hands.txt**: Health & safety concern (potential high risk)

### Sample Emails (`sample-emails/`)
- **Fair treatment Meeting.eml**: Professional meeting request
- **Re\_ Follow-up on Monday's Meeting.eml**: Follow-up communication
- Email threading and participant analysis examples

### Sample Images (`sample-images/`)
- **IMG_2143.JPEG**: Evidence photograph with EXIF metadata
- **IMG_2097.JPEG**: Additional photographic evidence
- Tests vision AI, OCR capabilities, and EXIF timeline extraction

---

## What You'll See in the Output

### Executive Summary Preview
```
================================
CASE SUMMARY: QUICKSTART-TEST
================================

CASE OVERVIEW
-------------
Evidence Analyzed: 5 pieces
  - Documents: 2
  - Emails: 1
  - Images: 2

CROSS-EVIDENCE CORRELATIONS
----------------------------
Key Entities Found Across Multiple Evidence:
  [Entities that appear in multiple files will be listed here]

AI-POWERED INSIGHTS
-------------------
[AI-generated summary of the case based on all evidence]
```

### Correlation Analysis
The system will identify:
- **Entities** appearing in multiple pieces of evidence
- **Timeline** of events from file metadata, email dates, and EXIF timestamps
- **Temporal patterns** (clusters, gaps, sequences)
- **Visual evidence** correlation with document/email content

### Storage Verification
```bash
# After running, you can inspect the storage:
ls -la data/storage/derived/sha256=*/

# Each evidence piece will have:
# - metadata.json (file information)
# - analysis.v1.json (AI analysis results)
# - chain_of_custody.json (audit trail)
# - evidence_bundle.v1.json (forensic bundle)
```

---

## Verifying Everything Works

### 1. Check Package Contents

```bash
# Unzip the generated package
unzip -l data/packages/QUICKSTART-TEST_analysis_package_*.zip

# You should see:
# - reports/executive_summary.txt
# - analysis/*.json
# - correlations/correlation_analysis.json
# - evidence_catalog/evidence_catalog.json
# - documentation/README.md
# - visualizations/*.png (if documents were analyzed)
```

### 2. Quick Validation Commands

```bash
# View storage statistics
uv run evidence-toolkit storage stats

# List all cases
uv run evidence-toolkit case list

# Show the test case details
uv run evidence-toolkit case show QUICKSTART-TEST

# View correlation results
cat data/storage/derived/sha256=*/analysis.v1.json | grep -A5 "legal_significance"
```

---

## Troubleshooting the Example

### "No text extracted from files"
Some sample files might be minimal or have encoding issues. This is expected! The toolkit handles it gracefully and will note which files had extraction issues.

### "OPENAI_API_KEY not set"
Make sure you've exported your API key:
```bash
export OPENAI_API_KEY="your-key-here"
# Or add to .env file in project root
```

### "Package seems small"
With only 5 sample files (including 2 images), the package will be ~3-6 MB. Real cases with dozens of documents and images will produce larger, more comprehensive packages.

---

## Next Steps After Testing

Once you've successfully processed the sample case:

1. **Review the Output**:
   - Open `data/packages/QUICKSTART-TEST*/reports/executive_summary.txt`
   - Examine the correlation analysis JSON
   - Check visualization PNGs (if any)

2. **Try Your Own Evidence**:
   - Create a new case directory: `data/cases/YOUR-CASE`
   - Add your actual evidence files
   - Run: `./quick-start.sh data/cases/YOUR-CASE YOUR-CASE`

3. **Explore Advanced Features**:
   - Re-analysis: `uv run evidence-toolkit reanalyze --case-id YOUR-CASE`
   - Storage management: `uv run evidence-toolkit storage stats`
   - Case management: `uv run evidence-toolkit case list --detailed`

---

## Sample Case Statistics

**Sample Case**: `sample-case-quickstart`
- **Files**: 5 total (2 documents, 1 email, 2 images)
- **Processing Time**: ~2-3 minutes (including AI vision analysis)
- **OpenAI Cost**: ~$0.02-0.04 (images use Vision API)
- **Package Size**: ~3-6 MB (with original images)

**Perfect for**:
- Verifying your installation works
- Understanding multi-modal evidence analysis (text + images)
- Testing the complete workflow
- Learning vision AI, OCR, and EXIF capabilities

---

**Ready to test?** Run the command at the top of this file and see your first multi-modal evidence package in under 3 minutes!
