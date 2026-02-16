"""
Minimal conductor agent for cloud deployment without ChromaDB.
This version works without conversation memory - just direct AI access.
"""

from typing import Dict, Any
import os

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from utils.logger import logger


class MinimalConductor:
    """Minimal conductor that works without ChromaDB/memory."""
    
    def __init__(self):
        """Initialize with OpenAI (most reliable for cloud)."""
        self.provider = "openai"
        self.model = "gpt-4o-mini"
        self.client = None
        
        # Check if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")
            
        logger.info(f"Initialized minimal conductor with {self.provider}, model: {self.model}")
    
    def _init_client(self):
        """Initialize OpenAI client."""
        if not self.client and OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def chat(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Simple chat without memory.
        
        Args:
            query: User question
            **kwargs: Ignored (for compatibility)
            
        Returns:
            Dict with 'response' and empty 'sources'
        """
        self._init_client()
        
        logger.info(f"Processing query: {query[:100]}...")
        
        # Simple system prompt
        system_prompt = """You are a helpful AI assistant. Answer questions clearly and concisely."""
        
        # Call OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
        return {
            'response': answer,
            'sources': [],
            'context_used': False
        }
