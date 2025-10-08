#!/usr/bin/env python3
"""
Cross-Evidence Correlation Analyzer

This module provides entity correlation and timeline analysis across
multiple evidence types (documents, images, emails) using existing
analysis results stored in content-addressed format.

Key Features:
- AI-powered entity extraction from OpenAI Responses API analysis
- Deterministic name canonicalization for robust entity matching
- Cross-evidence correlation with confidence scoring
- Timeline event extraction from evidence metadata

Architecture:
1. Entity Extraction: Pulls entities from AI analysis results
   - Documents: DocumentEntity objects (person, org, date, legal_term)
   - Emails: EmailParticipant objects with authority levels
   - Images: OCR text entities

2. Canonicalization: Converts names to standard forms
   - "John Q. Smith" → ("john q smith", "john smith", "j q s")
   - "Smith, John" → "john smith"
   - "Chief Executive Officer" → "ceo"

3. Correlation: Finds entities appearing in multiple evidence pieces
   - Deduplicates variant forms
   - Calculates average confidence
   - Sorts by occurrence count and confidence

4. Timeline: Extracts temporal events from evidence
   - Currently: file creation, analysis timestamps
   - Future: email dates, EXIF timestamps, content-based dates

Usage:
    from document_analyzer.evidence_manager import EvidenceManager
    from document_analyzer.correlation_analyzer import CorrelationAnalyzer

    evidence_manager = EvidenceManager("evidence")
    analyzer = CorrelationAnalyzer(evidence_manager)
    result = analyzer.analyze_case_correlations("CASE-2024-001")

    print(f"Found {len(result.entity_correlations)} correlated entities")
    for entity in result.entity_correlations[:5]:
        print(f"- {entity.entity_name} ({entity.occurrence_count} occurrences)")
"""

import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
from email.utils import parsedate_to_datetime

from .evidence_manager import EvidenceManager
from .unified_models import EvidenceType


def canonicalize_entity_name(name: str) -> Tuple[str, str, str]:
    """Deterministic entity name normalization for correlation.

    Converts entity names to canonical forms for matching across evidence.
    Returns three variants: (base_form, short_form, initials).

    Args:
        name: Entity name to canonicalize (e.g., "John Q. Smith", "CEO")

    Returns:
        Tuple of (base, short, initials):
        - base: "john q smith"
        - short: "john smith" (first + last only)
        - initials: "j q s"

    Examples:
        >>> canonicalize_entity_name("John Q. Smith")
        ("john q smith", "john smith", "j q s")
        >>> canonicalize_entity_name("Smith, John")
        ("john smith", "john smith", "j s")
        >>> canonicalize_entity_name("Chief Executive Officer")
        ("ceo", "ceo", "c")
    """
    if not name or not name.strip():
        return ("", "", "")

    # Unicode normalization (NFKC - compatibility composition)
    s = unicodedata.normalize("NFKC", name).strip()

    # Collapse multiple spaces
    s = re.sub(r"\s+", " ", s)

    # Casefold for case-insensitive matching (better than lower() for Unicode)
    low = s.casefold()

    # Role variant normalization (expand as needed)
    ROLE_VARIANTS = {
        "chief executive officer": "ceo",
        "chief operating officer": "coo",
        "chief financial officer": "cfo",
        "chief technology officer": "cto",
        "human resources": "hr",
        "human resources manager": "hr manager",
        "vice president": "vp",
    }

    for full_form, abbrev in ROLE_VARIANTS.items():
        if full_form in low:
            low = low.replace(full_form, abbrev)

    # Handle "Last, First" format (common in email headers)
    if "," in low:
        parts = [p.strip() for p in low.split(",", 1)]
        if len(parts) == 2:
            # "Smith, John" → "John Smith"
            low = f"{parts[1]} {parts[0]}"

    # Extract word parts (alphanumeric only)
    word_parts = [p for p in re.split(r"[^\w]+", low) if p]

    if not word_parts:
        return (low, low, low)

    # Base form: all words joined
    base = " ".join(word_parts)

    # Short form: first + last only (handles middle names/initials)
    if len(word_parts) >= 2:
        short = f"{word_parts[0]} {word_parts[-1]}"
    else:
        short = base

    # Initials: first letter of each word
    initials = " ".join(p[0] for p in word_parts if p)

    return (base, short, initials)


@dataclass
class EntityCorrelation:
    """Represents a correlated entity across multiple evidence pieces.

    An entity is "correlated" when it appears in 2+ different evidence files.
    This indicates the entity is significant to the case (mentioned repeatedly).

    Attributes:
        entity_name: Display name (longest proper form, e.g., "Paul Boucherat")
        entity_type: Category (person, organization, date, legal_term, email_address, etc.)
        evidence_occurrences: List of dicts with {evidence_sha256, context, confidence, original_name}
        confidence_average: Average AI confidence across all occurrences (0.0-1.0)
        occurrence_count: Number of unique evidence pieces containing this entity

    Example:
        EntityCorrelation(
            entity_name="Sarah Martinez",
            entity_type="person",
            evidence_occurrences=[
                {'evidence_sha256': 'abc123...', 'confidence': 0.95, 'context': 'Email from Sarah Martinez...'},
                {'evidence_sha256': 'def456...', 'confidence': 0.92, 'context': 'Meeting with S. Martinez...'}
            ],
            confidence_average=0.935,
            occurrence_count=2
        )
    """
    entity_name: str
    entity_type: str
    evidence_occurrences: List[Dict[str, Any]]
    confidence_average: float
    occurrence_count: int


@dataclass
class TimelineEvent:
    """Represents a temporal event extracted from evidence.

    Timeline events provide chronological context for case analysis.
    Includes AI-powered classification metadata for pattern detection.

    Attributes:
        timestamp: When the event occurred (datetime object)
        evidence_sha256: SHA256 hash of the evidence file
        evidence_type: Type of evidence (document, email, image)
        event_type: Category (file_created, analysis_performed, communication, photo_taken, etc.)
        description: Human-readable event description
        confidence: Reliability of the timestamp (1.0 = certain, <1.0 = estimated)
        ai_classification: AI-extracted metadata (legal_significance, risk_flags, communication_pattern, etc.)

    Example:
        TimelineEvent(
            timestamp=datetime(2025, 1, 15, 10, 30),
            evidence_sha256='abc123...',
            evidence_type='email',
            event_type='communication',
            description='Email: Complaint about workplace safety',
            confidence=1.0,
            ai_classification={
                'legal_significance': 'high',
                'risk_flags': ['retaliation'],
                'communication_pattern': 'hostile'
            }
        )
    """
    timestamp: datetime
    evidence_sha256: str
    evidence_type: str
    event_type: str
    description: str
    confidence: float
    ai_classification: Optional[Dict[str, Any]] = None


@dataclass
class CorrelationResult:
    """Results of cross-evidence correlation analysis.

    Contains all correlation findings for a case, including entities
    appearing across multiple evidence pieces, timeline events, and
    AI-powered temporal pattern detection.

    Attributes:
        case_id: Case identifier
        evidence_count: Number of evidence pieces analyzed
        entity_correlations: List of entities found in 2+ evidence pieces (sorted by occurrence)
        timeline_events: Chronological list of events (sorted by timestamp)
        analysis_timestamp: When this correlation analysis was performed
        temporal_sequences: Detected event patterns using AI classifications (retaliation, escalation, etc.)
        timeline_gaps: Suspicious gaps in evidence timeline (potential spoliation)

    Example:
        CorrelationResult(
            case_id='WORKPLACE-2024-001',
            evidence_count=32,
            entity_correlations=[...],  # 70 correlated entities
            timeline_events=[...],      # 64 timeline events
            temporal_sequences=[...],   # 5 retaliation patterns
            timeline_gaps=[...],        # 2 suspicious gaps
            analysis_timestamp=datetime.now()
        )
    """
    case_id: str
    evidence_count: int
    entity_correlations: List[EntityCorrelation]
    timeline_events: List[TimelineEvent]
    analysis_timestamp: datetime
    temporal_sequences: List[Dict] = field(default_factory=list)
    timeline_gaps: List[Dict] = field(default_factory=list)


class CorrelationAnalyzer:
    """Analyzes correlations across multiple evidence pieces.

    This analyzer processes evidence stored in content-addressed format,
    extracting AI-analyzed entities and correlating them across multiple
    evidence files to identify key participants, organizations, and events.

    The analyzer operates in three stages:
    1. Evidence Collection: Load all evidence for a case from derived/ storage
    2. Entity Extraction: Pull AI-extracted entities with canonicalization
    3. Correlation: Find entities appearing in multiple pieces, build timeline

    Example:
        evidence_manager = EvidenceManager("evidence")
        analyzer = CorrelationAnalyzer(evidence_manager)
        result = analyzer.analyze_case_correlations("CASE-2024-001")

        # Access results
        print(f"Top entity: {result.entity_correlations[0].entity_name}")
        print(f"Timeline span: {result.timeline_events[-1].timestamp - result.timeline_events[0].timestamp}")
    """

    def __init__(self, evidence_manager: EvidenceManager):
        """Initialize correlation analyzer.

        Args:
            evidence_manager: EvidenceManager instance for accessing stored evidence
        """
        self.evidence_manager = evidence_manager

    def analyze_case_correlations(self, case_id: str) -> CorrelationResult:
        """Analyze correlations for all evidence in a case.

        Args:
            case_id: Case identifier to analyze

        Returns:
            CorrelationResult with entity correlations and timeline
        """
        # Get all evidence for the case
        evidence_items = self._get_case_evidence(case_id)

        if not evidence_items:
            return CorrelationResult(
                case_id=case_id,
                evidence_count=0,
                entity_correlations=[],
                timeline_events=[],
                analysis_timestamp=datetime.now()
            )

        # Extract entities from all evidence
        all_entities = self._extract_entities_from_evidence(evidence_items)

        # Find correlations (entities appearing in multiple pieces)
        correlations = self._find_entity_correlations(all_entities)

        # Extract timeline events
        timeline_events = self._extract_timeline_events(evidence_items)

        # Detect temporal patterns (Phase 3: AI-powered sequence & gap detection)
        temporal_sequences = self._detect_temporal_sequences(timeline_events)
        timeline_gaps = self._detect_timeline_gaps(timeline_events)

        return CorrelationResult(
            case_id=case_id,
            evidence_count=len(evidence_items),
            entity_correlations=correlations,
            timeline_events=sorted(timeline_events, key=lambda x: x.timestamp),
            temporal_sequences=temporal_sequences,
            timeline_gaps=timeline_gaps,
            analysis_timestamp=datetime.now()
        )

    def _get_case_evidence(self, case_id: str) -> List[Dict[str, Any]]:
        """Get all evidence items for a case.

        Args:
            case_id: Case identifier

        Returns:
            List of evidence dictionaries with analysis data
        """
        evidence_items = []

        # Search through derived evidence directories
        derived_dir = self.evidence_manager.derived_dir

        for evidence_dir in derived_dir.glob("sha256=*"):
            # Check for analysis files
            analysis_file = evidence_dir / "analysis.v1.json"
            metadata_file = evidence_dir / "metadata.json"

            if not (analysis_file.exists() and metadata_file.exists()):
                continue

            try:
                # Load metadata
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                # Load analysis
                with open(analysis_file, 'r') as f:
                    analysis = json.load(f)

                # Check if this evidence belongs to the case (support both old and new schema)
                case_ids = analysis.get('case_ids', [])
                if not case_ids and 'case_id' in analysis:
                    # Legacy format - convert on the fly
                    case_ids = [analysis['case_id']] if analysis['case_id'] else []

                if case_id in case_ids:
                    evidence_items.append({
                        'sha256': evidence_dir.name.replace('sha256=', ''),
                        'metadata': metadata,
                        'analysis': analysis
                    })

            except (json.JSONDecodeError, FileNotFoundError) as e:
                # Skip invalid evidence
                continue

        return evidence_items

    def _extract_entities_from_evidence(self, evidence_items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract entities from all evidence items.

        Args:
            evidence_items: List of evidence with analysis data

        Returns:
            Dictionary mapping entity names to their occurrences
        """
        all_entities = defaultdict(list)

        for item in evidence_items:
            analysis = item['analysis']
            sha256 = item['sha256']
            evidence_type = analysis.get('evidence_type')

            # Extract entities based on evidence type
            if evidence_type == 'document' and analysis.get('document_analysis'):
                doc_analysis = analysis['document_analysis']

                # Use AI-extracted entities (DocumentEntity objects from OpenAI Responses API)
                ai_entities = doc_analysis.get('entities', [])

                if ai_entities:
                    # Process AI-extracted entities with canonicalization
                    for entity in ai_entities:
                        entity_name = entity.get('name', '')
                        if not entity_name:
                            continue

                        # Canonicalize to generate variants
                        base, short, initials = canonicalize_entity_name(entity_name)

                        # Create entity occurrence record
                        occurrence = {
                            'evidence_sha256': sha256,
                            'evidence_type': evidence_type,
                            'entity_type': entity.get('type', 'unknown'),  # person, organization, date, legal_term
                            'context': entity.get('context', '')[:200],  # Limit context length
                            'confidence': entity.get('confidence', 0.5),
                            'original_name': entity_name
                        }

                        # Index by all variants for robust matching
                        if base:
                            all_entities[base].append(occurrence.copy())
                        if short and short != base:
                            all_entities[short].append(occurrence.copy())
                        if initials and initials != base and initials != short:
                            all_entities[initials].append(occurrence.copy())
                else:
                    # Fallback: If no AI entities, use top words as backup
                    # (Preserves functionality if AI analysis is disabled)
                    top_words = doc_analysis.get('top_words', [])
                    for word, count in top_words[:20]:  # Limit to top 20 words
                        if len(word) > 3 and word.istitle():  # Likely proper noun
                            base, short, initials = canonicalize_entity_name(word)
                            all_entities[base].append({
                                'evidence_sha256': sha256,
                                'evidence_type': evidence_type,
                                'entity_type': 'unknown',
                                'context': f"Appeared {count} times in document",
                                'confidence': min(0.6, count / 10.0),  # Lower confidence for non-AI
                                'original_name': word
                            })

            elif evidence_type == 'email' and analysis.get('email_analysis'):
                # Emails have structured participant data from AI analysis
                email_analysis = analysis['email_analysis']

                # Use AI-extracted participants (EmailParticipant objects from OpenAI Responses API)
                participants = email_analysis.get('participants', [])

                if participants:
                    # Process structured participant data
                    for participant in participants:
                        # Extract email address (always present)
                        email_addr = participant.get('email_address', '').strip().lower()
                        if email_addr:
                            all_entities[email_addr].append({
                                'evidence_sha256': sha256,
                                'evidence_type': evidence_type,
                                'entity_type': 'email_address',
                                'context': f"Email participant: {participant.get('role', 'participant')} ({participant.get('authority_level', 'unknown')} level)",
                                'confidence': 0.95,  # High confidence from structured email headers
                                'original_name': email_addr
                            })

                        # Extract display name if available
                        display_name = participant.get('display_name', '').strip()
                        if display_name:
                            base, short, initials = canonicalize_entity_name(display_name)

                            occurrence = {
                                'evidence_sha256': sha256,
                                'evidence_type': evidence_type,
                                'entity_type': 'person',
                                'context': f"Email participant: {participant.get('role', 'participant')} ({participant.get('authority_level', 'unknown')} level)",
                                'confidence': participant.get('confidence', 0.9),
                                'original_name': display_name
                            }

                            # Index by all name variants
                            if base:
                                all_entities[base].append(occurrence.copy())
                            if short and short != base:
                                all_entities[short].append(occurrence.copy())
                            if initials and initials != base and initials != short:
                                all_entities[initials].append(occurrence.copy())
                else:
                    # Fallback: Extract email addresses from thread summary if no participants
                    summary = email_analysis.get('thread_summary', '')
                    if summary:
                        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                        emails_found = re.findall(email_pattern, summary)

                        for email_addr in emails_found:
                            all_entities[email_addr.lower()].append({
                                'evidence_sha256': sha256,
                                'evidence_type': evidence_type,
                                'entity_type': 'email_address',
                                'context': f"Found in email summary: {summary[:100]}...",
                                'confidence': 0.7,  # Lower confidence for regex extraction
                                'original_name': email_addr
                            })

            elif evidence_type == 'image' and analysis.get('image_analysis'):
                # Images might have text or scene descriptions
                image_analysis = analysis['image_analysis']
                detected_text = image_analysis.get('detected_text', '')
                scene_description = image_analysis.get('scene_description', '')

                # Extract potential entities from detected text (OCR)
                if detected_text:
                    words = detected_text.split()
                    for word in words:
                        if word.istitle() and len(word) > 2:
                            # Apply canonicalization for consistency
                            base, short, initials = canonicalize_entity_name(word)

                            occurrence = {
                                'evidence_sha256': sha256,
                                'evidence_type': evidence_type,
                                'entity_type': 'text_in_image',
                                'context': f"Text detected in image: {detected_text[:100]}",
                                'confidence': 0.7,  # OCR confidence moderate
                                'original_name': word
                            }

                            # Index by canonical form only (OCR is already noisy)
                            if base:
                                all_entities[base].append(occurrence)

        return dict(all_entities)

    def _find_entity_correlations(self, all_entities: Dict[str, List[Dict[str, Any]]]) -> List[EntityCorrelation]:
        """Find entities that appear in multiple pieces of evidence.

        Uses variant-based indexing with deduplication to find entities
        across different name formats (full name, short form, initials).

        Args:
            all_entities: Dictionary of entity occurrences indexed by canonical forms

        Returns:
            List of EntityCorrelation objects for entities appearing in multiple evidence pieces
        """
        # Track which original names we've already processed
        seen_original_names = set()
        correlations = []

        for canonical_name, occurrences in all_entities.items():
            # Skip if no occurrences or only single occurrence
            if not occurrences or len(occurrences) < 1:
                continue

            # Get unique original names in this canonical bucket
            original_names = {occ.get('original_name', canonical_name) for occ in occurrences}

            # Skip if we've already processed this entity group
            if original_names & seen_original_names:
                continue

            # Get unique evidence pieces (same entity may appear multiple times via variants)
            unique_evidence = {occ['evidence_sha256'] for occ in occurrences}

            # Only create correlation if entity appears in multiple evidence pieces
            if len(unique_evidence) > 1:
                seen_original_names.update(original_names)

                # Select best display name (longest proper name)
                display_name = max(
                    (occ.get('original_name', canonical_name) for occ in occurrences),
                    key=len
                )

                # Calculate average confidence across all occurrences
                avg_confidence = sum(occ['confidence'] for occ in occurrences) / len(occurrences)

                # Determine most common entity type (majority vote)
                entity_types = [occ['entity_type'] for occ in occurrences]
                most_common_type = max(set(entity_types), key=entity_types.count)

                # Deduplicate occurrences by evidence_sha256 (keep highest confidence per evidence)
                evidence_map = {}
                for occ in occurrences:
                    sha = occ['evidence_sha256']
                    if sha not in evidence_map or occ['confidence'] > evidence_map[sha]['confidence']:
                        evidence_map[sha] = occ

                correlations.append(EntityCorrelation(
                    entity_name=display_name,
                    entity_type=most_common_type,
                    evidence_occurrences=list(evidence_map.values()),
                    confidence_average=avg_confidence,
                    occurrence_count=len(unique_evidence)
                ))

        # Sort by occurrence count, then by confidence (most connected and confident first)
        return sorted(correlations, key=lambda x: (x.occurrence_count, x.confidence_average), reverse=True)

    def _extract_timeline_events(self, evidence_items: List[Dict[str, Any]]) -> List[TimelineEvent]:
        """Extract timeline events from evidence metadata and analysis.

        Args:
            evidence_items: List of evidence with analysis data

        Returns:
            List of TimelineEvent objects
        """
        timeline_events = []

        for item in evidence_items:
            analysis = item['analysis']
            metadata = item['metadata']
            sha256 = item['sha256']
            evidence_type = analysis.get('evidence_type')

            # Add file creation time as baseline event
            try:
                created_time = datetime.fromisoformat(metadata['created_time'])
                timeline_events.append(TimelineEvent(
                    timestamp=created_time,
                    evidence_sha256=sha256,
                    evidence_type=evidence_type,
                    event_type='file_created',
                    description=f"Evidence file created: {metadata['filename']}",
                    confidence=1.0
                ))
            except (ValueError, KeyError):
                pass

            # Add analysis timestamp
            try:
                analysis_time = datetime.fromisoformat(analysis['analysis_timestamp'])
                timeline_events.append(TimelineEvent(
                    timestamp=analysis_time,
                    evidence_sha256=sha256,
                    evidence_type=evidence_type,
                    event_type='analysis_performed',
                    description=f"AI analysis completed for {evidence_type} evidence",
                    confidence=1.0
                ))
            except (ValueError, KeyError):
                pass

            # Extract email send/receive timestamps
            if evidence_type == 'email' and analysis.get('email_metadata'):
                email_metadata = analysis['email_metadata']
                email_date = email_metadata.get('date')

                # Extract AI classification from email analysis
                email_analysis = analysis.get('email_analysis', {})
                ai_classification = None
                if email_analysis:
                    ai_classification = {
                        'communication_pattern': email_analysis.get('communication_pattern'),
                        'risk_flags': email_analysis.get('risk_flags', []),
                        'legal_significance': email_analysis.get('legal_significance'),
                        'escalation_count': len(email_analysis.get('escalation_events', []))
                    }

                if email_date:
                    try:
                        email_timestamp = parsedate_to_datetime(email_date)
                        # Convert to naive datetime for consistency (remove timezone info)
                        if email_timestamp.tzinfo is not None:
                            email_timestamp = email_timestamp.replace(tzinfo=None)
                        timeline_events.append(TimelineEvent(
                            timestamp=email_timestamp,
                            evidence_sha256=sha256,
                            evidence_type='email',
                            event_type='communication',
                            description=f"Email: {email_metadata.get('subject', 'No subject')}",
                            confidence=1.0,
                            ai_classification=ai_classification
                        ))
                    except Exception:
                        pass  # Malformed date

            # Extract photo capture timestamps from EXIF
            if evidence_type == 'image':
                evidence_dir = self.evidence_manager.derived_dir / f"sha256={sha256}"
                exif_file = evidence_dir / "exif.json"

                if exif_file.exists():
                    try:
                        with open(exif_file, 'r') as f:
                            exif_data = json.load(f)

                        if exif_data.get('DateTimeOriginal'):
                            exif_timestamp = datetime.strptime(
                                exif_data['DateTimeOriginal'],
                                "%Y:%m:%d %H:%M:%S"
                            )
                            timeline_events.append(TimelineEvent(
                                timestamp=exif_timestamp,
                                evidence_sha256=sha256,
                                evidence_type='image',
                                event_type='photo_taken',
                                description=f"Photo captured: {metadata.get('filename', 'unknown')}",
                                confidence=0.9  # EXIF can be manipulated
                            ))
                    except Exception:
                        pass  # Invalid EXIF

            # Extract dates mentioned in document content
            if evidence_type == 'document' and analysis.get('document_analysis'):
                doc_analysis = analysis['document_analysis']

                # Extract document-level AI classification
                doc_ai_classification = {
                    'sentiment': doc_analysis.get('sentiment'),
                    'legal_significance': doc_analysis.get('legal_significance'),
                    'risk_flags': doc_analysis.get('risk_flags', []),
                    'document_type': doc_analysis.get('document_type')
                }

                for entity in doc_analysis.get('entities', []):
                    if entity.get('type') == 'date':
                        try:
                            # Try to use dateutil.parser if available
                            try:
                                from dateutil import parser as date_parser
                                date_obj = date_parser.parse(entity['name'], fuzzy=True)
                            except ImportError:
                                # Graceful fallback if dateutil not installed
                                continue

                            # Convert to naive datetime for consistency (remove timezone info)
                            if date_obj.tzinfo is not None:
                                date_obj = date_obj.replace(tzinfo=None)

                            timeline_events.append(TimelineEvent(
                                timestamp=date_obj,
                                evidence_sha256=sha256,
                                evidence_type='document',
                                event_type='document_date_reference',
                                description=f"Date mentioned: {entity['name']} - {entity.get('context', '')[:100]}",
                                confidence=entity.get('confidence', 0.5),
                                ai_classification=doc_ai_classification
                            ))
                        except Exception:
                            pass  # Couldn't parse date

        return timeline_events

    def _detect_temporal_sequences(
        self,
        timeline_events: List[TimelineEvent],
        temporal_window_hours: int = 72
    ) -> List[Dict]:
        """Detect legally significant temporal patterns using AI classifications.

        Focuses on high-value patterns:
        - High/critical legal significance communications
        - Hostile/retaliatory communication patterns
        - Events with retaliation/harassment risk flags
        - Escalating communication sequences

        Args:
            timeline_events: List of timeline events
            temporal_window_hours: Time window for pattern detection (default 72h = 3 days)

        Returns:
            List of detected sequences with legal significance
        """
        sequences = []

        # Filter to forensically relevant events (exclude ingestion artifacts)
        relevant_events = [
            e for e in timeline_events
            if e.event_type not in ['analysis_performed', 'file_created']
        ]

        sorted_events = sorted(relevant_events, key=lambda x: x.timestamp)

        for i, anchor_event in enumerate(sorted_events):
            # Only process events with AI classification
            if not anchor_event.ai_classification:
                continue

            # Filter to high-value anchors
            ai_class = anchor_event.ai_classification

            # Check if anchor is legally significant
            is_significant = (
                ai_class.get('legal_significance') in ['high', 'critical'] or
                ai_class.get('communication_pattern') in ['hostile', 'retaliatory', 'escalating'] or
                any(flag in ai_class.get('risk_flags', []) for flag in
                    ['retaliation', 'harassment', 'discrimination', 'threatening'])
            )

            if not is_significant:
                continue

            # Find nearby events
            nearby_events = []
            for j in range(i + 1, min(i + 10, len(sorted_events))):
                time_diff = (sorted_events[j].timestamp - anchor_event.timestamp).total_seconds() / 3600

                if time_diff <= temporal_window_hours:
                    nearby_events.append(sorted_events[j])
                else:
                    break

            if len(nearby_events) >= 1:
                # Calculate time span
                time_span_hours = (nearby_events[-1].timestamp - anchor_event.timestamp).total_seconds() / 3600

                # Assess pattern significance
                pattern_risk_flags = set(ai_class.get('risk_flags', []))
                for event in nearby_events:
                    if event.ai_classification:
                        pattern_risk_flags.update(event.ai_classification.get('risk_flags', []))

                # Determine legal significance
                # Import legal domain critical flags
                from domains import legal_config
                critical_flags = legal_config.CRITICAL_RISK_FLAGS
                if critical_flags & pattern_risk_flags:
                    legal_sig = "high"
                elif ai_class.get('legal_significance') == 'critical':
                    legal_sig = "high"
                elif len(nearby_events) >= 3:
                    legal_sig = "medium"  # Multiple events in short window
                else:
                    legal_sig = "medium"

                sequences.append({
                    'anchor_event': {
                        'timestamp': anchor_event.timestamp.isoformat(),
                        'type': anchor_event.event_type,
                        'description': anchor_event.description,
                        'sha256': anchor_event.evidence_sha256,
                        'ai_classification': ai_class
                    },
                    'related_events': [{
                        'timestamp': e.timestamp.isoformat(),
                        'type': e.event_type,
                        'description': e.description,
                        'sha256': e.evidence_sha256,
                        'ai_classification': e.ai_classification
                    } for e in nearby_events],
                    'time_span_hours': round(time_span_hours, 2),
                    'time_span_days': round(time_span_hours / 24, 2),
                    'legal_significance': legal_sig,
                    'pattern_type': 'temporal_cluster',
                    'event_count': len(nearby_events) + 1,
                    'risk_flags': list(pattern_risk_flags)
                })

        return sequences

    def _detect_timeline_gaps(
        self,
        timeline_events: List[TimelineEvent],
        significant_gap_hours: int = 168  # 7 days
    ) -> List[Dict]:
        """Identify suspicious gaps in evidence timeline.

        Filters out ingestion artifacts to focus on real evidence gaps.
        Large gaps may indicate evidence spoliation, undisclosed communications,
        or investigation blind spots.

        Args:
            timeline_events: List of timeline events
            significant_gap_hours: Minimum gap duration to flag (default 168h = 7 days)

        Returns:
            List of detected gaps with significance assessment
        """
        gaps = []

        # Filter to forensically relevant events
        relevant_events = [
            e for e in timeline_events
            if e.event_type not in ['analysis_performed', 'file_created']
        ]

        sorted_events = sorted(relevant_events, key=lambda x: x.timestamp)

        for i in range(len(sorted_events) - 1):
            gap_hours = (sorted_events[i + 1].timestamp - sorted_events[i].timestamp).total_seconds() / 3600

            if gap_hours > significant_gap_hours:
                # Assess significance based on duration
                if gap_hours > 720:  # 30 days
                    significance = "high"
                elif gap_hours > 336:  # 14 days
                    significance = "medium"
                else:
                    significance = "low"

                gaps.append({
                    'gap_start': sorted_events[i].timestamp.isoformat(),
                    'gap_end': sorted_events[i + 1].timestamp.isoformat(),
                    'gap_duration_hours': round(gap_hours, 2),
                    'gap_duration_days': round(gap_hours / 24, 2),
                    'significance': significance,
                    'before_event': {
                        'type': sorted_events[i].event_type,
                        'description': sorted_events[i].description[:100],
                        'ai_classification': sorted_events[i].ai_classification
                    },
                    'after_event': {
                        'type': sorted_events[i + 1].event_type,
                        'description': sorted_events[i + 1].description[:100],
                        'ai_classification': sorted_events[i + 1].ai_classification
                    }
                })

        return gaps