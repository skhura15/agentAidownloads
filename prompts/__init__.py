"""
Prompts Package

This package contains centralized prompt templates and management.
"""

from prompts.prompt_manager import PromptManager, PromptTemplate

# UTA RAG Prompts
from prompts.uta_rag_prompts import RAGPrompts

__all__ = [
    "PromptManager", 
    "PromptTemplate",
    # UTA Prompts
    "RAGPrompts",
]
