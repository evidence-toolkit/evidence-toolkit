"""
Transcript Parser for Podcast Analysis

Supports common podcast transcript formats:
- Descript (.txt with timestamps)
- Otter.ai (.txt with speaker labels)
- Rev.com (.txt or .docx)
- Generic text files
"""

from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import timedelta
import re


@dataclass
class TranscriptSegment:
    """A single segment of transcript with optional metadata"""
    text: str
    speaker: Optional[str] = None
    timestamp: Optional[timedelta] = None
    segment_index: int = 0


@dataclass
class ParsedTranscript:
    """Structured transcript with metadata"""
    segments: List[TranscriptSegment]
    format_detected: str  # "descript", "otter", "rev", "generic"
    speakers: List[str]  # Unique speakers identified
    total_duration: Optional[timedelta] = None
    has_timestamps: bool = False
    has_speaker_labels: bool = False


class TranscriptParser:
    """Parse various podcast transcript formats into structured data"""

    def parse_file(self, file_path: Path) -> ParsedTranscript:
        """
        Auto-detect format and parse transcript

        Args:
            file_path: Path to transcript file (.txt, .docx, .pdf)

        Returns:
            ParsedTranscript with structured segments
        """
        content = self._read_file(file_path)

        # Detect format
        format_type = self._detect_format(content)

        # Parse based on format
        if format_type == "descript":
            return self._parse_descript(content)
        elif format_type == "otter":
            return self._parse_otter(content)
        elif format_type == "rev":
            return self._parse_rev(content)
        else:
            return self._parse_generic(content)

    def _read_file(self, file_path: Path) -> str:
        """Read file content based on extension"""
        if file_path.suffix == '.txt':
            return file_path.read_text(encoding='utf-8')
        elif file_path.suffix == '.docx':
            # TODO: Add python-docx support
            raise NotImplementedError("DOCX support coming soon")
        elif file_path.suffix == '.pdf':
            # TODO: Add PyPDF2 support
            raise NotImplementedError("PDF support coming soon")
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

    def _detect_format(self, content: str) -> str:
        """
        Auto-detect transcript format based on patterns

        Descript: [00:00:00] Speaker: Text
        Otter:    Speaker (00:00) Text
        Rev:      Speaker [timestamp]: Text
        """
        # Check for Descript format: [HH:MM:SS] at start of lines
        if re.search(r'^\[\d{2}:\d{2}:\d{2}\]', content, re.MULTILINE):
            return "descript"

        # Check for Otter format: Speaker Name (MM:SS)
        if re.search(r'^[A-Za-z\s]+\(\d{2}:\d{2}\)', content, re.MULTILINE):
            return "otter"

        # Check for Rev format: Speaker: or [timestamp]
        if re.search(r'^\w+:', content, re.MULTILINE):
            return "rev"

        return "generic"

    def _parse_descript(self, content: str) -> ParsedTranscript:
        """
        Parse Descript format:
        [00:00:00] Speaker Name: Text here
        [00:00:15] Speaker Name: More text
        """
        segments = []
        speakers = set()

        # Pattern: [HH:MM:SS] Speaker: Text
        pattern = r'\[(\d{2}):(\d{2}):(\d{2})\]\s*([^:]+):\s*(.+?)(?=\[\d{2}:\d{2}:\d{2}\]|$)'

        for i, match in enumerate(re.finditer(pattern, content, re.DOTALL)):
            hours, minutes, seconds, speaker, text = match.groups()

            timestamp = timedelta(
                hours=int(hours),
                minutes=int(minutes),
                seconds=int(seconds)
            )

            speaker = speaker.strip()
            speakers.add(speaker)

            segments.append(TranscriptSegment(
                text=text.strip(),
                speaker=speaker,
                timestamp=timestamp,
                segment_index=i
            ))

        return ParsedTranscript(
            segments=segments,
            format_detected="descript",
            speakers=list(speakers),
            has_timestamps=True,
            has_speaker_labels=True,
            total_duration=segments[-1].timestamp if segments else None
        )

    def _parse_otter(self, content: str) -> ParsedTranscript:
        """
        Parse Otter.ai format:
        Speaker Name (00:00)
        Text here on next line

        Speaker Name (00:15)
        More text
        """
        segments = []
        speakers = set()

        lines = content.split('\n')
        current_speaker = None
        current_timestamp = None
        current_text = []
        segment_index = 0

        # Pattern: Speaker (MM:SS)
        speaker_pattern = r'^([A-Za-z\s]+)\((\d{2}):(\d{2})\)\s*$'

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this is a speaker line
            match = re.match(speaker_pattern, line)
            if match:
                # Save previous segment if exists
                if current_speaker and current_text:
                    speakers.add(current_speaker)
                    segments.append(TranscriptSegment(
                        text=' '.join(current_text),
                        speaker=current_speaker,
                        timestamp=current_timestamp,
                        segment_index=segment_index
                    ))
                    segment_index += 1

                # Start new segment
                current_speaker = match.group(1).strip()
                minutes = int(match.group(2))
                seconds = int(match.group(3))
                current_timestamp = timedelta(minutes=minutes, seconds=seconds)
                current_text = []
            else:
                # This is transcript text
                current_text.append(line)

        # Save last segment
        if current_speaker and current_text:
            speakers.add(current_speaker)
            segments.append(TranscriptSegment(
                text=' '.join(current_text),
                speaker=current_speaker,
                timestamp=current_timestamp,
                segment_index=segment_index
            ))

        return ParsedTranscript(
            segments=segments,
            format_detected="otter",
            speakers=list(speakers),
            has_timestamps=True,
            has_speaker_labels=True,
            total_duration=segments[-1].timestamp if segments else None
        )

    def _parse_rev(self, content: str) -> ParsedTranscript:
        """
        Parse Rev.com format:
        Speaker: Text here

        Speaker: More text
        """
        segments = []
        speakers = set()

        # Pattern: Speaker: Text (may span multiple lines)
        pattern = r'^(\w+):\s*(.+?)(?=^\w+:|$)'

        for i, match in enumerate(re.finditer(pattern, content, re.MULTILINE | re.DOTALL)):
            speaker, text = match.groups()
            speakers.add(speaker)

            segments.append(TranscriptSegment(
                text=text.strip(),
                speaker=speaker,
                timestamp=None,  # Rev typically doesn't include timestamps
                segment_index=i
            ))

        return ParsedTranscript(
            segments=segments,
            format_detected="rev",
            speakers=list(speakers),
            has_timestamps=False,
            has_speaker_labels=True
        )

    def _parse_generic(self, content: str) -> ParsedTranscript:
        """
        Parse generic text file with no special formatting
        Just split into paragraphs
        """
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        segments = [
            TranscriptSegment(
                text=para,
                speaker=None,
                timestamp=None,
                segment_index=i
            )
            for i, para in enumerate(paragraphs)
        ]

        return ParsedTranscript(
            segments=segments,
            format_detected="generic",
            speakers=[],
            has_timestamps=False,
            has_speaker_labels=False
        )

    def to_plain_text(self, transcript: ParsedTranscript) -> str:
        """Convert parsed transcript back to plain text"""
        return '\n\n'.join(seg.text for seg in transcript.segments)

    def get_speaker_text(self, transcript: ParsedTranscript, speaker: str) -> str:
        """Extract all text from a specific speaker"""
        speaker_segments = [
            seg.text for seg in transcript.segments
            if seg.speaker == speaker
        ]
        return '\n\n'.join(speaker_segments)


# Example usage
if __name__ == '__main__':
    parser = TranscriptParser()

    # Test with sample file
    sample_transcript = Path("sample_transcript.txt")
    if sample_transcript.exists():
        result = parser.parse_file(sample_transcript)

        print(f"Format detected: {result.format_detected}")
        print(f"Speakers: {result.speakers}")
        print(f"Segments: {len(result.segments)}")

        if result.has_timestamps:
            print(f"Duration: {result.total_duration}")

        # Show first segment
        if result.segments:
            first = result.segments[0]
            print(f"\nFirst segment:")
            print(f"  Speaker: {first.speaker}")
            print(f"  Timestamp: {first.timestamp}")
            print(f"  Text: {first.text[:100]}...")
