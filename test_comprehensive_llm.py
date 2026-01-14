"""
Comprehensive LLM Query Parser Test Suite
Tests Simple, Medium, and Complex Natural Language Queries
Author: Aashish Kharel - GSoC 2026
Date: January 13, 2026
"""

import asyncio
import httpx
from typing import Dict, List, Tuple
from datetime import datetime
import json

BASE_URL = "http://localhost:8000"

# ============================================================================
# TEST CASES - Simple, Medium, Complex
# ============================================================================

SIMPLE_QUERIES = [
    {
        "query": "TP53 mutations in breast cancer",
        "expected": {"genes": ["TP53"], "cancer_type": "breast", "query_type": "mutations"}
    },
    {
        "query": "EGFR in lung cancer",
        "expected": {"genes": ["EGFR"], "cancer_type": "lung", "query_type": "mutations"}
    },
    {
        "query": "BRCA1 mutations",
        "expected": {"genes": ["BRCA1"], "query_type": "mutations"}
    }
]

MEDIUM_QUERIES = [
    {
        "query": "TP53 and BRCA1 co-mutations in ovarian cancer",
        "expected": {"genes": ["TP53", "BRCA1"], "cancer_type": "ovarian"}
    },
    {
        "query": "KRAS mutation frequency in colorectal cancer",
        "expected": {"genes": ["KRAS"], "cancer_type": "colorectal"}
    }
]

COMPLEX_QUERIES = [
    {
        "query": "Find EGFR mutations in non-small cell lung cancer",
        "expected": {"genes": ["EGFR"], "cancer_type": "lung"}
    },
    {
        "query": "PIK3CA and PTEN mutations in breast cancer",
        "expected": {"genes": ["PIK3CA", "PTEN"], "cancer_type": "breast"}
    },
    {
        "query": "KRAS and BRAF in colorectal cancer samples",
        "expected": {"genes": ["KRAS", "BRAF"], "cancer_type": "colorectal"}
    }
]

COMPLEX_QUERIES = [
    {
        "query": "What are the most common mutations in HER2-positive breast cancer?",
        "expected": {"cancer_type": "breast"}
    },
    {
        "query": "Show me all TP53, BRCA1, and BRCA2 mutations across all cancer types",
        "expected": {"genes": ["TP53", "BRCA1", "BRCA2"]}
    }
]

EDGE_CASES = [
    {"query": "TP53 mutaions", "expected": {"genes": ["TP53"]}},  # typo
    {"query": "Show me everything about BRAF", "expected": {"genes": ["BRAF"]}},
    {"query": "TP53", "expected": {"genes": ["TP53"]}}
]


class ComprehensiveTestRunner:
    def __init__(self):
        self.results = {
            "simple": [],
            "medium": [],
            "complex": [],
            "edge_cases": []
        }
        self.summary = {
            "simple": {"total": 0, "passed": 0, "failed": 0},
            "medium": {"total": 0, "passed": 0, "failed": 0},
            "complex": {"total": 0, "passed": 0, "failed": 0},
            "edge_cases": {"total": 0, "passed": 0, "failed": 0}
        }
        
    async def test_query(self, test_case: Dict, category: str) -> Dict:
        """Test a single query"""
        query = test_case["query"]
        expected = test_case["expected"]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{BASE_URL}/query",
                    params={"text": query}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Evaluate the result
                    passed, details = self._evaluate_result(data, expected, query)
                    
                    return {
                        "query": query,
                        "passed": passed,
                        "expected": expected,
                        "actual": {
                            "gene": data.get("gene"),
                            "cancer_type": data.get("parsed_query", {}).get("cancer_type"),
                            "status": data.get("status"),
                            "llm_used": data.get("parsed_query", {}).get("llm_used", False),
                            "confidence": data.get("parsed_query", {}).get("confidence", 0)
                        },
                        "details": details,
                        "response": data
                    }
                else:
                    return {
                        "query": query,
                        "passed": False,
                        "expected": expected,
                        "error": f"HTTP {response.status_code}",
                        "actual": None
                    }
                    
        except Exception as e:
            return {
                "query": query,
                "passed": False,
                "expected": expected,
                "error": str(e),
                "actual": None
            }
    
    def _evaluate_result(self, actual: Dict, expected: Dict, query: str) -> Tuple[bool, str]:
        """Evaluate if the result matches expectations"""
        details = []
        passed = True
        
        # Check for expected errors
        if expected.get("error"):
            if actual.get("status") == "error":
                return True, "Correctly handled invalid query"
            else:
                return True, "Query handled (acceptable)"
        
        # Check gene detection
        if "genes" in expected:
            expected_genes = expected["genes"]
            actual_gene = actual.get("gene")
            
            if actual_gene in expected_genes:
                details.append(f"✓ Gene: {actual_gene}")
            else:
                details.append(f"✗ Gene: Expected {expected_genes}, got {actual_gene}")
                passed = False
        
        # Check cancer type
        if "cancer_type" in expected:
            expected_cancer = expected["cancer_type"]
            actual_cancer = actual.get("parsed_query", {}).get("cancer_type")
            
            if actual_cancer == expected_cancer or (isinstance(expected_cancer, list) and actual_cancer in expected_cancer):
                details.append(f"✓ Cancer type: {actual_cancer}")
            elif actual_cancer is None:
                details.append(f"⚠ Cancer type not detected")
            else:
                details.append(f"✗ Cancer type: Expected {expected_cancer}, got {actual_cancer}")
        
        # Check status
        if actual.get("status") == "success":
            details.append("✓ Query successful")
        else:
            details.append(f"✗ Query failed: {actual.get('message', 'Unknown error')}")
            passed = False
        
        return passed, " | ".join(details)
    
    async def run_category(self, category: str, test_cases: List[Dict]):
        """Run all tests in a category"""
        print(f"\n{'='*80}")
        print(f"📋 TESTING: {category.upper()}")
        print(f"{'='*80}\n")
        
        for i, test_case in enumerate(test_cases, 1):
            result = await self.test_query(test_case, category)
            self.results[category].append(result)
            
            # Update summary
            self.summary[category]["total"] += 1
            if result["passed"]:
                self.summary[category]["passed"] += 1
            else:
                self.summary[category]["failed"] += 1
            
            # Print result
            status = "✅" if result["passed"] else "❌"
            print(f"{status} Test {i}/{len(test_cases)}: {result['query'][:60]}...")
            
            if result.get("actual"):
                print(f"   Gene: {result['actual']['gene']}")
                print(f"   Cancer Type: {result['actual'].get('cancer_type', 'N/A')}")
                print(f"   LLM Used: {result['actual']['llm_used']}")
                print(f"   Confidence: {result['actual']['confidence']}")
                print(f"   {result.get('details', '')}")
            
            if result.get("error"):
                print(f"   ⚠️  Error: {result['error']}")
            
            print()
            
            # Delay for Groq: 30 req/min = 2 seconds between requests
            await asyncio.sleep(2.0)
    
    async def run_all_tests(self):
        """Run all test categories"""
        print("="*80)
        print("🧪 COMPREHENSIVE LLM QUERY PARSER TEST SUITE")
        print("="*80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base URL: {BASE_URL}\n")
        
        # Run all categories
        await self.run_category("simple", SIMPLE_QUERIES)
        await self.run_category("medium", MEDIUM_QUERIES)
        await self.run_category("complex", COMPLEX_QUERIES)
        await self.run_category("edge_cases", EDGE_CASES)
        
        # Print summary
        self._print_summary()
        
        # Generate markdown report
        self._generate_markdown_report()
        
        # Save JSON results
        self._save_json_results()
    
    def _print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80 + "\n")
        
        total_tests = sum(s["total"] for s in self.summary.values())
        total_passed = sum(s["passed"] for s in self.summary.values())
        total_failed = sum(s["failed"] for s in self.summary.values())
        
        print(f"Overall Success Rate: {total_passed}/{total_tests} ({total_passed/total_tests*100:.1f}%)\n")
        
        for category, stats in self.summary.items():
            rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"{category.upper():15} | {stats['passed']:2}/{stats['total']:2} | {rate:5.1f}%")
        
        print("\n" + "="*80)
    
    def _generate_markdown_report(self):
        """Generate TEST_RESULTS.md"""
        total_tests = sum(s["total"] for s in self.summary.values())
        total_passed = sum(s["passed"] for s in self.summary.values())
        
        report = f"""# LLM Parser Test Results

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Author:** Aashish Kharel - GSoC 2026

## Summary

### Overall Success Rate: {total_passed}/{total_tests} ({total_passed/total_tests*100:.1f}%)

| Category | Passed | Total | Success Rate |
|----------|--------|-------|--------------|
"""
        
        for category, stats in self.summary.items():
            rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            report += f"| {category.title()} | {stats['passed']} | {stats['total']} | {rate:.1f}% |\n"
        
        # Add detailed results for each category
        for category in ["simple", "medium", "complex", "edge_cases"]:
            report += f"\n## {category.upper()} Queries\n\n"
            
            for result in self.results[category]:
                status = "✓" if result["passed"] else "✗"
                report += f"### {status} Query: \"{result['query']}\"\n\n"
                
                if result.get("actual"):
                    report += f"- **Gene Detected:** {result['actual']['gene']}\n"
                    report += f"- **Cancer Type:** {result['actual'].get('cancer_type', 'N/A')}\n"
                    report += f"- **LLM Used:** {result['actual']['llm_used']}\n"
                    report += f"- **Confidence:** {result['actual']['confidence']}\n"
                    report += f"- **Status:** {result['actual']['status']}\n"
                    report += f"- **Details:** {result.get('details', '')}\n"
                
                if result.get("error"):
                    report += f"- **Error:** {result['error']}\n"
                
                report += "\n"
        
        # Save report
        filename = "TEST_RESULTS.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Markdown report saved to: {filename}")
    
    def _save_json_results(self):
        """Save detailed JSON results"""
        filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output = {
            "test_date": datetime.now().isoformat(),
            "summary": self.summary,
            "results": self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        
        print(f"💾 JSON results saved to: {filename}")


async def main():
    print("Starting backend health check...")
    
    # Check if backend is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                print("❌ Backend is not responding. Please start the backend server first.")
                print("Run: python -m uvicorn backend.main:app --reload --port 8000")
                return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Please start the backend server first:")
        print("   cd cbioportal-ai-assistant-poc")
        print("   python -m uvicorn backend.main:app --reload --port 8000")
        return
    
    print("✓ Backend is running\n")
    
    # Run tests
    tester = ComprehensiveTestRunner()
    await tester.run_all_tests()
    
    print("\n" + "="*80)
    print("✅ TESTING COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
