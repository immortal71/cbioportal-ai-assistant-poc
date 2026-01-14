"""
Test script for LLM-based query parser
Author: Aashish Kharel
GSoC 2026
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_parser import get_parser
from config import Config


def load_test_queries():
    """Load test queries from JSON file"""
    with open("tests/test_queries.json", "r") as f:
        return json.load(f)


def test_llm_parser():
    """Test LLM parser with all test queries"""
    
    print("=" * 80)
    print("LLM QUERY PARSER TEST SUITE")
    print("=" * 80)
    print()
    
    # Check configuration
    if not Config.is_llm_configured():
        print("[ERROR] LLM not configured!")
        print("Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in your environment")
        print("See .env.example for instructions")
        return
    
    print(f"[INFO] Using LLM Provider: {Config.LLM_PROVIDER}")
    print()
    
    parser = get_parser()
    test_data = load_test_queries()
    
    results = {
        "simple": [],
        "medium": [],
        "complex": []
    }
    
    total_queries = 0
    successful_parses = 0
    high_confidence_count = 0
    
    # Test each category
    for category in ["simple_queries", "medium_queries", "complex_queries"]:
        category_name = category.replace("_queries", "")
        print(f"\n{'='*80}")
        print(f"Testing {category_name.upper()} Queries")
        print(f"{'='*80}\n")
        
        for query in test_data[category]:
            total_queries += 1
            print(f"[TEST] Query: \"{query}\"")
            
            try:
                result = parser.parse_query(query)
                
                print(f"  Genes: {result.get('genes', [])}")
                print(f"  Cancer Types: {result.get('cancer_types', [])}")
                print(f"  Query Type: {result.get('query_type', 'unknown')}")
                print(f"  Confidence: {result.get('confidence', 0)}/10")
                
                if result.get('reasoning'):
                    print(f"  Reasoning: {result['reasoning']}")
                
                # Check success
                if result.get('confidence', 0) >= Config.MIN_CONFIDENCE_SCORE:
                    print("  Status: [OK]")
                    successful_parses += 1
                    if result.get('confidence', 0) >= 8:
                        high_confidence_count += 1
                else:
                    print("  Status: [WARN] Low confidence")
                
                results[category_name].append({
                    "query": query,
                    "result": result,
                    "success": result.get('confidence', 0) >= Config.MIN_CONFIDENCE_SCORE
                })
                
            except Exception as e:
                print(f"  Status: [FAIL] {e}")
                results[category_name].append({
                    "query": query,
                    "error": str(e),
                    "success": False
                })
            
            print()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Queries Tested: {total_queries}")
    print(f"Successful Parses: {successful_parses}/{total_queries} ({successful_parses/total_queries*100:.1f}%)")
    print(f"High Confidence (8+): {high_confidence_count}/{total_queries} ({high_confidence_count/total_queries*100:.1f}%)")
    print()
    
    # Category breakdown
    for category in ["simple", "medium", "complex"]:
        cat_results = results[category]
        cat_success = sum(1 for r in cat_results if r.get('success', False))
        print(f"{category.capitalize()}: {cat_success}/{len(cat_results)} successful")
    
    print("\n" + "="*80)
    
    # Save results
    output_file = "tests/test_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "summary": {
                "total": total_queries,
                "successful": successful_parses,
                "high_confidence": high_confidence_count,
                "success_rate": successful_parses/total_queries*100
            },
            "results": results
        }, f, indent=2)
    
    print(f"\n[INFO] Detailed results saved to {output_file}")


if __name__ == "__main__":
    test_llm_parser()
