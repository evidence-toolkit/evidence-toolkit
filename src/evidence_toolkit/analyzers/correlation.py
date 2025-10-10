#!/usr/bin/env python3
"""
Cross-Evidence Correlation Analyzer - v3.0

This module provides entity correlation and timeline analysis across
multiple evidence types (documents, images, emails) using existing
analysis results stored in content-addressed format.

v3.0 Updates:
- Converted from dataclasses to Pydantic models for validation
- Uses CorrelationAnalysis, CorrelatedEntity, TimelineEvent from core.models
- Updated to use EvidenceStorage instead of EvidenceManager
- All models now validated at runtime for forensic compliance

Key Features:
- AI-powered entity extraction from OpenAI Responses API analysis
- Deterministic name canonicalization for robust entity matching
- Cross-evidence correlation with confidence scoring
- Timeline event extraction from evidence metadata
- Pydantic validation for all outputs

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
    from evidence_toolkit.core.storage import EvidenceStorage
    from evidence_toolkit.analyzers.correlation import CorrelationAnalyzer

    evidence_storage = EvidenceStorage("data/storage")
    analyzer = CorrelationAnalyzer(evidence_storage)
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
from collections import defaultdict
from email.utils import parsedate_to_datetime

from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.core.models import (
    CorrelationAnalysis,  # Was CorrelationResult
    CorrelatedEntity,      # Was EntityCorrelation
    TimelineEvent,         # Keep same name
    EvidenceType,
    EntityMatchResult,     # v3.2: AI entity matching
    # v3.1 Layer 1 enhancements
    LegalPatternAnalysis,
    Contradiction,
    CorroborationLink,
)
from evidence_toolkit.core.utils import read_json_safe, call_openai_structured, get_evidence_base_dir

# OpenAI Responses API for pattern detection (v3.1)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


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


class CorrelationAnalyzer:
    """Analyzes correlations across multiple evidence pieces.

    v3.0: Now uses Pydantic models and EvidenceStorage for validation.

    This analyzer processes evidence stored in content-addressed format,
    extracting AI-analyzed entities and correlating them across multiple
    evidence files to identify key participants, organizations, and events.

    The analyzer operates in three stages:
    1. Evidence Collection: Load all evidence for a case from derived/ storage
    2. Entity Extraction: Pull AI-extracted entities with canonicalization
    3. Correlation: Find entities appearing in multiple pieces, build timeline

    Example:
        evidence_storage = EvidenceStorage("data/storage")
        analyzer = CorrelationAnalyzer(evidence_storage)
        result = analyzer.analyze_case_correlations("CASE-2024-001")

        # Access results
        print(f"Top entity: {result.entity_correlations[0].entity_name}")
        print(f"Timeline span: {result.timeline_events[-1].timestamp - result.timeline_events[0].timestamp}")
    """

    def __init__(self, evidence_storage: EvidenceStorage, openai_client=None, verbose: bool = True):
        """Initialize correlation analyzer.

        Args:
            evidence_storage: EvidenceStorage instance for accessing stored evidence
            openai_client: Optional OpenAI client for AI pattern detection (v3.1)
            verbose: Enable verbose output for pattern detection
        """
        self.evidence_storage = evidence_storage
        self.openai_client = openai_client
        self.verbose = verbose

    def analyze_case_correlations(self, case_id: str, ai_resolve: bool = False) -> CorrelationAnalysis:
        """Analyze correlations for all evidence in a case.

        Args:
            case_id: Case identifier to analyze
            ai_resolve: If True, use AI to resolve ambiguous entity matches (v3.2 feature)

        Returns:
            CorrelationAnalysis with entity correlations and timeline (Pydantic validated)
        """
        # Get all evidence for the case
        evidence_items = self._get_case_evidence(case_id)

        if not evidence_items:
            return CorrelationAnalysis(
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

        # v3.3.1: AI-powered batch entity resolution (optimized single-call approach)
        if ai_resolve and self.openai_client:
            if self.verbose:
                print("🤖 Using AI batch resolution for ambiguous entities...")
            correlations = self._resolve_entities_with_ai_batch(correlations, all_entities, evidence_items)
            if self.verbose:
                print(f"   ✓ AI resolution complete - total correlations: {len(correlations)}")

        # Extract timeline events
        timeline_events = self._extract_timeline_events(evidence_items)

        # Detect temporal patterns (Phase 3: AI-powered sequence & gap detection)
        temporal_sequences = self._detect_temporal_sequences(timeline_events)
        timeline_gaps = self._detect_timeline_gaps(timeline_events)

        # v3.1: AI pattern detection (contradictions, corroboration, evidence gaps)
        legal_patterns = self._detect_legal_patterns(
            case_id=case_id,
            correlations=correlations,
            timeline_events=timeline_events,
            evidence_items=evidence_items
        )

        return CorrelationAnalysis(
            case_id=case_id,
            evidence_count=len(evidence_items),
            entity_correlations=correlations,
            timeline_events=sorted(timeline_events, key=lambda x: x.timestamp),
            temporal_sequences=temporal_sequences,
            timeline_gaps=timeline_gaps,
            legal_patterns=legal_patterns,
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
        derived_dir = self.evidence_storage.derived_dir

        for evidence_dir in derived_dir.glob("sha256=*"):
            # Check for analysis files
            analysis_file = evidence_dir / "analysis.v1.json"
            metadata_file = evidence_dir / "metadata.json"

            if not (analysis_file.exists() and metadata_file.exists()):
                continue

            # Load metadata and analysis using safe utility
            metadata = read_json_safe(metadata_file)
            analysis = read_json_safe(analysis_file)

            if not metadata or not analysis:
                continue  # Skip invalid evidence

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

                        # Extract display name if available (handle None from Optional[str])
                        display_name = participant.get('display_name') or ''
                        display_name = display_name.strip()

                        # If no display name, try parsing email address for person name
                        if not display_name and email_addr:
                            # Parse "Sarah.Johnson.9241@domain" → "Sarah Johnson"
                            local_part = email_addr.split('@')[0]
                            # Remove numbers and split on dots/underscores
                            name_parts = local_part.replace('.', ' ').replace('_', ' ').split()
                            # Filter out numeric parts and reconstruct name
                            name_parts = [p for p in name_parts if not p.isdigit() and len(p) > 1]
                            if name_parts:
                                display_name = ' '.join(p.capitalize() for p in name_parts)

                        if display_name:
                            base, short, initials = canonicalize_entity_name(display_name)

                            occurrence = {
                                'evidence_sha256': sha256,
                                'evidence_type': evidence_type,
                                'entity_type': 'person',
                                'context': f"Email participant: {participant.get('role', 'participant')} ({participant.get('authority_level', 'unknown')} level)",
                                'confidence': participant.get('confidence', 0.9) if participant.get('display_name') else 0.75,  # Lower confidence for parsed names
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

    def _find_entity_correlations(self, all_entities: Dict[str, List[Dict[str, Any]]]) -> List[CorrelatedEntity]:
        """Find entities that appear in multiple pieces of evidence.

        Uses variant-based indexing with deduplication to find entities
        across different name formats (full name, short form, initials).

        Args:
            all_entities: Dictionary of entity occurrences indexed by canonical forms

        Returns:
            List of CorrelatedEntity Pydantic models for entities appearing in multiple evidence pieces
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

                # Create Pydantic model instance
                correlations.append(CorrelatedEntity(
                    entity_name=display_name,
                    entity_type=most_common_type,
                    occurrence_count=len(unique_evidence),
                    confidence_average=avg_confidence,
                    evidence_occurrences=list(evidence_map.values())
                ))

        # Sort by occurrence count, then by confidence (most connected and confident first)
        return sorted(correlations, key=lambda x: (x.occurrence_count, x.confidence_average), reverse=True)

    def _extract_timeline_events(self, evidence_items: List[Dict[str, Any]]) -> List[TimelineEvent]:
        """Extract timeline events from evidence metadata and analysis.

        Args:
            evidence_items: List of evidence with analysis data

        Returns:
            List of TimelineEvent Pydantic models
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

                # v3.2 FIX: Extract escalation events as separate timeline entries
                escalation_events = email_analysis.get('escalation_events', [])
                for esc_event in escalation_events:
                    # escalation_events have: timestamp, trigger, participants, severity
                    try:
                        esc_time_str = esc_event.get('timestamp')
                        if esc_time_str:
                            # Try parsing ISO format first
                            try:
                                esc_time = datetime.fromisoformat(esc_time_str)
                            except (ValueError, AttributeError):
                                # Fallback to email date parsing
                                esc_time = parsedate_to_datetime(esc_time_str)

                            # Convert to naive datetime for consistency
                            if esc_time.tzinfo is not None:
                                esc_time = esc_time.replace(tzinfo=None)

                            timeline_events.append(TimelineEvent(
                                timestamp=esc_time,
                                evidence_sha256=sha256,
                                evidence_type='email',
                                event_type='escalation',
                                description=f"ESCALATION: {esc_event.get('trigger', 'Unknown trigger')} (severity: {esc_event.get('severity', 0):.1f})",
                                confidence=0.9,
                                ai_classification={
                                    'escalation_severity': esc_event.get('severity'),
                                    'participants': esc_event.get('participants', [])
                                }
                            ))
                    except (ValueError, KeyError, TypeError, AttributeError):
                        pass  # Malformed escalation event

            # Extract photo capture timestamps from EXIF
            if evidence_type == 'image':
                evidence_dir = get_evidence_base_dir(self.evidence_storage.derived_dir, sha256)
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

                # v3.3 Phase B: Extract date entities with associated events as semantic timeline entries
                for entity in doc_analysis.get('entities', []):
                    if entity.get('type') == 'date' and entity.get('associated_event'):
                        try:
                            # Parse the date string
                            date_str = entity.get('name', '')
                            event_description = entity.get('associated_event', '')

                            # Attempt to parse various date formats
                            parsed_date = None

                            # Try ISO format first
                            try:
                                parsed_date = datetime.fromisoformat(date_str)
                            except (ValueError, AttributeError):
                                # Try common formats
                                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d %B %Y', '%B %Y', '%d %B', '%B']:
                                    try:
                                        parsed_date = datetime.strptime(date_str, fmt)
                                        # If only month, use first day of month
                                        if fmt in ['%B %Y', '%B']:
                                            if parsed_date.year == 1900:  # Default year from strptime
                                                # Use current year if only month provided
                                                parsed_date = parsed_date.replace(year=datetime.now().year)
                                        break
                                    except (ValueError, AttributeError):
                                        continue

                                # Try dateutil parser as fallback
                                if not parsed_date:
                                    try:
                                        from dateutil import parser as date_parser
                                        parsed_date = date_parser.parse(date_str, fuzzy=True)
                                    except (ImportError, ValueError, AttributeError):
                                        pass

                            # If we successfully parsed a date, add to timeline
                            if parsed_date:
                                # Convert to naive datetime for consistency
                                if parsed_date.tzinfo is not None:
                                    parsed_date = parsed_date.replace(tzinfo=None)

                                timeline_events.append(TimelineEvent(
                                    timestamp=parsed_date,
                                    evidence_sha256=sha256,
                                    evidence_type='document',
                                    event_type='semantic_event',  # New type for AI-extracted events
                                    description=f"{date_str}: {event_description}",
                                    confidence=entity.get('confidence', 0.8),
                                    ai_classification={
                                        'original_date_string': date_str,
                                        'extracted_event': event_description,
                                        'entity_context': entity.get('context', '')[:100],
                                        **doc_ai_classification
                                    }
                                ))

                        except (ValueError, KeyError, TypeError, AttributeError):
                            # Skip malformed date entities
                            pass

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
                try:
                    from evidence_toolkit.domains import legal_config
                    critical_flags = legal_config.CRITICAL_RISK_FLAGS
                except ImportError:
                    # Fallback if domains not available
                    critical_flags = {'retaliation', 'harassment', 'discrimination', 'threatening'}

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

    def _resolve_entities_with_ai_batch(
        self,
        existing_correlations: List[CorrelatedEntity],
        all_entities: Dict[str, List[Dict[str, Any]]],
        evidence_items: List[Dict[str, Any]]
    ) -> List[CorrelatedEntity]:
        """Use AI batch resolution to find additional correlations (v3.3.1 optimization).

        Replaces O(n²) pairwise comparisons with single AI call.
        Cost: ~$0.01-0.05 vs ~$0.50-2.00 with old approach.

        Args:
            existing_correlations: Correlations found by string matching
            all_entities: All entity occurrences indexed by canonical forms
            evidence_items: All evidence for context lookup

        Returns:
            Enhanced list of correlations including AI-resolved matches
        """
        from evidence_toolkit.core.models import CorrelatedEntity, BatchEntityResolution

        if not self.openai_client:
            if self.verbose:
                print("   ⚠️  OpenAI client not available, skipping AI resolution")
            return existing_correlations

        # Build evidence context map for quick lookup
        evidence_context = {item['sha256']: item for item in evidence_items}

        # Find single-evidence entities (potential missed correlations)
        singles = []
        for canonical_name, occurrences in all_entities.items():
            unique_evidence = {occ['evidence_sha256'] for occ in occurrences}
            if len(unique_evidence) == 1 and occurrences[0].get('entity_type') == 'person':
                occ = occurrences[0]
                singles.append({
                    'name': occ.get('original_name', canonical_name),
                    'context': occ.get('context', '')[:300],  # Limit context length
                    'sha256': occ['evidence_sha256'],
                    'evidence_type': evidence_context.get(occ['evidence_sha256'], {}).get('evidence_type', 'unknown'),
                    'type': occ.get('entity_type', 'person'),
                    'confidence': occ.get('confidence', 0.8)
                })

        if not singles:
            if self.verbose:
                print("   ℹ️  No unmatched single entities found")
            return existing_correlations

        if self.verbose:
            print(f"   🤖 Batch resolving {len(singles)} unmatched entities with 1 AI call...")

        # Create batch resolution prompt
        entity_list = []
        for idx, s in enumerate(singles, 1):
            entity_list.append(f"{idx}. {s['name']} (context: \"{s['context'][:100]}...\" | evidence: {s['evidence_type']})")

        prompt = f"""You are analyzing entity names from legal evidence to identify which names refer to the same real-world people.

**Entity Names to Analyze:**
{chr(10).join(entity_list)}

**Your Task:**
Group entity names that likely refer to the same person. Consider:
- Informal vs formal names (e.g., "Sarah" vs "Sarah Johnson")
- Nicknames and abbreviations (e.g., "Bob" vs "Robert")
- Same role/organization mentioned in context
- NO conflicting surnames or organizations

**Conservative Bias:** Only group if CONFIDENT (>0.7) they're the same person. When in doubt, leave unmatched.

Return structured JSON with entity groups."""

        try:
            # Single AI call for all entities using standardized utility
            batch_result = call_openai_structured(
                self.openai_client,
                "gpt-4o-mini",
                "",  # No system prompt needed, instructions in user prompt
                prompt,
                BatchEntityResolution,
                verbose=self.verbose
            )

            if self.verbose:
                print(f"   ✓ Batch resolution: {batch_result.groups_created} groups from {batch_result.total_input_entities} entities")

            # Create new correlations from entity groups
            new_correlations = []
            matched_names = set()

            for group in batch_result.entity_groups:
                if group.confidence < 0.7:
                    continue  # Skip low-confidence groups

                # Find all singles that match this group
                group_occurrences = []
                all_names = [group.canonical_name] + group.variant_names

                for single in singles:
                    if single['name'] in all_names:
                        group_occurrences.append({
                            'evidence_sha256': single['sha256'],
                            'evidence_type': single['evidence_type'],
                            'entity_type': single['type'],
                            'context': single['context'],
                            'confidence': single['confidence'],
                            'original_name': single['name']
                        })
                        matched_names.add(single['name'])

                if len(group_occurrences) >= 2:
                    # Create correlation from grouped entities
                    new_corr = CorrelatedEntity(
                        entity_name=group.canonical_name,
                        entity_type='person',
                        occurrence_count=len(group_occurrences),
                        confidence_average=sum(o['confidence'] for o in group_occurrences) / len(group_occurrences),
                        evidence_occurrences=group_occurrences
                    )
                    new_correlations.append(new_corr)

                    if self.verbose:
                        variant_str = ', '.join(f"'{v}'" for v in group.variant_names[:3])
                        print(f"   ✓ NEW correlation: '{group.canonical_name}' ← {variant_str} (AI: {group.confidence:.2f})")

            # Combine with existing correlations
            all_correlations = existing_correlations + new_correlations

            # Sort by occurrence count
            return sorted(all_correlations, key=lambda x: (x.occurrence_count, x.confidence_average), reverse=True)

        except Exception as e:
            if self.verbose:
                print(f"   ⚠️  AI batch resolution failed: {e}")
            return existing_correlations

    def _resolve_entities_with_ai(
        self,
        existing_correlations: List[CorrelatedEntity],
        all_entities: Dict[str, List[Dict[str, Any]]],
        evidence_items: List[Dict[str, Any]]
    ) -> List[CorrelatedEntity]:
        """Use AI to find additional correlations missed by string matching.

        DEPRECATED in v3.3.1: Use _resolve_entities_with_ai_batch() instead.
        This O(n²) implementation makes too many API calls.

        Checks for entities that appear in only one evidence piece and tries to
        match them with existing correlations or other singles using AI reasoning.

        Args:
            existing_correlations: Correlations found by string matching
            all_entities: All entity occurrences indexed by canonical forms
            evidence_items: All evidence for context lookup

        Returns:
            Enhanced list of correlations including AI-resolved matches
        """
        from evidence_toolkit.core.models import CorrelatedEntity

        # Build evidence context map for quick lookup
        evidence_context = {item['sha256']: item for item in evidence_items}

        # Find single-evidence entities (potential missed correlations)
        singles = []
        for canonical_name, occurrences in all_entities.items():
            unique_evidence = {occ['evidence_sha256'] for occ in occurrences}
            if len(unique_evidence) == 1:  # Only in one piece of evidence
                # Get the occurrence
                occ = occurrences[0]
                singles.append({
                    'name': occ['original_name'],
                    'canonical': canonical_name,
                    'sha256': occ['evidence_sha256'],
                    'type': occ['entity_type'],
                    'context': occ['context'],
                    'evidence_type': occ['evidence_type'],
                    'confidence': occ['confidence']
                })

        if not singles:
            return existing_correlations

        if self.verbose:
            print(f"   Found {len(singles)} single-evidence entities to check")

        # Try matching singles with existing correlations
        new_correlations = list(existing_correlations)
        matched_singles = set()

        for single in singles:
            if single['name'] in matched_singles:
                continue

            # Try matching with existing correlations
            best_match = None
            best_confidence = 0.7  # Threshold for AI match

            for corr in existing_correlations:
                # Use first occurrence from correlation for comparison
                if not corr.evidence_occurrences:
                    continue

                corr_occ = corr.evidence_occurrences[0]

                # Ask AI if they match
                match_result = self._ai_match_entities(
                    entity_a=single['name'],
                    context_a=single['context'],
                    type_a=single['evidence_type'],
                    entity_b=corr.entity_name,
                    context_b=corr_occ.get('context', ''),
                    type_b=corr_occ.get('evidence_type', 'unknown')
                )

                if match_result and match_result.is_same_entity and match_result.confidence > best_confidence:
                    best_match = corr
                    best_confidence = match_result.confidence

            # If matched, merge into existing correlation
            if best_match:
                # Find the correlation in our list and update it
                for i, corr in enumerate(new_correlations):
                    if corr.entity_name == best_match.entity_name:
                        # Add this occurrence to the correlation
                        updated_occurrences = list(corr.evidence_occurrences)
                        updated_occurrences.append({
                            'evidence_sha256': single['sha256'],
                            'evidence_type': single['evidence_type'],
                            'entity_type': single['type'],
                            'context': single['context'],
                            'confidence': single['confidence'],
                            'original_name': single['name']
                        })

                        # Recalculate stats
                        new_correlations[i] = CorrelatedEntity(
                            entity_name=corr.entity_name,
                            entity_type=corr.entity_type,
                            occurrence_count=len(updated_occurrences),
                            confidence_average=sum(o.get('confidence', 0.5) for o in updated_occurrences) / len(updated_occurrences),
                            evidence_occurrences=updated_occurrences
                        )
                        matched_singles.add(single['name'])
                        if self.verbose:
                            print(f"   ✓ Matched '{single['name']}' → '{corr.entity_name}' (AI confidence: {best_confidence:.2f})")
                        break

        # v3.3.1: Removed O(n²) pairwise matching code - superseded by batch resolution
        # The old code (lines 1211-1353) made n×(n-1)/2 individual AI calls to match singles.
        # Batch resolution (_resolve_entities_with_ai_batch) does the same job in 1 call.

        # Sort by occurrence count (most connected first)
        return sorted(new_correlations, key=lambda x: (x.occurrence_count, x.confidence_average), reverse=True)

    def _detect_legal_patterns(
        self,
        case_id: str,
        correlations: List[CorrelatedEntity],
        timeline_events: List[TimelineEvent],
        evidence_items: List[Dict[str, Any]]
    ) -> Optional[LegalPatternAnalysis]:
        """Use AI to detect contradictions, corroboration, and evidence gaps.

        v3.1 Layer 1 Enhancement: AI-powered cross-evidence pattern detection
        for contradiction analysis, corroboration assessment, and evidence quality evaluation.

        Args:
            case_id: Case identifier
            correlations: Entity correlations across evidence
            timeline_events: Timeline of events
            evidence_items: Raw evidence data

        Returns:
            LegalPatternAnalysis if AI available and patterns detected, None otherwise
        """
        if not self.openai_client or not OPENAI_AVAILABLE:
            if self.verbose:
                print("⚠️  Legal pattern detection skipped - OpenAI client not available")
            return None

        if not correlations and not timeline_events:
            if self.verbose:
                print("⚠️  Legal pattern detection skipped - no correlation data")
            return None

        try:
            if self.verbose:
                print(f"🤖 Detecting legal patterns with AI (case: {case_id})...")

            # Build context from correlation data
            context = self._build_correlation_context(correlations, timeline_events, evidence_items)

            # Import legal domain prompt
            from evidence_toolkit.domains import legal_config
            pattern_prompt = legal_config.CORRELATION_PATTERN_PROMPT

            # Call OpenAI Responses API using standardized utility
            result = call_openai_structured(
                self.openai_client,
                "gpt-4o-mini",  # Cost-effective model (fixed from gpt-4.1-mini)
                pattern_prompt,
                context,
                LegalPatternAnalysis,
                verbose=self.verbose
            )

            if self.verbose:
                print(f"✅ Legal pattern analysis complete - confidence: {result.confidence:.2f}")
                print(f"   Contradictions: {len(result.contradictions)}")
                print(f"   Corroboration links: {len(result.corroboration)}")
                print(f"   Evidence gaps: {len(result.evidence_gaps)}")
            return result

        except Exception as e:
            if self.verbose:
                print(f"❌ Legal pattern analysis failed: {e}")
            return None

    def _build_correlation_context(
        self,
        correlations: List[CorrelatedEntity],
        timeline_events: List[TimelineEvent],
        evidence_items: List[Dict[str, Any]]
    ) -> str:
        """Build context string for AI pattern analysis.

        Args:
            correlations: Entity correlations
            timeline_events: Timeline events
            evidence_items: Evidence data

        Returns:
            Formatted context string for AI
        """
        context_parts = []

        # Entity correlations section
        if correlations:
            context_parts.append("ENTITY CORRELATIONS:")
            for corr in correlations[:20]:  # Top 20 entities
                context_parts.append(
                    f"- {corr.entity_name} ({corr.entity_type}): appears in {corr.occurrence_count} evidence pieces, "
                    f"avg confidence {corr.confidence_average:.2f}"
                )
            context_parts.append("")

        # Timeline events section
        if timeline_events:
            context_parts.append("TIMELINE EVENTS:")
            for event in timeline_events[:30]:  # Recent 30 events
                context_parts.append(
                    f"- {event.timestamp.isoformat()}: {event.description} "
                    f"(type: {event.event_type}, source: {event.evidence_sha256[:8]}...)"
                )
            context_parts.append("")

        # Evidence summaries section (if available)
        context_parts.append("EVIDENCE SUMMARIES:")
        for item in evidence_items[:10]:  # First 10 evidence pieces
            sha256 = item.get('sha256', 'unknown')[:16]
            evidence_type = item.get('evidence_type', 'unknown')

            # Extract AI summary if available
            if evidence_type == 'document' and 'document_analysis' in item:
                summary = item['document_analysis'].get('summary', 'No summary')[:200]
                context_parts.append(f"[{sha256}] Document: {summary}")
            elif evidence_type == 'email' and 'email_analysis' in item:
                summary = item['email_analysis'].get('thread_summary', 'No summary')[:200]
                context_parts.append(f"[{sha256}] Email: {summary}")
            elif evidence_type == 'image' and 'image_analysis' in item:
                description = item['image_analysis'].get('scene_description', 'No description')[:200]
                context_parts.append(f"[{sha256}] Image: {description}")

        return '\n'.join(context_parts)
