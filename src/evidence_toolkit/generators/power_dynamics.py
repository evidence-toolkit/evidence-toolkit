"""Power Dynamics Generator - Email authority hierarchy and deference analysis.

Generates a forensic report analyzing power dynamics in email communications,
including authority levels, deference scoring, and dominant topic identification.

Data source: EmailThreadAnalysis.participants (EmailParticipant models)
Created by: Email analysis phase (OpenAI Responses API)
Value: Reveals organizational hierarchy, authority relationships, communication patterns
Status: FUTURE IMPLEMENTATION - requires aggregation layer

Note: Power dynamics data EXISTS in individual email analysis files (deference_score,
authority_level, dominant_topics) but is not currently aggregated into overall_assessment.
This generator is a placeholder for Phase 4 when aggregation is implemented.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict

from evidence_toolkit.generators.base import BaseReportGenerator


class PowerDynamicsGenerator(BaseReportGenerator):
    """Generate power dynamics analysis from email thread participants.

    This generator creates a forensic report showing:
    - Email authority hierarchy (executive/management/employee/external)
    - Deference score analysis per participant
    - Dominant topics by participant
    - Communication pattern classification (professional/escalating/hostile)
    - Temporal deference trends
    - Legal implications for employment claims

    The analysis reveals power imbalances, organizational hierarchy, and
    communication control patterns that are forensically significant for
    workplace disputes, discrimination claims, and employment tribunals.

    Example output sections:
    - Authority Hierarchy: Participants ranked by organizational level
    - Deference Analysis: Who defers to whom (score 0.0-1.0)
    - Communication Control: Topics dominated by each participant
    - Pattern Evolution: How power dynamics changed over time
    - Legal Implications: Employment law significance

    Status: PLACEHOLDER - Full implementation requires aggregation layer
    """

    def get_report_filename(self) -> str:
        """Return filename for power dynamics report."""
        return "power_dynamics_analysis.md"

    def get_report_title(self) -> str:
        """Return title for power dynamics report."""
        return "Power Dynamics Analysis"

    def has_data(self) -> bool:
        """Check if power dynamics data is available.

        Returns:
            True if power_dynamics data exists in overall_assessment
        """
        power_dynamics = self._safe_get('power_dynamics')
        if not power_dynamics or not isinstance(power_dynamics, dict):
            return False

        # Check if we have participant data
        participants = power_dynamics.get('top_participants', [])
        return bool(participants) and len(participants) > 0

    def generate(self) -> Path:
        """Generate the power dynamics analysis report.

        Returns:
            Path to the generated report file
        """
        # Extract power dynamics data
        power_data = self._safe_get('power_dynamics', {})

        # Build report sections
        content = self._build_header(
            subtitle="Email Authority Hierarchy & Deference Analysis"
        )
        content += self._build_executive_summary(power_data)
        content += self._build_authority_hierarchy(power_data)
        content += self._build_deference_analysis(power_data)
        content += self._build_methodology_section()
        content += self._build_forensic_value_section()

        # Write report
        report_path = self.output_dir / self.get_report_filename()
        report_path.write_text(content, encoding='utf-8')

        return report_path

    def _build_executive_summary(self, power_data: Dict[str, Any]) -> str:
        """Build executive summary of power dynamics."""
        section = "\n## Executive Summary\n\n"

        participants = power_data.get('top_participants', [])
        participant_count = power_data.get('participant_count', len(participants))

        section += f"Email thread analysis reveals **{participant_count} participants** "
        section += f"across **{power_data.get('total_messages_analyzed', 0)} messages**.\n\n"

        if participants:
            # Identify authority levels
            by_authority = defaultdict(list)
            for p in participants:
                authority = p.get('authority', 'unknown')
                by_authority[authority].append(p)

            section += "**Authority Distribution**:\n"
            for level in ['executive', 'management', 'employee', 'external']:
                count = len(by_authority.get(level, []))
                if count > 0:
                    section += f"- {level.title()}: {count}\n"

            section += "\n"

            # Analyze deference patterns
            avg_deference = sum(p.get('avg_deference', 0.5) for p in participants) / len(participants)

            section += "**Communication Dynamics**:\n"
            if avg_deference < 0.4:
                section += "- Overall tone: Assertive and directive\n"
            elif avg_deference > 0.6:
                section += "- Overall tone: Deferential and cautious\n"
            else:
                section += "- Overall tone: Balanced and professional\n"

            section += "\n"

        section += "**Forensic Significance**: Power dynamics analysis reveals organizational hierarchy, "
        section += "communication control patterns, and potential evidence of intimidation or retaliation in "
        section += "workplace disputes.\n\n"

        return section

    def _build_status_notice(self) -> str:
        """Build notice explaining current implementation status."""
        section = "\n## Notice: Feature Pending Aggregation Layer\n\n"
        section += "Power dynamics analysis **exists in individual email analysis files** "
        section += "but is not yet aggregated into the case summary. This report is a placeholder.\n\n"

        section += "**Current Status**:\n\n"
        section += "- ✅ Email analysis captures: authority_level, deference_score, dominant_topics\n"
        section += "- ✅ Pydantic models defined: EmailParticipant, EmailThreadAnalysis\n"
        section += "- ❌ Aggregation layer: Not implemented (pending Phase 4)\n"
        section += "- ❌ Report generation: Waiting for aggregated data\n\n"

        section += "**When aggregation is implemented**, this report will include:\n\n"
        section += "- Authority hierarchy table (executive → management → employee)\n"
        section += "- Deference scoring per participant (0.0=dominant, 1.0=deferential)\n"
        section += "- Dominant topics analysis (who controlled which conversations)\n"
        section += "- Temporal power shift detection\n"
        section += "- Employment law implications\n\n"

        return section

    def _build_methodology_section(self) -> str:
        """Build methodology section explaining power dynamics analysis."""
        section = "\n## Power Dynamics Analysis Methodology\n\n"

        section += "### What is Power Dynamics Analysis?\n\n"
        section += "Power dynamics analysis examines authority relationships and communication patterns "
        section += "in email evidence to reveal organizational hierarchy, dominance, and deference.\n\n"

        section += "### Data Collection (AI-Powered)\n\n"
        section += "For each email thread, OpenAI Responses API analyzes:\n\n"

        section += "1. **Authority Level Classification**:\n"
        section += "   - **Executive**: C-level, directors, senior leadership\n"
        section += "   - **Management**: Managers, supervisors, team leads\n"
        section += "   - **Employee**: Individual contributors, staff\n"
        section += "   - **External**: Clients, vendors, third parties\n\n"

        section += "2. **Deference Score** (0.0 - 1.0):\n"
        section += "   - **0.0-0.3**: Highly dominant (controlling, directive language)\n"
        section += "   - **0.4-0.6**: Neutral (balanced, collegial communication)\n"
        section += "   - **0.7-1.0**: Highly deferential (submissive, apologetic language)\n\n"

        section += "3. **Dominant Topics**:\n"
        section += "   - Subjects/themes each participant drove or controlled\n"
        section += "   - Topics where participant's input was determinative\n"
        section += "   - Conversations initiated by participant\n\n"

        section += "4. **Communication Pattern** (thread-level):\n"
        section += "   - **Professional**: Respectful, business-appropriate\n"
        section += "   - **Escalating**: Increasing tension, stakes rising\n"
        section += "   - **Hostile**: Aggressive, confrontational tone\n"
        section += "   - **Retaliatory**: Response to complaint or challenge\n\n"

        return section

    def _build_forensic_value_section(self) -> str:
        """Build section explaining forensic value of power dynamics analysis."""
        section = "\n## Forensic Value of Power Dynamics Analysis\n\n"

        section += "### Why Power Dynamics Matter in Legal Cases\n\n"

        section += "**1. Employment Tribunal Evidence**:\n\n"
        section += "Power dynamics analysis is **directly relevant** to:\n\n"
        section += "- **Unfair Dismissal**: Was employee treated respectfully or dominated?\n"
        section += "- **Discrimination**: Did authority dynamics differ by protected characteristic?\n"
        section += "- **Whistleblowing (PIDA)**: Did power imbalance suppress disclosure?\n"
        section += "- **Constructive Dismissal**: Was workplace made intolerable through power abuse?\n\n"

        section += "**2. Deference Score as Evidence**:\n\n"
        section += "Deference patterns reveal:\n\n"
        section += "- **Asymmetric power**: Employee highly deferential (0.8+) to manager (0.2-)\n"
        section += "- **Power shift**: Deference decreasing over time = breakdown in authority\n"
        section += "- **Equality issues**: Different deference for same-level employees\n"
        section += "- **Intimidation**: Unusually high deference may indicate fear\n\n"

        section += "**3. Dominant Topics Analysis**:\n\n"
        section += "Shows who controlled the narrative:\n\n"
        section += "- Manager dominated grievance process = procedural control\n"
        section += "- Employee dominated safety concerns = protected disclosure\n"
        section += "- Executive silenced discussion = potential suppression\n\n"

        section += "**4. Communication Pattern Trends**:\n\n"
        section += "- **Professional → Escalating**: Relationship deterioration evidence\n"
        section += "- **Escalating → Hostile**: Potential hostile work environment\n"
        section += "- **Neutral → Retaliatory**: Response to complaint (victimization)\n\n"

        section += "### Legal Precedents\n\n"
        section += "UK employment tribunals consider communication patterns:\n\n"
        section += "- **Tone and manner** in email exchanges (House of Lords in Dunnachie v Kingston)\n"
        section += "- **Power imbalances** as context for constructive dismissal\n"
        section += "- **Organizational hierarchy** in vicarious liability claims\n"
        section += "- **Pattern of treatment** over isolated incidents\n\n"

        return section

    def _build_implementation_roadmap(self) -> str:
        """Build roadmap for full implementation."""
        section = "\n## Implementation Roadmap\n\n"

        section += "### Phase 4: Aggregation Layer (Required)\n\n"

        section += "**File**: `src/evidence_toolkit/analyzers/correlation.py`\n\n"

        section += "Add aggregation function:\n\n"
        section += "```python\n"
        section += "def _aggregate_power_dynamics(self, evidence_items: List[UnifiedAnalysis]) -> Dict:\n"
        section += "    \"\"\"Aggregate EmailParticipant data from email evidence.\"\"\"\n"
        section += "    participants_data = []\n"
        section += "    \n"
        section += "    for evidence in evidence_items:\n"
        section += "        if evidence.evidence_type == 'email':\n"
        section += "            email_analysis = evidence.analysis_result.get('email_thread')\n"
        section += "            if email_analysis and 'participants' in email_analysis:\n"
        section += "                participants_data.extend(email_analysis['participants'])\n"
        section += "    \n"
        section += "    # Aggregate by person\n"
        section += "    by_person = defaultdict(lambda: {...})\n"
        section += "    # Calculate averages, trends, etc.\n"
        section += "    \n"
        section += "    return {\n"
        section += "        'participants': [...],\n"
        section += "        'authority_hierarchy': [...],\n"
        section += "        'deference_matrix': {...},\n"
        section += "        'communication_patterns': {...}\n"
        section += "    }\n"
        section += "```\n\n"

        section += "**Add to overall_assessment**: `assessment['power_dynamics'] = self._aggregate_power_dynamics(evidence_items)`\n\n"

        section += "### Phase 5: Report Generation\n\n"

        section += "Once aggregation is complete, implement report sections:\n\n"
        section += "1. `_build_authority_hierarchy()` - Rank participants by authority\n"
        section += "2. `_build_deference_analysis()` - Show who defers to whom\n"
        section += "3. `_build_dominant_topics()` - Topic control per participant\n"
        section += "4. `_build_temporal_trends()` - Power shifts over time\n"
        section += "5. `_build_legal_implications()` - Employment law significance\n\n"

        section += "**Estimated effort**: 8-10 hours (5h aggregation + 5h report generation)\n\n"

        return section

    # Future implementation methods (for when aggregation is complete):

    def _build_authority_hierarchy(self, power_data: Dict[str, Any]) -> str:
        """Build authority hierarchy table.

        Args:
            power_data: Aggregated power dynamics data

        Returns:
            Formatted markdown section
        """
        section = "\n## Authority Hierarchy\n\n"
        section += "Participants ranked by organizational authority level:\n\n"

        participants = power_data.get('top_participants', [])

        # Group by authority level
        by_authority = defaultdict(list)
        for p in participants:
            authority = p.get('authority', 'unknown')
            by_authority[authority].append(p)

        # Display hierarchy
        for level in ['executive', 'management', 'employee', 'external']:
            people = by_authority.get(level, [])
            if people:
                section += f"### {level.title()} ({len(people)})\n\n"
                for person in people:
                    name = person.get('participant')
                    email = person.get('email')
                    avg_deference = person.get('avg_deference', 0.5)
                    messages = person.get('messages', 0)
                    section += f"- **{name}** ({email})\n"
                    section += f"  - Deference score: {avg_deference:.2f} "
                    section += f"({'assertive' if avg_deference < 0.4 else 'deferential' if avg_deference > 0.6 else 'balanced'})\n"
                    section += f"  - Messages: {messages}\n"
                section += "\n"

        return section

    def _build_deference_analysis(self, power_data: Dict[str, Any]) -> str:
        """Build deference analysis section.

        Args:
            power_data: Aggregated power dynamics data

        Returns:
            Formatted markdown section
        """
        section = "\n## Deference Analysis\n\n"

        participants = power_data.get('top_participants', [])

        if not participants:
            section += "_No deference data available._\n\n"
            return section

        section += "### Deference Score Interpretation\n\n"
        section += "Deference scores range from 0.0 (highly dominant/controlling) to 1.0 (highly deferential):\n\n"
        section += "- **0.0-0.3**: Assertive, directive, controlling language\n"
        section += "- **0.4-0.6**: Neutral, balanced, professional communication\n"
        section += "- **0.7-1.0**: Deferential, cautious, apologetic language\n\n"

        section += "### Participant Deference Scores\n\n"
        section += "| Participant | Authority | Deference | Messages | Interpretation |\n"
        section += "|-------------|-----------|-----------|----------|----------------|\n"

        for p in participants:
            name = p.get('participant')
            authority = p.get('authority', 'unknown').title()
            deference = p.get('avg_deference', 0.5)
            messages = p.get('messages', 0)

            if deference < 0.4:
                interp = "Assertive/Directive"
            elif deference > 0.6:
                interp = "Deferential/Cautious"
            else:
                interp = "Balanced/Professional"

            section += f"| {name} | {authority} | {deference:.2f} | {messages} | {interp} |\n"

        section += "\n"

        # Analyze power imbalances
        section += "### Power Dynamic Insights\n\n"

        # Find authority mismatches
        for p in participants:
            authority = p.get('authority')
            deference = p.get('avg_deference', 0.5)

            if authority == 'employee' and deference < 0.4:
                section += f"- ⚠️ **{p.get('participant')}** (employee) shows assertive communication (deference {deference:.2f}). "
                section += "May indicate confidence or potential conflict.\n"

            if authority == 'management' and deference > 0.6:
                section += f"- ⚠️ **{p.get('participant')}** (management) shows deferential communication (deference {deference:.2f}). "
                section += "Unusual for management role.\n"

        if not any(True for _ in participants):
            section += "_No significant power dynamic anomalies detected._\n"

        section += "\n"

        return section


# Export for package-level import
__all__ = ['PowerDynamicsGenerator']
