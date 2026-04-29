# SmartEntry — AI-Powered Invoice Processing System

> Upload a document. Get structured data. Watch it get smarter every time.

SmartEntry is a multi-agent AI system that reads invoices and sales reports — whether digital PDFs, scanned documents, or phone photos — extracts structured data, validates it, maps it to any ERP schema, and exports it to Excel. It learns from every correction made, improving accuracy over time.

---

## What It Does

| Step | What Happens |
|------|-------------|
| **Upload** | Drop a PDF or photo of a paper report |
| **Extract** | AI reads and pulls out all relevant fields |
| **Validate** | Rules engine checks for errors and flags low-confidence fields |
| **Map** | Data is translated into your company's ERP or Excel schema |
| **Export** | Download a clean, ready-to-import `.xlsx` file |
| **Learn** | Every correction you make is remembered for next time |

---

## Features

- **Dual-pipeline processing** — separate optimized pipelines for digital PDFs and camera photos
- **Vision AI extraction** — handles real-world photos with blur, shadows, and skewed angles
- **Arabic + English support** — EasyOCR handles both languages natively
- **Dynamic schema mapping** — adapts to any company's ERP format (SAP, Odoo, custom Excel)
- **Persistent memory** — remembers schemas, supplier patterns, and user corrections across sessions
- **Semantic similarity search** — finds similar past documents using vector embeddings
- **Confidence scoring** — every extracted field gets a confidence score so you know what to review
- **Full audit trail** — every extraction is logged with timestamp and approval record

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| LLM — text tasks | Groq (Llama 3) |
| LLM — vision tasks | Gemini 2.5 Flash |
| OCR | EasyOCR |
| Image preprocessing | OpenCV |
| PDF extraction | pdfplumber, PyMuPDF |
| Vector memory | ChromaDB + Sentence Transformers |
| Structured memory | SQLite |
| Schema validation | Pydantic |
| Data transformation | pandas |
| Excel export | openpyxl |
| Backend API | FastAPI |
| Frontend UI | Streamlit |

---

## Project Structure

```
smart-entry-ai/
│
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # Environment + settings
│   ├── dependencies.py          # Shared DI
│   │
│   ├── api/routes/              # API endpoints
│   │   ├── upload.py
│   │   ├── process.py
│   │   ├── schema.py
│   │   └── memory.py
│   │
│   ├── core/                    # Orchestration logic
│   │   ├── orchestrator.py      # Routes input to correct pipeline
│   │   ├── pipeline.py          # End-to-end flow
│   │   └── state.py             # Shared state between agents
│   │
│   ├── agents/                  # AI agents
│   │   ├── base_agent.py
│   │   ├── extraction_agent.py  # Text → structured JSON (Groq)
│   │   ├── vision_agent.py      # Image + OCR text → JSON (Gemini)
│   │   ├── validation_agent.py  # Field validation + confidence scoring
│   │   └── mapping_agent.py     # Maps to target ERP schema
│   │
│   ├── services/                # Tool wrappers
│   │   ├── pdf/                 # pdfplumber + PyMuPDF
│   │   ├── ocr/                 # EasyOCR
│   │   ├── vision/              # OpenCV preprocessing
│   │   ├── llm/                 # Groq + Gemini clients
│   │   ├── exports/             # Excel + CSV generation
│   │   └── detection/           # Input type classifier
│   │
│   ├── schemas/                 # Pydantic models + ERP profiles
│   │   ├── base_schema.py       # Universal extraction schema (Layer 1)
│   │   ├── company_schema.py    # Per-company output schema (Layer 2)
│   │   └── mapping_profiles/    # odoo.json, sap.json, generic_excel.json
│   │
│   ├── memory/                  # Memory system
│   │   ├── chroma_client.py     # Vector store
│   │   ├── sqlite_store.py      # Structured storage
│   │   ├── embeddings.py        # Sentence Transformers wrapper
│   │   ├── schema_memory.py     # Company schema persistence
│   │   ├── correction_store.py  # User correction learning
│   │   └── audit_log.py         # Full extraction audit trail
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   ├── file_utils.py
│   │   └── text_cleaning.py
│   │
│   └── constants/prompts/       # All LLM prompts centralized
│       ├── extraction_prompts.py
│       ├── validation_prompts.py
│       └── mapping_prompts.py
│
├── frontend/                    # Streamlit UI
│   ├── app.py
│   └── pages/
│       ├── upload.py            # File upload screen
│       ├── results.py           # Review + edit table
│       └── schema_config.py     # Company ERP setup
│
├── data/
│   ├── uploads/                 # Incoming files (gitignored)
│   ├── processed/               # Generated Excel outputs (gitignored)
│   ├── models/                  # EasyOCR model weights (gitignored)
│   └── company_schemas/         # Saved company configs
│
├── tests/
│   ├── conftest.py
│   ├── fixtures/                # Sample invoices + expected outputs
│   ├── test_pipeline.py
│   ├── test_agents.py
│   └── test_services.py
│
├── scripts/
│   ├── run_backend.sh
│   ├── run_frontend.sh
│   └── reset_db.py
│
├── .env
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd smart-entry-ai
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** First run will download EasyOCR model weights (~200MB). This is normal and only happens once. On demo day, make sure models are pre-downloaded.

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
GROQ_MODEL=llama-3.3-70b-versatile
```

Get your free API keys:
- Groq: https://console.groq.com
- Gemini: https://aistudio.google.com

---

## Running the System

### Backend (FastAPI)

```bash
python -m uvicorn app.main:app --reload
```

API docs available at: `http://127.0.0.1:8000/docs`

### Frontend (Streamlit)

```bash
streamlit run frontend/app.py
```

Or use the convenience scripts:

```bash
# Windows
scripts/run_backend.sh
scripts/run_frontend.sh
```

---

## How the Pipeline Works

```
                    ┌─────────────────┐
                    │   User Upload   │
                    │  PDF or Photo   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Orchestrator   │
                    │  Detects type   │
                    └──┬──────────┬───┘
                       │          │
          ┌────────────▼──┐   ┌───▼────────────┐
          │  PDF Pipeline │   │ Photo Pipeline │
          │               │   │                │
          │ pdfplumber or │   │ OpenCV →       │
          │ EasyOCR       │   │ EasyOCR →      │
          │     ↓         │   │ Gemini Vision  │
          │   Groq        │   └───────┬────────┘
          └──────┬────────┘           │
                 └─────────┬──────────┘
                           │
                  ┌────────▼────────┐
                  │  Same JSON out  │  ← both pipelines produce identical format
                  └────────┬────────┘
                           │
                  ┌────────▼────────┐
                  │ Validation Agent│  ← flags errors, scores confidence
                  └────────┬────────┘
                           │
                  ┌────────▼────────┐
                  │  Schema Mapper  │  ← translates to company ERP format
                  └────────┬────────┘
                           │
                  ┌────────▼────────┐
                  │  Excel Export   │
                  └─────────────────┘
```

---

## Memory System

The system has four layers of memory that improve accuracy over time:

**File Memory** — If the exact same file is uploaded again, the result is served instantly from cache with no reprocessing.

**Supplier Memory** — The system learns patterns per supplier. Once it knows that Supplier X always formats dates as `DD/MM/YYYY` and puts the total in a specific location, it applies that knowledge automatically on future documents from the same supplier.

**Correction Memory** — Every time a user fixes a wrong field in the review screen, that correction is stored. Next time a similar value appears, the system auto-corrects it. Example: if a user consistently changes `"$"` to `"USD"`, the system learns this.

**Semantic Memory** — ChromaDB stores vector embeddings of past documents. When a new document arrives, the system finds the most similar past document and uses its extraction strategy as a starting point — even if the layout has never been seen exactly before.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload a PDF or image file |
| `POST` | `/process` | Run the full extraction pipeline |
| `POST` | `/process/excel` | Export result as `.xlsx` |
| `POST` | `/schema/company` | Save a company ERP schema |
| `GET` | `/schema/company/{id}` | Retrieve a saved schema |
| `POST` | `/memory/save` | Manually save to memory |
| `POST` | `/memory/learn` | Store a user correction |

Full interactive API documentation: `http://127.0.0.1:8000/docs`

---

## ERP Schema Mapping

SmartEntry supports any ERP system through JSON mapping profiles located in `app/schemas/mapping_profiles/`.

Each profile maps the universal extracted fields to the target system's column names:

```json
{
  "company_id": "company_a",
  "erp_type": "odoo",
  "field_mapping": {
    "ref": "document_info.document_number",
    "invoice_date": "document_info.date",
    "partner_id": "parties.seller",
    "amount_untaxed": "totals.subtotal",
    "amount_tax": "totals.tax_amount",
    "amount_total": "totals.grand_total"
  }
}
```

Included profiles: `generic_excel.json`, `sap.json`, `odoo.json`

To add a new company, use the Schema Config page in the UI or `POST /schema/company`.

---

## Running Tests

```bash
pytest
```

Run a specific test file:

```bash
pytest tests/test_pipeline.py -v
```

Test fixtures (sample invoices and expected outputs) are located in `tests/fixtures/`.

---

## Branch Strategy

| Branch | Owner | Purpose |
|--------|-------|---------|
| `main` | Both | Stable, demo-ready code only |
| `branch/backend` | Member 1 | Agents, memory, API, orchestration |
| `branch/services-ui` | Member 2 | Services, tools, Streamlit frontend |

**Rule:** Never push directly to `main`. Merge together at agreed integration points only.

**Shared files** — coordinate before editing: `app/main.py`, `app/config.py`, `app/dependencies.py`, `requirements.txt`, `constants/prompts/`, `utils/logger.py`

---

## Environment Notes

- Python 3.10+ recommended
- First run downloads EasyOCR weights to `data/models/` — pre-download before demo day
- `data/uploads/`, `data/processed/`, and `data/models/` are gitignored — do not commit files from these directories
- All API keys live in `.env` only — never commit `.env` to the repository

---

## Future Improvements

- Auto schema detection for new companies
- Multi-user support with login
- Cloud deployment (Railway / Render)
- Better handling of handwritten fields
- Direct ERP API push (no Excel intermediary)
- Mobile-friendly UI

---

## Authors

Built as a course project for the Deep Generative Models course — Faculty of Artificial Intelligence.

---

*SmartEntry is not just an extraction tool — it is a learning AI system that improves with every document processed.*
