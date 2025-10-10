# Evidence Toolkit v3.3.0 - Release Checklist

**Target Release Date**: October 10, 2025
**Version**: 3.3.0
**Status**: 🟢 Ready for Release (pending final checks)

---

## Pre-Release Checklist

### 1. Code Quality ✅
- [x] All critical tests passing (13/13 forensic integrity tests)
- [x] Model tests passing (120/120)
- [x] Fixed test import issues (EmailAnalysisResult)
- [x] Only 1 TODO/FIXME in codebase (acceptable)
- [ ] Run full test suite with OpenAI API key to verify pipeline tests
- [ ] Manual smoke test: Run `process-case` on sample data

### 2. Documentation ✅
- [x] README.md updated with v3.3 features
- [x] CHANGELOG.md complete with all v3.3 changes
- [x] QUICKSTART.md reflects current version
- [x] CLAUDE.md (AI assistant guide) up to date
- [x] All features documented in docs/
- [ ] Verify repository URLs are correct (currently: `evidence-toolkit/evidence-toolkit`)

### 3. Version Control ✅
- [x] Version in pyproject.toml: 3.3.0
- [x] Version in README.md: 3.3.0
- [x] Version in CHANGELOG.md: 3.3.0
- [x] Git tag v3.3.0 exists
- [ ] All changes committed
- [ ] Working tree clean

### 4. Package Metadata ✅
- [x] pyproject.toml complete
- [x] LICENSE file present (MIT)
- [x] All dependencies listed
- [x] Entry points configured (`evidence-toolkit` CLI)
- [x] Project URLs set (Homepage, Repository, Issues, Docs)

### 5. Release Assets
- [ ] Create GitHub release from v3.3.0 tag
- [ ] Write release notes (copy from CHANGELOG.md)
- [ ] Build distribution packages (`uv build`)
- [ ] (Optional) Publish to PyPI

---

## Release Notes Template

```markdown
# Evidence Toolkit v3.3.0 - Maximum Data Utilization

**Released**: October 10, 2025

## 🎯 Highlights

- **98% Data Utilization** - Up from 65% in v3.1
- **Quoted Statements Extraction** - Direct quotes with speaker attribution & sentiment
- **Communication Pattern Analysis** - Email risk classification & pattern distribution
- **Semantic Timeline Events** - AI-extracted dates with narrative context
- **Relationship Network Extraction** - Escalation chains & communication mapping
- **Image OCR Aggregation** - Text extraction from 75% of visual evidence
- **Executive-First Report Layout** - Insights first (35-45%), appendix last (55-65%)
- **Zero Additional Cost** - All features use existing v3.1 analysis data

## 📦 What's New

### Phase A: Aggregated Pattern Data (95% utilization)
- Quoted statements extraction with sentiment analysis
- Communication pattern classification (professional/escalating/hostile)
- Risk level assessment across email corpus

### Phase B: Hidden Evidence Data (98% utilization)
- Image OCR aggregation grouped by evidence value
- Relationship network parsing for escalation chains
- Semantic timeline events from AI-extracted dates

### Phase B+: Forensic Display Restructuring
- Executive summary leads with strategic insights
- Supporting documentation moved to appendix
- Dual-layer analysis (forensic + enhanced)
- Transforms "glorified appendix" → executive-ready deliverable

## 🔧 Technical Improvements

- **Code Deduplication**: Eliminated ~969 lines across 4 phases
- **Report Structure**: 35-45% insights, 55-65% supporting docs
- **Enhanced Prompts**: Domain-specific workplace/generic case types
- **All Pydantic**: 48 validated models, 100% runtime validation

## 📊 Performance

- Processing: 2-3 min (5 files), 6-8 min (20 files), 15-20 min (50+ files)
- API Costs: ~$0.10-0.30 per 20-piece case
- Data Utilization: 98% (up from 65%)

## 🔗 Links

- [Full Changelog](CHANGELOG.md#330---2025-10-09)
- [Documentation](README.md)
- [Quick Start Guide](QUICKSTART.md)
- [Architecture](V3_ARCHITECTURE.md)

## 🙏 Contributors

Special thanks to all contributors who helped achieve maximum data utilization!

---

**Install**: `pip install uv && uv pip install -e .`
**Upgrade**: Compatible with v3.0-3.2, drop-in replacement
```

---

## Post-Release Checklist

- [ ] Announce on GitHub Discussions
- [ ] Update project website (if applicable)
- [ ] Share on relevant communities (legal tech, forensics)
- [ ] Monitor issues for bug reports
- [ ] Plan v3.4 features based on feedback

---

## Quick Release Commands

```bash
# 1. Verify everything is committed
git status

# 2. Ensure tag exists
git tag -l | grep v3.3.0

# 3. Push tag to GitHub
git push origin v3.3.0

# 4. Build distribution (optional, for PyPI)
uv build

# 5. Create GitHub Release
gh release create v3.3.0 \
  --title "Evidence Toolkit v3.3.0 - Maximum Data Utilization" \
  --notes-file RELEASE_NOTES.md \
  --verify-tag

# 6. (Optional) Publish to PyPI
# uv publish
```

---

## Rollback Plan

If critical issues are found post-release:

1. **Immediate**: Create issue on GitHub, label as `critical`
2. **Hotfix Branch**: `git checkout -b hotfix/v3.3.1`
3. **Fix & Test**: Apply fix, run full test suite
4. **Emergency Release**: Version 3.3.1 with patch
5. **Notify Users**: GitHub release + discussions

---

## Success Criteria

✅ Release is successful when:
- [ ] GitHub release published with v3.3.0 tag
- [ ] Release notes visible on GitHub
- [ ] No critical bugs reported within 48 hours
- [ ] At least 3 successful user installations
- [ ] Documentation accessible and accurate

---

**Prepared by**: Claude Code
**Review Status**: Pending human review
**Approved by**: _____________
**Release Date**: _____________
