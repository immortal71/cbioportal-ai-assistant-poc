"""
Comprehensive Test Suite for cBioPortal AI Assistant PoC
Tests real API integration with multiple genes and cancer types
"""
import asyncio
import httpx

API_URL = "http://localhost:8000"

async def test_all_queries():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=" * 70)
        print("  cBioPortal AI Assistant - COMPREHENSIVE API TEST")
        print("=" * 70)
        print()
        
        test_queries = [
            ("TP53 mutations in breast cancer", "TP53", "Breast cancer"),
            ("BRCA1 mutations", "BRCA1", "General"),
            ("EGFR mutations in lung cancer", "EGFR", "Lung cancer"),
            ("KRAS mutations in colorectal cancer", "KRAS", "Colorectal cancer"),
            ("PIK3CA mutations in breast cancer", "PIK3CA", "Breast cancer"),
            ("BRAF mutations", "BRAF", "General"),
        ]
        
        results = []
        
        for query_text, gene, context in test_queries:
            print(f"[TEST] Testing: {query_text}")
            print(f"   Gene: {gene} | Context: {context}")
            
            try:
                response = await client.get(f"{API_URL}/query?text={query_text}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == "success":
                        source = data.get("source", "Unknown")
                        total = data.get("total_in_study", 0)
                        showing = data.get("count", 0)
                        study = data.get("study_id", "N/A")
                        
                        # Check if using real API data
                        is_api_data = "API" in source
                        status_icon = "[OK]" if is_api_data else "[WARN]"
                        
                        print(f"   {status_icon} Status: SUCCESS")
                        print(f"   Source: {source}")
                        print(f"   Study: {study}")
                        print(f"   Mutations: {showing} shown (of {total} total)")
                        
                        # Show sample mutations
                        mutations = data.get("mutations", [])
                        if mutations:
                            print(f"   Sample mutations:")
                            for mut in mutations[:3]:
                                print(f"      - {mut['sample_id']}: {mut['mutation']} ({mut['type']})")
                        
                        results.append({
                            "query": query_text,
                            "gene": gene,
                            "success": True,
                            "api_data": is_api_data,
                            "mutations": total
                        })
                    else:
                        print(f"   [FAIL] Query failed: {data.get('message', 'Unknown error')}")
                        results.append({
                            "query": query_text,
                            "gene": gene,
                            "success": False,
                            "api_data": False,
                            "mutations": 0
                        })
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    results.append({
                        "query": query_text,
                        "gene": gene,
                        "success": False,
                        "api_data": False,
                        "mutations": 0
                    })
                    
            except Exception as e:
                print(f"   [FAIL] Exception: {e}")
                results.append({
                    "query": query_text,
                    "gene": gene,
                    "success": False,
                    "api_data": False,
                    "mutations": 0
                })
            
            print()
        
        # Summary
        print("=" * 70)
        print("  TEST SUMMARY")
        print("=" * 70)
        print()
        
        total_tests = len(results)
        successful = sum(1 for r in results if r["success"])
        api_data_count = sum(1 for r in results if r["api_data"])
        total_mutations = sum(r["mutations"] for r in results)
        
        print(f"Total Queries Tested: {total_tests}")
        print(f"Successful: {successful} [OK]")
        print(f"Failed: {total_tests - successful} [FAIL]")
        print(f"Using Real API Data: {api_data_count} / {total_tests}")
        print(f"Total Mutations Retrieved: {total_mutations:,}")
        print()
        
        if api_data_count == total_tests:
            print("*** ALL TESTS PASSED - 100% REAL API DATA! ***")
        elif api_data_count > 0:
            print(f"[OK] {api_data_count}/{total_tests} tests using real API data")
        else:
            print("[WARNING] All tests using fallback sample data")
        
        print()
        print("=" * 70)
        
        return results


if __name__ == "__main__":
    print("\nStarting comprehensive test suite...\n")
    asyncio.run(test_all_queries())
