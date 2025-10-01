#!/usr/bin/env python3
"""Simple validation test for cross-analysis schema without external dependencies."""

import json
import sys
from pathlib import Path
from datetime import datetime


def load_json(path: Path) -> dict:
    """Load and parse JSON file."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        print(f"Error: file not found -> {path}")
        return None
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in {path}: {exc}")
        return None


def validate_required_fields(data: dict, required_fields: list, path_prefix: str = "") -> list:
    """Validate that required fields are present."""
    errors = []
    for field in required_fields:
        if field not in data:
            errors.append(f"{path_prefix}Missing required field: {field}")
    return errors


def validate_sha256_format(value: str, field_name: str) -> list:
    """Validate SHA256 format."""
    errors = []
    if not isinstance(value, str):
        errors.append(f"{field_name} must be a string")
    elif len(value) != 64:
        errors.append(f"{field_name} must be 64 characters long")
    elif not all(c in "0123456789abcdef" for c in value.lower()):
        errors.append(f"{field_name} must contain only hexadecimal characters")
    return errors


def validate_confidence_score(value, field_name: str) -> list:
    """Validate confidence score is between 0.0 and 1.0."""
    errors = []
    if not isinstance(value, (int, float)):
        errors.append(f"{field_name} must be a number")
    elif value < 0.0 or value > 1.0:
        errors.append(f"{field_name} must be between 0.0 and 1.0")
    return errors


def validate_cross_analysis_basic(data: dict) -> list:
    """Perform basic validation of cross-analysis structure."""
    errors = []

    # Check top-level required fields
    required_top_level = ["schema_version", "analysis_metadata", "evidence_references", "analysis_results"]
    errors.extend(validate_required_fields(data, required_top_level))

    if "schema_version" in data and data["schema_version"] != "1.0.0":
        errors.append(f"Expected schema_version '1.0.0', got '{data['schema_version']}'")

    # Validate analysis_metadata
    if "analysis_metadata" in data:
        metadata = data["analysis_metadata"]
        required_metadata = ["analysis_id", "created_at", "analyst", "analysis_type", "version"]
        errors.extend(validate_required_fields(metadata, required_metadata, "analysis_metadata."))

        if "analysis_type" in metadata:
            valid_types = ["entity_correlation", "timeline_analysis", "narrative_consistency", "comprehensive"]
            if metadata["analysis_type"] not in valid_types:
                errors.append(f"analysis_metadata.analysis_type must be one of {valid_types}")

    # Validate evidence_references
    if "evidence_references" in data:
        evidence_refs = data["evidence_references"]
        if not isinstance(evidence_refs, list):
            errors.append("evidence_references must be an array")
        elif len(evidence_refs) < 2:
            errors.append("evidence_references must contain at least 2 items")
        else:
            for i, ref in enumerate(evidence_refs):
                prefix = f"evidence_references[{i}]."
                required_ref = ["evidence_id", "sha256", "evidence_type", "bundle_path"]
                errors.extend(validate_required_fields(ref, required_ref, prefix))

                if "sha256" in ref:
                    errors.extend(validate_sha256_format(ref["sha256"], f"{prefix}sha256"))

                if "evidence_type" in ref:
                    valid_evidence_types = ["document", "image", "email", "pdf", "audio", "video", "other"]
                    if ref["evidence_type"] not in valid_evidence_types:
                        errors.append(f"{prefix}evidence_type must be one of {valid_evidence_types}")

    # Validate analysis_results
    if "analysis_results" in data:
        results = data["analysis_results"]
        if "confidence_overall" not in results:
            errors.append("analysis_results.confidence_overall is required")
        else:
            errors.extend(validate_confidence_score(results["confidence_overall"], "analysis_results.confidence_overall"))

        # Validate entity correlation if present
        if "entity_correlation" in results:
            entity_corr = results["entity_correlation"]
            if "correlated_entities" in entity_corr:
                entities = entity_corr["correlated_entities"]
                if isinstance(entities, list):
                    for i, entity in enumerate(entities):
                        prefix = f"analysis_results.entity_correlation.correlated_entities[{i}]."
                        required_entity = ["entity_name", "entity_type", "evidence_occurrences", "correlation_confidence"]
                        errors.extend(validate_required_fields(entity, required_entity, prefix))

                        if "correlation_confidence" in entity:
                            errors.extend(validate_confidence_score(entity["correlation_confidence"], f"{prefix}correlation_confidence"))

                        if "evidence_occurrences" in entity:
                            occurrences = entity["evidence_occurrences"]
                            if isinstance(occurrences, list):
                                if len(occurrences) < 2:
                                    errors.append(f"{prefix}evidence_occurrences must contain at least 2 items")
                                for j, occ in enumerate(occurrences):
                                    occ_prefix = f"{prefix}evidence_occurrences[{j}]."
                                    if "evidence_sha256" in occ:
                                        errors.extend(validate_sha256_format(occ["evidence_sha256"], f"{occ_prefix}evidence_sha256"))
                                    if "confidence" in occ:
                                        errors.extend(validate_confidence_score(occ["confidence"], f"{occ_prefix}confidence"))

        # Validate timeline analysis if present
        if "timeline_analysis" in results:
            timeline = results["timeline_analysis"]
            if "temporal_events" in timeline:
                events = timeline["temporal_events"]
                if isinstance(events, list):
                    for i, event in enumerate(events):
                        prefix = f"analysis_results.timeline_analysis.temporal_events[{i}]."
                        if "evidence_sha256" in event:
                            errors.extend(validate_sha256_format(event["evidence_sha256"], f"{prefix}evidence_sha256"))
                        if "confidence" in event:
                            errors.extend(validate_confidence_score(event["confidence"], f"{prefix}confidence"))

    return errors


def test_schema_structure():
    """Test that the schema file has the expected structure."""
    print("Testing schema structure...")

    schema_path = Path("schemas/cross-analysis.v1.json")
    schema = load_json(schema_path)

    if schema is None:
        return False

    # Check schema metadata
    expected_schema_fields = ["$schema", "$id", "title", "type", "additionalProperties", "required", "properties"]
    missing_fields = [field for field in expected_schema_fields if field not in schema]

    if missing_fields:
        print(f"❌ Schema missing required fields: {missing_fields}")
        return False

    if schema.get("type") != "object":
        print(f"❌ Expected schema type 'object', got '{schema.get('type')}'")
        return False

    if schema.get("additionalProperties") is not False:
        print(f"❌ Expected additionalProperties: false for forensic compliance")
        return False

    required_props = schema.get("required", [])
    expected_required = ["schema_version", "analysis_metadata", "evidence_references", "analysis_results"]
    missing_required = [prop for prop in expected_required if prop not in required_props]

    if missing_required:
        print(f"❌ Schema missing required properties: {missing_required}")
        return False

    print("✅ Schema structure validation passed")
    return True


def test_example_validation():
    """Test that the example file validates against the schema requirements."""
    print("Testing example validation...")

    example_path = Path("examples/cross-analysis-example.json")
    example = load_json(example_path)

    if example is None:
        return False

    errors = validate_cross_analysis_basic(example)

    if errors:
        print("❌ Example validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False

    print("✅ Example validation passed")
    return True


def test_schema_consistency():
    """Test consistency between schema definitions and example data."""
    print("Testing schema-example consistency...")

    schema_path = Path("schemas/cross-analysis.v1.json")
    example_path = Path("examples/cross-analysis-example.json")

    schema = load_json(schema_path)
    example = load_json(example_path)

    if schema is None or example is None:
        return False

    # Check that example has all required top-level fields from schema
    schema_required = schema.get("required", [])
    example_keys = set(example.keys())

    missing_in_example = [field for field in schema_required if field not in example_keys]
    if missing_in_example:
        print(f"❌ Example missing required fields from schema: {missing_in_example}")
        return False

    # Check schema version consistency
    schema_version_def = schema.get("properties", {}).get("schema_version", {})
    if "const" in schema_version_def:
        expected_version = schema_version_def["const"]
        actual_version = example.get("schema_version")
        if actual_version != expected_version:
            print(f"❌ Version mismatch: schema expects '{expected_version}', example has '{actual_version}'")
            return False

    print("✅ Schema-example consistency validation passed")
    return True


def main():
    """Run all validation tests."""
    print("Cross-Analysis Schema Validation Test Suite")
    print("=" * 50)

    tests = [
        ("Schema Structure", test_schema_structure),
        ("Example Validation", test_example_validation),
        ("Schema Consistency", test_schema_consistency),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! Cross-analysis schema is valid.")
        return 0
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())