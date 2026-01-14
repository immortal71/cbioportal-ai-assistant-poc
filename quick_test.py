"""
Quick test of LLM parser
"""

from llm_parser import LLMQueryParser
from gene_validator import GeneValidator

print("Initializing LLM Parser...")
parser = LLMQueryParser()
validator = GeneValidator()

print("\n" + "="*60)
print("Testing LLM Query Parser")
print("="*60)

# Test queries
test_queries = [
    "TP53 mutations in breast cancer",
    "EGFR and ALK in lung cancer",
    "What are the most common mutations in HER2+ breast cancer?"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n[Test {i}] Query: \"{query}\"")
    
    try:
        result = parser.parse_query(query)
        
        # Check if it's a dict (current implementation) or object
        if isinstance(result, dict):
            genes = result.get("genes", [])
            cancer_types = result.get("cancer_types", [])
            query_type = result.get("query_type", "unknown")
            confidence = result.get("confidence", 0)
            
            print(f"  ✓ Genes: {genes}")
            print(f"  ✓ Cancer Types: {cancer_types}")
            print(f"  ✓ Query Type: {query_type}")
            print(f"  ✓ Confidence: {confidence}/10")
            
            # Validate genes
            if genes:
                validation = validator.validate_and_suggest(genes)
                if validation["all_valid"]:
                    print(f"  ✓ All genes validated")
                else:
                    print(f"  ⚠ Invalid genes: {validation['invalid_genes']}")
                    print(f"  ⚠ Suggestions: {validation['suggestions']}")
        else:
            print(f"  ✗ Unexpected result type: {type(result)}")
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")

print("\n" + "="*60)
print("Quick test complete!")
print("="*60)
