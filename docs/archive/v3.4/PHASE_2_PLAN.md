# Phase 2: Complete Code Deduplication Plan

**Status**: 🟡 Ready to Execute
**Estimated Time**: 30-45 minutes
**Risk Level**: 🟢 Low (pure refactoring)
**Dependencies**: Phase 1 complete ✅

---

## Objective

Eliminate the remaining **23 path construction duplications** and **3 JSON read duplications** across 8 files, achieving **100% deduplication** of the Evidence Toolkit codebase.

---

## Current State

### Phase 1 Results ✅
- ✅ OpenAI API calls: 8/9 refactored (89%)
- ✅ JSON reads in analyzers: 9/9 refactored (100%)
- ✅ Quality improvement discovered and validated
- ✅ Zero functionality regressions

### Phase 2 Scope ⏳
- ⏳ Path construction: 0/23 refactored (0%)
- ⏳ JSON reads in storage.py: 0/3 refactored (0%)
- ⏳ Dead code cleanup: `get_analysis_paths()` unused

**Total remaining duplication**: ~55 lines across 8 files

---

## Step 1: Update Utilities (5 minutes)

### Task 1.1: Replace Dead Code with Working Utility

**File**: `src/evidence_toolkit/core/utils.py`

**Action**: Replace lines 203-214 (`get_analysis_paths()`) with:

```python
def get_evidence_base_dir(derived_dir: Path, sha256: str) -> Path:
    """Get base evidence directory for SHA256 hash.

    This centralizes the evidence directory path construction pattern that
    was duplicated 23+ times across the codebase. All evidence files
    (analysis.v1.json, metadata.json, exif.json, chain_of_custody.json,
    evidence_bundle.v1.json) live in this directory.

    Args:
        derived_dir: Base derived storage directory path
        sha256: Evidence SHA256 hash

    Returns:
        Path to evidence base directory: derived_dir/sha256={sha256}/

    Example:
        >>> evidence_dir = get_evidence_base_dir(storage.derived_dir, "abc123...")
        >>> analysis_file = evidence_dir / "analysis.v1.json"
        >>> metadata_file = evidence_dir / "metadata.json"
    """
    return derived_dir / f"sha256={sha256}"
```

**Why**:
- More flexible than tuple return (works for ANY evidence file)
- Matches actual usage patterns (most code needs base dir, not specific files)
- Clear forensic intent (centralizes SHA256 directory structure)

**Test**:
```bash
uv run python -c "from evidence_toolkit.core.utils import get_evidence_base_dir; print('✅')"
```

---

## Step 2: Refactor High-Priority Files (20 minutes)

### Task 2.1: `core/storage.py` (8 paths + 3 JSON reads)

**Complexity**: 🟠 Medium (core module, multiple patterns)
**Impact**: 🔴 High (used by all analyzers)
**Lines to save**: ~18

#### Path Refactoring Locations

Add import at top:
```python
from .utils import read_json_safe, get_evidence_base_dir
```

Replace these 8 instances:

1. **Line 134**: `derived_hash_dir = self.derived_dir / f"sha256={sha256}"`
   ```python
   # After:
   derived_hash_dir = get_evidence_base_dir(self.derived_dir, sha256)
   ```

2. **Line 206**: `analysis_file = self.derived_dir / f"sha256={sha256}" / "analysis.v1.json"`
   ```python
   # After:
   evidence_dir = get_evidence_base_dir(self.derived_dir, sha256)
   analysis_file = evidence_dir / "analysis.v1.json"
   ```

3. **Line 230**: `derived_hash_dir = self.derived_dir / f"sha256={sha256}"`
   ```python
   # After:
   derived_hash_dir = get_evidence_base_dir(self.derived_dir, sha256)
   ```

4. **Line 281**: `derived_hash_dir = self.derived_dir / f"sha256={sha256}"`
   ```python
   # After:
   derived_hash_dir = get_evidence_base_dir(self.derived_dir, sha256)
   ```

5. **Line 459**: `custody_file = self.derived_dir / f"sha256={sha256}" / "chain_of_custody.json"`
   ```python
   # After:
   evidence_dir = get_evidence_base_dir(self.derived_dir, sha256)
   custody_file = evidence_dir / "chain_of_custody.json"
   ```

6. **Line 472**: `custody_file = self.derived_dir / f"sha256={sha256}" / "chain_of_custody.json"`
   ```python
   # After:
   evidence_dir = get_evidence_base_dir(self.derived_dir, sha256)
   custody_file = evidence_dir / "chain_of_custody.json"
   ```

7. **Line 496**: `original_file = self.raw_dir / f"sha256={sha256}" / f"original{extension}"`
   ```python
   # After (raw dir pattern):
   raw_evidence_dir = get_evidence_base_dir(self.raw_dir, sha256)
   original_file = raw_evidence_dir / f"original{extension}"
   ```

8. **Line 665**: `derived_dir = self.derived_dir / f"sha256={sha256}"`
   ```python
   # After:
   evidence_dir = get_evidence_base_dir(self.derived_dir, sha256)
   ```

#### JSON Read Refactoring Locations

Replace these 3 instances:

1. **Lines 212-213**: In `get_analysis()`
   ```python
   # Before:
   try:
       with open(analysis_file, 'r') as f:
           data = json.load(f)
       return UnifiedAnalysis.model_validate(data)
   except Exception as e:
       print(f"Error loading analysis for {sha256}: {e}")
       return None

   # After:
   data = read_json_safe(analysis_file)
   if not data:
       return None
   try:
       return UnifiedAnalysis.model_validate(data)
   except Exception as e:
       print(f"Error loading analysis for {sha256}: {e}")
       return None
   ```

2. **Lines 478-479**: In `_add_custody_event()`
   ```python
   # Before:
   if custody_file.exists():
       try:
           with open(custody_file, 'r') as f:
               events_data = json.load(f)
           events = [ChainOfCustodyEvent.model_validate(e) for e in events_data]
       except Exception as e:
           print(f"Warning: Could not load existing custody events: {e}")

   # After:
   if custody_file.exists():
       events_data = read_json_safe(custody_file)
       if events_data:
           try:
               events = [ChainOfCustodyEvent.model_validate(e) for e in events_data]
           except Exception as e:
               print(f"Warning: Could not load existing custody events: {e}")
   ```

3. **Lines 552-553**: In `get_storage_stats()`
   ```python
   # Before:
   try:
       with open(analysis_file, 'r') as f:
           data = json.load(f)
       evidence_type = data.get('evidence_type', 'unknown')

   # After:
   data = read_json_safe(analysis_file)
   if data:
       evidence_type = data.get('evidence_type', 'unknown')
   ```

**Test after storage.py**:
```bash
# Critical test - storage is core module
uv run evidence-toolkit storage stats
uv run evidence-toolkit --help
```

---

### Task 2.2: `pipeline/summary.py` (6 paths)

**Complexity**: 🟢 Low (already refactored in Phase 1)
**Impact**: 🟠 Medium (generates executive summaries)
**Lines to save**: ~6

Add import (if not already present):
```python
from evidence_toolkit.core.utils import get_evidence_base_dir
```

Replace these 6 instances:

1. **Line 990**: `analysis_file = self.storage.derived_dir / f"sha256={evidence.sha256}" / "analysis.v1.json"`
2. **Line 1077**: `analysis_file = self.storage.derived_dir / f"sha256={evidence.sha256}" / "analysis.v1.json"`
3. **Line 1150**: `analysis_file = self.storage.derived_dir / f"sha256={evidence.sha256}" / "analysis.v1.json"`
4. **Line 1237**: `analysis_file = self.storage.derived_dir / f"sha256={evidence.sha256}" / "analysis.v1.json"`
5. **Line 1321**: `analysis_file = self.storage.derived_dir / f"sha256={evidence.sha256}" / "analysis.v1.json"`
6. **Line 1554**: `analysis_file = self.storage.derived_dir / f"sha256={summary.sha256}" / "analysis.v1.json"`

**Pattern for all 6**:
```python
# After:
evidence_dir = get_evidence_base_dir(self.storage.derived_dir, evidence.sha256)
analysis_file = evidence_dir / "analysis.v1.json"
```

**Test**:
```bash
uv run evidence-toolkit process-case data/cases/test003 --case-id test003
```

---

### Task 2.3: `pipeline/analyze.py` (3 paths)

**Complexity**: 🟢 Low
**Impact**: 🟠 Medium (analysis orchestration)
**Lines to save**: ~4

Add import:
```python
from evidence_toolkit.core.utils import get_evidence_base_dir
```

Replace these 3 instances:

1. **Line 146**: `analysis_file = storage.derived_dir / f"sha256={sha256}" / "analysis.v1.json"`
   ```python
   # After:
   evidence_dir = get_evidence_base_dir(storage.derived_dir, sha256)
   analysis_file = evidence_dir / "analysis.v1.json"
   ```

2. **Line 164**: `metadata_file = storage.derived_dir / f"sha256={sha256}" / "metadata.json"`
   ```python
   # After (reuse evidence_dir from above):
   metadata_file = evidence_dir / "metadata.json"
   ```

3. **Line 173**: `derived_evidence_dir = storage.derived_dir / f"sha256={sha256}"`
   ```python
   # After (reuse evidence_dir):
   derived_evidence_dir = evidence_dir
   ```

**Note**: Lines 164 and 173 can reuse the `evidence_dir` variable from line 146, saving even more lines.

**Test**:
```bash
uv run evidence-toolkit analyze <sha256> --case-id test003
```

---

## Step 3: Refactor Medium-Priority Files (10 minutes)

### Task 3.1: `pipeline/package.py` (2 paths)

**Lines to save**: ~2

1. **Line 209**: `evidence_dir = self.storage.derived_dir / f"sha256={evidence_summary.sha256}"`
2. **Line 241**: `evidence_dir = self.storage.derived_dir / f"sha256={evidence.sha256}"`

Both become:
```python
evidence_dir = get_evidence_base_dir(self.storage.derived_dir, evidence_summary.sha256)
```

---

### Task 3.2: `pipeline/batch.py` (1 path)

**Lines to save**: ~1

1. **Line 112**: `metadata_file = storage.derived_dir / f"sha256={sha256}" / "metadata.json"`
   ```python
   evidence_dir = get_evidence_base_dir(storage.derived_dir, sha256)
   metadata_file = evidence_dir / "metadata.json"
   ```

---

### Task 3.3: `analyzers/correlation.py` (1 path)

**Lines to save**: ~1

1. **Line 655**: `evidence_dir = self.evidence_storage.derived_dir / f"sha256={sha256}"`
   ```python
   evidence_dir = get_evidence_base_dir(self.evidence_storage.derived_dir, sha256)
   ```

---

### Task 3.4: `cli.py` (1 path)

**Lines to save**: ~1

1. **Line 163**: `sha256_dir = storage.derived_dir / f"sha256={sha256}"`
   ```python
   from evidence_toolkit.core.utils import get_evidence_base_dir
   sha256_dir = get_evidence_base_dir(storage.derived_dir, sha256)
   ```

---

## Step 4: Final Validation (10 minutes)

### Test Suite

Run after ALL changes complete:

```bash
# 1. Import validation
uv run python -c "from evidence_toolkit.core.utils import get_evidence_base_dir, read_json_safe; print('✅ Imports work')"

# 2. CLI commands
uv run evidence-toolkit --help
uv run evidence-toolkit version
uv run evidence-toolkit storage stats

# 3. Full pipeline integration test
uv run evidence-toolkit process-case data/cases/test003 --case-id test003-phase2

# 4. Compare output to Phase 1 baseline
diff data/packages/test003_analysis_package_*/reports/executive_summary.txt

# 5. Check for regressions
ls -lh data/packages/test003-phase2*/reports/
```

### Success Criteria

✅ All CLI commands execute without errors
✅ Storage stats display correctly
✅ Full pipeline processes 26 evidence items
✅ Executive summary quality matches Phase 1 baseline
✅ No Python exceptions or warnings
✅ Git diff shows only path refactoring changes

---

## Step 5: Commit Changes

### Commit Message

```
refactor: Complete code deduplication (Phase 2) - Path construction

Eliminates remaining duplication by centralizing evidence path construction:

Path Construction:
- New utility: get_evidence_base_dir(derived_dir, sha256)
- Replaces 23 instances of f"sha256={sha256}" pattern
- Files: storage.py (8), summary.py (6), analyze.py (3), others (6)

JSON Reads:
- Refactored 3 remaining instances in storage.py
- Now uses read_json_safe() for consistency

Dead Code:
- Removed unused get_analysis_paths() function
- Replaced with more flexible get_evidence_base_dir()

Impact:
- Lines saved: ~55 (46 paths + 9 JSON reads)
- Duplication eliminated: 100% (all patterns centralized)
- Forensic compliance: Single source of truth for evidence paths

Testing:
- ✅ Storage stats functional
- ✅ Full pipeline tested (26 evidence items)
- ✅ Executive summary quality maintained
- ✅ Zero regressions

This completes the v3.x deduplication effort started in commit 1bbff17.
Phase 1 eliminated API/JSON duplication; Phase 2 eliminates path duplication.

Related: docs/V3_DEDUPLICATION_REPORT.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Risk Assessment

### Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking storage.py | Low | High | Test after each file; storage.py first |
| Path format errors | Very Low | Medium | Utility uses same f-string pattern |
| Import conflicts | Very Low | Low | Same pattern as Phase 1 |
| Regression in AI quality | Very Low | Medium | Compare outputs to Phase 1 baseline |

### Rollback Plan

If ANY issues detected:

```bash
# Immediate rollback
git reset --hard HEAD~1

# Verify rollback
uv run evidence-toolkit --help
```

**Recovery time**: < 1 minute

---

## Expected Results

### Quantitative

- **Lines removed**: ~55 (path + JSON duplication)
- **Net reduction**: ~40 lines (after accounting for imports)
- **Duplication eliminated**: 100% (Phase 1: 72% → Phase 2: 100%)
- **Dead code removed**: 12 lines (`get_analysis_paths()`)
- **Files modified**: 8

### Qualitative

✅ **Single source of truth**: All evidence paths constructed identically
✅ **Forensic compliance**: Centralized path logic aids auditing
✅ **Maintainability**: Change path format in ONE place
✅ **Developer experience**: Clear utility eliminates confusion
✅ **No regressions**: Quality maintained or improved

---

## Timeline

| Task | Time | Cumulative |
|------|------|------------|
| Update utilities | 5 min | 5 min |
| Refactor storage.py | 10 min | 15 min |
| Refactor summary.py | 5 min | 20 min |
| Refactor analyze.py | 3 min | 23 min |
| Refactor 4 remaining files | 7 min | 30 min |
| Final validation | 10 min | 40 min |
| Commit & document | 5 min | 45 min |

**Total estimated time**: 45 minutes

---

## Phase 2 Checklist

### Pre-Flight
- [ ] Phase 1 complete and committed ✅
- [ ] Git working tree clean ✅
- [ ] Test case available (`test003`) ✅
- [ ] Backup created (`data/storage.bzckup`) ✅

### Execution
- [ ] Step 1: Update `get_evidence_base_dir()` utility
- [ ] Test: Import utility successfully
- [ ] Step 2.1: Refactor `storage.py` (8 paths + 3 JSON)
- [ ] Test: Storage stats work
- [ ] Step 2.2: Refactor `summary.py` (6 paths)
- [ ] Test: Generate executive summary
- [ ] Step 2.3: Refactor `analyze.py` (3 paths)
- [ ] Test: Analyze command works
- [ ] Step 3: Refactor 4 remaining files (6 paths total)
- [ ] Step 4: Final validation (full pipeline)
- [ ] Step 5: Commit with detailed message

### Post-Flight
- [ ] Git diff review
- [ ] Documentation updated
- [ ] Quality comparison (Phase 1 vs Phase 2 output)
- [ ] Update `V3_DEDUPLICATION_REPORT.md` with Phase 2 results

---

## Success Definition

Phase 2 is **complete** when:

1. ✅ All 23 path construction patterns use `get_evidence_base_dir()`
2. ✅ All 3 JSON reads in `storage.py` use `read_json_safe()`
3. ✅ Dead code (`get_analysis_paths()`) removed
4. ✅ Full pipeline test passes (26 evidence items)
5. ✅ Executive summary quality matches Phase 1
6. ✅ Zero functionality regressions
7. ✅ Clean commit with comprehensive message
8. ✅ Documentation updated

**Definition of Done**: Code is cleaner, more maintainable, and 100% deduplicated with no functionality loss.

---

**Plan Version**: 1.0
**Created**: 2025-10-09
**Status**: Ready to Execute
**Approval Required**: ✅ Yes (user confirmation)
