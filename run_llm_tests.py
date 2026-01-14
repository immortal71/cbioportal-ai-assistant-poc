"""
Simplified LLM Test Suite
Tests 30 queries and generates results report
Author: Aashish Kharel
GSoC 2026
"""

import json
import time
from datetime import datetime
from pathlib import Path
from llm_parser import LLMQueryParser
from gene_validator import GeneValidator

print("="*70)
print(" LLM PARSER COMPREHENSIVE TEST SUITE")
print("="*70)

# Initialize
parser = LLMQueryParser()
validator = GeneValidator()

# Load test queries
test_file = Path("tests/test_queries.json")
with open(test_file, 'r') as f:
    test_data = json.load(f)

# Collect all tests
all_tests = []
test_id = 1

for category in ["simple_queries", "medium_queries", "complex_queries"]:
    for query in test_data.get(category, []):
        all_tests.append({
            "id": test_id,
            "query": query,
            "category": category.replace("_queries", ""),
            "expected": {}  # We'll evaluate based on successful parse
        })
        test_id += 1

print(f"\nTotal Tests: {len(all_tests)}")
print(f"Starting at: {datetime.now().strftime('%H:%M:%S')}\n")

# Run tests
results = []
passed = 0
failed = 0

for test in all_tests:
    test_id = test["id"]
    query = test["query"]
    category = test["category"]
    
    print(f"[Test #{test_id}] {query}")
    
    try:
        result = parser.parse_query(query)
        
        # Extract data
        genes = result.get("genes", [])
        cancer_types = result.get("cancer_types", [])
        query_type = result.get("query_type", "unknown")
        confidence = result.get("confidence", 0)
        
        # Consider it passed if we got a reasonable parse
        test_passed = confidence >= 5 and (genes or cancer_types or query_type != "unknown")
        
        if test_passed:
            passed += 1
            status = "[OK]"
        else:
            failed += 1
            status = "[FAIL]"
        
        print(f"  {status} Genes: {genes}, Cancers: {cancer_types}, Confidence: {confidence}/10")
        
        results.append({
            "id": test_id,
            "category": category,
            "query": query,
            "result": result,
            "passed": test_passed,
            "confidence": confidence
        })
        
        # Small delay to avoid rate limits
        time.sleep(0.3)
        
    except Exception as e:
        failed += 1
        print(f"  [ERROR] {str(e)}")
        results.append({
            "id": test_id,
            "category": category,
            "query": query,
            "result": {"error": str(e)},
            "passed": False,
            "confidence": 0
        })

# Calculate stats
total = len(all_tests)
success_rate = (passed / total * 100) if total > 0 else 0
avg_confidence = sum(r["confidence"] for r in results if r["confidence"] > 0) / total

# Print summary
print("\n" + "="*70)
print(f" RESULTS: {passed}/{total} PASSED ({success_rate:.1f}%)")
print("="*70)

# Category breakdown
for category in ["simple", "medium", "complex"]:
    cat_results = [r for r in results if r["category"] == category]
    cat_passed = sum(1 for r in cat_results if r["passed"])
    cat_total = len(cat_results)
    cat_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0
    print(f"{category.capitalize():10} {cat_passed}/{cat_total} ({cat_rate:.1f}%)")

print(f"\nAverage Confidence: {avg_confidence:.1f}/10")
print(f"Completed at: {datetime.now().strftime('%H:%M:%S')}")

# Generate markdown report
report_lines = [
    "# LLM Parser Test Results",
    "",
    f"**Date:** {datetime.now().strftime('%B %d, %Y %H:%M:%S')}",
    f"**LLM Provider:** OpenAI GPT-4o-mini",
    f"**Total Tests:** {total}",
    f"**Passed:** {passed}  ",
    f"**Failed:** {failed}",
    f"**Success Rate:** {success_rate:.1f}%",
    f"**Average Confidence:** {avg_confidence:.1f}/10",
    "",
    "---",
    "",
    "## Results by Category",
    ""
]

for category in ["simple", "medium", "complex"]:
    cat_results = [r for r in results if r["category"] == category]
    cat_passed = sum(1 for r in cat_results if r["passed"])
    cat_total = len(cat_results)
    cat_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0
    
    report_lines.extend([
        f"### {category.capitalize()} Queries ({cat_passed}/{cat_total} - {cat_rate:.1f}%)",
        ""
    ])
    
    for r in cat_results:
        status_icon = "✓" if r["passed"] else "✗"
        genes_str = ", ".join(r["result"].get("genes", [])) if "genes" in r["result"] else "ERROR"
        report_lines.extend([
            f"**{status_icon} Test #{r['id']}:** {r['query']}  ",
            f"- Genes: {genes_str}  ",
            f"- Cancer Types: {', '.join(r['result'].get('cancer_types', []))}  ",
            f"- Confidence: {r['confidence']}/10  ",
            ""
        ])

# Add failed tests detail
failed_results = [r for r in results if not r["passed"]]
if failed_results:
    report_lines.extend([
        "---",
        "",
        f"## Failed Tests ({len(failed_results)})",
        ""
    ])
    
    for r in failed_results:
        report_lines.extend([
            f"### Test #{r['id']}: {r['query']}",
            f"**Genes:** {r['result'].get('genes', [])}  ",
            f"**Cancer Types:** {r['result'].get('cancer_types', [])}  ",
            f"**Confidence:** {r['confidence']}/10  ",
            ""
        ])

# Write report
report_path = Path("tests/LLM_TEST_RESULTS.md")
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(report_lines))

# Save JSON
json_path = Path("tests/llm_test_results.json")
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump({
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": success_rate,
            "avg_confidence": avg_confidence
        },
        "results": results
    }, f, indent=2)

print(f"\n✓ Report saved to: {report_path}")
print(f"✓ JSON results saved to: {json_path}")
print("\n" + "="*70)
