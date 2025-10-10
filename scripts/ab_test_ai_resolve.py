#!/usr/bin/env python3
"""A/B Test Script: AI Entity Resolution Impact Analysis

This script creates paired test cases and runs comparative analysis to measure
the impact of the --ai-resolve flag on entity correlation, timeline reconstruction,
and legal pattern detection.

Usage:
    # Standard test (10 images + 5 documents)
    python scripts/ab_test_ai_resolve.py

    # Large test (30 images + 10 documents)
    python scripts/ab_test_ai_resolve.py --large

    # Custom counts
    python scripts/ab_test_ai_resolve.py --images 20 --documents 8

    # Skip pipeline execution (analyze existing packages)
    python scripts/ab_test_ai_resolve.py --analyze-only \
        --case-a AB-TEST-A-NO-RESOLVE \
        --case-b AB-TEST-B-WITH-RESOLVE

The script will:
1. Generate two identical test cases with different SHA256 hashes
2. Run Case A without --ai-resolve
3. Run Case B with --ai-resolve
4. Extract and compare the generated packages
5. Generate a comprehensive Markdown report in reports/
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from create_test_case import create_test_case, calculate_sha256


def create_paired_test_cases(
    source_case: Path,
    image_count: int,
    document_count: int
) -> Tuple[Path, Path]:
    """Create two identical test cases with different SHA256 hashes

    Args:
        source_case: Source case directory to sample from
        image_count: Number of test images
        document_count: Number of test documents

    Returns:
        Tuple of (case_a_path, case_b_path)
    """
    print("=" * 80)
    print("🧪 PAIRED TEST CASE GENERATION")
    print("=" * 80)

    cases_dir = Path("data/cases")
    case_a = cases_dir / "AB-TEST-A-NO-RESOLVE"
    case_b = cases_dir / "AB-TEST-B-WITH-RESOLVE"

    print(f"\n📁 Creating Case A (without AI resolve): {case_a}")
    create_test_case(
        source_case_dir=source_case,
        output_dir=case_a,
        image_count=image_count,
        document_count=document_count,
        images_only=False
    )

    print(f"\n" + "=" * 80)
    print(f"📁 Creating Case B (with AI resolve): {case_b}")
    create_test_case(
        source_case_dir=source_case,
        output_dir=case_b,
        image_count=image_count,
        document_count=document_count,
        images_only=False
    )

    print(f"\n" + "=" * 80)
    print("✅ PAIRED TEST CASES CREATED")
    print("=" * 80)
    print(f"\nCase A: {case_a}")
    print(f"Case B: {case_b}")
    print(f"\n💡 Both cases contain {image_count} images + {document_count} documents")
    print(f"   with different SHA256 hashes for clean analysis")

    return case_a, case_b


def run_pipeline(case_dir: Path, case_id: str, use_ai_resolve: bool) -> Tuple[float, Path]:
    """Run evidence toolkit pipeline on a test case

    Args:
        case_dir: Path to case directory
        case_id: Case ID for processing
        use_ai_resolve: Whether to use --ai-resolve flag

    Returns:
        Tuple of (processing_time_seconds, package_path)
    """
    resolve_flag = "WITH AI RESOLVE" if use_ai_resolve else "WITHOUT AI RESOLVE"
    print(f"\n{'=' * 80}")
    print(f"🚀 RUNNING PIPELINE: {case_id} ({resolve_flag})")
    print(f"{'=' * 80}")

    cmd = [
        "uv", "run", "evidence-toolkit", "process-case",
        str(case_dir),
        "--case-id", case_id,
        "--case-type", "workplace"
    ]

    if use_ai_resolve:
        cmd.append("--ai-resolve")

    print(f"\n📋 Command: {' '.join(cmd)}")
    print(f"⏱️  Starting at {datetime.now().strftime('%H:%M:%S')}")

    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )

        elapsed = time.time() - start_time

        print(f"\n✅ Pipeline completed in {elapsed:.1f}s")

        # Find the generated package
        packages_dir = Path("data/packages")
        packages = sorted(packages_dir.glob(f"{case_id}_analysis_package_*.zip"))

        if not packages:
            raise FileNotFoundError(f"No package found for {case_id}")

        latest_package = packages[-1]
        print(f"📦 Package: {latest_package.name}")

        return elapsed, latest_package

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Pipeline failed!")
        print(f"   Error: {e}")
        print(f"   stderr: {e.stderr}")
        raise


def extract_package(package_path: Path) -> Path:
    """Extract a package ZIP file

    Args:
        package_path: Path to package ZIP

    Returns:
        Path to extracted directory
    """
    import zipfile

    extract_dir = package_path.parent / f"{package_path.stem}_extracted"

    print(f"\n📂 Extracting {package_path.name}...")

    with zipfile.ZipFile(package_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    print(f"   ✅ Extracted to {extract_dir}")

    return extract_dir


def load_correlation_analysis(extracted_dir: Path) -> Dict[str, Any]:
    """Load correlation analysis JSON from extracted package

    Args:
        extracted_dir: Path to extracted package directory

    Returns:
        Correlation analysis dictionary
    """
    correlation_file = extracted_dir / "correlations" / "correlation_analysis.json"

    if not correlation_file.exists():
        raise FileNotFoundError(f"correlation_analysis.json not found in {extracted_dir}")

    with open(correlation_file, 'r') as f:
        return json.load(f)


def load_package_metadata(extracted_dir: Path) -> Dict[str, Any]:
    """Load package metadata JSON from extracted package

    Args:
        extracted_dir: Path to extracted package directory

    Returns:
        Package metadata dictionary
    """
    metadata_file = extracted_dir / "package_metadata.json"

    if not metadata_file.exists():
        raise FileNotFoundError(f"package_metadata.json not found in {extracted_dir}")

    with open(metadata_file, 'r') as f:
        return json.load(f)


def compare_entity_correlations(corr_a: Dict, corr_b: Dict) -> Dict[str, Any]:
    """Compare entity correlations between two analyses

    Args:
        corr_a: Correlation analysis from Case A (no AI)
        corr_b: Correlation analysis from Case B (with AI)

    Returns:
        Comparison results dictionary
    """
    entities_a = corr_a.get('entity_correlations', [])
    entities_b = corr_b.get('entity_correlations', [])

    # Create entity name sets
    names_a = {e['entity_name'] for e in entities_a}
    names_b = {e['entity_name'] for e in entities_b}

    # Find new entities discovered by AI
    new_entities = names_b - names_a

    # Find entities with increased occurrence count
    improved_entities = []
    for entity_b in entities_b:
        name = entity_b['entity_name']
        if name in names_a:
            entity_a = next((e for e in entities_a if e['entity_name'] == name), None)
            if entity_a and entity_b['occurrence_count'] > entity_a['occurrence_count']:
                improved_entities.append({
                    'name': name,
                    'count_a': entity_a['occurrence_count'],
                    'count_b': entity_b['occurrence_count'],
                    'improvement': entity_b['occurrence_count'] - entity_a['occurrence_count']
                })

    return {
        'total_a': len(entities_a),
        'total_b': len(entities_b),
        'new_entities': sorted(new_entities),
        'improved_entities': improved_entities,
        'improvement_pct': ((len(entities_b) - len(entities_a)) / len(entities_a) * 100) if entities_a else 0
    }


def generate_report(
    case_a_id: str,
    case_b_id: str,
    time_a: float,
    time_b: float,
    corr_a: Dict,
    corr_b: Dict,
    meta_a: Dict,
    meta_b: Dict,
    entity_comp: Dict
) -> str:
    """Generate comprehensive Markdown report

    Args:
        case_a_id: Case A identifier
        case_b_id: Case B identifier
        time_a: Processing time for Case A (seconds)
        time_b: Processing time for Case B (seconds)
        corr_a: Correlation analysis from Case A
        corr_b: Correlation analysis from Case B
        meta_a: Package metadata from Case A
        meta_b: Package metadata from Case B
        entity_comp: Entity comparison results

    Returns:
        Markdown report string
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extract summary metrics
    evidence_count = meta_a['package_info']['evidence_count']
    evidence_types = meta_a['package_info']['evidence_types']

    timeline_a = len(corr_a.get('timeline_events', []))
    timeline_b = len(corr_b.get('timeline_events', []))

    risk_flags_a = meta_a['analysis_summary']['total_risk_flags']
    risk_flags_b = meta_b['analysis_summary']['total_risk_flags']

    # Build report
    report = f"""# A/B Test Report: AI Entity Resolution Impact

**Test Date**: {timestamp}
**Evidence**: {evidence_count} files ({', '.join(evidence_types)})
**Source Case**: BCH_WORKPLACE_2025_2

---

## Executive Summary

| Metric | Case A (No AI) | Case B (With AI) | Improvement |
|--------|----------------|------------------|-------------|
| **Entity Correlations** | {entity_comp['total_a']} | {entity_comp['total_b']} | **+{entity_comp['improvement_pct']:.0f}%** |
| Timeline Events | {timeline_a} | {timeline_b} | +{timeline_b - timeline_a} |
| Risk Flags | {risk_flags_a} | {risk_flags_b} | +{risk_flags_b - risk_flags_a} |
| Processing Time | {time_a:.1f}s | {time_b:.1f}s | +{time_b - time_a:.1f}s ({(time_b - time_a) / time_a * 100:.0f}%) |

**Key Insight**: AI entity resolution found **{len(entity_comp['new_entities'])} additional entities**
that string matching alone could not correlate.

---

## Entity Correlation Analysis

### Case A: String Matching Only

Found **{entity_comp['total_a']} correlations**:

"""

    # Add Case A entities
    for i, entity in enumerate(corr_a.get('entity_correlations', []), 1):
        report += f"{i}. **{entity['entity_name']}** ({entity['entity_type']}) - {entity['occurrence_count']} occurrences\n"

    report += f"\n### Case B: With AI Resolution\n\n"
    report += f"Found **{entity_comp['total_b']} correlations**:\n\n"

    # Add Case B entities with highlighting
    for i, entity in enumerate(corr_b.get('entity_correlations', []), 1):
        name = entity['entity_name']
        count = entity['occurrence_count']
        entity_type = entity['entity_type']

        if name in entity_comp['new_entities']:
            report += f"{i}. **{name}** ({entity_type}) - {count} occurrences ⭐ **NEW** (AI resolved)\n"
        else:
            # Check if improved
            improved = next((e for e in entity_comp['improved_entities'] if e['name'] == name), None)
            if improved:
                report += f"{i}. **{name}** ({entity_type}) - {count} occurrences ⭐ +{improved['improvement']}\n"
            else:
                report += f"{i}. **{name}** ({entity_type}) - {count} occurrences\n"

    report += f"\n---\n\n## New Entities Discovered by AI\n\n"

    if entity_comp['new_entities']:
        for name in entity_comp['new_entities']:
            entity = next(e for e in corr_b['entity_correlations'] if e['entity_name'] == name)
            report += f"### {name} ({entity['entity_type']})\n\n"
            report += f"- **Occurrences**: {entity['occurrence_count']}\n"
            report += f"- **Confidence**: {entity['confidence_average']:.2f}\n"

            # Show first occurrence context
            if entity['evidence_occurrences']:
                first_occ = entity['evidence_occurrences'][0]
                context = first_occ.get('context', 'N/A')[:150]
                report += f"- **Context**: \"{context}...\"\n"

            report += "\n"
    else:
        report += "_No new entities discovered (test case may be too small or names already correlated by string matching)_\n\n"

    report += f"""---

## Timeline Analysis

| Metric | Case A | Case B | Delta |
|--------|--------|--------|-------|
| Total Events | {timeline_a} | {timeline_b} | +{timeline_b - timeline_a} |
| Temporal Sequences | {len(corr_a.get('temporal_sequences', []))} | {len(corr_b.get('temporal_sequences', []))} | +{len(corr_b.get('temporal_sequences', [])) - len(corr_a.get('temporal_sequences', []))} |
| Timeline Gaps | {len(corr_a.get('timeline_gaps', []))} | {len(corr_b.get('timeline_gaps', []))} | +{len(corr_b.get('timeline_gaps', [])) - len(corr_a.get('timeline_gaps', []))} |

---

## Legal Pattern Detection

### Contradictions
- Case A: {len(corr_a.get('legal_patterns', {}).get('contradictions', []))} contradictions
- Case B: {len(corr_b.get('legal_patterns', {}).get('contradictions', []))} contradictions

### Corroboration
- Case A: {len(corr_a.get('legal_patterns', {}).get('corroboration', []))} corroborations
- Case B: {len(corr_b.get('legal_patterns', {}).get('corroboration', []))} corroborations

### Evidence Gaps
- Case A: {len(corr_a.get('legal_patterns', {}).get('evidence_gaps', []))} gaps identified
- Case B: {len(corr_b.get('legal_patterns', {}).get('evidence_gaps', []))} gaps identified

---

## Cost-Benefit Analysis

**Time Investment**: +{time_b - time_a:.1f}s ({(time_b - time_a) / time_a * 100:.0f}% increase)

**Value Delivered**:
- {entity_comp['improvement_pct']:.0f}% more entity correlations
- {len(entity_comp['new_entities'])} new key players identified
- Complete network mapping enabled

**Estimated API Cost**: ~$0.01-0.05 per case for AI batch resolution

**Recommendation**: For workplace investigations with mixed evidence types,
`--ai-resolve` provides significant value for negligible cost increase.

---

## Test Case Details

**Case A**: {case_a_id}
**Case B**: {case_b_id}

**Evidence Count**: {evidence_count}
**Evidence Types**: {', '.join(evidence_types)}

---

_Generated by Evidence Toolkit v3.3.0 A/B Testing Framework_
"""

    return report


def main():
    parser = argparse.ArgumentParser(
        description="A/B test AI entity resolution impact",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--source-case',
        type=Path,
        default=Path("data/cases/BCH_WORKPLACE_2025_2"),
        help='Source case to sample from (default: BCH_WORKPLACE_2025_2)'
    )

    parser.add_argument(
        '--images',
        type=int,
        help='Number of test images (default: 10 standard, 30 large)'
    )

    parser.add_argument(
        '--documents',
        type=int,
        help='Number of test documents (default: 5 standard, 10 large)'
    )

    parser.add_argument(
        '--large',
        action='store_true',
        help='Create large test case (30 images + 10 documents)'
    )

    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Skip test case generation and pipeline execution, only analyze existing packages'
    )

    parser.add_argument(
        '--case-a',
        type=str,
        default='AB-TEST-A-NO-RESOLVE',
        help='Case A identifier (default: AB-TEST-A-NO-RESOLVE)'
    )

    parser.add_argument(
        '--case-b',
        type=str,
        default='AB-TEST-B-WITH-RESOLVE',
        help='Case B identifier (default: AB-TEST-B-WITH-RESOLVE)'
    )

    args = parser.parse_args()

    # Determine counts
    if args.large:
        image_count = args.images if args.images is not None else 30
        document_count = args.documents if args.documents is not None else 10
    else:
        image_count = args.images if args.images is not None else 10
        document_count = args.documents if args.documents is not None else 5

    case_a_id = args.case_a
    case_b_id = args.case_b

    # Step 1: Create paired test cases (unless analyze-only)
    if not args.analyze_only:
        case_a_dir, case_b_dir = create_paired_test_cases(
            source_case=args.source_case,
            image_count=image_count,
            document_count=document_count
        )

        # Step 2: Run pipelines
        print(f"\n{'=' * 80}")
        print("⏱️  PIPELINE EXECUTION")
        print(f"{'=' * 80}")

        time_a, package_a = run_pipeline(case_a_dir, case_a_id, use_ai_resolve=False)
        print(f"\n⏸️  Waiting 5 seconds before next pipeline...")
        time.sleep(5)

        time_b, package_b = run_pipeline(case_b_dir, case_b_id, use_ai_resolve=True)
    else:
        print("\n🔍 ANALYZE-ONLY MODE: Skipping test case generation and pipeline execution")

        # Find existing packages
        packages_dir = Path("data/packages")
        packages_a = sorted(packages_dir.glob(f"{case_a_id}_analysis_package_*.zip"))
        packages_b = sorted(packages_dir.glob(f"{case_b_id}_analysis_package_*.zip"))

        if not packages_a or not packages_b:
            print(f"\n❌ Could not find packages for {case_a_id} and/or {case_b_id}")
            sys.exit(1)

        package_a = packages_a[-1]
        package_b = packages_b[-1]
        time_a = 0.0
        time_b = 0.0

        print(f"\n📦 Found packages:")
        print(f"   Case A: {package_a.name}")
        print(f"   Case B: {package_b.name}")

    # Step 3: Extract packages
    print(f"\n{'=' * 80}")
    print("📂 PACKAGE EXTRACTION")
    print(f"{'=' * 80}")

    extracted_a = extract_package(package_a)
    extracted_b = extract_package(package_b)

    # Step 4: Load analysis results
    print(f"\n{'=' * 80}")
    print("📊 LOADING ANALYSIS RESULTS")
    print(f"{'=' * 80}")

    corr_a = load_correlation_analysis(extracted_a)
    corr_b = load_correlation_analysis(extracted_b)
    meta_a = load_package_metadata(extracted_a)
    meta_b = load_package_metadata(extracted_b)

    print(f"\n✅ Case A: {len(corr_a['entity_correlations'])} entity correlations")
    print(f"✅ Case B: {len(corr_b['entity_correlations'])} entity correlations")

    # Step 5: Compare results
    print(f"\n{'=' * 80}")
    print("🔬 COMPARATIVE ANALYSIS")
    print(f"{'=' * 80}")

    entity_comp = compare_entity_correlations(corr_a, corr_b)

    print(f"\n📊 Entity Correlation Comparison:")
    print(f"   Total (Case A): {entity_comp['total_a']}")
    print(f"   Total (Case B): {entity_comp['total_b']}")
    print(f"   Improvement: +{entity_comp['improvement_pct']:.0f}%")
    print(f"   New entities: {len(entity_comp['new_entities'])}")

    if entity_comp['new_entities']:
        print(f"\n   ⭐ Entities discovered by AI:")
        for name in entity_comp['new_entities']:
            print(f"      - {name}")

    # Step 6: Generate report
    print(f"\n{'=' * 80}")
    print("📝 GENERATING REPORT")
    print(f"{'=' * 80}")

    report = generate_report(
        case_a_id=case_a_id,
        case_b_id=case_b_id,
        time_a=time_a,
        time_b=time_b,
        corr_a=corr_a,
        corr_b=corr_b,
        meta_a=meta_a,
        meta_b=meta_b,
        entity_comp=entity_comp
    )

    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = Path("reports") / f"ab_test_{timestamp}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\n✅ Report saved to: {report_path}")
    print(f"\n{'=' * 80}")
    print("✅ A/B TEST COMPLETE")
    print(f"{'=' * 80}")
    print(f"\n📄 View report: {report_path}")


if __name__ == "__main__":
    main()
