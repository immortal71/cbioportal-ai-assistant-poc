"""
LLM-based Natural Language Query Parser
Author: Aashish Kharel
GSoC 2026

This module uses Claude/GPT to parse natural language queries into structured data
that can be used to query the cBioPortal API.
"""

import json
import os
from typing import Dict, List, Optional, Any
from config import Config

# Import LLM libraries conditionally
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class LLMQueryParser:
    """Parse natural language queries using LLM"""
    
    SYSTEM_PROMPT = """You are a cancer genomics query parser for cBioPortal. Extract structured information from user queries.

Your task is to analyze the user's natural language query and extract:
1. genes: List of gene symbols (e.g., ["TP53", "BRCA1"]) - CORRECT any spelling mistakes
2. cancer_types: List of cancer types (e.g., ["breast", "lung"])
3. query_type: Type of query - "mutations", "expression", "copy_number", "clinical", or "general"
4. filters: Any additional constraints or filters mentioned
5. confidence: Your confidence in this parse (1-10 scale)

Common gene symbols: TP53, BRCA1, BRCA2, EGFR, KRAS, PIK3CA, BRAF, PTEN, APC, RB1, NF1, CDKN2A, MTOR, FGFR3, ALK, ROS1, NRAS, HRAS, AKT1, ERBB2

Common cancer types: breast, lung, colorectal, ovarian, prostate, pancreatic, melanoma, glioblastoma

IMPORTANT RULES:
- Fix spelling mistakes (e.g., "TP53 mutaions" → extract "TP53")
- Handle ambiguous genes (e.g., "BRCA" → pick "BRCA1" as most common)
- If just cancer type mentioned (e.g., "breast cancer"), leave genes empty
- For invalid genes (e.g., "FAKEGENEXYZ"), return empty genes list with low confidence
- Extract ALL genes mentioned (e.g., "TP53 and BRCA1" → ["TP53", "BRCA1"])

Respond ONLY with valid JSON in this exact format:
{
    "genes": ["GENE1", "GENE2"],
    "cancer_types": ["type1"],
    "query_type": "mutations",
    "filters": [],
    "confidence": 8,
    "reasoning": "brief explanation"
}

No additional text or explanation outside the JSON."""

    def __init__(self):
        """Initialize LLM parser"""
        self.provider = Config.LLM_PROVIDER
        
        if self.provider == "anthropic" and ANTHROPIC_AVAILABLE and Config.ANTHROPIC_API_KEY:
            self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.model = Config.CLAUDE_MODEL
        elif self.provider == "openai" and OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = Config.OPENAI_MODEL
        elif self.provider == "gemini" and GEMINI_AVAILABLE and Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.client = genai.GenerativeModel(Config.GEMINI_MODEL)
            self.model = Config.GEMINI_MODEL
        elif self.provider == "groq" and GROQ_AVAILABLE and Config.GROQ_API_KEY:
            self.client = Groq(api_key=Config.GROQ_API_KEY)
            self.model = Config.GROQ_MODEL
        elif self.provider == "ollama":
            # Ollama runs locally - no API key needed!
            self.client = "ollama"
            self.model = Config.OLLAMA_MODEL
            self.base_url = Config.OLLAMA_BASE_URL
        else:
            self.client = None
            print("[WARNING] No LLM configured. Will use pattern matching fallback.")
    
    def parse_query(self, user_query: str) -> Dict[str, Any]:
        """
        Parse a natural language query using LLM
        
        Args:
            user_query: User's natural language query
            
        Returns:
            Dictionary with structured query information
        """
        if not self.client:
            return self._fallback_parse(user_query)
        
        try:
            if self.provider == "anthropic":
                return self._parse_with_claude(user_query)
            elif self.provider == "openai":
                return self._parse_with_openai(user_query)
            elif self.provider == "gemini":
                return self._parse_with_gemini(user_query)
            elif self.provider == "groq":
                return self._parse_with_groq(user_query)
            elif self.provider == "ollama":
                return self._parse_with_ollama(user_query)
        except Exception as e:
            print(f"[ERROR] LLM parsing failed: {e}")
            return self._fallback_parse(user_query)
    
    def _parse_with_claude(self, user_query: str) -> Dict[str, Any]:
        """Parse query using Claude"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"{self.SYSTEM_PROMPT}\n\nUser query: \"{user_query}\""
                }
            ]
        )
        
        response_text = message.content[0].text
        return self._parse_llm_response(response_text)
    
    def _parse_with_openai(self, user_query: str) -> Dict[str, Any]:
        """Parse query using OpenAI"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"User query: \"{user_query}\""}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        
        response_text = response.choices[0].message.content
        return self._parse_llm_response(response_text)
    
    def _parse_with_gemini(self, user_query: str) -> Dict[str, Any]:
        """Parse query using Google Gemini"""
        full_prompt = f"{self.SYSTEM_PROMPT}\n\nUser Query: {user_query}"
        response = self.client.generate_content(full_prompt)
        response_text = response.text
        return self._parse_llm_response(response_text)
    
    def _parse_with_groq(self, user_query: str) -> Dict[str, Any]:
        """Parse query using Groq (ultra-fast inference)"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            temperature=0.3,
            max_tokens=500
        )
        response_text = response.choices[0].message.content
        return self._parse_llm_response(response_text)
    
    def _parse_with_ollama(self, user_query: str) -> Dict[str, Any]:
        """Parse query using Ollama (local LLM)"""
        import requests
        
        full_prompt = f"{self.SYSTEM_PROMPT}\n\nUser Query: {user_query}"
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        response_text = response.json()["response"]
        return self._parse_llm_response(response_text)
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate LLM JSON response"""
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            parsed = json.loads(response_text.strip())
            
            # Validate required fields
            required_fields = ["genes", "cancer_types", "query_type", "confidence"]
            for field in required_fields:
                if field not in parsed:
                    parsed[field] = [] if field != "confidence" else 5
            
            # Ensure proper types
            parsed["genes"] = [g.upper() for g in parsed.get("genes", [])]
            parsed["cancer_types"] = [c.lower() for c in parsed.get("cancer_types", [])]
            parsed["query_type"] = parsed.get("query_type", "general").lower()
            parsed["confidence"] = float(parsed.get("confidence", 5))
            parsed["filters"] = parsed.get("filters", [])
            
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse LLM response as JSON: {e}")
            print(f"Response was: {response_text}")
            return self._fallback_parse("")
    
    def _fallback_parse(self, user_query: str) -> Dict[str, Any]:
        """Fallback pattern matching when LLM is unavailable"""
        return {
            "genes": [],
            "cancer_types": [],
            "query_type": "general",
            "filters": [],
            "confidence": 0,
            "reasoning": "LLM unavailable - using fallback",
            "fallback_used": True
        }
    
    def validate_genes(self, genes: List[str], known_genes: List[str]) -> tuple[List[str], List[str]]:
        """
        Validate gene names against known gene list
        
        Returns:
            (valid_genes, invalid_genes)
        """
        known_genes_upper = [g.upper() for g in known_genes]
        valid = [g for g in genes if g.upper() in known_genes_upper]
        invalid = [g for g in genes if g.upper() not in known_genes_upper]
        
        return valid, invalid


# Singleton instance
_parser_instance = None

def get_parser() -> LLMQueryParser:
    """Get or create parser instance"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = LLMQueryParser()
    return _parser_instance
