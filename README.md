<p align="center">

# VAST Engine

*An enterprise-grade, local-first RAG infrastructure designed to process, index, and semantically search dense textual knowledge spaces without relying on external cloud APIs or proprietary black-box frameworks.*

<p>
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" />
  <img src="https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi" />
  <img src="https://img.shields.io/badge/Streamlit-UI-ff4b4b?logo=streamlit" />
  <img src="https://img.shields.io/badge/ChromaDB-VectorDB-6f42c1" />
  <img src="https://img.shields.io/badge/PyTorch-DeepLearning-ee4c2c?logo=pytorch" />
  <img src="https://img.shields.io/badge/Deploy-Render-46E3B7?logo=render" />
</p>

</p>

---

# Live Demo

**Frontend UI**

> https://vast-engine-ui.onrender.com

> **Note:** The application is deployed on **Render's Free Tier**. Backend instances automatically enter a sleep state after periods of inactivity. The initial request may therefore require several seconds while the service cold-starts.

---

# Online Walkthrough

## 1. The Cold Boot

When opening the application, VAST first intercepts the initial connection and displays a dedicated loading interface while attempting to wake the backend service.

This prevents users from interacting with an unavailable API and provides a deterministic startup sequence.

---

## 2. Manual Override

If the backend remains unavailable beyond the timeout threshold, the interface exposes a **Manual Override** control.

Selecting this button opens the backend endpoint in a separate browser tab, forcing Render to wake the sleeping instance.

---

## 3. Upload & Query

Once connectivity has been established:

- Status indicator changes to **green**
- Upload interface becomes available
- Accepts:

```
.txt
.md
```

Documents are immediately indexed and become searchable through semantic retrieval.

---

# Key Architectural Features

- **Microservice Architecture** — Decoupled **Streamlit frontend** and **FastAPI backend** communicating exclusively through REST APIs.

- **Local Dense Representation** — Utilizes the **SentenceTransformers `all-MiniLM-L6-v2`** encoder to project textual knowledge into **384-dimensional dense vector spaces**.

- **Deterministic Chunking Pipeline** — Employs a sliding token window with overlap to preserve contextual continuity across chunk boundaries.

- **Abstract Data Layer** — Repository Pattern abstraction isolates application logic from ChromaDB, enabling backend storage implementations to be replaced without affecting higher application layers.

---

# Cloud Optimizations (The 512MB RAM Challenge)

Deploying modern embedding models inside Render's **512MB Free Tier** required aggressive optimization.

## Austerity Mode Embedding

Tokenizer parallelism is explicitly disabled

```bash
TOKENIZERS_PARALLELISM=false
```

Embedding generation additionally forces

```python
batch_size = 8
```

during encoding, significantly reducing peak RAM consumption and preventing Out-Of-Memory process termination.

---

## Vectorless Telemetry

Administrative database statistics intentionally avoid loading dense embedding vectors.

Instead of

```python
include=["embeddings"]
```

VAST requests

```python
include=["metadatas"]
```

allowing health checks to execute without allocating large floating-point arrays.

---

## Single-Worker Execution

The FastAPI server intentionally runs as

```bash
uvicorn ... --workers 1
```

Multiple workers would duplicate the embedding model in memory, exceeding Render's RAM limitations.

---

## Smart Cold-Boot UI

The Streamlit frontend maintains connection state using

```python
st.session_state
```

A hidden polling loop repeatedly contacts the backend root endpoint.

Receiving a **404 HTTP response** confirms that FastAPI has fully initialized, allowing the interface to transition automatically from the loading screen to the operational state while masking backend cold-start latency.

---

# Mathematical Foundations

Traditional search engines rely primarily on **lexical keyword matching** (for example, **BM25**), where retrieval quality depends on exact token overlap between the query and indexed documents.

VAST instead represents text as **dense semantic vectors**, allowing conceptually related content to be retrieved even when the wording differs significantly.

Document relevance is computed using **Cosine Similarity**.

$$
\operatorname{CosineSimilarity}(q,d)=
\frac{q\cdot d}
{\|q\|_2\|d\|_2}
$$

Where:

- $q$ = Query embedding vector
- $d$ = Document embedding vector
- $q \cdot d$ = Dot product between vectors
- $\|q\|_2$ = Euclidean (L2) norm of the query vector
- $\|d\|_2$ = Euclidean (L2) norm of the document vector

Higher cosine similarity indicates stronger semantic relevance between the query and retrieved document.

---

# Project Structure

```text
VAST-Engine/
│
├── config/
│   └── Environmental settings
│
├── data/
│   └── Target domain data
│
├── src/
│   ├── api/
│   │   └── FastAPI routes
│   │
│   ├── core/
│   │   └── ML utilities & embedding engine
│   │
│   ├── repository/
│   │   └── Vector database connections
│   │
│   └── services/
│       └── Retrieval & indexing pipelines
│
├── tests/
│   └── Test suites
│
├── Dockerfile.backend
├── frontend.py
└── requirements.txt
```

---

# Offline Testing Guide

## 1. Clone Repository

```bash
git clone https://github.com/<username>/VAST-Engine.git

cd VAST-Engine

python -m venv .venv

source .venv/bin/activate
```

Windows

```bash
.venv\Scripts\activate
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Start Backend

```bash
uvicorn src.api.routes:app \
    --host 127.0.0.1 \
    --port 8000 \
    --reload
```

---

## 4. Start Frontend

```bash
export BACKEND_URL="http://127.0.0.1:8000/api/v1"

streamlit run frontend.py
```

Windows (PowerShell)

```powershell
$env:BACKEND_URL="http://127.0.0.1:8000/api/v1"

streamlit run frontend.py
```

---

# Upcoming Roadmap

- [ ] Multi-Format Parsing (PDF, DOCX, Markdown tables)

- [ ] Conversational Memory (Contextual follow-up queries)

- [ ] Dynamic Chunking (Semantic chunking boundaries)

---

## License

This project is intended for educational, research, and experimentation purposes. License terms may be updated as the project evolves.