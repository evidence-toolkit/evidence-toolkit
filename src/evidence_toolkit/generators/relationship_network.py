"""Relationship Network Generator - Entity connection mapping and key player analysis.

Generates a forensic report analyzing the relationship network between entities
identified in the evidence. Visualizes communication patterns, escalation chains,
and identifies key players by connection count.

Data source: overall_assessment['relationship_network'] (Dict)
Created by: Correlation analysis phase
Value: Network visualization helps identify witnesses, escalation chains, authority structures
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter

from evidence_toolkit.generators.base import BaseReportGenerator


class RelationshipNetworkGenerator(BaseReportGenerator):
    """Generate relationship network analysis from entity correlations.

    This generator creates a forensic report showing:
    - Entity connection mapping (who communicates with whom)
    - Key players identification (by connection count)
    - Communication flow patterns
    - Escalation chain analysis
    - Witness prioritization recommendations

    The analysis uses relationship data extracted from:
    - Email sender/recipient patterns
    - Mentioned entities in documents
    - Escalation patterns (employee → manager → executive)

    Example output sections:
    - Network Overview: Total entities, connections, relationship types
    - Key Players: Ranked by connection count with roles
    - Relationship Details: Source → Target connections with evidence
    - Network Insights: Centrality, isolation, escalation patterns
    - Investigation Recommendations: Witness interview priorities
    """

    def get_report_filename(self) -> str:
        """Return filename for relationship network report."""
        return "relationship_network_analysis.md"

    def get_report_title(self) -> str:
        """Return title for relationship network report."""
        return "Relationship Network Analysis"

    def has_data(self) -> bool:
        """Check if relationship network data exists.

        Returns:
            True if relationship_network exists and has relationships
        """
        network = self._safe_get('relationship_network')
        if not network or not isinstance(network, dict):
            return False

        relationships = network.get('relationships', [])
        return bool(relationships) and len(relationships) > 0

    def generate(self) -> Path:
        """Generate the relationship network analysis report.

        Returns:
            Path to the generated report file
        """
        # Extract network data
        network = self._safe_get('relationship_network', {})

        # Build report sections
        content = self._build_header(
            subtitle="Entity Connection Mapping & Key Player Identification"
        )
        content += self._build_executive_summary(network)
        content += self._build_network_overview(network)
        content += self._build_key_players_section(network)
        content += self._build_relationships_detail(network)
        content += self._build_network_insights(network)
        content += self._build_investigation_recommendations(network)

        # Write report
        report_path = self.output_dir / self.get_report_filename()
        report_path.write_text(content, encoding='utf-8')

        return report_path

    def _build_executive_summary(self, network: Dict[str, Any]) -> str:
        """Build executive summary of network analysis."""
        total_relationships = network.get('total_relationships', 0)
        unique_connections = network.get('unique_connections', 0)
        key_players = network.get('key_players', [])

        section = "\n## Executive Summary\n\n"
        section += f"Network analysis reveals **{total_relationships} documented relationships** "
        section += f"between **{unique_connections} unique entities**. "

        if key_players:
            top_player = key_players[0]
            section += f"**{top_player.get('name')}** emerges as the central figure "
            section += f"with **{top_player.get('connection_count', 0)} connections**. "

        # Analyze network structure
        if total_relationships < 3:
            section += "The limited network suggests isolated communications or a focused dispute. "
        elif total_relationships > 10:
            section += "The extensive network indicates complex organizational dynamics. "

        section += "\n\n"
        section += "**Forensic Significance**: Relationship mapping reveals escalation chains, "
        section += "communication patterns, and potential witnesses. Key players should be "
        section += "prioritized for interview and document production.\n\n"

        return section

    def _build_network_overview(self, network: Dict[str, Any]) -> str:
        """Build network overview statistics."""
        section = "\n## Network Overview\n\n"

        total_rels = network.get('total_relationships', 0)
        unique_conns = network.get('unique_connections', 0)
        rel_type_dist = network.get('relationship_type_distribution', {})

        section += "### Network Metrics\n\n"
        section += f"- **Total Relationships**: {total_rels}\n"
        section += f"- **Unique Connections**: {unique_conns}\n"
        section += f"- **Network Density**: {self._calculate_density(total_rels, unique_conns)}\n"
        section += "\n"

        # Relationship type distribution
        if rel_type_dist:
            section += "### Relationship Type Distribution\n\n"
            section += "| Relationship Type | Count | Percentage |\n"
            section += "|-------------------|-------|------------|\n"

            for rel_type, count in sorted(rel_type_dist.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_rels * 100) if total_rels > 0 else 0
                section += f"| {rel_type.replace('_', ' ').title()} | {count} | {percentage:.1f}% |\n"

            section += "\n"

        return section

    def _calculate_density(self, total_rels: int, unique_conns: int) -> str:
        """Calculate and describe network density."""
        if unique_conns < 2:
            return "N/A (insufficient connections)"

        # Max possible connections in undirected network: n(n-1)/2
        # For directed network (emails): n(n-1)
        max_possible = unique_conns * (unique_conns - 1)
        density = (total_rels / max_possible) if max_possible > 0 else 0

        density_pct = density * 100

        if density_pct < 10:
            desc = "Sparse (isolated communications)"
        elif density_pct < 30:
            desc = "Moderate (selective communications)"
        elif density_pct < 60:
            desc = "Dense (active communications)"
        else:
            desc = "Very Dense (extensive interactions)"

        return f"{density_pct:.1f}% - {desc}"

    def _build_key_players_section(self, network: Dict[str, Any]) -> str:
        """Build key players section with connection counts."""
        section = "\n## Key Players\n\n"
        section += "Entities ranked by connection count (centrality in communication network):\n\n"

        key_players = network.get('key_players', [])

        if not key_players:
            section += "_No key players identified._\n\n"
            return section

        section += "| Rank | Name | Connections | Role/Context |\n"
        section += "|------|------|-------------|---------------|\n"

        for rank, player in enumerate(key_players, 1):
            name = player.get('name', 'Unknown')
            conn_count = player.get('connection_count', 0)
            role = player.get('role', 'Role not specified')

            # Truncate long roles
            if len(role) > 60:
                role = role[:57] + "..."

            section += f"| {rank} | **{name}** | {conn_count} | {role} |\n"

        section += "\n"

        # Add forensic interpretation
        section += "### Forensic Interpretation\n\n"

        if len(key_players) >= 1:
            top_player = key_players[0]
            section += f"- **{top_player.get('name')}** is the network hub with "
            section += f"{top_player.get('connection_count', 0)} connections. "
            section += "This individual should be prioritized for witness interviews.\n"

        if len(key_players) >= 3:
            section += f"- Top 3 players account for the majority of network activity. "
            section += "Focus investigation on these individuals' communications.\n"

        # Check for isolated individuals (connection_count == 1)
        isolated = [p for p in key_players if p.get('connection_count', 0) == 1]
        if isolated:
            section += f"- **{len(isolated)} isolated individual(s)** with single connections. "
            section += "May represent peripheral witnesses or external parties.\n"

        section += "\n"

        return section

    def _build_relationships_detail(self, network: Dict[str, Any]) -> str:
        """Build detailed relationship listing."""
        section = "\n## Relationship Details\n\n"
        section += "Complete mapping of documented relationships:\n\n"

        relationships = network.get('relationships', [])

        if not relationships:
            section += "_No relationships documented._\n\n"
            return section

        # Group by relationship type
        by_type: Dict[str, List[Dict]] = {}
        for rel in relationships:
            rel_type = rel.get('relationship_type', 'other')
            if rel_type not in by_type:
                by_type[rel_type] = []
            by_type[rel_type].append(rel)

        # Display each type
        for rel_type, rels in sorted(by_type.items()):
            section += f"### {rel_type.replace('_', ' ').title()} ({len(rels)})\n\n"

            for rel in rels:
                source = rel.get('source', 'Unknown')
                target = rel.get('target', 'Unknown')
                context = rel.get('context', 'No context')
                evidence_sha = rel.get('evidence_sha256', '')

                section += f"- **{source}** → **{target}**\n"
                section += f"  - Context: {context}\n"

                if evidence_sha:
                    section += f"  - Evidence: `{self._truncate_sha(evidence_sha)}`\n"

                section += "\n"

        return section

    def _build_network_insights(self, network: Dict[str, Any]) -> str:
        """Build network insights and patterns section."""
        section = "\n## Network Insights\n\n"

        relationships = network.get('relationships', [])
        key_players = network.get('key_players', [])

        # Analyze communication flow
        section += "### Communication Flow Analysis\n\n"

        # Count sources and targets
        sources = [r.get('source') for r in relationships if r.get('source')]
        targets = [r.get('target') for r in relationships if r.get('target')]

        source_counts = Counter(sources)
        target_counts = Counter(targets)

        # Find top senders/receivers
        if source_counts:
            top_sender = source_counts.most_common(1)[0]
            section += f"- **Top Sender**: {top_sender[0]} ({top_sender[1]} outbound communications)\n"

        if target_counts:
            top_receiver = target_counts.most_common(1)[0]
            section += f"- **Top Receiver**: {top_receiver[0]} ({top_receiver[1]} inbound communications)\n"

        section += "\n"

        # Check for escalation patterns
        section += "### Escalation Patterns\n\n"

        escalations = [r for r in relationships if r.get('relationship_type') == 'escalation']

        if escalations:
            section += f"Detected **{len(escalations)} escalation event(s)**:\n\n"
            for esc in escalations:
                section += f"- {esc.get('source')} escalated to {esc.get('target')}\n"
            section += "\n"
        else:
            section += "_No explicit escalation patterns detected in relationship data._\n\n"
            section += "**Note**: Escalations may exist in email content but not captured as relationships.\n\n"

        # Network centrality analysis
        section += "### Centrality Analysis\n\n"

        if key_players and len(key_players) >= 2:
            top_player = key_players[0]
            top_conn = top_player.get('connection_count', 0)
            avg_conn = sum(p.get('connection_count', 0) for p in key_players) / len(key_players)

            section += f"- **Network Hub**: {top_player.get('name')} ({top_conn} connections)\n"
            section += f"- **Average Connections**: {avg_conn:.1f} per player\n"

            if top_conn > avg_conn * 2:
                section += f"- **Assessment**: {top_player.get('name')} is a dominant hub "
                section += "(>2x average connections). Critical witness for case.\n"

            section += "\n"

        return section

    def _build_investigation_recommendations(self, network: Dict[str, Any]) -> str:
        """Build investigation recommendations based on network analysis."""
        section = "\n## Investigation Recommendations\n\n"

        key_players = network.get('key_players', [])
        relationships = network.get('relationships', [])

        section += "### Witness Interview Priorities\n\n"

        if key_players:
            section += "Recommend interviewing witnesses in the following priority order:\n\n"

            for rank, player in enumerate(key_players[:5], 1):  # Top 5
                name = player.get('name')
                conn_count = player.get('connection_count', 0)
                role = player.get('role', 'Unknown role')

                section += f"**Priority {rank}: {name}**\n"
                section += f"- Network centrality: {conn_count} connections\n"
                section += f"- Context: {role}\n"
                section += f"- Rationale: "

                if rank == 1:
                    section += "Network hub - likely has comprehensive knowledge of events\n"
                elif conn_count > 3:
                    section += "High connection count - key witness with broad exposure\n"
                else:
                    section += "Connected to primary actors - corroboration potential\n"

                section += "\n"

        # Document production recommendations
        section += "### Document Production Recommendations\n\n"

        # Identify relationship gaps
        if key_players and len(key_players) >= 2:
            section += "Request additional communications between:\n\n"

            # Check for missing connections between top players
            top_names = [p.get('name') for p in key_players[:3]]
            existing_pairs = set()

            for rel in relationships:
                source = rel.get('source')
                target = rel.get('target')
                if source in top_names and target in top_names:
                    existing_pairs.add((source, target))

            # Find missing pairs
            missing_count = 0
            for i, name1 in enumerate(top_names):
                for name2 in top_names[i+1:]:
                    if (name1, name2) not in existing_pairs and (name2, name1) not in existing_pairs:
                        section += f"- {name1} ↔ {name2} (no documented communication)\n"
                        missing_count += 1

            if missing_count == 0:
                section += "_All top players have documented communications._\n"

            section += "\n"

        # Strategic recommendations
        section += "### Strategic Analysis\n\n"

        section += "**Network Structure Implications**:\n\n"

        total_rels = network.get('total_relationships', 0)

        if total_rels < 5:
            section += "- **Sparse network** suggests isolated dispute or limited evidence. "
            section += "Focus on deepening existing relationships through witness statements.\n"
        elif total_rels > 15:
            section += "- **Complex network** indicates organizational-wide issues. "
            section += "Consider systemic failure analysis beyond individual relationships.\n"
        else:
            section += "- **Moderate network** shows focused dispute with clear actors. "
            section += "Relationships map should guide targeted investigation.\n"

        section += "\n"

        return section


# Export for package-level import
__all__ = ['RelationshipNetworkGenerator']
