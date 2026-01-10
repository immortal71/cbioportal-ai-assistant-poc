"""
cBioPortal AI Assistant - Backend API
Author: Aashish Kharel
Project: Google Summer of Code 2026
Organization: NRNB / cBioPortal
Description: Natural language interface for querying cBioPortal cancer genomics data
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from typing import Optional, List, Dict, Any
import asyncio

__author__ = "Aashish Kharel"
__version__ = "0.1.0"
__project__ = "cBioPortal AI Assistant PoC - GSoC 2026"

app = FastAPI(
    title="cBioPortal AI Assistant PoC",
    description="Natural language interface for cancer genomics data",
    version="0.1.0",
    contact={
        "name": "Aashish Kharel",
        "url": "https://github.com/nrnb/GoogleSummerOfCode/issues/274"
    }
)

# Enable CORS for frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# cBioPortal API Configuration
CBIOPORTAL_API_URL = "https://www.cbioportal.org/api"
CBIOPORTAL_TIMEOUT = 30.0  # seconds

# cBioPortal API Configuration
CBIOPORTAL_API_URL = "https://www.cbioportal.org/api"
CBIOPORTAL_TIMEOUT = 30.0  # seconds


class QueryRequest(BaseModel):
    text: str


# ====================
# cBioPortal API Functions
# ====================

async def get_studies() -> List[Dict]:
    """Fetch available studies from cBioPortal."""
    async with httpx.AsyncClient(timeout=CBIOPORTAL_TIMEOUT) as client:
        try:
            response = await client.get(f"{CBIOPORTAL_API_URL}/studies")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching studies: {e}")
            return []


async def get_gene_mutations(gene_symbol: str, study_id: str = "msk_impact_2017") -> Dict[str, Any]:
    """
    Fetch mutations for a specific gene from cBioPortal.
    
    Args:
        gene_symbol: Gene symbol (e.g., 'TP53', 'BRCA1')
        study_id: Study identifier (default: MSK-IMPACT 2017)
    
    Returns:
        Dictionary containing mutation data
    """
    async with httpx.AsyncClient(timeout=CBIOPORTAL_TIMEOUT) as client:
        try:
            # Get Entrez Gene ID
            entrez_id = await get_gene_entrez_id(gene_symbol)
            if not entrez_id:
                return {"error": f"Could not find Entrez ID for gene {gene_symbol}"}
            
            # Construct molecular profile ID and sample list ID
            mutation_profile_id = f"{study_id}_mutations"
            sample_list_id = f"{study_id}_all"
            
            # Build the mutations fetch URL
            mutations_url = f"{CBIOPORTAL_API_URL}/molecular-profiles/{mutation_profile_id}/mutations/fetch"
            
            # Request body with correct format
            request_body = {
                "sampleListId": sample_list_id,
                "entrezGeneIds": [entrez_id]
            }
            
            # POST request to fetch mutations
            mutations_response = await client.post(
                mutations_url,
                json=request_body,
                headers={"Content-Type": "application/json"}
            )
            
            if mutations_response.status_code != 200:
                return {"error": f"API returned status {mutations_response.status_code}"}
            
            mutations = mutations_response.json()
            
            if not mutations or len(mutations) == 0:
                return {"error": f"No mutations found for {gene_symbol} in study {study_id}"}
            
            return {
                "gene": gene_symbol,
                "study_id": study_id,
                "mutations": mutations[:30],  # Limit to first 30 for display
                "total_count": len(mutations)
            }
            
        except httpx.HTTPStatusError as e:
            print(f"HTTP Error fetching mutations: {e}")
            return {"error": f"API error: {e.response.status_code}"}
        except Exception as e:
            print(f"Error fetching mutations: {e}")
            return {"error": str(e)}


async def get_gene_entrez_id(gene_symbol: str) -> Optional[int]:
    """Get Entrez Gene ID for a gene symbol."""
    async with httpx.AsyncClient(timeout=CBIOPORTAL_TIMEOUT) as client:
        try:
            response = await client.get(f"{CBIOPORTAL_API_URL}/genes/{gene_symbol}")
            response.raise_for_status()
            gene_data = response.json()
            return gene_data.get('entrezGeneId')
        except Exception as e:
            print(f"Error fetching gene ID for {gene_symbol}: {e}")
            # Fallback to common gene IDs
            gene_id_map = {
                'TP53': 7157,
                'BRCA1': 672,
                'BRCA2': 675,
                'EGFR': 1956,
                'KRAS': 3845,
                'PIK3CA': 5290,
                'PTEN': 5728
            }
            return gene_id_map.get(gene_symbol.upper())


async def search_studies_by_cancer_type(cancer_type: str) -> List[Dict]:
    """Search for studies by cancer type."""
    async with httpx.AsyncClient(timeout=CBIOPORTAL_TIMEOUT) as client:
        try:
            response = await client.get(f"{CBIOPORTAL_API_URL}/studies")
            response.raise_for_status()
            studies = response.json()
            
            # Filter studies by cancer type
            cancer_type_lower = cancer_type.lower()
            matching_studies = [
                s for s in studies 
                if cancer_type_lower in s.get('name', '').lower() 
                or cancer_type_lower in s.get('description', '').lower()
                or cancer_type_lower in s.get('cancerTypeId', '').lower()
            ]
            
            return matching_studies[:10]  # Return top 10 matches
            
        except Exception as e:
            print(f"Error searching studies: {e}")
            return []



# Sample data for demonstration
SAMPLE_DATA = {
    "tp53": {
        "gene": "TP53",
        "description": "Tumor protein p53",
        "mutations": [
            {"sample_id": "TCGA-A1-A0SB", "mutation": "p.R248Q", "type": "Missense", "cancer_type": "Breast Cancer"},
            {"sample_id": "TCGA-A1-A0SD", "mutation": "p.Y234H", "type": "Missense", "cancer_type": "Breast Cancer"},
            {"sample_id": "TCGA-A1-A0SE", "mutation": "p.R273C", "type": "Missense", "cancer_type": "Lung Cancer"},
            {"sample_id": "TCGA-A1-A0SF", "mutation": "p.R175H", "type": "Missense", "cancer_type": "Colorectal Cancer"},
        ]
    },
    "brca1": {
        "gene": "BRCA1",
        "description": "Breast cancer 1, early onset",
        "mutations": [
            {"sample_id": "TCGA-B1-A0SB", "mutation": "p.Q1756fs", "type": "Frameshift", "cancer_type": "Breast Cancer"},
            {"sample_id": "TCGA-B1-A0SC", "mutation": "p.R1699Q", "type": "Missense", "cancer_type": "Ovarian Cancer"},
            {"sample_id": "TCGA-B1-A0SD", "mutation": "p.C61G", "type": "Missense", "cancer_type": "Breast Cancer"},
        ]
    },
    "egfr": {
        "gene": "EGFR",
        "description": "Epidermal growth factor receptor",
        "mutations": [
            {"sample_id": "TCGA-E1-A0SB", "mutation": "p.L858R", "type": "Missense", "cancer_type": "Lung Cancer"},
            {"sample_id": "TCGA-E1-A0SC", "mutation": "p.T790M", "type": "Missense", "cancer_type": "Lung Cancer"},
            {"sample_id": "TCGA-E1-A0SD", "mutation": "p.G719A", "type": "Missense", "cancer_type": "Lung Cancer"},
        ]
    }
}



# ====================
# Query Parsing
# ====================

def parse_query(text: str) -> dict:
    """
    Enhanced query parser - extracts gene names and cancer types.
    In a real implementation, this would use LLM/NLP.
    """
    text_lower = text.lower()
    
    # Common gene symbols to detect
    gene_symbols = ['tp53', 'brca1', 'brca2', 'egfr', 'kras', 'pten', 'pik3ca', 
                    'apc', 'rb1', 'nf1', 'cdkn2a', 'braf', 'mtor', 'fgfr3']
    
    # Cancer types to detect
    cancer_types = {
        'breast': ['breast', 'brca'],
        'lung': ['lung', 'nsclc', 'sclc'],
        'colorectal': ['colorectal', 'colon', 'crc'],
        'ovarian': ['ovarian', 'ovary'],
        'prostate': ['prostate'],
        'melanoma': ['melanoma', 'skin'],
        'pancreatic': ['pancreatic', 'pancreas']
    }
    
    detected_gene = None
    detected_cancer_type = None
    
    # Detect gene
    for gene in gene_symbols:
        if gene in text_lower:
            detected_gene = gene.upper()
            break
    
    # Detect cancer type
    for cancer_type, keywords in cancer_types.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_cancer_type = cancer_type
            break
    
    if detected_gene:
        result = {
            "query_type": "gene_mutations",
            "gene": detected_gene,
            "status": "success"
        }
        if detected_cancer_type:
            result["cancer_type"] = detected_cancer_type
        return result
    
    return {
        "query_type": "unknown",
        "status": "not_found",
        "message": "Gene not recognized. Try: TP53, BRCA1, EGFR, KRAS, etc."
    }


@app.get("/")
def read_root():
    return {
        "message": "cBioPortal AI Assistant API",
        "version": "0.1.0 (PoC)",
        "endpoints": ["/query", "/health"]
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/query")
async def query_get(text: str = Query(..., description="Natural language query")):
    """
    GET endpoint for queries - useful for browser testing.
    """
    return await process_query(text)


@app.post("/query")
async def query_post(request: QueryRequest):
    """
    POST endpoint for queries - preferred for frontend.
    """
    return await process_query(request.text)


async def process_query(text: str) -> dict:
    """
    Process the natural language query and return results from cBioPortal API.
    Falls back to sample data if API fails.
    """
    if not text or len(text.strip()) == 0:
        return {"error": "Empty query", "status": "error"}
    
    # Parse the query
    parsed = parse_query(text)
    
    if parsed["status"] == "not_found":
        return {
            "status": "error",
            "message": parsed["message"],
            "query": text
        }
    
    gene_symbol = parsed["gene"]
    cancer_type = parsed.get("cancer_type")
    
    # Try to fetch real data from cBioPortal API
    try:
        # Determine study ID based on cancer type or use default
        study_id = "msk_impact_2017"  # Default: MSK-IMPACT Clinical Sequencing Cohort
        
        if cancer_type:
            # Map cancer types to specific studies
            cancer_study_map = {
                'breast': 'brca_tcga',
                'lung': 'luad_tcga',
                'colorectal': 'coadread_tcga',
                'ovarian': 'ov_tcga',
                'prostate': 'prad_tcga'
            }
            study_id = cancer_study_map.get(cancer_type, study_id)
        
        print(f"Fetching mutations for {gene_symbol} from study: {study_id}")
        api_result = await get_gene_mutations(gene_symbol, study_id)
        
        if "error" in api_result:
            # Fall back to sample data
            print(f"API error, using sample data: {api_result['error']}")
            return get_sample_data_response(gene_symbol, text)
        
        # Format API response for frontend
        mutations = api_result.get("mutations", [])
        formatted_mutations = []
        
        for mutation in mutations[:30]:  # Limit to 30 results for display
            # Handle mutation type variations
            mut_type = mutation.get("mutationType", "Unknown")
            # Simplify mutation types for display
            if "Missense" in mut_type:
                mut_type = "Missense"
            elif "Nonsense" in mut_type or "Truncating" in mut_type:
                mut_type = "Truncating"
            elif "Frame_Shift" in mut_type or "Frameshift" in mut_type:
                mut_type = "Frameshift"
            elif "In_Frame" in mut_type or "Inframe" in mut_type:
                mut_type = "In-frame"
            elif "Splice" in mut_type:
                mut_type = "Splice"
            
            formatted_mutations.append({
                "sample_id": mutation.get("sampleId", "N/A"),
                "mutation": mutation.get("proteinChange", "N/A"),
                "type": mut_type,
                "cancer_type": study_id.replace('_', ' ').replace('tcga', 'TCGA').title(),
                "chromosome": mutation.get("chr", "N/A"),
                "position": mutation.get("startPosition", "N/A"),
                "ref_allele": mutation.get("referenceAllele", ""),
                "var_allele": mutation.get("variantAllele", "")
            })
        
        return {
            "status": "success",
            "query": text,
            "parsed_query": parsed,
            "gene": gene_symbol,
            "description": f"Mutations from cBioPortal ({study_id})",
            "mutations": formatted_mutations,
            "count": len(formatted_mutations),
            "total_in_study": api_result.get("total_count", len(mutations)),
            "study_id": study_id,
            "source": "cBioPortal API"
        }
        
    except Exception as e:
        print(f"Exception during API call: {e}")
        # Fall back to sample data on any error
        return get_sample_data_response(gene_symbol, text)


def get_sample_data_response(gene_symbol: str, query_text: str) -> dict:
    """Return sample data as fallback."""
    gene_key = gene_symbol.lower()
    if gene_key in SAMPLE_DATA:
        data = SAMPLE_DATA[gene_key]
        return {
            "status": "success",
            "query": query_text,
            "gene": data["gene"],
            "description": data["description"] + " (Sample Data)",
            "mutations": data["mutations"],
            "count": len(data["mutations"]),
            "source": "Sample Data (API unavailable)"
        }
    
    return {
        "status": "error",
        "message": f"No data found for {gene_symbol} (API unavailable)",
        "query": query_text
    }


@app.get("/genes")
def list_available_genes():
    """
    List all available genes in the PoC dataset.
    """
    return {
        "available_genes": [data["gene"] for data in SAMPLE_DATA.values()],
        "common_genes": ["TP53", "BRCA1", "BRCA2", "EGFR", "KRAS", "PTEN", "PIK3CA", "APC", "RB1"],
        "count": len(SAMPLE_DATA)
    }


@app.get("/studies")
async def get_available_studies(cancer_type: Optional[str] = None):
    """
    Get available studies from cBioPortal.
    Optionally filter by cancer type.
    """
    try:
        if cancer_type:
            studies = await search_studies_by_cancer_type(cancer_type)
        else:
            studies = await get_studies()
        
        # Return simplified study info
        simplified = [
            {
                "study_id": s.get("studyId"),
                "name": s.get("name"),
                "description": s.get("description", "")[:100],
                "cancer_type": s.get("cancerTypeId", "unknown")
            }
            for s in studies[:20]  # Limit to 20
        ]
        
        return {
            "status": "success",
            "studies": simplified,
            "count": len(simplified)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/api-status")
async def check_api_status():
    """Check if cBioPortal API is accessible."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{CBIOPORTAL_API_URL}/studies")
            return {
                "status": "online" if response.status_code == 200 else "error",
                "api_url": CBIOPORTAL_API_URL,
                "response_code": response.status_code
            }
    except Exception as e:
        return {
            "status": "offline",
            "api_url": CBIOPORTAL_API_URL,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
