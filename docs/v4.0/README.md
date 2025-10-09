# Evidence Toolkit v4.0 - Clean Architecture Migration

**Status**: Planning Phase
**Target Release**: 7 weeks from kickoff
**Estimated Effort**: 40-50 hours
**Architecture Pattern**: Hexagonal (Ports & Adapters)

---

## Overview

v4.0 is a **complete architectural redesign** that preserves all v3.3 functionality while introducing:

1. **Clean Architecture** - Hexagonal pattern with dependency injection
2. **Async-First** - 3-5x performance improvement via concurrent processing
3. **Configuration-Driven** - All settings externalized (YAML + env vars)
4. **Modular & Testable** - Interfaces for easy testing and adapter swapping
5. **Zero Technical Debt** - Eliminates all 875 duplicate lines identified in analysis

**Key Principle**: We're refactoring the HOW, not the WHAT. All v3.3 features remain.

---

## Documentation Index

| Document | Purpose | Audience |
|----------|---------|----------|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Complete system design (layers, interfaces, data flow) | Architects, developers |
| **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** | Step-by-step migration from v3.3 → v4.0 | Implementation team |
| **[CONFIGURATION.md](CONFIGURATION.md)** | Configuration system design (Pydantic Settings) | DevOps, users |
| **[ASYNC_PATTERNS.md](ASYNC_PATTERNS.md)** | Async/await patterns and concurrency control | Async migration team |
| **[TESTING_STRATEGY.md](TESTING_STRATEGY.md)** | Testing approach (mocks, benchmarks, validation) | QA, testing team |
| **[AGENT_WORKFLOW.md](AGENT_WORKFLOW.md)** | How to use specialized agents for v4.0 tasks | Project coordinators |
| **[TASK_BREAKDOWN.md](TASK_BREAKDOWN.md)** | Week-by-week task list with effort estimates | Project managers |

---

## Design Principles

### 1. **Preserve What Works** ✅

**Keep unchanged:**
- [src/evidence_toolkit/core/models.py](../../src/evidence_toolkit/core/models.py) - 48 Pydantic models (perfect!)
- Content-addressed storage pattern (SHA256 deduplication)
- Domain configuration system ([domains/legal_config.py](../../src/evidence_toolkit/domains/legal_config.py))
- OpenAI integration (just wrapped in adapters)
- CLI user experience (command structure stays same)

### 2. **Fix What's Broken** 🔧

**Replace/refactor:**
- Scattered configuration → Unified Pydantic Settings
- Tight coupling → Dependency injection
- Sync blocking → Async concurrent
- Code duplication (875 lines) → DRY abstractions
- Monolithic analyzers → Composable services

### 3. **Enable Future Growth** 🚀

**New capabilities:**
- Swap AI providers (OpenAI → Anthropic/local models)
- Swap storage backends (local → S3/Azure)
- Easy testing (mock adapters, no API calls)
- Parallel workflows (concurrent analysis)
- Domain extensibility (corporate, journalism, research)

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│  Presentation Layer (CLI)                               │
│  - Ultra-thin wrapper (argument parsing only)           │
│  - Delegates to workflows                               │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Application Layer (Workflows, Pipeline)                │
│  - Composable async workflows                           │
│  - Orchestration logic (ingest → analyze → package)     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Domain Layer (Services, Business Logic)                │
│  - EvidenceAnalysisService                              │
│  - Pure business logic (no I/O, no AI imports)          │
│  - Uses interfaces (ports)                              │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Infrastructure Layer (Adapters)                        │
│  - OpenAI adapter (implements IAIProvider)              │
│  - LocalStorage adapter (implements IStorageProvider)   │
│  - PDF extractor (implements IDocumentExtractor)        │
└─────────────────────────────────────────────────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete details.

---

## Migration Timeline

### **Week 1: Foundation** (Infrastructure Layer)
- Create core interfaces (IAIProvider, IStorageProvider, IDocumentExtractor)
- Implement Pydantic Settings configuration system
- Create OpenAI adapter
- Create local storage adapter
- **Deliverable**: Foundation layer complete, tested independently

### **Week 2: Services** (Domain Layer)
- Create EvidenceAnalysisService with business logic
- Migrate DocumentAnalyzer to use dependency injection
- Create workflow orchestration system
- **Deliverable**: Document analysis working end-to-end (async)

### **Week 3: Complete Async Migration**
- Migrate ImageAnalyzer to async + DI
- Migrate EmailAnalyzer to async + DI
- Migrate CorrelationAnalyzer to async + DI
- **Deliverable**: All analyzers async, 3x+ speedup demonstrated

### **Week 4: Pipeline Integration**
- Refactor pipeline modules (ingest, package, summary)
- Integrate workflows with new service layer
- **Deliverable**: Complete pipeline working async

### **Week 5: Testing & Validation**
- Unit tests for all services (mock adapters)
- Integration tests (real OpenAI calls)
- Performance benchmarks (v3.3 vs v4.0)
- **Deliverable**: 90%+ test coverage

### **Week 6: CLI & Documentation**
- Refactor CLI to thin wrapper
- Configuration files (defaults.yaml, profiles)
- Update all user documentation
- **Deliverable**: v4.0 feature-complete

### **Week 7: Polish & Release**
- Bug fixes from testing
- Migration guide for users
- Release notes and changelog
- **Deliverable**: v4.0.0 tagged and released

---

## Performance Goals

| Metric | v3.3 (Baseline) | v4.0 (Target) | Improvement |
|--------|-----------------|---------------|-------------|
| 10 documents (sequential) | 30s | 10s | **3x faster** |
| 20 mixed evidence | 90s | 25s | **3.6x faster** |
| 50+ evidence (chunked) | 300s | 80s | **3.75x faster** |
| Code duplication | 875 lines (56% files) | 0 lines | **100% eliminated** |
| Test coverage | ~20% | 90% | **4.5x improvement** |
| Configuration files | Hardcoded | YAML + env | **Externalized** |

---

## Risk Mitigation

### **High Risk: Async Migration Bugs**
- **Mitigation**: POC first (Week 1), validate 3x speedup before full migration
- **Fallback**: If POC shows <2x speedup, pivot to sync BaseAnalyzer

### **Medium Risk: Breaking Changes**
- **Mitigation**: CLI commands stay identical, only internal refactoring
- **Fallback**: Provide v3.3 → v4.0 migration script

### **Low Risk: Effort Overrun**
- **Mitigation**: Use specialized agents for parallel work (see [AGENT_WORKFLOW.md](AGENT_WORKFLOW.md))
- **Fallback**: Reduce scope (defer S3 adapter, Anthropic adapter to v4.1)

---

## Success Criteria

✅ **Must Have (v4.0.0)**:
- All v3.3 features working (documents, images, emails, correlation)
- 3x+ performance improvement demonstrated
- Zero code duplication (BaseAnalyzer, config consolidation)
- Configuration externalized (YAML + Pydantic Settings)
- 90%+ test coverage

🎯 **Should Have (v4.0.0)**:
- Async pipeline complete (ingest, analyze, correlate, package)
- Mock adapters for testing (no OpenAI calls in tests)
- Documentation complete (architecture, migration guide)

🚀 **Could Have (v4.1)**:
- S3 storage adapter
- Anthropic Claude adapter
- Additional domain configs (corporate, journalism)
- Web UI for case management

---

## Agent-Assisted Development

v4.0 implementation uses **specialized Claude Code subagents** for parallel development:

- **v4-architect**: Creates infrastructure layer (interfaces, adapters, config)
- **v4-async-specialist**: Handles async migration and concurrency patterns
- **v4-tester**: Writes tests, benchmarks, validates performance

See [AGENT_WORKFLOW.md](AGENT_WORKFLOW.md) for delegation strategy.

---

## Next Steps

1. **Review this documentation** - Ensure architectural vision aligns with goals
2. **Run POC** - Validate async performance gains (Week 1)
3. **Create agents** - Set up specialized subagents for parallel work
4. **Start Week 1** - Begin infrastructure layer implementation

---

**Questions or feedback?** Open an issue or discuss in project planning sessions.

**Ready to begin?** Start with [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design.
