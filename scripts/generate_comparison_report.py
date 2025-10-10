#!/usr/bin/env python3
"""Generate Comparison Report from Existing Packages

This utility analyzes two existing evidence packages and generates
a detailed comparison report, useful for:
- Post-hoc analysis of completed cases
- Comparing different processing runs
- Validating AI resolution impact

Usage:
    # Compare two specific packages
    python scripts/generate_comparison_report.py \
        data/packages/CASE-A_analysis_package_*.zip \
        data/packages/CASE-B_analysis_package_*.zip

    # Custom output location
    python scripts/generate_comparison_report.py \
        pkg_a.zip pkg_b.zip \
        --output reports/my_comparison.md

    # Include executive summary diff
    python scripts/generate_comparison_report.py \
        pkg_a.zip pkg_b.zip \
        --include-summary-diff
"""

import argparse
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional


def extract_package_to_temp(package_path: Path) -> Path:
    """Extract package to temporary directory

    Args:
        package_path: Path to ZIP package

    Returns:
        Path to extracted directory
    """
    extract_dir = package_path.parent / f".{package_path.stem}_temp"

    if extract_dir.exists():
        import shutil
        shutil.rmtree(extract_dir)

    with zipfile.ZipFile(package_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    return extract_dir


def load_correlation_analysis(extracted_dir: Path) -> Dict[str, Any]:
    """Load correlation analysis from extracted package"""
    correlation_file = extracted_dir / "correlations" / "correlation_analysis.json"

    if not correlation_file.exists():
        raise FileNotFoundError(f"correlation_analysis.json not found in {extracted_dir}")

    with open(correlation_file, 'r') as f:
        return json.load(f)


def load_package_metadata(extracted_dir: Path) -> Dict[str, Any]:
    """Load package metadata from extracted package"""
    metadata_file = extracted_dir / "package_metadata.json"

    if not metadata_file.exists():
        raise FileNotFoundError(f"package_metadata.json not found in {extracted_dir}")

    with open(metadata_file, 'r') as f:
        return json.load(f)


def load_executive_summary(extracted_dir: Path) -> str:
    """Load executive summary text from extracted package"""
    summary_file = extracted_dir / "reports" / "executive_summary.txt"

    if not summary_file.exists():
        return "_Executive summary not found_"

    with open(summary_file, 'r') as f:
        return f.read()


def compare_entities(corr_a: Dict, corr_b: Dict) -> Dict[str, Any]:
    """Detailed entity comparison"""
    entities_a = {e['entity_name']: e for e in corr_a.get('entity_correlations', [])}
    entities_b = {e['entity_name']: e for e in corr_b.get('entity_correlations', [])}

    names_a = set(entities_a.keys())
    names_b = set(entities_b.keys())

    return {
        'only_in_a': sorted(names_a - names_b),
        'only_in_b': sorted(names_b - names_a),
        'in_both': sorted(names_a & names_b),
        'total_a': len(entities_a),
        'total_b': len(entities_b),
        'entities_a': entities_a,
        'entities_b': entities_b
    }


def generate_detailed_report(
    package_a_name: str,
    package_b_name: str,
    corr_a: Dict,
    corr_b: Dict,
    meta_a: Dict,
    meta_b: Dict,
    include_summary_diff: bool = False,
    summary_a: Optional[str] = None,
    summary_b: Optional[str] = None
) -> str:
    """Generate comprehensive comparison report"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entity_comp = compare_entities(corr_a, corr_b)

    # Calculate improvement metrics
    entity_improvement = entity_comp['total_b'] - entity_comp['total_a']
    entity_improvement_pct = (entity_improvement / entity_comp['total_a'] * 100) if entity_comp['total_a'] > 0 else 0

    timeline_a = len(corr_a.get('timeline_events', []))
    timeline_b = len(corr_b.get('timeline_events', []))
    timeline_improvement = timeline_b - timeline_a

    report = f"""# Package Comparison Report

**Generated**: {timestamp}
**Package A**: {package_a_name}
**Package B**: {package_b_name}

---

## Summary

| Metric | Package A | Package B | Delta |
|--------|-----------|-----------|-------|
| **Entity Correlations** | {entity_comp['total_a']} | {entity_comp['total_b']} | **{entity_improvement:+d}** ({entity_improvement_pct:+.0f}%) |
| Timeline Events | {timeline_a} | {timeline_b} | {timeline_improvement:+d} |
| Temporal Sequences | {len(corr_a.get('temporal_sequences', []))} | {len(corr_b.get('temporal_sequences', []))} | {len(corr_b.get('temporal_sequences', [])) - len(corr_a.get('temporal_sequences', [])):+d} |
| Timeline Gaps | {len(corr_a.get('timeline_gaps', []))} | {len(corr_b.get('timeline_gaps', []))} | {len(corr_b.get('timeline_gaps', [])) - len(corr_a.get('timeline_gaps', [])):+d} |
| Legal Significance | {meta_a['analysis_summary']['overall_legal_significance']} | {meta_b['analysis_summary']['overall_legal_significance']} | — |
| Total Risk Flags | {meta_a['analysis_summary']['total_risk_flags']} | {meta_b['analysis_summary']['total_risk_flags']} | {meta_b['analysis_summary']['total_risk_flags'] - meta_a['analysis_summary']['total_risk_flags']:+d} |

---

## Entity Correlation Detailed Analysis

### Entities Found in Both Packages

"""

    if entity_comp['in_both']:
        report += "| Entity Name | Package A Count | Package B Count | Delta |\n"
        report += "|-------------|-----------------|-----------------|-------|\n"

        for name in entity_comp['in_both']:
            count_a = entity_comp['entities_a'][name]['occurrence_count']
            count_b = entity_comp['entities_b'][name]['occurrence_count']
            delta = count_b - count_a

            delta_str = f"{delta:+d}" if delta != 0 else "—"
            report += f"| {name} | {count_a} | {count_b} | {delta_str} |\n"
    else:
        report += "_No entities found in both packages_\n"

    report += "\n### Entities Only in Package A\n\n"

    if entity_comp['only_in_a']:
        for name in entity_comp['only_in_a']:
            entity = entity_comp['entities_a'][name]
            report += f"- **{name}** ({entity['entity_type']}) - {entity['occurrence_count']} occurrences\n"
    else:
        report += "_None_\n"

    report += "\n### Entities Only in Package B\n\n"

    if entity_comp['only_in_b']:
        for name in entity_comp['only_in_b']:
            entity = entity_comp['entities_b'][name]
            report += f"- **{name}** ({entity['entity_type']}) - {entity['occurrence_count']} occurrences ⭐\n"

            # Show context for new entities
            if entity.get('evidence_occurrences'):
                first_occ = entity['evidence_occurrences'][0]
                context = first_occ.get('context', 'N/A')[:120]
                report += f"  - Context: \"{context}...\"\n"
    else:
        report += "_None_\n"

    report += f"""

---

## Timeline Quality Analysis

**IMPORTANT**: Timeline quality is measured by coherence and completeness, not just event count.

| Metric | Package A | Package B | Analysis |
|--------|-----------|-----------|----------|
| Timeline Events | {timeline_a} | {timeline_b} | {'+' + str(timeline_b - timeline_a) if timeline_b > timeline_a else str(timeline_b - timeline_a)} events |
| Temporal Sequences | {len(corr_a.get('temporal_sequences', []))} | {len(corr_b.get('temporal_sequences', []))} | {"✅ Better (larger clusters)" if len(corr_b.get('temporal_sequences', [])) < len(corr_a.get('temporal_sequences', [])) and timeline_b > timeline_a else "More sequences"} |
| Timeline Gaps | {len(corr_a.get('timeline_gaps', []))} | {len(corr_b.get('timeline_gaps', []))} | {"✅ Better (fewer gaps)" if len(corr_b.get('timeline_gaps', [])) < len(corr_a.get('timeline_gaps', [])) else "More gaps"} |
| Avg Events/Sequence | {timeline_a / len(corr_a.get('temporal_sequences', [])) if len(corr_a.get('temporal_sequences', [])) > 0 else 0:.1f} | {timeline_b / len(corr_b.get('temporal_sequences', [])) if len(corr_b.get('temporal_sequences', [])) > 0 else 0:.1f} | {"✅ Better coherence" if (timeline_b / len(corr_b.get('temporal_sequences', [])) if len(corr_b.get('temporal_sequences', [])) > 0 else 0) > (timeline_a / len(corr_a.get('temporal_sequences', [])) if len(corr_a.get('temporal_sequences', [])) > 0 else 0) else "Lower density"} |

### Timeline Gaps Breakdown

**Package A Gaps**:
"""

    # Add gap details for Package A
    gaps_a = corr_a.get('timeline_gaps', [])
    if gaps_a:
        for gap in gaps_a:
            report += f"- **{gap['gap_duration_days']:.0f} days** ({gap['gap_start'][:10]} → {gap['gap_end'][:10]}) - {gap['significance']} significance\n"
    else:
        report += "_No gaps detected_\n"

    report += "\n**Package B Gaps**:\n"

    # Add gap details for Package B
    gaps_b = corr_b.get('timeline_gaps', [])
    if gaps_b:
        for gap in gaps_b:
            report += f"- **{gap['gap_duration_days']:.0f} days** ({gap['gap_start'][:10]} → {gap['gap_end'][:10]}) - {gap['significance']} significance\n"
    else:
        report += "_No gaps detected_\n"

    # Add interpretation
    report += f"""

### Interpretation

"""

    if len(gaps_b) < len(gaps_a):
        report += f"✅ **Package B has better timeline continuity** ({len(gaps_a) - len(gaps_b)} fewer gaps)\n\n"
        report += "Fewer gaps indicate:\n"
        report += "- More complete evidentiary coverage\n"
        report += "- AI successfully linked events that string matching missed\n"
        report += "- Better narrative coherence for legal analysis\n"
    elif len(gaps_b) > len(gaps_a):
        report += f"⚠️ **Package A has better timeline continuity** ({len(gaps_b) - len(gaps_a)} fewer gaps)\n\n"
    else:
        report += f"⏸️ **Equal timeline continuity** (same gap count)\n\n"

    if timeline_b > timeline_a and len(corr_b.get('temporal_sequences', [])) < len(corr_a.get('temporal_sequences', [])):
        report += f"\n✅ **Package B has better sequence coherence**\n\n"
        report += f"More events ({timeline_b} vs {timeline_a}) organized into fewer, larger sequences "
        report += f"({len(corr_b.get('temporal_sequences', []))} vs {len(corr_a.get('temporal_sequences', []))}) "
        report += "indicates consolidated narrative rather than fragmented events.\n"

    report += f"""

---

## Legal Pattern Comparison

### Contradictions

| Package | Count | Details |
|---------|-------|---------|
| A | {len(corr_a.get('legal_patterns', {}).get('contradictions', []))} | """

    if corr_a.get('legal_patterns', {}).get('contradictions'):
        contradictions_a = corr_a['legal_patterns']['contradictions']
        report += f"Severity avg: {sum(c['severity'] for c in contradictions_a) / len(contradictions_a):.2f}"
    else:
        report += "None found"

    report += f""" |
| B | {len(corr_b.get('legal_patterns', {}).get('contradictions', []))} | """

    if corr_b.get('legal_patterns', {}).get('contradictions'):
        contradictions_b = corr_b['legal_patterns']['contradictions']
        report += f"Severity avg: {sum(c['severity'] for c in contradictions_b) / len(contradictions_b):.2f}"
    else:
        report += "None found"

    report += """ |

### Corroboration

| Package | Count | Strength Distribution |
|---------|-------|-----------------------|
"""

    def get_corroboration_dist(patterns):
        corr_list = patterns.get('legal_patterns', {}).get('corroboration', [])
        if not corr_list:
            return "—"
        strengths = [c['corroboration_strength'] for c in corr_list]
        strong = strengths.count('strong')
        moderate = strengths.count('moderate')
        weak = strengths.count('weak')
        return f"Strong: {strong}, Moderate: {moderate}, Weak: {weak}"

    report += f"| A | {len(corr_a.get('legal_patterns', {}).get('corroboration', []))} | {get_corroboration_dist(corr_a)} |\n"
    report += f"| B | {len(corr_b.get('legal_patterns', {}).get('corroboration', []))} | {get_corroboration_dist(corr_b)} |\n"

    report += f"""

### Evidence Gaps

- **Package A**: {len(corr_a.get('legal_patterns', {}).get('evidence_gaps', []))} gaps identified
- **Package B**: {len(corr_b.get('legal_patterns', {}).get('evidence_gaps', []))} gaps identified

"""

    # Include executive summary diff if requested
    if include_summary_diff and summary_a and summary_b:
        report += """---

## Executive Summary Comparison

### Package A Summary

```
"""
        report += summary_a[:1000]  # Limit to first 1000 chars
        report += """
```

### Package B Summary

```
"""
        report += summary_b[:1000]
        report += """
```

"""

    report += f"""---

## Package Metadata

### Package A
- **Created**: {meta_a['package_info']['created']}
- **Case ID**: {meta_a['package_info']['case_id']}
- **Evidence Count**: {meta_a['package_info']['evidence_count']}
- **Evidence Types**: {', '.join(meta_a['package_info']['evidence_types'])}

### Package B
- **Created**: {meta_b['package_info']['created']}
- **Case ID**: {meta_b['package_info']['case_id']}
- **Evidence Count**: {meta_b['package_info']['evidence_count']}
- **Evidence Types**: {', '.join(meta_b['package_info']['evidence_types'])}

---

_Generated by Evidence Toolkit Comparison Report Generator v3.3.0_
"""

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Generate comparison report from two existing evidence packages"
    )

    parser.add_argument(
        'package_a',
        type=Path,
        help='First package ZIP file (Package A)'
    )

    parser.add_argument(
        'package_b',
        type=Path,
        help='Second package ZIP file (Package B)'
    )

    parser.add_argument(
        '--output',
        type=Path,
        help='Output report path (default: reports/comparison_TIMESTAMP.md)'
    )

    parser.add_argument(
        '--include-summary-diff',
        action='store_true',
        help='Include executive summary comparison in report'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("📊 PACKAGE COMPARISON REPORT GENERATOR")
    print("=" * 80)

    # Verify packages exist
    if not args.package_a.exists():
        print(f"\n❌ Package A not found: {args.package_a}")
        sys.exit(1)

    if not args.package_b.exists():
        print(f"\n❌ Package B not found: {args.package_b}")
        sys.exit(1)

    print(f"\n📦 Package A: {args.package_a.name}")
    print(f"📦 Package B: {args.package_b.name}")

    # Extract packages
    print(f"\n📂 Extracting packages...")
    extracted_a = extract_package_to_temp(args.package_a)
    extracted_b = extract_package_to_temp(args.package_b)

    print(f"   ✅ Package A extracted")
    print(f"   ✅ Package B extracted")

    # Load data
    print(f"\n📊 Loading analysis data...")
    corr_a = load_correlation_analysis(extracted_a)
    corr_b = load_correlation_analysis(extracted_b)
    meta_a = load_package_metadata(extracted_a)
    meta_b = load_package_metadata(extracted_b)

    summary_a = None
    summary_b = None

    if args.include_summary_diff:
        print(f"\n📄 Loading executive summaries...")
        summary_a = load_executive_summary(extracted_a)
        summary_b = load_executive_summary(extracted_b)

    print(f"   ✅ Data loaded")

    # Generate report
    print(f"\n📝 Generating comparison report...")

    report = generate_detailed_report(
        package_a_name=args.package_a.stem,
        package_b_name=args.package_b.stem,
        corr_a=corr_a,
        corr_b=corr_b,
        meta_a=meta_a,
        meta_b=meta_b,
        include_summary_diff=args.include_summary_diff,
        summary_a=summary_a,
        summary_b=summary_b
    )

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path("reports") / f"comparison_{timestamp}.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save report
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\n✅ Report saved to: {output_path}")
    print(f"\n" + "=" * 80)
    print("✅ COMPARISON COMPLETE")
    print("=" * 80)

    # Cleanup temp directories
    import shutil
    shutil.rmtree(extracted_a)
    shutil.rmtree(extracted_b)


if __name__ == "__main__":
    main()
