"""
Gene Name Validation against cBioPortal
Author: Aashish Kharel
GSoC 2026
"""

import httpx
import json
import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from difflib import get_close_matches

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeneValidator:
    """Validate gene names against cBioPortal database"""
    
    CACHE_FILE = Path("data/known_genes.json")
    CBIOPORTAL_GENES_API = "https://www.cbioportal.org/api/genes"
    
    def __init__(self):
        """Initialize validator and load gene cache"""
        self.known_genes: List[str] = []
        self.gene_info: Dict[str, Dict] = {}
        self._load_or_fetch_genes()
    
    def _load_or_fetch_genes(self):
        """Load genes from cache or fetch from API"""
        # Try to load from cache first
        if self.CACHE_FILE.exists():
            try:
                with open(self.CACHE_FILE, 'r') as f:
                    data = json.load(f)
                    self.known_genes = data.get("genes", [])
                    self.gene_info = data.get("gene_info", {})
                logger.info(f"Loaded {len(self.known_genes)} genes from cache")
                return
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        # Fetch from API
        try:
            self._fetch_genes_from_api()
        except Exception as e:
            logger.error(f"Failed to fetch genes from API: {e}")
            # Use fallback list of common genes
            self._use_fallback_genes()
    
    def _fetch_genes_from_api(self):
        """Fetch gene list from cBioPortal API"""
        logger.info("Fetching genes from cBioPortal API...")
        
        response = httpx.get(
            self.CBIOPORTAL_GENES_API,
            headers={"Accept": "application/json"},
            timeout=30.0
        )
        
        if response.status_code == 200:
            genes_data = response.json()
            
            # Extract gene symbols and info
            for gene in genes_data[:5000]:  # Limit to first 5000
                symbol = gene.get("hugoGeneSymbol")
                if symbol:
                    self.known_genes.append(symbol)
                    self.gene_info[symbol] = {
                        "entrezGeneId": gene.get("entrezGeneId"),
                        "type": gene.get("type"),
                        "cytoband": gene.get("cytoband")
                    }
            
            logger.info(f"Fetched {len(self.known_genes)} genes from API")
            
            # Save to cache
            self._save_cache()
        else:
            raise Exception(f"API returned status {response.status_code}")
    
    def _save_cache(self):
        """Save genes to cache file"""
        self.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.CACHE_FILE, 'w') as f:
            json.dump({
                "genes": self.known_genes,
                "gene_info": self.gene_info
            }, f, indent=2)
        
        logger.info(f"Saved gene cache to {self.CACHE_FILE}")
    
    def _use_fallback_genes(self):
        """Use fallback list of common cancer genes"""
        self.known_genes = [
            "TP53", "BRCA1", "BRCA2", "EGFR", "KRAS", "PIK3CA", "BRAF",
            "PTEN", "APC", "RB1", "NF1", "CDKN2A", "MTOR", "FGFR3",
            "ALK", "ROS1", "MET", "NRAS", "HRAS", "ERBB2", "MYC",
            "ATM", "CHEK2", "PALB2", "CDH1", "STK11", "SMAD4", "VHL"
        ]
        logger.warning(f"Using fallback gene list ({len(self.known_genes)} genes)")
    
    def validate_genes(self, gene_list: List[str]) -> Tuple[List[str], List[str], Dict[str, List[str]]]:
        """
        Validate a list of gene names
        
        Args:
            gene_list: List of gene symbols to validate
            
        Returns:
            Tuple of (valid_genes, invalid_genes, suggestions)
            where suggestions is a dict mapping invalid genes to possible matches
        """
        valid = []
        invalid = []
        suggestions = {}
        
        for gene in gene_list:
            gene = gene.upper().strip()
            
            if gene in self.known_genes:
                valid.append(gene)
            else:
                invalid.append(gene)
                # Find similar genes
                matches = get_close_matches(gene, self.known_genes, n=3, cutoff=0.7)
                if matches:
                    suggestions[gene] = matches
        
        return valid, invalid, suggestions
    
    def get_gene_id(self, gene_symbol: str) -> Optional[int]:
        """Get Entrez Gene ID for a gene symbol"""
        gene_symbol = gene_symbol.upper().strip()
        info = self.gene_info.get(gene_symbol)
        return info.get("entrezGeneId") if info else None
    
    def validate_and_suggest(self, gene_list: List[str]) -> Dict:
        """
        Validate genes and return detailed report
        
        Returns:
            Dictionary with validation results and suggestions
        """
        valid, invalid, suggestions = self.validate_genes(gene_list)
        
        return {
            "all_valid": len(invalid) == 0,
            "valid_genes": valid,
            "invalid_genes": invalid,
            "suggestions": suggestions,
            "summary": f"{len(valid)}/{len(gene_list)} genes validated successfully"
        }


# Example usage
if __name__ == "__main__":
    validator = GeneValidator()
    
    # Test cases
    test_genes = ["TP53", "BRCA1", "EGFR", "INVALID_GENE", "KRA"]  # KRA is typo of KRAS
    
    result = validator.validate_and_suggest(test_genes)
    print(json.dumps(result, indent=2))
