"""Email thread analysis using OpenAI Responses API.

This module provides forensic-grade email thread analysis following the same
proven patterns as DocumentAnalyzer. Uses OpenAI Responses API (NOT chat
completions) for deterministic, legally-admissible analysis results.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path

from .email_models import EmailThreadAnalysis
from .email_parser import EmailParser


class EmailAnalyzer:
    """Email chain analyzer following DocumentAnalyzer patterns.

    Provides forensic-grade analysis of email threads using the same
    OpenAI Responses API patterns proven successful in document analysis.
    """

    def __init__(self, openai_client, verbose: bool = True):
        """Initialize email analyzer using same pattern as DocumentAnalyzer.

        Args:
            openai_client: OpenAI client instance (from openai package)
            verbose: Enable verbose output for analysis operations
        """
        self.openai_client = openai_client
        self.verbose = verbose
        self.email_parser = EmailParser(verbose=verbose)

        # Check if AI analysis is enabled (same pattern as DocumentAnalyzer)
        self.ai_enabled = openai_client is not None

        if self.verbose and not self.ai_enabled:
            print("⚠️  AI analysis disabled - OpenAI client not available")

    def analyze_email_thread(self, emails: List[Dict[str, Any]]) -> Optional[EmailThreadAnalysis]:
        """
        Analyze email thread using OpenAI Responses API.

        CRITICAL: Uses OpenAI Responses API (same as DocumentAnalyzer), NOT chat completions.
        This ensures deterministic, forensic-grade analysis suitable for legal evidence.

        Args:
            emails: List of parsed email dictionaries from EmailParser

        Returns:
            EmailThreadAnalysis object with structured insights or None if analysis fails
        """
        if not self.ai_enabled:
            if self.verbose:
                print("⚠️  AI analysis disabled - OpenAI client not available")
            return None

        if not emails:
            if self.verbose:
                print("⚠️  No emails provided for thread analysis")
            return None

        try:
            if self.verbose:
                print(f"🤖 Analyzing email thread ({len(emails)} emails) with OpenAI Responses API...")

            # Build thread context for analysis
            thread_text = self._format_thread_for_analysis(emails)

            # Import legal domain prompt
            from domains import legal_config
            email_analysis_prompt = legal_config.EMAIL_ANALYSIS_PROMPT

            # OpenAI Responses API call (SAME PATTERN as DocumentAnalyzer)
            response = self.openai_client.responses.parse(
                model="gpt-4o-2024-08-06",
                input=[
                    {"role": "system", "content": email_analysis_prompt},
                    {"role": "user", "content": thread_text}
                ],
                text_format=EmailThreadAnalysis
            )

            # Handle responses correctly for Responses API (SAME PATTERN as DocumentAnalyzer)
            if response.status == "completed" and response.output_parsed:
                if self.verbose:
                    print(f"✅ Email thread analysis complete - confidence: {response.output_parsed.confidence_overall:.2f}")
                return response.output_parsed
            elif response.status == "incomplete":
                if self.verbose:
                    print(f"❌ Email analysis incomplete: {response.incomplete_details}")
                return None
            else:
                # Check for refusal in output (SAME PATTERN as DocumentAnalyzer)
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

    def analyze_email_files(self, file_paths: List[Path], case_id: Optional[str] = None) -> Optional[EmailThreadAnalysis]:
        """Analyze email files as a thread.

        Args:
            file_paths: List of email file paths to analyze
            case_id: Optional case identifier for tracking

        Returns:
            EmailThreadAnalysis object or None if analysis fails
        """
        if self.verbose:
            print(f"📧 Parsing {len(file_paths)} email files...")

        # Parse all email files
        emails = []
        for file_path in file_paths:
            email_data = self.email_parser.parse_file(file_path)
            if email_data:
                emails.append(email_data)
            elif self.verbose:
                print(f"⚠️  Failed to parse: {file_path}")

        if not emails:
            if self.verbose:
                print("❌ No emails successfully parsed")
            return None

        # Build thread from emails
        threaded_emails = self.email_parser.build_thread_from_emails(emails)

        if self.verbose:
            thread_metadata = self.email_parser.extract_thread_metadata(threaded_emails)
            print(f"📊 Thread metadata: {thread_metadata['participant_count']} participants, "
                  f"{thread_metadata['email_count']} emails")

        # Analyze the thread
        return self.analyze_email_thread(threaded_emails)

    def _format_thread_for_analysis(self, emails: List[Dict[str, Any]]) -> str:
        """Format email thread for AI analysis.

        Args:
            emails: List of email dictionaries in thread order

        Returns:
            Formatted thread text for AI processing
        """
        thread_parts = []

        for i, email_data in enumerate(emails):
            headers = email_data['headers']

            # Format email section
            email_section = f"""
EMAIL {i+1}/{len(emails)}:
From: {headers.get('from', 'Unknown')}
To: {', '.join(headers.get('to', []))}"""

            # Add CC if present
            if headers.get('cc'):
                email_section += f"\nCC: {', '.join(headers['cc'])}"

            email_section += f"""
Subject: {headers.get('subject', 'No Subject')}
Date: {headers.get('date', 'Unknown Date')}

{email_data.get('body', '').strip()}

---"""

            thread_parts.append(email_section)

        return '\n'.join(thread_parts)

    def export_analysis_to_json(self, analysis: EmailThreadAnalysis, output_path: Path) -> bool:
        """Export analysis results to JSON file.

        Args:
            analysis: EmailThreadAnalysis object to export
            output_path: Path for output JSON file

        Returns:
            True if export successful, False otherwise
        """
        try:
            import json

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis.dict(), f, indent=2, ensure_ascii=False)

            if self.verbose:
                print(f"✅ Analysis exported to: {output_path}")
            return True

        except Exception as e:
            if self.verbose:
                print(f"❌ Export failed: {e}")
            return False

    def get_analysis_summary(self, analysis: EmailThreadAnalysis) -> str:
        """Generate human-readable summary of analysis results.

        Args:
            analysis: EmailThreadAnalysis object

        Returns:
            Formatted summary string
        """
        summary_parts = [
            f"📧 Email Thread Analysis Summary",
            f"=" * 40,
            f"Overall Confidence: {analysis.confidence_overall:.2f}",
            f"Legal Significance: {analysis.legal_significance.upper()}",
            f"Communication Pattern: {analysis.communication_pattern}",
            f"Participants: {len(analysis.participants)}",
            f"Escalation Events: {len(analysis.escalation_events)}",
            f"Risk Flags: {', '.join(analysis.risk_flags) if analysis.risk_flags else 'None'}",
            "",
            "Thread Summary:",
            analysis.thread_summary
        ]

        if analysis.escalation_events:
            summary_parts.extend([
                "",
                "Key Escalation Events:"
            ])
            for event in analysis.escalation_events:
                summary_parts.append(
                    f"  • Email {event.email_position + 1}: {event.escalation_type} "
                    f"(confidence: {event.confidence:.2f})"
                )

        if analysis.timeline_reconstruction:
            summary_parts.extend([
                "",
                "Timeline Reconstruction:"
            ])
            for i, event in enumerate(analysis.timeline_reconstruction, 1):
                summary_parts.append(f"  {i}. {event}")

        return '\n'.join(summary_parts)