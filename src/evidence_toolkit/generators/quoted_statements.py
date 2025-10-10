"""Quoted Statements Generator - v3.4 Phase 2 (Final)

Generates person-by-person quoted statement analysis from evidence corpus.
Extracts direct quotes with speaker attribution, sentiment, and risk indicators.

Data Sources:
- overall_assessment['quoted_statements'] (Dict with nested structure)
  - quoted_statements: List of person objects with statements
  - total_statements: Count of extracted quotes
  - people_quoted: Number of unique speakers
  - documents_with_quotes: Count of evidence with quotes

This generator provides valuable tribunal preparation by:
1. Identifying key speakers and their positions
2. Analyzing sentiment patterns per person (professional/hostile/neutral)
3. Flagging high-risk statements (threats, admissions, policy violations)
4. Cross-referencing statements with evidence sources
5. Supporting witness preparation and cross-examination strategy

Cost: ZERO new AI calls - uses existing quoted statement extraction
Value: Witness preparation tool + cross-examination strategy
Effort: ~4 hours implementation
"""

from pathlib import Path
from typing import Dict, List, Any, Optional

from evidence_toolkit.generators.base import BaseReportGenerator


class QuotedStatementsGenerator(BaseReportGenerator):
    """Generate quoted statements analysis report.

    Extracts and analyzes direct quotes from evidence, grouped by speaker,
    with sentiment analysis and risk indicator flagging.

    Data Sources:
        - overall_assessment['quoted_statements']['quoted_statements']
        - overall_assessment['quoted_statements']['total_statements']
        - overall_assessment['quoted_statements']['people_quoted']

    Output: quoted_statements_analysis.md (professional Markdown report)

    Example:
        >>> generator = QuotedStatementsGenerator(case_summary, reports_dir)
        >>> if generator.has_data():
        ...     report_path = generator.generate()
        ...     # Creates: reports/quoted_statements_analysis.md
    """

    def get_report_filename(self) -> str:
        """Return filename for quoted statements report."""
        return "quoted_statements_analysis.md"

    def get_report_title(self) -> str:
        """Return human-readable report title."""
        return "Quoted Statements Analysis"

    def has_data(self) -> bool:
        """Check if quoted statements data exists.

        Report is generated if quoted statements are available.

        Returns:
            True if statements exist
        """
        quoted_data = self._get_quoted_statements_data()

        if not quoted_data:
            return False

        statements = quoted_data.get('quoted_statements', [])
        return bool(statements and len(statements) > 0)

    def generate(self) -> Path:
        """Generate the quoted statements analysis report.

        Creates a person-by-person breakdown of quoted statements with
        sentiment analysis and risk indicators.

        Returns:
            Path to generated report file

        Raises:
            Exception: If report generation fails
        """
        # Build report content
        content = self._build_header(subtitle="Direct Quote Extraction & Speaker Analysis")

        # Add executive summary
        content += self._build_executive_summary()

        # Section 1: Key Speakers Overview
        content += self._build_speakers_overview_section()

        # Section 2: Detailed Statements by Person
        content += self._build_statements_by_person_section()

        # Section 3: Risk Indicators Analysis
        content += self._build_risk_indicators_section()

        # Section 4: Sentiment Analysis
        content += self._build_sentiment_analysis_section()

        # Section 5: Tribunal Implications
        content += self._build_tribunal_implications_section()

        # Section 6: Strategic Recommendations
        content += self._build_strategic_recommendations_section()

        # Write report to file
        report_path = self.output_dir / self.get_report_filename()
        report_path.write_text(content, encoding='utf-8')

        return report_path

    # =========================================================================
    # SECTION BUILDERS
    # =========================================================================

    def _build_executive_summary(self) -> str:
        """Build executive summary of quoted statements."""
        quoted_data = self._get_quoted_statements_data()

        total_statements = quoted_data.get('total_statements', 0)
        people_quoted = quoted_data.get('people_quoted', 0)
        documents_with_quotes = quoted_data.get('documents_with_quotes', 0)

        content = "## Executive Summary\n\n"

        content += f"**Total Statements Extracted**: {total_statements}\n"
        content += f"**People Quoted**: {people_quoted}\n"
        content += f"**Documents with Quotes**: {documents_with_quotes}\n\n"

        # Identify speakers with high-risk statements
        statements = quoted_data.get('quoted_statements', [])
        high_risk_speakers = [
            s for s in statements
            if s.get('has_risk_indicators', False)
        ]

        if high_risk_speakers:
            content += f"⚠️ **ATTENTION**: {len(high_risk_speakers)} speaker(s) with high-risk statements detected\n\n"

        # Sentiment overview
        hostile_speakers = [
            s for s in statements
            if s.get('dominant_sentiment') == 'hostile'
        ]

        if hostile_speakers:
            content += f"⚠️ **CONCERN**: {len(hostile_speakers)} speaker(s) with hostile sentiment\n\n"

        content += "---\n\n"
        return content

    def _build_speakers_overview_section(self) -> str:
        """Build key speakers overview."""
        quoted_data = self._get_quoted_statements_data()
        statements = quoted_data.get('quoted_statements', [])

        if not statements:
            return ""

        content = "## 1. Key Speakers Overview\n\n"

        # Sort by statement count (most active first)
        sorted_speakers = sorted(
            statements,
            key=lambda s: s.get('statement_count', 0),
            reverse=True
        )

        content += "| Person | Role | Statements | Sentiment | Risk Flags |\n"
        content += "|--------|------|------------|-----------|------------|\n"

        for speaker in sorted_speakers:
            person = speaker.get('person', 'Unknown')
            role = speaker.get('role', 'Not specified')
            stmt_count = speaker.get('statement_count', 0)
            sentiment = speaker.get('dominant_sentiment', 'unknown').title()
            has_risk = "⚠️ Yes" if speaker.get('has_risk_indicators', False) else "No"

            content += f"| {person} | {role} | {stmt_count} | {sentiment} | {has_risk} |\n"

        content += "\n---\n\n"
        return content

    def _build_statements_by_person_section(self) -> str:
        """Build detailed statements grouped by person."""
        quoted_data = self._get_quoted_statements_data()
        statements = quoted_data.get('quoted_statements', [])

        if not statements:
            return ""

        content = "## 2. Detailed Statements by Person\n\n"
        content += "Chronological listing of all extracted statements, grouped by speaker.\n\n"

        # Sort by statement count (most active first)
        sorted_speakers = sorted(
            statements,
            key=lambda s: s.get('statement_count', 0),
            reverse=True
        )

        for speaker in sorted_speakers:
            person = speaker.get('person', 'Unknown')
            role = speaker.get('role', 'Not specified')
            stmt_list = speaker.get('statements', [])
            sentiment = speaker.get('dominant_sentiment', 'unknown')

            # Speaker header
            content += f"### {person}\n\n"
            content += f"**Role**: {role}\n"
            content += f"**Total Statements**: {len(stmt_list)}\n"
            content += f"**Dominant Sentiment**: {sentiment.title()}\n\n"

            # Risk indicators if present
            risk_types = speaker.get('risk_types', [])
            if risk_types:
                content += f"**Risk Indicators**: {', '.join(risk_types)}\n\n"

            # Sentiment distribution
            sentiment_dist = speaker.get('sentiment_distribution', {})
            if sentiment_dist:
                content += "**Sentiment Breakdown**: "
                sentiment_parts = [f"{sent.title()}: {count}" for sent, count in sentiment_dist.items()]
                content += ", ".join(sentiment_parts) + "\n\n"

            # Individual statements
            if stmt_list:
                content += "#### Statements\n\n"

                for i, statement in enumerate(stmt_list, 1):
                    text = statement.get('text', '[No text]')
                    source_sha = statement.get('source_sha256', '')
                    source_file = statement.get('source_file', 'Unknown')
                    doc_sentiment = statement.get('document_sentiment', 'unknown')
                    risk_flags = statement.get('risk_flags', [])
                    context = statement.get('context', '')

                    content += f"**Statement {i}**:\n\n"
                    content += f"> \"{text}\"\n\n"

                    content += f"- **Source**: Evidence {self._truncate_sha(source_sha)} ({source_file})\n"
                    content += f"- **Document Sentiment**: {doc_sentiment.title()}\n"

                    if risk_flags:
                        content += f"- **Risk Flags**: {', '.join(risk_flags)}\n"

                    if context:
                        # Truncate context if too long
                        context_preview = context[:150] + "..." if len(context) > 150 else context
                        content += f"- **Context**: {context_preview}\n"

                    content += "\n"

            content += "---\n\n"

        return content

    def _build_risk_indicators_section(self) -> str:
        """Build risk indicators analysis."""
        quoted_data = self._get_quoted_statements_data()
        statements = quoted_data.get('quoted_statements', [])

        # Collect all risk-flagged statements
        risk_statements = []
        for speaker in statements:
            if speaker.get('has_risk_indicators', False):
                person = speaker.get('person', 'Unknown')
                for stmt in speaker.get('statements', []):
                    if stmt.get('risk_flags'):
                        risk_statements.append({
                            'person': person,
                            'statement': stmt
                        })

        if not risk_statements:
            content = "## 3. Risk Indicators Analysis\n\n"
            content += "✓ **No high-risk statements identified**.\n\n"
            content += "No statements were flagged with risk indicators (threats, admissions, policy violations).\n\n"
            content += "---\n\n"
            return content

        content = "## 3. Risk Indicators Analysis\n\n"
        content += f"⚠️ **{len(risk_statements)} high-risk statement(s) identified**.\n\n"

        # Group by risk type
        risk_by_type: Dict[str, List] = {}
        for item in risk_statements:
            stmt = item['statement']
            for risk_flag in stmt.get('risk_flags', []):
                if risk_flag not in risk_by_type:
                    risk_by_type[risk_flag] = []
                risk_by_type[risk_flag].append(item)

        content += "### Risk Categories\n\n"

        for risk_type, items in sorted(risk_by_type.items(), key=lambda x: len(x[1]), reverse=True):
            content += f"#### {risk_type.replace('_', ' ').title()} ({len(items)} statement(s))\n\n"

            for item in items[:3]:  # Show top 3 per category
                person = item['person']
                stmt = item['statement']
                text = stmt.get('text', '[No text]')
                source_sha = stmt.get('source_sha256', '')

                content += f"**{person}**: \"{text[:100]}{'...' if len(text) > 100 else ''}\"\n"
                content += f"- Source: Evidence {self._truncate_sha(source_sha)}\n\n"

            if len(items) > 3:
                content += f"*(+{len(items) - 3} additional {risk_type} statement(s))*\n\n"

        content += "---\n\n"
        return content

    def _build_sentiment_analysis_section(self) -> str:
        """Build sentiment analysis section."""
        quoted_data = self._get_quoted_statements_data()
        statements = quoted_data.get('quoted_statements', [])

        content = "## 4. Sentiment Analysis\n\n"

        # Overall sentiment distribution
        overall_sentiment: Dict[str, int] = {}
        for speaker in statements:
            sentiment_dist = speaker.get('sentiment_distribution', {})
            for sentiment, count in sentiment_dist.items():
                overall_sentiment[sentiment] = overall_sentiment.get(sentiment, 0) + count

        if overall_sentiment:
            content += "### Overall Sentiment Distribution\n\n"

            total_stmts = sum(overall_sentiment.values())
            for sentiment, count in sorted(overall_sentiment.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_stmts * 100) if total_stmts > 0 else 0
                content += f"- **{sentiment.title()}**: {count} statement(s) ({percentage:.1f}%)\n"

            content += "\n"

        # Highlight hostile sentiment
        hostile_speakers = [
            s for s in statements
            if s.get('dominant_sentiment') == 'hostile'
        ]

        if hostile_speakers:
            content += "### Hostile Sentiment Speakers\n\n"
            content += "⚠️ The following speakers exhibited hostile sentiment in their statements:\n\n"

            for speaker in hostile_speakers:
                person = speaker.get('person', 'Unknown')
                stmt_count = speaker.get('statement_count', 0)
                content += f"- **{person}**: {stmt_count} hostile statement(s)\n"

            content += "\n**Tribunal Implications**: Hostile sentiment may indicate workplace conflict, "
            content += "potential harassment claims, or retaliatory conduct.\n\n"

        content += "---\n\n"
        return content

    def _build_tribunal_implications_section(self) -> str:
        """Build tribunal implications section."""
        quoted_data = self._get_quoted_statements_data()
        statements = quoted_data.get('quoted_statements', [])

        content = "## 5. Tribunal Implications\n\n"

        content += "### Witness Preparation\n\n"
        content += "Quoted statements provide foundation for:\n\n"
        content += "1. **Direct Examination**: Use statements as talking points for witness testimony\n"
        content += "2. **Cross-Examination**: Challenge opposing witnesses with contradictory statements\n"
        content += "3. **Credibility Assessment**: Evaluate consistency of statements over time\n"
        content += "4. **Documentary Evidence**: Link statements to supporting documents\n\n"

        # High-value speakers (most statements)
        sorted_speakers = sorted(
            statements,
            key=lambda s: s.get('statement_count', 0),
            reverse=True
        )

        if sorted_speakers:
            top_speakers = sorted_speakers[:3]
            content += "### Key Witnesses\n\n"
            content += "Prioritize preparation for speakers with most statements:\n\n"

            for i, speaker in enumerate(top_speakers, 1):
                person = speaker.get('person', 'Unknown')
                stmt_count = speaker.get('statement_count', 0)
                sentiment = speaker.get('dominant_sentiment', 'unknown')
                has_risk = speaker.get('has_risk_indicators', False)

                content += f"{i}. **{person}**: {stmt_count} statement(s), "
                content += f"{sentiment} sentiment"
                if has_risk:
                    content += " ⚠️ (risk indicators present)"
                content += "\n"

            content += "\n"

        content += "### Statement Admissibility\n\n"
        content += "**Considerations**:\n"
        content += "- Statements from documents are generally admissible as documentary evidence\n"
        content += "- Email statements carry evidentiary weight (contemporaneous records)\n"
        content += "- Risk-flagged statements may be particularly probative\n"
        content += "- Context is crucial - review full documents before citing\n\n"

        content += "---\n\n"
        return content

    def _build_strategic_recommendations_section(self) -> str:
        """Build strategic recommendations section."""
        quoted_data = self._get_quoted_statements_data()
        statements = quoted_data.get('quoted_statements', [])

        content = "## 6. Strategic Recommendations\n\n"

        # Count risk statements
        risk_count = sum(1 for s in statements if s.get('has_risk_indicators', False))
        hostile_count = sum(1 for s in statements if s.get('dominant_sentiment') == 'hostile')

        content += "### Immediate Actions\n\n"

        if risk_count > 0:
            content += "1. **High Priority**: Review all risk-flagged statements with legal counsel\n"
            content += "   - Assess admissibility and probative value\n"
            content += "   - Prepare responses to potential opposing arguments\n"
            content += "   - Consider settlement implications\n\n"

        content += "2. **Witness Statement Collection**\n"
        content += "   - Obtain written statements from key speakers\n"
        content += "   - Ensure consistency with quoted statements\n"
        content += "   - Address any gaps or contradictions\n\n"

        content += "3. **Document Verification**\n"
        content += "   - Verify authenticity of source documents\n"
        content += "   - Confirm dates and recipients\n"
        content += "   - Preserve original electronic copies (metadata)\n\n"

        if hostile_count > 0:
            content += "4. **Hostile Sentiment Mitigation**\n"
            content += "   - Investigate workplace conflict escalation\n"
            content += "   - Consider mediation or settlement\n"
            content += "   - Prepare defense against harassment/bullying claims\n\n"

        content += "### Cross-Examination Strategy\n\n"
        content += "**For Claimant**:\n"
        content += "- Use favorable quotes to support timeline of events\n"
        content += "- Challenge respondent witnesses with their own statements\n"
        content += "- Highlight hostile sentiment as evidence of workplace toxicity\n\n"

        content += "**For Respondent**:\n"
        content += "- Demonstrate professional handling through formal communications\n"
        content += "- Challenge claimant's credibility if statements conflict\n"
        content += "- Show procedural compliance through documented exchanges\n\n"

        content += "---\n\n"

        # Footer
        content += "*This quoted statements analysis was generated by Evidence Toolkit v3.4. "
        content += "All quotes should be verified against original source documents before tribunal use.*\n"

        return content

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _get_quoted_statements_data(self) -> Dict[str, Any]:
        """Get quoted statements data from overall assessment.

        Returns:
            Quoted statements dict or empty dict if not found
        """
        overall_assessment = self.case_summary.overall_assessment

        if not overall_assessment:
            return {}

        # The data is nested under 'quoted_statements' key
        return overall_assessment.get('quoted_statements', {})
