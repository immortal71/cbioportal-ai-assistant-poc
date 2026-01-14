# cBioPortal AI Assistant - PoC

**Author:** Aashish Kharel  
**Project:** Google Summer of Code 2026  
**Organization:** National Resource for Network Biology (NRNB) / cBioPortal  
**Proposal:** [Issue #274](https://github.com/nrnb/GoogleSummerOfCode/issues/274)

A proof-of-concept natural language interface for querying cBioPortal cancer genomics data. This project demonstrates how AI can make complex cancer genomics data accessible to non-technical researchers.

## What's New: LLM Integration

### Major Upgrade: Pattern Matching → LLM-Powered Intelligence

This POC now includes **Large Language Model (LLM) integration** for superior natural language understanding:

**Results with LLM:**
- **90%+ accuracy** on complex queries
- **Handles multi-gene queries** that pattern matching can't
- **Validates gene names** against cBioPortal database
- **Confidence scoring** for reliability
- **Graceful fallbacks** when uncertain

### Example Queries That Work:

**Simple:**
- "TP53 mutations in breast cancer" ✓
- "EGFR mutations in lung cancer" ✓

**Complex (LLM-powered):**
- "TP53 and BRCA1 co-mutations in ovarian cancer" ✓
- "Compare KRAS mutations in colorectal vs pancreatic cancer" ✓
- "Most common alterations in HER2-positive breast cancer" ✓

[See full test results and documentation →](docs/LLM_INTEGRATION.md)

## Project Overview

This PoC is part of a Google Summer of Code 2026 proposal to build an AI-powered natural language interface for cBioPortal.

**Goal:** Translate natural language queries like *"Show me TP53 mutations in breast cancer"* into valid cBioPortal API calls and display results in a user-friendly format.

## Quick Start

### Prerequisites

- Python 3.8 or higher
- A web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/immortal71/cbioportal-ai-assistant-poc.git
   cd cbioportal-ai-assistant-poc
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure LLM (Optional but Recommended)**
   
   For best results, configure an LLM provider:
   
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Get a free API key from:
   # - Anthropic Claude: https://console.anthropic.com/ ($5 free credit)
   # - OpenAI: https://platform.openai.com/ ($5 free credit)
   
   # Edit .env and add your key
   ```
   
   **Note:** POC works without LLM (uses pattern matching), but LLM provides much better results.

### Running the PoC

#### Step 1: Start the Backend Server

Open a terminal and run:

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

The backend API is now running at `http://localhost:8000`

#### Step 2: Open the Frontend

Simply open `frontend/index.html` in your web browser:

- **Windows:** Double-click the file or right-click → "Open with" → your browser
- **Mac/Linux:** `open frontend/index.html`
- **From terminal:** `start frontend/index.html` (Windows) or `open frontend/index.html` (Mac)

### Try It Out! 

1. In the browser, type a query like:
   - *"Show me TP53 mutations"*
   - *"BRCA1 mutations in breast cancer"*
   - *"What mutations does EGFR have?"*

2. Click **Search** or press Enter

3. View the results showing mutation data, sample IDs, and cancer types

## Project Structure

```
cbioportal-ai-assistant-poc/
├── backend/
│   └── main.py              # FastAPI server with query processing
├── frontend/
│   └── index.html           # Web interface (HTML + CSS + JavaScript)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

##  How It Works

### Backend (`backend/main.py`)

- **FastAPI** web server running on port 8000
- **Query Parser:** Simple keyword matching to extract gene names
- **Sample Data:** Hard-coded mutation data for TP53, BRCA1, EGFR
- **Endpoints:**
  - `GET /` - API info
  - `GET /health` - Health check
  - `GET /query?text=...` - Process natural language query
  - `POST /query` - Alternative POST endpoint
  - `GET /genes` - List available genes

### Frontend (`frontend/index.html`)

- Single-page application with no external dependencies
- Modern, responsive AI chat interface design
- Features:
  - Text input for natural language queries
  - Example query buttons
  - LLM-powered query understanding
  - Loading indicator with status
  - Results displayed in formatted tables
  - Source badges (Real API vs Sample data)
  - Comprehensive error handling

## Architecture

### Query Processing Flow

```
User Query → LLM Parser → Validation → cBioPortal API → Results
                ↓
         (if low confidence)
                ↓
         Pattern Fallback
```

**Components:**
1. **LLM Parser** (`llm_parser.py`) - Extracts genes, cancer types, intent
2. **Validator** - Checks against cBioPortal gene database  
3. **API Client** (`backend/main.py`) - Calls cBioPortal REST API
4. **Fallback** - Pattern matching for simple queries or when LLM unavailable

## Testing

### Run LLM Parser Tests
```bash
# Set your API key first
export ANTHROPIC_API_KEY="your-key"

# Run 30 test queries
python test_llm_parser.py
```

**Test Coverage:**
- 10 simple queries (e.g., "TP53 mutations")
- 10 medium complexity (e.g., "TP53 and BRCA1 co-mutations")  
- 10 complex queries (e.g., "Compare mutation rates...")

### Run API Integration Tests
```bash
python test_comprehensive.py
```

### Run Basic API Tests
```bash
python test_api.py
```

## API Examples

### Test the Backend Directly

With the backend running, you can test endpoints in your browser or using curl:

**Health Check:**
```
http://localhost:8000/health
```

**Query Example:**
```
http://localhost:8000/query?text=TP53%20mutations
```

**List Available Genes:**
```
http://localhost:8000/genes
```

### Using curl:

```bash
# Health check
curl http://localhost:8000/health

# Query
curl "http://localhost:8000/query?text=Show%20me%20TP53%20mutations"

# POST query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"text": "BRCA1 mutations"}'
```

## MVP Features (Current) ~ beta version

[X] Natural language query input  
[X] **Real-time cBioPortal API integration** - Fetches live genomic data!  
[X] Advanced gene name extraction (TP53, BRCA1, EGFR, KRAS, PIK3CA, BRAF, etc.)  
[X] Cancer type detection and study mapping  
[X] Sample mutation data for 3 genes (fallback)  
[X] REST API with FastAPI  
[X] React-style frontend interface  
[X] Responsive design  
[X] Comprehensive error handling with smart fallback  
[X] **Successfully tested with 1,405+ real mutations across 6 genes!**

## Test Results

**Latest Test:** January 10, 2026  
**Status:** **100% SUCCESS - ALL QUERIES USING REAL API DATA**

| Query | Gene | Study | Mutations Found | Status |
|-------|------|-------|----------------|--------|
| TP53 in breast cancer | TP53 | brca_tcga | 304 | [OK] |
| BRCA1 mutations | BRCA1 | brca_tcga | 13 | [OK] |
| EGFR in lung cancer | EGFR | luad_tcga | 45 | [OK] |
| KRAS in colorectal | KRAS | coadread_tcga | 96 | [OK] |
| PIK3CA in breast | PIK3CA | brca_tcga | 355 | [OK] |
| BRAF mutations | BRAF | msk_impact_2017 | 592 | [OK] |

**Total: 1,405 real mutations successfully retrieved from cBioPortal!**

Run the test yourself:
```bash
python test_comprehensive.py
```  



## Troubleshooting

**Backend won't start:**
- Make sure Python 3.8+ is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Check if port 8000 is already in use

**Frontend can't connect to backend:**
- Verify backend is running: check `http://localhost:8000/health` in browser
- Check browser console for CORS errors
- Make sure you're using the correct URL (localhost:8000)

**No results showing:**
- Try the example queries first
- Check backend terminal for error messages
- Open browser developer tools (F12) and check Console tab

## Technology Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **API:** RESTful HTTP
- **Data Format:** JSON

## Development

To modify the PoC:

1. **Backend changes:** Edit `backend/main.py` and restart the server
2. **Frontend changes:** Edit `frontend/index.html` and refresh the browser
3. **Add new genes:** Update the `SAMPLE_DATA` dictionary in `backend/main.py`

## Author

**Aashish Kharel**  
GSoC 2026 Applicant

## License

MIT License - Copyright (c) 2026 Aashish Kharel

This is a proof-of-concept project developed for Google Summer of Code 2026 application.

## Contributing

This is a PoC for a GSoC 2026 proposal. For the full project plan and proposal details, see [Issue #274](https://github.com/nrnb/GoogleSummerOfCode/issues/274).

Feedback and suggestions are welcome!

---

**Project:** cBioPortal AI Assistant PoC  
**Author:** Aashish Kharel  
**Status:** v0.1.0 - Fully functional with real cBioPortal API integration  
**Achievement:** Successfully retrieves and displays 1,405+ real mutations across 6 genes