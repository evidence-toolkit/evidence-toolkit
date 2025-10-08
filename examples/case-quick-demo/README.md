# Quick Demo Case

**Purpose**: Minimal test case for quick validation and demonstrations
**Evidence Count**: 3 pieces
**Processing Time**: ~30 seconds

---

## Overview

This is the smallest example case, designed for:
- Quick functionality tests
- CI/CD pipeline validation
- Fast demonstrations
- Learning the basic workflow

**Scenario**: Simple contract review matter - client contacts legal counsel about potential breach of service agreement.

---

## Evidence Files

1. **2025-01-15-EMAIL-InitialInquiry-Client-Legal.eml**
   - Client's initial contact with law firm
   - Brief description of contract issue

2. **2025-01-20-LETTER-LegalResponse-Legal-Client.txt**
   - Attorney's response letter
   - Outlines next steps and information needed

3. **client-notes.txt**
   - Client's personal timeline notes
   - Summary of key issues and people involved

---

## What This Demonstrates

- **Entity extraction**: Alex Thompson, Jennifer Martinez, David Chen, Sarah Williams, VendorCo, ExampleCorp
- **Timeline**: June 2024 - January 2025
- **Document types**: Email (.eml), Letter (.txt), Notes (.txt)
- **Basic correlation**: Same entities appearing across multiple documents

---

## Usage

```bash
# Quick test (30 seconds)
uv run evidence-toolkit process-case examples/case-quick-demo \
  --case-id demo-test

# View results
cat data/packages/demo-test_*/reports/executive_summary.txt
```

---

## Expected Results

**Entities**:
- 4 people identified
- 3 organizations
- Multiple dates extracted

**Timeline**:
- Spans 7+ months (June 2024 - Jan 2025)
- 2 key communication events

**Analysis**:
- Professional communication pattern
- Low legal significance (early-stage inquiry)
- No risk flags expected

---

**Note**: This is an intentionally minimal case. For more realistic examples with richer analysis, see `case-workplace-safety/`.
