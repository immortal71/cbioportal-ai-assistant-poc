"""
Comprehensive LLM Parser Test Suite
Author: Aashish Kharel
GSoC 2026

Tests the LLM parser against 30 diverse queries and generates detailed results.
"""

import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from llm_parser import LLMQueryParser, QueryParseResult
from gene_validator import GeneValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestResult:
    """Individual test result"""
    
    def __init__(
        self,
        test_id: int,
        query: str,
        expected: Dict,
        actual: QueryParseResult,
        validation_result: Dict,
        passed: bool,
        notes: str = ""
    ):
        self.test_id = test_id
        self.query = query
        self.expected = expected
        self.actual = actual
        self.validation_result = validation_result
        self.passed = passed
        self.notes = notes
    
    def to_dict(self) -> Dict:
        return {
            "test_id": self.test_id,
            "query": self.query,
            "expected": self.expected,
            "actual": self.actual.to_dict() if self.actual.success else {"error": self.actual.error},
            "validation": self.validation_result,
            "passed": self.passed,
            "notes": self.notes
        }


class LLMTestSuite:
    """Run comprehensive tests on LLM parser"""
    
    def __init__(self):
        self.parser = None
        self.validator = GeneValidator()
        self.results: List[TestResult] = []
    
    def load_test_queries(self) -> Dict:
        """Load test queries from JSON file"""
        test_file = Path("tests/test_queries.json")
        with open(test_file, 'r') as f:
            return json.load(f)
    
    def evaluate_result(self, expected: Dict, actual: QueryParseResult) -> tuple[bool, str]:
        """
        Evaluate if actual result matches expected
        
        Returns:
            (passed, notes)
        """
        if not actual.success:
            return False, f"Parse failed: {actual.error}"
        
        notes = []
        passed = True
        
        # Check genes
        expected_genes = set(g.upper() for g in expected.get("genes", []))
        actual_genes = set(g.upper() for g in actual.genes)
        
        if expected_genes and expected_genes != actual_genes:
            passed = False
            notes.append(f"Gene mismatch: expected {expected_genes}, got {actual_genes}")
        elif not expected_genes and actual_genes:
            notes.append(f"Extracted genes: {actual_genes} (none expected)")
        
        # Check cancer types
        expected_cancers = set(c.lower() for c in expected.get("cancer_types", []))
        actual_cancers = set(c.lower() for c in actual.cancer_types)
        
        if expected_cancers and not actual_cancers.intersection(expected_cancers):
            passed = False
            notes.append(f"Cancer type mismatch: expected {expected_cancers}, got {actual_cancers}")
        
        # Check query type
        expected_type = expected.get("query_type")
        if expected_type and expected_type != actual.query_type:
            # Allow some flexibility
            if not (expected_type == "general" or actual.query_type == "general"):
                notes.append(f"Query type: expected {expected_type}, got {actual.query_type}")
        
        # Check confidence
        if actual.confidence < 5.0:
            notes.append(f"Low confidence: {actual.confidence}/10")
        
        return passed, "; ".join(notes) if notes else "OK"
    
    async def run_test(self, test_data: Dict) -> TestResult:
        """Run a single test"""
        test_id = test_data["id"]
        query = test_data["query"]
        expected = test_data["expected"]
        
        logger.info(f"Test #{test_id}: {query}")
        
        try:
            # Parse query
            result = self.parser.parse_query(query)
            
            # Validate genes if any were extracted
            validation_result = {}
            if result.genes:
                validation_result = self.validator.validate_and_suggest(result.genes)
            
            # Evaluate
            passed, notes = self.evaluate_result(expected, result)
            
            return TestResult(
                test_id=test_id,
                query=query,
                expected=expected,
                actual=result,
                validation_result=validation_result,
                passed=passed,
                notes=notes
            )
            
        except Exception as e:
            logger.error(f"Test #{test_id} failed with exception: {e}")
            return TestResult(
                test_id=test_id,
                query=query,
                expected=expected,
                actual=QueryParseResult(
                    genes=[], cancer_types=[], query_type="general",
                    filters={}, confidence=0.0, raw_response="",
                    success=False, error=str(e)
                ),
                validation_result={},
                passed=False,
                notes=f"Exception: {str(e)}"
            )
    
    async def run_all_tests(self):
        """Run all test queries"""
        logger.info("=== Starting LLM Parser Test Suite ===")
        
        # Initialize parser (will fail gracefully if no API key)
        try:
            self.parser = LLMQueryParser()
        except Exception as e:
            logger.error(f"Failed to initialize LLM parser: {e}")
            logger.info("Run with: ANTHROPIC_API_KEY=your-key python test_llm_parser.py")
            return
        
        # Load test queries
        test_data = self.load_test_queries()
        all_tests = []
        
        for category in ["simple", "medium", "complex"]:
            all_tests.extend(test_data["test_queries"][category])
        
        logger.info(f"Running {len(all_tests)} tests...")
        
        # Run tests
        for test in all_tests:
            result = await self.run_test(test)
            self.results.append(result)
            
            # Small delay to avoid rate limits
            await asyncio.sleep(0.5)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate detailed test report"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        # Create markdown report
        report_lines = [
            "# LLM Parser Test Results",
            f"**Date:** {datetime.now().strftime('%B %d, %Y %H:%M:%S')}",
            f"**Total Tests:** {total}",
            f"**Passed:** {passed}",
            f"**Failed:** {failed}",
            f"**Success Rate:** {success_rate:.1f}%",
            "",
            "---",
            ""
        ]
        
        # Successful tests
        successful = [r for r in self.results if r.passed]
        if successful:
            report_lines.extend([
                f"## Successful Tests ({len(successful)}/{total})",
                ""
            ])
            
            for result in successful:
                genes_str = ", ".join(result.actual.genes) if result.actual.genes else "None"
                cancers_str = ", ".join(result.actual.cancer_types) if result.actual.cancer_types else "None"
                
                report_lines.extend([
                    f"### Test #{result.test_id} [OK]",
                    f"**Query:** \"{result.query}\"",
                    f"- **Genes:** {genes_str}",
                    f"- **Cancer Types:** {cancers_str}",
                    f"- **Query Type:** {result.actual.query_type}",
                    f"- **Confidence:** {result.actual.confidence}/10",
                    f"- **Notes:** {result.notes or 'Perfect match'}",
                    ""
                ])
                
                # Add validation info if genes were found
                if result.validation_result:
                    if result.validation_result.get("all_valid"):
                        report_lines.append(f"- **Validation:** All genes valid")
                    else:
                        invalid = result.validation_result.get("invalid_genes", [])
                        report_lines.append(f"- **Validation:** Invalid genes: {invalid}")
                    report_lines.append("")
        
        # Failed tests
        failed_tests = [r for r in self.results if not r.passed]
        if failed_tests:
            report_lines.extend([
                f"## Failed Tests ({len(failed_tests)}/{total})",
                ""
            ])
            
            for result in failed_tests:
                report_lines.extend([
                    f"### Test #{result.test_id} [FAIL]",
                    f"**Query:** \"{result.query}\"",
                    f"- **Expected Genes:** {result.expected.get('genes', [])}",
                    f"- **Actual Genes:** {result.actual.genes if result.actual.success else 'N/A'}",
                    f"- **Issue:** {result.notes}",
                    ""
                ])
        
        # Summary statistics
        report_lines.extend([
            "---",
            "",
            "## Summary",
            "",
            "### By Category",
            ""
        ])
        
        # Calculate stats by category
        simple_results = [r for r in self.results if r.test_id <= 10]
        medium_results = [r for r in self.results if 11 <= r.test_id <= 20]
        complex_results = [r for r in self.results if r.test_id >= 21]
        
        for category, results in [
            ("Simple", simple_results),
            ("Medium", medium_results),
            ("Complex", complex_results)
        ]:
            cat_total = len(results)
            cat_passed = sum(1 for r in results if r.passed)
            cat_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0
            report_lines.append(f"- **{category}:** {cat_passed}/{cat_total} ({cat_rate:.1f}%)")
        
        # Average confidence
        avg_confidence = sum(r.actual.confidence for r in self.results if r.actual.success) / total
        report_lines.extend([
            "",
            f"### Average Confidence Score",
            f"- {avg_confidence:.1f}/10",
            ""
        ])
        
        # Write report
        report_path = Path("tests/TEST_RESULTS.md")
        with open(report_path, 'w') as f:
            f.write("\n".join(report_lines))
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Test Results: {passed}/{total} passed ({success_rate:.1f}%)")
        logger.info(f"Report saved to: {report_path}")
        logger.info(f"{'='*60}")
        
        # Also save JSON results
        json_path = Path("tests/test_results.json")
        with open(json_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "success_rate": success_rate,
                    "avg_confidence": avg_confidence
                },
                "results": [r.to_dict() for r in self.results]
            }, f, indent=2)
        
        logger.info(f"JSON results saved to: {json_path}")


async def main():
    """Main test runner"""
    suite = LLMTestSuite()
    await suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
