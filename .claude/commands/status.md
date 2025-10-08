---
description: Quick project status - evidence, cases, packages, v3.1/v3.2/vx.x features
allowed-tools: Bash(echo:*), Bash(ls:*), Bash(find:*), Bash(grep:*), Bash(uv run python:*), Bash(awk:*), Bash(cat:*)
---

# Status

Quick project status check - see what evidence, cases, and packages currently exist, plus detection of v3.1/v3.2 AI features.

You can check git logs , commits etc. For example in v3.1 we added these; 

## Execute

```bash
echo "=== EVIDENCE TOOLKIT STATUS ==="
echo ""

echo "📦 Package Version:"
pkg_ver=$(uv run python -c "import evidence_toolkit; print(evidence_toolkit.__version__)" 2>/dev/null)
if [ -n "$pkg_ver" ]; then
    echo "  v${pkg_ver}"
    # Check for v3.1 features in code
    if grep -q "legal_patterns.*LegalPatternAnalysis" src/evidence_toolkit/core/models.py 2>/dev/null; then
        echo "  ✅ v3.1 AI enhancements: PRESENT"
    else
        echo "  ⚠️  v3.1 AI enhancements: NOT FOUND"
    fi
else
    echo "  Package not installed"
fi

echo ""
echo "📁 Root Structure:"
ls -la | grep -E "^d" | awk '{print "  " $9}' | grep -v "^\.$" | grep -v "^\.\.$"

echo ""
echo "📊 Evidence Storage:"
if [ -d data/storage/raw ]; then
    raw_count=$(find data/storage/raw -type f 2>/dev/null | wc -l)
    derived_count=$(find data/storage/derived -type d -name "sha256=*" 2>/dev/null | wc -l)
    echo "  Raw files: $raw_count"
    echo "  Derived analyses: $derived_count"

    # Check for v3.1 analysis features
    if [ $derived_count -gt 0 ]; then
        has_legal_patterns=$(find data/storage/derived -name "*.json" -exec grep -l "legal_patterns" {} \; 2>/dev/null | wc -l)
        if [ $has_legal_patterns -gt 0 ]; then
            echo "  ✨ v3.1 legal patterns: $has_legal_patterns files"
        fi
    fi
elif [ -d evidence/raw ]; then
    echo "  Legacy evidence/: $(find evidence/raw -type f 2>/dev/null | wc -l) files"
else
    echo "  No storage directory yet"
fi

echo ""
echo "📁 Cases:"
if [ -d data/cases/ ]; then
    case_count=$(ls -1 data/cases/ 2>/dev/null | wc -l)
    if [ $case_count -gt 0 ]; then
        ls -1 data/cases/ 2>/dev/null | sed 's/^/  - /'

        # Check for correlation analysis with v3.1 features
        for case_dir in data/cases/*/; do
            case_name=$(basename "$case_dir")
            corr_file="data/storage/cases/$case_name/correlation_analysis.json"
            if [ -f "$corr_file" ]; then
                if grep -q "legal_patterns" "$corr_file" 2>/dev/null; then
                    echo "    ✨ $case_name: v3.1 legal patterns detected"
                fi
            fi
        done
    else
        echo "  No cases in data/cases/"
    fi
elif [ -d cases/ ]; then
    ls -1 cases/ 2>/dev/null | sed 's/^/  - (legacy) /'
else
    echo "  No cases directory yet"
fi
# Use data/packages/ not client_packages
echo ""
echo "📦 Client Packages:"
if [ -d data/packages/ ]; then
    pkg_count=$(ls -1 data/packages/*.zip 2>/dev/null | wc -l)
    if [ $pkg_count -gt 0 ]; then
        ls -1 data/packages/*.zip 2>/dev/null | xargs -n1 basename | sed 's/^/  ✓ /'
    else
        echo "  No ZIP files in data/packages/"
    fi
elif [ -d client_packages/ ]; then
    ls -1 client_packages/*.zip 2>/dev/null | xargs -n1 basename | sed 's/^/  ✓ (legacy) /' || echo "  No packages yet"
else
    echo "  No packages directory yet"
fi

echo ""
echo "🔧 Installed Tools:"
which evidence-toolkit >/dev/null 2>&1 && echo "  ✅ evidence-toolkit CLI installed" || echo "  ❌ evidence-toolkit not found (run: uv pip install -e .)"

echo ""
echo "🤖 AI Features (v3.1):"
echo "  Legal pattern detection: $(grep -c 'LegalPatternAnalysis' src/evidence_toolkit/core/models.py 2>/dev/null || echo 0) model references"
echo "  Power dynamics (deference_score): $(grep -c 'deference_score' src/evidence_toolkit/core/models.py 2>/dev/null || echo 0) field references"
echo "  Enhanced relationships: $(grep -c 'relationship.*Optional' src/evidence_toolkit/core/models.py 2>/dev/null || echo 0) field references"

echo ""
echo "📝 Recent Activity:"
echo "  Last modified (top 5):"
find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.sh" \) 2>/dev/null | grep -v ".venv" | grep -v ".git" | grep -v "archive" | xargs ls -lt 2>/dev/null | head -5 | awk '{print "    " $9 " (" $6 " " $7 " " $8 ")"}'

echo ""
echo "=== END STATUS ==="
```

## Report

Summarize the current state:
- Package version and feature detection status
- How many evidence files are stored with v3.1 AI enhancements
- Whether the CLI is installed
- v3.x AI feature presence: legal patterns, power dynamics, enhanced relationships etc.. 
- Any immediate issues or recommendations
