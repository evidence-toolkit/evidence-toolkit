#!/usr/bin/env python3
"""Document analysis validation using JSON schema."""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

from jsonschema import Draft7Validator, exceptions


class DocumentValidator:
    """Validates document analysis results against the document.v1.json schema."""

    def __init__(self, schema_path: Path = None):
        """Initialize validator with schema path."""
        if schema_path is None:
            # Default schema path relative to package location
            package_root = Path(__file__).parent.parent.parent
            schema_path = package_root / "schemas" / "document.v1.json"

        self.schema_path = schema_path
        self.schema = self._load_schema()
        self.validator = Draft7Validator(self.schema)

    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema from file."""
        try:
            with self.schema_path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError:
            raise SystemExit(f"error: schema file not found -> {self.schema_path}")
        except json.JSONDecodeError as exc:
            raise SystemExit(f"error: invalid JSON in schema {self.schema_path}: {exc}")

    def validate(self, analysis_data: Dict[str, Any]) -> List[str]:
        """
        Validate analysis data against schema.

        Args:
            analysis_data: Dictionary containing analysis results to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = sorted(self.validator.iter_errors(analysis_data), key=lambda err: err.path)
        return [self._format_error(error) for error in errors]

    def validate_file(self, file_path: Path) -> List[str]:
        """
        Validate analysis file against schema.

        Args:
            file_path: Path to JSON file to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        try:
            with file_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            return self.validate(data)
        except FileNotFoundError:
            return [f"file not found: {file_path}"]
        except json.JSONDecodeError as exc:
            return [f"invalid JSON in {file_path}: {exc}"]

    def validate_and_raise(self, analysis_data: Dict[str, Any]) -> None:
        """
        Validate analysis data and raise exception if invalid.

        Args:
            analysis_data: Dictionary containing analysis results to validate

        Raises:
            ValueError: If validation fails
        """
        errors = self.validate(analysis_data)
        if errors:
            error_msg = f"Schema validation failed:\n" + "\n".join(f" - {error}" for error in errors)
            raise ValueError(error_msg)

    def _format_error(self, error: exceptions.ValidationError) -> str:
        """Format validation error for display."""
        location = "/".join(str(part) for part in error.path) or "<root>"
        return f"{location}: {error.message}"


def validate_document_analysis(analysis_data: Dict[str, Any], schema_path: Path = None) -> List[str]:
    """
    Convenience function to validate document analysis data.

    Args:
        analysis_data: Analysis results to validate
        schema_path: Optional path to schema file

    Returns:
        List of validation error messages (empty if valid)
    """
    validator = DocumentValidator(schema_path)
    return validator.validate(analysis_data)


def validate_document_analysis_file(file_path: Path, schema_path: Path = None) -> List[str]:
    """
    Convenience function to validate document analysis file.

    Args:
        file_path: Path to analysis JSON file
        schema_path: Optional path to schema file

    Returns:
        List of validation error messages (empty if valid)
    """
    validator = DocumentValidator(schema_path)
    return validator.validate_file(file_path)


def main() -> None:
    """CLI entry point for standalone validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate a document analysis JSON file against the V1 schema."
    )
    parser.add_argument(
        "instance",
        type=Path,
        help="Path to the JSON file to validate",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        help="Path to the JSON schema (default: schemas/document.v1.json)",
    )
    args = parser.parse_args()

    validator = DocumentValidator(args.schema)
    errors = validator.validate_file(args.instance)

    if errors:
        print(f"Validation failed for {args.instance} (schema: {validator.schema_path})")
        for error in errors:
            print(f" - {error}")
        sys.exit(1)
    else:
        print(f"Validation passed for {args.instance} (schema: {validator.schema_path})")
        sys.exit(0)


if __name__ == "__main__":
    main()