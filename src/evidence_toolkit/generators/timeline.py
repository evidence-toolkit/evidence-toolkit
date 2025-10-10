"""Timeline Reconstruction Generator - v3.4 Phase 2

Generates chronological timeline reconstruction from extracted temporal events.
Creates a tribunal-ready timeline with gap analysis and legal implications.

Data Sources:
- correlation_result.timeline_events (List[TimelineEvent])
  - Chronologically ordered events from all evidence
  - Includes document timestamps, semantic events, and analysis events
- correlation_result.temporal_sequences (List[TemporalSequence])
  - Identified patterns and sequences
- correlation_result.timeline_gaps (List[str])
  - Periods with missing documentation or activity

This generator transforms raw temporal data into a professional forensic timeline
suitable for:
1. Tribunal presentation (chronological narrative)
2. Gap analysis (identify suspicious periods)
3. Pattern detection (escalation, retaliation sequences)
4. Strategic planning (strengthen weak periods)

Cost: ZERO new AI calls - uses existing timeline extraction
Value: Transforms 24 events → Professional chronological reconstruction
Effort: ~8 hours implementation (including gap analysis logic)
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from evidence_toolkit.generators.base import BaseReportGenerator
from evidence_toolkit.core.models import TimelineEvent


class TimelineGenerator(BaseReportGenerator):
    """Generate chronological timeline reconstruction with gap analysis.

    Creates a professional forensic timeline from extracted temporal events,
    with visual presentation, gap analysis, and legal implications.

    Data Sources:
        - correlation_result.timeline_events: List[TimelineEvent]
        - correlation_result.temporal_sequences: List (pattern sequences)
        - correlation_result.timeline_gaps: List[str] (identified gaps)

    Output: timeline_reconstruction.md (professional Markdown report)

    Example:
        >>> generator = TimelineGenerator(case_summary, reports_dir)
        >>> if generator.has_data():
        ...     report_path = generator.generate()
        ...     # Creates: reports/timeline_reconstruction.md
    """

    def get_report_filename(self) -> str:
        """Return filename for timeline report."""
        return "timeline_reconstruction.md"

    def get_report_title(self) -> str:
        """Return human-readable report title."""
        return "Timeline Reconstruction"

    def has_data(self) -> bool:
        """Check if timeline data exists.

        Report is generated if timeline events are available.

        Returns:
            True if timeline events exist
        """
        correlation_result = self.case_summary.correlation_result

        if not correlation_result:
            return False

        timeline_events = correlation_result.timeline_events

        return bool(timeline_events and len(timeline_events) > 0)

    def generate(self) -> Path:
        """Generate the timeline reconstruction report.

        Creates a chronological timeline with events, gaps, and legal analysis.

        Returns:
            Path to generated report file

        Raises:
            Exception: If report generation fails
        """
        # Build report content
        content = self._build_header(subtitle="Chronological Event Reconstruction & Gap Analysis")

        # Add executive summary
        content += self._build_executive_summary()

        # Section 1: Visual Timeline
        content += self._build_visual_timeline_section()

        # Section 2: Detailed Events
        content += self._build_detailed_events_section()

        # Section 3: Timeline Gaps
        content += self._build_timeline_gaps_section()

        # Section 4: Temporal Patterns
        content += self._build_temporal_patterns_section()

        # Section 5: Legal Implications
        content += self._build_legal_implications_section()

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
        """Build executive summary of timeline."""
        correlation_result = self.case_summary.correlation_result

        timeline_events = correlation_result.timeline_events
        timeline_gaps = correlation_result.timeline_gaps if hasattr(correlation_result, 'timeline_gaps') else []

        content = "## Executive Summary\n\n"

        # Get date range
        if timeline_events:
            sorted_events = sorted(timeline_events, key=lambda e: e.timestamp)
            start_date = sorted_events[0].timestamp
            end_date = sorted_events[-1].timestamp
            span_days = (end_date - start_date).days

            content += f"**Timeline Span**: {start_date.strftime('%d %B %Y')} → {end_date.strftime('%d %B %Y')} ({span_days} days)\n\n"

        content += f"**Events Identified**: {len(timeline_events)}\n"
        content += f"**Timeline Gaps**: {len(timeline_gaps)}\n\n"

        # Event type breakdown
        event_types = {}
        for event in timeline_events:
            event_type = event.event_type
            event_types[event_type] = event_types.get(event_type, 0) + 1

        if event_types:
            content += "**Event Types**:\n"
            for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
                content += f"- {event_type.replace('_', ' ').title()}: {count}\n"
            content += "\n"

        # Risk assessment
        if timeline_gaps:
            content += "⚠️ **ATTENTION**: Timeline gaps detected - may indicate missing evidence or suspicious activity periods\n\n"

        content += "---\n\n"
        return content

    def _build_visual_timeline_section(self) -> str:
        """Build visual ASCII timeline."""
        correlation_result = self.case_summary.correlation_result
        timeline_events = correlation_result.timeline_events

        if not timeline_events:
            return ""

        content = "## 1. Visual Timeline\n\n"
        content += "```\n"

        # Sort events chronologically
        sorted_events = sorted(timeline_events, key=lambda e: e.timestamp)

        # Group by month for compact display
        monthly_groups = {}
        for event in sorted_events:
            month_key = event.timestamp.strftime('%Y-%m')
            if month_key not in monthly_groups:
                monthly_groups[month_key] = []
            monthly_groups[month_key].append(event)

        # Build timeline
        for month_key in sorted(monthly_groups.keys()):
            events = monthly_groups[month_key]
            month_label = datetime.strptime(month_key, '%Y-%m').strftime('%B %Y')

            content += f"\n{month_label}\n"
            content += "=" * len(month_label) + "\n"

            for event in events:
                day = event.timestamp.strftime('%d')
                desc_short = event.description[:60] + "..." if len(event.description) > 60 else event.description

                # Add risk indicator
                risk_indicator = ""
                if event.ai_classification:
                    legal_sig = event.ai_classification.get('legal_significance', '')
                    if legal_sig == 'high':
                        risk_indicator = " [!]"
                    elif legal_sig == 'critical':
                        risk_indicator = " [!!]"

                content += f"  {day}: {desc_short}{risk_indicator}\n"

        content += "\n```\n\n"
        content += "*Legend: [!] = High legal significance, [!!] = Critical event*\n\n"
        content += "---\n\n"
        return content

    def _build_detailed_events_section(self) -> str:
        """Build detailed chronological event list."""
        correlation_result = self.case_summary.correlation_result
        timeline_events = correlation_result.timeline_events

        if not timeline_events:
            return ""

        content = "## 2. Detailed Event Log\n\n"
        content += "Chronological listing of all identified events with evidence citations.\n\n"

        # Sort events
        sorted_events = sorted(timeline_events, key=lambda e: e.timestamp)

        for i, event in enumerate(sorted_events, 1):
            timestamp_str = event.timestamp.strftime('%d %B %Y, %H:%M' if event.timestamp.hour or event.timestamp.minute else '%d %B %Y')
            evidence_short = self._truncate_sha(event.evidence_sha256)

            content += f"### Event #{i}: {timestamp_str}\n\n"
            content += f"**Description**: {event.description}\n\n"
            content += f"**Source**: Evidence {evidence_short} ({event.evidence_type})\n"
            content += f"**Type**: {event.event_type.replace('_', ' ').title()}\n"
            content += f"**Confidence**: {self._format_percentage(event.confidence, decimals=0)}\n\n"

            # Add AI classification if available
            if event.ai_classification:
                ai_class = event.ai_classification

                if ai_class.get('legal_significance'):
                    content += f"**Legal Significance**: {ai_class['legal_significance'].upper()}\n"

                if ai_class.get('sentiment'):
                    content += f"**Sentiment**: {ai_class['sentiment'].title()}\n"

                risk_flags = ai_class.get('risk_flags', [])
                if risk_flags:
                    content += f"**Risk Indicators**: {', '.join(risk_flags)}\n"

                content += "\n"

                # Add context if available
                if ai_class.get('entity_context'):
                    content += f"**Context**: {ai_class['entity_context']}\n\n"

            content += "---\n\n"

        return content

    def _build_timeline_gaps_section(self) -> str:
        """Build timeline gaps analysis."""
        correlation_result = self.case_summary.correlation_result
        timeline_gaps = correlation_result.timeline_gaps if hasattr(correlation_result, 'timeline_gaps') else []
        timeline_events = correlation_result.timeline_events

        content = "## 3. Timeline Gaps Analysis\n\n"

        if not timeline_gaps:
            content += "✓ **No significant timeline gaps detected**.\n\n"
            content += "The timeline shows continuous activity with no suspicious periods of missing documentation.\n\n"
            content += "---\n\n"
            return content

        content += f"⚠️ **{len(timeline_gaps)} timeline gap(s) identified**.\n\n"
        content += "Timeline gaps represent periods with missing documentation or unexplained inactivity. "
        content += "These may indicate:\n"
        content += "- Missing evidence (lost emails, undocumented meetings)\n"
        content += "- Deliberate concealment of activity\n"
        content += "- Normal business lulls (holidays, etc.)\n\n"

        content += "### Identified Gaps\n\n"

        for i, gap in enumerate(timeline_gaps, 1):
            content += f"{i}. {gap}\n"

        content += "\n"

        # Gap severity assessment
        content += "### Gap Severity Assessment\n\n"

        if len(timeline_gaps) >= 3:
            content += "**HIGH CONCERN**: Multiple timeline gaps may indicate systematic evidence destruction or concealment.\n\n"
            content += "**Recommended Actions**:\n"
            content += "1. Issue document production requests for missing periods\n"
            content += "2. Depose witnesses about activities during gap periods\n"
            content += "3. Subpoena third-party records (IT logs, building access, etc.)\n"
            content += "4. Prepare adverse inference arguments for tribunal\n\n"
        elif len(timeline_gaps) >= 1:
            content += "**MODERATE CONCERN**: Timeline gaps require investigation.\n\n"
            content += "**Recommended Actions**:\n"
            content += "1. Request additional documentation for gap periods\n"
            content += "2. Interview witnesses about missing period activities\n"
            content += "3. Cross-reference with external records (calendars, meeting logs)\n\n"

        content += "---\n\n"
        return content

    def _build_temporal_patterns_section(self) -> str:
        """Build temporal patterns analysis."""
        correlation_result = self.case_summary.correlation_result
        temporal_sequences = correlation_result.temporal_sequences if hasattr(correlation_result, 'temporal_sequences') else []

        if not temporal_sequences:
            return ""

        content = "## 4. Temporal Patterns\n\n"
        content += f"**{len(temporal_sequences)} temporal pattern(s) identified** in event sequences.\n\n"

        content += "Temporal patterns reveal relationships between events over time, including:\n"
        content += "- Escalation sequences (increasing severity)\n"
        content += "- Retaliation patterns (adverse action following protected activity)\n"
        content += "- Cause-and-effect chains\n\n"

        for i, sequence in enumerate(temporal_sequences, 1):
            # Note: temporal_sequences structure depends on CorrelationAnalyzer implementation
            # This is a placeholder - adjust based on actual data structure
            content += f"### Pattern #{i}\n\n"

            if isinstance(sequence, dict):
                pattern_type = sequence.get('pattern_type', 'Unknown')
                description = sequence.get('description', 'No description')
                confidence = sequence.get('confidence', 0.0)

                content += f"**Type**: {pattern_type.title()}\n"
                content += f"**Description**: {description}\n"
                content += f"**Confidence**: {self._format_percentage(confidence, decimals=0)}\n\n"
            else:
                content += f"{sequence}\n\n"

        content += "---\n\n"
        return content

    def _build_legal_implications_section(self) -> str:
        """Build legal implications of timeline."""
        correlation_result = self.case_summary.correlation_result
        timeline_events = correlation_result.timeline_events
        timeline_gaps = correlation_result.timeline_gaps if hasattr(correlation_result, 'timeline_gaps') else []

        content = "## 5. Legal Implications\n\n"

        # Analyze high-risk events
        high_risk_events = []
        for event in timeline_events:
            if event.ai_classification:
                legal_sig = event.ai_classification.get('legal_significance', '')
                if legal_sig in ['high', 'critical']:
                    high_risk_events.append(event)

        if high_risk_events:
            content += "### High-Risk Events\n\n"
            content += f"**{len(high_risk_events)} event(s)** identified with high legal significance:\n\n"

            for event in high_risk_events[:5]:  # Show top 5
                timestamp_str = event.timestamp.strftime('%d %B %Y')
                content += f"- **{timestamp_str}**: {event.description}\n"

            if len(high_risk_events) > 5:
                content += f"- *(+{len(high_risk_events) - 5} additional high-risk events)*\n"

            content += "\n"

        # Timeline gap implications
        if timeline_gaps:
            content += "### Documentation Gap Implications\n\n"
            content += "Timeline gaps create legal vulnerabilities:\n\n"
            content += "1. **Adverse Inference Risk**: Tribunal may infer missing evidence is unfavorable\n"
            content += "2. **Discovery Obligations**: May trigger additional document production requests\n"
            content += "3. **Witness Credibility**: Gaps undermine witness testimony about events\n"
            content += "4. **Spoliation Concerns**: Intentional destruction may trigger sanctions\n\n"

        # Temporal patterns implications
        content += "### Temporal Analysis Value\n\n"
        content += "**For Claimant**:\n"
        content += "- Demonstrates chronological progression of adverse treatment\n"
        content += "- Establishes proximity between protected activity and retaliation\n"
        content += "- Highlights patterns of escalating hostility\n\n"

        content += "**For Respondent**:\n"
        content += "- Shows legitimate business reasons for actions\n"
        content += "- Demonstrates consistent treatment over time\n"
        content += "- Refutes claims of sudden or pretextual adverse action\n\n"

        content += "---\n\n"
        return content

    def _build_strategic_recommendations_section(self) -> str:
        """Build strategic recommendations based on timeline."""
        correlation_result = self.case_summary.correlation_result
        timeline_gaps = correlation_result.timeline_gaps if hasattr(correlation_result, 'timeline_gaps') else []
        timeline_events = correlation_result.timeline_events

        content = "## 6. Strategic Recommendations\n\n"

        # Count high-risk events
        high_risk_count = sum(1 for e in timeline_events if e.ai_classification and
                             e.ai_classification.get('legal_significance') in ['high', 'critical'])

        content += "### Immediate Actions\n\n"

        if timeline_gaps:
            content += "1. **Gap Investigation** (HIGH PRIORITY)\n"
            content += "   - Request additional documentation for missing periods\n"
            content += "   - Interview witnesses about activities during gaps\n"
            content += "   - Obtain third-party records (IT logs, calendars)\n\n"

        if high_risk_count >= 3:
            content += "2. **High-Risk Event Analysis**\n"
            content += f"   - {high_risk_count} high-risk events require detailed review\n"
            content += "   - Prepare witness statements for critical events\n"
            content += "   - Gather corroborating evidence for key dates\n\n"

        content += "3. **Timeline Presentation Preparation**\n"
        content += "   - Create visual timeline for tribunal (PowerPoint/exhibits)\n"
        content += "   - Prepare witness testimony to walk through key dates\n"
        content += "   - Cross-reference timeline with opposing party's version\n\n"

        content += "### Evidence Strengthening\n\n"
        content += "1. **Document Collection**\n"
        content += "   - Request employment records for timeline period\n"
        content += "   - Subpoena relevant third-party communications\n"
        content += "   - Obtain contemporaneous notes/diaries\n\n"

        content += "2. **Witness Preparation**\n"
        content += "   - Identify witnesses for each critical event\n"
        content += "   - Prepare chronological witness statements\n"
        content += "   - Address timeline gaps in witness testimony\n\n"

        content += "### Tribunal Strategy\n\n"
        content += "- **Opening Statement**: Use timeline to frame narrative\n"
        content += "- **Evidence Presentation**: Introduce documents chronologically\n"
        content += "- **Cross-Examination**: Challenge opposing timeline inconsistencies\n"
        content += "- **Closing Argument**: Emphasize pattern and progression\n\n"

        content += "---\n\n"

        # Footer
        content += "*This timeline reconstruction was generated by Evidence Toolkit v3.4. "
        content += "All dates and events should be verified against original evidence before tribunal use.*\n"

        return content

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    # No additional helper methods needed - using base class helpers
