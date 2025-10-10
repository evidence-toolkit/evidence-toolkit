"""Legal Patterns Detailed Generator - v3.4 Phase 2

Generates comprehensive legal pattern analysis report from AI-detected patterns
in the correlation analysis. Expands contradictions, corroboration, and evidence
gaps into a detailed forensic report suitable for legal review.

Data Sources:
- correlation_analysis.legal_patterns (dict with 4 keys)
  - contradictions: list[dict] - Conflicting statements across evidence
  - corroboration: list[dict] - Claims supported by multiple evidence pieces
  - evidence_gaps: list[str] - Missing documentation or witnesses
  - pattern_summary: str - Overall pattern assessment
  - confidence: float - AI confidence in pattern detection

This generator provides deeper analysis than the basic executive summary by:
1. Categorizing contradictions by type (factual, temporal, attribution)
2. Assessing corroboration strength (weak/moderate/strong)
3. Prioritizing evidence gaps by legal significance
4. Cross-referencing all findings with specific evidence items

Cost: ZERO new AI calls - uses existing correlation analysis
Value: Transforms generic patterns → actionable legal findings
Effort: ~6 hours implementation
"""

from pathlib import Path
from typing import Dict, List, Optional

from evidence_toolkit.generators.base import BaseReportGenerator
from evidence_toolkit.core.models import LegalPatternAnalysis


class LegalPatternsGenerator(BaseReportGenerator):
    """Generate detailed legal patterns analysis report.

    Expands the correlation_analysis.legal_patterns data into a comprehensive
    report suitable for legal review, with evidence citations and strategic
    recommendations.

    Data Sources:
        - correlation_analysis.legal_patterns.contradictions
        - correlation_analysis.legal_patterns.corroboration
        - correlation_analysis.legal_patterns.evidence_gaps
        - correlation_analysis.legal_patterns.pattern_summary
        - correlation_analysis.legal_patterns.confidence

    Output: legal_patterns_analysis.md (professional Markdown report)

    Example:
        >>> generator = LegalPatternsGenerator(case_summary, reports_dir)
        >>> if generator.has_data():
        ...     report_path = generator.generate()
        ...     # Creates: reports/legal_patterns_analysis.md
    """

    def get_report_filename(self) -> str:
        """Return filename for legal patterns report."""
        return "legal_patterns_analysis.md"

    def get_report_title(self) -> str:
        """Return human-readable report title."""
        return "Legal Patterns Analysis"

    def has_data(self) -> bool:
        """Check if legal patterns data exists.

        Report is generated if ANY pattern data exists (contradictions,
        corroboration, or evidence gaps).

        Returns:
            True if pattern data available
        """
        legal_patterns = self._get_legal_patterns()

        if not legal_patterns:
            return False

        contradictions = legal_patterns.contradictions
        corroboration = legal_patterns.corroboration
        evidence_gaps = legal_patterns.evidence_gaps

        # Return True if ANY pattern data exists
        return bool(contradictions or corroboration or evidence_gaps)

    def generate(self) -> Path:
        """Generate the legal patterns analysis report.

        Creates a comprehensive legal patterns report with contradictions,
        corroboration analysis, and evidence gaps prioritization.

        Returns:
            Path to generated report file

        Raises:
            Exception: If report generation fails
        """
        # Build report content
        content = self._build_header(subtitle="Cross-Evidence Pattern Detection & Analysis")

        # Add executive summary
        content += self._build_executive_summary()

        # Section 1: Contradictions Analysis
        content += self._build_contradictions_section()

        # Section 2: Corroboration Analysis
        content += self._build_corroboration_section()

        # Section 3: Evidence Gaps
        content += self._build_evidence_gaps_section()

        # Section 4: Pattern Summary
        content += self._build_pattern_summary_section()

        # Section 5: Strategic Implications
        content += self._build_strategic_implications_section()

        # Section 6: Methodology
        content += self._build_methodology_section()

        # Write report to file
        report_path = self.output_dir / self.get_report_filename()
        report_path.write_text(content, encoding='utf-8')

        return report_path

    # =========================================================================
    # SECTION BUILDERS
    # =========================================================================

    def _build_executive_summary(self) -> str:
        """Build executive summary of legal patterns."""
        legal_patterns = self._get_legal_patterns()

        if not legal_patterns:
            return ""

        contradictions = legal_patterns.contradictions
        corroboration = legal_patterns.corroboration
        evidence_gaps = legal_patterns.evidence_gaps
        confidence = legal_patterns.confidence

        content = "## Executive Summary\n\n"

        content += f"**Pattern Detection Confidence**: {self._format_percentage(confidence, decimals=0)}\n\n"

        content += "### Pattern Overview\n\n"
        content += f"- **Contradictions Detected**: {len(contradictions)}\n"
        content += f"- **Corroboration Links**: {len(corroboration)}\n"
        content += f"- **Evidence Gaps Identified**: {len(evidence_gaps)}\n\n"

        # Add risk assessment
        if contradictions:
            content += "⚠️ **HIGH PRIORITY**: Contradictions detected - requires immediate investigation\n\n"
        elif len(evidence_gaps) > 3:
            content += "⚠️ **MODERATE PRIORITY**: Multiple evidence gaps may weaken defense position\n\n"
        else:
            content += "✓ **LOWER RISK**: Limited contradictions, corroboration supporting key claims\n\n"

        content += "---\n\n"
        return content

    def _build_contradictions_section(self) -> str:
        """Build contradictions analysis section."""
        legal_patterns = self._get_legal_patterns()

        if not legal_patterns:
            return ""

        contradictions = legal_patterns.contradictions

        if not contradictions:
            content = "## 1. Contradictions Analysis\n\n"
            content += "✓ **No contradictions detected** across evidence corpus.\n\n"
            content += "The AI analysis found no conflicting statements between evidence items. "
            content += "This suggests consistency in the evidence base, which strengthens overall "
            content += "case credibility.\n\n"
            content += "---\n\n"
            return content

        content = "## 1. Contradictions Analysis\n\n"
        content += f"⚠️ **{len(contradictions)} contradiction(s) detected** requiring investigation.\n\n"
        content += "Contradictions represent conflicting statements or facts across evidence items. "
        content += "These must be resolved before proceeding to tribunal, as opposing counsel will "
        content += "exploit inconsistencies.\n\n"

        for i, contradiction in enumerate(contradictions, 1):
            contradiction_type = contradiction.contradiction_type
            severity_score = contradiction.severity
            explanation = contradiction.explanation
            statement_1 = contradiction.statement_1
            statement_2 = contradiction.statement_2
            source_1 = contradiction.statement_1_source
            source_2 = contradiction.statement_2_source

            # Convert severity float to category
            severity_label = "HIGH" if severity_score >= 0.7 else "MODERATE" if severity_score >= 0.4 else "LOW"

            content += f"### Contradiction #{i}: {self._format_contradiction_type(contradiction_type)}\n\n"
            content += f"**Severity**: {severity_label} ({self._format_percentage(severity_score, decimals=0)})\n\n"
            content += f"**Explanation**: {explanation}\n\n"

            content += "**Conflicting Statements**:\n\n"
            content += f"1. \"{statement_1}\"\n"
            content += f"   - Source: Evidence {self._truncate_sha(source_1)}\n\n"
            content += f"2. \"{statement_2}\"\n"
            content += f"   - Source: Evidence {self._truncate_sha(source_2)}\n\n"

            content += "**Recommended Actions**:\n"
            content += self._get_contradiction_recommendations(contradiction_type, severity_label)
            content += "\n"

        content += "---\n\n"
        return content

    def _build_corroboration_section(self) -> str:
        """Build corroboration analysis section."""
        legal_patterns = self._get_legal_patterns()

        if not legal_patterns:
            return ""

        corroboration = legal_patterns.corroboration

        if not corroboration:
            content = "## 2. Corroboration Analysis\n\n"
            content += "No explicit corroboration links detected.\n\n"
            content += "---\n\n"
            return content

        content = "## 2. Corroboration Analysis\n\n"
        content += f"**{len(corroboration)} corroboration link(s) identified** supporting key claims.\n\n"
        content += "Corroboration strengthens case credibility by showing multiple independent evidence "
        content += "pieces supporting the same facts or claims.\n\n"

        # Group by strength
        strong = [c for c in corroboration if c.corroboration_strength == 'strong']
        moderate = [c for c in corroboration if c.corroboration_strength == 'moderate']
        weak = [c for c in corroboration if c.corroboration_strength == 'weak']

        content += "### Corroboration Strength Distribution\n\n"
        content += f"- **Strong**: {len(strong)} link(s)\n"
        content += f"- **Moderate**: {len(moderate)} link(s)\n"
        content += f"- **Weak**: {len(weak)} link(s)\n\n"

        # Detail each corroboration link
        content += "### Corroboration Details\n\n"

        for i, link in enumerate(corroboration, 1):
            claim = link.claim
            strength = link.corroboration_strength
            explanation = link.explanation
            evidence_refs = link.supporting_evidence

            strength_emoji = "🟢" if strength == "strong" else "🟡" if strength == "moderate" else "⚪"

            content += f"#### {strength_emoji} Link #{i} [{strength.upper()}]\n\n"
            content += f"**Claim**: {claim}\n\n"
            content += f"**Analysis**: {explanation}\n\n"

            if evidence_refs:
                content += f"**Supporting Evidence** ({len(evidence_refs)} piece(s)):\n"
                for ref in evidence_refs:
                    sha_short = self._truncate_sha(ref)
                    content += f"- Evidence {sha_short}\n"
                content += "\n"

        content += "---\n\n"
        return content

    def _build_evidence_gaps_section(self) -> str:
        """Build evidence gaps analysis section."""
        legal_patterns = self._get_legal_patterns()

        if not legal_patterns:
            return ""

        evidence_gaps = legal_patterns.evidence_gaps

        if not evidence_gaps:
            content = "## 3. Evidence Gaps\n\n"
            content += "✓ **No significant evidence gaps identified**.\n\n"
            content += "---\n\n"
            return content

        content = "## 3. Evidence Gaps\n\n"
        content += f"**{len(evidence_gaps)} evidence gap(s) identified** that may impact case outcome.\n\n"
        content += "Evidence gaps represent missing documentation, witness statements, or other "
        content += "supporting materials that could strengthen the case or address potential weaknesses.\n\n"

        content += "### Identified Gaps\n\n"

        for i, gap in enumerate(evidence_gaps, 1):
            # Assess gap priority
            priority = self._assess_gap_priority(gap, i, len(evidence_gaps))

            content += f"{i}. **[{priority}]** {gap}\n\n"

        content += "### Gap Mitigation Strategy\n\n"
        content += self._build_gap_mitigation_strategy(evidence_gaps)
        content += "\n"

        content += "---\n\n"
        return content

    def _build_pattern_summary_section(self) -> str:
        """Build overall pattern summary section."""
        legal_patterns = self._get_legal_patterns()

        if not legal_patterns:
            return ""

        pattern_summary = legal_patterns.pattern_summary
        confidence = legal_patterns.confidence

        if not pattern_summary:
            return ""

        content = "## 4. Overall Pattern Assessment\n\n"
        content += f"**AI Confidence**: {self._format_percentage(confidence, decimals=0)}\n\n"
        content += f"{pattern_summary}\n\n"
        content += "---\n\n"
        return content

    def _build_strategic_implications_section(self) -> str:
        """Build strategic implications section."""
        legal_patterns = self._get_legal_patterns()

        if not legal_patterns:
            return ""

        contradictions = legal_patterns.contradictions
        corroboration = legal_patterns.corroboration
        evidence_gaps = legal_patterns.evidence_gaps

        content = "## 5. Strategic Implications\n\n"

        # Defense/prosecution positioning
        content += "### Case Positioning\n\n"

        strong_corroboration = sum(1 for c in corroboration if c.corroboration_strength == 'strong')

        if contradictions:
            content += "**Defense Challenges**:\n"
            content += f"- {len(contradictions)} contradiction(s) must be resolved before trial\n"
            content += "- Opposing counsel will exploit inconsistencies\n"
            content += "- Consider settlement to avoid courtroom exposure\n\n"

        if strong_corroboration >= 3:
            content += "**Strengths**:\n"
            content += f"- {strong_corroboration} strong corroboration link(s) support key claims\n"
            content += "- Multiple independent evidence pieces strengthen credibility\n"
            content += "- Strong foundation for tribunal presentation\n\n"

        if len(evidence_gaps) > 3:
            content += "**Evidence Collection Priority**:\n"
            content += f"- {len(evidence_gaps)} gap(s) require attention\n"
            content += "- Focus on high-priority gaps first\n"
            content += "- Consider discovery requests for missing documentation\n\n"

        # Recommended actions
        content += "### Recommended Actions\n\n"
        content += self._get_strategic_recommendations(contradictions, corroboration, evidence_gaps)
        content += "\n"

        content += "---\n\n"
        return content

    def _build_methodology_section(self) -> str:
        """Build methodology section."""
        content = "## 6. Methodology\n\n"

        content += "### Pattern Detection Process\n\n"
        content += "Legal pattern analysis uses AI-powered cross-evidence comparison:\n\n"

        content += "1. **Contradiction Detection**: Identifies conflicting statements across evidence\n"
        content += "   - Factual contradictions (mutually exclusive facts)\n"
        content += "   - Temporal contradictions (timeline inconsistencies)\n"
        content += "   - Attribution contradictions (conflicting testimony about who said/did what)\n\n"

        content += "2. **Corroboration Analysis**: Finds multiple evidence items supporting same claims\n"
        content += "   - Strong: 3+ independent evidence pieces, clear alignment\n"
        content += "   - Moderate: 2 evidence pieces, general alignment\n"
        content += "   - Weak: 1-2 pieces, partial or indirect support\n\n"

        content += "3. **Evidence Gap Identification**: Detects missing documentation/witnesses\n"
        content += "   - Missing witnesses mentioned in evidence\n"
        content += "   - Referenced but not provided documentation\n"
        content += "   - Procedural documentation gaps (HR records, meeting minutes)\n\n"

        content += "### Quality Assurance\n\n"
        content += "- All patterns detected by OpenAI GPT-4 analysis\n"
        content += "- Confidence scores reflect AI certainty (higher = more reliable)\n"
        content += "- Evidence references use SHA256 for cryptographic integrity\n"
        content += "- Human review recommended for final case strategy\n\n"

        content += "---\n\n"

        # Footer
        content += "*This legal patterns analysis was generated by Evidence Toolkit v3.4. "
        content += "All findings should be validated by qualified legal counsel before making strategic decisions.*\n"

        return content

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _get_legal_patterns(self) -> Optional[LegalPatternAnalysis]:
        """Get legal patterns data from correlation analysis.

        Returns:
            LegalPatternAnalysis Pydantic model or None if not found
        """
        correlation_result = self.case_summary.correlation_result

        if not correlation_result:
            return None

        # correlation_result is a CorrelationAnalysis Pydantic model
        # Access legal_patterns attribute directly
        if hasattr(correlation_result, 'legal_patterns'):
            return correlation_result.legal_patterns

        return None

    def _format_contradiction_type(self, contradiction_type: str) -> str:
        """Format contradiction type for display.

        Args:
            contradiction_type: Type of contradiction (factual, temporal, etc.)

        Returns:
            Formatted type string
        """
        type_map = {
            'factual': 'Factual Contradiction',
            'temporal': 'Timeline Inconsistency',
            'attribution': 'Attribution Conflict',
            'procedural': 'Procedural Discrepancy',
            'general': 'General Contradiction'
        }

        return type_map.get(contradiction_type.lower(), contradiction_type.title())

    def _get_contradiction_recommendations(self, contradiction_type: str, severity: str) -> str:
        """Get recommendations for resolving contradiction.

        Args:
            contradiction_type: Type of contradiction
            severity: Severity level (high, moderate, low)

        Returns:
            Markdown formatted recommendations
        """
        recommendations = ""

        if severity.lower() == 'high':
            recommendations += "1. **URGENT**: Resolve before proceeding to tribunal\n"
            recommendations += "2. Obtain clarifying statements from involved parties\n"
            recommendations += "3. Review original evidence for context\n"
            recommendations += "4. Consider settlement if contradiction cannot be resolved\n"
        else:
            recommendations += "1. Investigate discrepancy with involved parties\n"
            recommendations += "2. Determine if contradiction is material to case outcome\n"
            recommendations += "3. Prepare explanation for potential tribunal questions\n"

        return recommendations

    def _assess_gap_priority(self, gap: str, position: int, total: int) -> str:
        """Assess evidence gap priority.

        Args:
            gap: Gap description
            position: Position in list (1-indexed)
            total: Total number of gaps

        Returns:
            Priority label: CRITICAL, HIGH, MEDIUM, or STANDARD
        """
        gap_lower = gap.lower()

        # Keyword-based priority assessment
        critical_keywords = ['witness', 'statement', 'hr', 'policy', 'tribunal', 'legal']
        high_keywords = ['document', 'record', 'email', 'communication']

        if any(kw in gap_lower for kw in critical_keywords):
            return "CRITICAL"
        elif any(kw in gap_lower for kw in high_keywords):
            return "HIGH"
        elif position <= (total * 0.5):
            return "MEDIUM"
        else:
            return "STANDARD"

    def _build_gap_mitigation_strategy(self, evidence_gaps: List[str]) -> str:
        """Build gap mitigation strategy recommendations.

        Args:
            evidence_gaps: List of evidence gap descriptions

        Returns:
            Markdown formatted strategy
        """
        strategy = "**Recommended Approach**:\n\n"

        strategy += "1. **Immediate Actions** (within 7 days):\n"
        strategy += "   - Identify and contact potential witnesses for statements\n"
        strategy += "   - Submit document production requests for referenced materials\n"
        strategy += "   - Review internal records for missing documentation\n\n"

        strategy += "2. **Short-term Actions** (within 30 days):\n"
        strategy += "   - Conduct follow-up interviews to clarify missing details\n"
        strategy += "   - Engage discovery process for third-party documentation\n"
        strategy += "   - Assess whether gaps are material to case outcome\n\n"

        strategy += "3. **Contingency Planning**:\n"
        strategy += "   - If gaps cannot be filled, prepare alternative arguments\n"
        strategy += "   - Consider impact on tribunal probability and settlement positioning\n"
        strategy += "   - Document all attempts to obtain missing evidence (shows good faith)\n"

        return strategy

    def _get_strategic_recommendations(
        self,
        contradictions: List,
        corroboration: List,
        evidence_gaps: List
    ) -> str:
        """Get strategic recommendations based on pattern analysis.

        Args:
            contradictions: List of contradictions
            corroboration: List of corroboration links
            evidence_gaps: List of evidence gaps

        Returns:
            Markdown formatted recommendations
        """
        recommendations = ""

        strong_corr = sum(1 for c in corroboration if c.corroboration_strength == 'strong')

        if contradictions and evidence_gaps:
            recommendations += "1. **Priority**: Address contradictions AND fill evidence gaps\n"
            recommendations += "2. Settlement may be preferable to avoid tribunal exposure\n"
            recommendations += "3. Obtain external counsel review of contradictions\n"
        elif contradictions:
            recommendations += "1. **Priority**: Resolve all contradictions before trial\n"
            recommendations += "2. Consider mediation/settlement to avoid courtroom inconsistencies\n"
            recommendations += "3. Prepare detailed explanations for each contradiction\n"
        elif evidence_gaps:
            recommendations += "1. **Priority**: Fill high-priority evidence gaps\n"
            recommendations += "2. Assess whether remaining gaps are material\n"
            recommendations += "3. Proceed with strong corroboration as foundation\n"
        elif strong_corr >= 3:
            recommendations += "1. **Strength**: Leverage strong corroboration in settlement negotiations\n"
            recommendations += "2. Prepare tribunal presentation highlighting evidence alignment\n"
            recommendations += "3. Consider pursuing case if financially viable\n"
        else:
            recommendations += "1. Continue evidence gathering to strengthen position\n"
            recommendations += "2. Monitor for additional corroboration opportunities\n"
            recommendations += "3. Assess cost-benefit of tribunal vs. settlement\n"

        return recommendations
