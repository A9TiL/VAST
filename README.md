# VAST: Vector-Augmented Semantic Retrieval & Text-Generation Engine

VAST is an enterprise-grade, local-first Retrieval-Augmented Generation (RAG) infrastructure designed to process, index, and semantically search dense textual knowledge spaces without relying on external cloud APIs or proprietary black-box frameworks. 

The architecture bridges lightweight mathematical embedding spaces with robust software engineering patterns to achieve predictable, deterministic non-parametric retrieval.

---

## 🚀 Key Architectural Features

- **Local Dense Representation:** Utilizes a highly optimized dual-encoder model (`all-MiniLM-L6-v2`) mapping text streams into dense 384-dimensional vector spaces.
- **Deterministic Chunking Pipeline:** Implements a sliding token window mechanism to guarantee context preservation across chunk boundaries.
- **Singleton Model Lifecycle:** Guarantees that neural network weights are instantiated exactly once on application startup, enforcing rigorous memory management.
- **Abstract Data Layer:** Utilizes the Repository Pattern to completely decouple backend services from the underlying vector storage index (ChromaDB/FAISS).

---

## 📊 System Requirements & Constraints

### Functional Requirements
- Parse, clean, and ingest structural documents (`.txt`, `.md`).
- Convert text chunks into normalized vectors.
- Perform Maximum Inner Product Search (MIPS) or Cosine Similarity matching over the vector index.
- Execute guarded context injection into an LLM generation pipeline to mitigate hallucinations.

### Non-Functional Requirements
- **Search Latency:** Vector database query retrieval executed beneath $50\text{ ms}$.
- **Memory Footprint:** Application runtime bound to $< 512\text{ MB}$ RAM at steady-state.
- **Privacy-First:** Zero dependency on paid external embedding APIs or tracking services.

---

## 🧮 Mathematical Foundations

Traditional search frameworks rely on lexical keyword matching (e.g., BM25), which fails to capture semantic meaning. VAST resolves this by mapping textual sequences into a continuous vector space where semantic similarity corresponds to geometric proximity.

Given a user query vector $\vec{q}$ and a documented text chunk vector $\vec{d}$, VAST calculates the semantic relevance using **Cosine Similarity**:

$$\text{Similarity}(\vec{q}, \vec{d}) = \frac{\vec{q} \cdot \vec{d}}{\|\vec{q}\| \|\vec{d}\|} = \frac{\sum_{i=1}^{n} q_i d_i}{\sqrt{\sum_{i=1}^{n} q_i^2} \sqrt{\sum_{i=1}^{n} d_i^2}}$$

Where:
- $\vec{q} \cdot \vec{d}$ represents the dot product of the query and document vectors.
- $\|\vec{q}\|$ and $\|\vec{d}\|$ represent the Euclidean $L_2$ norms, normalizing the scores between $[-1, 1]$.

---

## 📂 Project Structure

```text
vast-engine/
├── config/          # Central environmental settings & boundaries
├── data/            # Target domain data divided into isolated testing zones
├── src/
│   ├── api/         # FastAPI web server interfaces & schemas
│   ├── core/        # Core ML utilities (chunking, embedding Singletons)
│   ├── repository/  # Abstract & concrete Vector DB connections
│   └── services/    # Orchestration pipelines (Ingestion, Generation)
├── tests/           # Automated integration and unit test suites
└── main.py          # Application bootstrapper
```

---

## 🛠️ Installation & Baseline Initialization

    Clone the repository and navigate to the project directory:
    Bash

    git clone [https://github.com/yourusername/vast-engine.git](https://github.com/yourusername/vast-engine.git)
    cd vast-engine

    Initialize your Python virtual environment:
    Bash

    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate

    Install requirements (once defined):
    Bash

    pip install -r requirements.txt