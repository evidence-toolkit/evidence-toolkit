#!/usr/bin/env python3
"""Case Summary Generator - v3.0

Creates comprehensive case summaries by aggregating all evidence analysis results,
correlations, and timelines into professional reports suitable for legal proceedings.

Moved from document_analyzer/case_summary_generator.py for v3.0 architecture.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict
from pydantic import BaseModel, Field

from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.core.models import (
    CorrelationAnalysis,
    EvidenceSummary,  # v3.1: Moved from @dataclass to Pydantic in models.py
    CaseSummary,      # v3.1: Moved from @dataclass to Pydantic in models.py
)
from evidence_toolkit.analyzers.correlation import CorrelationAnalyzer


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


class ChunkSummaryResponse(BaseModel):
    """AI-generated summary for a chunk of evidence.

    Used in map-reduce pattern for handling large cases.
    """
    chunk_summary: str = Field(
        ..., description="Summary of evidence in this chunk"
    )
    key_entities: List[str] = Field(
        default_factory=list,
        description="Key people, organizations, or entities in this chunk"
    )
    key_findings: List[str] = Field(
        default_factory=list,
        description="3-5 most important findings from this chunk"
    )
    risk_flags: List[str] = Field(
        default_factory=list,
        description="Risk or legal concern flags from this chunk"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confidence in this chunk's analysis"
    )


class EnhancedExecutiveSummary(BaseModel):
    """Client-ready executive summary with strategic recommendations and quantified risk.

    v3.2: Enhancement layer that transforms forensic analysis into actionable legal strategy.
    This extends ExecutiveSummaryResponse with tribunal probability, financial estimates,
    and strategic recommendations suitable for client delivery.
    """
    # Narrative summary
    executive_summary: str = Field(
        ..., description="Polished narrative summary for client delivery"
    )
    key_findings: List[str] = Field(
        default_factory=list,
        description="3-5 tribunal-winning discoveries with evidence support"
    )

    # Quantified risk assessment (NEW in v3.2)
    tribunal_probability: float = Field(
        ..., ge=0.0, le=1.0,
        description="Success probability at tribunal (0.0-1.0 based on evidence strength)"
    )
    financial_exposure_summary: str = Field(
        ..., description="Financial exposure summary (e.g., '£40,000-60,000 total exposure')"
    )
    claim_strength_summary: str = Field(
        ..., description="Claim strength summary (e.g., 'Unfair dismissal: STRONG, Whistleblowing: MODERATE')"
    )

    # Strategic recommendations (NEW in v3.2)
    immediate_actions: List[str] = Field(
        default_factory=list,
        description="Urgent next steps (file ET1, ACAS conciliation, deadlines)"
    )
    settlement_recommendation: str = Field(
        default="Not assessed",
        description="Settlement range recommendation (e.g., '£45,000-55,000 based on mid-range exposure')"
    )
    evidence_gaps: List[str] = Field(
        default_factory=list,
        description="Missing evidence that would strengthen the case"
    )

    # Metadata
    confidence_overall: float = Field(
        ..., ge=0.0, le=1.0,
        description="Overall confidence in enhanced recommendations"
    )
    enhancement_applied: bool = Field(
        default=True,
        description="Whether AI enhancement was successfully applied"
    )


class SummaryGenerator:
    """Generates comprehensive case summaries from evidence analysis.

    v3.0: Renamed from CaseSummaryGenerator, now uses EvidenceStorage
    """

    def __init__(self, storage: EvidenceStorage, openai_client=None, case_type: str = 'generic'):
        """Initialize summary generator.

        Args:
            storage: EvidenceStorage instance for accessing evidence
            openai_client: Optional OpenAI client for AI executive summaries
            case_type: Type of case for domain-specific prompts (generic, workplace, contract)
        """
        self.storage = storage
        # v3.1: Pass openai_client to CorrelationAnalyzer for AI pattern detection
        self.correlation_analyzer = CorrelationAnalyzer(storage, openai_client=openai_client, verbose=True)
        self.openai_client = openai_client
        self.ai_enabled = openai_client is not None
        self.case_type = case_type.lower()

    def generate_case_summary(self, case_id: str) -> CaseSummary:
        """Generate a comprehensive summary for a case.

        Args:
            case_id: Case identifier to summarize

        Returns:
            CaseSummary object with complete case analysis

        Raises:
            ValueError: If no evidence found for case
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
                # Step 1: Generate forensic summary (technical analysis)
                print("   🔬 Generating forensic executive summary...")
                executive_response = self._generate_ai_executive_summary(case_summary)

                # Step 2: Enhance for client delivery (v3.2 enhancement layer)
                print("   ✨ Enhancing summary with tribunal probability & financial estimates...")
                enhanced_response = self._enhance_executive_summary(
                    executive_response,
                    correlation_result
                )

                # Use enhanced summary for client delivery
                case_summary.executive_summary = enhanced_response.executive_summary

                # Store enhanced insights in overall_assessment
                case_summary.overall_assessment['ai_key_findings'] = enhanced_response.key_findings
                case_summary.overall_assessment['ai_confidence'] = enhanced_response.confidence_overall
                case_summary.overall_assessment['enhancement_applied'] = enhanced_response.enhancement_applied

                # v3.2: Store quantified risk assessment
                case_summary.overall_assessment['tribunal_probability'] = enhanced_response.tribunal_probability
                case_summary.overall_assessment['financial_exposure_summary'] = enhanced_response.financial_exposure_summary
                case_summary.overall_assessment['claim_strength_summary'] = enhanced_response.claim_strength_summary
                case_summary.overall_assessment['immediate_actions'] = enhanced_response.immediate_actions
                case_summary.overall_assessment['settlement_recommendation'] = enhanced_response.settlement_recommendation
                case_summary.overall_assessment['evidence_gaps'] = enhanced_response.evidence_gaps

                # Also store forensic response for reference
                case_summary.overall_assessment['forensic_summary'] = executive_response.executive_summary
                case_summary.overall_assessment['forensic_legal_implications'] = executive_response.legal_implications
                case_summary.overall_assessment['forensic_recommended_actions'] = executive_response.recommended_actions
                case_summary.overall_assessment['forensic_risk_assessment'] = executive_response.risk_assessment

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
        derived_dir = self.storage.derived_dir

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

            # Extract AI analysis fields if available (v3.0 AI-powered analysis)
            if doc_analysis.get('ai_summary'):
                # Use AI-generated summary as primary finding
                key_findings = [doc_analysis['ai_summary']]

                # Add entity information if available
                if doc_analysis.get('entities'):
                    entity_count = len(doc_analysis['entities'])
                    key_entity_types = set(e.get('type', 'unknown') for e in doc_analysis['entities'][:5])
                    key_findings.append(f"Extracted {entity_count} entities: {', '.join(key_entity_types)}")

                # Extract AI assessment fields
                confidence = doc_analysis.get('analysis_confidence')
                legal_significance = doc_analysis.get('legal_significance')
                risk_flags = doc_analysis.get('risk_flags', [])
            else:
                # Fallback to basic word frequency analysis (legacy/no-AI mode)
                key_findings = [
                    f"Document contains {doc_analysis['total_words']} words",
                    f"Top concepts: {', '.join([word for word, count in doc_analysis['top_words'][:5]])}"
                ]
                # No AI assessment available in word-frequency-only mode

        elif evidence_type == 'email' and analysis.get('email_analysis'):
            email_analysis = analysis['email_analysis']
            # v3.1: email_analysis is now EmailThreadAnalysis with participants list
            participant_count = len(email_analysis.get('participants', []))
            key_findings = [
                f"Email thread with {participant_count} participants",
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

        Raises:
            ValueError: If OpenAI client not available
            Exception: If AI generation fails
        """
        if not self.ai_enabled:
            raise ValueError("OpenAI client not available for AI executive summary")

        # Build context for AI analysis
        case_context = self._build_case_context_for_ai(case_summary)

        # Import legal domain executive summary prompts and select based on case type
        from evidence_toolkit.domains import legal_config
        executive_summary_prompt = legal_config.EXECUTIVE_SUMMARY_PROMPTS.get(
            self.case_type,
            legal_config.EXECUTIVE_SUMMARY_PROMPT_GENERIC
        )

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

    def _enhance_executive_summary(
        self,
        forensic_response: ExecutiveSummaryResponse,
        correlation_result: CorrelationAnalysis
    ) -> EnhancedExecutiveSummary:
        """Enhance forensic summary into client-ready strategic assessment.

        v3.2: Post-processing layer that transforms technical analysis into actionable
        legal strategy with tribunal probability, financial estimates, and recommendations.

        Args:
            forensic_response: Original AI-generated executive summary (forensic)
            correlation_result: Correlation analysis with legal patterns

        Returns:
            EnhancedExecutiveSummary with quantified risk and strategic recommendations

        Raises:
            ValueError: If OpenAI client not available
            Exception: If enhancement fails (returns fallback with forensic data)
        """
        if not self.ai_enabled:
            raise ValueError("AI enhancement requires OpenAI client")

        # Extract metadata for enhancement context
        contradiction_count = 0
        corroboration_strength = "MODERATE"
        evidence_gap_count = 0

        if correlation_result.legal_patterns:
            contradiction_count = len(correlation_result.legal_patterns.contradictions)
            corroboration_items = correlation_result.legal_patterns.corroboration
            corroboration_strength = "STRONG" if any(
                c.corroboration_strength == "strong" for c in corroboration_items
            ) else "MODERATE"
            evidence_gap_count = len(correlation_result.legal_patterns.evidence_gaps)

        # Timeline analysis
        timeline_days = 0
        if correlation_result.timeline_events and len(correlation_result.timeline_events) > 1:
            first_event = min(correlation_result.timeline_events, key=lambda e: e.timestamp)
            last_event = max(correlation_result.timeline_events, key=lambda e: e.timestamp)
            timeline_days = (last_event.timestamp - first_event.timestamp).days

        # Build enhancement context (structured data for AI)
        enhancement_context = f"""
<forensic_summary>
{forensic_response.executive_summary}

Key findings:
{chr(10).join(f'- {finding}' for finding in forensic_response.key_findings)}

Legal implications:
{chr(10).join(f'- {impl}' for impl in forensic_response.legal_implications)}

Recommended actions (forensic):
{chr(10).join(f'- {action}' for action in forensic_response.recommended_actions)}

Risk assessment: {forensic_response.risk_assessment}
Confidence: {forensic_response.confidence_overall:.2f}
</forensic_summary>

<correlation_patterns>
- Contradictions found: {contradiction_count}
- Corroboration strength: {corroboration_strength}
- Evidence gaps identified: {evidence_gap_count}
- Legal patterns analyzed: {len(correlation_result.legal_patterns.contradictions + correlation_result.legal_patterns.corroboration + correlation_result.legal_patterns.evidence_gaps) if correlation_result.legal_patterns else 0}
</correlation_patterns>

<case_metadata>
- Evidence count: {len(correlation_result.entity_correlations)}
- Critical contradictions: {contradiction_count}
- Corroboration strength: {corroboration_strength}
- Timeline span: {timeline_days} days
- Entity network size: {len(correlation_result.entity_correlations)}
- Case type: {self.case_type}
</case_metadata>
"""

        # Get enhancer prompt from legal domain config
        from evidence_toolkit.domains import legal_config

        try:
            # Call OpenAI for enhancement using Responses API
            response = self.openai_client.responses.parse(
                model="gpt-4o-2024-08-06",
                input=[
                    {"role": "system", "content": legal_config.EXECUTIVE_SUMMARY_ENHANCER_PROMPT},
                    {"role": "user", "content": enhancement_context}
                ],
                text_format=EnhancedExecutiveSummary
            )

            # Handle response (same pattern as other analyzers)
            if response.status == "completed" and response.output_parsed:
                print("   ✨ Executive summary enhanced with tribunal probability & financial estimates")
                return response.output_parsed

            elif response.status == "incomplete":
                raise Exception(f"Enhancement incomplete: {response.incomplete_details}")

            else:
                # Check for refusal
                if (response.output and len(response.output) > 0 and
                    len(response.output[0].content) > 0 and
                    response.output[0].content[0].type == "refusal"):
                    raise Exception(f"Enhancement refused: {response.output[0].content[0].refusal}")
                raise Exception("Enhancement failed with unknown error")

        except Exception as e:
            # Fallback: return forensic response wrapped in enhanced structure
            print(f"   ⚠️  Enhancement failed ({e}), using forensic summary as fallback")

            return EnhancedExecutiveSummary(
                executive_summary=forensic_response.executive_summary,
                key_findings=forensic_response.key_findings,
                tribunal_probability=0.5,  # Neutral fallback
                financial_exposure_summary=f"Enhancement unavailable - forensic risk: {forensic_response.risk_assessment}",
                claim_strength_summary="Enhancement unavailable - manual assessment required",
                immediate_actions=forensic_response.recommended_actions,
                settlement_recommendation="Enhancement unavailable",
                evidence_gaps=[],
                confidence_overall=forensic_response.confidence_overall,
                enhancement_applied=False
            )

    def _summarize_evidence_chunk(
        self,
        chunk: List[EvidenceSummary],
        chunk_index: int,
        total_chunks: int
    ) -> ChunkSummaryResponse:
        """Summarize a chunk of evidence using AI.

        Args:
            chunk: List of EvidenceSummary objects for this chunk
            chunk_index: Index of this chunk (0-based)
            total_chunks: Total number of chunks

        Returns:
            ChunkSummaryResponse with AI-generated chunk summary
        """
        # Build context for this chunk
        context_parts = []
        context_parts.append(f"EVIDENCE CHUNK {chunk_index + 1} of {total_chunks}")
        context_parts.append(f"Items in chunk: {len(chunk)}")
        context_parts.append("")

        for i, evidence in enumerate(chunk, 1):
            context_parts.append(f"{i}. {evidence.filename} ({evidence.evidence_type.upper()})")
            if evidence.analysis_confidence:
                context_parts.append(f"   Confidence: {evidence.analysis_confidence:.2f}")
            if evidence.legal_significance:
                context_parts.append(f"   Legal significance: {evidence.legal_significance}")
            if evidence.risk_flags:
                context_parts.append(f"   Risk flags: {', '.join(evidence.risk_flags)}")
            context_parts.append("   Findings:")
            for finding in evidence.key_findings[:3]:  # Limit to top 3 findings per evidence
                context_parts.append(f"   • {finding}")
            context_parts.append("")

        chunk_context = "\n".join(context_parts)

        # Chunk summary prompt
        chunk_prompt = """You are analyzing a subset of evidence from a legal case. Your task is to:
1. Summarize the key themes and patterns in this chunk of evidence
2. Identify the most important entities (people, organizations)
3. Extract the 3-5 most legally significant findings
4. Note any risk flags or concerns
5. Provide a confidence score for your analysis

Be concise but thorough. Focus on legally significant information."""

        # Call OpenAI
        response = self.openai_client.responses.parse(
            model="gpt-4o-2024-08-06",
            input=[
                {"role": "system", "content": chunk_prompt},
                {"role": "user", "content": chunk_context}
            ],
            text_format=ChunkSummaryResponse
        )

        if response.status == "completed" and response.output_parsed:
            return response.output_parsed
        else:
            raise Exception(f"Chunk summary failed: {response.status}")

    def _build_case_context_for_ai(self, case_summary: CaseSummary) -> str:
        """Build comprehensive case context for AI analysis.

        Uses map-reduce pattern for large cases to avoid context length issues.

        Args:
            case_summary: CaseSummary object

        Returns:
            Formatted case context string for AI processing
        """
        # v3.2: Chunked summarization for large cases
        CHUNK_SIZE = 30  # Evidence items per chunk
        MAX_DIRECT_EVIDENCE = 50  # If fewer items, use direct approach

        if case_summary.evidence_count <= MAX_DIRECT_EVIDENCE:
            # Small case - use original direct approach
            return self._build_direct_case_context(case_summary)
        else:
            # Large case - use map-reduce chunking
            return self._build_chunked_case_context(case_summary, CHUNK_SIZE)

    def _build_direct_case_context(self, case_summary: CaseSummary) -> str:
        """Build direct case context for small cases (legacy method).

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

        # Entity correlations (top 20)
        if case_summary.correlation_result.entity_correlations:
            context_parts.append("ENTITY CORRELATIONS (Top 20):")
            for corr in case_summary.correlation_result.entity_correlations[:20]:
                context_parts.append(f"- {corr.entity_name} ({corr.entity_type}): {corr.occurrence_count} occurrences, confidence {corr.confidence_average:.2f}")
            context_parts.append("")

        # Timeline (last 10 events)
        if case_summary.correlation_result.timeline_events:
            context_parts.append("TIMELINE EVENTS (Last 10):")
            for event in case_summary.correlation_result.timeline_events[-10:]:
                context_parts.append(f"- {event.timestamp.strftime('%Y-%m-%d %H:%M')}: {event.description}")
            context_parts.append("")

        # v3.2 FIX: Include power dynamics in AI context (workplace/employment cases)
        assessment = case_summary.overall_assessment
        if 'power_dynamics' in assessment:
            pd = assessment['power_dynamics']
            context_parts.append(f"POWER DYNAMICS (Top 5 participants):")
            for p in pd['top_participants'][:5]:
                deference_label = 'dominant' if p['avg_deference'] < 0.4 else 'deferential' if p['avg_deference'] > 0.6 else 'neutral'
                context_parts.append(f"  • {p['participant']} ({p['authority']}): {p['messages']} messages, {deference_label} ({p['avg_deference']})")
                if p['top_topics']:
                    context_parts.append(f"    Topics: {', '.join(p['top_topics'])}")
            context_parts.append("")

        # v3.3: Include quoted statements from documents
        if 'quoted_statements' in assessment:
            qs = assessment['quoted_statements']
            context_parts.append("QUOTED STATEMENTS FROM DOCUMENTS:")
            context_parts.append(f"  Total: {qs['total_statements']} statements from {qs['people_quoted']} people across {qs['documents_with_quotes']} documents")
            for person_data in qs['quoted_statements'][:5]:  # Top 5 most quoted
                context_parts.append(f"  • {person_data['person']} ({person_data['role']}): {person_data['statement_count']} statements [{person_data['dominant_sentiment']}]")
                for stmt in person_data['statements'][:2]:  # First 2 quotes per person
                    risk_indicator = f" [RISK: {', '.join(stmt['risk_flags'][:2])}]" if stmt['risk_flags'] else ""
                    context_parts.append(f"    - \"{stmt['text'][:100]}...\"{risk_indicator}")
            context_parts.append("")

        # v3.3: Include communication pattern analysis
        if 'communication_patterns' in assessment:
            cp = assessment['communication_patterns']
            context_parts.append("EMAIL COMMUNICATION PATTERNS:")
            context_parts.append(f"  Emails analyzed: {cp['email_count']}")
            context_parts.append(f"  Dominant pattern: {cp['dominant_pattern'].upper()} (risk: {cp['risk_level']})")
            context_parts.append(f"  Distribution: Professional={cp['professional_count']}, Escalating={cp['escalating_count']}, Hostile/Retaliatory={cp['hostile_or_retaliatory_count']}")
            context_parts.append("")

        # v3.3 Phase B: Include image OCR text
        if 'image_ocr' in assessment:
            ocr = assessment['image_ocr']
            context_parts.append("IMAGE OCR TEXT DETECTED:")
            context_parts.append(f"  Images with text: {ocr['total_images_with_text']} ({ocr['text_extraction_rate']:.0%} of images)")
            context_parts.append(f"  High evidence value: {ocr['high_evidence_value_count']}, Medium: {ocr['medium_evidence_value_count']}")
            if ocr['people_present_count'] > 0:
                context_parts.append(f"  Images with people: {ocr['people_present_count']}")
            if ocr['timestamps_visible_count'] > 0:
                context_parts.append(f"  Images with timestamps: {ocr['timestamps_visible_count']}")
            context_parts.append("  Sample OCR extractions:")
            for img in ocr['images_with_text'][:5]:  # Top 5
                context_parts.append(f"    • {img['filename']}: \"{img['detected_text'][:60]}...\" [{img['evidence_value']}]")
            context_parts.append("")

        # v3.3 Phase B: Include relationship network
        if 'relationship_network' in assessment:
            rn = assessment['relationship_network']
            context_parts.append("RELATIONSHIP NETWORK:")
            context_parts.append(f"  Total connections: {rn['total_relationships']}")
            context_parts.append(f"  Distribution: Email={rn['relationship_type_distribution']['email_communication']}, Escalation={rn['relationship_type_distribution']['escalation']}")
            context_parts.append("  Key players by connection count:")
            for player in rn['key_players'][:5]:  # Top 5
                context_parts.append(f"    • {player['name']} ({player['connection_count']} connections): {player['role']}")
            context_parts.append("")

        # v3.2 FIX: Include legal patterns in AI context for richer executive summaries
        if case_summary.correlation_result.legal_patterns:
            lp = case_summary.correlation_result.legal_patterns
            context_parts.append("LEGAL PATTERN ANALYSIS:")

            if lp.contradictions:
                context_parts.append(f"  Contradictions detected: {len(lp.contradictions)}")
                for c in lp.contradictions[:3]:  # Top 3 most severe
                    context_parts.append(f"    • {c.contradiction_type.upper()}: {c.statement_1[:80]}... vs {c.statement_2[:80]}... (severity: {c.severity})")

            if lp.corroboration:
                context_parts.append(f"  Corroboration links: {len(lp.corroboration)}")
                for corr in lp.corroboration[:5]:  # Top 5
                    context_parts.append(f"    • {corr.corroboration_strength.upper()}: {corr.claim[:100]}... ({len(corr.supporting_evidence)} pieces)")

            if lp.evidence_gaps:
                context_parts.append(f"  Evidence gaps identified: {len(lp.evidence_gaps)}")
                for gap in lp.evidence_gaps[:3]:  # Top 3 critical gaps
                    context_parts.append(f"    • {gap[:150]}...")

            context_parts.append(f"  Pattern analysis confidence: {lp.confidence:.2f}")
            context_parts.append("")

        return "\n".join(context_parts)

    def _build_chunked_case_context(self, case_summary: CaseSummary, chunk_size: int) -> str:
        """Build chunked case context for large cases using map-reduce.

        Args:
            case_summary: CaseSummary object
            chunk_size: Number of evidence items per chunk

        Returns:
            Formatted case context string combining chunk summaries
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

        # Chunk evidence and generate summaries
        evidence_chunks = [
            case_summary.evidence_summaries[i:i + chunk_size]
            for i in range(0, len(case_summary.evidence_summaries), chunk_size)
        ]
        total_chunks = len(evidence_chunks)

        print(f"   📊 Chunking {case_summary.evidence_count} evidence items into {total_chunks} chunks...")

        context_parts.append(f"EVIDENCE ANALYSIS (Chunked - {total_chunks} chunks):")
        for chunk_idx, chunk in enumerate(evidence_chunks):
            print(f"   🤖 Summarizing chunk {chunk_idx + 1}/{total_chunks}...")
            try:
                chunk_summary = self._summarize_evidence_chunk(chunk, chunk_idx, total_chunks)
                context_parts.append(f"\nChunk {chunk_idx + 1} ({len(chunk)} items):")
                context_parts.append(f"  Summary: {chunk_summary.chunk_summary}")
                context_parts.append(f"  Key entities: {', '.join(chunk_summary.key_entities)}")
                context_parts.append(f"  Key findings: {'; '.join(chunk_summary.key_findings)}")
                if chunk_summary.risk_flags:
                    context_parts.append(f"  Risk flags: {', '.join(chunk_summary.risk_flags)}")
                context_parts.append(f"  Confidence: {chunk_summary.confidence:.2f}")
            except Exception as e:
                print(f"   ⚠️  Chunk {chunk_idx + 1} summary failed: {e}")
                # Fallback: include first 3 evidence items from chunk
                context_parts.append(f"\nChunk {chunk_idx + 1} ({len(chunk)} items) - AI summary failed:")
                for evidence in chunk[:3]:
                    context_parts.append(f"  - {evidence.filename}: {evidence.key_findings[0] if evidence.key_findings else 'N/A'}")

        context_parts.append("")

        # Entity correlations (top 30 for large cases)
        if case_summary.correlation_result.entity_correlations:
            context_parts.append("ENTITY CORRELATIONS (Top 30):")
            for corr in case_summary.correlation_result.entity_correlations[:30]:
                context_parts.append(f"- {corr.entity_name} ({corr.entity_type}): {corr.occurrence_count} occurrences")
            context_parts.append("")

        # Timeline summary (first 5 and last 5 events)
        if case_summary.correlation_result.timeline_events:
            context_parts.append("TIMELINE SUMMARY:")
            context_parts.append("First 5 events:")
            for event in case_summary.correlation_result.timeline_events[:5]:
                context_parts.append(f"- {event.timestamp.strftime('%Y-%m-%d %H:%M')}: {event.description}")
            context_parts.append("Last 5 events:")
            for event in case_summary.correlation_result.timeline_events[-5:]:
                context_parts.append(f"- {event.timestamp.strftime('%Y-%m-%d %H:%M')}: {event.description}")
            context_parts.append("")

        # v3.2 FIX: Include power dynamics in AI context (workplace/employment cases - chunked version)
        assessment = case_summary.overall_assessment
        if 'power_dynamics' in assessment:
            pd = assessment['power_dynamics']
            context_parts.append(f"POWER DYNAMICS (Top 5 participants):")
            for p in pd['top_participants'][:5]:
                deference_label = 'dominant' if p['avg_deference'] < 0.4 else 'deferential' if p['avg_deference'] > 0.6 else 'neutral'
                context_parts.append(f"  • {p['participant']} ({p['authority']}): {p['messages']} messages, {deference_label} ({p['avg_deference']})")
                if p['top_topics']:
                    context_parts.append(f"    Topics: {', '.join(p['top_topics'])}")
            context_parts.append("")

        # v3.3: Include quoted statements (chunked version - space-saving)
        if 'quoted_statements' in assessment:
            qs = assessment['quoted_statements']
            context_parts.append(f"QUOTED STATEMENTS: {qs['total_statements']} from {qs['people_quoted']} people")
            for person_data in qs['quoted_statements'][:3]:  # Top 3 for chunked
                context_parts.append(f"  • {person_data['person']}: {person_data['statement_count']} statements [{person_data['dominant_sentiment']}]")
            context_parts.append("")

        # v3.3: Include communication patterns (chunked version)
        if 'communication_patterns' in assessment:
            cp = assessment['communication_patterns']
            context_parts.append(f"COMM PATTERNS: {cp['email_count']} emails, dominant={cp['dominant_pattern']} (risk:{cp['risk_level']})")
            context_parts.append("")

        # v3.3 Phase B: Include image OCR (chunked version - space-optimized)
        if 'image_ocr' in assessment:
            ocr = assessment['image_ocr']
            context_parts.append(f"IMAGE OCR: {ocr['total_images_with_text']} images with text ({ocr['text_extraction_rate']:.0%}), {ocr['high_evidence_value_count']} high-value")
            context_parts.append("")

        # v3.3 Phase B: Include relationship network (chunked version)
        if 'relationship_network' in assessment:
            rn = assessment['relationship_network']
            context_parts.append(f"RELATIONSHIPS: {rn['total_relationships']} connections, {len(rn['key_players'])} key players")
            context_parts.append("")

        # v3.2 FIX: Include legal patterns in AI context for richer executive summaries (chunked version)
        if case_summary.correlation_result.legal_patterns:
            lp = case_summary.correlation_result.legal_patterns
            context_parts.append("LEGAL PATTERN ANALYSIS:")

            if lp.contradictions:
                context_parts.append(f"  Contradictions detected: {len(lp.contradictions)}")
                for c in lp.contradictions[:3]:  # Top 3 most severe
                    context_parts.append(f"    • {c.contradiction_type.upper()}: {c.statement_1[:80]}... vs {c.statement_2[:80]}... (severity: {c.severity})")

            if lp.corroboration:
                context_parts.append(f"  Corroboration links: {len(lp.corroboration)}")
                for corr in lp.corroboration[:5]:  # Top 5
                    context_parts.append(f"    • {corr.corroboration_strength.upper()}: {corr.claim[:100]}... ({len(corr.supporting_evidence)} pieces)")

            if lp.evidence_gaps:
                context_parts.append(f"  Evidence gaps identified: {len(lp.evidence_gaps)}")
                for gap in lp.evidence_gaps[:3]:  # Top 3 critical gaps
                    context_parts.append(f"    • {gap[:150]}...")

            context_parts.append(f"  Pattern analysis confidence: {lp.confidence:.2f}")
            context_parts.append("")

        return "\n".join(context_parts)

    def _calculate_overall_assessment(
        self,
        evidence_summaries: List[EvidenceSummary],
        correlation_result: CorrelationAnalysis
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
        legal_significance_counts: Dict[str, int] = {}
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

        # v3.2 FIX: Extract power dynamics from email evidence
        power_dynamics_summary = self._extract_power_dynamics(evidence_summaries)

        # v3.3: Extract quoted statements from document evidence
        quoted_statements_summary = self._extract_quoted_statements(evidence_summaries)

        # v3.3: Analyze communication patterns from email evidence
        communication_patterns_summary = self._analyze_communication_patterns(evidence_summaries)

        # v3.3 Phase B: Extract image OCR text
        image_ocr_summary = self._extract_image_ocr_text(evidence_summaries)

        # v3.3 Phase B: Extract relationship network
        relationship_network = self._extract_relationship_network(evidence_summaries)

        result = {
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

        # Add power dynamics if available (workplace/employment cases)
        if power_dynamics_summary:
            result['power_dynamics'] = power_dynamics_summary

        # Add quoted statements if available (v3.3)
        if quoted_statements_summary:
            result['quoted_statements'] = quoted_statements_summary

        # Add communication patterns if available (v3.3)
        if communication_patterns_summary:
            result['communication_patterns'] = communication_patterns_summary

        # Add image OCR if available (v3.3 Phase B)
        if image_ocr_summary:
            result['image_ocr'] = image_ocr_summary

        # Add relationship network if available (v3.3 Phase B)
        if relationship_network:
            result['relationship_network'] = relationship_network

        return result

    def _extract_power_dynamics(self, evidence_summaries: List[EvidenceSummary]) -> Optional[Dict[str, Any]]:
        """Extract power dynamics insights from email evidence (v3.2 enhancement).

        Args:
            evidence_summaries: List of evidence summaries

        Returns:
            Power dynamics summary dict or None if no email evidence
        """
        participants_data = []

        # Find email analysis files and extract participant data
        for evidence in evidence_summaries:
            if evidence.evidence_type == 'email':
                analysis_file = self.storage.derived_dir / f"sha256={evidence.sha256}" / "analysis.v1.json"
                if analysis_file.exists():
                    try:
                        with open(analysis_file) as f:
                            analysis = json.load(f)
                            email_analysis = analysis.get('email_analysis', {})
                            participants = email_analysis.get('participants', [])
                            participants_data.extend(participants)
                    except (json.JSONDecodeError, FileNotFoundError):
                        continue

        if not participants_data:
            return None

        # Aggregate by participant email
        participant_stats = defaultdict(lambda: {
            'message_count': 0,
            'deference_scores': [],
            'authority_level': None,
            'topics': set(),
            'display_name': None
        })

        for p in participants_data:
            email = p.get('email_address', '').strip().lower()
            if not email:
                continue

            participant_stats[email]['message_count'] += p.get('message_count', 0)

            if p.get('deference_score') is not None:
                participant_stats[email]['deference_scores'].append(p['deference_score'])

            # Use highest authority level seen
            auth_level = p.get('authority_level')
            if auth_level:
                participant_stats[email]['authority_level'] = auth_level

            # Collect topics
            participant_stats[email]['topics'].update(p.get('dominant_topics', []))

            # Use display name if available
            if p.get('display_name'):
                participant_stats[email]['display_name'] = p['display_name']

        # Calculate averages and format for output
        summary = []
        for email, stats in sorted(participant_stats.items(), key=lambda x: -x[1]['message_count'])[:10]:
            avg_deference = (
                sum(stats['deference_scores']) / len(stats['deference_scores'])
                if stats['deference_scores'] else 0.5
            )

            display_name = stats['display_name'] or email.split('@')[0]

            summary.append({
                'participant': display_name,
                'email': email,
                'authority': stats['authority_level'] or 'unknown',
                'messages': stats['message_count'],
                'avg_deference': round(avg_deference, 2),
                'top_topics': list(stats['topics'])[:3]
            })

        return {
            'top_participants': summary,
            'participant_count': len(participant_stats),
            'total_messages_analyzed': sum(s['messages'] for s in summary)
        }

    def _analyze_communication_patterns(self, evidence_summaries: List[EvidenceSummary]) -> Optional[Dict[str, Any]]:
        """Analyze email communication patterns (v3.3 enhancement).

        Aggregates existing EmailThreadAnalysis.communication_pattern fields across all emails.
        NO new AI calls required - reuses captured data.

        Args:
            evidence_summaries: List of evidence summaries

        Returns:
            Communication pattern analysis dict or None if no email evidence
        """
        from collections import Counter

        patterns = []
        pattern_by_evidence = []

        # Extract communication patterns from email analyses
        for evidence in evidence_summaries:
            if evidence.evidence_type == 'email':
                analysis_file = self.storage.derived_dir / f"sha256={evidence.sha256}" / "analysis.v1.json"
                if analysis_file.exists():
                    try:
                        with open(analysis_file) as f:
                            analysis = json.load(f)
                            email_analysis = analysis.get('email_analysis', {})

                            if not email_analysis:
                                continue

                            # Get communication pattern
                            pattern = email_analysis.get('communication_pattern')
                            if pattern:
                                patterns.append(pattern)
                                pattern_by_evidence.append({
                                    'sha256': evidence.sha256,
                                    'filename': analysis.get('file_metadata', {}).get('filename', 'unknown'),
                                    'pattern': pattern,
                                    'risk_flags': email_analysis.get('risk_flags', [])
                                })

                    except (json.JSONDecodeError, FileNotFoundError, KeyError):
                        continue

        if not patterns:
            return None

        # Aggregate patterns
        pattern_counts = Counter(patterns)
        dominant_pattern = pattern_counts.most_common(1)[0][0]

        # Determine risk level based on patterns
        hostile_count = pattern_counts.get('hostile', 0) + pattern_counts.get('retaliatory', 0)
        escalating_count = pattern_counts.get('escalating', 0)

        if hostile_count > 0 or pattern_counts.get('retaliatory', 0) > 0:
            risk_level = 'high'
        elif escalating_count > 0:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'email_count': len(patterns),
            'pattern_distribution': dict(pattern_counts),
            'dominant_pattern': dominant_pattern,
            'risk_level': risk_level,
            'hostile_or_retaliatory_count': hostile_count,
            'escalating_count': escalating_count,
            'professional_count': pattern_counts.get('professional', 0),
            'pattern_details': pattern_by_evidence
        }

    def _extract_quoted_statements(self, evidence_summaries: List[EvidenceSummary]) -> Optional[Dict[str, Any]]:
        """Extract and aggregate quoted statements from document analyses (v3.3 enhancement).

        Aggregates existing v3.1 DocumentEntity.quoted_text fields by person, along with
        document-level sentiment and risk flags. NO new AI calls required - reuses captured data.

        Args:
            evidence_summaries: List of evidence summaries

        Returns:
            Quoted statements summary dict or None if no quoted statements found
        """
        from collections import Counter

        statements_by_person = defaultdict(lambda: {
            'statements': [],
            'sentiments': [],
            'risk_flags': set(),
            'role': None
        })

        # Find document analysis files and extract quoted statements
        for evidence in evidence_summaries:
            if evidence.evidence_type == 'document':
                analysis_file = self.storage.derived_dir / f"sha256={evidence.sha256}" / "analysis.v1.json"
                if analysis_file.exists():
                    try:
                        with open(analysis_file) as f:
                            analysis = json.load(f)
                            doc_analysis = analysis.get('document_analysis', {})

                            if not doc_analysis:
                                continue

                            # Get document-level metadata
                            doc_sentiment = doc_analysis.get('sentiment', 'neutral')
                            doc_risk_flags = doc_analysis.get('risk_flags', [])
                            doc_filename = analysis.get('file_metadata', {}).get('filename', 'unknown')

                            # Extract quoted statements from entities
                            for entity in doc_analysis.get('entities', []):
                                if entity.get('type') == 'person' and entity.get('quoted_text'):
                                    person_name = entity['name']

                                    statements_by_person[person_name]['statements'].append({
                                        'text': entity['quoted_text'],
                                        'source_sha256': evidence.sha256,
                                        'source_file': doc_filename,
                                        'document_sentiment': doc_sentiment,
                                        'risk_flags': doc_risk_flags,
                                        'context': entity.get('context', '')[:100]
                                    })

                                    statements_by_person[person_name]['sentiments'].append(doc_sentiment)
                                    statements_by_person[person_name]['risk_flags'].update(doc_risk_flags)

                                    # Store role from relationship field if available
                                    if entity.get('relationship') and not statements_by_person[person_name]['role']:
                                        statements_by_person[person_name]['role'] = entity['relationship']

                    except (json.JSONDecodeError, FileNotFoundError, KeyError):
                        continue

        if not statements_by_person:
            return None

        # Aggregate by person with sentiment analysis
        summary = []
        for person, data in statements_by_person.items():
            # Calculate dominant sentiment (most common)
            sentiment_counts = Counter(data['sentiments'])
            dominant_sentiment = sentiment_counts.most_common(1)[0][0] if sentiment_counts else 'neutral'

            summary.append({
                'person': person,
                'role': data['role'] or 'unknown',
                'statement_count': len(data['statements']),
                'statements': data['statements'],
                'dominant_sentiment': dominant_sentiment,
                'sentiment_distribution': dict(sentiment_counts),
                'has_risk_indicators': len(data['risk_flags']) > 0,
                'risk_types': list(data['risk_flags'])
            })

        # Sort by statement count (most quoted people first)
        summary.sort(key=lambda x: -x['statement_count'])

        return {
            'quoted_statements': summary,
            'total_statements': sum(p['statement_count'] for p in summary),
            'people_quoted': len(summary),
            'documents_with_quotes': len(set(
                stmt['source_sha256']
                for person_data in statements_by_person.values()
                for stmt in person_data['statements']
            ))
        }

    def _extract_image_ocr_text(self, evidence_summaries: List[EvidenceSummary]) -> Optional[Dict[str, Any]]:
        """Extract and aggregate OCR text from image analyses (v3.3 Phase B).

        Aggregates ImageAnalysisStructured.detected_text across all images,
        grouping by detected_objects and potential_evidence_value.

        Args:
            evidence_summaries: List of evidence summaries

        Returns:
            Image OCR summary dict or None if no images with text
        """
        images_with_text = []
        object_categories = defaultdict(list)

        for evidence in evidence_summaries:
            if evidence.evidence_type == 'image':
                analysis_file = self.storage.derived_dir / f"sha256={evidence.sha256}" / "analysis.v1.json"
                if analysis_file.exists():
                    try:
                        with open(analysis_file) as f:
                            analysis = json.load(f)
                            img_analysis = analysis.get('image_analysis', {})
                            img_parsed = img_analysis.get('openai_response', {}).get('parsed', {})

                            detected_text = img_parsed.get('detected_text')
                            if detected_text:
                                images_with_text.append({
                                    'sha256': evidence.sha256,
                                    'filename': analysis.get('file_metadata', {}).get('filename', 'unknown'),
                                    'detected_text': detected_text,
                                    'scene_description': img_parsed.get('scene_description', '')[:100],
                                    'detected_objects': img_parsed.get('detected_objects', []),
                                    'evidence_value': img_parsed.get('potential_evidence_value', 'low'),
                                    'people_present': img_parsed.get('people_present', False),
                                    'timestamps_visible': img_parsed.get('timestamps_visible', False)
                                })

                                # Group by object categories for analysis
                                for obj in img_parsed.get('detected_objects', []):
                                    object_categories[obj].append(detected_text)

                    except (json.JSONDecodeError, FileNotFoundError, KeyError):
                        continue

        if not images_with_text:
            return None

        # Calculate statistics
        high_value_count = sum(1 for img in images_with_text if img['evidence_value'] == 'high')
        medium_value_count = sum(1 for img in images_with_text if img['evidence_value'] == 'medium')
        people_present_count = sum(1 for img in images_with_text if img['people_present'])
        timestamp_count = sum(1 for img in images_with_text if img['timestamps_visible'])

        # Calculate extraction rate
        total_images = len([e for e in evidence_summaries if e.evidence_type == 'image'])
        extraction_rate = len(images_with_text) / total_images if total_images > 0 else 0

        return {
            'images_with_text': images_with_text[:20],  # Top 20 for space
            'total_images_with_text': len(images_with_text),
            'text_extraction_rate': extraction_rate,
            'high_evidence_value_count': high_value_count,
            'medium_evidence_value_count': medium_value_count,
            'people_present_count': people_present_count,
            'timestamps_visible_count': timestamp_count,
            'object_categories': {k: len(v) for k, v in sorted(object_categories.items(), key=lambda x: -len(x[1]))[:10]}
        }

    def _extract_relationship_network(self, evidence_summaries: List[EvidenceSummary]) -> Optional[Dict[str, Any]]:
        """Extract relationship network from entity relationships (v3.3 Phase B).

        Parses DocumentEntity.relationship fields to build a network graph showing
        who communicated with whom, who escalated to whom, and organizational structure.

        Args:
            evidence_summaries: List of evidence summaries

        Returns:
            Relationship network dict or None if no relationships found
        """
        import re

        relationships = []
        entity_roles = {}

        # Relationship parsing patterns
        email_patterns = [
            r'sent email to (.+)',
            r'email to (.+)',
            r'email from (.+)',
            r'replied to (.+)',
            r"cc['\u2019]?d? (.+)"
        ]

        escalation_patterns = [
            r'reported to (.+)',
            r'escalated to (.+)',
            r'complained to (.+)',
            r'raised concern with (.+)'
        ]

        for evidence in evidence_summaries:
            if evidence.evidence_type == 'document':
                analysis_file = self.storage.derived_dir / f"sha256={evidence.sha256}" / "analysis.v1.json"
                if analysis_file.exists():
                    try:
                        with open(analysis_file) as f:
                            analysis = json.load(f)
                            doc_analysis = analysis.get('document_analysis', {})

                            if not doc_analysis:
                                continue

                            for entity in doc_analysis.get('entities', []):
                                entity_name = entity.get('name')
                                relationship = entity.get('relationship', '')

                                if not entity_name or not relationship:
                                    continue

                                # Store role information
                                if entity_name not in entity_roles:
                                    entity_roles[entity_name] = relationship

                                # Parse relationship for network edges
                                relationship_type = 'other'
                                target = None

                                # Check email patterns
                                for pattern in email_patterns:
                                    match = re.search(pattern, relationship, re.IGNORECASE)
                                    if match:
                                        target = match.group(1).strip()
                                        relationship_type = 'email_communication'
                                        break

                                # Check escalation patterns
                                if not target:
                                    for pattern in escalation_patterns:
                                        match = re.search(pattern, relationship, re.IGNORECASE)
                                        if match:
                                            target = match.group(1).strip()
                                            relationship_type = 'escalation'
                                            break

                                # If we found a target, create relationship edge
                                if target:
                                    relationships.append({
                                        'source': entity_name,
                                        'target': target,
                                        'relationship_type': relationship_type,
                                        'evidence_sha256': evidence.sha256,
                                        'context': relationship
                                    })

                    except (json.JSONDecodeError, FileNotFoundError, KeyError):
                        continue

        if not relationships:
            return None

        # Aggregate relationships by source-target pairs
        relationship_counts = defaultdict(int)
        for rel in relationships:
            key = (rel['source'], rel['target'], rel['relationship_type'])
            relationship_counts[key] += 1

        # Identify key players (most connected entities)
        entity_connections = defaultdict(int)
        for rel in relationships:
            entity_connections[rel['source']] += 1
            entity_connections[rel['target']] += 1

        key_players = sorted(entity_connections.items(), key=lambda x: -x[1])[:10]

        return {
            'relationships': relationships[:50],  # Top 50 for space
            'total_relationships': len(relationships),
            'unique_connections': len(relationship_counts),
            'key_players': [
                {
                    'name': name,
                    'connection_count': count,
                    'role': entity_roles.get(name, 'unknown')
                }
                for name, count in key_players
            ],
            'relationship_type_distribution': {
                'email_communication': sum(1 for r in relationships if r['relationship_type'] == 'email_communication'),
                'escalation': sum(1 for r in relationships if r['relationship_type'] == 'escalation'),
                'other': sum(1 for r in relationships if r['relationship_type'] == 'other')
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
            # v3.2 FIX: Use Pydantic serialization to preserve ALL fields
            # This ensures legal_patterns, temporal_sequences, timeline_gaps are included
            summary_dict = case_summary.model_dump(mode='json')

            # Convert datetime objects to ISO format strings
            if isinstance(summary_dict.get('generation_timestamp'), str):
                pass  # Already serialized
            else:
                summary_dict['generation_timestamp'] = case_summary.generation_timestamp.isoformat()

            # Ensure correlation_result is fully serialized
            if case_summary.correlation_result:
                summary_dict['correlation_analysis'] = case_summary.correlation_result.model_dump(mode='json')
                # Remove the raw correlation_result field (we renamed it to correlation_analysis for clarity)
                if 'correlation_result' in summary_dict:
                    del summary_dict['correlation_result']

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

        # v3.3 Phase B+: Forensic Summary (detailed narrative analysis)
        forensic_summary = case_summary.overall_assessment.get('forensic_summary')
        if forensic_summary:
            lines.append("🔍 FORENSIC SUMMARY")
            lines.append("-" * 30)
            lines.append(forensic_summary)
            lines.append("")

        # v3.3 Phase B+: AI Key Findings (bullet-point discoveries)
        ai_key_findings = case_summary.overall_assessment.get('ai_key_findings')
        if ai_key_findings:
            lines.append("💡 KEY FINDINGS")
            lines.append("-" * 30)
            for i, finding in enumerate(ai_key_findings, 1):
                lines.append(f"{i}. {finding}")
            lines.append("")

        # v3.3 Phase B+: Forensic Legal Implications (specific risk areas)
        forensic_legal_impl = case_summary.overall_assessment.get('forensic_legal_implications')
        if forensic_legal_impl:
            lines.append("⚖️  LEGAL IMPLICATIONS")
            lines.append("-" * 30)
            for i, impl in enumerate(forensic_legal_impl, 1):
                lines.append(f"{i}. {impl}")
            lines.append("")

        # v3.2: Enhanced Risk Assessment (if enhancement was applied)
        if case_summary.overall_assessment.get('enhancement_applied'):
            lines.append("⚖️  LEGAL RISK ASSESSMENT")
            lines.append("-" * 30)

            # Tribunal probability
            tribunal_prob = case_summary.overall_assessment.get('tribunal_probability', 0)
            lines.append(f"Tribunal success probability: {tribunal_prob:.0%}")

            # Financial exposure
            financial = case_summary.overall_assessment.get('financial_exposure', {})
            if financial and 'total_range' in financial:
                lines.append(f"Estimated financial exposure: {financial.get('total_range', 'Not assessed')}")
                if 'basic_award' in financial:
                    lines.append(f"  - Basic award: {financial.get('basic_award', 'N/A')}")
                if 'compensatory' in financial:
                    lines.append(f"  - Compensatory: {financial.get('compensatory', 'N/A')}")
                if 'injury_to_feelings' in financial:
                    lines.append(f"  - Injury to feelings: {financial.get('injury_to_feelings', 'N/A')}")

            # Claim strength
            claim_strength = case_summary.overall_assessment.get('claim_strength', {})
            if claim_strength:
                lines.append("")
                lines.append("Claim strength breakdown:")
                for claim_type, strength in claim_strength.items():
                    if claim_type != 'note':  # Skip fallback notes
                        lines.append(f"  • {claim_type}: {strength}")

            # Immediate actions
            immediate_actions = case_summary.overall_assessment.get('immediate_actions', [])
            if immediate_actions:
                lines.append("")
                lines.append("Recommended immediate actions:")
                for action in immediate_actions:
                    lines.append(f"  • {action}")

            # Settlement range
            settlement = case_summary.overall_assessment.get('settlement_range', {})
            if settlement and 'min' in settlement and settlement['min'] > 0:
                lines.append("")
                lines.append(f"Settlement recommendation: £{settlement['min']:,} - £{settlement['max']:,}")

            lines.append("")

        # v3.3: Quoted Statements Section
        if 'quoted_statements' in case_summary.overall_assessment:
            qs = case_summary.overall_assessment['quoted_statements']
            lines.append("💬 QUOTED STATEMENTS")
            lines.append("-" * 30)
            lines.append(f"Total statements captured: {qs['total_statements']} from {qs['people_quoted']} people across {qs['documents_with_quotes']} documents")
            lines.append("")
            for person_data in qs['quoted_statements'][:5]:  # Top 5
                lines.append(f"• {person_data['person']} ({person_data['role']})")
                lines.append(f"  {person_data['statement_count']} statement(s) - Sentiment: {person_data['dominant_sentiment']}")
                if person_data['has_risk_indicators']:
                    lines.append(f"  Risk indicators: {', '.join(person_data['risk_types'][:3])}")
                for stmt in person_data['statements'][:2]:  # First 2 quotes per person
                    risk_str = f" [RISK: {', '.join(stmt['risk_flags'][:2])}]" if stmt['risk_flags'] else ""
                    lines.append(f"  → \"{stmt['text'][:120]}...\"{risk_str}")
                lines.append("")

        # v3.3: Communication Patterns Section
        if 'communication_patterns' in case_summary.overall_assessment:
            cp = case_summary.overall_assessment['communication_patterns']
            lines.append("📧 EMAIL COMMUNICATION PATTERNS")
            lines.append("-" * 30)
            lines.append(f"Emails analyzed: {cp['email_count']}")
            lines.append(f"Dominant pattern: {cp['dominant_pattern'].upper()}")
            lines.append(f"Risk level: {cp['risk_level'].upper()}")
            lines.append("")
            lines.append("Pattern distribution:")
            lines.append(f"  • Professional: {cp['professional_count']} emails")
            lines.append(f"  • Escalating: {cp['escalating_count']} emails")
            lines.append(f"  • Hostile/Retaliatory: {cp['hostile_or_retaliatory_count']} emails")
            lines.append("")

        # v3.3 Phase B: Relationship Network Section
        if 'relationship_network' in case_summary.overall_assessment:
            rn = case_summary.overall_assessment['relationship_network']
            lines.append("🔗 RELATIONSHIP NETWORK")
            lines.append("-" * 30)
            lines.append(f"Total connections identified: {rn['total_relationships']}")
            lines.append(f"Unique connection pairs: {rn['unique_connections']}")
            lines.append("")
            lines.append("Connection type distribution:")
            lines.append(f"  • Email communication: {rn['relationship_type_distribution']['email_communication']}")
            lines.append(f"  • Escalation: {rn['relationship_type_distribution']['escalation']}")
            lines.append(f"  • Other relationships: {rn['relationship_type_distribution']['other']}")
            lines.append("")
            lines.append("Key players by connection count:")
            for player in rn['key_players'][:8]:  # Top 8
                lines.append(f"  • {player['name']} - {player['connection_count']} connection(s)")
                if player['role'] and player['role'] != 'unknown':
                    lines.append(f"    Role: {player['role']}")
            lines.append("")

        # v3.3 Phase B: Image OCR Section (if applicable)
        if 'image_ocr' in case_summary.overall_assessment:
            ocr = case_summary.overall_assessment['image_ocr']
            lines.append("🖼️  IMAGE OCR ANALYSIS")
            lines.append("-" * 30)
            lines.append(f"Images with detected text: {ocr['total_images_with_text']} ({ocr['text_extraction_rate']:.0%} of all images)")
            lines.append(f"Evidence value: {ocr['high_evidence_value_count']} high, {ocr['medium_evidence_value_count']} medium")
            if ocr['people_present_count'] > 0:
                lines.append(f"Images with people visible: {ocr['people_present_count']}")
            if ocr['timestamps_visible_count'] > 0:
                lines.append(f"Images with timestamps: {ocr['timestamps_visible_count']}")
            lines.append("")
            if ocr['images_with_text']:
                lines.append("Sample OCR extractions:")
                for img in ocr['images_with_text'][:3]:  # Top 3
                    lines.append(f"  • {img['filename']} [{img['evidence_value']}]")
                    lines.append(f"    \"{img['detected_text'][:80]}...\"")
                lines.append("")

        # v3.3 Phase B+: Forensic Recommended Actions (strategic guidance)
        forensic_actions = case_summary.overall_assessment.get('forensic_recommended_actions')
        if forensic_actions:
            lines.append("🎯 RECOMMENDED ACTIONS")
            lines.append("-" * 30)
            for i, action in enumerate(forensic_actions, 1):
                lines.append(f"{i}. {action}")
            lines.append("")

        # Original risk flags (still useful)
        if case_summary.overall_assessment['total_risk_flags'] > 0:
            lines.append("⚠️  RISK FLAGS IDENTIFIED")
            lines.append("-" * 30)
            lines.append(f"Total risk flags: {case_summary.overall_assessment['total_risk_flags']}")
            lines.append(f"Unique risk types: {case_summary.overall_assessment['unique_risk_flags']}")
            lines.append("")

        # APPENDIX: Evidence details moved to end for reference
        lines.append("=" * 60)
        lines.append("APPENDIX: SUPPORTING DOCUMENTATION")
        lines.append("=" * 60)
        lines.append("The following sections contain detailed information about each piece")
        lines.append("of evidence, entity correlations, and timeline reconstruction.")
        lines.append("This serves as supporting documentation for the analysis above.")
        lines.append("")

        # Evidence Details (moved to appendix)
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

        # Correlations (moved to appendix)
        if case_summary.correlation_result.entity_correlations:
            lines.append("🔗 ENTITY CORRELATIONS")
            lines.append("-" * 30)
            for corr in case_summary.correlation_result.entity_correlations:
                lines.append(f"• {corr.entity_name} ({corr.entity_type})")
                lines.append(f"  Appears in {corr.occurrence_count} evidence pieces")
                lines.append(f"  Average confidence: {corr.confidence_average:.2f}")
            lines.append("")

        # Timeline (moved to appendix)
        if case_summary.correlation_result.timeline_events:
            lines.append("⏰ TIMELINE")
            lines.append("-" * 30)
            for event in case_summary.correlation_result.timeline_events[:10]:  # Show first 10
                lines.append(f"{event.timestamp.strftime('%Y-%m-%d %H:%M')} - {event.description}")
            lines.append("")

        return "\n".join(lines)


__all__ = [
    'ExecutiveSummaryResponse',
    'EnhancedExecutiveSummary',  # v3.2: Client-ready enhanced summary
    'ChunkSummaryResponse',
    'EvidenceSummary',
    'CaseSummary',
    'SummaryGenerator',
]
