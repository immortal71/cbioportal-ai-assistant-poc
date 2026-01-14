# LLM Integration Guide

**Author:** Aashish Kharel  
**Project:** cBioPortal AI Assistant - GSoC 2026  
**Date:** January 12, 2026

## Overview

This document explains how the LLM (Large Language Model) integration enhances the cBioPortal AI Assistant to understand complex natural language queries.

## Why LLM Integration?

**Before (Pattern Matching Only):**
- Limited to simple, predefined patterns
- Can't handle complex multi-gene queries
- No understanding of context or synonyms
- Fails on variations of phrasing

**After (LLM-Powered):**
- Understands natural language variations
- Handles complex multi-entity queries
- Extracts context and intent
- Provides confidence scores for reliability

## Architecture

```
User Query → LLM Parser → Structured Data → cBioPortal API → Results
                ↓
         (if low confidence)
                ↓
         Pattern Fallback
```

### Components

1. **LLM Parser (`llm_parser.py`)**
   - Sends query to Claude/GPT
   - Parses JSON response
   - Validates extracted entities
   - Returns structured data

2. **Configuration (`config.py`)**
   - API key management
   - Model selection
   - Confidence thresholds

3. **Validation Layer**
   - Gene name validation against cBioPortal database
   - Cancer type mapping
   - Confidence scoring

## Supported LLM Providers

### Option 1: Anthropic Claude (Recommended)

**Pros:**
- Excellent at structured outputs
- Better reasoning capabilities
- Competitive pricing

**Setup:**
```bash
# Get API key from https://console.anthropic.com/
export ANTHROPIC_API_KEY="your-key-here"
export LLM_PROVIDER="anthropic"
```

**Cost:**
- ~$0.01-0.03 per query
- Free tier: $5 credit (500+ test queries)

### Option 2: OpenAI GPT-4

**Pros:**
- Well-documented
- Fast response times
- Good JSON mode support

**Setup:**
```bash
# Get API key from https://platform.openai.com/
export OPENAI_API_KEY="your-key-here"
export LLM_PROVIDER="openai"
```

**Cost:**
- ~$0.02-0.04 per query
- Free tier: $5 credit on new accounts

## Query Parsing Process

### Step 1: Send Query to LLM

```python
user_query = "Show me TP53 and BRCA1 mutations in breast cancer"
parser = get_parser()
result = parser.parse_query(user_query)
```

### Step 2: LLM Returns Structured Data

```json
{
  "genes": ["TP53", "BRCA1"],
  "cancer_types": ["breast"],
  "query_type": "mutations",
  "filters": [],
  "confidence": 9,
  "reasoning": "Clear request for mutations in specific genes and cancer type"
}
```

### Step 3: Validation

- Check genes against cBioPortal gene list
- Validate cancer type names
- Verify confidence score > threshold

### Step 4: API Call or Fallback

- **High confidence (≥5/10):** Use LLM-parsed entities
- **Low confidence (<5/10):** Fall back to pattern matching
- **LLM unavailable:** Automatic fallback

## Confidence Scoring

The LLM provides a confidence score (1-10) indicating parse quality:

| Score | Meaning | Action |
|-------|---------|--------|
| 9-10 | Very confident | Use LLM parse |
| 7-8 | Confident | Use LLM parse |
| 5-6 | Moderate | Use LLM parse with caution |
| 3-4 | Low confidence | Consider fallback |
| 1-2 | Very uncertain | Use fallback |

## Error Handling

### Scenario 1: Invalid Gene Names
```python
# LLM extracts: ["TP53", "BRCAA"]  (typo)
valid, invalid = parser.validate_genes(genes, known_genes)
# Returns: valid=["TP53"], invalid=["BRCAA"]
# Suggest: "Did you mean BRCA1 or BRCA2?"
```

### Scenario 2: Ambiguous Query
```
Query: "Show me everything about cancer"
Confidence: 2/10
Action: Prompt user for clarification
```

### Scenario 3: LLM API Error
```python
try:
    result = parser.parse_query(query)
except Exception:
    # Automatically falls back to pattern matching
    result = fallback_parse(query)
```

## Performance Metrics

Expected results from testing:

- **Simple queries:** 95-100% accuracy
- **Medium queries:** 85-95% accuracy
- **Complex queries:** 75-90% accuracy
- **Overall:** 85-90% success rate

**Response Time:**
- LLM call: 1-3 seconds
- Pattern fallback: <100ms
- Total with cBioPortal API: 2-5 seconds

## Cost Analysis

For POC testing (100 queries):

| Provider | Per Query | 100 Queries | Free Tier |
|----------|-----------|-------------|-----------|
| Claude | $0.01-0.03 | $1-3 | $5 credit |
| GPT-4 | $0.02-0.04 | $2-4 | $5 credit |

**Total POC cost:** $5-10 (mostly covered by free credits)

## Testing

Run the test suite:

```bash
# Set your API key first
export ANTHROPIC_API_KEY="your-key"

# Run tests
python test_llm_parser.py
```

Tests cover:
- 10 simple queries
- 10 medium complexity queries
- 10 complex queries

Results saved to `tests/test_results.json`

## Future Enhancements

1. **Caching:** Cache parsed queries to reduce API calls
2. **Fine-tuning:** Train on cBioPortal-specific terminology
3. **Multi-turn conversations:** Support follow-up questions
4. **Explanation generation:** Have LLM explain results to users
5. **Query suggestions:** Generate related queries

## Security & Privacy

- API keys stored in environment variables
- No user queries logged or stored
- LLM providers' data retention policies apply
- Consider self-hosted LLM for sensitive data

## Troubleshooting

### Issue: "LLM not configured"
**Solution:** Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` environment variable

### Issue: Low confidence scores
**Solution:** Queries may be ambiguous. Add more context or rephrase

### Issue: API rate limits
**Solution:** Implement request throttling or upgrade API tier

### Issue: Invalid JSON response
**Solution:** LLM parser automatically retries and falls back

## References

- Anthropic Claude API: https://docs.anthropic.com/
- OpenAI API: https://platform.openai.com/docs/
- cBioPortal API: https://www.cbioportal.org/api/
