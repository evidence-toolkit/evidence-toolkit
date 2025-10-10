# Quick Start: A/B Testing AI Entity Resolution

**Goal**: Prove that `--ai-resolve` finds more entity correlations than string matching alone

**Time**: 5-10 minutes

---

## Option 1: Automated (Recommended for First Run)

### Run Full A/B Test in One Command

```bash
# Standard test (10 images + 5 documents from real case)
python scripts/ab_test_ai_resolve.py

# Wait 2-3 minutes for pipeline execution...
```

**What Happens**:
1. ✅ Creates two identical test cases (AB-TEST-A-NO-RESOLVE, AB-TEST-B-WITH-RESOLVE)
2. ✅ Runs Case A without AI resolution
3. ✅ Runs Case B with AI resolution
4. ✅ Generates comparison report in `reports/ab_test_YYYYMMDD_HHMMSS.md`

### View Results

```bash
# Find the latest report
ls -lht reports/ab_test_*.md | head -1

# Read it
cat reports/ab_test_*.md
```

**Expected Results**:
- Entity correlations: 3-5 → 8-12 (+100-200%)
- New entities discovered: 5-7 people
- Processing time: +15-30 seconds
- Cost: +$0.01-0.05

---

## Option 2: Controlled (Known Entity Patterns)

### Step 1: Generate Test Case with Known Variants

```bash
python scripts/generate_ab_test_cases.py \
    --documents 5 \
    --images 10 \
    --output-dir data/cases/CONTROLLED-TEST
```

**Creates**:
- 5 documents with intentional "Sarah" vs "Sarah Johnson" variants
- 10 images with embedded entity names
- GROUND_TRUTH.json documenting expected correlations

### Step 2: Run WITHOUT AI Resolution

```bash
uv run evidence-toolkit process-case data/cases/CONTROLLED-TEST \
    --case-id CONTROLLED-NO-AI \
    --case-type workplace
```

### Step 3: Run WITH AI Resolution

```bash
uv run evidence-toolkit process-case data/cases/CONTROLLED-TEST \
    --case-id CONTROLLED-WITH-AI \
    --case-type workplace \
    --ai-resolve
```

### Step 4: Compare Results

```bash
python scripts/generate_comparison_report.py \
    data/packages/CONTROLLED-NO-AI_analysis_package_*.zip \
    data/packages/CONTROLLED-WITH-AI_analysis_package_*.zip \
    --output reports/controlled_comparison.md \
    --include-summary-diff
```

### Step 5: View Report

```bash
cat reports/controlled_comparison.md
```

**Expected Results**:
- Sarah + Sarah Johnson → resolved to 1 entity (Sarah Johnson)
- Paul + Paul Boucherat → resolved to 1 entity (Paul Boucherat)
- Amy + A. Martin → resolved to 1 entity (Amy Martin)
- Total: 5 canonical entities with 10-15 total occurrences

---

## Option 3: Compare Your Existing Packages

If you've already run pipelines with/without `--ai-resolve`:

```bash
python scripts/generate_comparison_report.py \
    data/packages/FINAL-1-3_analysis_package_*.zip \
    data/packages/FINAL-2-3-resolve_analysis_package_*.zip \
    --output reports/your_comparison.md \
    --include-summary-diff
```

---

## Interpreting Results

### Look For

✅ **Entities Only in Package B** section:
- New people discovered by AI resolution
- Should see ⭐ markers

✅ **Summary Table**:
- Entity Correlations delta (e.g., +167%)
- Processing Time delta (e.g., +17s)

✅ **Cost-Benefit Analysis**:
- Recommendation for workplace investigations

### Example Good Result

```markdown
| Metric | Package A (No AI) | Package B (With AI) | Improvement |
|--------|-------------------|---------------------|-------------|
| Entity Correlations | 3 | 8 | **+167%** |
| Timeline Events | 25 | 41 | +64% |

### Entities Only in Package B

- **Sarah Johnson** (person) - 3 occurrences ⭐ (AI resolved "Sarah" → "Sarah Johnson")
- **Michael Kicks** (person) - 2 occurrences ⭐
- **Rachel Hemmings** (person) - 2 occurrences ⭐
```

---

## Troubleshooting

### "No new entities discovered"

**Cause**: Test case may be too small or names already formal

**Solution**:
```bash
# Use controlled test with known variants
python scripts/generate_ab_test_cases.py
```

### "Package not found"

**Cause**: Pipeline didn't complete successfully

**Solution**: Check for errors:
```bash
# List all packages
ls -lh data/packages/

# Re-run pipeline manually
uv run evidence-toolkit process-case data/cases/AB-TEST-A-NO-RESOLVE \
    --case-id AB-TEST-A-NO-RESOLVE
```

### "Takes too long"

**Cause**: Large test case

**Solution**: Reduce size
```bash
python scripts/ab_test_ai_resolve.py --images 5 --documents 3
```

---

## Next Steps

1. **Review Report**: Understand which entities AI resolution found
2. **Run on Real Data**: Use `--source-case` with your own evidence
3. **Adjust Case Type**: Try `--case-type contract` or `workplace`
4. **Stress Test**: Run `--large` for 30 images + 10 documents
5. **Automate**: Add to CI/CD for regression testing

---

## Commands Cheat Sheet

```bash
# Quick automated test
python scripts/ab_test_ai_resolve.py

# Large automated test
python scripts/ab_test_ai_resolve.py --large

# Controlled test with known entities
python scripts/generate_ab_test_cases.py

# Compare existing packages
python scripts/generate_comparison_report.py pkg_a.zip pkg_b.zip

# Analyze only (skip generation/execution)
python scripts/ab_test_ai_resolve.py --analyze-only \
    --case-a EXISTING-CASE-A \
    --case-b EXISTING-CASE-B
```

---

## Documentation

- **Full Guide**: [scripts/README.md](README.md)
- **Architecture**: [../V3_ARCHITECTURE.md](../V3_ARCHITECTURE.md)
- **Changelog**: [../CHANGELOG.md](../CHANGELOG.md)

---

_Evidence Toolkit A/B Testing Framework v3.3.0_
