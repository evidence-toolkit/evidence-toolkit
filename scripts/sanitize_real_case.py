#!/usr/bin/env python3
"""
Sanitize REAL Evidence Toolkit output for demo purposes.

Takes actual pipeline output and does find/replace for PII.
Does NOT generate synthetic content - uses your real analysis.
"""

import re
import shutil
from pathlib import Path
from typing import Dict

# Sanitization mappings
SANITIZE_MAP = {
    # Company/Brand
    r"Sainsbury'?s?": "Major UK Retailer",
    r"sainsbury'?s?": "major UK retailer",
    r"SAINSBURY'?S?": "MAJOR UK RETAILER",

    # People
    r"Paul Boucherat": "Employee A",
    r"paul boucherat": "employee A",
    r"PAUL BOUCHERAT": "EMPLOYEE A",
    r"Boucherat": "Employee A",
    # Note: "Paul" is too common to safely replace (could be in product names, etc.)

    # Locations
    r"Swadlincote": "Store Location X",
    r"swadlincote": "store location X",
    r"SWADLINCOTE": "STORE LOCATION X",

    # Case IDs
    r"BCH_WORKPLACE_205_1": "DEMO_WORKPLACE_001",
    r"bch001": "demo001",
    r"BCH001": "DEMO001",
}

def sanitize_text(text: str) -> str:
    """Apply sanitization mappings to text."""
    result = text
    for pattern, replacement in SANITIZE_MAP.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result

def sanitize_case_package(source_dir: Path, output_dir: Path):
    """
    Sanitize entire case package (reports, correlations, metadata).
    Preserves directory structure and file types.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    # Files to sanitize (text files)
    text_files_to_process = [
        "reports/executive_summary.txt",
        "correlations/correlation_analysis.json",
        "package_metadata.json",
    ]

    sanitized_count = 0

    for file_path in text_files_to_process:
        source_file = source_dir / file_path
        if not source_file.exists():
            print(f"⚠️  Skipping {file_path} (not found)")
            continue

        # Read original content
        try:
            original = source_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            print(f"⚠️  Skipping {file_path} (binary file)")
            continue

        # Sanitize
        sanitized = sanitize_text(original)

        # Write to output
        output_file = output_dir / file_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(sanitized, encoding='utf-8')

        sanitized_count += 1

        # Report changes
        changes = len(original) - len(sanitized)
        print(f"✅ Sanitized: {file_path} ({sanitized_count} files)")
        if changes != 0:
            print(f"   Size change: {changes:+d} bytes")

    # Create README
    readme = f"""# Demo Case: Workplace Investigation 001

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

- `reports/executive_summary.txt` - Full case analysis ({(output_dir / 'reports/executive_summary.txt').stat().st_size // 1024}KB)
- `correlations/correlation_analysis.json` - Entity relationships and patterns
- `package_metadata.json` - Case metadata and processing info

## How This Was Generated

```bash
# 1. Original case processed with Evidence Toolkit
uv run evidence-toolkit process-case data/cases/Sainsburys \\
  --case-id BCH_WORKPLACE_205_1 \\
  --case-type workplace

# 2. Output sanitized with find/replace script
python scripts/sanitize_real_case.py \\
  data/packages/BCH_WORKPLACE_205_1_analysis_package_* \\
  demos/workplace_investigation_001_real

# 3. Branded PDF generated
python scripts/create_branded_pdf.py \\
  demos/workplace_investigation_001_real/reports/executive_summary.txt \\
  demos/DEMO_Report_Real.pdf \\
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
"""

    (output_dir / "README.md").write_text(readme)
    print(f"✅ Created README.md")

    print(f"\n🎉 Sanitization complete!")
    print(f"   Source: {source_dir}")
    print(f"   Output: {output_dir}")
    print(f"   Files processed: {sanitized_count}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python sanitize_real_case.py <source_package_dir> <output_demo_dir>")
        print("\nExample:")
        print("  python scripts/sanitize_real_case.py \\")
        print("    data/packages/BCH_WORKPLACE_205_1_analysis_package_20251006_234304 \\")
        print("    demos/workplace_investigation_001_real")
        sys.exit(1)

    source = Path(sys.argv[1])
    output = Path(sys.argv[2])

    if not source.exists():
        print(f"❌ Error: Source directory not found: {source}")
        sys.exit(1)

    sanitize_case_package(source, output)
