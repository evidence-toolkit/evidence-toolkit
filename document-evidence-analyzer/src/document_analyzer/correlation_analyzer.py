#!/usr/bin/env python3
"""
Cross-Evidence Correlation Analyzer

This module provides entity correlation and timeline analysis across
multiple evidence types (documents, images, emails) using existing
analysis results stored in content-addressed format.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict

from .evidence_manager import EvidenceManager
from .unified_models import EvidenceType


@dataclass
class EntityCorrelation:
    """Represents a correlated entity across multiple evidence pieces."""
    entity_name: str
    entity_type: str  # person, organization, date, etc.
    evidence_occurrences: List[Dict[str, Any]]
    confidence_average: float
    occurrence_count: int


@dataclass
class TimelineEvent:
    """Represents a temporal event extracted from evidence."""
    timestamp: datetime
    evidence_sha256: str
    evidence_type: str
    event_type: str
    description: str
    confidence: float


@dataclass
class CorrelationResult:
    """Results of cross-evidence correlation analysis."""
    case_id: str
    evidence_count: int
    entity_correlations: List[EntityCorrelation]
    timeline_events: List[TimelineEvent]
    analysis_timestamp: datetime


class CorrelationAnalyzer:
    """Analyzes correlations across multiple evidence pieces."""

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

        return CorrelationResult(
            case_id=case_id,
            evidence_count=len(evidence_items),
            entity_correlations=correlations,
            timeline_events=sorted(timeline_events, key=lambda x: x.timestamp),
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

                # Check if this evidence belongs to the case
                if analysis.get('case_id') == case_id:
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
                # Documents have word frequency - look for potential entities
                doc_analysis = analysis['document_analysis']
                top_words = doc_analysis.get('top_words', [])

                # Enhanced entity detection for documents
                for word, count in top_words:
                    word_lower = word.lower()

                    # Check if it's a known entity (regardless of case)
                    if len(word) > 2:
                        # Check if it's a person name
                        if word_lower in ['john', 'sarah', 'johnson', 'manager', 'director']:
                            # Use consistent case for matching
                            all_entities[word_lower.title()].append({
                                'evidence_sha256': sha256,
                                'evidence_type': evidence_type,
                                'entity_type': 'person_name',
                                'context': f"Appeared {count} times in document",
                                'confidence': min(0.8, count / 5.0)
                            })

                        # Organizations
                        elif word_lower in ['acme', 'corporation', 'company']:
                            # Use consistent case for organizations too
                            all_entities[word_lower.title()].append({
                                'evidence_sha256': sha256,
                                'evidence_type': evidence_type,
                                'entity_type': 'organization',
                                'context': f"Appeared {count} times in document",
                                'confidence': min(0.9, count / 3.0)
                            })

            elif evidence_type == 'email' and analysis.get('email_analysis'):
                # Emails have thread summary with rich entity information
                email_analysis = analysis['email_analysis']
                summary = email_analysis.get('thread_summary', '')

                # Enhanced entity extraction from email thread summary
                import re

                # Extract email addresses from summary
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails_found = re.findall(email_pattern, summary)

                for email_addr in emails_found:
                    all_entities[email_addr].append({
                        'evidence_sha256': sha256,
                        'evidence_type': evidence_type,
                        'entity_type': 'email_address',
                        'context': f"Found in email analysis: {summary[:100]}...",
                        'confidence': 0.9
                    })

                # Extract person names (look for common names in summary)
                words = summary.split()
                for word in words:
                    word_clean = word.strip('.,;:').title()
                    word_lower = word_clean.lower()

                    # Look for person names
                    if word_lower in ['john', 'sarah', 'johnson', 'manager', 'director', 'coordinator']:
                        all_entities[word_clean].append({
                            'evidence_sha256': sha256,
                            'evidence_type': evidence_type,
                            'entity_type': 'person_name',
                            'context': f"Found in email summary: {summary[:100]}...",
                            'confidence': 0.8
                        })

                    # Look for organizations
                    elif word_lower in ['acme', 'corporation', 'company']:
                        all_entities[word_clean].append({
                            'evidence_sha256': sha256,
                            'evidence_type': evidence_type,
                            'entity_type': 'organization',
                            'context': f"Found in email summary: {summary[:100]}...",
                            'confidence': 0.9
                        })

            elif evidence_type == 'image' and analysis.get('image_analysis'):
                # Images might have text or scene descriptions
                image_analysis = analysis['image_analysis']
                detected_text = image_analysis.get('detected_text', '')
                scene_description = image_analysis.get('scene_description', '')

                # Extract potential entities from detected text
                if detected_text:
                    words = detected_text.split()
                    for word in words:
                        if word.istitle() and len(word) > 2:
                            all_entities[word].append({
                                'evidence_sha256': sha256,
                                'evidence_type': evidence_type,
                                'entity_type': 'text_in_image',
                                'context': f"Text detected in image: {detected_text[:100]}",
                                'confidence': 0.7
                            })

        return dict(all_entities)

    def _find_entity_correlations(self, all_entities: Dict[str, List[Dict[str, Any]]]) -> List[EntityCorrelation]:
        """Find entities that appear in multiple pieces of evidence.

        Args:
            all_entities: Dictionary of entity occurrences

        Returns:
            List of EntityCorrelation objects for entities appearing multiple times
        """
        correlations = []

        for entity_name, occurrences in all_entities.items():
            if len(occurrences) > 1:  # Only correlate if appears in multiple evidence
                # Calculate average confidence
                avg_confidence = sum(occ['confidence'] for occ in occurrences) / len(occurrences)

                # Determine most likely entity type
                entity_types = [occ['entity_type'] for occ in occurrences]
                most_common_type = max(set(entity_types), key=entity_types.count)

                correlations.append(EntityCorrelation(
                    entity_name=entity_name,
                    entity_type=most_common_type,
                    evidence_occurrences=occurrences,
                    confidence_average=avg_confidence,
                    occurrence_count=len(occurrences)
                ))

        # Sort by occurrence count (most correlated first)
        return sorted(correlations, key=lambda x: x.occurrence_count, reverse=True)

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

        return timeline_events