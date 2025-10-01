#!/usr/bin/env python3
"""Validate cross-evidence analysis JSON payloads against the V1 schema.

This validation script ensures that cross-evidence analysis results maintain
forensic integrity and comply with the canonical schema requirements.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

from jsonschema import Draft7Validator, exceptions


DEFAULT_CROSS_SCHEMA_PATH = Path("schemas/cross-analysis.v1.json")
DEFAULT_EVIDENCE_SCHEMAS = {
    "document": Path("document-evidence-analyzer/schemas/document.v1.json"),
    "image": Path("image-analysis/schemas/images.v1.json")
}


def load_json(path: Path) -> dict:
    """Load and parse JSON file with error handling."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise SystemExit(f"error: file not found -> {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: invalid JSON in {path}: {exc}")


def format_error(error: exceptions.ValidationError) -> str:
    """Format validation error with clear location information."""
    location = "/".join(str(part) for part in error.path) or "<root>"
    return f"{location}: {error.message}"


def validate_cross_analysis(instance_path: Path, schema_path: Path) -> int:
    """Validate cross-analysis file against schema.

    Returns:
        0 if validation passes, 1 if validation fails
    """
    schema = load_json(schema_path)
    instance = load_json(instance_path)

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda err: err.path)

    if errors:
        print(f"Cross-analysis validation failed for {instance_path}")
        print(f"Schema: {schema_path}")
        for error in errors:
            print(f" - {format_error(error)}")
        return 1

    print(f"Cross-analysis validation passed for {instance_path}")
    return 0


def validate_evidence_references(cross_analysis: Dict[str, Any],
                                evidence_schema_paths: Dict[str, Path]) -> List[str]:
    """Validate that referenced evidence bundles exist and are valid.

    Args:
        cross_analysis: Parsed cross-analysis JSON
        evidence_schema_paths: Mapping of evidence types to schema paths

    Returns:
        List of validation errors
    """
    errors = []
    evidence_refs = cross_analysis.get("evidence_references", [])

    for ref in evidence_refs:
        evidence_type = ref.get("evidence_type")
        bundle_path = ref.get("bundle_path")
        sha256 = ref.get("sha256")

        if not bundle_path:
            errors.append(f"Missing bundle_path for evidence {sha256}")
            continue

        bundle_file = Path(bundle_path)
        if not bundle_file.exists():
            errors.append(f"Evidence bundle not found: {bundle_path}")
            continue

        # Validate the referenced evidence bundle
        if evidence_type in evidence_schema_paths:
            schema_path = evidence_schema_paths[evidence_type]
            if schema_path.exists():
                try:
                    schema = load_json(schema_path)
                    evidence_bundle = load_json(bundle_file)

                    validator = Draft7Validator(schema)
                    bundle_errors = list(validator.iter_errors(evidence_bundle))

                    if bundle_errors:
                        errors.append(f"Referenced evidence bundle {bundle_path} is invalid:")
                        for error in bundle_errors[:3]:  # Limit to first 3 errors
                            errors.append(f"  - {format_error(error)}")
                        if len(bundle_errors) > 3:
                            errors.append(f"  ... and {len(bundle_errors) - 3} more errors")

                    # Verify SHA256 matches
                    bundle_sha256 = evidence_bundle.get("evidence", {}).get("sha256")
                    if bundle_sha256 != sha256:
                        errors.append(f"SHA256 mismatch in {bundle_path}: expected {sha256}, found {bundle_sha256}")

                except Exception as e:
                    errors.append(f"Error validating referenced bundle {bundle_path}: {e}")
            else:
                errors.append(f"Schema not found for evidence type {evidence_type}: {schema_path}")
        else:
            errors.append(f"Unknown evidence type: {evidence_type}")

    return errors


def validate_cross_analysis_integrity(cross_analysis: Dict[str, Any]) -> List[str]:
    """Perform additional integrity checks on cross-analysis data.

    Args:
        cross_analysis: Parsed cross-analysis JSON

    Returns:
        List of integrity check errors
    """
    errors = []

    # Check that all evidence references are used in analysis results
    evidence_refs = cross_analysis.get("evidence_references", [])
    referenced_sha256s = {ref.get("sha256") for ref in evidence_refs}

    analysis_results = cross_analysis.get("analysis_results", {})

    # Check entity correlation references
    entity_corr = analysis_results.get("entity_correlation", {})
    correlated_entities = entity_corr.get("correlated_entities", [])

    used_sha256s = set()
    for entity in correlated_entities:
        for occurrence in entity.get("evidence_occurrences", []):
            used_sha256s.add(occurrence.get("evidence_sha256"))

    # Check timeline analysis references
    timeline = analysis_results.get("timeline_analysis", {})
    temporal_events = timeline.get("temporal_events", [])

    for event in temporal_events:
        used_sha256s.add(event.get("evidence_sha256"))

    # Check narrative consistency references
    narrative = analysis_results.get("narrative_consistency", {})

    for contradiction in narrative.get("contradictions", []):
        used_sha256s.update(contradiction.get("evidence_pair", []))

    for support_group in narrative.get("supporting_evidence", []):
        used_sha256s.update(support_group.get("evidence_group", []))

    for theme in narrative.get("narrative_themes", []):
        used_sha256s.update(theme.get("supporting_evidence", []))

    # Check for unreferenced evidence
    unreferenced = referenced_sha256s - used_sha256s
    if unreferenced:
        errors.append(f"Evidence referenced but not used in analysis: {', '.join(unreferenced)}")

    # Check for invalid evidence references in analysis
    invalid_refs = used_sha256s - referenced_sha256s
    if invalid_refs:
        errors.append(f"Analysis references evidence not in evidence_references: {', '.join(invalid_refs)}")

    # Validate confidence scores are consistent
    overall_confidence = analysis_results.get("confidence_overall", 0)
    if overall_confidence < 0 or overall_confidence > 1:
        errors.append(f"Overall confidence score out of range: {overall_confidence}")

    return errors


def comprehensive_validation(instance_path: Path,
                           schema_path: Path,
                           evidence_schema_paths: Dict[str, Path],
                           validate_references: bool = True,
                           validate_integrity: bool = True) -> int:
    """Perform comprehensive validation of cross-analysis file.

    Args:
        instance_path: Path to cross-analysis JSON file
        schema_path: Path to cross-analysis schema
        evidence_schema_paths: Mapping of evidence types to schema paths
        validate_references: Whether to validate referenced evidence bundles
        validate_integrity: Whether to perform integrity checks

    Returns:
        0 if all validations pass, 1 if any validation fails
    """
    # First, validate against the schema
    schema_result = validate_cross_analysis(instance_path, schema_path)
    if schema_result != 0:
        return schema_result

    # Load the validated instance for additional checks
    cross_analysis = load_json(instance_path)
    total_errors = []

    # Validate evidence references if requested
    if validate_references:
        ref_errors = validate_evidence_references(cross_analysis, evidence_schema_paths)
        total_errors.extend(ref_errors)

    # Validate integrity if requested
    if validate_integrity:
        integrity_errors = validate_cross_analysis_integrity(cross_analysis)
        total_errors.extend(integrity_errors)

    if total_errors:
        print(f"\nAdditional validation errors for {instance_path}:")
        for error in total_errors:
            print(f" - {error}")
        return 1

    if validate_references or validate_integrity:
        print(f"Comprehensive validation passed for {instance_path}")

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate cross-evidence analysis JSON against schema and integrity checks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic schema validation
  python validate_cross_analysis.py analysis.json

  # Comprehensive validation with reference checking
  python validate_cross_analysis.py analysis.json --comprehensive

  # Custom schema locations
  python validate_cross_analysis.py analysis.json --schema custom-schema.json
        """
    )

    parser.add_argument(
        "instance",
        type=Path,
        help="Path to the cross-analysis JSON file to validate"
    )

    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_CROSS_SCHEMA_PATH,
        help=f"Path to the cross-analysis schema (default: {DEFAULT_CROSS_SCHEMA_PATH})"
    )

    parser.add_argument(
        "--document-schema",
        type=Path,
        default=DEFAULT_EVIDENCE_SCHEMAS["document"],
        help="Path to document evidence schema"
    )

    parser.add_argument(
        "--image-schema",
        type=Path,
        default=DEFAULT_EVIDENCE_SCHEMAS["image"],
        help="Path to image evidence schema"
    )

    parser.add_argument(
        "--comprehensive",
        action="store_true",
        help="Perform comprehensive validation including reference and integrity checks"
    )

    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Only validate against schema, skip reference and integrity checks"
    )

    return parser.parse_args()


def main() -> None:
    """Main validation entry point."""
    args = parse_args()

    # Build evidence schema mapping
    evidence_schemas = {
        "document": args.document_schema,
        "image": args.image_schema
    }

    if args.schema_only:
        # Only schema validation
        exit_code = validate_cross_analysis(args.instance, args.schema)
    elif args.comprehensive:
        # Full comprehensive validation
        exit_code = comprehensive_validation(
            args.instance,
            args.schema,
            evidence_schemas,
            validate_references=True,
            validate_integrity=True
        )
    else:
        # Default: schema + integrity checks, no reference validation
        exit_code = comprehensive_validation(
            args.instance,
            args.schema,
            evidence_schemas,
            validate_references=False,
            validate_integrity=True
        )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()