# v4.0 Agentic Architecture

**Question**: Should Evidence Toolkit use a production agent system (e.g., LangGraph, AutoGen) for runtime orchestration?

**Answer**: **YES** - Multi-agent architecture is a perfect fit for evidence analysis.

---

## Why Agents?

### Current Problem (v3.3)
```python
# Sequential, rigid pipeline
for evidence in evidence_list:
    if is_document(evidence):
        analyze_document(evidence)
    elif is_image(evidence):
        analyze_image(evidence)
    elif is_email(evidence):
        analyze_email(evidence)

correlate_all(evidence_list)
generate_summary()
```

**Limitations**:
- ❌ Sequential execution (slow)
- ❌ Fixed routing logic (if/elif chains)
- ❌ No dynamic decision-making (can't adapt to evidence content)
- ❌ No inter-agent communication (correlation is post-hoc)
- ❌ No task prioritization (critical evidence waits same as trivial)

### Agentic Solution (v4.0)
```python
# Multi-agent system with autonomous coordination
agents = [
    DocumentAnalysisAgent(),
    ImageAnalysisAgent(),
    EmailAnalysisAgent(),
    CorrelationAgent(),
    SummaryAgent()
]

orchestrator = EvidenceOrchestrator(agents)
result = await orchestrator.analyze_case(case_id)
```

**Benefits**:
- ✅ Parallel execution (3-5x faster)
- ✅ Dynamic routing (agents choose based on evidence characteristics)
- ✅ Inter-agent communication (correlation agent queries others)
- ✅ Adaptive workflows (summary agent decides what to prioritize)
- ✅ Resilience (one agent failure doesn't crash entire pipeline)

---

## Agent System Design

### Architecture: LangGraph-Based Multi-Agent System

**Why LangGraph?**
- Built on LangChain (proven framework)
- Graph-based workflows (flexible routing)
- Built-in state management (evidence catalog, findings)
- Tool integration (can use existing analyzers as tools)
- Human-in-the-loop support (future: ask user for clarification)

### Agent Roles

#### 1. **Router Agent** (Orchestrator)
**Role**: Classify evidence and route to specialist agents

```python
class RouterAgent:
    """Routes evidence to appropriate specialist agents."""

    async def route(self, evidence_sha256: str) -> list[str]:
        """Determine which agents should process this evidence."""

        metadata = await self.storage.get_metadata(evidence_sha256)

        # Dynamic routing based on evidence characteristics
        agents_needed = []

        if metadata.mime_type.startswith("image"):
            agents_needed.append("image-analyst")

            # Check if it's also a text-heavy image (OCR candidate)
            if await self._has_substantial_text(evidence_sha256):
                agents_needed.append("document-analyst")  # OCR → text analysis

        elif metadata.mime_type == "application/pdf":
            # Check if PDF is text-extractable
            if await self._can_extract_text(evidence_sha256):
                agents_needed.append("document-analyst")
            else:
                # Image-only PDF
                agents_needed.append("image-analyst")

        elif metadata.extension == ".eml":
            agents_needed.append("email-analyst")

        return agents_needed
```

#### 2. **Document Analysis Agent**
**Role**: Analyze text-based evidence (PDFs, TXT, DOCX)

**Tools**:
- PDF text extractor
- OpenAI text analysis
- Entity extraction
- Legal risk flagging

**Inputs**: Evidence SHA256
**Outputs**: DocumentAnalysis (entities, sentiment, risk flags)

```python
class DocumentAnalysisAgent:
    """Specialist agent for document analysis."""

    async def analyze(self, evidence_sha256: str, context: dict) -> DocumentAnalysis:
        """Analyze document evidence."""

        # Extract text
        content = await self.extractor.extract_text(evidence_sha256)

        # Analyze with AI
        analysis = await self.ai_provider.generate_structured(
            prompt=self.domain_config.DOCUMENT_ANALYSIS_PROMPT,
            context=content,
            response_model=DocumentAnalysis
        )

        # Publish findings to shared state (for other agents)
        await self.publish_entities(analysis.entities)

        return analysis
```

#### 3. **Image Analysis Agent**
**Role**: Analyze visual evidence (JPG, PNG, screenshots)

**Tools**:
- OpenAI Vision API
- OCR extraction
- EXIF metadata reader

**Inputs**: Evidence SHA256
**Outputs**: ImageAnalysisStructured (scene description, OCR text, evidential value)

#### 4. **Email Analysis Agent**
**Role**: Analyze email threads (power dynamics, escalation)

**Tools**:
- Email parser
- OpenAI thread analysis
- Power dynamics scorer

**Inputs**: Evidence SHA256
**Outputs**: EmailThreadAnalysis (participants, communication pattern, escalation events)

#### 5. **Correlation Agent**
**Role**: Find cross-evidence patterns (runs AFTER specialist agents)

**Tools**:
- Entity matching (AI-powered for v3.2+ feature)
- Timeline reconstruction
- Legal pattern detection

**Inputs**: All analyses from specialist agents
**Outputs**: CorrelationAnalysis (entity correlations, legal patterns, timeline)

```python
class CorrelationAgent:
    """Finds patterns across all analyzed evidence."""

    async def correlate(self, all_analyses: list[UnifiedAnalysis]) -> CorrelationAnalysis:
        """Correlate findings across evidence."""

        # Subscribe to entity stream from all specialist agents
        all_entities = await self.get_all_entities()

        # AI-powered entity resolution
        canonical_entities = await self._resolve_entities(all_entities)

        # Detect legal patterns (contradictions, corroboration, gaps)
        patterns = await self._detect_legal_patterns(all_analyses)

        # Build timeline
        timeline = self._construct_timeline(all_analyses)

        return CorrelationAnalysis(
            entity_correlations=canonical_entities,
            legal_patterns=patterns,
            timeline=timeline
        )
```

#### 6. **Executive Summary Agent**
**Role**: Generate client-facing executive summary

**Tools**:
- OpenAI summary generation
- Domain-specific templates (workplace/contract/generic)

**Inputs**: All analyses + correlations
**Outputs**: CaseSummary (forensic summary, key findings, legal implications, recommended actions)

**Special Feature**: Can ask Correlation Agent for specific data
```python
class ExecutiveSummaryAgent:
    """Generates executive summaries for client deliverables."""

    async def generate(
        self,
        all_analyses: list[UnifiedAnalysis],
        correlations: CorrelationAnalysis
    ) -> CaseSummary:
        """Generate executive summary."""

        # Query correlation agent for high-priority findings
        critical_entities = await self.correlation_agent.get_critical_entities()

        # Generate summary with domain-specific prompt
        summary = await self.ai_provider.generate_structured(
            prompt=self.domain_config.EXECUTIVE_SUMMARY_PROMPT,
            context=self._build_context(all_analyses, correlations),
            response_model=CaseSummary
        )

        return summary
```

---

## LangGraph Workflow

### State Schema
```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph

class EvidenceAnalysisState(TypedDict):
    """Shared state across all agents."""

    # Input
    case_id: str
    evidence_list: list[str]  # SHA256s

    # Specialist agent outputs
    document_analyses: Annotated[list[DocumentAnalysis], "append"]
    image_analyses: Annotated[list[ImageAnalysisStructured], "append"]
    email_analyses: Annotated[list[EmailThreadAnalysis], "append"]

    # Correlation agent output
    correlations: CorrelationAnalysis | None

    # Summary agent output
    executive_summary: CaseSummary | None

    # Metadata
    completed_evidence: Annotated[list[str], "append"]
    errors: Annotated[list[dict], "append"]
```

### Graph Definition
```python
def create_analysis_graph():
    """Create LangGraph workflow for evidence analysis."""

    workflow = StateGraph(EvidenceAnalysisState)

    # Add agent nodes
    workflow.add_node("route", router_agent_node)
    workflow.add_node("analyze_document", document_agent_node)
    workflow.add_node("analyze_image", image_agent_node)
    workflow.add_node("analyze_email", email_agent_node)
    workflow.add_node("correlate", correlation_agent_node)
    workflow.add_node("summarize", summary_agent_node)

    # Define edges (workflow)
    workflow.add_edge(START, "route")

    # Router fans out to specialist agents (parallel)
    workflow.add_conditional_edges(
        "route",
        route_to_specialists,  # Function that returns list of agents
        {
            "analyze_document": "analyze_document",
            "analyze_image": "analyze_image",
            "analyze_email": "analyze_email"
        }
    )

    # All specialist agents converge to correlation
    workflow.add_edge("analyze_document", "correlate")
    workflow.add_edge("analyze_image", "correlate")
    workflow.add_edge("analyze_email", "correlate")

    # Correlation → Summary → End
    workflow.add_edge("correlate", "summarize")
    workflow.add_edge("summarize", END)

    return workflow.compile()
```

### Visual Workflow
```
                    ┌─────────┐
                    │  START  │
                    └────┬────┘
                         │
                         ↓
                  ┌─────────────┐
                  │   ROUTER    │
                  │   AGENT     │
                  └──────┬──────┘
                         │
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │ DOCUMENT │    │  IMAGE   │    │  EMAIL   │
   │  AGENT   │    │  AGENT   │    │  AGENT   │
   └────┬─────┘    └────┬─────┘    └────┬─────┘
        │               │               │
        └───────────────┼───────────────┘
                        ↓
                ┌──────────────┐
                │ CORRELATION  │
                │    AGENT     │
                └──────┬───────┘
                       ↓
                ┌──────────────┐
                │   SUMMARY    │
                │    AGENT     │
                └──────┬───────┘
                       ↓
                    ┌─────────┐
                    │   END   │
                    └─────────┘
```

---

## Advanced Agent Features

### 1. **Inter-Agent Communication**

Correlation Agent can query specialist agents:
```python
# Correlation agent needs more context about an entity
document_agent_response = await self.send_message(
    to="document-analyst",
    query="Get all quotes from 'John Smith' in evidence abc123"
)
```

### 2. **Human-in-the-Loop** (Future)

```python
# Summary agent encounters ambiguity
user_input = await self.ask_human(
    question="Found two 'John Smith' entities. Same person?",
    options=["Yes, same person", "No, different people", "Unsure"]
)
```

### 3. **Dynamic Workflows**

```python
# If correlation agent finds contradictions, invoke new agent
if correlations.contradictions:
    contradiction_analysis = await self.invoke_agent(
        agent="contradiction-specialist",
        context=correlations.contradictions
    )
```

### 4. **Streaming Results**

```python
# Stream results to user as agents complete
async for update in orchestrator.analyze_case_stream(case_id):
    if update.agent == "document-analyst":
        print(f"✅ Document {update.evidence_sha256[:8]} analyzed")
    elif update.agent == "correlation":
        print(f"🔗 Found {len(update.result.correlations)} correlations")
```

---

## Integration with v4.0 Clean Architecture

**Perfect Fit**: Agents use the same interfaces we're designing!

```python
class DocumentAnalysisAgent:
    """LangGraph agent that uses v4.0 infrastructure."""

    def __init__(
        self,
        ai_provider: IAIProvider,        # ✅ Uses interface
        storage: IStorageProvider,       # ✅ Uses interface
        config: ToolkitSettings           # ✅ Uses config
    ):
        self.ai = ai_provider
        self.storage = storage
        self.config = config

    async def __call__(self, state: EvidenceAnalysisState) -> dict:
        """LangGraph node function."""

        sha256 = state["current_evidence"]

        # Use existing service layer (or directly call adapters)
        analysis = await self._analyze_document(sha256)

        # Update state
        return {
            "document_analyses": [analysis],
            "completed_evidence": [sha256]
        }
```

**No architectural changes needed!** Agents are just another application layer on top of services.

---

## Implementation Plan

### Phase 1: v4.0 Foundation (Weeks 1-6)
- Build clean architecture (interfaces, services, adapters)
- Async pipeline working
- Configuration system
- **Don't add agents yet** - keep simple orchestrator

### Phase 2: Agentic Migration (Weeks 7-9)
- Install LangGraph
- Convert analyzers to LangGraph agents
- Implement state management
- Add inter-agent communication

### Phase 3: Advanced Features (v4.1+)
- Human-in-the-loop for ambiguous cases
- Contradiction specialist agent
- Dynamic workflow routing
- Agent monitoring and observability

---

## Decision: Should v4.0 Be Agentic?

### Framework Comparison Summary

| Framework | Complexity | Lock-in | Best For |
|-----------|------------|---------|----------|
| **Custom (v3.3)** | Low | None | Linear pipelines, full control |
| **OpenAI Agents SDK** | Medium | OpenAI | Conversational workflows, handoff delegation |
| **LangGraph** | High | None | Complex routing, state machines, multi-provider |

### Option A: v4.0 = Clean Architecture (No Framework)
**Implementation**: Keep pipeline.py pattern, add async + DI + config

**Pros**:
- ✅ Simplest implementation (40-50 hours)
- ✅ No new dependencies
- ✅ Full control over orchestration
- ✅ Current pipeline is proven and working
- ✅ Easy to test and debug

**Cons**:
- ❌ Manual orchestration code (workflows.py)
- ❌ No natural language case queries
- ❌ Limited future extensibility

**Best for**: Production stability, minimal risk, proven patterns

---

### Option B: v4.0 = Clean Architecture + OpenAI Agents SDK
**Implementation**: Hybrid - keep pipeline.py, add optional agent chat interface

**Pros**:
- ✅ Production pipeline unchanged (low risk)
- ✅ Experimental agent interface for power users
- ✅ Natural language case exploration ("What contradictions exist?")
- ✅ Minimal additional code (~100 lines for chat agent)
- ✅ Handoff pattern matches forensic workflow

**Cons**:
- ⚠️ OpenAI vendor lock-in (but already using OpenAI)
- ⚠️ Two interfaces to maintain (CLI + chat)
- ⚠️ Handoff pattern may not fit all use cases

**Best for**: Gradual innovation, keeping production stable while exploring agentic features

---

### Option C: v4.0 = Clean Architecture + LangGraph
**Implementation**: Rewrite pipeline as LangGraph state machine

**Pros**:
- ✅ Explicit state management (great for debugging)
- ✅ Graph visualization of workflow
- ✅ Multi-provider support (swap OpenAI for Anthropic/local)
- ✅ Conditional routing (chunking threshold, case type routing)
- ✅ Future-proof for complex workflows

**Cons**:
- ❌ Most complex (60-70 hours)
- ❌ Steep learning curve
- ❌ Overkill for current linear pipeline
- ❌ Significant refactoring risk

**Best for**: Complex future workflows, multi-provider requirements, state-heavy applications

---

## **RECOMMENDED: Option A + B Hybrid**

### **Core v4.0: Clean Architecture (No Framework)**
**Why**: Current pipeline is working, linear, and optimized
- Keep pipeline.py pattern (ingest → analyze → correlate → package)
- Add async + dependency injection + Pydantic Settings
- Focus on eliminating technical debt (875 duplicate lines)
- **Effort**: 40-50 hours
- **Risk**: Low

### **Experimental v4.1: OpenAI Agents Chat Interface**
**Why**: Enable conversational case exploration without risking production
- Add optional chat interface (`evidence-toolkit chat --case-id CASE-001`)
- Agent uses existing pipeline as tools (zero duplication)
- Natural language queries: "What contradictions exist between witnesses?"
- **Effort**: +10 hours
- **Risk**: Isolated (production unaffected)

### Implementation Strategy

**v4.0 Core (Weeks 1-6)**:
```python
# Traditional production interface (unchanged UX)
uv run evidence-toolkit process-case data/cases/MY-CASE --case-id MY-CASE

# Uses clean architecture internally:
# - Async concurrent processing (3x speedup)
# - Dependency injection (testable)
# - Configuration-driven (YAML + env)
```

**v4.1 Experimental (Weeks 7-8)**:
```python
# New optional chat interface
uv run evidence-toolkit chat --case-id MY-CASE

# Conversational analysis:
> "Process the evidence in data/cases/MY-CASE"
✅ Processed 15 evidence items. Found 23 entities, 4 contradictions.

> "Tell me about the contradictions"
📋 Found 4 contradictions:
   1. John Smith's timeline conflicts between email and statement
   2. Meeting date discrepancy (Feb 14 vs Feb 15)
   ...

> "Show me John Smith's quoted statements"
💬 John Smith statements:
   - "I never received the email" (statement.pdf, confidence: 0.95)
   - Email sent to john.smith@company.com on Feb 10 (evidence abc123)
```

This approach:
- ✅ Keeps production stable (v4.0 core is proven patterns)
- ✅ Enables innovation (v4.1 chat interface for exploration)
- ✅ No vendor lock-in for core pipeline
- ✅ Optional OpenAI agents for power users
- ✅ Minimal risk, maximum flexibility

---

## Next Steps

1. **Review this agentic design** - Does it align with vision?
2. **Decide: v4.0 with or without agents?**
3. **If agents: Add LangGraph to dependencies** in [docs/v4.0/MIGRATION_GUIDE.md](docs/v4.0/MIGRATION_GUIDE.md)
4. **Update task breakdown** - Add agent implementation tasks (Week 7-9)

---

**Questions to answer:**
- Do we want agentic in v4.0 or defer to v4.1?
- LangGraph vs. Custom implementation?
- Which agents are MVP (must-have) vs. nice-to-have?

Let me know and I'll update the migration guide accordingly!
