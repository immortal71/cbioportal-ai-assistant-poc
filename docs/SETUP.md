# Setup Instructions

**Author:** Aashish Kharel  
**Project:** cBioPortal AI Assistant PoC - GSoC 2026

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/immortal71/cbioportal-ai-assistant-poc.git
cd cbioportal-ai-assistant-poc
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure LLM (Optional but Recommended)

The POC works with or without LLM, but LLM integration provides much better results.

#### Option A: Use Claude (Recommended)
```bash
# Get free API key from https://console.anthropic.com/
# You get $5 free credit (enough for 500+ queries)

# Create .env file
cp .env.example .env

# Edit .env and add your key:
ANTHROPIC_API_KEY=your_key_here
LLM_PROVIDER=anthropic
```

#### Option B: Use OpenAI
```bash
# Get API key from https://platform.openai.com/
# New accounts get $5 free credit

# Edit .env and add your key:
OPENAI_API_KEY=your_key_here
LLM_PROVIDER=openai
```

#### Option C: Skip LLM (Basic Mode)
```bash
# POC will work with pattern matching only
# No configuration needed
```

### 4. Run Backend
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 5. Open Frontend
```bash
# Open frontend/index.html in your browser
# Or navigate to: file:///path/to/frontend/index.html
```

## Testing

### Test LLM Parser
```bash
# Make sure you've set ANTHROPIC_API_KEY or OPENAI_API_KEY
python test_llm_parser.py
```

### Test API Integration
```bash
python test_comprehensive.py
```

### Test Individual Queries
```bash
python test_api.py
```

## Environment Variables

Create a `.env` file with:

```env
# LLM Provider (anthropic or openai)
LLM_PROVIDER=anthropic

# API Keys (only one needed)
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
```

## Project Structure

```
cbioportal-ai-assistant-poc/
├── backend/
│   └── main.py              # FastAPI server
├── frontend/
│   └── index.html           # Web interface
├── tests/
│   ├── test_queries.json    # 30 test queries
│   └── test_results.json    # Test results (generated)
├── docs/
│   ├── LLM_INTEGRATION.md   # LLM docs
│   └── SETUP.md             # This file
├── config.py                # Configuration
├── llm_parser.py            # LLM integration
├── test_llm_parser.py       # LLM test suite
├── test_api.py              # API tests
├── test_comprehensive.py    # Full integration tests
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment file
└── README.md                # Project overview
```

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check port 8000
# Windows: netstat -ano | findstr :8000
# Mac/Linux: lsof -i :8000
```

### LLM not working
```bash
# Verify API key is set
python -c "import os; print(os.getenv('ANTHROPIC_API_KEY'))"

# Test with simple query
python test_llm_parser.py
```

### Frontend can't connect
- Make sure backend is running on port 8000
- Check browser console for errors (F12)
- Verify CORS is enabled in backend

## Getting API Keys

### Anthropic Claude
1. Go to https://console.anthropic.com/
2. Sign up for free account
3. Get $5 free credit
4. Create API key
5. Copy to `.env` file

### OpenAI
1. Go to https://platform.openai.com/
2. Sign up for account
3. Get $5 credit (new accounts)
4. Create API key
5. Copy to `.env` file

## Cost Estimates

With free tier credits:
- **Testing (100 queries):** $1-3
- **POC Development:** $5-10
- **Free credits cover:** 200-500 queries

Both providers' free tiers are sufficient for POC testing.

## Next Steps

After setup:
1. Test with example queries
2. Run LLM test suite
3. Review test results
4. Try your own queries
5. Check documentation in `docs/`

## Support

For issues or questions:
- Review [LLM Integration Guide](docs/LLM_INTEGRATION.md)
- Check [Test Results](tests/test_results.json)
- See [GitHub Issue #274](https://github.com/nrnb/GoogleSummerOfCode/issues/274)
