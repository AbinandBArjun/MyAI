# MyAI

MyAI is a personal knowledge-base assistant. It combines a React dashboard with a FastAPI backend, PostgreSQL storage, semantic search, and a local Ollama language model.

## Features

- Dashboard UI for personal notes, saved articles, news, and trends
- Create, read, update, and delete notes
- Automatic embedding generation for notes and stored articles
- Semantic retrieval over notes and articles using `all-MiniLM-L6-v2`
- Local RAG chat assistant powered by Ollama
- TechCrunch AI news feed integration
- FastAPI interactive documentation at `/docs`

## Architecture

```text
frontend/                 React + TypeScript + Vite dashboard
backend/app/api/          FastAPI routes for notes, articles, news, and chat
backend/app/models/       SQLAlchemy models and vector embeddings
backend/app/rag/          Embedding generation and similarity retrieval
backend/app/services/     Embedding persistence and Ollama chat service
```

The chat flow retrieves the most relevant notes and articles from PostgreSQL, then sends their content as context to the local Ollama model. Listing-style questions such as “show my notes” are handled directly so they do not depend only on semantic similarity.

## Prerequisites

- Python 3.11 or newer
- Node.js 18 or newer and npm
- PostgreSQL with the `pgvector` extension
- [Ollama](https://ollama.com/)
- The configured Ollama model:

  ```bash
  ollama pull qwen3:4b-instruct-2507-q4_K_M
  ```

## Backend Setup

From the repository root:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
pip install pgvector
```

Create a PostgreSQL database, enable pgvector, and configure the connection string in a `.env` file at the repository root:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/myai
```

For a PostgreSQL database, enable the extension once:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Create the application tables:

```bash
cd backend
python -m app.create_tables
```

Start the API:

```bash
cd backend
uvicorn app.main:app --reload
```

The backend runs at `http://localhost:8000`. OpenAPI documentation is available at `http://localhost:8000/docs`.

## Frontend Setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The Vite development server runs at `http://localhost:5173` and expects the backend at `http://localhost:8000`.

## Optional Data and Embeddings

The news endpoint reads the TechCrunch AI RSS feed. Existing articles and notes can have their missing vector embeddings generated with:

```bash
cd backend
python -m app.scripts.backfill_embeddings
```

The embedding model is downloaded by `sentence-transformers` the first time it is used.

## API Routes

| Method | Route | Description |
| --- | --- | --- |
| `GET` | `/` | Backend health response |
| `GET` | `/news/` | Latest TechCrunch AI news links |
| `GET` | `/articles/` | Stored articles |
| `GET` | `/notes/` | Stored notes |
| `POST` | `/notes/` | Create a note and its embedding |
| `PUT` | `/notes/{note_id}` | Update a note and regenerate its embedding |
| `DELETE` | `/notes/{note_id}` | Delete a note and its embedding |
| `POST` | `/chat/` | Answer a question using retrieved knowledge |

## Testing

From the repository root, with the backend environment configured:

```bash
pytest backend
```

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

## Project Status

MyAI is an active work in progress. The current setup is intended for local development, with the API, database, embedding model, and Ollama service running on the developer machine.