"""
Small LLM Test - Respects Free Tier Rate Limits
Only runs 5 queries with delays
"""

import time
from llm_parser import LLMQueryParser
from gene_validator import GeneValidator

print("="*60)
print("SMALL LLM TEST (Free Tier Friendly)")
print("="*60)
print("\nRunning only 5 queries with delays to respect rate limits...\n")

parser = LLMQueryParser()
validator = GeneValidator()

# Just 5 carefully selected queries
test_queries = [
    "TP53 mutations in breast cancer",
    "EGFR and ALK in lung cancer", 
    "BRCA1 and BRCA2 in ovarian cancer",
    "KRAS in colorectal cancer",
    "PIK3CA mutations"
]

results = []
for i, query in enumerate(test_queries, 1):
    print(f"[{i}/5] Testing: \"{query}\"")
    
    try:
        result = parser.parse_query(query)
        
        if result and "genes" in result:
            genes = result.get("genes", [])
            cancer_types = result.get("cancer_types", [])
            confidence = result.get("confidence", 0)
            
            print(f"  ✓ Genes: {genes}")
            print(f"  ✓ Cancer: {cancer_types}")
            print(f"  ✓ Confidence: {confidence}/10")
            results.append("PASS")
        else:
            print(f"  ✗ Parse failed")
            results.append("FAIL")
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:100]}")
        results.append("ERROR")
    
    # Wait 2 seconds between calls to respect rate limits
    if i < len(test_queries):
        print("  (waiting 2 seconds...)\n")
        time.sleep(2)

print("\n" + "="*60)
print("RESULTS SUMMARY")
print("="*60)
passed = results.count("PASS")
print(f"Passed: {passed}/{len(results)}")
print(f"Success Rate: {passed/len(results)*100:.0f}%")
print("\nNote: This was a small test to preserve your free tier credits!")
print("="*60)
