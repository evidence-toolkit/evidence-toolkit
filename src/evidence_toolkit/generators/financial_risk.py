"""Financial Risk Assessment Generator - v3.4 Phase 1

Expands tribunal probability and financial exposure analysis into a detailed
risk assessment report suitable for client decision-making and settlement strategy.

Data Sources (all existing in overall_assessment):
- tribunal_probability: Statistical likelihood of tribunal proceedings
- financial_exposure_summary: Estimated liability ranges
- claim_strength_summary: Assessment of claimant's case strength
- settlement_recommendation: Recommended settlement positioning
- _forensic_risk_assessment: Risk characterization narrative

Unlike forensic_legal.py which just unhides data, this generator ENHANCES
financial analysis by breaking down:
1. Tribunal probability factors
2. Detailed cost breakdowns (basic awards, compensatory awards, legal costs)
3. Settlement positioning strategy
4. Risk-adjusted financial modeling

Cost: ZERO new AI calls - uses existing analyzed data
Value: Transforms basic tribunal % → actionable financial strategy
Effort: ~3 hours implementation
"""

from pathlib import Path
from typing import Dict, Optional, Tuple

from evidence_toolkit.generators.base import BaseReportGenerator


class FinancialRiskAssessmentGenerator(BaseReportGenerator):
    """Generate detailed financial risk assessment for tribunal exposure.

    Expands the basic tribunal_probability and financial_exposure_summary fields
    into a comprehensive financial risk report with cost breakdowns, settlement
    positioning, and risk-adjusted modeling.

    Data Sources:
        - tribunal_probability: Base probability (0.0-1.0)
        - financial_exposure_summary: Text summary of exposure range
        - claim_strength_summary: Claimant case strength assessment
        - settlement_recommendation: Settlement positioning guidance
        - _forensic_risk_assessment: Risk characterization (optional)

    Output: financial_risk_assessment.md (professional Markdown report)

    Example:
        >>> generator = FinancialRiskAssessmentGenerator(case_summary, reports_dir)
        >>> if generator.has_data():
        ...     report_path = generator.generate()
        ...     # Creates: reports/financial_risk_assessment.md
    """

    def get_report_filename(self) -> str:
        """Return filename for financial risk assessment report."""
        return "financial_risk_assessment.md"

    def get_report_title(self) -> str:
        """Return human-readable report title."""
        return "Financial Risk Assessment"

    def has_data(self) -> bool:
        """Check if financial risk data exists.

        Report generated if tribunal probability OR financial exposure data present.

        Returns:
            True if financial risk data available
        """
        tribunal_prob = self._safe_get('tribunal_probability')
        financial_exposure = self._safe_get('financial_exposure_summary')

        return tribunal_prob is not None or bool(financial_exposure)

    def generate(self) -> Path:
        """Generate the financial risk assessment report.

        Creates a detailed financial risk analysis expanding on the basic
        tribunal probability and exposure estimates.

        Returns:
            Path to generated report file

        Raises:
            Exception: If report generation fails
        """
        # Build report content
        content = self._build_header(subtitle="Tribunal Exposure & Settlement Strategy")

        # Add executive summary
        content += self._build_executive_summary()

        # Section 1: Tribunal Probability Analysis
        content += self._build_tribunal_probability_section()

        # Section 2: Financial Exposure Breakdown
        content += self._build_financial_exposure_section()

        # Section 3: Claim Strength Assessment
        content += self._build_claim_strength_section()

        # Section 4: Settlement Strategy
        content += self._build_settlement_strategy_section()

        # Section 5: Risk-Adjusted Modeling
        content += self._build_risk_modeling_section()

        # Section 6: Recommendations
        content += self._build_recommendations_section()

        # Write report to file
        report_path = self.output_dir / self.get_report_filename()
        report_path.write_text(content, encoding='utf-8')

        return report_path

    # =========================================================================
    # SECTION BUILDERS
    # =========================================================================

    def _build_executive_summary(self) -> str:
        """Build executive summary of financial risk."""
        tribunal_prob = self._safe_get('tribunal_probability')
        financial_exposure = self._safe_get('financial_exposure_summary', 'Not assessed')

        content = "## Executive Summary\n\n"

        if tribunal_prob is not None:
            risk_level = self._assess_risk_level(tribunal_prob)
            content += f"**Tribunal Risk Level**: {risk_level} ({self._format_percentage(tribunal_prob, decimals=0)})\n\n"

        content += f"**Estimated Financial Exposure**: {financial_exposure}\n\n"

        # Add strategic positioning
        settlement_rec = self._safe_get('settlement_recommendation')
        if settlement_rec:
            content += f"**Settlement Positioning**: {settlement_rec}\n\n"

        content += "---\n\n"
        return content

    def _build_tribunal_probability_section(self) -> str:
        """Build tribunal probability analysis."""
        tribunal_prob = self._safe_get('tribunal_probability')

        if tribunal_prob is None:
            return ""

        content = "## 1. Tribunal Probability Analysis\n\n"

        # Risk level assessment
        risk_level = self._assess_risk_level(tribunal_prob)
        content += f"### Overall Assessment: {risk_level}\n\n"
        content += f"**Probability**: {self._format_percentage(tribunal_prob, decimals=1)}\n\n"

        # Interpretation
        content += self._interpret_tribunal_probability(tribunal_prob)

        # Contributing factors
        claim_strength = self._safe_get('claim_strength_summary')
        if claim_strength:
            content += "\n### Contributing Factors\n\n"
            content += f"**Claim Strength Analysis**: {claim_strength}\n\n"

        # Evidence quality factors
        evidence_gaps = self._safe_get('evidence_gaps', [])
        if evidence_gaps:
            content += "**Evidence Weaknesses**:\n\n"
            content += self._format_list_items(evidence_gaps, numbered=False)
            content += "\n"

        content += "---\n\n"
        return content

    def _build_financial_exposure_section(self) -> str:
        """Build financial exposure breakdown."""
        financial_exposure = self._safe_get('financial_exposure_summary')

        if not financial_exposure:
            return ""

        content = "## 2. Financial Exposure Breakdown\n\n"

        # Parse exposure range if it follows standard format
        exposure_range = self._parse_exposure_range(financial_exposure)

        if exposure_range:
            low, high = exposure_range
            content += f"### Exposure Range\n\n"
            content += f"- **Lower Bound**: {low}\n"
            content += f"- **Upper Bound**: {high}\n"
            content += f"- **Mid-Range Estimate**: {self._calculate_midpoint(low, high)}\n\n"
        else:
            content += f"### Estimated Exposure\n\n"
            content += f"{financial_exposure}\n\n"

        # Cost components (UK employment tribunal typical structure)
        content += "### Typical Cost Components\n\n"
        content += "Employment tribunal claims typically comprise:\n\n"
        content += "1. **Basic Award** (unfair dismissal)\n"
        content += "   - Calculated as: 0.5-1.5 weeks' gross pay × years of service\n"
        content += "   - Statutory cap applies (£21,000 as of 2025)\n\n"

        content += "2. **Compensatory Award** (unfair dismissal)\n"
        content += "   - Lost earnings from dismissal to tribunal hearing\n"
        content += "   - Future loss of earnings (typically 6-18 months)\n"
        content += "   - Loss of statutory rights (typically £500)\n"
        content += "   - Statutory cap: £115,115 (2025) or 52 weeks' gross pay, whichever is lower\n\n"

        content += "3. **Injury to Feelings** (discrimination claims)\n"
        content += "   - Vento bands: Lower (£1,200-£12,900), Middle (£12,900-£38,700), Upper (£38,700-£64,500)\n\n"

        content += "4. **Aggravated Damages** (if conduct particularly bad)\n"
        content += "   - Typically 25-50% uplift on injury to feelings\n\n"

        content += "5. **Legal Costs & Management Time**\n"
        content += "   - Internal legal costs: £15,000-30,000\n"
        content += "   - External counsel: £20,000-50,000+ (if contested)\n"
        content += "   - Management time: £5,000-15,000\n\n"

        content += "---\n\n"
        return content

    def _build_claim_strength_section(self) -> str:
        """Build claim strength assessment."""
        claim_strength = self._safe_get('claim_strength_summary')

        if not claim_strength:
            return ""

        content = "## 3. Claim Strength Assessment\n\n"
        content += f"{claim_strength}\n\n"

        # Add risk flag analysis
        risk_flag_breakdown = self._safe_get('risk_flag_breakdown', {})
        if risk_flag_breakdown:
            risk_flags = list(risk_flag_breakdown.keys())
            high_risk = [f for f in risk_flags if f in ['threatening', 'hostile', 'deadline']]
            if high_risk:
                content += "### High-Risk Indicators Present\n\n"
                content += self._format_list_items(high_risk, numbered=False)
                content += "\n"

        content += "---\n\n"
        return content

    def _build_settlement_strategy_section(self) -> str:
        """Build settlement strategy recommendations."""
        settlement_rec = self._safe_get('settlement_recommendation')
        tribunal_prob = self._safe_get('tribunal_probability')

        if not settlement_rec and tribunal_prob is None:
            return ""

        content = "## 4. Settlement Strategy\n\n"

        if settlement_rec:
            content += "### Recommended Settlement Positioning\n\n"
            content += f"{settlement_rec}\n\n"

        # Add strategic considerations based on tribunal probability
        if tribunal_prob is not None:
            content += "### Strategic Considerations\n\n"

            if tribunal_prob >= 0.70:
                content += "**HIGH RISK** - Strong settlement recommended:\n\n"
                content += "- Early settlement likely more cost-effective than defense\n"
                content += "- Consider opening with mid-range offer to signal seriousness\n"
                content += "- ACAS Early Conciliation strongly advised\n"
                content += "- Reputational risk mitigation through swift resolution\n\n"

            elif tribunal_prob >= 0.40:
                content += "**MODERATE RISK** - Settlement vs. defense decision point:\n\n"
                content += "- Cost-benefit analysis required (settlement vs. defense costs)\n"
                content += "- Consider conditional settlement (without admission of liability)\n"
                content += "- Explore ACAS Early Conciliation\n"
                content += "- Strengthen defense position through additional evidence gathering\n\n"

            else:
                content += "**LOWER RISK** - Defense may be viable:\n\n"
                content += "- Consider defending if strong procedural compliance evident\n"
                content += "- Settlement still possible at lower range to avoid costs\n"
                content += "- Focus on evidence gaps in claimant's case\n"
                content += "- ACAS Early Conciliation can still achieve cost-effective resolution\n\n"

        # Add immediate actions
        immediate_actions = self._safe_get('immediate_actions', [])
        if immediate_actions:
            content += "### Immediate Actions\n\n"
            content += self._format_list_items(immediate_actions, numbered=True)
            content += "\n"

        content += "---\n\n"
        return content

    def _build_risk_modeling_section(self) -> str:
        """Build risk-adjusted financial modeling."""
        tribunal_prob = self._safe_get('tribunal_probability')
        financial_exposure = self._safe_get('financial_exposure_summary')

        if tribunal_prob is None or not financial_exposure:
            return ""

        content = "## 5. Risk-Adjusted Financial Modeling\n\n"

        # Parse exposure range
        exposure_range = self._parse_exposure_range(financial_exposure)

        if exposure_range:
            low, high = exposure_range
            low_val = self._parse_currency(low)
            high_val = self._parse_currency(high)

            if low_val and high_val:
                # Calculate risk-adjusted expected value
                midpoint = (low_val + high_val) / 2
                expected_value = midpoint * tribunal_prob

                content += "### Expected Value Calculation\n\n"
                content += f"- **Exposure Range**: {low} - {high}\n"
                content += f"- **Mid-Range**: £{midpoint:,.0f}\n"
                content += f"- **Tribunal Probability**: {self._format_percentage(tribunal_prob, decimals=0)}\n"
                content += f"- **Expected Value**: £{expected_value:,.0f}\n\n"

                content += "> **Expected Value** = (Exposure Mid-Range) × (Tribunal Probability)\n\n"

                # Add defense cost comparison
                content += "### Defense Cost Comparison\n\n"
                content += "Estimated defense costs if case proceeds to tribunal:\n\n"
                content += "- **Internal legal costs**: £15,000 - £30,000\n"
                content += "- **External counsel**: £20,000 - £50,000\n"
                content += "- **Management time**: £5,000 - £15,000\n"
                content += "- **Total defense costs**: £40,000 - £95,000\n\n"

                settlement_breakeven = expected_value + 45000  # Midpoint of defense costs
                content += f"**Settlement Break-Even Point**: £{settlement_breakeven:,.0f}\n\n"
                content += f"> Settlement offers below £{settlement_breakeven:,.0f} may be more cost-effective than full defense.\n\n"

        content += "---\n\n"
        return content

    def _build_recommendations_section(self) -> str:
        """Build final recommendations."""
        content = "## 6. Recommendations\n\n"

        tribunal_prob = self._safe_get('tribunal_probability', 0)

        content += "### Strategic Recommendations\n\n"

        if tribunal_prob >= 0.70:
            content += "1. **Priority**: Early settlement negotiations\n"
            content += "2. Engage ACAS Early Conciliation immediately\n"
            content += "3. Prepare settlement authority at mid-to-high range\n"
            content += "4. Consider reputational risk mitigation strategy\n"
            content += "5. Minimize publicity and management distraction\n\n"

        elif tribunal_prob >= 0.40:
            content += "1. **Priority**: Parallel defense preparation and settlement exploration\n"
            content += "2. Gather additional evidence to strengthen defense position\n"
            content += "3. Engage ACAS Early Conciliation to test settlement appetite\n"
            content += "4. Prepare cost-benefit analysis (defense vs. settlement)\n"
            content += "5. Obtain external counsel opinion on merits\n\n"

        else:
            content += "1. **Priority**: Strengthen defense position\n"
            content += "2. Gather comprehensive evidence to address claimant's case\n"
            content += "3. Consider low-to-mid range settlement to avoid defense costs\n"
            content += "4. Prepare robust defense strategy if settlement fails\n"
            content += "5. ACAS Early Conciliation remains option for cost-effective resolution\n\n"

        content += "### Risk Mitigation\n\n"
        content += "- Maintain comprehensive documentation of all steps taken\n"
        content += "- Ensure legal professional privilege for all settlement discussions\n"
        content += "- Consider insurance coverage (EPLI - Employment Practices Liability Insurance)\n"
        content += "- Review and strengthen HR policies to prevent future claims\n\n"

        content += "---\n\n"

        # Footer
        content += "*This financial risk assessment is based on automated analysis and typical tribunal outcomes. "
        content += "Actual awards may vary significantly based on specific case circumstances. "
        content += "Consult with qualified employment law counsel before making strategic decisions.*\n"

        return content

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _assess_risk_level(self, probability: float) -> str:
        """Assess risk level from probability value."""
        if probability >= 0.70:
            return "HIGH RISK"
        elif probability >= 0.40:
            return "MODERATE RISK"
        elif probability >= 0.20:
            return "LOWER RISK"
        else:
            return "LOW RISK"

    def _interpret_tribunal_probability(self, probability: float) -> str:
        """Provide interpretation of tribunal probability."""
        interpretation = "### Interpretation\n\n"

        if probability >= 0.70:
            interpretation += ("A tribunal probability above 70% indicates strong likelihood of "
                             "proceedings if settlement is not reached. This suggests significant "
                             "evidence supporting potential claims and/or procedural weaknesses in "
                             "the respondent's position. Early settlement should be seriously considered.\n\n")

        elif probability >= 0.40:
            interpretation += ("A tribunal probability between 40-70% indicates moderate risk. "
                             "The case could reasonably proceed in either direction depending on "
                             "additional evidence and legal arguments. Cost-benefit analysis of "
                             "defense vs. settlement is critical.\n\n")

        elif probability >= 0.20:
            interpretation += ("A tribunal probability between 20-40% suggests lower but non-negligible "
                             "risk. Defense may be viable, but settlement could still be cost-effective "
                             "to avoid legal costs and management distraction.\n\n")

        else:
            interpretation += ("A tribunal probability below 20% suggests lower risk of proceedings. "
                             "However, even low-probability cases may proceed, and settlement may be "
                             "worthwhile to eliminate risk entirely.\n\n")

        return interpretation

    def _parse_exposure_range(self, exposure_text: str) -> Optional[Tuple[str, str]]:
        """Parse financial exposure text to extract range.

        Args:
            exposure_text: Text like "£50,000-70,000" or "£50K-70K"

        Returns:
            Tuple of (low, high) as formatted strings, or None if unparseable
        """
        import re

        # Match patterns like "£50,000-70,000" or "£50K-70K"
        pattern = r'£([\d,]+\.?\d*[KkMm]?)\s*[-–]\s*£?([\d,]+\.?\d*[KkMm]?)'
        match = re.search(pattern, exposure_text)

        if match:
            low = match.group(1)
            high = match.group(2)

            # Ensure both have £ prefix
            if not low.startswith('£'):
                low = f"£{low}"
            if not high.startswith('£'):
                high = f"£{high}"

            return (low, high)

        return None

    def _parse_currency(self, currency_str: str) -> Optional[float]:
        """Parse currency string to numeric value.

        Args:
            currency_str: String like "£50,000" or "£50K"

        Returns:
            Numeric value or None if unparseable
        """
        import re

        # Remove £ and commas
        clean = currency_str.replace('£', '').replace(',', '').strip()

        # Handle K/M suffixes
        multiplier = 1
        if clean.endswith('K') or clean.endswith('k'):
            multiplier = 1000
            clean = clean[:-1]
        elif clean.endswith('M') or clean.endswith('m'):
            multiplier = 1000000
            clean = clean[:-1]

        try:
            return float(clean) * multiplier
        except ValueError:
            return None

    def _calculate_midpoint(self, low: str, high: str) -> str:
        """Calculate midpoint of currency range.

        Args:
            low: Low end of range (e.g., "£50,000")
            high: High end of range (e.g., "£70,000")

        Returns:
            Formatted midpoint (e.g., "£60,000")
        """
        low_val = self._parse_currency(low)
        high_val = self._parse_currency(high)

        if low_val and high_val:
            midpoint = (low_val + high_val) / 2
            return f"£{midpoint:,.0f}"

        return "Unable to calculate"
