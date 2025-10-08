"""
Evidence Toolkit v1 Web Dashboard

Quick-start dashboard for viewing client packages.
Run: python -m document_analyzer.web_dashboard /path/to/client_package
"""

import json
from pathlib import Path
from typing import Optional
import sys

import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go


class ClientPackageDashboard:
    """Interactive dashboard for evidence toolkit client packages"""

    def __init__(self, package_path: Path):
        self.package_path = Path(package_path)
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            title="Evidence Toolkit Viewer"
        )

        # Load package data
        self.metadata = self._load_metadata()
        self.evidence_catalog = self._load_evidence_catalog()
        self.correlation_analysis = self._load_correlations()

        self._setup_layout()

    def _load_metadata(self) -> dict:
        """Load package_metadata.json"""
        metadata_file = self.package_path / "package_metadata.json"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Package metadata not found: {metadata_file}")

        with open(metadata_file, 'r') as f:
            return json.load(f)

    def _load_evidence_catalog(self) -> dict:
        """Load evidence_catalog/evidence_catalog.json"""
        catalog_file = self.package_path / "evidence_catalog" / "evidence_catalog.json"
        if catalog_file.exists():
            with open(catalog_file, 'r') as f:
                return json.load(f)
        return {}

    def _load_correlations(self) -> Optional[dict]:
        """Load correlations/correlation_analysis.json"""
        corr_file = self.package_path / "correlations" / "correlation_analysis.json"
        if corr_file.exists():
            with open(corr_file, 'r') as f:
                return json.load(f)
        return None

    def _setup_layout(self):
        """Setup dashboard layout"""

        case_id = self.metadata.get('package_info', {}).get('case_id', 'Unknown')
        evidence_count = self.metadata.get('package_info', {}).get('evidence_count', 0)

        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1([
                        "🔍 Evidence Toolkit Viewer",
                        html.Small(f" - {case_id}", className="text-muted ms-3")
                    ]),
                    html.P(
                        f"Generated: {self.metadata.get('package_info', {}).get('created', 'Unknown')}",
                        className="text-muted"
                    )
                ])
            ], className="mb-4"),

            # Summary Cards
            dbc.Row([
                dbc.Col(self._create_metric_card(
                    "Total Evidence",
                    str(evidence_count),
                    "📁",
                    "primary"
                ), width=3),
                dbc.Col(self._create_metric_card(
                    "Entity Correlations",
                    str(self.metadata.get('analysis_summary', {}).get('entity_correlations', 0)),
                    "🔗",
                    "success"
                ), width=3),
                dbc.Col(self._create_metric_card(
                    "Timeline Events",
                    str(self.metadata.get('analysis_summary', {}).get('timeline_events', 0)),
                    "📅",
                    "info"
                ), width=3),
                dbc.Col(self._create_metric_card(
                    "Risk Flags",
                    str(self.metadata.get('analysis_summary', {}).get('total_risk_flags', 0)),
                    "⚠️",
                    "warning"
                ), width=3)
            ], className="mb-4"),

            # Main Content Tabs
            dbc.Tabs([
                dbc.Tab(label="📊 Overview", tab_id="overview"),
                dbc.Tab(label="📁 Evidence Catalog", tab_id="evidence"),
                dbc.Tab(label="🔗 Correlations", tab_id="correlations"),
                dbc.Tab(label="📄 Reports", tab_id="reports"),
            ], id="tabs", active_tab="overview"),

            html.Div(id="tab-content", className="mt-4")

        ], fluid=True, className="p-4")

        # Callbacks
        @self.app.callback(
            Output("tab-content", "children"),
            Input("tabs", "active_tab")
        )
        def render_tab_content(active_tab):
            if active_tab == "overview":
                return self._render_overview_tab()
            elif active_tab == "evidence":
                return self._render_evidence_tab()
            elif active_tab == "correlations":
                return self._render_correlations_tab()
            elif active_tab == "reports":
                return self._render_reports_tab()
            return html.Div("Select a tab")

    def _create_metric_card(self, title: str, value: str, icon: str, color: str):
        """Create a summary metric card"""
        return dbc.Card([
            dbc.CardBody([
                html.H2(icon, className="text-center mb-2"),
                html.H3(value, className="text-center mb-2"),
                html.P(title, className="text-center text-muted mb-0")
            ])
        ], color=color, outline=True)

    def _render_overview_tab(self):
        """Render overview tab with charts"""

        # Evidence type distribution pie chart
        evidence_types = self.metadata.get('package_info', {}).get('evidence_types', [])
        type_counts = {}
        for item in self.evidence_catalog.get('evidence_inventory', []):
            etype = item.get('evidence_type', 'unknown')
            type_counts[etype] = type_counts.get(etype, 0) + 1

        pie_fig = go.Figure(data=[go.Pie(
            labels=list(type_counts.keys()),
            values=list(type_counts.values()),
            hole=0.4,
            marker=dict(colors=['#3498db', '#e74c3c', '#f39c12', '#9b59b6'])
        )])
        pie_fig.update_layout(
            title="Evidence Type Distribution",
            height=400
        )

        # Legal significance gauge
        significance_map = {'low': 25, 'medium': 50, 'high': 75, 'critical': 100}
        overall_sig = self.metadata.get('analysis_summary', {}).get('overall_legal_significance', 'medium')
        sig_value = significance_map.get(overall_sig, 50)

        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sig_value,
            title={'text': "Overall Legal Significance"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#3498db"},
                'steps': [
                    {'range': [0, 25], 'color': "#95a5a6"},
                    {'range': [25, 50], 'color': "#f1c40f"},
                    {'range': [50, 75], 'color': "#e67e22"},
                    {'range': [75, 100], 'color': "#e74c3c"}
                ]
            }
        ))
        gauge_fig.update_layout(height=400)

        return dbc.Row([
            dbc.Col([
                dcc.Graph(figure=pie_fig)
            ], width=6),
            dbc.Col([
                dcc.Graph(figure=gauge_fig)
            ], width=6)
        ])

    def _render_evidence_tab(self):
        """Render evidence catalog as table"""

        evidence_items = self.evidence_catalog.get('evidence_inventory', [])

        if not evidence_items:
            return html.Div("No evidence catalog found", className="alert alert-warning")

        # Create table rows
        table_rows = []
        for item in evidence_items:
            confidence = item.get('analysis_confidence')
            conf_badge = self._create_confidence_badge(confidence) if confidence else "-"

            risk_flags = item.get('risk_flags', [])
            risk_badges = [
                dbc.Badge(flag, color="danger", className="me-1")
                for flag in risk_flags
            ] if risk_flags else [html.Span("-")]

            table_rows.append(html.Tr([
                html.Td(item.get('filename', 'Unknown')[:50]),
                html.Td(dbc.Badge(item.get('evidence_type', 'unknown'), color="info")),
                html.Td(f"{item.get('file_size_bytes', 0):,} bytes"),
                html.Td(conf_badge),
                html.Td(risk_badges),
                html.Td(item.get('sha256', '')[:16] + "...")
            ]))

        table = dbc.Table([
            html.Thead(html.Tr([
                html.Th("Filename"),
                html.Th("Type"),
                html.Th("Size"),
                html.Th("Confidence"),
                html.Th("Risk Flags"),
                html.Th("SHA-256")
            ])),
            html.Tbody(table_rows)
        ], striped=True, hover=True, responsive=True)

        return dbc.Row([
            dbc.Col([
                html.H3(f"Evidence Catalog ({len(evidence_items)} items)"),
                table
            ])
        ])

    def _create_confidence_badge(self, confidence: float) -> dbc.Badge:
        """Create a colored badge for confidence score"""
        if confidence >= 0.9:
            color = "success"
        elif confidence >= 0.8:
            color = "info"
        elif confidence >= 0.7:
            color = "warning"
        else:
            color = "danger"

        return dbc.Badge(f"{confidence:.2f}", color=color)

    def _render_correlations_tab(self):
        """Render entity correlations"""

        if not self.correlation_analysis:
            return html.Div("No correlation analysis found", className="alert alert-warning")

        # Simple list view of top entities
        entity_correlations = self.correlation_analysis.get('entity_correlations', [])

        if not entity_correlations:
            return html.Div("No entity correlations found", className="alert alert-info")

        # Sort by occurrence count
        top_entities = sorted(
            entity_correlations,
            key=lambda x: x.get('occurrence_count', 0),
            reverse=True
        )[:20]

        entity_cards = []
        for entity in top_entities:
            entity_cards.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H5(entity.get('entity_name', 'Unknown')),
                        html.P([
                            dbc.Badge(entity.get('entity_type', 'unknown'), color="primary", className="me-2"),
                            dbc.Badge(f"{entity.get('occurrence_count', 0)} occurrences", color="secondary")
                        ]),
                        html.Small(f"Avg Confidence: {entity.get('confidence_average', 0):.2f}", className="text-muted")
                    ])
                ], className="mb-3")
            )

        return dbc.Row([
            dbc.Col([
                html.H3("Top Entity Correlations"),
                html.Div(entity_cards)
            ])
        ])

    def _render_reports_tab(self):
        """Render available reports"""

        reports_dir = self.package_path / "reports"
        documentation_dir = self.package_path / "documentation"

        available_files = []

        if reports_dir.exists():
            for report_file in reports_dir.glob("*"):
                available_files.append({
                    'name': report_file.name,
                    'path': report_file,
                    'size': report_file.stat().st_size,
                    'type': 'Report'
                })

        if documentation_dir.exists():
            for doc_file in documentation_dir.glob("*"):
                available_files.append({
                    'name': doc_file.name,
                    'path': doc_file,
                    'size': doc_file.stat().st_size,
                    'type': 'Documentation'
                })

        if not available_files:
            return html.Div("No reports or documentation found", className="alert alert-warning")

        file_list = []
        for file_info in available_files:
            file_list.append(
                dbc.ListGroupItem([
                    html.Div([
                        html.H5(file_info['name']),
                        html.P([
                            dbc.Badge(file_info['type'], color="primary", className="me-2"),
                            html.Small(f"{file_info['size']:,} bytes", className="text-muted")
                        ], className="mb-0")
                    ])
                ])
            )

        return dbc.Row([
            dbc.Col([
                html.H3("Available Reports & Documentation"),
                dbc.ListGroup(file_list)
            ])
        ])

    def run(self, debug: bool = True, port: int = 8050):
        """Start the dashboard server"""
        print(f"\n{'='*60}")
        print(f"Evidence Toolkit Dashboard")
        print(f"{'='*60}")
        print(f"Package: {self.package_path.name}")
        print(f"Case ID: {self.metadata.get('package_info', {}).get('case_id', 'Unknown')}")
        print(f"\n🌐 Dashboard running at: http://localhost:{port}")
        print(f"{'='*60}\n")

        self.app.run(debug=debug, port=port, host='0.0.0.0')


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python -m document_analyzer.web_dashboard <client_package_path>")
        print("\nExample:")
        print("  python -m document_analyzer.web_dashboard ./client_packages/WORKPLACE-2024-001_analysis_package_20251002_113539")
        sys.exit(1)

    package_path = Path(sys.argv[1])

    if not package_path.exists():
        print(f"Error: Package path does not exist: {package_path}")
        sys.exit(1)

    try:
        dashboard = ClientPackageDashboard(package_path)
        dashboard.run()
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
