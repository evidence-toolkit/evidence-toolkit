# Demo Case: Workplace Investigation 001

**REAL ANALYSIS OUTPUT** - Sanitized from actual Evidence Toolkit pipeline

## Source
This demo was generated from a real workplace investigation case involving:
- 1,295 evidence items analyzed
- Food safety and hygiene concerns
- Whistleblowing allegations
- Employment law implications

All personally identifiable information has been sanitized:
- Company: "Sainsbury's" → "Major UK Retailer"
- Individual: "Paul Boucherat" → "Employee A"
- Location: "Swadlincote" → "Store Location X"
- Case ID: "BCH_WORKPLACE_205_1" → "DEMO_WORKPLACE_001"

## What This Demonstrates

This is **actual output** from the Evidence Toolkit pipeline, showing:

1. **Scale**: Analysis of 1,295 evidence pieces (photos, documents)
2. **AI Pattern Detection**: Contradictions, corroboration, evidence gaps
3. **Entity Correlation**: Tracking individuals across 1,295 items
4. **Legal Assessment**: Tribunal risk scoring, financial exposure estimates
5. **Timeline Construction**: Chronological narrative from unstructured data

## Files Included

- `reports/executive_summary.txt` - Full case analysis (1104KB)
- `correlations/correlation_analysis.json` - Entity relationships and patterns
- `package_metadata.json` - Case metadata and processing info

## How This Was Generated

```bash
# 1. Original case processed with Evidence Toolkit
uv run evidence-toolkit process-case data/cases/Sainsburys \
  --case-id BCH_WORKPLACE_205_1 \
  --case-type workplace

# 2. Output sanitized with find/replace script
python scripts/sanitize_real_case.py \
  data/packages/BCH_WORKPLACE_205_1_analysis_package_* \
  demos/workplace_investigation_001_real

# 3. Branded PDF generated
python scripts/create_branded_pdf.py \
  demos/workplace_investigation_001_real/reports/executive_summary.txt \
  demos/DEMO_Report_Real.pdf \
  DEMO_WORKPLACE_001
```

## Typical Use Case

**Client scenario**: Employee alleges unfair dismissal after raising food safety concerns. Provides 1,295 photos of hygiene issues taken over 6 months, plus emails and incident reports.

**Manual process**: 3-4 days paralegal time reviewing all evidence = £1,200-1,600 cost

**Evidence Toolkit process**:
- Upload: 10 minutes (ZIP all files)
- Processing: 30-45 minutes (AI analysis)
- Review: 15 minutes (QA the output)
- Cost: £150-300

**Time saved**: 3+ days → 1 hour

---

*This is actual Evidence Toolkit output. Content sanitized for privacy.*
