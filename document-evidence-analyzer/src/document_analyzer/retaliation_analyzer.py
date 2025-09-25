"""Advanced retaliation-pattern analysis toolkit.

This module adapts the legacy retaliation analysis script into the
package so it can be reused programmatically or from the CLI.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


@dataclass
class RetaliationSummary:
    total_documents: int
    analysis_period_days: Optional[int]
    complaint_date: Optional[pd.Timestamp]
    suspension_date: Optional[pd.Timestamp]
    days_to_retaliation: Optional[int]
    chart_paths: Dict[str, Path]


class RetaliationAnalyzer:
    """Analyze communication timelines for retaliation patterns."""

    def __init__(
        self,
        data_dir: Path | str,
        output_dir: Optional[Path | str] = None,
        verbose: bool = True,
    ) -> None:
        self.data_dir = Path(data_dir)
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path.cwd() / "retaliation_analysis"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.verbose = verbose
        self.documents: List[Dict] = []
        self.timeline_df: Optional[pd.DataFrame] = None
        sns.set_palette("husl")

    # ------------------------------------------------------------------
    def run_full_analysis(
        self,
        file_pattern: str = "*.txt",
    ) -> RetaliationSummary:
        """Execute the complete retaliation analysis workflow."""

        self.load_documents(file_pattern=file_pattern)
        timeline_df = self.create_timeline_dataframe()
        if timeline_df.empty:
            raise ValueError("No dated documents found for retaliation analysis")

        escalation_stats = self.analyze_escalation_patterns()
        self.analyze_communication_frequency()
        sentiment_df = self.analyze_content_sentiment()
        events_df = self.identify_retaliation_timeline()

        chart_paths = self.generate_visualizations(sentiment_df, events_df)
        summary = self.generate_statistical_summary(sentiment_df, escalation_stats)
        summary.chart_paths = chart_paths
        return summary

    # ------------------------------------------------------------------
    def load_documents(self, file_pattern: str = "*.txt") -> List[Dict]:
        """Load text documents from disk and capture filename metadata."""
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory '{self.data_dir}' does not exist")

        self.documents = []
        for file_path in sorted(self.data_dir.glob(file_pattern)):
            if not file_path.is_file():
                continue
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            doc_info = self._parse_filename(file_path.name)
            doc_info.update(
                {
                    "content": content,
                    "filepath": file_path,
                    "word_count": len(content.split()),
                }
            )
            self.documents.append(doc_info)
            self._log(f"Loaded: {file_path.name}")

        if not self.documents:
            self._log("No documents matched the provided pattern")
        else:
            self._log(f"Total documents loaded: {len(self.documents)}")
        return self.documents

    # ------------------------------------------------------------------
    def _parse_filename(self, filename: str) -> Dict:
        parts = filename.replace(".txt", "").split("-")
        doc_info: Dict[str, object] = {
            "filename": filename,
            "date_str": None,
            "date": None,
            "doc_type": "UNKNOWN",
            "description": "",
            "participants": [],
        }

        if len(parts) >= 3:
            try:
                date_str = f"{parts[0]}-{parts[1]}-{parts[2]}"
                doc_info["date_str"] = date_str
                doc_info["date"] = pd.to_datetime(date_str, errors="raise")
            except Exception:
                pass

            if len(parts) >= 4:
                doc_info["doc_type"] = parts[3]

            if len(parts) >= 5:
                doc_info["description"] = parts[4]

            if len(parts) >= 6:
                last_segment = parts[-1]
                participants = last_segment.split("-") if "-" in last_segment else [last_segment]
                doc_info["participants"] = [p.strip() for p in participants if p.strip()]

        return doc_info

    # ------------------------------------------------------------------
    def create_timeline_dataframe(self) -> pd.DataFrame:
        """Aggregate document metadata into a chronological dataframe."""
        rows = []
        for doc in self.documents:
            if doc.get("date") is not None:
                rows.append(
                    {
                        "date": doc["date"],
                        "date_str": doc["date_str"],
                        "doc_type": doc["doc_type"],
                        "description": doc["description"],
                        "participants": doc["participants"],
                        "word_count": doc["word_count"],
                        "filename": doc["filename"],
                    }
                )

        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values("date").reset_index(drop=True)
            df["days_since_start"] = (df["date"] - df["date"].min()).dt.days
            df["month_year"] = df["date"].dt.to_period("M")
            df["year"] = df["date"].dt.year
            df["month"] = df["date"].dt.month

        self.timeline_df = df
        self._log(f"Timeline documents: {len(df)}")
        return df

    # ------------------------------------------------------------------
    def analyze_escalation_patterns(self) -> Dict[str, object]:
        if self.timeline_df is None or self.timeline_df.empty:
            raise ValueError("Timeline dataframe is empty. Run create_timeline_dataframe first.")

        df = self.timeline_df
        complaint_events = df[df["description"].str.contains("OriginalEmail|FairTreatment", case=False, na=False)]
        escalation_events = df[df["description"].str.contains("Escalate", case=False, na=False)]
        suspension_events = df[(df["doc_type"] == "LETTER") & df["description"].str.contains("Suspension", case=False, na=False)]

        first_complaint = complaint_events["date"].min() if not complaint_events.empty else None
        first_suspension = suspension_events["date"].min() if not suspension_events.empty else None
        days_to_suspension = None
        if first_complaint is not None and first_suspension is not None:
            days_to_suspension = (first_suspension - first_complaint).days

        self._log("=== Escalation Pattern Analysis ===")
        self._log(f"Initial complaints: {len(complaint_events)}")
        self._log(f"Escalations: {len(escalation_events)}")
        self._log(f"Suspensions: {len(suspension_events)}")
        if days_to_suspension is not None:
            self._log(
                f"Days from first complaint ({first_complaint.date()}) to suspension"
                f" ({first_suspension.date()}): {days_to_suspension}"
            )

        return {
            "complaint_events": complaint_events,
            "escalation_events": escalation_events,
            "suspension_events": suspension_events,
            "first_complaint": first_complaint,
            "first_suspension": first_suspension,
            "days_to_suspension": days_to_suspension,
        }

    # ------------------------------------------------------------------
    def analyze_communication_frequency(self) -> Tuple[pd.Series, pd.Series]:
        if self.timeline_df is None or self.timeline_df.empty:
            raise ValueError("Timeline dataframe is empty. Run create_timeline_dataframe first.")

        df = self.timeline_df
        monthly_counts = df.groupby("month_year").size()
        type_counts = df["doc_type"].value_counts()
        self._log("=== Communication Frequency ===")
        for month, count in monthly_counts.items():
            self._log(f"  {month}: {count} documents")
        for doc_type, count in type_counts.items():
            self._log(f"  {doc_type}: {count}")
        return monthly_counts, type_counts

    # ------------------------------------------------------------------
    def analyze_content_sentiment(self) -> pd.DataFrame:
        retaliation_keywords = [
            "suspension",
            "disciplinary",
            "misconduct",
            "investigation",
            "allegations",
            "gross misconduct",
            "unreasonable behaviour",
            "targeted",
            "unfair",
            "stressed",
            "frustrated",
            "mental toll",
        ]

        positive_keywords = [
            "award",
            "thank you",
            "well done",
            "appreciate",
            "great work",
            "hard work",
            "support",
            "helping",
        ]

        concern_keywords = [
            "safety",
            "hygiene",
            "contamination",
            "health",
            "concern",
            "blood",
            "debris",
            "dirty",
            "cleaning",
            "standards",
        ]

        results = []
        for doc in self.documents:
            content_lower = doc.get("content", "").lower()
            date = doc.get("date")
            if date is None:
                continue

            retaliation_score = sum(keyword in content_lower for keyword in retaliation_keywords)
            positive_score = sum(keyword in content_lower for keyword in positive_keywords)
            concern_score = sum(keyword in content_lower for keyword in concern_keywords)

            results.append(
                {
                    "filename": doc.get("filename"),
                    "date": date,
                    "doc_type": doc.get("doc_type"),
                    "retaliation_score": retaliation_score,
                    "positive_score": positive_score,
                    "concern_score": concern_score,
                    "word_count": doc.get("word_count"),
                }
            )

        sentiment_df = pd.DataFrame(results).sort_values("date").reset_index(drop=True)
        self._log("=== Content Sentiment Analysis ===")
        if not sentiment_df.empty:
            self._log(f"Average retaliation score: {sentiment_df['retaliation_score'].mean():.2f}")
            self._log(f"Average positive score: {sentiment_df['positive_score'].mean():.2f}")
            self._log(f"Average concern score: {sentiment_df['concern_score'].mean():.2f}")
        return sentiment_df

    # ------------------------------------------------------------------
    def identify_retaliation_timeline(self) -> pd.DataFrame:
        if self.timeline_df is None or self.timeline_df.empty:
            raise ValueError("Timeline dataframe is empty. Run create_timeline_dataframe first.")

        events = []
        for _, row in self.timeline_df.iterrows():
            description = str(row.get("description", "")).lower()
            doc_type = str(row.get("doc_type", "")).upper()

            event_type = "OTHER"
            if "award" in description or doc_type == "REWARDS":
                event_type = "POSITIVE_RECOGNITION"
            elif "originalemail" in description or "fairtreatment" in description:
                event_type = "INITIAL_COMPLAINT"
            elif "escalate" in description:
                event_type = "ESCALATION"
            elif "suspension" in description:
                event_type = "SUSPENSION"
            elif "fitnote" in description or "fit note" in description:
                event_type = "HEALTH_IMPACT"
            elif any(keyword in description for keyword in ["meeting", "followup", "follow-up"]):
                event_type = "MANAGEMENT_RESPONSE"

            events.append(
                {
                    "date": row["date"],
                    "event_type": event_type,
                    "description": row.get("description"),
                    "filename": row.get("filename"),
                }
            )

        events_df = pd.DataFrame(events).sort_values("date").reset_index(drop=True)
        self._log("=== Retaliation Timeline ===")
        for _, event in events_df.iterrows():
            self._log(
                f"{event['date'].date()} | {event['event_type']:<20} | {event['description']}"
            )
        return events_df

    # ------------------------------------------------------------------
    def generate_visualizations(
        self,
        sentiment_df: pd.DataFrame,
        events_df: Optional[pd.DataFrame] = None
    ) -> Dict[str, Path]:
        if self.timeline_df is None or self.timeline_df.empty:
            raise ValueError("Timeline dataframe is empty. Run create_timeline_dataframe first.")

        charts: Dict[str, Path] = {}
        df = self.timeline_df
        chart_path = self.output_dir / "retaliation_analysis_charts.png"
        detailed_path = self.output_dir / "retaliation_detailed_timeline.png"

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle("Workplace Retaliation Pattern Analysis", fontsize=16, fontweight="bold")

        ax1 = axes[0, 0]
        colors = {"EMAIL": "blue", "LETTER": "red", "REWARDS": "green"}
        for doc_type, subset in df.groupby("doc_type"):
            ax1.scatter(
                subset["date"],
                [doc_type] * len(subset),
                c=colors.get(doc_type, "gray"),
                label=doc_type,
                s=60,
                alpha=0.7,
            )
        ax1.set_title("Timeline of Communications by Type")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Document Type")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2 = axes[0, 1]
        monthly_counts = df.groupby("month_year").size()
        ax2.bar(monthly_counts.index.astype(str), monthly_counts.values, color="steelblue")
        ax2.set_title("Communication Frequency by Month")
        ax2.set_xlabel("Month-Year")
        ax2.set_ylabel("Number of Documents")
        ax2.tick_params(axis="x", rotation=45)

        ax3 = axes[1, 0]
        if not sentiment_df.empty:
            ax3.plot(
                sentiment_df["date"],
                sentiment_df["retaliation_score"],
                "ro-",
                label="Retaliation Score",
                linewidth=2,
            )
            ax3.plot(
                sentiment_df["date"],
                sentiment_df["concern_score"],
                "bo-",
                label="Concern Score",
                linewidth=2,
            )
            ax3.plot(
                sentiment_df["date"],
                sentiment_df["positive_score"],
                "go-",
                label="Positive Score",
                linewidth=2,
            )
        ax3.set_title("Content Sentiment Analysis Over Time")
        ax3.set_xlabel("Date")
        ax3.set_ylabel("Keyword Score")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        ax4 = axes[1, 1]
        type_counts = df["doc_type"].value_counts()
        ax4.pie(type_counts.values, labels=type_counts.index, autopct="%1.1f%%")
        ax4.set_title("Distribution of Document Types")

        plt.tight_layout()
        fig.savefig(chart_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        charts["overview"] = chart_path

        if events_df is None:
            events_df = self.identify_retaliation_timeline()
        fig2, ax = plt.subplots(figsize=(16, 8))
        color_map = {
            "POSITIVE_RECOGNITION": "green",
            "INITIAL_COMPLAINT": "orange",
            "ESCALATION": "red",
            "SUSPENSION": "darkred",
            "HEALTH_IMPACT": "purple",
            "MANAGEMENT_RESPONSE": "blue",
            "OTHER": "gray",
        }
        for idx, event in events_df.iterrows():
            color = color_map.get(event["event_type"], "gray")
            ax.scatter(event["date"], idx, c=color, s=100, alpha=0.8)
            ax.text(
                event["date"],
                idx + 0.1,
                str(event["description"])[:30] + ("..." if len(str(event["description"])) > 30 else ""),
                rotation=45,
                fontsize=8,
                ha="left",
            )

        legend_elements = [
            plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=color, markersize=10, label=etype)
            for etype, color in color_map.items()
            if etype in events_df["event_type"].unique()
        ]
        if legend_elements:
            ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc="upper left")

        ax.set_title("Detailed Timeline: Potential Retaliation Pattern", fontsize=14, fontweight="bold")
        ax.set_xlabel("Date")
        ax.set_ylabel("Event Sequence")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        fig2.savefig(detailed_path, dpi=300, bbox_inches="tight")
        plt.close(fig2)
        charts["detailed_timeline"] = detailed_path

        self._log(f"Charts saved to {chart_path} and {detailed_path}")
        return charts

    # ------------------------------------------------------------------
    def generate_statistical_summary(
        self,
        sentiment_df: pd.DataFrame,
        escalation_stats: Dict[str, object],
    ) -> RetaliationSummary:
        if self.timeline_df is None or self.timeline_df.empty:
            raise ValueError("Timeline dataframe is empty. Run create_timeline_dataframe first.")

        df = self.timeline_df
        analysis_period_days = None
        if not df.empty:
            analysis_period_days = int((df["date"].max() - df["date"].min()).days)

        first_complaint = escalation_stats.get("first_complaint")
        first_suspension = escalation_stats.get("first_suspension")
        days_to_retaliation = escalation_stats.get("days_to_suspension")

        if first_complaint is not None:
            pre = sentiment_df[sentiment_df["date"] < first_complaint]
            post = sentiment_df[sentiment_df["date"] >= first_complaint]
            self._log("=== Statistical Summary ===")
            self._log(f"Total documents: {len(df)}")
            self._log(f"Analysis period: {analysis_period_days} days")
            self._log(f"Pre-complaint retaliation score: {pre['retaliation_score'].mean():.2f}")
            self._log(f"Post-complaint retaliation score: {post['retaliation_score'].mean():.2f}")
        else:
            self._log("=== Statistical Summary ===")
            self._log(f"Total documents: {len(df)}")
            self._log(f"Analysis period: {analysis_period_days} days")

        return RetaliationSummary(
            total_documents=len(df),
            analysis_period_days=analysis_period_days,
            complaint_date=first_complaint,
            suspension_date=first_suspension,
            days_to_retaliation=days_to_retaliation,
            chart_paths={},
        )

    # ------------------------------------------------------------------
    def _log(self, message: str) -> None:
        if self.verbose:
            print(message)


def analyze_retaliation_case(
    data_dir: Path | str,
    output_dir: Optional[Path | str] = None,
    file_pattern: str = "*.txt",
    verbose: bool = True,
) -> RetaliationSummary:
    analyzer = RetaliationAnalyzer(data_dir=data_dir, output_dir=output_dir, verbose=verbose)
    return analyzer.run_full_analysis(file_pattern=file_pattern)
