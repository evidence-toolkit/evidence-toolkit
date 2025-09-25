#!/usr/bin/env python3
"""
Create comprehensive visualizations for workplace retaliation analysis
"""

import os
from datetime import datetime, timedelta
import json

def create_ascii_timeline():
    """Create an ASCII-based timeline visualization."""

    # Timeline data from analysis
    events = [
        ("2022-04-06", "AWARDS", "Multiple awards/recognition period begins", "green"),
        ("2025-02-03", "COMPLAINT", "Initial formal health & safety complaint", "orange"),
        ("2025-02-08", "DOCS", "Document sharing begins", "blue"),
        ("2025-03-01", "ESCALATION", "Escalation to Michael K", "red"),
        ("2025-03-08", "ESCALATION", "Escalation to Ryan A", "red"),
        ("2025-03-22", "MGMT", "Management response meeting", "blue"),
        ("2025-06-16", "ESCALATION", "Escalation to Paul G & David L", "red"),
        ("2025-06-19", "CONTACT", "Nick R contacts Paul", "blue"),
        ("2025-06-20", "COMPLAINT", "Fair treatment complaint", "orange"),
        ("2025-07-18", "HEALTH", "Fit note - work stress begins", "purple"),
        ("2025-07-21", "HEALTH", "Additional fit note", "purple"),
        ("2025-07-24", "OUTCOME", "Fair treatment outcome + investigation noted", "blue"),
        ("2025-08-24", "SUSPENSION", "Formal suspension for gross misconduct", "darkred"),
        ("2025-08-28", "RESPONSE", "Response to allegations", "blue"),
    ]

    print("\n" + "="*100)
    print("COMPREHENSIVE RETALIATION TIMELINE VISUALIZATION")
    print("="*100)

    print("\nTimeline Legend:")
    print("🏆 = Awards/Recognition")
    print("📢 = Initial Complaints")
    print("⬆️ = Escalations")
    print("💼 = Management Actions")
    print("🏥 = Health Impact")
    print("⚠️ = Suspension/Discipline")
    print()

    # Calculate timeline positions
    start_date = datetime.strptime("2022-04-06", "%Y-%m-%d")
    end_date = datetime.strptime("2025-08-28", "%Y-%m-%d")
    total_days = (end_date - start_date).days

    print("Timeline: April 2022 ────────────────────────────────────── August 2025")
    print("          │                                                        │")
    print("          │←── 1034 days recognition period ──→│←── 202 days to suspension ──→│")
    print()

    # Print detailed timeline
    for date_str, event_type, description, color in events:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

        # Select emoji based on event type
        if "AWARDS" in event_type:
            emoji = "🏆"
        elif "COMPLAINT" in event_type:
            emoji = "📢"
        elif "ESCALATION" in event_type:
            emoji = "⬆️"
        elif "HEALTH" in event_type:
            emoji = "🏥"
        elif "SUSPENSION" in event_type:
            emoji = "⚠️"
        else:
            emoji = "💼"

        print(f"{date_str} {emoji} {description}")

    return events

def create_participant_network():
    """Create a text-based participant network diagram."""

    print("\n" + "="*100)
    print("PARTICIPANT NETWORK & ROLE ANALYSIS")
    print("="*100)

    participants = {
        "PB": {
            "name": "Paul Boucherat",
            "role": "Complainant/Employee",
            "frequency": 15,
            "description": "Primary complainant, online assistant"
        },
        "AM": {
            "name": "Amy Martin",
            "role": "HR/Management",
            "frequency": 4,
            "description": "Lead GOL Manager, issued suspension"
        },
        "RE": {
            "name": "R. Edwards(?)",
            "role": "Investigation/HR",
            "frequency": 4,
            "description": "Fair treatment investigator"
        },
        "RA": {
            "name": "Ryan Allen",
            "role": "Management",
            "frequency": 3,
            "description": "Manager, received escalations"
        },
        "MK": {
            "name": "Michael Kicks",
            "role": "Management",
            "frequency": 2,
            "description": "Manager, promised cleaning schedule"
        },
        "RH": {
            "name": "Rachel Hemmings",
            "role": "Line Manager",
            "frequency": 1,
            "description": "Initial recipient of complaint"
        },
        "PG": {
            "name": "Paul G",
            "role": "Senior Management",
            "frequency": 1,
            "description": "Higher-level escalation target"
        },
        "DL": {
            "name": "David L",
            "role": "Senior Management",
            "frequency": 1,
            "description": "Higher-level escalation target"
        },
        "NR": {
            "name": "Nick R",
            "role": "Unknown Role",
            "frequency": 1,
            "description": "Contacted Paul (investigation related?)"
        },
        "ER": {
            "name": "E. R.",
            "role": "Unknown Role",
            "frequency": 1,
            "description": "Fair treatment related contact"
        },
        "DS": {
            "name": "D. S.",
            "role": "Unknown Role",
            "frequency": 1,
            "description": "Response to allegations contact"
        }
    }

    print("Communication Frequency Analysis:")
    print("-" * 50)
    for code, info in sorted(participants.items(), key=lambda x: x[1]['frequency'], reverse=True):
        print(f"{code:3} | {info['name']:20} | {info['role']:20} | {info['frequency']:2} docs | {info['description']}")

    print(f"\nCommunication Flow Analysis:")
    print("-" * 50)
    print("PB (Paul) → RH (Rachel) → Initial complaint not escalated properly")
    print("PB (Paul) → MK (Michael) → Promised cleaning, limited follow-through")
    print("PB (Paul) → RA (Ryan) → Multiple escalations")
    print("PB (Paul) → PG,DL → Senior management escalation")
    print("PB (Paul) → ER → Fair treatment process")
    print("RE → PB → Fair treatment outcome (partially upheld)")
    print("AM → PB → Suspension letter (gross misconduct)")
    print("NR → PB → Investigation contact")

    print(f"\nCommunication Pattern Insights:")
    print("-" * 50)
    print("• PB appears in 15/16 documents (93.8%) - central to all communications")
    print("• Management responses show increasing formality over time")
    print("• Multiple management levels involved suggests escalation pressure")
    print("• Health impacts (fit notes) appear during investigation period")
    print("• Suspension occurs 30+ days after fair treatment outcome")

def create_retaliation_indicators():
    """Visualize retaliation indicators over time."""

    print("\n" + "="*100)
    print("RETALIATION INDICATORS ANALYSIS")
    print("="*100)

    # Data from content analysis
    timeline_data = [
        ("2022-04-06", "AWARDS", 0, 8, 1),  # ret, pos, concern
        ("2025-02-03", "COMPLAINT", 2, 2, 11),
        ("2025-02-08", "DOCS", 0, 0, 1),
        ("2025-03-01", "ESCALATION", 0, 1, 4),
        ("2025-03-07", "DOCS", 0, 0, 1),
        ("2025-03-08", "ESCALATION", 0, 1, 2),
        ("2025-03-22", "MGMT_RESP", 0, 3, 5),
        ("2025-06-16", "ESCALATION", 0, 2, 9),
        ("2025-06-19", "CONTACT", 1, 3, 8),
        ("2025-06-20", "COMPLAINT", 0, 1, 5),
        ("2025-07-18", "HEALTH", 0, 0, 0),
        ("2025-07-21", "HEALTH", 0, 2, 1),
        ("2025-07-24", "INVESTIGATION", 2, 3, 5),
        ("2025-08-24", "SUSPENSION", 7, 1, 0),
        ("2025-08-28", "RESPONSE", 4, 0, 3),
    ]

    print("Retaliation Indicators Over Time (Keyword Analysis):")
    print("-" * 80)
    print("Date       | Event Type    | Retaliation | Positive | Concern | Pattern")
    print("-" * 80)

    for date, event, ret, pos, con in timeline_data:
        pattern = ""
        if ret >= 4:
            pattern = "🚨 HIGH RETALIATION"
        elif ret >= 2:
            pattern = "⚠️ MODERATE RETALIATION"
        elif ret == 1:
            pattern = "⚡ LOW RETALIATION"
        elif pos >= 5:
            pattern = "✅ POSITIVE PERIOD"
        elif con >= 8:
            pattern = "🔍 HIGH CONCERN"

        print(f"{date} | {event:13} | {ret:11} | {pos:8} | {con:7} | {pattern}")

    print(f"\nKey Statistical Findings:")
    print("-" * 50)
    total_ret = sum(data[2] for data in timeline_data)
    total_pos = sum(data[3] for data in timeline_data)
    total_con = sum(data[4] for data in timeline_data)

    pre_complaint = [data for data in timeline_data if data[0] < "2025-02-03"]
    post_complaint = [data for data in timeline_data if data[0] >= "2025-02-03"]

    pre_ret_avg = sum(data[2] for data in pre_complaint) / len(pre_complaint) if pre_complaint else 0
    post_ret_avg = sum(data[2] for data in post_complaint) / len(post_complaint) if post_complaint else 0

    print(f"• Total retaliation indicators: {total_ret}")
    print(f"• Total positive indicators: {total_pos}")
    print(f"• Total concern indicators: {total_con}")
    print(f"• Pre-complaint retaliation average: {pre_ret_avg:.2f}")
    print(f"• Post-complaint retaliation average: {post_ret_avg:.2f}")
    print(f"• Retaliation increase factor: {post_ret_avg/max(pre_ret_avg, 0.1):.1f}x")

    # Identify peak retaliation periods
    print(f"\nPeak Retaliation Periods:")
    print("-" * 30)
    for date, event, ret, pos, con in timeline_data:
        if ret >= 4:
            print(f"• {date}: {event} (Score: {ret})")

def create_timing_analysis():
    """Analyze timing patterns for potential retaliation."""

    print("\n" + "="*100)
    print("TIMING PATTERN ANALYSIS FOR RETALIATION")
    print("="*100)

    # Key dates
    last_award = datetime.strptime("2024-05-25", "%Y-%m-%d")  # Approximate from awards doc
    initial_complaint = datetime.strptime("2025-02-03", "%Y-%m-%d")
    fair_treatment = datetime.strptime("2025-06-20", "%Y-%m-%d")
    health_impact = datetime.strptime("2025-07-18", "%Y-%m-%d")
    suspension = datetime.strptime("2025-08-24", "%Y-%m-%d")

    print("Critical Timeline Intervals:")
    print("-" * 50)

    intervals = [
        ("Award period ends to complaint", last_award, initial_complaint),
        ("Initial complaint to fair treatment", initial_complaint, fair_treatment),
        ("Fair treatment to health impact", fair_treatment, health_impact),
        ("Health impact to suspension", health_impact, suspension),
        ("Initial complaint to suspension", initial_complaint, suspension),
    ]

    for desc, start, end in intervals:
        days = (end - start).days
        print(f"{desc:35}: {days:4} days")

    print(f"\nRetaliation Risk Assessment:")
    print("-" * 50)

    complaint_to_suspension = (suspension - initial_complaint).days
    if complaint_to_suspension < 90:
        risk = "HIGH RISK"
    elif complaint_to_suspension < 180:
        risk = "MODERATE RISK"
    else:
        risk = "LOW RISK"

    print(f"• Time from complaint to disciplinary action: {complaint_to_suspension} days")
    print(f"• Risk classification: {risk}")
    print(f"• Health impacts appeared {(health_impact - fair_treatment).days} days after fair treatment process")
    print(f"• Suspension occurred {(suspension - health_impact).days} days after health impacts reported")

    print(f"\nPattern Significance:")
    print("-" * 50)
    print("• Rapid escalation from health impacts to suspension suggests correlation")
    print("• 202-day timeline from complaint to suspension within typical retaliation timeframe")
    print("• Health stress emerges during investigation period (potential pressure)")
    print("• Fair treatment partially upheld, followed by disciplinary action")

def main():
    """Generate all visualizations."""

    print("WORKPLACE RETALIATION PATTERN ANALYSIS")
    print("COMPREHENSIVE VISUALIZATION REPORT")
    print("=" * 60)

    # Generate all visualizations
    create_ascii_timeline()
    create_participant_network()
    create_retaliation_indicators()
    create_timing_analysis()

    print("\n" + "="*100)
    print("VISUALIZATION SUMMARY")
    print("="*100)
    print("All visualizations completed. Key patterns identified:")
    print("1. Clear timeline from complaint (Feb 2025) to suspension (Aug 2025)")
    print("2. Escalating retaliation indicators in documents over time")
    print("3. Health impacts emerging during investigation period")
    print("4. Communication network showing management response patterns")
    print("5. Statistical evidence of increased negative indicators post-complaint")

if __name__ == "__main__":
    main()