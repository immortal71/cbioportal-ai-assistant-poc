# Quick Start Guide - LLM Integration

## Get Started in 5 Minutes

### Step 1: Get an API Key (2 minutes)

**Option A: Claude (Recommended)**
1. Go to https://console.anthropic.com/
2. Sign up for free account
3. Get $5 free credit
4. Create an API key
5. Copy the key

**Option B: OpenAI**
1. Go to https://platform.openai.com/
2. Sign up for free account  
3. Get $5 free credit
4. Create an API key
5. Copy the key

### Step 2: Set Up Environment (1 minute)

Create a `.env` file in the project root:

```bash
# For Claude
echo "LLM_PROVIDER=anthropic" > .env
echo "ANTHROPIC_API_KEY=your-actual-key-here" >> .env

# OR for OpenAI
echo "LLM_PROVIDER=openai" > .env
echo "OPENAI_API_KEY=your-actual-key-here" >> .env
```

### Step 3: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

### Step 4: Test It! (1 minute)

```bash
# Simple test
python llm_parser.py

# Run full test suite (30 queries)
python test_llm_comprehensive.py
```

## Example Usage

### Interactive Testing

```python
from llm_parser import LLMQueryParser
from gene_validator import GeneValidator

# Initialize
parser = LLMQueryParser()
validator = GeneValidator()

# Try some queries
queries = [
    "TP53 mutations in breast cancer",
    "EGFR and ALK in lung cancer",
    "What are the most common mutations in HER2+ breast cancer?"
]

for query in queries:
    print(f"\nQuery: {query}")
    result = parser.parse_query(query)
    
    print(f"  Genes: {result.genes}")
    print(f"  Cancer Types: {result.cancer_types}")
    print(f"  Query Type: {result.query_type}")
    print(f"  Confidence: {result.confidence}/10")
    
    # Validate genes
    if result.genes:
        validation = validator.validate_and_suggest(result.genes)
        print(f"  Valid: {validation['all_valid']}")
```

## What You Can Try

### Simple Queries
- "TP53 mutations in breast cancer"
- "EGFR in lung cancer"
- "BRCA1 mutations"

### Complex Queries
- "TP53 and BRCA1 co-mutations in ovarian cancer"
- "Compare KRAS mutations in colorectal vs pancreatic cancer"
- "Most common mutations in HER2-positive breast cancer"

### Edge Cases
- "Show me everything about BRAF" (tests clarity handling)
- "TP53, BRCA1, and EGFR in breast, ovarian, and lung cancer" (multi-entity)
- "KRAZ mutations" (typo - should suggest KRAS)

## Expected Results

**With Valid API Key:**
- 90%+ accuracy on diverse queries
- Confidence scores 7-10/10 for clear queries
- Typo suggestions for misspelled genes
- ~1-3 second response time

**Without API Key:**
- Error message with setup instructions
- Falls back to pattern matching
- Limited to simple query formats

## Costs

**Free Tier Coverage:**
- $5 credit = ~1,000-1,250 queries
- Perfect for POC and testing
- Enough for several demos

**Per Query:**
- ~$0.004 (less than half a cent)
- 100 queries = ~$0.40
- Very affordable for demonstration

## Troubleshooting

### "API key not set"
```bash
# Check if .env file exists
ls -la .env

# Check if key is loaded
python -c "from config import Config; print(Config.ANTHROPIC_API_KEY)"
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Rate limit exceeded"
```python
# Add delay between queries
import time
for query in queries:
    result = parser.parse_query(query)
    time.sleep(0.5)  # Wait 500ms between calls
```

## Next Steps

1. Run the comprehensive test suite:
   ```bash
   python test_llm_comprehensive.py
   ```

2. Check results:
   ```bash
   cat tests/TEST_RESULTS.md
   ```

3. Integrate with backend:
   - Update `backend/main.py` to use LLM parser
   - Add fallback to pattern matching
   - Test with frontend

4. Document your findings:
   - Success rate on test queries
   - Performance metrics
   - Cost estimates

## Support

- See `docs/LLM_INTEGRATION.md` for detailed documentation
- Check test results in `tests/TEST_RESULTS.md`
- Review example queries in `tests/test_queries.json`

---

**Ready to start?** Just run:
```bash
python test_llm_comprehensive.py
```
