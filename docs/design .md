## 1. System Requirements Specification

#### I. Functional Requirements (FR)

   - Deterministic Ingestion Pipeline: The system must read local text, Markdown, and PDF documents, cleaning extraneous whitespaces and formatting issues.

   - Context-Preserving Chunking: The engine must split documents into configurable chunk sizes with a defined sliding token overlap to maintain cross-boundary context.

   - Vector Database Indexing: The system must convert text chunks into dense 384-dimensional vectors using a local embedding model and index them into a persistent vector store.

   - Semantic Retrieval Querying: The system must compute cosine similarity or maximum inner product search between an incoming query vector and the document index to return the top-k relevant text passages along with distance metrics.

   - Hallucination-Guarded Generation: The engine must pass the query and exact context passages to an external inference endpoint, utilizing strict system prompting to prevent the LLM from synthesizing information outside the provided text.

   #### II. Non-Functional Requirements (NFR)

   - Low-Latency Search Execution: The local database retrieval process (excluding the LLM generation step) must run in under 50 ms for a standard indexed dataset.

   - Zero-State Local Dependency: The data ingestion, embedding calculations, and vector retrieval must run entirely on consumer-grade local hardware without requiring external cloud data storage or paid third-party APIs.

   - Memory Efficiency: The embedding and database layers must consume less than 512 MB of local RAM during steady-state execution.

   - Domain Agnostic / Generalization: The ingestion and indexing logic must be abstract enough to process a completely new domain repository without modifying a single line of core application code.

## 2. Architectural Design Patterns

To demonstrate clean coding practices, the codebase will adhere to three core design principles:

- Singleton Pattern (Model Management)
Loading an ML model into memory from disk is an expensive operation. We will implement a Singleton wrapper around sentence-transformers to guarantee that the 90MB model file is instantiated exactly once on application startup and reused across all subsequent user queries.
Repository Pattern (Data Abstraction)

- Backend routes should not care whether we are using ChromaDB, FAISS, or a raw dictionary to query our vectors. We will define an abstract base class (VectorRepository) that acts as an interface. If someone asks why we chose ChromaDB, we can show them that our architecture allows swapping it for FAISS with a single line of config changes.
Dependency Injection (FastAPI Middleware)

- FastAPI's dependency injection system (Depends) to provide clean, testable access to our database sessions and model instances, isolating our HTTP layer entirely from our business logic.