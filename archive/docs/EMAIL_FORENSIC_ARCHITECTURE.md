# Email Chain Analysis: Forensic-Grade Architecture

**Building on Proven Success**

Your document and image analyzers already achieve forensic-grade analysis (4.6/5). Email analysis will use the **exact same proven patterns** to maintain consistency and quality.

---

## 🏗️ Architecture Foundation

### Proven Forensic Pattern (Document + Image Analyzers)
```python
# Your successful pattern
response = client.responses.parse(
    model="gpt-4o-2024-08-06",
    input=[system_prompt, user_content],
    text_format=StructuredAnalysisModel  # Pydantic validation
)
```

### Email Analysis Implementation
```python
# Same pattern applied to email threads
response = client.responses.parse(
    model="gpt-4o-2024-08-06",
    input=[email_thread_prompt, email_content],
    text_format=EmailThreadAnalysis  # New Pydantic model
)
```

---

## 📧 Email Analysis Models

### Core Pydantic Models (Following Your Patterns)

**`email_models.py`** - Following your `ai_models.py` structure:

```python
"""Email analysis models using OpenAI Responses API.

Following the same forensic-grade patterns as DocumentAnalysis
for consistent professional quality across all evidence types.
"""

from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class EmailParticipant(BaseModel):
    """Email participant with role analysis."""
    email_address: str = Field(..., description="Email address")
    display_name: Optional[str] = Field(None, description="Display name if available")
    role: Literal["sender", "recipient", "cc", "bcc"] = Field(..., description="Role in email")
    authority_level: Literal["executive", "management", "employee", "external"] = Field(
        ..., description="Organizational authority level"
    )

class EscalationEvent(BaseModel):
    """Detected escalation point in email thread."""
    email_position: int = Field(..., description="Position in thread (0-based)")
    escalation_type: Literal["tone_change", "new_recipient", "authority_escalation", "threat"] = Field(
        ..., description="Type of escalation detected"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in escalation detection")
    description: str = Field(..., description="Description of escalation event")

class EmailThreadAnalysis(BaseModel):
    """Complete forensic analysis of email thread.

    Uses same structure as DocumentAnalysis for consistency.
    """
    thread_summary: str = Field(..., description="Executive summary of email thread")

    participants: List[EmailParticipant] = Field(
        default_factory=list,
        description="All participants with role analysis"
    )

    communication_pattern: Literal["professional", "escalating", "hostile", "retaliatory"] = Field(
        ..., description="Overall communication pattern"
    )

    sentiment_progression: List[float] = Field(
        ..., description="Sentiment score for each email (0.0=hostile, 0.5=neutral, 1.0=professional)"
    )

    escalation_events: List[EscalationEvent] = Field(
        default_factory=list,
        description="Detected escalation points in thread"
    )

    legal_significance: Literal["critical", "high", "medium", "low"] = Field(
        ..., description="Legal importance assessment"
    )

    risk_flags: List[Literal[
        "threatening", "harassment", "discrimination", "retaliation",
        "deadline", "pii", "confidential", "hostile_takeover"
    ]] = Field(default_factory=list, description="Legal risk indicators")

    timeline_reconstruction: List[str] = Field(
        default_factory=list,
        description="Chronological summary of key events"
    )

    confidence_overall: float = Field(
        ..., ge=0.0, le=1.0,
        description="Overall confidence in analysis"
    )
```

---

## 🔧 Implementation Strategy

### Phase 1: Email Parser (Week 1)
**Goal**: Multi-format email parsing with content-addressed storage

#### Email Parser Module
```python
"""email_parser.py - Multi-format email parsing"""

import email
from email.message import EmailMessage
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

class EmailParser:
    """Parse various email formats into standardized structure."""

    def parse_eml_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse .eml format (RFC 822)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            msg = email.message_from_file(f)

        return self._extract_email_data(msg)

    def parse_msg_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse Outlook .msg format"""
        # Using extract-msg library
        import extract_msg
        msg = extract_msg.Message(str(file_path))

        return {
            'headers': {
                'from': msg.sender,
                'to': [msg.to] if msg.to else [],
                'cc': msg.cc.split(';') if msg.cc else [],
                'subject': msg.subject,
                'date': msg.date,
                'message_id': getattr(msg, 'message_id', None)
            },
            'body': msg.body,
            'attachments': [att.longFilename for att in msg.attachments]
        }

    def _extract_email_data(self, msg: EmailMessage) -> Dict[str, Any]:
        """Extract standardized data from email message."""
        return {
            'headers': {
                'from': msg.get('From'),
                'to': msg.get_all('To') or [],
                'cc': msg.get_all('Cc') or [],
                'bcc': msg.get_all('Bcc') or [],
                'subject': msg.get('Subject'),
                'date': msg.get('Date'),
                'message_id': msg.get('Message-ID'),
                'in_reply_to': msg.get('In-Reply-To'),
                'references': msg.get('References')
            },
            'body': self._extract_body(msg),
            'attachments': self._extract_attachments(msg)
        }

    def build_thread_from_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Reconstruct conversation threads from individual emails."""
        # Group by subject line (normalized)
        # Sort by timestamp
        # Link via In-Reply-To and References headers
        pass
```

### Phase 2: Email Analysis Engine (Week 2)
**Goal**: AI-powered thread analysis using your proven patterns

#### Email Analyzer Module
```python
"""email_analyzer.py - Following DocumentAnalyzer patterns"""

from typing import Optional, List, Dict, Any
from pathlib import Path
from .email_models import EmailThreadAnalysis
from .email_parser import EmailParser

class EmailAnalyzer:
    """Email chain analyzer following DocumentAnalyzer patterns."""

    def __init__(self, openai_client, verbose: bool = True):
        """Initialize using same pattern as DocumentAnalyzer."""
        self.openai_client = openai_client
        self.verbose = verbose
        self.email_parser = EmailParser()

    def analyze_email_thread(self, emails: List[Dict[str, Any]]) -> Optional[EmailThreadAnalysis]:
        """
        Analyze email thread using OpenAI Responses API.

        CRITICAL: Uses Responses API (same as DocumentAnalyzer), NOT chat completions.
        """
        if not emails:
            return None

        try:
            # Build thread context
            thread_text = self._format_thread_for_analysis(emails)

            # Legal analysis prompt (following DocumentAnalyzer pattern)
            email_analysis_prompt = """You are a forensic email analyzer for legal evidence processing.

Analyze the provided email thread with these requirements:

1. **Thread Summary**: Concise summary focusing on legal significance and communication evolution
2. **Participant Analysis**: Identify all participants with organizational authority levels
3. **Communication Pattern**: Assess overall pattern (professional, escalating, hostile, retaliatory)
4. **Sentiment Progression**: Track sentiment changes across emails in thread
5. **Escalation Detection**: Identify tone changes, authority escalation, new recipients, threats
6. **Legal Significance**: Rate critical/high/medium/low based on legal implications
7. **Risk Assessment**: Flag threatening language, harassment, discrimination, retaliation, deadlines
8. **Timeline Reconstruction**: Chronological summary of key communication events

Provide confidence scores (0.0-1.0) for all assessments. Use >0.9 only for extremely clear cases.

Focus on workplace investigation patterns: retaliation, escalation to management, policy violations, harassment sequences."""

            # OpenAI Responses API call (SAME PATTERN as DocumentAnalyzer)
            response = self.openai_client.responses.parse(
                model="gpt-4o-2024-08-06",
                input=[
                    {"role": "system", "content": email_analysis_prompt},
                    {"role": "user", "content": thread_text}
                ],
                text_format=EmailThreadAnalysis
            )

            # Handle response (SAME PATTERN as DocumentAnalyzer)
            if response.status == "completed" and response.output_parsed:
                if self.verbose:
                    print(f"✅ Email thread analysis complete - confidence: {response.output_parsed.confidence_overall:.2f}")
                return response.output_parsed
            elif response.status == "incomplete":
                if self.verbose:
                    print(f"❌ Email analysis incomplete: {response.incomplete_details}")
                return None
            else:
                # Check for refusal (SAME PATTERN as DocumentAnalyzer)
                if (response.output and len(response.output) > 0 and
                    len(response.output[0].content) > 0 and
                    response.output[0].content[0].type == "refusal"):
                    if self.verbose:
                        print(f"❌ Email analysis refused: {response.output[0].content[0].refusal}")
                return None

        except Exception as e:
            if self.verbose:
                print(f"❌ Email analysis failed: {e}")
            return None

    def _format_thread_for_analysis(self, emails: List[Dict[str, Any]]) -> str:
        """Format email thread for AI analysis."""
        thread_parts = []
        for i, email in enumerate(emails):
            headers = email['headers']
            thread_parts.append(f"""
EMAIL {i+1}/{len(emails)}:
From: {headers['from']}
To: {', '.join(headers['to'])}
CC: {', '.join(headers.get('cc', []))}
Subject: {headers['subject']}
Date: {headers['date']}

{email['body']}

---""")
        return '\n'.join(thread_parts)
```

### Phase 3: CLI Integration (Week 2)
**Goal**: Seamless integration with existing Evidence Toolkit CLI

#### Updated CLI Commands
```bash
# Following existing document-analyzer patterns
document-analyzer email-thread ./email_files --case-id CASE123
document-analyzer email-analyze <sha256>
document-analyzer email-timeline <thread-id>

# Unified evidence workflow
evidence-toolkit email ingest ./emails --case-id CASE123
evidence-toolkit email analyze <sha256>
```

---

## 📊 Evidence Storage Integration

### Content-Addressed Storage Pattern
**Following your existing evidence manager patterns:**

```
evidence/raw/sha256=<hash>/original.eml
evidence/derived/sha256=<hash>/parsed_email.json       # Parsed headers/body
evidence/derived/sha256=<hash>/thread_analysis.json    # AI analysis results
evidence/derived/sha256=<hash>/chain_of_custody.json   # Audit trail
evidence/labels/thread-<id>/                           # Thread organization
```

### Database Integration
**Extending your existing evidence.sqlite:**

```sql
-- Email-specific tables following your patterns
CREATE TABLE email_threads (
    thread_id TEXT PRIMARY KEY,
    subject_normalized TEXT,
    participant_count INTEGER,
    email_count INTEGER,
    first_email_date TIMESTAMP,
    last_email_date TIMESTAMP,
    case_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE thread_emails (
    thread_id TEXT,
    email_sha256 TEXT,
    position_in_thread INTEGER,
    timestamp TIMESTAMP,
    from_address TEXT,
    sentiment_score REAL,
    FOREIGN KEY (email_sha256) REFERENCES evidence (sha256)
);
```

---

## 🎯 Success Metrics

### Quality Standards (Match Your Current 4.6/5)
- **AI Analysis Accuracy**: >90% correct escalation detection
- **Thread Reconstruction**: >95% correct chronological ordering
- **Schema Compliance**: 100% validation against Pydantic models
- **Processing Speed**: <30 seconds per 10-email thread
- **Legal Readiness**: All outputs court-admissible with chain of custody

### Integration Success
- **CLI Consistency**: Same command patterns as document/image analysis
- **Evidence Storage**: Seamless integration with content-addressed system
- **Cross-References**: AI detection of email → document/image connections

---

## 📅 Implementation Timeline

### Week 1: Email Parser & Storage
- Multi-format email parsing (.eml, .msg, .mbox)
- Content-addressed storage integration
- Thread reconstruction logic
- Database schema extensions

### Week 2: AI Analysis Engine
- EmailThreadAnalysis Pydantic model
- AI analysis using Responses API (same pattern)
- CLI integration with existing commands
- Schema validation and testing

### Week 3: Polish & Integration
- Cross-evidence reference detection
- Performance optimization
- Comprehensive testing with real email threads
- Documentation and examples

---

This architecture leverages your **proven forensic-grade patterns** to deliver email analysis at the same professional standard as your existing document and image analysis capabilities.