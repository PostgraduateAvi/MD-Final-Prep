# MD Exam Prep API Usage Guide

## Overview

The `md_exam_prep_api.py` implements a FastAPI server that provides medical exam preparation endpoints following the OpenAPI specification defined in `openapi.yaml`.

## Starting the API Server

```bash
# Start the API server on port 8001
python3 md_exam_prep_api.py
```

The server will be available at `http://localhost:8001`

## API Endpoints

### 1. Get Content for a Topic
**GET** `/content/{topic}`

Retrieves medical content for a specific topic.

```bash
# Example: Get content for cardiology
curl http://localhost:8001/content/cardiology

# Example: Get content for diabetes
curl http://localhost:8001/content/diabetes
```

**Available Topics:**
- `cardiology` - Cardiovascular medicine
- `rheumatology` - Joint and autoimmune conditions  
- `neurology` - Neurological conditions
- `kidney_disease` - Nephrology and renal medicine
- `diabetes` - Diabetes management
- `hypertension` - Blood pressure management
- `heart_failure` - Cardiac failure conditions
- `pneumonia` - Respiratory infections
- `gastroenterology` - Digestive system

### 2. Summarize a Topic
**POST** `/summarize`

Generates high-yield summary points for a topic.

```bash
# Example: Summarize cardiology
curl -X POST -H "Content-Type: application/json" \
     -d '{"topic": "cardiology"}' \
     http://localhost:8001/summarize
```

**Response:**
```json
{
  "topic": "cardiology",
  "summary": [
    "Key clinical considerations for cardiology",
    "Diagnostic and therapeutic approaches",
    "Important management principles"
  ]
}
```

### 3. Predict Exam Topics
**GET** `/predict?limit={number}`

Returns the most likely topics that may appear on examinations.

```bash
# Example: Get top 3 predicted topics
curl "http://localhost:8001/predict?limit=3"

# Example: Get top 5 predicted topics  
curl "http://localhost:8001/predict?limit=5"
```

**Response:**
```json
{
  "predictions": [
    {"topic": "hypertension", "score": 1.0},
    {"topic": "neurology", "score": 0.96},
    {"topic": "diabetes", "score": 0.96}
  ]
}
```

## Interactive Documentation

Visit `http://localhost:8001/docs` for interactive Swagger UI documentation where you can test all endpoints directly in your browser.

## Health Check

```bash
# Check if the API is running
curl http://localhost:8001/health
```

## Testing the API

Run the test script to verify all endpoints are working:

```bash
python3 test_md_exam_prep_api.py
```

## Integration with Existing Server

The MD Exam Prep API runs on port 8001 to avoid conflicts with the existing `server.py` (port 8000). Both can run simultaneously:

- **Existing server** (`server.py`): `http://localhost:8000` - File operations, tokenization
- **New API** (`md_exam_prep_api.py`): `http://localhost:8001` - Medical content access

## Data Source

The API processes content from the `tokenized_content.json` file, which contains:
- Harrison's Internal Medicine textbooks (10 files)
- Medical guidelines (13 files) 
- Neurology textbooks (8 files)
- Question papers (25 files)

Total: 19.2M tokens across 56 medical files covering comprehensive MD exam topics.