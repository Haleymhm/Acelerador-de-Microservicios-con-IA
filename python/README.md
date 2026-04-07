# 🚀 Risk Analysis Accelerator — Python Boilerplate

AI-powered microservice for **automated risk detection** and **dependency identification** using Amazon Bedrock (Claude 3).

## 📋 Features

| Feature | Description |
|---|---|
| **Risk Detection** | Identifies risks with probability/impact scores and mitigation suggestions |
| **Dependency Mapping** | Extracts component dependency graphs from unstructured text |
| **Document Ingestion** | Supports text, Markdown, PDF and images via Amazon Textract |
| **Async Processing** | Non-blocking background analysis with FastAPI Background Tasks |
| **Structured LLM Output** | JSON schema enforcement on all Bedrock (Claude 3) responses |

## 🏗️ Architecture

```
app/
├── api/v1/          # FastAPI endpoints (health, analysis)
├── core/            # Config (Pydantic Settings) + AWS provider (aioboto3)
├── models/          # Pydantic schemas (risk, dependency, analysis)
└── services/        # Business logic (Textract, Bedrock, RiskAnalyzer)
```

**Analysis Pipeline:**

```
Document → Textract (text extraction)
                ↓
        Bedrock Claude 3
         ┌──────┴──────┐
   Step 1: Dependencies   Step 2: Risks
   (graph: nodes/edges)   (probability/impact)
         └──────┬──────┘
              DynamoDB
           (persistence)
```

## ⚡ Quick Start

### 1. Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- AWS credentials configured (`~/.aws/credentials` or environment variables)

### 2. Install

```bash
cd python/
poetry install
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env with your AWS settings
```

### 4. Run

```bash
poetry run uvicorn app.main:app --reload --port 8000
```

### 5. Explore

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health check |
| `POST` | `/api/v1/analysis/analyze` | Submit raw text for analysis |
| `POST` | `/api/v1/analysis/analyze/file` | Upload a document for analysis |
| `GET` | `/api/v1/analysis/{analysis_id}` | Retrieve analysis results |

### Example: Submit Text Analysis

```bash
curl -X POST http://localhost:8000/api/v1/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The payment service depends on the user authentication module. There is a critical risk that the database migration may fail during peak hours, causing downtime for all dependent services.",
    "source_filename": "project-notes.md"
  }'
```

**Response (202 Accepted):**

```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Analysis has been submitted for processing"
}
```

### Example: Get Results

```bash
curl http://localhost:8000/api/v1/analysis/550e8400-e29b-41d4-a716-446655440000
```

## 🐳 Docker

```bash
docker build -t risk-analysis-accelerator .
docker run -p 8000:8000 --env-file .env risk-analysis-accelerator
```

## 🧪 Development

```bash
# Run tests
poetry run pytest tests/ -v

# Lint
poetry run ruff check app/

# Type check
poetry run mypy app/ --strict
```

## ☁️ AWS Services Used

| Service | Purpose |
|---|---|
| **Amazon Bedrock** | LLM invocation (Claude 3) for risk/dependency analysis |
| **Amazon Textract** | Document text extraction (PDF, images) |
| **Amazon S3** | Document storage |
| **Amazon DynamoDB** | Analysis result persistence |

## 📄 License

MIT
