# Evidence Templates

This directory contains blank templates you can use to create your own evidence files for analysis with the Evidence Toolkit.

---

## Available Templates

### 📧 Email Template (`email-template.eml`)

Standard email format with headers and body structure.

**Use for**:
- Email correspondence
- Thread analysis
- Participant identification
- Communication pattern detection

**How to use**:
1. Copy `email-template.eml` to your case directory
2. Rename following naming convention: `YYYY-MM-DD-EMAIL-Subject-From-To.eml`
3. Replace placeholders with actual content
4. Keep email headers intact (From, To, CC, Date, Subject)

### 📄 Document Template (`document-template.txt`)

Generic document structure for letters, memos, and formal communications.

**Use for**:
- Formal letters
- Internal memos
- Investigation reports
- Policy documents
- Formal statements

**How to use**:
1. Copy `document-template.txt` to your case directory
2. Rename following naming convention: `YYYY-MM-DD-TYPE-Subject-From-To.txt`
3. Replace [bracketed placeholders] with actual content
4. Maintain structure for better AI analysis

### 📋 Naming Convention Guide (`naming-convention.md`)

Complete guide to naming evidence files for optimal analysis.

**Recommended format**:
```
YYYY-MM-DD-TYPE-Subject-From-To.ext

Examples:
  2025-01-15-EMAIL-ComplaintInitial-JSmith-HR.txt
  2025-01-20-LETTER-PolicyViolation-HR-JSmith.pdf
  2025-02-01-MEMO-InvestigationUpdate-Legal-Mgmt.txt
```

**Why naming matters**:
- Files sort chronologically
- Timeline reconstruction is easier
- Entity extraction works better
- Professional package appearance

---

## Creating Your Own Evidence

### Step 1: Plan Your Case Structure

Decide what evidence you need:
- Initial complaint or incident report
- Email correspondence between parties
- Management responses
- Investigation documents
- Supporting documentation (notes, photos, etc.)

### Step 2: Create Evidence Files

1. **Copy templates** from this directory
2. **Rename consistently** using the naming convention
3. **Fill in content** replacing all placeholders
4. **Organize by date** to maintain timeline integrity

### Step 3: Organize in a Case Directory

```
your-case-name/
├── 2025-01-15-EMAIL-InitialConcern-Employee-Manager.eml
├── 2025-01-20-LETTER-FormalComplaint-Employee-HR.txt
├── 2025-02-01-MEMO-InvestigationNotice-HR-Employee.txt
├── 2025-02-15-EMAIL-FollowUp-Manager-Employee.eml
└── README.md (optional case description)
```

### Step 4: Process with Evidence Toolkit

```bash
# Process your case
uv run evidence-toolkit process-case your-case-name \
  --case-id YOUR-CASE-ID

# View results
cat data/packages/YOUR-CASE-ID_*/reports/executive_summary.txt
```

---

## Best Practices

### Content Guidelines

**DO**:
- ✅ Use realistic but anonymized names
- ✅ Include specific dates and timelines
- ✅ Maintain professional language
- ✅ Include relevant details (job titles, departments, etc.)
- ✅ Create logical document progression

**DON'T**:
- ❌ Use real names, companies, or identifying information
- ❌ Include actual personal data (SSNs, real addresses, etc.)
- ❌ Create evidence with real legal cases (unless client case, kept private)
- ❌ Leave template placeholders (like [SUBJECT]) in final files

### Entity Consistency

For better cross-document correlation:
- **Use consistent names**: If "James Wilson" in one document, use "James Wilson" (not "J. Wilson" or "Jim Wilson") in others
- **Include job titles**: Helps with power dynamics analysis
- **Reference same locations**: If "Warehouse Area 3" in one doc, use same name elsewhere
- **Maintain timeline**: Ensure dates progress logically

### Email-Specific Tips

For `.eml` files:
- Always include From, To, Date, Subject headers
- CC relevant parties to demonstrate organizational hierarchy
- Use professional email signatures
- Create threads by referencing previous emails in subject/body

---

## Example Use Cases

### Workplace Investigation
- Employee complaint letter
- Management response email
- HR investigation notice
- Witness statements
- Resolution memo

### Contract Dispute
- Original contract/agreement
- Breach notification letter
- Email correspondence about dispute
- Invoice discrepancies
- Settlement proposal

### Safety Incident
- Incident report
- Safety inspection findings
- Email warnings
- Policy violation notices
- Corrective action plans

---

## Getting Help

**Documentation**:
- See example cases in `examples/case-workplace-safety/`
- Read the Evidence Toolkit README for processing instructions
- Check `naming-convention.md` for detailed naming rules

**Questions?**:
- Review existing example cases for inspiration
- Consult Evidence Toolkit documentation
- Ask in GitHub Issues if you need help

---

**Remember**: All evidence you create should be for legitimate legal work, training, or demonstrations only. Never fabricate evidence for actual legal proceedings.

**Privacy**: Keep all real case data in `data/cases/` (automatically gitignored). Only use these templates for practice, demonstrations, or anonymized training materials.
