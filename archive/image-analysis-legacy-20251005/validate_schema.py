#!/usr/bin/env python3
"""Validate evidence JSON payloads against the V1 schema."""

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator, exceptions

DEFAULT_SCHEMA_PATH = Path("schemas/images.v1.json")


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise SystemExit(f"error: file not found -> {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: invalid JSON in {path}: {exc}")


def format_error(error: exceptions.ValidationError) -> str:
    location = "/".join(str(part) for part in error.path) or "<root>"
    return f"{location}: {error.message}"


def validate(instance_path: Path, schema_path: Path) -> int:
    schema = load_json(schema_path)
    instance = load_json(instance_path)

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda err: err.path)
    if errors:
        print(f"Validation failed for {instance_path} (schema: {schema_path})")
        for error in errors:
            print(f" - {format_error(error)}")
        return 1

    print(f"Validation passed for {instance_path} (schema: {schema_path})")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an evidence JSON file against the V1 schema."
    )
    parser.add_argument(
        "instance",
        type=Path,
        help="Path to the JSON file to validate",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA_PATH,
        help=f"Path to the JSON schema (default: {DEFAULT_SCHEMA_PATH})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    exit_code = validate(args.instance, args.schema)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
