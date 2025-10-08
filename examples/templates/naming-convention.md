# File Naming Convention for Evidence

## Recommended Format

```
YYYY-MM-DD-TYPE-Subject-From-To.ext
```

### Components

1. **Date** (YYYY-MM-DD): When the document was created or sent
   - Use ISO 8601 format for sorting
   - Example: `2025-01-15`

2. **Type**: Document classification
   - `EMAIL` - Email correspondence
   - `LETTER` - Formal letter
   - `MEMO` - Internal memorandum
   - `REPORT` - Investigation or analysis report
   - `NOTICE` - Official notice or announcement
   - `CONTRACT` - Legal contract or agreement
   - `INVOICE` - Financial document
   - `STATEMENT` - Witness or formal statement

3. **Subject**: Brief description (use hyphens, not spaces)
   - Keep it concise (3-5 words)
   - Use TitleCase or lowercase
   - Example: `SafetyConcerns` or `safety-concerns`

4. **From**: Sender's last name or initials
   - Use last name: `JWilson` or `Wilson`
   - Or initials: `JW`

5. **To**: Recipient's last name or initials
   - Same format as From
   - Can be generic: `HR`, `Management`, `Legal`

6. **Extension**: File type
   - `.txt` - Plain text documents
   - `.eml` - Email messages
   - `.pdf` - PDF documents
   - `.jpg`, `.png` - Images
   - `.doc`, `.docx` - Word documents

---

## Examples

### Good Examples

```
2025-01-15-EMAIL-ComplaintInitial-JSmith-HR.txt
2025-01-20-LETTER-PolicyViolation-HR-JSmith.eml
2025-02-01-MEMO-InvestigationUpdate-Legal-Management.txt
2025-02-15-EMAIL-EscalationResponse-CEO-Legal.txt
2025-03-01-LETTER-Resolution-Legal-JSmith.pdf
2025-03-10-REPORT-SafetyInspection-SafetyDept-Management.pdf
```

### Why This Format?

**Benefits:**
- ✅ Files sort chronologically automatically
- ✅ Timeline reconstruction is easier
- ✅ Entity extraction works better
- ✅ Evidence correlation is improved
- ✅ Human-readable at a glance

**What the toolkit extracts:**
- Date entities from filename and content
- Document type classification
- Sender and recipient entities
- Subject matter for categorization

---

## Alternative Formats

If you have existing files with different naming, that's OK! The toolkit will still analyze them. However, consistent naming helps with:

- Cross-evidence correlation
- Timeline accuracy
- Entity relationship mapping
- Professional package appearance

---

## Special Cases

### Multiple Recipients
```
2025-01-15-EMAIL-SafetyAlert-JSmith-Team.txt
(where "Team" represents multiple recipients)
```

### Follow-up/Response Emails
```
2025-01-15-EMAIL-ComplaintInitial-JSmith-HR.txt
2025-01-20-EMAIL-ComplaintResponse-HR-JSmith.txt
(note the reversed From-To to show response direction)
```

### Images/Photos
```
2025-01-15-PHOTO-WarehouseDamage-Area3.jpg
2025-02-05-SCREENSHOT-EmailThread-SafetyConcern.png
```

### Personal Notes
```
2025-01-01-NOTES-Timeline-JSmith.txt
2025-02-15-NOTES-MeetingSummary-JSmith.txt
```

---

## Quick Reference

| File Type | Example Name |
|-----------|--------------|
| Email | `2025-01-15-EMAIL-Subject-From-To.eml` |
| Letter | `2025-01-15-LETTER-Subject-From-To.txt` |
| Memo | `2025-01-15-MEMO-Subject-From-To.txt` |
| Report | `2025-01-15-REPORT-Subject-Author.pdf` |
| Image | `2025-01-15-PHOTO-Description-Location.jpg` |
| Notes | `2025-01-15-NOTES-Topic-Author.txt` |

---

**Tip**: If you have many existing files to rename, you can use a batch renaming tool or script. The Evidence Toolkit will work with any naming convention, but consistent names improve analysis quality.
