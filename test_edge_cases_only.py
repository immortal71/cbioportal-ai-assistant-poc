"""
Test ONLY edge cases in isolation to prove if the issue is rate limiting or broken code.
"""
import asyncio
import httpx
from typing import Dict, List

BASE_URL = "http://localhost:8000"

EDGE_CASES = [
    {"query": "", "expected": {"error": True}},
    {"query": "mutations", "expected": {"error": True}},
    {"query": "cancer", "expected": {"error": True}},
    {"query": "FAKEGENEXYZ mutations", "expected": {"error": True}},
    {"query": "TP53", "expected": {"genes": ["TP53"]}},
    {"query": "breast cancer", "expected": {"cancer_type": "breast"}},
    {"query": "tp53 mutations", "expected": {"genes": ["TP53"]}},
    {"query": "TP53 mutaions", "expected": {"genes": ["TP53"]}},
    {"query": "BRCA muations", "expected": {"genes": ["BRCA1"]}},
    {"query": "Show me everything about BRAF", "expected": {"genes": ["BRAF"]}}
]

async def test_one_query(query: str, expected: Dict) -> Dict:
    """Test a single query"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{BASE_URL}/query",
                params={"text": query}
            )
            
            print(f"\n{'='*60}")
            print(f"Query: '{query}'")
            print(f"HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response gene: {data.get('gene')}")
                print(f"Response cancer_type: {data.get('cancer_type')}")
                print(f"Response status: {data.get('status')}")
                print(f"Response message: {data.get('message', 'N/A')}")
                
                # Check if it matches expectations
                if expected.get("error"):
                    passed = data.get("status") == "error"
                    print(f"Result: {'PASS' if passed else 'FAIL'} (expected error)")
                elif "genes" in expected:
                    passed = data.get("gene") in expected["genes"]
                    print(f"Result: {'PASS' if passed else 'FAIL'} (expected gene {expected['genes']})")
                elif "cancer_type" in expected:
                    passed = data.get("cancer_type") == expected["cancer_type"]
                    print(f"Result: {'PASS' if passed else 'FAIL'} (expected cancer type {expected['cancer_type']})")
                else:
                    passed = False
                    print("Result: FAIL (no clear expectation)")
                
                return {"passed": passed, "response": data}
            else:
                print(f"HTTP ERROR: {response.status_code}")
                print(f"Response text: {response.text[:200]}")
                return {"passed": False, "error": f"HTTP {response.status_code}"}
                
    except Exception as e:
        print(f"EXCEPTION: {type(e).__name__}: {e}")
        return {"passed": False, "error": str(e)}

async def main():
    print("="*60)
    print("TESTING EDGE CASES IN ISOLATION")
    print("="*60)
    
    # Check if server is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                print("❌ Server not responding. Start it first!")
                return
    except:
        print("❌ Server not running. Start it with: python -m uvicorn backend.main:app --port 8000")
        return
    
    print("✅ Server is running\n")
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(EDGE_CASES, 1):
        result = await test_one_query(test_case["query"], test_case["expected"])
        if result.get("passed"):
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {passed}/{len(EDGE_CASES)} passed ({passed*100//len(EDGE_CASES)}%)")
    print(f"{'='*60}")
    
    if passed == 0:
        print("\n❌ 0% SUCCESS - Your edge case handling is BROKEN")
        print("This is NOT rate limiting. Your code has bugs.")
    elif passed >= 7:
        print(f"\n✅ {passed*100//len(EDGE_CASES)}% SUCCESS - Edge cases work in isolation!")
        print("If they fail in full test suite, THEN it's rate limiting or state corruption.")
    else:
        print(f"\n⚠️  {passed*100//len(EDGE_CASES)}% SUCCESS - Some edge cases work, some don't")
        print("You have bugs in your edge case handling.")

if __name__ == "__main__":
    asyncio.run(main())
