# Document Inbox

This is the default input directory for the Document Evidence Analyzer.

## Usage

Drop your documents here and run analysis commands without specifying paths:

```bash
# Copy your documents to inbox
cp /path/to/your/documents/*.txt inbox/
cp /path/to/your/documents/*.pdf inbox/
cp /path/to/your/emails/*.eml inbox/

# Run analysis (defaults to ./inbox/)
document-analyzer analyze

# Run retaliation analysis (defaults to ./inbox/)
document-analyzer retaliation

# Email analysis
document-analyzer email --case-id YOUR_CASE
```

## File Naming Convention

For best timeline analysis results, use this naming pattern:
- `YYYY-MM-DD-TYPE-Description-Parties.ext`
- Example: `2025-03-15-EMAIL-ComplaintFollowUp-JSmith-HR.eml`

## Sample Data

For sample documents to test the system, see the main examples directory:
- [Sample Documents](../../examples/sample-documents/) - Legal case progression samples
- [Sample Emails](../../examples/sample-emails/) - Email communication examples
- [Sample PDFs](../../examples/sample-pdfs/) - PDF document samples

## Getting Started

Try the system with sample data:

```bash
# Copy samples to inbox
cp ../../examples/sample-documents/*.txt ./
cp ../../examples/sample-emails/*.eml ./

# Run analysis
document-analyzer analyze
document-analyzer email --case-id DEMO_CASE
document-analyzer correlate --case-id DEMO_CASE
```

Results will be saved with visualizations and analysis reports.