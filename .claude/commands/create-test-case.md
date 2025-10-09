---
description: Create mixed-evidence test case for comprehensive pipeline testing
allowed-tools: Bash(python create_test_case.py:*), Bash(ls:*), Bash(echo:*), Bash(find:*)
argument-hint: [--large] [--images-only]
---

# Create Test Case

Quick test case generation with hash-spoofed evidence for comprehensive pipeline testing.

**Samples from BCH_WORKPLACE_2025_2 case** with unique SHA256 hashes for clean testing:
- Standard: 10 images + 3 documents
- Large: 50 images + 10 documents
- Images-only: Backward compatibility mode

## Context

**Available source cases:**
!`ls -d data/cases/*/`

**Current test case status:**
!`ls -lh data/cases/TEST-CASE/ 2>/dev/null || echo "No test case exists yet"`

---

## Your Task

Execute the test case generator based on the user's arguments:

### Arguments
- **No args**: Standard test case (10 images + 3 documents)
- **`--large`**: Large test case (50 images + 10 documents)
- **`--images-only`**: Only images (backward compatibility)

### Execution

Parse arguments and run the appropriate command:

```bash
# Determine mode from arguments
if [ "$1" = "--large" ]; then
    echo "🧪 Creating LARGE test case (50 images + 10 documents)..."
    python create_test_case.py --large
elif [ "$1" = "--images-only" ]; then
    echo "🧪 Creating IMAGES-ONLY test case (10 images)..."
    python create_test_case.py --images-only
else
    echo "🧪 Creating STANDARD test case (10 images + 3 documents)..."
    python create_test_case.py
fi
```

### Post-Creation Instructions

After successful creation, inform the user:

```
✅ Test case created at: data/cases/TEST-CASE/

🚀 Run pipeline:
   uv run evidence-toolkit process-case data/cases/TEST-CASE --case-id TEST-CASE

🎯 With v3.2+ features:
   uv run evidence-toolkit process-case data/cases/TEST-CASE \
       --case-id TEST-CASE \
       --case-type workplace \
       --ai-resolve

⚡ With parallel processing (v3.3.1+):
   uv run evidence-toolkit process-case data/cases/TEST-CASE \
       --case-id TEST-CASE \
       --max-concurrent 5

💡 All evidence files have unique SHA256 hashes for clean analysis
```

---

## Notes

**Hash Spoofing Methods:**
- Images: PNG metadata injection
- Text files: Invisible trailing whitespace + UUID comment
- Future: PDF metadata, EML headers (when available in source case)

**Source Case:**
Default: `data/cases/BCH_WORKPLACE_2025_2/` (real workplace investigation evidence)

**Output:**
Always creates/overwrites: `data/cases/TEST-CASE/`

**Use Cases:**
- Quick development testing
- Pipeline benchmarking
- Feature validation (AI entity resolution, case types, parallel processing)
- Regression testing
