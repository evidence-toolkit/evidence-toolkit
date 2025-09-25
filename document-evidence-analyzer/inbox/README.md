# Document Inbox

This is the default input directory for the Document Evidence Analyzer.

## Usage

Simply drop your text documents here and run analysis commands without specifying paths:

```bash
# Copy your documents to inbox
cp /path/to/your/documents/*.txt inbox/

# Run analysis (defaults to ./inbox/)
document-analyzer analyze

# Run retaliation analysis (defaults to ./inbox/)
document-analyzer retaliation
```

## Sample Documents

This directory contains sample legal documents demonstrating a workplace harassment case progression:

- `2025-01-15-EMAIL-ComplaintInitial-JSmith-HR.txt` - Initial harassment complaint
- `2025-01-20-LETTER-PolicyViolation-HR-JSmith.txt` - HR response with policy citations
- `2025-02-01-MEMO-InvestigationUpdate-Legal-Management.txt` - Internal legal memo
- `2025-02-15-EMAIL-EscalationResponse-CEO-Legal.txt` - Executive decision communication
- `2025-03-01-LETTER-Resolution-Legal-JSmith.txt` - Settlement agreement letter

## File Naming Convention

For best timeline analysis results, use this naming pattern:
- `YYYY-MM-DD-TYPE-Description-Parties.txt`
- Example: `2025-03-15-EMAIL-ComplaintFollowUp-JSmith-HR.txt`

## Getting Started

Try running analysis on these sample documents:

```bash
document-analyzer analyze
document-analyzer retaliation
```

Results will be saved to the current directory with visualizations and analysis reports.