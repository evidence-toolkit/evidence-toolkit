# Evidence Toolkit A/B Testing Scripts

Comprehensive testing framework for quantifying the impact of AI entity resolution (`--ai-resolve` flag) on correlation analysis, timeline reconstruction, and legal pattern detection.

---

## 📋 Overview

This directory contains three complementary scripts for A/B testing:

1. **`ab_test_ai_resolve.py`** - Main orchestrator (full automated workflow)
2. **`generate_ab_test_cases.py`** - Controlled test case generator (known entity patterns)
3. **`generate_comparison_report.py`** - Post-hoc package comparison (existing packages)

---

## 🚀 Quick Start

### Option 1: Full Automated A/B Test

Run complete workflow (create test cases → run pipelines → generate report):

```bash
# Standard test (10 images + 5 documents)
python scripts/ab_test_ai_resolve.py

# Large test (30 images + 10 documents)
python scripts/ab_test_ai_resolve.py --large

# Custom counts
python scripts/ab_test_ai_resolve.py --images 20 --documents 8
```

**Output**: Comparison report in `reports/ab_test_YYYYMMDD_HHMMSS.md`

---

### Option 2: Manual Step-by-Step Testing

#### Step 1: Generate Controlled Test Cases

```bash
# Create test case with known entity patterns
python scripts/generate_ab_test_cases.py \
    --documents 5 \
    --images 10 \
    --output-dir data/cases/MY-TEST-CASE
```

**Features:**
- Intentional informal/formal name variants (e.g., "Sarah" vs "Sarah Johnson")
- Mixed evidence types (emails with headers, meeting notes, images)
- Ground truth JSON documenting expected correlations

#### Step 2: Run Pipelines Manually

```bash
# Run WITHOUT AI resolution
uv run evidence-toolkit process-case data/cases/MY-TEST-CASE \
    --case-id TEST-NO-AI \
    --case-type workplace

# Run WITH AI resolution
uv run evidence-toolkit process-case data/cases/MY-TEST-CASE \
    --case-id TEST-WITH-AI \
    --case-type workplace \
    --ai-resolve
```

#### Step 3: Compare Results

```bash
# Generate comparison report from packages
python scripts/generate_comparison_report.py \
    data/packages/TEST-NO-AI_analysis_package_*.zip \
    data/packages/TEST-WITH-AI_analysis_package_*.zip \
    --output reports/my_comparison.md \
    --include-summary-diff
```

---

## 📖 Script Documentation

### 1. `ab_test_ai_resolve.py` - Main Orchestrator

**Purpose**: Automated end-to-end A/B testing workflow

**Usage**:
```bash
python scripts/ab_test_ai_resolve.py [OPTIONS]
```

**Options**:
- `--source-case PATH` - Source case to sample from (default: BCH_WORKPLACE_2025_2)
- `--images N` - Number of test images (default: 10 standard, 30 large)
- `--documents N` - Number of test documents (default: 5 standard, 10 large)
- `--large` - Create large test case (30 images + 10 documents)
- `--analyze-only` - Skip generation/execution, analyze existing packages
- `--case-a ID` - Case A identifier (default: AB-TEST-A-NO-RESOLVE)
- `--case-b ID` - Case B identifier (default: AB-TEST-B-WITH-RESOLVE)

**What It Does**:
1. Creates two identical test cases with different SHA256 hashes (using `create_test_case.py`)
2. Runs Case A pipeline **without** `--ai-resolve`
3. Runs Case B pipeline **with** `--ai-resolve`
4. Extracts and compares generated packages
5. Generates comprehensive Markdown report

**Example Output**:
```
reports/ab_test_20251010_120000.md
```

**Key Metrics Tracked**:
- Entity correlation counts (total, new, improved)
- Timeline event reconstruction
- Legal pattern detection (contradictions, corroboration, gaps)
- Processing time comparison
- Estimated API costs

---

### 2. `generate_ab_test_cases.py` - Controlled Test Generator

**Purpose**: Create test cases with known entity patterns for validation

**Usage**:
```bash
python scripts/generate_ab_test_cases.py [OPTIONS]
```

**Options**:
- `--output-dir PATH` - Output directory (default: data/cases/AB-TEST-CONTROLLED)
- `--documents N` - Number of documents (default: 5)
- `--images N` - Number of images (default: 10)

**What It Creates**:

#### Documents
1. **Formal Emails** - Full names in headers: `From: Sarah Johnson <sarah.j@company.com>`
2. **Meeting Notes** - Mixed formal/informal: "Sarah attended..." "Sarah Johnson noted..."
3. **Informal Notes** - First names only: "Paul and Amy discussed..."

#### Images
- PNG images with embedded text mentioning entity names
- Mix of formal ("Paul Boucherat") and informal ("Paul") variants
- Realistic meeting/document scenarios

#### Ground Truth JSON
- Expected correlations documented
- Entity variants listed
- Validation criteria

**Controlled Entities**:
- Sarah Johnson (informal: Sarah, Sarah J, S. Johnson)
- Paul Boucherat (informal: Paul, Paul B, P. Boucherat)
- Amy Martin (informal: Amy, A. Martin)
- Michael Kicks (informal: Michael, Mike Kicks, M. Kicks)
- Rachel Hemmings (informal: Rachel, R. Hemmings)

**Example**:
```bash
python scripts/generate_ab_test_cases.py \
    --documents 5 \
    --images 10

# Creates:
# - 5 text documents with intentional name variants
# - 10 PNG images with embedded entity names
# - 1 GROUND_TRUTH.json with expected correlations
```

---

### 3. `generate_comparison_report.py` - Post-Hoc Analysis

**Purpose**: Analyze and compare two existing evidence packages

**Usage**:
```bash
python scripts/generate_comparison_report.py \
    PACKAGE_A.zip \
    PACKAGE_B.zip \
    [OPTIONS]
```

**Options**:
- `--output PATH` - Report output path (default: reports/comparison_TIMESTAMP.md)
- `--include-summary-diff` - Include executive summary comparison

**What It Analyzes**:
- Entity correlations (found in both, unique to each)
- Occurrence count deltas
- Timeline event differences
- Legal pattern detection comparison
- Package metadata

**Use Cases**:
1. **Compare Different Versions**: Test v3.2 vs v3.3 output
2. **AI Resolution Impact**: Compare with/without `--ai-resolve`
3. **Case Type Comparison**: Generic vs workplace vs contract prompts
4. **Historical Analysis**: Review changes over time

**Example**:
```bash
# Compare your existing FINAL-1-3 and FINAL-2-3-resolve packages
python scripts/generate_comparison_report.py \
    data/packages/FINAL-1-3_analysis_package_20251010_031347.zip \
    data/packages/FINAL-2-3-resolve_analysis_package_20251010_034938.zip \
    --output reports/final_comparison.md \
    --include-summary-diff
```

---

## 📊 Understanding the Reports

### Report Sections

#### 1. **Executive Summary**
Quick metrics table showing:
- Entity correlation improvements (count & percentage)
- Timeline event differences
- Risk flag changes
- Processing time delta

#### 2. **Entity Correlation Analysis**
- **Found in Both**: Entities appearing in both packages (with count deltas)
- **Only in Package A**: Entities missed by Package B
- **Only in Package B**: New entities discovered (⭐ indicates AI resolution)

#### 3. **Legal Pattern Comparison**
- Contradictions detected (count & severity)
- Corroboration strength distribution
- Evidence gaps identified

#### 4. **Timeline Analysis**
- Total events comparison
- Temporal sequence reconstruction
- Timeline gaps detected

#### 5. **Cost-Benefit Analysis**
- Processing time increase
- Estimated API cost
- Value delivered (correlations, network mapping)
- Recommendation

---

## 🎯 Real-World Examples

### Example 1: Validate AI Resolution Impact

**Scenario**: You want to prove AI resolution provides value

```bash
# Generate controlled test case
python scripts/generate_ab_test_cases.py \
    --documents 5 \
    --images 10

# Run full A/B test
python scripts/ab_test_ai_resolve.py \
    --source-case data/cases/AB-TEST-CONTROLLED

# Review report
cat reports/ab_test_*.md
```

**Expected Results**:
- 3-5 new entity correlations discovered
- "Sarah" → "Sarah Johnson" resolution demonstrated
- 50-100% improvement in entity correlation count

---

### Example 2: Compare Your Existing Packages

**Scenario**: You already ran FINAL-1-3 and FINAL-2-3-resolve

```bash
python scripts/generate_comparison_report.py \
    data/packages/FINAL-1-3_analysis_package_*.zip \
    data/packages/FINAL-2-3-resolve_analysis_package_*.zip \
    --output reports/final_packages_comparison.md \
    --include-summary-diff
```

**What You'll Learn**:
- Exactly which 5 entities AI resolution found
- Occurrence count improvements (e.g., Paul: 2 → 3)
- Network mapping enabled by additional correlations

---

### Example 3: Large-Scale Stress Test

**Scenario**: Test performance with 30 images + 10 documents

```bash
python scripts/ab_test_ai_resolve.py --large
```

**Monitors**:
- Processing time at scale
- API cost increase
- Correlation discovery rate
- Memory/performance impact

---

## 🔧 Technical Details

### Hash Spoofing Methods

To ensure clean testing without cached analysis:

**Images (PNG)**:
- Injects random metadata (`test_id`, `timestamp`, `random_data`)
- Preserves visual content
- Guarantees unique SHA256

**Text Documents**:
- Appends invisible trailing whitespace
- Adds UUID comment: `<!-- Test ID: uuid -->`
- Content remains human-readable

**Why This Matters**:
- Same source content, different hashes
- Forces fresh AI analysis
- Prevents cache contamination

### Directory Structure

```
evidence-toolkit/
├── scripts/
│   ├── ab_test_ai_resolve.py          # Main orchestrator
│   ├── generate_ab_test_cases.py      # Controlled generator
│   ├── generate_comparison_report.py  # Post-hoc analysis
│   └── README.md                       # This file
├── data/
│   ├── cases/
│   │   ├── AB-TEST-A-NO-RESOLVE/      # Generated test case A
│   │   ├── AB-TEST-B-WITH-RESOLVE/    # Generated test case B
│   │   └── AB-TEST-CONTROLLED/        # Controlled entities
│   └── packages/                       # Generated packages
└── reports/
    ├── ab_test_YYYYMMDD_HHMMSS.md     # A/B test reports
    └── comparison_YYYYMMDD_HHMMSS.md  # Comparison reports
```

---

## 💡 Best Practices

### When to Use Each Script

**Use `ab_test_ai_resolve.py` when**:
- Running first-time validation
- Need automated end-to-end workflow
- Want standardized comparison metrics
- Testing on sampled real-world data

**Use `generate_ab_test_cases.py` when**:
- Need controlled entity patterns
- Validating specific name resolution scenarios
- Creating reproducible test fixtures
- Building regression test suite

**Use `generate_comparison_report.py` when**:
- Already have two packages to compare
- Comparing historical runs
- Analyzing production vs test outputs
- Quick ad-hoc comparisons

---

## 🐛 Troubleshooting

### Issue: "No packages found for CASE-ID"

**Solution**: Check package directory
```bash
ls -lh data/packages/ | grep CASE-ID
```

If missing, run pipeline manually first.

---

### Issue: "correlation_analysis.json not found"

**Cause**: Incomplete package or old toolkit version

**Solution**: Re-run pipeline with latest toolkit:
```bash
uv run evidence-toolkit process-case data/cases/CASE --case-id CASE
```

---

### Issue: "Only found N entities (expected more)"

**Causes**:
1. Test case too small (use `--large`)
2. All names already formal (no informal variants to resolve)
3. Not enough cross-evidence mentions

**Solution**: Use controlled test generator:
```bash
python scripts/generate_ab_test_cases.py --documents 8 --images 15
```

---

### Issue: Processing takes too long

**Solution**: Reduce test case size
```bash
python scripts/ab_test_ai_resolve.py --images 5 --documents 3
```

Or use `--analyze-only` to skip pipeline execution.

---

## 📈 Interpreting Results

### Good AI Resolution Performance

**Indicators**:
- **Entity correlation improvement**: +50% to +200%
- **New entities discovered**: 3-8 additional people
- **Occurrence count increases**: Existing entities +1 to +3
- **Processing time**: +15-30 seconds
- **Cost**: +$0.01-0.05 per case

**Example Good Result**:
```
Entity Correlations: 3 → 8 (+167%)
New Entities: Sarah Johnson, Michael Kicks, Rachel Hemmings, Ryan Allen, Trish Sullivan
Cost: $0.12 → $0.15 (+$0.03)
Time: 45s → 62s (+17s)
```

---

### Poor/No AI Resolution Impact

**Indicators**:
- **Entity correlation improvement**: 0% to +10%
- **New entities discovered**: 0-1
- **No occurrence count increases**

**Common Causes**:
1. **All names already formal**: No informal variants in evidence
2. **Small case**: Not enough evidence for cross-correlation
3. **Single evidence type**: Documents only, no emails/images
4. **Consistent naming**: Everyone uses full names throughout

**Solution**: Use controlled test generator to create known variants.

---

## 📚 Related Documentation

- [V3_ARCHITECTURE.md](../V3_ARCHITECTURE.md) - Overall toolkit architecture
- [CHANGELOG.md](../CHANGELOG.md) - Version history and features
- [create_test_case.py](../create_test_case.py) - Base test case generator

---

## 🤝 Contributing

To add new test scenarios:

1. Update `TEST_ENTITIES` in `generate_ab_test_cases.py`
2. Add document generation functions
3. Update ground truth JSON format
4. Run validation test
5. Update this README

---

## 📄 License

MIT License - same as parent Evidence Toolkit project

---

_Evidence Toolkit A/B Testing Framework v3.3.0_
