---
name: AI Entity Resolution Optimization
about: Optimize single-to-single entity matching performance
title: 'Optimize AI entity resolution for large cases'
labels: enhancement, performance, v3.2
assignees: ''
---

## Summary

The v3.2 AI entity resolution feature (`--ai-resolve`) works correctly but has performance limitations for large cases due to O(n²) entity comparisons. Current hard limit of 50 API calls prevents timeout but may miss correlations in cases with many entities.

## Current Behavior

**File**: `src/evidence_toolkit/analyzers/correlation.py:960-1025`

When `--ai-resolve` is enabled, the system:
1. Extracts all single-evidence entities (entities appearing in only 1 piece)
2. Compares each person entity pairwise using AI
3. Stops after 50 AI calls to prevent timeout

**Example**:
- 66 person entities → 2,145 possible comparisons (66 choose 2)
- Current limit: Only checks first 50 pairs
- Result: Potentially missed correlations after limit reached

## Root Cause Analysis

The core fix (email name parsing) solved 80% of cases:
- ✅ "Paul.Boucherat.9241@domain" → "Paul Boucherat" (now works via string matching)
- ✅ "Paul" vs "Paul Boucherat" → Match via `short="paul"` variant

AI resolution handles remaining edge cases:
- ❌ "Paul" vs "P. Boucherat" (initials don't match)
- ❌ "Bob Smith" vs "Robert Smith" (nicknames)
- ✅ "J. Smith" vs "John Smith" (works via initials)

## Proposed Solutions

### Option 1: Smart Filtering (Recommended)
Only compare entities likely to match:
```python
# Filter by first letter or phonetic similarity
if entity_a[0].lower() == entity_b[0].lower():
    # Only compare "Paul" with "P. Boucherat", not "Bob Smith"
```

**Pros**: Reduces comparisons by ~96% (26x reduction for uniform distribution)
**Cons**: May miss "Robert" vs "Bob" matches

### Option 2: Batch Processing
Group entities and prioritize high-value comparisons:
```python
# Prioritize single-word vs multi-word names (likely matches)
priority_pairs = [(s, l) for s in single_word for l in multi_word]
```

**Pros**: More likely to catch important matches first
**Cons**: More complex logic

### Option 3: Dynamic Limit
Scale limit based on case size:
```python
max_ai_calls = min(200, len(person_singles) * 2)
```

**Pros**: Handles both small and large cases
**Cons**: May still timeout on very large cases (100+ entities)

## Metrics

**Performance targets**:
- Small cases (< 20 entities): < 10 seconds
- Medium cases (20-50 entities): < 30 seconds
- Large cases (50-100 entities): < 60 seconds
- Very large cases (100+ entities): Graceful degradation with warning

**API cost considerations**:
- gpt-4o-mini: ~$0.15 per 1M input tokens
- Typical comparison: ~500 tokens/call
- 50 calls ≈ $0.004 (negligible)
- 200 calls ≈ $0.015 (still very cheap)

## Implementation Notes

- Maintain forensic conservatism (false negatives > false positives)
- Keep 0.7 confidence threshold for matches
- Log skipped comparisons for transparency
- Add verbose output showing which filtering strategy was used

## Related Files

- `src/evidence_toolkit/analyzers/correlation.py:960-1025` - Single-to-single matching logic
- `src/evidence_toolkit/domains/legal_config.py:131-208` - ENTITY_MATCH_PROMPT
- `docs/module-docs/CORRELATION_ANALYZER.md` - User documentation

## Priority

**Medium**: Feature works correctly for typical cases (5-20 evidence pieces). Optimization needed for large-scale investigations (50+ evidence pieces).
