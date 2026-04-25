#!/bin/bash

# Root
mkdir -p smart-entry-ai
cd smart-entry-ai

# App structure
mkdir -p app/api/routes
mkdir -p app/core
mkdir -p app/agents
mkdir -p app/services/pdf
mkdir -p app/services/ocr
mkdir -p app/services/vision
mkdir -p app/services/llm
mkdir -p app/services/exports
mkdir -p app/services/detection
mkdir -p app/schemas/mapping_profiles
mkdir -p app/memory
mkdir -p app/utils
mkdir -p app/constants/prompts

# Frontend
mkdir -p frontend/pages
mkdir -p frontend/components

# Data
mkdir -p data/uploads data/processed data/cache data/models data/company_schemas

# Tests
mkdir -p tests/fixtures/expected_outputs

# Scripts
mkdir -p scripts

# -------- FILES --------

touch app/main.py app/config.py app/dependencies.py
touch app/api/router.py
touch app/api/routes/upload.py app/api/routes/process.py app/api/routes/schema.py app/api/routes/memory.py

touch app/core/orchestrator.py app/core/pipeline.py app/core/state.py

touch app/agents/base_agent.py app/agents/extraction_agent.py app/agents/vision_agent.py app/agents/validation_agent.py app/agents/mapping_agent.py

touch app/services/pdf/pdfplumber_service.py app/services/pdf/pymupdf_service.py
touch app/services/ocr/easyocr_service.py
touch app/services/vision/preprocessing.py
touch app/services/llm/groq_service.py app/services/llm/gemini_service.py
touch app/services/exports/excel_exporter.py app/services/exports/csv_exporter.py
touch app/services/detection/input_classifier.py

touch app/schemas/base_schema.py app/schemas/company_schema.py app/schemas/validation.py app/schemas/responses.py
touch app/schemas/mapping_profiles/odoo.json app/schemas/mapping_profiles/sap.json app/schemas/mapping_profiles/generic_excel.json

touch app/memory/chroma_client.py app/memory/sqlite_store.py app/memory/schema_memory.py app/memory/correction_store.py app/memory/embeddings.py app/memory/audit_log.py

touch app/utils/logger.py app/utils/file_utils.py app/utils/text_cleaning.py

touch app/constants/prompts/extraction_prompts.py app/constants/prompts/validation_prompts.py app/constants/prompts/mapping_prompts.py

touch frontend/app.py
touch frontend/pages/upload.py frontend/pages/results.py frontend/pages/schema_config.py
touch frontend/components/preview.py

touch tests/conftest.py tests/test_pipeline.py tests/test_agents.py tests/test_services.py
touch tests/fixtures/sample_invoice.pdf tests/fixtures/sample_photo.jpg

touch scripts/run_backend.sh scripts/run_frontend.sh scripts/reset_db.py

touch .env requirements.txt README.md .gitignore

echo "✅ Project structure created successfully!"