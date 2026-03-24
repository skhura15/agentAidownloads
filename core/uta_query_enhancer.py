"""
Query Enhancement Module for RAG

Improves retrieval by:
1. Query expansion - generate multiple search queries
2. Hypothetical Document Embedding (HyDE) - generate hypothetical answer for better matching
3. Keyword extraction - extract key terms for hybrid search
4. Query rewriting - reformulate queries for better semantic matching
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EnhancedQuery:
    """Enhanced query with multiple search variations."""
    original_query: str
    expanded_queries: List[str]  # Multiple query reformulations
    keywords: List[str]  # Extracted keywords for hybrid search
    hypothetical_answer: Optional[str]  # HyDE-style hypothetical document
    intent: str  # Detected query intent


class QueryEnhancer:
    """
    Enhances queries for better RAG retrieval.
    
    Strategies:
    1. Multi-query expansion: Generate semantically similar queries
    2. Keyword extraction: Pull out key technical terms
    3. HyDE: Create hypothetical answer text for embedding
    4. Intent detection: Understand what type of answer is needed
    """
    
    # Domain-specific synonyms for CCaaS
    DOMAIN_SYNONYMS = {
        "routing": ["queue", "skill-based routing", "call distribution", "agent assignment", "overflow"],
        "call": ["contact", "interaction", "voice", "phone"],
        "agent": ["representative", "user", "operator", "CSR"],
        "error": ["issue", "problem", "failure", "exception", "bug"],
        "timeout": ["delay", "latency", "slow", "hang", "unresponsive"],
        "connection": ["connectivity", "network", "websocket", "link"],
        "license": ["licensing", "SKU", "entitlement", "permission", "subscription"],
        "queue": ["routing queue", "call queue", "contact queue"],
        "skill": ["proficiency", "capability", "expertise"],
        "config": ["configuration", "settings", "setup", "parameter"],
    }
    
    # Technical term patterns
    ERROR_CODE_PATTERN = re.compile(r'\b(ERR[-_]?\d+|[A-Z]{2,5}[-_]\d{3,})\b', re.IGNORECASE)
    
    def __init__(self, llm_client=None, use_llm: bool = True):
        """
        Initialize query enhancer.
        
        Args:
            llm_client: Optional LLM client for advanced query expansion
            use_llm: Whether to use LLM for query expansion (can be disabled for speed)
        """
        self.llm = llm_client
        self.use_llm = use_llm and llm_client is not None
    
    def enhance(self, query: str) -> EnhancedQuery:
        """
        Enhance a query with multiple retrieval strategies.
        
        Args:
            query: Original user query
            
        Returns:
            EnhancedQuery with expanded queries and metadata
        """
        # 1. Extract keywords
        keywords = self._extract_keywords(query)
        
        # 2. Detect intent
        intent = self._detect_intent(query)
        
        # 3. Expand query
        if self.use_llm:
            expanded_queries = self._llm_expand_query(query, intent)
        else:
            expanded_queries = self._rule_based_expand(query, keywords)
        
        # 4. Generate hypothetical answer (if using LLM)
        hypothetical_answer = None
        if self.use_llm and intent in ["troubleshooting", "howto"]:
            hypothetical_answer = self._generate_hyde(query, intent)
        
        return EnhancedQuery(
            original_query=query,
            expanded_queries=expanded_queries,
            keywords=keywords,
            hypothetical_answer=hypothetical_answer,
            intent=intent,
        )
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query."""
        keywords = []
        
        # Extract error codes
        error_codes = self.ERROR_CODE_PATTERN.findall(query)
        keywords.extend(error_codes)
        
        # Extract domain-specific terms
        query_lower = query.lower()
        for term, synonyms in self.DOMAIN_SYNONYMS.items():
            if term in query_lower:
                keywords.append(term)
            for syn in synonyms:
                if syn.lower() in query_lower:
                    keywords.append(term)  # Add canonical term
                    break
        
        # Extract quoted terms (exact matches)
        quoted = re.findall(r'"([^"]+)"', query)
        keywords.extend(quoted)
        
        return list(set(keywords))
    
    def _detect_intent(self, query: str) -> str:
        """Detect the intent behind a query."""
        query_lower = query.lower()
        
        # Troubleshooting intent
        trouble_indicators = ["not working", "error", "fail", "issue", "problem", 
                             "broken", "why", "can't", "cannot", "unable"]
        if any(ind in query_lower for ind in trouble_indicators):
            return "troubleshooting"
        
        # How-to intent
        howto_indicators = ["how to", "how do", "steps to", "procedure", "configure", "setup"]
        if any(ind in query_lower for ind in howto_indicators):
            return "howto"
        
        # What-is intent (conceptual)
        whatis_indicators = ["what is", "what are", "explain", "describe", "define"]
        if any(ind in query_lower for ind in whatis_indicators):
            return "conceptual"
        
        # Search/find intent
        search_indicators = ["find", "search", "look for", "where", "locate"]
        if any(ind in query_lower for ind in search_indicators):
            return "search"
        
        return "general"
    
    def _rule_based_expand(self, query: str, keywords: List[str]) -> List[str]:
        """
        Rule-based query expansion without LLM.
        
        Generates variations using synonyms and reformulations.
        """
        expanded = [query]  # Always include original
        
        # Add synonym-based expansions
        query_lower = query.lower()
        for term, synonyms in self.DOMAIN_SYNONYMS.items():
            if term in query_lower:
                for syn in synonyms[:2]:  # Limit to avoid explosion
                    expanded_query = query_lower.replace(term, syn)
                    if expanded_query != query_lower:
                        expanded.append(expanded_query)
        
        # Add technical reformulations
        reformulations = {
            "not routing": "calls stuck in queue agents not receiving",
            "calls not routing": "skill-based routing configuration agent assignment",
            "connection timeout": "network connectivity websocket disconnect",
            "license error": "SKU entitlement feature flag permission",
            "agent status": "presence availability ready state",
        }
        
        for pattern, expansion in reformulations.items():
            if pattern in query_lower:
                expanded.append(f"{query} {expansion}")
        
        return expanded[:5]  # Limit to 5 variations
    
    def _llm_expand_query(self, query: str, intent: str) -> List[str]:
        """Use LLM to generate query expansions."""
        if not self.llm:
            return [query]
        
        try:
            prompt = f"""Generate 3 alternative search queries for this question. 
The queries should help find relevant documentation about this CCaaS (Contact Center as a Service) issue.
Focus on different ways to describe the same problem using technical terms.

Original query: {query}
Intent: {intent}

Respond with exactly 3 queries, one per line, no numbering or bullets:"""

            from core.uta_ollama_client import ChatMessage
            
            response = self.llm.chat([
                ChatMessage(role="user", content=prompt)
            ])
            
            # Parse response - one query per line
            expanded = [query]  # Always include original
            for line in response.strip().split("\n"):
                line = line.strip()
                if line and len(line) > 10:  # Skip empty/short lines
                    # Remove any numbering or bullets
                    line = re.sub(r'^[\d\.\-\*\)]+\s*', '', line)
                    if line:
                        expanded.append(line)
            
            return expanded[:4]  # Original + 3 expansions
            
        except Exception as e:
            logger.warning(f"LLM query expansion failed: {e}")
            return [query]
    
    def _generate_hyde(self, query: str, intent: str) -> Optional[str]:
        """
        Generate Hypothetical Document Embedding (HyDE).
        
        Creates a hypothetical answer that should have similar embeddings
        to actual relevant documents.
        """
        if not self.llm:
            return None
        
        try:
            if intent == "troubleshooting":
                prompt = f"""Write a brief troubleshooting guide excerpt (2-3 sentences) 
that would directly answer this CCaaS support question:

{query}

Write as if you're quoting from official documentation. Be technical and specific."""
            else:
                prompt = f"""Write a brief documentation excerpt (2-3 sentences) 
that would answer this question about CCaaS (Contact Center as a Service):

{query}

Write as if you're quoting from official documentation."""

            from core.uta_ollama_client import ChatMessage
            
            response = self.llm.chat([
                ChatMessage(role="user", content=prompt)
            ])
            
            return response.strip()
            
        except Exception as e:
            logger.warning(f"HyDE generation failed: {e}")
            return None


def expand_query_simple(query: str) -> List[str]:
    """
    Simple query expansion without LLM dependency.
    
    Quick function for basic query enhancement.
    """
    enhancer = QueryEnhancer(use_llm=False)
    result = enhancer.enhance(query)
    return result.expanded_queries
