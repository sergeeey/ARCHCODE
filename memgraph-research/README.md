# MemGraph Research Platform

**Cross-project hypothesis transfer via research memory graphs**

## Quick Start (Day 1 Setup)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `anthropic` — Claude API for 7-pass analysis
- `neo4j` — Graph database (optional, uses NetworkX fallback)
- `networkx` — In-memory graph fallback
- `sentence-transformers` — Embeddings for similarity
- `pydantic`, `pyyaml`, `pandas`, `scikit-learn` — Data processing

### 2. Configuration

```bash
# Copy example config
cp .env.example .env

# Edit .env — add your Claude API key
# NEO4J_URI is optional (will use NetworkX if not available)
```

### 3. Run Setup Test

```bash
python setup_test.py
```

**Expected output:**
```
✅ DAY 1 SETUP COMPLETE - Ready for Day 2

Summary:
  Dependencies              ✅ PASS
  Neo4j (optional)          ⚠️  WARN (using fallback)
  NetworkX Fallback         ✅ PASS
  Embeddings                ✅ PASS
  Project Parser            ✅ PASS
```

### 4. Analyze First Project (Day 2)

```bash
# Run 7-pass analysis on ARCHCODE
python -m src.generator.seven_pass --project ../ARCHCODE

# Output:
#   - analysis_report.md (7-pass output)
#   - data/research_memory.db (graph updated)
```

---

## Architecture

```
memgraph-research/
├── src/
│   ├── acquisition/      # Project parsing
│   ├── memory/           # Graph + embeddings
│   ├── generator/        # 7-pass hypothesis generator
│   ├── verifier/         # Evidence audit
│   ├── ranker/           # DeepConf scoring
│   └── reporter/         # Markdown output
├── data/
│   ├── research_memory.db    # Neo4j or NetworkX graph
│   └── embeddings/           # Cached sentence embeddings
└── experiments/          # Analysis results
```

## Core Components

### 1. Graph Manager (`src/memory/graph_manager.py`)

Manages research memory graph with automatic backend selection:
- **Neo4j** (preferred): Persistent graph database
- **NetworkX** (fallback): In-memory graph

**Usage:**
```python
from src.memory.graph_manager import GraphManager

# Auto-selects backend (Neo4j or NetworkX)
gm = GraphManager(uri="bolt://localhost:7687")

# Add project
gm.add_project("archcode", {"domain": "genomics", "status": "active"})

# Add hypothesis
gm.add_hypothesis(
    "h3_benchmark", 
    "archcode", 
    "Foundation model benchmark",
    score=24.0,
    metadata={"type": "evaluation"}
)

# Find similar hypotheses from other projects
similar = gm.get_similar_hypotheses("new_project", min_similarity=0.7)
```

### 2. Embeddings Engine (`src/memory/embeddings.py`)

Computes sentence embeddings for hypothesis similarity:
- Model: `all-MiniLM-L6-v2` (384-dim, fast, good quality)
- Automatic caching (in-memory + disk)

**Usage:**
```python
from src.memory.embeddings import EmbeddingEngine

engine = EmbeddingEngine()

# Embed hypotheses
texts = [
    "Foundation model benchmark",
    "Cross-locus transfer via memory"
]
embeddings = engine.embed(texts)  # shape: (2, 384)

# Compute similarity
sim = engine.cosine_similarity(embeddings[0], embeddings[1])
print(f"Similarity: {sim:.3f}")  # 0.73
```

### 3. Project Parser (`src/acquisition/project_parser.py`)

Extracts metadata from project directories:
- Supports: `project.yaml`, git repos, directory scan
- Auto-detects domain (genomics, NLP, CV, etc.)

**Usage:**
```python
from src.acquisition.project_parser import ProjectParser

parser = ProjectParser("../ARCHCODE")
metadata = parser.parse()

print(metadata)
# {
#   "name": "ARCHCODE",
#   "domain": "genomics",
#   "file_count": 847,
#   "type": "git_repo"
# }

key_files = parser.get_key_files()
# Returns: readme, decisions, active_context, code_files
```

---

## Day 1 Checklist

- [x] Repository structure created
- [x] Dependencies documented (`requirements.txt`, `pyproject.toml`)
- [x] Graph manager with Neo4j + NetworkX fallback
- [x] Embeddings engine with caching
- [x] Project parser with domain detection
- [x] Setup test script (`setup_test.py`)
- [ ] Claude API integration (Day 2)
- [ ] 7-pass generator (Day 2-3)
- [ ] Transfer test (Day 4-5)

---

## Next Steps

**Day 2-3:** Implement 7-pass generator
- Port current prompt to `seven_pass.py`
- Integrate Claude API
- Generate 10 hypotheses for ARCHCODE

**Day 4-5:** Transfer test
- Analyze 3 projects (ARCHCODE, ChernoffPy, ContextProof)
- Compute hypothesis embeddings
- Test cross-project retrieval

**Day 6:** Go/No-Go decision
- Measure transfer rate (target: ≥20%)
- Measure Recall@3 (target: ≥0.60)
- Decide: continue to full 14-day plan or pivot

---

## Architecture Decisions

**ADR-001:** NetworkX fallback (2026-05-08)
- **Context:** Neo4j requires Docker, may not be available on all systems
- **Decision:** Use NetworkX as fallback (in-memory graph)
- **Trade-off:** NetworkX = not persistent (need manual save), но zero setup cost
- **Mitigation:** `save_to_file()` / `load_from_file()` for persistence

**ADR-002:** sentence-transformers for embeddings (2026-05-08)
- **Context:** Need fast, good-quality embeddings для hypothesis similarity
- **Decision:** `all-MiniLM-L6-v2` (384-dim, 0.42s для 1K sentences)
- **Alternative rejected:** OpenAI embeddings (cost $0.13/1M tokens, external dependency)
- **Trade-off:** Local model = slower first run (300MB download), но no API costs

---

**Version:** 0.1.0 (Day 1 MVP)  
**Status:** ✅ Setup complete, ready for Day 2  
**Author:** Sergey Boyko (ARCHCODE Project)
