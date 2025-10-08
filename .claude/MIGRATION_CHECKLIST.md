# .claude/ Migration Checklist

**Date**: 2025-10-07
**Backup**: `.claude-backup-20251007-204041.tar.gz`

---

## 🎯 Migration Goals

- [x] Backup current structure
- [ ] Reorganize commands by category
- [ ] Extract reusable prompts
- [ ] Add Evidence Toolkit specific commands
- [ ] Create templates for future commands
- [ ] Document workflows

---

## Phase 1: Reorganize Existing Commands

### Discovery Commands
- [ ] Move `commands/prime.md` → `commands/discovery/prime.md`
- [ ] Move `commands/status.md` → `commands/discovery/status.md`
- [ ] Update command descriptions to show namespace

### Development Commands
- [ ] Move `commands/commit.md` → `commands/development/commit.md`
- [ ] Move `commands/test-fix.md` → `commands/development/test-fix.md`
- [ ] Add argument hints where missing

### Documentation Commands
- [ ] Move `commands/create-docs.md` → `commands/documentation/create-docs.md`
- [ ] Move `commands/update-docs.md` → `commands/documentation/update-docs.md`
- [ ] Fix conversational preamble (already done in create-docs)

### Analysis Commands
- [ ] Move `commands/rca.md` → `commands/analysis/rca.md`
- [ ] Verify agent delegation works correctly

### Release Commands
- [ ] Move `commands/package-release.md` → `commands/release/package-release.md`

### Create READMEs
- [ ] Create `commands/discovery/README.md`
- [ ] Create `commands/development/README.md`
- [ ] Create `commands/documentation/README.md`
- [ ] Create `commands/analysis/README.md`
- [ ] Create `commands/release/README.md`
- [ ] Update main `commands/README.md`

---

## Phase 2: Extract Prompts

- [ ] Create `prompts/` directory
- [ ] Extract `prompts/code-review.md` (from commit.md)
- [ ] Extract `prompts/pydantic-validation.md` (from create-docs.md)
- [ ] Create `prompts/forensic-integrity.md` (Evidence Toolkit standards)
- [ ] Create `prompts/ai-prompt-engineering.md` (OpenAI best practices)
- [ ] Create `prompts/README.md`

---

## Phase 3: New Commands

### Evidence Toolkit Specific
- [ ] Create `commands/evidence/` directory
- [ ] Create `commands/evidence/ingest-case.md`
- [ ] Create `commands/evidence/analyze-evidence.md`
- [ ] Create `commands/evidence/correlate.md`
- [ ] Create `commands/evidence/package-case.md`
- [ ] Create `commands/evidence/README.md`

### Development Enhancements
- [ ] Create `commands/development/lint.md`
- [ ] Create `commands/development/review.md`

### Documentation Enhancements
- [ ] Create `commands/documentation/docstring.md`

### Analysis Enhancements
- [ ] Create `commands/analysis/trace.md`
- [ ] Create `commands/analysis/profile.md`

### Release Enhancements
- [ ] Create `commands/release/pr.md`
- [ ] Create `commands/release/changelog.md`

---

## Phase 4: Templates

- [ ] Create `commands/_templates/` directory
- [ ] Create `commands/_templates/basic-command.md`
- [ ] Create `commands/_templates/bash-command.md`
- [ ] Create `commands/_templates/agent-delegating-command.md`
- [ ] Create `commands/_templates/README.md`

- [ ] Create `templates/` directory
- [ ] Create `templates/analyzer.py.template`
- [ ] Create `templates/test.py.template`
- [ ] Create `templates/model.py.template`
- [ ] Create `templates/module-doc.md.template`
- [ ] Create `templates/README.md`

---

## Phase 5: Workflows

- [ ] Create `workflows/` directory
- [ ] Create `workflows/new-analyzer.md`
- [ ] Create `workflows/new-case-type.md`
- [ ] Create `workflows/add-ai-feature.md`
- [ ] Create `workflows/release-process.md`
- [ ] Create `workflows/README.md`

---

## Phase 6: Documentation Updates

- [ ] Update main `.claude/README.md`
- [ ] Update `AUTOMATION_GUIDE.md`
- [ ] Update root `CLAUDE.md` to reference new structure
- [ ] Create `config/` directory with example configs

---

## Phase 7: Testing

- [ ] Test all discovery commands work
- [ ] Test all development commands work
- [ ] Test all documentation commands work
- [ ] Test all analysis commands work
- [ ] Test all release commands work
- [ ] Test new evidence commands work
- [ ] Verify namespaces appear correctly in `/help`

---

## Phase 8: Cleanup

- [ ] Remove old command files from root
- [ ] Archive old AUTOMATION_GUIDE.md or update it
- [ ] Commit changes with proper message
- [ ] Update project documentation

---

## Rollback Procedure

If something goes wrong:

```bash
# Stop and extract backup
tar -xzf .claude-backup-20251007-204041.tar.gz

# This will restore .claude/ to its original state
# Then investigate what went wrong
```

---

## Success Criteria

- ✅ All original commands still work (just in new locations)
- ✅ New commands are functional
- ✅ Prompts are reusable across commands
- ✅ Templates make creating new commands easy
- ✅ Workflows guide complex multi-step processes
- ✅ Documentation is clear and comprehensive
- ✅ Evidence Toolkit has domain-specific automation

---

## Timeline Estimate

- **Phase 1**: 30 minutes (move files, create READMEs)
- **Phase 2**: 20 minutes (extract prompts)
- **Phase 3**: 60 minutes (create new commands)
- **Phase 4**: 30 minutes (create templates)
- **Phase 5**: 30 minutes (document workflows)
- **Phase 6**: 20 minutes (update docs)
- **Phase 7**: 20 minutes (testing)
- **Phase 8**: 10 minutes (cleanup)

**Total**: ~3 hours 20 minutes

---

## Notes

- Keep backup until migration is fully tested and validated
- Can do phases incrementally (don't need to do all at once)
- Test each phase before moving to next
- Document any issues or improvements discovered during migration
