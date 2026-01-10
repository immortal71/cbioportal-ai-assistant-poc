"""
Test script for cBioPortal API and backend
"""
import asyncio
import httpx

CBIOPORTAL_API_URL = "https://www.cbioportal.org/api"

async def test_api():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("[TEST] Testing cBioPortal API...")
        print()
        
        # Test 1: Get studies
        print("1. Fetching studies...")
        studies_response = await client.get(f"{CBIOPORTAL_API_URL}/studies")
        if studies_response.status_code == 200:
            studies = studies_response.json()
            print(f"   [OK] Found {len(studies)} studies")
            print(f"   First study: {studies[0]['studyId']} - {studies[0]['name']}")
        else:
            print(f"   [FAIL] Failed: {studies_response.status_code}")
        print()
        
        # Test 2: Get gene info
        print("2. Getting TP53 gene info...")
        gene_response = await client.get(f"{CBIOPORTAL_API_URL}/genes/TP53")
        if gene_response.status_code == 200:
            gene = gene_response.json()
            print(f"   [OK] Gene: {gene['hugoGeneSymbol']}, Entrez ID: {gene['entrezGeneId']}")
        else:
            print(f"   [FAIL] Failed: {gene_response.status_code}")
        print()
        
        # Test 3: Get molecular profiles
        study_id = "brca_tcga"
        print(f"3. Getting molecular profiles for {study_id}...")
        profiles_response = await client.get(f"{CBIOPORTAL_API_URL}/studies/{study_id}/molecular-profiles")
        if profiles_response.status_code == 200:
            profiles = profiles_response.json()
            mutation_profiles = [p for p in profiles if p['molecularAlterationType'] == 'MUTATION_EXTENDED']
            print(f"   [OK] Found {len(mutation_profiles)} mutation profile(s)")
            if mutation_profiles:
                print(f"   Profile ID: {mutation_profiles[0]['molecularProfileId']}")
        else:
            print(f"   [FAIL] Failed: {profiles_response.status_code}")
        print()
        
        # Test 4: Test backend
        print("4. Testing local backend...")
        try:
            backend_response = await client.get("http://localhost:8000/health")
            if backend_response.status_code == 200:
                print("   [OK] Backend is running")
            else:
                print(f"   [FAIL] Backend returned: {backend_response.status_code}")
        except Exception as e:
            print(f"   [FAIL] Backend not accessible: {e}")
        print()
        
        # Test 5: Test query endpoint
        print("5. Testing backend query...")
        try:
            query_response = await client.get("http://localhost:8000/query?text=TP53%20mutations")
            if query_response.status_code == 200:
                data = query_response.json()
                print(f"   [OK] Query successful")
                print(f"   Status: {data.get('status')}")
                print(f"   Gene: {data.get('gene')}")
                print(f"   Mutations: {data.get('count')}")
                print(f"   Source: {data.get('source')}")
            else:
                print(f"   [FAIL] Query failed: {query_response.status_code}")
        except Exception as e:
            print(f"   [FAIL] Query error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
