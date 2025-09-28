#!/bin/bash

# validate_cross_analyses.sh
# CI/CD validation script for cross-evidence analysis files
# Ensures all cross-analysis outputs maintain forensic integrity

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CROSS_SCHEMA_PATH="$PROJECT_ROOT/schemas/cross-analysis.v1.json"
VALIDATOR_SCRIPT="$PROJECT_ROOT/validate_cross_analysis.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_FILES=0
VALID_FILES=0
INVALID_FILES=0

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo
    print_status "$BLUE" "=================================="
    print_status "$BLUE" "Cross-Analysis Validation Pipeline"
    print_status "$BLUE" "=================================="
    echo
}

print_summary() {
    echo
    print_status "$BLUE" "========================================="
    print_status "$BLUE" "Cross-Analysis Validation Summary"
    print_status "$BLUE" "========================================="
    echo
    echo "Total files processed: $TOTAL_FILES"
    echo "Valid files: $VALID_FILES"
    echo "Invalid files: $INVALID_FILES"
    echo

    if [ $INVALID_FILES -eq 0 ]; then
        print_status "$GREEN" "✅ All cross-analysis files passed validation!"
        return 0
    else
        print_status "$RED" "❌ Some cross-analysis files failed validation"
        return 1
    fi
}

validate_file() {
    local file_path=$1
    local validation_mode=${2:-"default"}

    print_status "$BLUE" "Validating: $file_path"

    TOTAL_FILES=$((TOTAL_FILES + 1))

    # Check if validator script exists
    if [ ! -f "$VALIDATOR_SCRIPT" ]; then
        print_status "$RED" "❌ Validator script not found: $VALIDATOR_SCRIPT"
        INVALID_FILES=$((INVALID_FILES + 1))
        return 1
    fi

    # Check if schema exists
    if [ ! -f "$CROSS_SCHEMA_PATH" ]; then
        print_status "$RED" "❌ Schema not found: $CROSS_SCHEMA_PATH"
        INVALID_FILES=$((INVALID_FILES + 1))
        return 1
    fi

    # Run validation based on mode
    local validation_cmd
    case "$validation_mode" in
        "comprehensive")
            validation_cmd="python3 $VALIDATOR_SCRIPT '$file_path' --comprehensive"
            ;;
        "schema-only")
            validation_cmd="python3 $VALIDATOR_SCRIPT '$file_path' --schema-only"
            ;;
        *)
            validation_cmd="python3 $VALIDATOR_SCRIPT '$file_path'"
            ;;
    esac

    if eval "$validation_cmd" 2>/dev/null; then
        print_status "$GREEN" "✅ Valid: $file_path"
        VALID_FILES=$((VALID_FILES + 1))
        return 0
    else
        print_status "$RED" "❌ Invalid: $file_path"

        # Show detailed error output
        echo "Error details:"
        eval "$validation_cmd" 2>&1 | sed 's/^/  /' || true
        echo

        INVALID_FILES=$((INVALID_FILES + 1))
        return 1
    fi
}

find_cross_analysis_files() {
    local search_path=${1:-"$PROJECT_ROOT"}

    # Find cross-analysis files using multiple patterns
    find "$search_path" -type f \( \
        -name "*cross-analysis*.json" -o \
        -name "*cross_analysis*.json" -o \
        -name "cross-analysis.v*.json" -o \
        -path "*/evidence/derived/*/cross-analysis.*.json" -o \
        -path "*/cross-analysis/*.json" \
    \) 2>/dev/null | sort
}

validate_all_found_files() {
    local search_path=${1:-"$PROJECT_ROOT"}
    local validation_mode=${2:-"default"}
    local force_validation=${3:-false}

    print_status "$YELLOW" "Searching for cross-analysis files in: $search_path"

    local files
    files=$(find_cross_analysis_files "$search_path")

    if [ -z "$files" ]; then
        if [ "$force_validation" = true ]; then
            print_status "$RED" "❌ No cross-analysis files found for validation"
            return 1
        else
            print_status "$YELLOW" "⚠️  No cross-analysis files found - this may be expected"
            return 0
        fi
    fi

    echo "Found files:"
    echo "$files" | sed 's/^/  - /'
    echo

    local validation_failed=false
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            if ! validate_file "$file" "$validation_mode"; then
                validation_failed=true
                if [ "${FAIL_FAST:-false}" = true ]; then
                    print_status "$RED" "❌ Fail-fast mode enabled, stopping on first error"
                    return 1
                fi
            fi
        fi
    done <<< "$files"

    if [ "$validation_failed" = true ]; then
        return 1
    fi

    return 0
}

show_help() {
    cat << EOF
Usage: $0 [OPTIONS] [FILE_OR_DIRECTORY]

Validate cross-evidence analysis JSON files against the forensic schema.

OPTIONS:
    -h, --help              Show this help message
    -c, --comprehensive     Perform comprehensive validation (includes reference checking)
    -s, --schema-only       Only validate against schema, skip other checks
    -f, --force             Require at least one file to be found for validation
    --fail-fast             Stop on first validation error
    -v, --verbose           Enable verbose output

ARGUMENTS:
    FILE_OR_DIRECTORY       Specific file to validate or directory to search
                           (default: search entire project)

ENVIRONMENT VARIABLES:
    FAIL_FAST              Set to 'true' to enable fail-fast mode
    VALIDATION_MODE        Set to 'comprehensive' or 'schema-only'

EXAMPLES:
    # Validate all cross-analysis files in project
    $0

    # Validate specific file with comprehensive checks
    $0 --comprehensive ./evidence/cross-analysis.json

    # Validate files in specific directory, schema only
    $0 --schema-only ./evidence/

    # CI mode: require files and fail fast
    FAIL_FAST=true $0 --force --comprehensive

EXIT CODES:
    0    All validations passed
    1    One or more validations failed
    2    Script error (missing dependencies, etc.)

EOF
}

check_dependencies() {
    local missing_deps=()

    # Check for Python 3
    if ! command -v python3 >/dev/null 2>&1; then
        missing_deps+=("python3")
    fi

    # Check for required Python packages
    if ! python3 -c "import jsonschema, pydantic" >/dev/null 2>&1; then
        missing_deps+=("jsonschema and/or pydantic Python packages")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_status "$RED" "❌ Missing dependencies:"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        echo
        print_status "$YELLOW" "Please install missing dependencies and try again."
        return 2
    fi

    return 0
}

main() {
    local validation_mode="default"
    local target_path="$PROJECT_ROOT"
    local force_validation=false
    local verbose=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -c|--comprehensive)
                validation_mode="comprehensive"
                shift
                ;;
            -s|--schema-only)
                validation_mode="schema-only"
                shift
                ;;
            -f|--force)
                force_validation=true
                shift
                ;;
            --fail-fast)
                export FAIL_FAST=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                set -x
                shift
                ;;
            -*)
                print_status "$RED" "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                target_path="$1"
                shift
                ;;
        esac
    done

    # Override validation mode from environment if set
    if [ -n "${VALIDATION_MODE:-}" ]; then
        validation_mode="$VALIDATION_MODE"
    fi

    print_header

    # Check dependencies
    if ! check_dependencies; then
        exit 2
    fi

    print_status "$BLUE" "Validation mode: $validation_mode"
    print_status "$BLUE" "Target path: $target_path"
    print_status "$BLUE" "Force validation: $force_validation"
    echo

    # Determine if target is file or directory
    if [ -f "$target_path" ]; then
        # Single file validation
        if validate_file "$target_path" "$validation_mode"; then
            print_status "$GREEN" "✅ File validation completed successfully"
            exit 0
        else
            print_status "$RED" "❌ File validation failed"
            exit 1
        fi
    elif [ -d "$target_path" ]; then
        # Directory validation
        if validate_all_found_files "$target_path" "$validation_mode" "$force_validation"; then
            if ! print_summary; then
                exit 1
            fi
        else
            print_summary
            exit 1
        fi
    else
        print_status "$RED" "❌ Target path does not exist: $target_path"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"