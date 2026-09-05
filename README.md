# Enterprise Multimodal RAG Knowledge Platform

A production-oriented Retrieval-Augmented Generation (RAG) platform for securely uploading documents, processing them asynchronously, retrieving relevant context, and generating grounded answers with source references.

The system combines FastAPI, React, PostgreSQL with pgvector, Redis/RQ, MinIO, Ollama, Prometheus, Grafana, Docker, and GitHub Actions into a complete end-to-end AI application.

---

## Overview

This project was built to demonstrate how an enterprise-style RAG system can go beyond a basic chatbot.

Users can:

- Register and log in securely
- Upload PDF, DOCX, PNG, and JPEG files
- Process documents asynchronously
- Extract and chunk document content
- Generate vector embeddings
- Search across uploaded documents
- Ask grounded questions using RAG
- Continue conversations with follow-up questions
- View the source pages used for an answer
- Manage their own documents
- Monitor system health and performance

The platform also includes authentication, authorization, background workers, observability, automated testing, CI/CD, and Docker-based deployment support.

---

## Key Features

### Multimodal Document Ingestion

Supports:

- PDF documents
- DOCX documents
- PNG images
- JPEG images

Uploaded files are stored in MinIO and processed asynchronously using Redis Queue workers.

---

### Structured Chunking

Instead of splitting documents only by character count, the ingestion pipeline preserves document structure such as:

- Parent sections
- Subsections
- Page numbers
- Chunk indexes
- Chunk types

This metadata is stored together with each chunk and used during retrieval.

---

### Contextual Embeddings

The embedding representation includes:

- Parent section title
- Section title
- Chunk text

Embeddings are generated using:

`sentence-transformers/all-MiniLM-L6-v2`

Vector size:

`384`

Embeddings are stored in PostgreSQL using the pgvector extension.

---

## RAG Pipeline

The query flow is:

```text
User Question
      |
      v
Authentication
      |
      v
Document Access Control
      |
      v
Conversation Context
      |
      v
Follow-up Query Rewriting
      |
      v
Vector Retrieval
      |
      v
Relevant Document Chunks
      |
      v
Prompt Construction
      |
      v
Ollama LLM
      |
      v
Grounded Answer + Sources
The LLM is instructed to answer only from retrieved document context and clearly state when there is insufficient evidence.

Conversation Memory

The application supports multi-turn conversations.

For follow-up questions, previous conversation messages are used to rewrite ambiguous queries into standalone retrieval questions.

Example:

User:
What is Bayes theorem?

User:
How is it used in disease testing?

The second question can be rewritten internally so that retrieval understands the original topic.

Document-Level Access Control

Each uploaded document belongs to a specific user.

Normal users can:

List only their documents
View only their documents
Delete only their documents
Query only their documents

Administrator accounts can access documents across users.

Unauthorized document access returns a 404 response rather than exposing the existence of another user's resource.

Authentication

Authentication is implemented using:

JWT access tokens
Argon2 password hashing
Role-based authorization
Protected FastAPI routes

Supported roles:

user
admin

Main authentication endpoints:

POST /auth/register
POST /auth/login
GET  /auth/me
Background Processing

Document ingestion runs asynchronously through Redis Queue.

Processing workflow:

Upload
  |
  v
MinIO Storage
  |
  v
RQ Job
  |
  v
Document Worker
  |
  v
Parsing
  |
  v
Chunking
  |
  v
Embedding Generation
  |
  v
PostgreSQL + pgvector

RQ retry support is enabled for failed document-processing jobs.

Observability

The platform includes production-style monitoring.

Health Checks

Endpoint:

GET /health

The endpoint verifies:

API
PostgreSQL
Redis
MinIO

Example response:

{
  "status": "healthy",
  "services": {
    "api": "healthy",
    "postgres": "healthy",
    "redis": "healthy",
    "minio": "healthy"
  }
}
Prometheus Metrics

Metrics endpoint:

GET /metrics

Tracked metrics include:

HTTP request count
HTTP request latency
Total RAG queries
Total document uploads
RQ queued jobs
RQ started jobs
RQ failed jobs
RQ finished jobs
Grafana Dashboard

Grafana provides dashboards for:

Total RAG queries
Document uploads
API request volume
API request rate
API latency
RQ queue statistics
Worker failures
Technology Stack
Backend
Python 3.12
FastAPI
SQLAlchemy
Pydantic
JWT Authentication
Argon2 password hashing
AI / Retrieval
Retrieval-Augmented Generation
Sentence Transformers
pgvector
Ollama
Follow-up query rewriting
Multi-document retrieval
Storage and Infrastructure
PostgreSQL
pgvector
Redis
Redis Queue
MinIO
Docker
Docker Compose
Frontend
React
TypeScript
Vite
React Markdown
Nginx
Monitoring
Prometheus
Grafana
Structured Python logging
Testing and CI/CD
Pytest
FastAPI TestClient
GitHub Actions
Project Structure
enterprise-multimodal-rag/
├── api/
├── auth/
├── config/
├── database/
├── ingestion/
├── monitoring/
├── retrieval/
├── storage/
├── workers/
├── tests/
├── frontend/
├── .github/
│   └── workflows/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
Running the Project with Docker
1. Clone the Repository
git clone https://github.com/TripuraSindhuNadimpalli/enterprise-multimodal-rag.git
cd enterprise-multimodal-rag
2. Create Environment File
cp .env.example .env

Update the values in .env before using the project outside local development.

Do not commit the real .env file.

3. Start Ollama

The current local deployment uses Ollama for generation.

Make sure Ollama is running before starting the complete RAG workflow.

Example:

ollama serve

The configured model must also be available locally.

4. Start the Application
docker compose up -d --build

Check running services:

docker compose ps
Local Service URLs

After Docker Compose starts successfully:

Frontend
http://localhost:8080

FastAPI
http://localhost:8000

Swagger API Documentation
http://localhost:8000/docs

Health Check
http://localhost:8000/health

Prometheus Metrics
http://localhost:8000/metrics

MinIO Console
http://localhost:9001

Prometheus
http://localhost:9091

Grafana
http://localhost:3001
Document Upload Workflow

After logging in:

Open the Documents section.
Select a supported file.
Upload the document.
The upload is stored in MinIO.
An RQ background job is created.
The worker processes and embeds the document.
The document becomes available for RAG queries.

Processing status can progress through:

Queued
Processing
Finished
Ask AI

Once a document has been processed, select it and ask a question.

Example:

What are the technologies used in Project 1?

The platform retrieves relevant chunks and produces a grounded answer.

Example result:

FastAPI
React
PostgreSQL
Redis
LangGraph
LangChain
Qdrant
Docker
Kubernetes
AWS/GCP

Retrieved source pages are displayed separately in the frontend.

API Endpoints

Main endpoint groups include:

/auth
/documents
/query
/health
/metrics

Important document endpoints:

POST   /documents/upload
GET    /documents
GET    /documents/{document_id}
DELETE /documents/{document_id}
GET    /documents/jobs/{job_id}

RAG query endpoint:

POST /query
Testing

Run backend tests from the project root:

pytest tests/test_auth.py tests/test_document_access.py tests/test_query_access.py -v

The automated test suite covers:

User registration
Login
Invalid authentication
Protected endpoints
Document ownership
Cross-user document access
Query authorization
Conversation privacy
Continuous Integration

GitHub Actions automatically runs on pushes and pull requests to the main branch.

The CI pipeline:

Checkout Repository
      |
      v
Create PostgreSQL + pgvector Service
      |
      v
Install Python Dependencies
      |
      v
Enable pgvector
      |
      v
Initialize Database
      |
      v
Run Backend Tests

A separate frontend job:

Install Node.js
      |
      v
npm ci
      |
      v
npm run build

Both backend tests and frontend production builds must pass.

Docker Architecture

The Docker Compose environment contains:

React / Nginx Frontend
          |
          v
      FastAPI API
       /      \
      v        v
PostgreSQL    Redis
 + pgvector     |
                v
             RQ Worker
                |
                v
              MinIO

Monitoring:

FastAPI Metrics
      |
      v
Prometheus
      |
      v
Grafana

The local LLM is accessed through Ollama running on the host machine.

Retrieval Evaluation

Multiple retrieval strategies were explored during development, including:

Semantic vector retrieval
Hybrid retrieval
Reranking

Evaluation experiments were used to compare retrieval quality.

For the tested document set, semantic retrieval produced strong ranking performance and was retained as the practical retrieval path.

Security Considerations

The application implements several security controls:

Password hashing with Argon2
JWT authentication
Role-based access control
Per-user document ownership
Conversation ownership
Protected upload and query endpoints
Restricted cross-user access
Environment-based secrets
.env exclusion from Git
CORS configuration

Production deployments should use strong secrets and managed credentials instead of development defaults.

Production Considerations

The current Docker Compose environment is designed for local development and portfolio demonstration.

For a production deployment, recommended improvements include:

Managed PostgreSQL with pgvector
Managed Redis
S3-compatible object storage
External or managed LLM inference
HTTPS
Reverse proxy
Secret management
Centralized logging
Autoscaling workers
Persistent monitoring
Production-grade database migrations
Future Improvements

Potential extensions include:

RAG evaluation dashboard
Groundedness scoring
Citation quality scoring
Retrieval precision and recall tracking
Additional file formats
Streaming LLM responses
Admin dashboard
Kubernetes deployment
Managed cloud LLM integration
Advanced reranking
Agentic document workflows
What This Project Demonstrates

This project demonstrates practical experience with:

Generative AI
Retrieval-Augmented Generation
Backend engineering
REST API development
Vector databases
Asynchronous job processing
Authentication and authorization
React frontend development
PostgreSQL
Redis
Object storage
Docker
Observability
Automated testing
CI/CD
Production-oriented system design

Author

Tripura Sindhu Nadimpalli

GitHub:
https://github.com/TripuraSindhuNadimpalli
