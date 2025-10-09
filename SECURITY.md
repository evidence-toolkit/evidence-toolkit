# Security Policy

## Supported Versions

We actively support the following versions of Evidence Toolkit with security updates:

| Version | Supported          | Support End |
| ------- | ------------------ | ----------- |
| 3.3.x   | :white_check_mark: | Current     |
| 3.2.x   | :white_check_mark: | 2025-12-31  |
| 3.1.x   | :warning: Security fixes only | 2025-10-31  |
| 3.0.x   | :warning: Security fixes only | 2025-10-31  |
| < 3.0   | :x: End of life    | 2025-10-05  |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

### How to Report

If you discover a security vulnerability, please report it responsibly:

1. **Email**: Send details to the project maintainers (contact information in README.md)
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)
3. **Response Time**: You should receive an acknowledgment within **48 hours**

### What to Expect

After reporting a vulnerability:

1. **Acknowledgment**: Within 48 hours
2. **Assessment**: We'll assess severity and impact within 1 week
3. **Fix Timeline**:
   - Critical vulnerabilities: Patch within 7 days
   - High severity: Patch within 14 days
   - Medium/Low severity: Patch in next scheduled release
4. **Disclosure**: We'll coordinate disclosure timing with you
5. **Credit**: You'll be credited in the security advisory (unless you prefer anonymity)

## Security Considerations

### Data Handling

**Local-Only Processing**:
- Evidence files are **stored locally** in the `data/` directory
- **No evidence data** is transmitted except to OpenAI API for analysis
- All analysis results stored locally on your filesystem

**OpenAI API**:
- Evidence content is sent to OpenAI API for AI analysis
- OpenAI's data usage policy: [https://openai.com/policies/api-data-usage-policies](https://openai.com/policies/api-data-usage-policies)
- As of March 2023, OpenAI does not train on API data by default
- See [PRIVACY.md](PRIVACY.md) for complete data handling documentation

**Chain of Custody**:
- All operations logged locally in `chain_of_custody.json`
- Logs include: timestamp, action, SHA256 hash
- No external transmission of custody logs

### API Key Security

**Never commit credentials**:
```bash
# ✅ Use environment variables
export OPENAI_API_KEY="your-key-here"

# ✅ Use .env file (automatically gitignored)
echo "OPENAI_API_KEY=your-key-here" > .env

# ❌ NEVER hardcode in source code
# ❌ NEVER commit to version control
```

**Key Rotation**:
- If your OpenAI API key is compromised, rotate immediately at [platform.openai.com](https://platform.openai.com/api-keys)
- Update your `.env` file or environment variable
- Evidence Toolkit will automatically use the new key

### Dependency Security

**Managed Dependencies**:
- We use `uv` for deterministic dependency management
- All dependencies pinned to specific versions in `uv.lock`
- Regular dependency updates for security patches

**Verify Installation**:
```bash
# Ensure you're using locked dependencies
uv sync

# Check for known vulnerabilities (optional)
uv run pip-audit  # If installed
```

### File System Security

**Evidence Storage**:
- Evidence files stored unencrypted in `data/` directory
- **Recommendation**: Use filesystem encryption (LUKS, FileVault, BitLocker) for sensitive cases
- **Recommendation**: Regular backups to encrypted storage
- **Recommendation**: Secure deletion of evidence when no longer needed

**Permissions**:
- Evidence Toolkit does not modify file permissions
- Ensure `data/` directory has appropriate access controls
- On multi-user systems, use: `chmod 700 data/` to restrict access

### Network Security

**Minimal Network Usage**:
- Only outbound HTTPS connections to OpenAI API
- No inbound connections required
- No telemetry or analytics transmitted
- No automatic updates (you control when to upgrade)

**Firewall Considerations**:
- Requires outbound HTTPS (port 443) to `api.openai.com`
- No other network access needed

### Known Limitations

**Forensic Use Considerations**:
1. **Local Storage Only**: All evidence stored locally - ensure proper backups
2. **No Encryption**: Evidence files not encrypted by default - use filesystem encryption if needed
3. **Chain of Custody**: Logs are local only - backup appropriately for legal compliance
4. **OpenAI Processing**: Evidence content analyzed by third-party AI service
5. **No Access Control**: No built-in user authentication - relies on filesystem permissions

**Not Suitable For**:
- Multi-tenant environments without proper isolation
- Cases requiring air-gapped processing (OpenAI API required)
- Environments with strict data residency requirements (OpenAI API is US-based)

### Best Practices

**For Maximum Security**:

1. **Isolated Environment**:
   ```bash
   # Run on dedicated system or VM
   # No other users or services
   ```

2. **Encrypted Storage**:
   ```bash
   # Use filesystem encryption
   # LUKS (Linux), FileVault (macOS), BitLocker (Windows)
   ```

3. **Regular Updates**:
   ```bash
   # Check for security updates monthly
   git pull origin main
   uv sync
   ```

4. **Audit Logs**:
   ```bash
   # Review chain of custody logs
   cat data/storage/derived/sha256=*/chain_of_custody.json
   ```

5. **Secure Disposal**:
   ```bash
   # Use secure deletion when done
   shred -vfz -n 3 data/cases/MY-CASE/*
   # Or use filesystem-level secure erase
   ```

## Security Features

### Current Security Measures

✅ **Content-Addressed Storage**: SHA256 verification prevents tampering
✅ **Chain of Custody**: Complete audit trail for all operations
✅ **Pydantic Validation**: Runtime validation prevents injection attacks
✅ **Deterministic Analysis**: Temperature=0 ensures reproducible forensic results
✅ **No Telemetry**: Zero external data transmission (except OpenAI API)
✅ **MIT License**: Full source code transparency

### Planned Security Enhancements (v4.0+)

- Encryption at rest for evidence files
- Digital signatures for chain of custody
- Multi-factor authentication for sensitive operations
- Audit log encryption and tamper detection
- Air-gapped processing mode (local LLM support)

## Compliance

**Data Protection**:
- See [PRIVACY.md](PRIVACY.md) for GDPR/data handling considerations
- Evidence Toolkit is a tool - compliance is user's responsibility
- No PII is collected or transmitted by Evidence Toolkit itself

**Legal Admissibility**:
- Chain of custody logs support legal evidence requirements
- SHA256 verification ensures evidence integrity
- Deterministic analysis (temperature=0) ensures reproducibility

## Contact

For security inquiries:
- General security questions: Open a GitHub Discussion
- Vulnerability reports: Email maintainers (see README.md)
- Urgent security issues: Contact maintainers directly

---

**Last Updated**: 2025-10-09
**Version**: v3.3.0
