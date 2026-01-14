"""
Test isolated queries to verify LLM integration works
"""
import requests
import time

BASE_URL = "http://localhost:8000"

# Test queries
TESTS = [
    ("Simple", "TP53 mutations in breast cancer"),
    ("Complex", "What are the most common mutations in HER2-positive breast cancer?"),
    ("Edge", "TP53 mutaions"),  # typo
    ("Edge", "Show me everything about BRAF"),
]

def test_isolated():
    success = 0
    total = len(TESTS)
    
    print("=" * 80)
    print("🧪 ISOLATED TEST (Small Batch)")
    print("=" * 80)
    
    for category, query in TESTS:
        print(f"\n[{category}] Testing: '{query}'")
        
        try:
            response = requests.get(f"{BASE_URL}/query", params={"text": query}, timeout=10)
            result = response.json()
            
            llm_used = result.get("llm_used", False)
            confidence = result.get("confidence", 0)
            gene = result.get("gene")
            status = result.get("status")
            
            print(f"   LLM Used: {llm_used}")
            print(f"   Confidence: {confidence}")
            print(f"   Gene: {gene}")
            print(f"   Status: {status}")
            
            if status == "success":
                success += 1
                print("   ✅ PASS")
            else:
                print("   ❌ FAIL")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
        
        time.sleep(1)  # 1 second delay between requests
    
    print("\n" + "=" * 80)
    print(f"RESULT: {success}/{total} ({success/total*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    print("Starting server check...")
    try:
        requests.get(f"{BASE_URL}/health", timeout=5)
        print("✅ Server is running\n")
        test_isolated()
    except:
        print("❌ Server not running. Start with: python -m uvicorn backend.main:app --port 8000")
