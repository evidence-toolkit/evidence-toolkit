# Evidence Toolkit Examples

This directory contains fully anonymized example cases for testing and demonstrating the Evidence Toolkit's capabilities.

---

## 📁 Example Cases

### 🏭 Workplace Safety Escalation (`case-workplace-safety/`)

**Scenario**: Employee raises workplace safety concerns, management response focuses on productivity metrics rather than addressing systemic issues.

**Evidence**: 6 pieces
- 4 documents (letters, emails, memos)
- 1 .eml email file  
- 1 personal timeline notes

**Demonstrates**:
- ✅ Safety concern escalation patterns
- ✅ Potential retaliation detection
- ✅ Power dynamics analysis (employee → supervisor → manager → HR)
- ✅ Legal pattern detection (evidence gaps, contradictions)
- ✅ Timeline reconstruction (2 months of events)
- ✅ Entity correlation across multiple documents

**Use cases**: Employment law, workplace safety, retaliation claims, OSHA compliance

**Processing time**: ~2-3 minutes

```bash
uv run evidence-toolkit process-case examples/case-workplace-safety \
  --case-id workplace-demo --case-type workplace
```

---

### ⚡ Quick Demo (`case-quick-demo/`)

**Scenario**: Minimal test case showing initial client inquiry about contract dispute.

**Evidence**: 3 pieces
- 1 email (.eml)
- 1 letter (.txt)
- 1 client notes (.txt)

**Demonstrates**:
- ✅ Basic entity extraction
- ✅ Simple timeline reconstruction
- ✅ Document classification
- ✅ Fast processing for testing/CI/CD

**Use cases**: Quick validation, demonstrations, learning the workflow

**Processing time**: ~30 seconds

```bash
uv run evidence-toolkit process-case examples/case-quick-demo \
  --case-id demo-test
```

---

## 📋 Templates (`templates/`)

Reusable templates for creating your own evidence files - see [templates/README.md](templates/README.md)

---

## 🔒 Privacy Notice

**All example data is completely anonymized** - no real names, companies, or events.
Safe for public demonstrations and training.

Your own evidence goes in `data/cases/` (automatically gitignored).

See [../PRIVACY.md](../PRIVACY.md) for complete details.

---

**Examples created**: 2025-10-08 for Evidence Toolkit v3.3.0 launch
