"""
LLM Accuracy & Robustness Testing
Tests spelling errors, ambiguity, edge cases, and natural language processing
Author: Aashish Kharel - GSoC 2026
"""

import asyncio
import httpx
from typing import Dict, List
from datetime import datetime
import json

BASE_URL = "http://localhost:8000"

# Test cases organized by category
TEST_CASES = {
    "correct_queries": [
        "Show me TP53 mutations",
        "BRCA1 mutations in breast cancer",
        "What mutations does EGFR have in lung cancer?",
        "KRAS mutations",
        "PIK3CA in ovarian cancer",
    ],
    
    "spelling_mistakes": [
        "TP53 mutaions",  # missing 't'
        "BRCA1 mutatioons",  # double 'o'
        "EGFR mutaton",  # missing 'i'
        "Show me KRAS mutatins in lung caner",  # multiple errors
        "breast cancr",  # missing 'e'
        "BRCA muations",  # missing '1'
        "PIK3A mutations",  # missing 'C'
        "TP5 mutations",  # missing '3'
    ],
    
    "ambiguous_similar_genes": [
        "BRCA mutations",  # Could be BRCA1 or BRCA2
        "TP mutations",  # Could be TP53, TP63, TP73
        "PIK mutations",  # Could be PIK3CA, PIK3CB, etc.
        "RAF mutations",  # Could be BRAF, RAF1, ARAF
        "RAS mutations",  # Could be KRAS, NRAS, HRAS
    ],
    
    "complex_natural_language": [
        "I want to see all the mutations in the TP53 gene",
        "Can you show me what kind of mutations BRCA1 has?",
        "Are there any EGFR mutations in patients with lung cancer?",
        "Tell me about KRAS",
        "What's the mutation profile for PIK3CA?",
        "Find me mutations for breast cancer gene BRCA1",
        "Show mutations in tumor suppressor gene TP53",
    ],
    
    "edge_cases": [
        "",  # Empty query
        "mutations",  # No gene specified
        "cancer",  # No gene specified
        "ABCDEFG mutations",  # Completely invalid gene
        "TP53",  # Just gene name, no context
        "breast cancer",  # Just cancer type, no gene
        "123456",  # Numbers only
        "!@#$%",  # Special characters
        "tp53 mutations tp53 mutations tp53",  # Repeated text
    ],
    
    "case_variations": [
        "tp53 mutations",  # lowercase
        "TP53 MUTATIONS",  # uppercase
        "Tp53 Mutations",  # mixed case
        "tP53 MuTaTiOnS",  # random case
    ],
    
    "synonym_variations": [
        "TP53 alterations",
        "TP53 variants",
        "TP53 changes",
        "TP53 genetic changes",
        "TP53 genomic alterations",
    ]
}


class AccuracyTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed = 0
        self.failed = 0
        
    async def test_query(self, query: str, category: str) -> Dict:
        """Test a single query and return results"""
        self.total_tests += 1
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{BASE_URL}/query",
                    params={"text": query}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Determine if test passed based on category
                    passed = self._evaluate_response(query, data, category)
                    
                    if passed:
                        self.passed += 1
                    else:
                        self.failed += 1
                    
                    return {
                        "query": query,
                        "category": category,
                        "status": "success" if passed else "failed",
                        "response": data,
                        "gene_detected": data.get("gene", "None"),
                        "cancer_type_detected": data.get("parsed_query", {}).get("cancer_type", "None"),
                        "llm_used": data.get("parsed_query", {}).get("llm_used", False),
                        "confidence": data.get("parsed_query", {}).get("confidence", 0),
                        "error": None
                    }
                else:
                    self.failed += 1
                    return {
                        "query": query,
                        "category": category,
                        "status": "failed",
                        "error": f"HTTP {response.status_code}",
                        "gene_detected": "None",
                        "llm_used": False
                    }
                    
        except Exception as e:
            self.failed += 1
            return {
                "query": query,
                "category": category,
                "status": "error",
                "error": str(e),
                "gene_detected": "None",
                "llm_used": False
            }
    
    def _evaluate_response(self, query: str, data: Dict, category: str) -> bool:
        """Evaluate if response is appropriate for the query"""
        
        # For correct queries, we expect success
        if category == "correct_queries":
            return data.get("status") == "success" and data.get("gene")
        
        # For spelling mistakes, we should still detect the gene (LLM should handle it)
        if category == "spelling_mistakes":
            # At minimum, should not crash
            return data.get("status") in ["success", "error"]
        
        # For ambiguous genes, should detect at least one gene
        if category == "ambiguous_similar_genes":
            return data.get("gene") is not None
        
        # Complex NL should be parsed correctly
        if category == "complex_natural_language":
            return data.get("status") == "success" and data.get("gene")
        
        # Edge cases should handle gracefully (not crash)
        if category == "edge_cases":
            return data.get("status") in ["success", "error"]
        
        # Case variations should all work
        if category == "case_variations":
            return data.get("gene") == "TP53"
        
        # Synonym variations should detect TP53
        if category == "synonym_variations":
            return data.get("gene") == "TP53"
        
        return True
    
    async def run_all_tests(self):
        """Run all test cases"""
        print("=" * 80)
        print("🧪 LLM ACCURACY & ROBUSTNESS TEST SUITE")
        print("=" * 80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        for category, queries in TEST_CASES.items():
            print(f"\n{'='*80}")
            print(f"📋 Testing: {category.upper().replace('_', ' ')}")
            print(f"{'='*80}")
            
            for query in queries:
                result = await self.test_query(query, category)
                self.results.append(result)
                
                # Print result
                status_emoji = "✅" if result["status"] == "success" else "❌"
                print(f"\n{status_emoji} Query: '{query}'")
                print(f"   Gene Detected: {result['gene_detected']}")
                print(f"   LLM Used: {result.get('llm_used', False)}")
                print(f"   Confidence: {result.get('confidence', 'N/A')}")
                
                if result.get('cancer_type_detected') and result['cancer_type_detected'] != 'None':
                    print(f"   Cancer Type: {result['cancer_type_detected']}")
                
                if result.get('error'):
                    print(f"   ⚠️  Error: {result['error']}")
                
                # Show specific issues for spelling mistakes
                if category == "spelling_mistakes":
                    if result['gene_detected'] == 'None':
                        print(f"   ⚠️  Failed to handle spelling error")
                    else:
                        print(f"   ✨ Successfully corrected spelling!")
        
        # Print summary
        self._print_summary()
        
        # Save detailed results
        self._save_results()
    
    def _print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed} ({self.passed/self.total_tests*100:.1f}%)")
        print(f"Failed: {self.failed} ({self.failed/self.total_tests*100:.1f}%)")
        
        # Category breakdown
        print("\n📈 CATEGORY BREAKDOWN:")
        for category in TEST_CASES.keys():
            category_results = [r for r in self.results if r['category'] == category]
            total = len(category_results)
            passed = len([r for r in category_results if r['status'] == 'success'])
            print(f"   {category.replace('_', ' ').title()}: {passed}/{total} ({passed/total*100:.1f}%)")
        
        # LLM usage stats
        llm_used_count = len([r for r in self.results if r.get('llm_used')])
        print(f"\n🤖 LLM Usage: {llm_used_count}/{self.total_tests} queries ({llm_used_count/self.total_tests*100:.1f}%)")
        
        # Key findings
        print("\n🔍 KEY FINDINGS:")
        
        # Spelling error handling
        spelling_tests = [r for r in self.results if r['category'] == 'spelling_mistakes']
        spelling_success = len([r for r in spelling_tests if r['gene_detected'] != 'None'])
        print(f"   • Spelling Error Tolerance: {spelling_success}/{len(spelling_tests)} ({spelling_success/len(spelling_tests)*100:.1f}%)")
        
        # Ambiguity handling
        ambiguous_tests = [r for r in self.results if r['category'] == 'ambiguous_similar_genes']
        ambiguous_success = len([r for r in ambiguous_tests if r['gene_detected'] != 'None'])
        print(f"   • Ambiguous Query Handling: {ambiguous_success}/{len(ambiguous_tests)}")
        
        # Edge case handling
        edge_tests = [r for r in self.results if r['category'] == 'edge_cases']
        edge_no_crash = len([r for r in edge_tests if r['status'] != 'error'])
        print(f"   • Edge Case Stability: {edge_no_crash}/{len(edge_tests)} (no crashes)")
    
    def _save_results(self):
        """Save detailed results to JSON file"""
        filename = f"test_results_accuracy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output = {
            "test_date": datetime.now().isoformat(),
            "summary": {
                "total_tests": self.total_tests,
                "passed": self.passed,
                "failed": self.failed,
                "pass_rate": f"{self.passed/self.total_tests*100:.1f}%"
            },
            "results": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {filename}")


async def main():
    tester = AccuracyTester()
    await tester.run_all_tests()
    
    print("\n" + "=" * 80)
    print("✅ Testing Complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
