#!/usr/bin/env python3
"""
Case Summary Generator

This module creates comprehensive case summaries by aggregating all evidence
analysis results, correlations, and timelines into professional reports
suitable for legal proceedings.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel, Field

from .evidence_manager import EvidenceManager
from .correlation_analyzer import CorrelationAnalyzer, CorrelationResult
from .unified_models import EvidenceType


class ExecutiveSummaryResponse(BaseModel):
    """AI-generated executive summary using OpenAI Responses API.

    Following the same forensic-grade patterns as other evidence analysis.
    """
    executive_summary: str = Field(
        ..., description="Comprehensive executive summary of the case"
    )
    key_findings: List[str] = Field(
        default_factory=list,
        description="List of 3-5 key findings from the evidence analysis"
    )
    legal_implications: List[str] = Field(
        default_factory=list,
        description="Legal implications and significance of the evidence"
    )
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="Recommended next steps or actions based on the analysis"
    )
    confidence_overall: float = Field(
        ..., ge=0.0, le=1.0,
        description="Overall confidence in the executive assessment"
    )
    risk_assessment: str = Field(
        ..., description="Overall risk level assessment (low/medium/high/critical)"
    )


@dataclass
class EvidenceSummary:
    """Summary of a single piece of evidence."""
    sha256: str
    evidence_type: str
    filename: str
    file_size: int
    analysis_confidence: Optional[float]
    key_findings: List[str]
    legal_significance: Optional[str]
    risk_flags: List[str]


@dataclass
class CaseSummary:
    """Complete case summary with all evidence and analysis."""
    case_id: str
    generation_timestamp: datetime
    evidence_count: int
    evidence_types: List[str]
    evidence_summaries: List[EvidenceSummary]
    correlation_result: CorrelationResult
    overall_assessment: Dict[str, Any]
    executive_summary: Optional[str] = None


class CaseSummaryGenerator:
    """Generates comprehensive case summaries from evidence analysis."""

    def __init__(self, evidence_manager: EvidenceManager, openai_client=None):
        """Initialize case summary generator.

        Args:
            evidence_manager: EvidenceManager instance for accessing evidence
            openai_client: Optional OpenAI client for AI executive summaries
        """
        self.evidence_manager = evidence_manager
        self.correlation_analyzer = CorrelationAnalyzer(evidence_manager)
        self.openai_client = openai_client
        self.ai_enabled = openai_client is not None

    def generate_case_summary(self, case_id: str) -> CaseSummary:
        """Generate a comprehensive summary for a case.

        Args:
            case_id: Case identifier to summarize

        Returns:
            CaseSummary object with complete case analysis
        """
        # Get correlation analysis (includes all case evidence)
        correlation_result = self.correlation_analyzer.analyze_case_correlations(case_id)

        if correlation_result.evidence_count == 0:
            raise ValueError(f"No evidence found for case ID: {case_id}")

        # Get detailed evidence summaries
        evidence_summaries = self._create_evidence_summaries(case_id)

        # Calculate overall assessment
        overall_assessment = self._calculate_overall_assessment(
            evidence_summaries, correlation_result
        )

        # Collect evidence types
        evidence_types = list(set(summary.evidence_type for summary in evidence_summaries))

        # Create base case summary
        case_summary = CaseSummary(
            case_id=case_id,
            generation_timestamp=datetime.now(),
            evidence_count=len(evidence_summaries),
            evidence_types=evidence_types,
            evidence_summaries=evidence_summaries,
            correlation_result=correlation_result,
            overall_assessment=overall_assessment
        )

        # Generate AI executive summary if enabled
        if self.ai_enabled:
            try:
                executive_response = self._generate_ai_executive_summary(case_summary)
                case_summary.executive_summary = executive_response.executive_summary
                # Could also store other AI insights in overall_assessment
                case_summary.overall_assessment['ai_key_findings'] = executive_response.key_findings
                case_summary.overall_assessment['ai_legal_implications'] = executive_response.legal_implications
                case_summary.overall_assessment['ai_recommended_actions'] = executive_response.recommended_actions
                case_summary.overall_assessment['ai_confidence'] = executive_response.confidence_overall
                case_summary.overall_assessment['ai_risk_assessment'] = executive_response.risk_assessment
            except Exception as e:
                print(f"⚠️  AI executive summary generation failed: {e}")

        return case_summary

    def _create_evidence_summaries(self, case_id: str) -> List[EvidenceSummary]:
        """Create detailed summaries for each piece of evidence in the case.

        Args:
            case_id: Case identifier

        Returns:
            List of EvidenceSummary objects
        """
        evidence_summaries = []

        # Search through derived evidence directories
        derived_dir = self.evidence_manager.derived_dir

        for evidence_dir in derived_dir.glob("sha256=*"):
            # Check for analysis files
            analysis_file = evidence_dir / "analysis.v1.json"
            metadata_file = evidence_dir / "metadata.json"

            if not (analysis_file.exists() and metadata_file.exists()):
                continue

            try:
                # Load metadata and analysis
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                with open(analysis_file, 'r') as f:
                    analysis = json.load(f)

                # Check if this evidence belongs to the case (support both old and new schema)
                case_ids = analysis.get('case_ids', [])
                if not case_ids and 'case_id' in analysis:
                    # Legacy format - convert on the fly
                    case_ids = [analysis['case_id']] if analysis['case_id'] else []

                if case_id not in case_ids:
                    continue

                sha256 = evidence_dir.name.replace('sha256=', '')
                evidence_type = analysis.get('evidence_type')

                # Extract key findings based on evidence type
                key_findings, confidence, legal_significance, risk_flags = self._extract_key_findings(
                    evidence_type, analysis
                )

                evidence_summaries.append(EvidenceSummary(
                    sha256=sha256,
                    evidence_type=evidence_type,
                    filename=metadata['filename'],
                    file_size=metadata['file_size'],
                    analysis_confidence=confidence,
                    key_findings=key_findings,
                    legal_significance=legal_significance,
                    risk_flags=risk_flags
                ))

            except (json.JSONDecodeError, KeyError) as e:
                # Skip invalid evidence
                continue

        return evidence_summaries

    def _extract_key_findings(self, evidence_type: str, analysis: Dict[str, Any]) -> tuple:
        """Extract key findings from evidence analysis.

        Args:
            evidence_type: Type of evidence (document, image, email)
            analysis: Analysis results dictionary

        Returns:
            Tuple of (key_findings, confidence, legal_significance, risk_flags)
        """
        key_findings = []
        confidence = None
        legal_significance = None
        risk_flags = []

        if evidence_type == 'document' and analysis.get('document_analysis'):
            doc_analysis = analysis['document_analysis']
            key_findings = [
                f"Document contains {doc_analysis['total_words']} words",
                f"Top concepts: {', '.join([word for word, count in doc_analysis['top_words'][:5]])}"
            ]
            # Document analysis doesn't have built-in confidence/legal assessment

        elif evidence_type == 'email' and analysis.get('email_analysis'):
            email_analysis = analysis['email_analysis']
            key_findings = [
                f"Email thread with {email_analysis['participant_count']} participants",
                f"Communication pattern: {email_analysis['communication_pattern']}",
                email_analysis['thread_summary']
            ]
            confidence = email_analysis.get('confidence_overall')
            legal_significance = email_analysis.get('legal_significance')
            risk_flags = email_analysis.get('risk_flags', [])

        elif evidence_type == 'image' and analysis.get('image_analysis'):
            image_analysis = analysis['image_analysis']
            key_findings = []

            if image_analysis.get('scene_description'):
                key_findings.append(f"Scene: {image_analysis['scene_description']}")

            if image_analysis.get('detected_text'):
                key_findings.append(f"Text detected: {image_analysis['detected_text']}")

            if image_analysis.get('detected_objects'):
                key_findings.append(f"Objects: {', '.join(image_analysis['detected_objects'])}")

            confidence = image_analysis.get('analysis_confidence')

        return key_findings, confidence, legal_significance, risk_flags

    def _generate_ai_executive_summary(self, case_summary: CaseSummary) -> ExecutiveSummaryResponse:
        """Generate AI-powered executive summary using OpenAI Responses API.

        Args:
            case_summary: CaseSummary object to analyze

        Returns:
            ExecutiveSummaryResponse with AI-generated insights
        """
        if not self.ai_enabled:
            raise ValueError("OpenAI client not available for AI executive summary")

        # Build context for AI analysis
        case_context = self._build_case_context_for_ai(case_summary)

        # Import legal domain executive summary prompt
        from domains import legal_config
        executive_summary_prompt = legal_config.EXECUTIVE_SUMMARY_PROMPT

        try:
            # OpenAI Responses API call (SAME PATTERN as other analyzers)
            response = self.openai_client.responses.parse(
                model="gpt-4o-2024-08-06",
                input=[
                    {"role": "system", "content": executive_summary_prompt},
                    {"role": "user", "content": case_context}
                ],
                text_format=ExecutiveSummaryResponse
            )

            # Handle response (SAME PATTERN as other analyzers)
            if response.status == "completed" and response.output_parsed:
                return response.output_parsed
            elif response.status == "incomplete":
                raise Exception(f"AI executive summary incomplete: {response.incomplete_details}")
            else:
                # Check for refusal
                if (response.output and len(response.output) > 0 and
                    len(response.output[0].content) > 0 and
                    response.output[0].content[0].type == "refusal"):
                    raise Exception(f"AI executive summary refused: {response.output[0].content[0].refusal}")
                raise Exception("AI executive summary failed with unknown error")

        except Exception as e:
            raise Exception(f"OpenAI executive summary generation failed: {e}")

    def _build_case_context_for_ai(self, case_summary: CaseSummary) -> str:
        """Build comprehensive case context for AI analysis.

        Args:
            case_summary: CaseSummary object

        Returns:
            Formatted case context string for AI processing
        """
        context_parts = []

        # Case overview
        context_parts.append(f"CASE ID: {case_summary.case_id}")
        context_parts.append(f"EVIDENCE COUNT: {case_summary.evidence_count}")
        context_parts.append(f"EVIDENCE TYPES: {', '.join(case_summary.evidence_types)}")
        context_parts.append("")

        # Overall assessment
        assessment = case_summary.overall_assessment
        context_parts.append("OVERALL ASSESSMENT:")
        context_parts.append(f"- Legal significance: {assessment['overall_legal_significance']}")
        context_parts.append(f"- Average confidence: {assessment['overall_confidence']:.2f}")
        context_parts.append(f"- Risk flags: {assessment['total_risk_flags']} total, {assessment['unique_risk_flags']} unique")
        context_parts.append(f"- Entity correlations: {assessment['entity_correlations_found']}")
        context_parts.append("")

        # Evidence summaries
        context_parts.append("EVIDENCE ANALYSIS:")
        for i, evidence in enumerate(case_summary.evidence_summaries, 1):
            context_parts.append(f"{i}. {evidence.filename} ({evidence.evidence_type.upper()})")
            context_parts.append(f"   - Size: {evidence.file_size:,} bytes")
            if evidence.analysis_confidence:
                context_parts.append(f"   - Confidence: {evidence.analysis_confidence:.2f}")
            if evidence.legal_significance:
                context_parts.append(f"   - Legal significance: {evidence.legal_significance}")
            if evidence.risk_flags:
                context_parts.append(f"   - Risk flags: {', '.join(evidence.risk_flags)}")
            context_parts.append("   - Key findings:")
            for finding in evidence.key_findings:
                context_parts.append(f"     • {finding}")
            context_parts.append("")

        # Entity correlations
        if case_summary.correlation_result.entity_correlations:
            context_parts.append("ENTITY CORRELATIONS:")
            for corr in case_summary.correlation_result.entity_correlations:
                context_parts.append(f"- {corr.entity_name} ({corr.entity_type}): {corr.occurrence_count} occurrences, confidence {corr.confidence_average:.2f}")
            context_parts.append("")

        # Timeline
        if case_summary.correlation_result.timeline_events:
            context_parts.append("TIMELINE EVENTS:")
            for event in case_summary.correlation_result.timeline_events[-10:]:  # Last 10 events
                context_parts.append(f"- {event.timestamp.strftime('%Y-%m-%d %H:%M')}: {event.description}")
            context_parts.append("")

        return "\n".join(context_parts)

    def _calculate_overall_assessment(
        self,
        evidence_summaries: List[EvidenceSummary],
        correlation_result: CorrelationResult
    ) -> Dict[str, Any]:
        """Calculate overall case assessment metrics.

        Args:
            evidence_summaries: List of evidence summaries
            correlation_result: Cross-evidence correlation results

        Returns:
            Dictionary with overall assessment metrics
        """
        # Calculate confidence scores
        confidences = [s.analysis_confidence for s in evidence_summaries if s.analysis_confidence]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Count risk flags
        all_risk_flags = []
        for summary in evidence_summaries:
            all_risk_flags.extend(summary.risk_flags)

        # Count legal significance levels
        legal_significance_counts = {}
        for summary in evidence_summaries:
            if summary.legal_significance:
                legal_significance_counts[summary.legal_significance] = (
                    legal_significance_counts.get(summary.legal_significance, 0) + 1
                )

        # Determine overall legal significance
        overall_legal_significance = "low"
        if "critical" in legal_significance_counts:
            overall_legal_significance = "critical"
        elif "high" in legal_significance_counts:
            overall_legal_significance = "high"
        elif "medium" in legal_significance_counts:
            overall_legal_significance = "medium"

        return {
            "overall_confidence": avg_confidence,
            "total_risk_flags": len(all_risk_flags),
            "unique_risk_flags": len(set(all_risk_flags)),
            "risk_flag_breakdown": dict(zip(*[iter(all_risk_flags)] * 2)) if all_risk_flags else {},
            "legal_significance_distribution": legal_significance_counts,
            "overall_legal_significance": overall_legal_significance,
            "entity_correlations_found": len(correlation_result.entity_correlations),
            "timeline_events_count": len(correlation_result.timeline_events),
            "evidence_type_distribution": {
                evidence_type: len([s for s in evidence_summaries if s.evidence_type == evidence_type])
                for evidence_type in set(s.evidence_type for s in evidence_summaries)
            }
        }

    def export_summary_to_json(self, case_summary: CaseSummary, output_path: Path) -> bool:
        """Export case summary to JSON file.

        Args:
            case_summary: CaseSummary object to export
            output_path: Path for output JSON file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert dataclasses to dictionaries for JSON serialization
            summary_dict = {
                "case_id": case_summary.case_id,
                "generation_timestamp": case_summary.generation_timestamp.isoformat(),
                "evidence_count": case_summary.evidence_count,
                "evidence_types": case_summary.evidence_types,
                "evidence_summaries": [
                    {
                        "sha256": summary.sha256,
                        "evidence_type": summary.evidence_type,
                        "filename": summary.filename,
                        "file_size": summary.file_size,
                        "analysis_confidence": summary.analysis_confidence,
                        "key_findings": summary.key_findings,
                        "legal_significance": summary.legal_significance,
                        "risk_flags": summary.risk_flags
                    }
                    for summary in case_summary.evidence_summaries
                ],
                "correlation_analysis": {
                    "entity_correlations": [
                        {
                            "entity_name": corr.entity_name,
                            "entity_type": corr.entity_type,
                            "occurrence_count": corr.occurrence_count,
                            "confidence_average": corr.confidence_average,
                            "evidence_occurrences": corr.evidence_occurrences
                        }
                        for corr in case_summary.correlation_result.entity_correlations
                    ],
                    "timeline_events": [
                        {
                            "timestamp": event.timestamp.isoformat(),
                            "evidence_sha256": event.evidence_sha256,
                            "evidence_type": event.evidence_type,
                            "event_type": event.event_type,
                            "description": event.description,
                            "confidence": event.confidence
                        }
                        for event in case_summary.correlation_result.timeline_events
                    ]
                },
                "overall_assessment": case_summary.overall_assessment,
                "executive_summary": case_summary.executive_summary
            }

            with open(output_path, 'w') as f:
                json.dump(summary_dict, f, indent=2)

            return True

        except Exception as e:
            print(f"Error exporting case summary: {e}")
            return False

    def format_summary_report(self, case_summary: CaseSummary) -> str:
        """Format case summary as a human-readable report.

        Args:
            case_summary: CaseSummary object to format

        Returns:
            Formatted text report
        """
        lines = []

        # Header
        lines.append("=" * 60)
        lines.append(f"CASE ANALYSIS SUMMARY: {case_summary.case_id}")
        lines.append("=" * 60)
        lines.append(f"Generated: {case_summary.generation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Overview
        lines.append("📊 CASE OVERVIEW")
        lines.append("-" * 30)
        lines.append(f"Evidence pieces analyzed: {case_summary.evidence_count}")
        lines.append(f"Evidence types: {', '.join(case_summary.evidence_types)}")
        lines.append(f"Overall legal significance: {case_summary.overall_assessment['overall_legal_significance'].upper()}")
        lines.append(f"Cross-evidence correlations: {case_summary.overall_assessment['entity_correlations_found']}")
        lines.append("")

        # Executive Summary (if available)
        if case_summary.executive_summary:
            lines.append("📋 EXECUTIVE SUMMARY")
            lines.append("-" * 30)
            lines.append(case_summary.executive_summary)
            lines.append("")

        # Evidence Details
        lines.append("📁 EVIDENCE ANALYSIS")
        lines.append("-" * 30)
        for i, summary in enumerate(case_summary.evidence_summaries, 1):
            lines.append(f"{i}. {summary.filename} ({summary.evidence_type.upper()})")
            lines.append(f"   SHA256: {summary.sha256[:16]}...")
            lines.append(f"   Size: {summary.file_size:,} bytes")

            if summary.analysis_confidence:
                lines.append(f"   Confidence: {summary.analysis_confidence:.2f}")

            if summary.legal_significance:
                lines.append(f"   Legal significance: {summary.legal_significance}")

            if summary.risk_flags:
                lines.append(f"   Risk flags: {', '.join(summary.risk_flags)}")

            lines.append("   Key findings:")
            for finding in summary.key_findings:
                lines.append(f"     • {finding}")
            lines.append("")

        # Correlations
        if case_summary.correlation_result.entity_correlations:
            lines.append("🔗 ENTITY CORRELATIONS")
            lines.append("-" * 30)
            for corr in case_summary.correlation_result.entity_correlations:
                lines.append(f"• {corr.entity_name} ({corr.entity_type})")
                lines.append(f"  Appears in {corr.occurrence_count} evidence pieces")
                lines.append(f"  Average confidence: {corr.confidence_average:.2f}")
            lines.append("")

        # Timeline
        if case_summary.correlation_result.timeline_events:
            lines.append("⏰ TIMELINE")
            lines.append("-" * 30)
            for event in case_summary.correlation_result.timeline_events[:10]:  # Show first 10
                lines.append(f"{event.timestamp.strftime('%Y-%m-%d %H:%M')} - {event.description}")
            lines.append("")

        # Risk Assessment
        if case_summary.overall_assessment['total_risk_flags'] > 0:
            lines.append("⚠️  RISK ASSESSMENT")
            lines.append("-" * 30)
            lines.append(f"Total risk flags: {case_summary.overall_assessment['total_risk_flags']}")
            lines.append(f"Unique risk types: {case_summary.overall_assessment['unique_risk_flags']}")
            lines.append("")

        return "\n".join(lines)