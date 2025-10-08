"""Multi-format email parsing for forensic analysis.

This module provides comprehensive email parsing capabilities for various
formats (.eml, .msg, .mbox) with thread reconstruction and standardized
data extraction for legal evidence processing.
"""

import email
import mailbox
import re
from email.message import EmailMessage
from email.utils import parsedate_to_datetime, parseaddr
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime


class EmailParser:
    """Parse various email formats into standardized structure.

    Supports:
    - .eml files (RFC 822 format)
    - .msg files (Outlook format, requires extract-msg)
    - .mbox files (Unix mailbox format)
    """

    def __init__(self, verbose: bool = True):
        """Initialize email parser.

        Args:
            verbose: Enable verbose output for parsing operations
        """
        self.verbose = verbose

    def parse_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse any supported email file format.

        Args:
            file_path: Path to email file

        Returns:
            Standardized email data dictionary or None if parsing fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            if self.verbose:
                print(f"❌ Email file not found: {file_path}")
            return None

        suffix = file_path.suffix.lower()

        try:
            if suffix == '.eml':
                return self.parse_eml_file(file_path)
            elif suffix == '.msg':
                return self.parse_msg_file(file_path)
            elif suffix == '.mbox':
                # For .mbox files, return the first email
                emails = self.parse_mbox_file(file_path)
                return emails[0] if emails else None
            else:
                if self.verbose:
                    print(f"⚠️  Unsupported email format: {suffix}")
                return None

        except Exception as e:
            if self.verbose:
                print(f"❌ Failed to parse {file_path}: {e}")
            return None

    def parse_eml_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse .eml format (RFC 822).

        Args:
            file_path: Path to .eml file

        Returns:
            Standardized email data dictionary
        """
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            msg = email.message_from_file(f)

        return self._extract_email_data(msg, str(file_path))

    def parse_msg_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse Outlook .msg format.

        Args:
            file_path: Path to .msg file

        Returns:
            Standardized email data dictionary
        """
        try:
            import extract_msg
        except ImportError:
            raise ImportError(
                "extract-msg library required for .msg files. "
                "Install with: pip install extract-msg"
            )

        msg = extract_msg.Message(str(file_path))

        # Convert to standard format
        return {
            'headers': {
                'from': msg.sender,
                'to': [msg.to] if msg.to else [],
                'cc': msg.cc.split(';') if msg.cc else [],
                'bcc': [],  # Usually not available in .msg
                'subject': msg.subject or '',
                'date': msg.date,
                'message_id': getattr(msg, 'message_id', None),
                'in_reply_to': getattr(msg, 'in_reply_to', None),
                'references': getattr(msg, 'references', None)
            },
            'body': msg.body or '',
            'html_body': getattr(msg, 'htmlBody', None),
            'attachments': [att.longFilename for att in msg.attachments] if msg.attachments else [],
            'source_file': str(file_path),
            'file_format': 'msg'
        }

    def parse_mbox_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse .mbox format (Unix mailbox).

        Args:
            file_path: Path to .mbox file

        Returns:
            List of standardized email data dictionaries
        """
        emails = []
        mbox = mailbox.mbox(str(file_path))

        for i, msg in enumerate(mbox):
            email_data = self._extract_email_data(msg, f"{file_path}:{i}")
            emails.append(email_data)

        return emails

    def _extract_email_data(self, msg: EmailMessage, source: str) -> Dict[str, Any]:
        """Extract standardized data from email message.

        Args:
            msg: Email message object
            source: Source identifier for the email

        Returns:
            Standardized email data dictionary
        """
        # Parse date with fallback
        date_str = msg.get('Date')
        parsed_date = None
        if date_str:
            try:
                parsed_date = parsedate_to_datetime(date_str)
            except (ValueError, TypeError):
                # Try to extract date with regex as fallback
                date_match = re.search(r'\d{1,2}\s+\w{3}\s+\d{4}', date_str)
                if date_match:
                    try:
                        parsed_date = datetime.strptime(date_match.group(), '%d %b %Y')
                    except ValueError:
                        pass

        # Extract body content
        body = self._extract_body(msg)
        html_body = self._extract_html_body(msg)

        return {
            'headers': {
                'from': msg.get('From', ''),
                'to': self._parse_address_list(msg.get_all('To') or []),
                'cc': self._parse_address_list(msg.get_all('Cc') or []),
                'bcc': self._parse_address_list(msg.get_all('Bcc') or []),
                'subject': msg.get('Subject', ''),
                'date': date_str,
                'parsed_date': parsed_date.isoformat() if parsed_date else None,
                'message_id': msg.get('Message-ID'),
                'in_reply_to': msg.get('In-Reply-To'),
                'references': msg.get('References')
            },
            'body': body,
            'html_body': html_body,
            'attachments': self._extract_attachments(msg),
            'source_file': source,
            'file_format': 'eml'
        }

    def _extract_body(self, msg: EmailMessage) -> str:
        """Extract plain text body from email message."""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    charset = part.get_content_charset() or 'utf-8'
                    try:
                        return part.get_payload(decode=True).decode(charset, errors='replace')
                    except (UnicodeDecodeError, AttributeError):
                        continue
            return ''
        else:
            if msg.get_content_type() == 'text/plain':
                charset = msg.get_content_charset() or 'utf-8'
                try:
                    return msg.get_payload(decode=True).decode(charset, errors='replace')
                except (UnicodeDecodeError, AttributeError):
                    return msg.get_payload()
        return ''

    def _extract_html_body(self, msg: EmailMessage) -> Optional[str]:
        """Extract HTML body from email message."""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/html':
                    charset = part.get_content_charset() or 'utf-8'
                    try:
                        return part.get_payload(decode=True).decode(charset, errors='replace')
                    except (UnicodeDecodeError, AttributeError):
                        continue
        return None

    def _extract_attachments(self, msg: EmailMessage) -> List[str]:
        """Extract attachment filenames from email message."""
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        attachments.append(filename)

        return attachments

    def _parse_address_list(self, addresses: List[str]) -> List[str]:
        """Parse and clean email address list."""
        parsed = []
        for addr_string in addresses:
            if isinstance(addr_string, str):
                # Split on commas and parse each address
                for addr in addr_string.split(','):
                    name, email_addr = parseaddr(addr.strip())
                    if email_addr:
                        parsed.append(email_addr)
        return parsed

    def build_thread_from_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Reconstruct conversation threads from individual emails.

        Args:
            emails: List of parsed email dictionaries

        Returns:
            List of emails sorted in thread order
        """
        if not emails:
            return []

        # Group emails by normalized subject
        subject_groups = {}
        for email_data in emails:
            subject = email_data['headers'].get('subject', '')
            normalized_subject = self._normalize_subject(subject)

            if normalized_subject not in subject_groups:
                subject_groups[normalized_subject] = []
            subject_groups[normalized_subject].append(email_data)

        # Sort each group by date and build thread relationships
        threaded_emails = []
        for subject, group_emails in subject_groups.items():
            # Sort by parsed date, then by original date string
            group_emails.sort(key=lambda x: (
                x['headers'].get('parsed_date') or '1970-01-01T00:00:00',
                x['headers'].get('date') or ''
            ))

            # Add thread position information
            for i, email_data in enumerate(group_emails):
                email_data['thread_position'] = i
                email_data['thread_size'] = len(group_emails)
                email_data['normalized_subject'] = subject

            threaded_emails.extend(group_emails)

        return threaded_emails

    def _normalize_subject(self, subject: str) -> str:
        """Normalize email subject for thread grouping.

        Removes common prefixes like 'Re:', 'Fwd:', etc.
        """
        if not subject:
            return ''

        # Remove common reply/forward prefixes
        normalized = re.sub(r'^(re|fwd?|fw):\s*', '', subject.strip(), flags=re.IGNORECASE)

        # Remove extra whitespace
        normalized = ' '.join(normalized.split())

        return normalized.lower()

    def extract_thread_metadata(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract metadata about an email thread.

        Args:
            emails: List of emails in thread order

        Returns:
            Thread metadata dictionary
        """
        if not emails:
            return {}

        # Get all participants
        participants = set()
        for email_data in emails:
            headers = email_data['headers']
            participants.add(headers.get('from', ''))
            participants.update(headers.get('to', []))
            participants.update(headers.get('cc', []))
            participants.update(headers.get('bcc', []))

        participants.discard('')  # Remove empty addresses

        # Calculate time span
        dates = []
        for email_data in emails:
            parsed_date = email_data['headers'].get('parsed_date')
            if parsed_date:
                dates.append(parsed_date)

        dates.sort()

        return {
            'thread_id': emails[0]['headers'].get('message_id', f"thread_{hash(str(emails[0]))}"),
            'subject': emails[0]['headers'].get('subject', ''),
            'normalized_subject': emails[0].get('normalized_subject', ''),
            'participant_count': len(participants),
            'participants': list(participants),
            'email_count': len(emails),
            'start_date': dates[0] if dates else None,
            'end_date': dates[-1] if dates else None,
            'duration_days': (
                (datetime.fromisoformat(dates[-1]) - datetime.fromisoformat(dates[0])).days
                if len(dates) >= 2 else 0
            )
        }