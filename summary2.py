#!/usr/bin/env python3
"""Case Summary Generator - v3.0 (refactor: same behavior, less code)."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict
from pydantic import BaseModel, Field

from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.core.models import CorrelationAnalysis, EvidenceSummary, CaseSummary
from evidence_toolkit.analyzers.correlation import CorrelationAnalyzer


# ------------------------- Pydantic response models -------------------------

class ExecutiveSummaryResponse(BaseModel):
    executive_summary: str
    key_findings: List[str] = Field(default_factory=list)
    legal_implications: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    confidence_overall: float = Field(..., ge=0.0, le=1.0)
    risk_assessment: str


class ChunkSummaryResponse(BaseModel):
    chunk_summary: str
    key_entities: List[str] = Field(default_factory=list)
    key_findings: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)


class EnhancedExecutiveSummary(BaseModel):
    executive_summary: str
    key_findings: List[str] = Field(default_factory=list)
    tribunal_probability: float = Field(..., ge=0.0, le=1.0)
    financial_exposure_summary: str
    claim_strength_summary: str
    immediate_actions: List[str] = Field(default_factory=list)
    settlement_recommendation: str = "Not assessed"
    evidence_gaps: List[str] = Field(default_factory=list)
    confidence_overall: float = Field(..., ge=0.0, le=1.0)
    enhancement_applied: bool = True


# ------------------------------ Utilities -----------------------------------

def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None


def _analysis_paths(derived_dir: Path, sha256: str) -> Tuple[Path, Path]:
    base = derived_dir / f"sha256={sha256}"
    return base / "analysis.v1.json", base / "metadata.json"


def _ai_parse(client, model: str, sys_prompt: str, user: str, schema):
    resp = client.responses.parse(
        model=model,
        input=[{"role": "system", "content": sys_prompt},
               {"role": "user", "content": user}],
        text_format=schema,
    )
    if resp.status == "completed" and resp.output_parsed:
        return resp.output_parsed
    if resp.status == "incomplete":
        raise Exception(f"incomplete: {resp.incomplete_details}")
    if (resp.output and resp.output[0].content and
            resp.output[0].content[0].type == "refusal"):
        raise Exception(f"refused: {resp.output[0].content[0].refusal}")
    raise Exception("unknown error")


# --------------------------- Summary Generator ------------------------------

class SummaryGenerator:
    def __init__(self, storage: EvidenceStorage, openai_client=None, case_type: str = "generic"):
        self.storage = storage
        self.correlation_analyzer = CorrelationAnalyzer(storage, openai_client=openai_client, verbose=True)
        self.openai_client = openai_client
        self.ai_enabled = openai_client is not None
        self.case_type = case_type.lower()

    # ---- Public API ----

    def generate_case_summary(self, case_id: str) -> CaseSummary:
        corr = self.correlation_analyzer.analyze_case_correlations(case_id)
        if corr.evidence_count == 0:
            raise ValueError(f"No evidence found for case ID: {case_id}")

        evidence_summaries = self._create_evidence_summaries(case_id)
        overall = self._calculate_overall_assessment(evidence_summaries, corr)
        evidence_types = list({s.evidence_type for s in evidence_summaries})

        cs = CaseSummary(
            case_id=case_id,
            generation_timestamp=datetime.now(),
            evidence_count=len(evidence_summaries),
            evidence_types=evidence_types,
            evidence_summaries=evidence_summaries,
            correlation_result=corr,
            overall_assessment=overall,
        )

        if self.ai_enabled:
            try:
                print("   🔬 Generating forensic executive summary...")
                forensic = self._generate_ai_executive_summary(cs)
                print("   ✨ Enhancing summary with tribunal probability & financial estimates...")
                enhanced = self._enhance_executive_summary(forensic, corr)

                cs.executive_summary = enhanced.executive_summary
                oa = cs.overall_assessment
                oa.update({
                    "ai_key_findings": enhanced.key_findings,
                    "ai_confidence": enhanced.confidence_overall,
                    "enhancement_applied": enhanced.enhancement_applied,
                    "tribunal_probability": enhanced.tribunal_probability,
                    "financial_exposure_summary": enhanced.financial_exposure_summary,
                    "claim_strength_summary": enhanced.claim_strength_summary,
                    "immediate_actions": enhanced.immediate_actions,
                    "settlement_recommendation": enhanced.settlement_recommendation,
                    "evidence_gaps": enhanced.evidence_gaps,
                    "_forensic_summary": forensic.executive_summary,
                    "_forensic_legal_implications": forensic.legal_implications,
                    "_forensic_recommended_actions": forensic.recommended_actions,
                    "_forensic_risk_assessment": forensic.risk_assessment,
                })
            except Exception as e:
                print(f"⚠️  AI executive summary generation failed: {e}")

        return cs

    def export_summary_to_json(self, case_summary: CaseSummary, output_path: Path) -> bool:
        try:
            data = case_summary.model_dump(mode="json")
            if not isinstance(data.get("generation_timestamp"), str):
                data["generation_timestamp"] = case_summary.generation_timestamp.isoformat()
            if case_summary.correlation_result:
                data["correlation_analysis"] = case_summary.correlation_result.model_dump(mode="json")
                data.pop("correlation_result", None)
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting case summary: {e}")
            return False

    def format_summary_report(self, case_summary: CaseSummary) -> str:
        cs = case_summary
        oa = cs.overall_assessment
        L = []
        L += [
            "=" * 80,
            f"FORENSIC EVIDENCE ANALYSIS: {cs.case_id}",
            "=" * 80,
            f"Generated: {cs.generation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Evidence analyzed: {cs.evidence_count} items | Legal significance: {oa['overall_legal_significance'].upper()}",
            "",
            "=" * 80,
            "STRATEGIC ANALYSIS",
            "=" * 80,
            "",
        ]
        if cs.executive_summary:
            L += ["🔍 EXECUTIVE SUMMARY", "-" * 80, cs.executive_summary, ""]
        if oa.get("ai_key_findings"):
            L += ["💡 KEY FINDINGS", "-" * 80]
            L += [f"{i}. {f}" for i, f in enumerate(oa["ai_key_findings"], 1)]
            L.append("")

        if oa.get("enhancement_applied"):
            L += ["⚖️  LEGAL RISK ASSESSMENT", "-" * 30]
            L.append(f"Tribunal success probability: {oa.get('tribunal_probability', 0):.0%}")
            financial = oa.get("financial_exposure", {})
            if financial and "total_range" in financial:
                L.append(f"Estimated financial exposure: {financial.get('total_range', 'Not assessed')}")
                for k in ("basic_award", "compensatory", "injury_to_feelings"):
                    if k in financial:
                        L.append(f"  - {k.replace('_',' ').title()}: {financial[k]}")
            claim_strength = oa.get("claim_strength", {})
            if claim_strength:
                L += ["", "Claim strength breakdown:"]
                for t, s in claim_strength.items():
                    if t != "note":
                        L.append(f"  • {t}: {s}")
            if oa.get("immediate_actions"):
                L += ["", "Recommended immediate actions:"]
                L += [f"  • {a}" for a in oa["immediate_actions"]]
            settlement = oa.get("settlement_range", {})
            if settlement and settlement.get("min", 0) > 0:
                L += ["", f"Settlement recommendation: £{settlement['min']:,} - £{settlement['max']:,}", ""]
            L.append("")

        if oa.get("immediate_actions"):
            L += ["🎯 RECOMMENDED ACTIONS", "-" * 80]
            L += [f"{i}. {a}" for i, a in enumerate(oa["immediate_actions"], 1)]
            L.append("")

        if "quoted_statements" in oa:
            qs = oa["quoted_statements"]
            L += ["💬 QUOTED STATEMENTS", "-" * 80,
                  f"Total: {qs['total_statements']} statements from {qs['people_quoted']} people across {qs['documents_with_quotes']} documents", ""]
            for p in qs["quoted_statements"][:5]:
                L += [f"• {p['person']} ({p['role']})",
                      f"  {p['statement_count']} statement(s) - Sentiment: {p['dominant_sentiment']}"]
                if p["has_risk_indicators"]:
                    L.append(f"  Risk indicators: {', '.join(p['risk_types'][:3])}")
                for s in p["statements"][:2]:
                    risk = f" [RISK: {', '.join(s['risk_flags'][:2])}]" if s["risk_flags"] else ""
                    L.append(f"  → \"{s['text'][:120]}...\"{risk}")
                L.append("")

        if "communication_patterns" in oa:
            cp = oa["communication_patterns"]
            L += ["📧 EMAIL COMMUNICATION PATTERNS", "-" * 80,
                  f"Emails analyzed: {cp['email_count']}",
                  f"Dominant pattern: {cp['dominant_pattern'].upper()}",
                  f"Risk level: {cp['risk_level'].upper()}", "",
                  "Pattern distribution:",
                  f"  • Professional: {cp['professional_count']} emails",
                  f"  • Escalating: {cp['escalating_count']} emails",
                  f"  • Hostile/Retaliatory: {cp['hostile_or_retaliatory_count']} emails", ""]

        if "relationship_network" in oa:
            rn = oa["relationship_network"]
            L += ["🔗 RELATIONSHIP NETWORK", "-" * 80,
                  f"Total connections: {rn['total_relationships']} | Unique pairs: {rn['unique_connections']}", "",
                  "Connection types: Email={0} | Escalation={1} | Other={2}".format(
                      rn['relationship_type_distribution']['email_communication'],
                      rn['relationship_type_distribution']['escalation'],
                      rn['relationship_type_distribution']['other']), "",
                  "Key players:"]
            for p in rn["key_players"][:8]:
                role = f" ({p['role']})" if p.get("role") and p["role"] != "unknown" else ""
                L.append(f"  • {p['name']}{role} - {p['connection_count']} connection(s)")
            L.append("")

        if "image_ocr" in oa:
            o = oa["image_ocr"]
            L += ["🖼️  IMAGE OCR ANALYSIS", "-" * 80,
                  f"Images with text: {o['total_images_with_text']} ({o['text_extraction_rate']:.0%}) | High-value: {o['high_evidence_value_count']} | Medium: {o['medium_evidence_value_count']}"]
            if o["people_present_count"] > 0:
                L.append(f"Images with people: {o['people_present_count']}")
            if o["timestamps_visible_count"] > 0:
                L.append(f"Images with timestamps: {o['timestamps_visible_count']}")
            if o.get("object_categories"):
                obj = ', '.join([f"{c} {k}" for k, c in list(o["object_categories"].items())[:5]])
                L += [f"Objects detected: {obj}", ""]
            if o["images_with_text"]:
                L += ["Sample extractions:"]
                for img in o["images_with_text"][:3]:
                    rel = f" - {img['legal_relevance_notes']}" if img.get("legal_relevance_notes") else ""
                    L += [f"  • {img['filename']} [{img['evidence_value'].upper()}]{rel}",
                          f"    \"{img['detected_text'][:80]}...\""]
                L.append("")

        # Appendix
        L += ["", "=" * 80, "APPENDIX: SUPPORTING DOCUMENTATION", "=" * 80,
              "The following sections contain detailed information about each piece",
              "of evidence, entity correlations, and timeline reconstruction.",
              "This serves as supporting documentation for the analysis above.", "",
              "📁 EVIDENCE ANALYSIS", "-" * 30]
        for i, s in enumerate(cs.evidence_summaries, 1):
            t = s.document_type.upper() if s.document_type else s.evidence_type.upper()
            L += [f"{i}. {s.filename} ({t})",
                  f"   SHA256: {s.sha256[:16]}...",
                  f"   Size: {s.file_size:,} bytes"]
            if s.analysis_confidence:
                L.append(f"   Confidence: {s.analysis_confidence:.2f}")
            if s.legal_significance:
                L.append(f"   Legal significance: {s.legal_significance}")
            if s.risk_flags:
                L.append(f"   Risk flags: {', '.join(s.risk_flags)}")
            L += ["   Key findings:", *[f"     • {f}" for f in s.key_findings], ""]

        if cs.correlation_result.entity_correlations:
            L += ["🔗 ENTITY CORRELATIONS", "-" * 30]
            for c in cs.correlation_result.entity_correlations:
                L += [f"• {c.entity_name} ({c.entity_type})",
                      f"  Appears in {c.occurrence_count} evidence pieces",
                      f"  Average confidence: {c.confidence_average:.2f}"]
            L.append("")

        if cs.correlation_result.timeline_events:
            L += ["⏰ TIMELINE", "-" * 30]
            for e in cs.correlation_result.timeline_events[:10]:
                L.append(f"{e.timestamp.strftime('%Y-%m-%d %H:%M')} - {e.description}")
            L.append("")

        return "\n".join(L)

    # ---- Internals ----

    def _create_evidence_summaries(self, case_id: str) -> List[EvidenceSummary]:
        summaries: List[EvidenceSummary] = []
        for evidence_dir in self.storage.derived_dir.glob("sha256=*"):
            a_path = evidence_dir / "analysis.v1.json"
            m_path = evidence_dir / "metadata.json"
            if not (a_path.exists() and m_path.exists()):
                continue

            analysis = _read_json(a_path)
            metadata = _read_json(m_path)
            if not analysis or not metadata:
                continue

            case_ids = analysis.get("case_ids") or ([analysis["case_id"]] if analysis.get("case_id") else [])
            if case_id not in case_ids:
                continue

            sha256 = evidence_dir.name.replace("sha256=", "")
            e_type = analysis.get("evidence_type")

            key_findings, conf, legal_sig, risk_flags = self._extract_key_findings(e_type, analysis)
            doc_type = (analysis.get("document_analysis") or {}).get("document_type") if e_type == "document" else None

            summaries.append(EvidenceSummary(
                sha256=sha256,
                evidence_type=e_type,
                filename=metadata["filename"],
                file_size=metadata["file_size"],
                analysis_confidence=conf,
                key_findings=key_findings,
                legal_significance=legal_sig,
                risk_flags=risk_flags,
                document_type=doc_type,
            ))
        return summaries

    def _extract_key_findings(self, e_type: str, analysis: Dict[str, Any]) -> Tuple[List[str], Optional[float], Optional[str], List[str]]:
        kf, conf, legal, risks = [], None, None, []
        if e_type == "document" and analysis.get("document_analysis"):
            d = analysis["document_analysis"]
            if d.get("ai_summary"):
                kf = [d["ai_summary"]]
                if d.get("entities"):
                    types = {e.get("type", "unknown") for e in d["entities"][:5]}
                    kf.append(f"Extracted {len(d['entities'])} entities: {', '.join(types)}")
                conf, legal, risks = d.get("analysis_confidence"), d.get("legal_significance"), d.get("risk_flags", [])
            else:
                kf = [f"Document contains {d['total_words']} words",
                      "Top concepts: " + ", ".join([w for w, _ in d["top_words"][:5]])]
        elif e_type == "email" and analysis.get("email_analysis"):
            e = analysis["email_analysis"]
            kf = [f"Email thread with {len(e.get('participants', []))} participants",
                  f"Communication pattern: {e['communication_pattern']}",
                  e["thread_summary"]]
            conf, legal, risks = e.get("confidence_overall"), e.get("legal_significance"), e.get("risk_flags", [])
        elif e_type == "image" and analysis.get("image_analysis"):
            i = analysis["image_analysis"]
            if i.get("scene_description"):
                kf.append(f"Scene: {i['scene_description']}")
            if i.get("detected_text"):
                kf.append(f"Text detected: {i['detected_text']}")
            if i.get("detected_objects"):
                kf.append(f"Objects: {', '.join(i['detected_objects'])}")
            conf = i.get("analysis_confidence")
        return kf, conf, legal, risks

    def _generate_ai_executive_summary(self, case_summary: CaseSummary) -> ExecutiveSummaryResponse:
        if not self.ai_enabled:
            raise ValueError("OpenAI client not available for AI executive summary")
        from evidence_toolkit.domains import legal_config
        context = self._build_case_context_for_ai(case_summary)
        prompt = legal_config.EXECUTIVE_SUMMARY_PROMPTS.get(self.case_type, legal_config.EXECUTIVE_SUMMARY_PROMPT_GENERIC)
        try:
            return _ai_parse(self.openai_client, "gpt-4o-2024-08-06", prompt, context, ExecutiveSummaryResponse)
        except Exception as e:
            raise Exception(f"OpenAI executive summary generation failed: {e}")

    def _enhance_executive_summary(self, forensic: ExecutiveSummaryResponse, corr: CorrelationAnalysis) -> EnhancedExecutiveSummary:
        if not self.ai_enabled:
            raise ValueError("AI enhancement requires OpenAI client")

        lp = corr.legal_patterns
        contradictions = len(lp.contradictions) if lp else 0
        corroboration_strength = ("STRONG" if lp and any(c.corroboration_strength == "strong" for c in lp.corroboration) else "MODERATE")
        evidence_gaps = len(lp.evidence_gaps) if lp else 0

        timeline_days = 0
        if corr.timeline_events and len(corr.timeline_events) > 1:
            first, last = min(corr.timeline_events, key=lambda e: e.timestamp), max(corr.timeline_events, key=lambda e: e.timestamp)
            timeline_days = (last.timestamp - first.timestamp).days

        enhancement_context = f"""
<forensic_summary>
{forensic.executive_summary}

Key findings:
{chr(10).join(f'- {f}' for f in forensic.key_findings)}

Legal implications:
{chr(10).join(f'- {x}' for x in forensic.legal_implications)}

Recommended actions (forensic):
{chr(10).join(f'- {a}' for a in forensic.recommended_actions)}

Risk assessment: {forensic.risk_assessment}
Confidence: {forensic.confidence_overall:.2f}
</forensic_summary>

<correlation_patterns>
- Contradictions found: {contradictions}
- Corroboration strength: {corroboration_strength}
- Evidence gaps identified: {evidence_gaps}
- Legal patterns analyzed: {len(lp.contradictions + lp.corroboration + lp.evidence_gaps) if lp else 0}
</correlation_patterns>

<case_metadata>
- Evidence count: {len(corr.entity_correlations)}
- Critical contradictions: {contradictions}
- Corroboration strength: {corroboration_strength}
- Timeline span: {timeline_days} days
- Entity network size: {len(corr.entity_correlations)}
- Case type: {self.case_type}
</case_metadata>
""".strip()

        from evidence_toolkit.domains import legal_config
        try:
            print("   ✨ Executive summary enhanced with tribunal probability & financial estimates")
            return _ai_parse(self.openai_client, "gpt-4o-2024-08-06", legal_config.EXECUTIVE_SUMMARY_ENHANCER_PROMPT,
                             enhancement_context, EnhancedExecutiveSummary)
        except Exception as e:
            print(f"   ⚠️  Enhancement failed ({e}), using forensic summary as fallback")
            return EnhancedExecutiveSummary(
                executive_summary=forensic.executive_summary,
                key_findings=forensic.key_findings,
                tribunal_probability=0.5,
                financial_exposure_summary=f"Enhancement unavailable - forensic risk: {forensic.risk_assessment}",
                claim_strength_summary="Enhancement unavailable - manual assessment required",
                immediate_actions=forensic.recommended_actions,
                settlement_recommendation="Enhancement unavailable",
                evidence_gaps=[],
                confidence_overall=forensic.confidence_overall,
                enhancement_applied=False,
            )

    def _summarize_evidence_chunk(self, chunk: List[EvidenceSummary], idx: int, total: int) -> ChunkSummaryResponse:
        context = [f"EVIDENCE CHUNK {idx + 1} of {total}", f"Items in chunk: {len(chunk)}", ""]
        for i, e in enumerate(chunk, 1):
            context += [f"{i}. {e.filename} ({e.evidence_type.upper()})"]
            if e.analysis_confidence:
                context.append(f"   Confidence: {e.analysis_confidence:.2f}")
            if e.legal_significance:
                context.append(f"   Legal significance: {e.legal_significance}")
            if e.risk_flags:
                context.append(f"   Risk flags: {', '.join(e.risk_flags)}")
            context.append("   Findings:")
            context += [f"   • {f}" for f in e.key_findings[:3]]
            context.append("")
        prompt = ("You are analyzing a subset of evidence from a legal case. Your task is to:\n"
                  "1) Summarize key themes/patterns 2) Identify key entities 3) Extract 3-5 legally significant findings "
                  "4) Note risk flags 5) Provide a confidence score. Be concise but thorough.")
        resp = self.openai_client.responses.parse(
            model="gpt-4o-2024-08-06",
            input=[{"role": "system", "content": prompt}, {"role": "user", "content": "\n".join(context)}],
            text_format=ChunkSummaryResponse,
        )
        if resp.status == "completed" and resp.output_parsed:
            return resp.output_parsed
        raise Exception(f"Chunk summary failed: {resp.status}")

    # ---- AI context builders ----

    def _build_case_context_for_ai(self, case_summary: CaseSummary) -> str:
        CHUNK_SIZE, MAX_DIRECT = 30, 50
        return (self._build_direct_case_context(case_summary) if case_summary.evidence_count <= MAX_DIRECT
                else self._build_chunked_case_context(case_summary, CHUNK_SIZE))

    def _overall_header(self, cs: CaseSummary) -> List[str]:
        oa = cs.overall_assessment
        return [
            f"CASE ID: {cs.case_id}",
            f"EVIDENCE COUNT: {cs.evidence_count}",
            f"EVIDENCE TYPES: {', '.join(cs.evidence_types)}",
            "",
            "OVERALL ASSESSMENT:",
            f"- Legal significance: {oa['overall_legal_significance']}",
            f"- Average confidence: {oa['overall_confidence']:.2f}",
            f"- Risk flags: {oa['total_risk_flags']} total, {oa['unique_risk_flags']} unique",
            f"- Entity correlations: {oa['entity_correlations_found']}",
            "",
        ]

    def _append_if(self, parts: List[str], cond: bool, lines: List[str]):
        if cond:
            parts.extend(lines)

    def _build_direct_case_context(self, cs: CaseSummary) -> str:
        parts: List[str] = self._overall_header(cs)
        parts.append("EVIDENCE ANALYSIS:")
        for i, e in enumerate(cs.evidence_summaries, 1):
            parts += [f"{i}. {e.filename} ({e.evidence_type.upper()})",
                      f"   - Size: {e.file_size:,} bytes"]
            if e.analysis_confidence:
                parts.append(f"   - Confidence: {e.analysis_confidence:.2f}")
            if e.legal_significance:
                parts.append(f"   - Legal significance: {e.legal_significance}")
            if e.risk_flags:
                parts.append(f"   - Risk flags: {', '.join(e.risk_flags)}")
            parts += ["   - Key findings:", *[f"     • {f}" for f in e.key_findings], ""]

        if cs.correlation_result.entity_correlations:
            parts.append("ENTITY CORRELATIONS (Top 20):")
            for c in cs.correlation_result.entity_correlations[:20]:
                parts.append(f"- {c.entity_name} ({c.entity_type}): {c.occurrence_count} occurrences, confidence {c.confidence_average:.2f}")
            parts.append("")

        if cs.correlation_result.timeline_events:
            parts.append("TIMELINE EVENTS (Last 10):")
            for ev in cs.correlation_result.timeline_events[-10:]:
                parts.append(f"- {ev.timestamp.strftime('%Y-%m-%d %H:%M')}: {ev.description}")
            parts.append("")

        oa = cs.overall_assessment

        if "power_dynamics" in oa:
            pd = oa["power_dynamics"]
            parts.append("POWER DYNAMICS (Top 5 participants):")
            for p in pd["top_participants"][:5]:
                label = "dominant" if p["avg_deference"] < 0.4 else "deferential" if p["avg_deference"] > 0.6 else "neutral"
                parts.append(f"  • {p['participant']} ({p['authority']}): {p['messages']} messages, {label} ({p['avg_deference']})")
                if p["top_topics"]:
                    parts.append(f"    Topics: {', '.join(p['top_topics'])}")
            parts.append("")

        if "quoted_statements" in oa:
            qs = oa["quoted_statements"]
            parts += ["QUOTED STATEMENTS FROM DOCUMENTS:",
                      f"  Total: {qs['total_statements']} statements from {qs['people_quoted']} people across {qs['documents_with_quotes']} documents"]
            for person in qs["quoted_statements"][:5]:
                parts.append(f"  • {person['person']} ({person['role']}): {person['statement_count']} statements [{person['dominant_sentiment']}]")
                for s in person["statements"][:2]:
                    risk = f" [RISK: {', '.join(s['risk_flags'][:2])}]" if s["risk_flags"] else ""
                    parts.append(f"    - \"{s['text'][:100]}...\"{risk}")
            parts.append("")

        if "communication_patterns" in oa:
            cp = oa["communication_patterns"]
            parts += ["EMAIL COMMUNICATION PATTERNS:",
                      f"  Emails analyzed: {cp['email_count']}",
                      f"  Dominant pattern: {cp['dominant_pattern'].upper()} (risk: {cp['risk_level']})",
                      f"  Distribution: Professional={cp['professional_count']}, Escalating={cp['escalating_count']}, Hostile/Retaliatory={cp['hostile_or_retaliatory_count']}", ""]

        if "image_ocr" in oa:
            o = oa["image_ocr"]
            parts += ["IMAGE OCR TEXT DETECTED:",
                      f"  Images with text: {o['total_images_with_text']} ({o['text_extraction_rate']:.0%} of images)",
                      f"  High evidence value: {o['high_evidence_value_count']}, Medium: {o['medium_evidence_value_count']}"]
            if o["people_present_count"] > 0:
                parts.append(f"  Images with people: {o['people_present_count']}")
            if o["timestamps_visible_count"] > 0:
                parts.append(f"  Images with timestamps: {o['timestamps_visible_count']}")
            parts.append("  Sample OCR extractions:")
            for img in o["images_with_text"][:5]:
                parts.append(f"    • {img['filename']}: \"{img['detected_text'][:60]}...\" [{img['evidence_value']}]")
            parts.append("")

        lp = cs.correlation_result.legal_patterns
        if lp:
            parts.append("LEGAL PATTERN ANALYSIS:")
            if lp.contradictions:
                parts.append(f"  Contradictions detected: {len(lp.contradictions)}")
                for c in lp.contradictions[:3]:
                    parts.append(f"    • {c.contradiction_type.upper()}: {c.statement_1[:80]}... vs {c.statement_2[:80]}... (severity: {c.severity})")
            if lp.corroboration:
                parts.append(f"  Corroboration links: {len(lp.corroboration)}")
                for co in lp.corroboration[:5]:
                    parts.append(f"    • {co.corroboration_strength.upper()}: {co.claim[:100]}... ({len(co.supporting_evidence)} pieces)")
            if lp.evidence_gaps:
                parts.append(f"  Evidence gaps identified: {len(lp.evidence_gaps)}")
                for g in lp.evidence_gaps[:3]:
                    parts.append(f"    • {g[:150]}...")
            parts.append(f"  Pattern analysis confidence: {lp.confidence:.2f}\n")
        return "\n".join(parts)

    def _build_chunked_case_context(self, cs: CaseSummary, chunk_size: int) -> str:
        parts: List[str] = self._overall_header(cs)
        chunks = [cs.evidence_summaries[i:i + chunk_size] for i in range(0, len(cs.evidence_summaries), chunk_size)]
        total = len(chunks)
        print(f"   📊 Chunking {cs.evidence_count} evidence items into {total} chunks...")
        parts.append(f"EVIDENCE ANALYSIS (Chunked - {total} chunks):")
        for idx, ch in enumerate(chunks):
            print(f"   🤖 Summarizing chunk {idx + 1}/{total}...")
            try:
                csum = self._summarize_evidence_chunk(ch, idx, total)
                parts += [f"\nChunk {idx + 1} ({len(ch)} items):",
                          f"  Summary: {csum.chunk_summary}",
                          f"  Key entities: {', '.join(csum.key_entities)}",
                          f"  Key findings: {'; '.join(csum.key_findings)}"]
                if csum.risk_flags:
                    parts.append(f"  Risk flags: {', '.join(csum.risk_flags)}")
                parts.append(f"  Confidence: {csum.confidence:.2f}")
            except Exception as e:
                print(f"   ⚠️  Chunk {idx + 1} summary failed: {e}")
                parts += [f"\nChunk {idx + 1} ({len(ch)} items) - AI summary failed:"]
                for evi in ch[:3]:
                    parts.append(f"  - {evi.filename}: {evi.key_findings[0] if evi.key_findings else 'N/A'}")
        parts.append("")

        if cs.correlation_result.entity_correlations:
            parts.append("ENTITY CORRELATIONS (Top 30):")
            for c in cs.correlation_result.entity_correlations[:30]:
                parts.append(f"- {c.entity_name} ({c.entity_type}): {c.occurrence_count} occurrences")
            parts.append("")

        if cs.correlation_result.timeline_events:
            parts += ["TIMELINE SUMMARY:", "First 5 events:"]
            parts += [f"- {e.timestamp.strftime('%Y-%m-%d %H:%M')}: {e.description}" for e in cs.correlation_result.timeline_events[:5]]
            parts.append("Last 5 events:")
            parts += [f"- {e.timestamp.strftime('%Y-%m-%d %H:%M')}: {e.description}" for e in cs.correlation_result.timeline_events[-5:]]
            parts.append("")

        oa = cs.overall_assessment
        if "power_dynamics" in oa:
            pd = oa["power_dynamics"]
            parts.append("POWER DYNAMICS (Top 5 participants):")
            for p in pd["top_participants"][:5]:
                label = "dominant" if p["avg_deference"] < 0.4 else "deferential" if p["avg_deference"] > 0.6 else "neutral"
                parts.append(f"  • {p['participant']} ({p['authority']}): {p['messages']} messages, {label} ({p['avg_deference']})")
                if p["top_topics"]:
                    parts.append(f"    Topics: {', '.join(p['top_topics'])}")
            parts.append("")

        if "quoted_statements" in oa:
            qs = oa["quoted_statements"]
            parts += [f"QUOTED STATEMENTS: {qs['total_statements']} from {qs['people_quoted']} people"]
            for p in qs["quoted_statements"][:3]:
                parts.append(f"  • {p['person']}: {p['statement_count']} statements [{p['dominant_sentiment']}]")
            parts.append("")

        if "communication_patterns" in oa:
            cp = oa["communication_patterns"]
            parts += [f"COMM PATTERNS: {cp['email_count']} emails, dominant={cp['dominant_pattern']} (risk:{cp['risk_level']})", ""]

        if "image_ocr" in oa:
            o = oa["image_ocr"]
            parts += [f"IMAGE OCR: {o['total_images_with_text']} images with text ({o['text_extraction_rate']:.0%}), {o['high_evidence_value_count']} high-value", ""]

        if cs.correlation_result.legal_patterns:
            lp = cs.correlation_result.legal_patterns
            parts.append("LEGAL PATTERN ANALYSIS:")
            if lp.contradictions:
                parts.append(f"  Contradictions detected: {len(lp.contradictions)}")
                for c in lp.contradictions[:3]:
                    parts.append(f"    • {c.contradiction_type.upper()}: {c.statement_1[:80]}... vs {c.statement_2[:80]}... (severity: {c.severity})")
            if lp.corroboration:
                parts.append(f"  Corroboration links: {len(lp.corroboration)}")
                for co in lp.corroboration[:5]:
                    parts.append(f"    • {co.corroboration_strength.upper()}: {co.claim[:100]}... ({len(co.supporting_evidence)} pieces)")
            if lp.evidence_gaps:
                parts.append(f"  Evidence gaps identified: {len(lp.evidence_gaps)}")
                for g in lp.evidence_gaps[:3]:
                    parts.append(f"    • {g[:150]}...")
            parts.append(f"  Pattern analysis confidence: {lp.confidence:.2f}\n")

        return "\n".join(parts)

    # ---- Derived assessments ----

    def _calculate_overall_assessment(self, summaries: List[EvidenceSummary], corr: CorrelationAnalysis) -> Dict[str, Any]:
        confidences = [s.analysis_confidence for s in summaries if s.analysis_confidence]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        all_risks = [rf for s in summaries for rf in s.risk_flags]
        legal_counts: Dict[str, int] = {}
        for s in summaries:
            if s.legal_significance:
                legal_counts[s.legal_significance] = legal_counts.get(s.legal_significance, 0) + 1

        overall_sig = "low"
        for lvl in ("critical", "high", "medium"):
            if lvl in legal_counts:
                overall_sig = lvl
                break

        power = self._extract_power_dynamics(summaries)
        quotes = self._extract_quoted_statements(summaries)
        comms = self._analyze_communication_patterns(summaries)
        ocr = self._extract_image_ocr_text(summaries)
        rel = self._extract_relationship_network(summaries)

        result: Dict[str, Any] = {
            "overall_confidence": avg_conf,
            "total_risk_flags": len(all_risks),
            "unique_risk_flags": len(set(all_risks)),
            "risk_flag_breakdown": dict(zip(*[iter(all_risks)] * 2)) if all_risks else {},
            "legal_significance_distribution": legal_counts,
            "overall_legal_significance": overall_sig,
            "entity_correlations_found": len(corr.entity_correlations),
            "timeline_events_count": len(corr.timeline_events),
            "evidence_type_distribution": {
                t: sum(1 for s in summaries if s.evidence_type == t) for t in {s.evidence_type for s in summaries}
            },
        }
        if power: result["power_dynamics"] = power
        if quotes: result["quoted_statements"] = quotes
        if comms: result["communication_patterns"] = comms
        if ocr: result["image_ocr"] = ocr
        if rel: result["relationship_network"] = rel
        return result

    # ---- Feature extractors ----

    def _extract_power_dynamics(self, summaries: List[EvidenceSummary]) -> Optional[Dict[str, Any]]:
        participants = []
        for e in summaries:
            if e.evidence_type != "email":
                continue
            a_path, _ = _analysis_paths(self.storage.derived_dir, e.sha256)
            a = _read_json(a_path) or {}
            email = a.get("email_analysis", {})
            participants.extend(email.get("participants", []))

        if not participants:
            return None

        stats = defaultdict(lambda: {"message_count": 0, "deference_scores": [], "authority_level": None, "topics": set(), "display_name": None})
        for p in participants:
            email = (p.get("email_address") or "").strip().lower()
            if not email:
                continue
            s = stats[email]
            s["message_count"] += p.get("message_count", 0)
            if p.get("deference_score") is not None:
                s["deference_scores"].append(p["deference_score"])
            s["authority_level"] = s["authority_level"] or p.get("authority_level")
            s["topics"].update(p.get("dominant_topics", []))
            s["display_name"] = s["display_name"] or p.get("display_name")

        top = []
        for email, s in sorted(stats.items(), key=lambda x: -x[1]["message_count"])[:10]:
            avg_def = sum(s["deference_scores"]) / len(s["deference_scores"]) if s["deference_scores"] else 0.5
            top.append({
                "participant": s["display_name"] or email.split("@")[0],
                "email": email,
                "authority": s["authority_level"] or "unknown",
                "messages": s["message_count"],
                "avg_deference": round(avg_def, 2),
                "top_topics": list(s["topics"])[:3],
            })
        return {"top_participants": top, "participant_count": len(stats), "total_messages_analyzed": sum(x["messages"] for x in top)}

    def _analyze_communication_patterns(self, summaries: List[EvidenceSummary]) -> Optional[Dict[str, Any]]:
        from collections import Counter
        patterns, details = [], []
        for e in summaries:
            if e.evidence_type != "email":
                continue
            a_path, _ = _analysis_paths(self.storage.derived_dir, e.sha256)
            a = _read_json(a_path) or {}
            em = a.get("email_analysis") or {}
            p = em.get("communication_pattern")
            if p:
                patterns.append(p)
                details.append({
                    "sha256": e.sha256,
                    "filename": (a.get("file_metadata") or {}).get("filename", "unknown"),
                    "pattern": p,
                    "risk_flags": em.get("risk_flags", []),
                })
        if not patterns:
            return None
        c = Counter(patterns)
        dominant = c.most_common(1)[0][0]
        hostile = c.get("hostile", 0) + c.get("retaliatory", 0)
        escalating = c.get("escalating", 0)
        risk = "high" if hostile > 0 or c.get("retaliatory", 0) > 0 else "medium" if escalating > 0 else "low"
        return {
            "email_count": len(patterns),
            "pattern_distribution": dict(c),
            "dominant_pattern": dominant,
            "risk_level": risk,
            "hostile_or_retaliatory_count": hostile,
            "escalating_count": escalating,
            "professional_count": c.get("professional", 0),
            "pattern_details": details,
        }

    def _extract_quoted_statements(self, summaries: List[EvidenceSummary]) -> Optional[Dict[str, Any]]:
        from collections import Counter
        by_person = defaultdict(lambda: {"statements": [], "sentiments": [], "risk_flags": set(), "role": None})
        for e in summaries:
            if e.evidence_type != "document":
                continue
            a_path, _ = _analysis_paths(self.storage.derived_dir, e.sha256)
            a = _read_json(a_path) or {}
            d = a.get("document_analysis") or {}
            if not d:
                continue
            doc_sent = d.get("sentiment", "neutral")
            doc_risks = d.get("risk_flags", [])
            fname = (a.get("file_metadata") or {}).get("filename", "unknown")
            for ent in d.get("entities", []):
                if ent.get("type") == "person" and ent.get("quoted_text"):
                    name = ent["name"]
                    by_person[name]["statements"].append({
                        "text": ent["quoted_text"],
                        "source_sha256": e.sha256,
                        "source_file": fname,
                        "document_sentiment": doc_sent,
                        "risk_flags": doc_risks,
                        "context": (ent.get("context") or "")[:100],
                    })
                    by_person[name]["sentiments"].append(doc_sent)
                    by_person[name]["risk_flags"].update(doc_risks)
                    if ent.get("relationship") and not by_person[name]["role"]:
                        by_person[name]["role"] = ent["relationship"]

        if not by_person:
            return None

        out = []
        for person, data in by_person.items():
            dist = Counter(data["sentiments"])
            out.append({
                "person": person,
                "role": data["role"] or "unknown",
                "statement_count": len(data["statements"]),
                "statements": data["statements"],
                "dominant_sentiment": dist.most_common(1)[0][0] if dist else "neutral",
                "sentiment_distribution": dict(dist),
                "has_risk_indicators": bool(data["risk_flags"]),
                "risk_types": list(data["risk_flags"]),
            })
        out.sort(key=lambda x: -x["statement_count"])
        return {
            "quoted_statements": out,
            "total_statements": sum(p["statement_count"] for p in out),
            "people_quoted": len(out),
            "documents_with_quotes": len({s["source_sha256"] for v in by_person.values() for s in v["statements"]}),
        }

    def _extract_image_ocr_text(self, summaries: List[EvidenceSummary]) -> Optional[Dict[str, Any]]:
        images, obj_cats = [], defaultdict(list)
        for e in summaries:
            if e.evidence_type != "image":
                continue
            a_path, _ = _analysis_paths(self.storage.derived_dir, e.sha256)
            a = _read_json(a_path) or {}
            img = (a.get("image_analysis") or {}).get("openai_response", {}).get("parsed", {}) or {}
            txt = img.get("detected_text")
            if not txt:
                continue
            images.append({
                "sha256": e.sha256,
                "filename": (a.get("file_metadata") or {}).get("filename", "unknown"),
                "detected_text": txt,
                "scene_description": (img.get("scene_description") or "")[:100],
                "detected_objects": img.get("detected_objects", []),
                "evidence_value": img.get("potential_evidence_value", "low"),
                "people_present": img.get("people_present", False),
                "timestamps_visible": img.get("timestamps_visible", False),
                "legal_relevance_notes": img.get("legal_relevance_notes", ""),
            })
            for obj in img.get("detected_objects", []):
                obj_cats[obj].append(txt)

        if not images:
            return None

        high = sum(1 for i in images if i["evidence_value"] == "high")
        medium = sum(1 for i in images if i["evidence_value"] == "medium")
        ppl = sum(1 for i in images if i["people_present"])
        ts = sum(1 for i in images if i["timestamps_visible"])
        total_imgs = sum(1 for s in summaries if s.evidence_type == "image")
        rate = (len(images) / total_imgs) if total_imgs else 0
        return {
            "images_with_text": images[:20],
            "total_images_with_text": len(images),
            "text_extraction_rate": rate,
            "high_evidence_value_count": high,
            "medium_evidence_value_count": medium,
            "people_present_count": ppl,
            "timestamps_visible_count": ts,
            "object_categories": {k: len(v) for k, v in sorted(obj_cats.items(), key=lambda x: -len(x[1]))[:10]},
        }

    def _extract_relationship_network(self, summaries: List[EvidenceSummary]) -> Optional[Dict[str, Any]]:
        import re
        rels, roles = [], {}
        email_pats = [r"sent email to (.+)", r"email to (.+)", r"email from (.+)", r"replied to (.+)", r"cc['\u2019]?d? (.+)"]
        escal_pats = [r"reported to (.+)", r"escalated to (.+)", r"complained to (.+)", r"raised concern with (.+)"]

        for e in summaries:
            if e.evidence_type != "document":
                continue
            a_path, _ = _analysis_paths(self.storage.derived_dir, e.sha256)
            a = _read_json(a_path) or {}
            d = a.get("document_analysis") or {}
            for ent in d.get("entities", []):
                name, rel = ent.get("name"), ent.get("relationship", "")
                if not name or not rel:
                    continue
                roles.setdefault(name, rel)
                rtype, target = "other", None
                for pat in email_pats:
                    m = re.search(pat, rel, re.IGNORECASE)
                    if m:
                        target, rtype = m.group(1).strip(), "email_communication"; break
                if not target:
                    for pat in escal_pats:
                        m = re.search(pat, rel, re.IGNORECASE)
                        if m:
                            target, rtype = m.group(1).strip(), "escalation"; break
                if target:
                    rels.append({"source": name, "target": target, "relationship_type": rtype, "evidence_sha256": e.sha256, "context": rel})

        if not rels:
            return None

        counts = defaultdict(int)
        for r in rels:
            counts[(r["source"], r["target"], r["relationship_type"])] += 1

        degree = defaultdict(int)
        for r in rels:
            degree[r["source"]] += 1
            degree[r["target"]] += 1
        key_players = sorted(degree.items(), key=lambda x: -x[1])[:10]

        return {
            "relationships": rels[:50],
            "total_relationships": len(rels),
            "unique_connections": len(counts),
            "key_players": [{"name": n, "connection_count": c, "role": roles.get(n, "unknown")} for n, c in key_players],
            "relationship_type_distribution": {
                "email_communication": sum(1 for r in rels if r["relationship_type"] == "email_communication"),
                "escalation": sum(1 for r in rels if r["relationship_type"] == "escalation"),
                "other": sum(1 for r in rels if r["relationship_type"] == "other"),
            },
        }


__all__ = [
    "ExecutiveSummaryResponse",
    "EnhancedExecutiveSummary",
    "ChunkSummaryResponse",
    "EvidenceSummary",
    "CaseSummary",
    "SummaryGenerator",
]
