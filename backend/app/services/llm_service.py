"""
LLM Service for interacting with various language models.
Supports Google Gemini, OpenAI, Mistral, and others.
"""
from typing import List, Dict, Any, Optional
import logging
from enum import Enum

from app.config import settings

logger = logging.getLogger(__name__)


class ModelComplexity(Enum):
    """Model complexity levels."""
    SIMPLE = "simple"
    COMPLEX = "complex"


class LLMService:
    """Service for interacting with LLMs."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.provider = settings.model_provider
        self._client = None
        logger.info(f"Initializing LLM service with provider: {self.provider}")
    
    def _get_client(self):
        """Lazy load the appropriate LLM client."""
        if self._client is not None:
            return self._client
        
        if self.provider.lower() in ["gemini", "google"]:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self._client = genai
                logger.info("Gemini client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                raise
        
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
                raise
        
        elif self.provider == "mistral":
            try:
                from mistralai.client import MistralClient
                self._client = MistralClient(api_key=settings.mistral_api_key)
                logger.info("Mistral client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Mistral: {e}")
                raise
        
        else:
            # Default to mock client for development
            logger.warning(f"Unknown provider '{self.provider}', using mock client")
            self._client = "mock"
        
        return self._client
    
    def generate(
        self,
        prompt: str,
        complexity: ModelComplexity = ModelComplexity.SIMPLE,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate text using the configured LLM.
        
        Args:
            prompt: Input prompt.
            complexity: Model complexity level.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            system_prompt: Optional system prompt.
            
        Returns:
            Generated text.
        """
        client = self._get_client()
        
        # Select model based on complexity
        model = (
            settings.large_model if complexity == ModelComplexity.COMPLEX
            else settings.small_model
        )
        
        logger.info(f"Generating with {model} (temp={temperature})")
        
        try:
            if self.provider.lower() in ["gemini", "google"]:
                return self._generate_gemini(
                    client, model, prompt, temperature, max_tokens, system_prompt
                )
            elif self.provider == "openai":
                return self._generate_openai(
                    client, model, prompt, temperature, max_tokens, system_prompt
                )
            elif self.provider == "mistral":
                return self._generate_mistral(
                    client, model, prompt, temperature, max_tokens, system_prompt
                )
            else:
                # Mock response for development
                return f"[Mock response to: {prompt[:100]}...]"
        
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return f"I encountered an error while processing your request. Please try again."
    
    def _generate_gemini(
        self,
        client: Any,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> str:
        """Generate using Google Gemini."""
        model_instance = client.GenerativeModel(model)
        
        # Combine system prompt if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = model_instance.generate_content(
            full_prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
        )
        
        return response.text
    
    def _generate_openai(
        self,
        client: Any,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> str:
        """Generate using OpenAI."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def _generate_mistral(
        self,
        client: Any,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> str:
        """Generate using Mistral."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def compress_prompt(self, prompt: str, target_tokens: int = None) -> str:
        """Compress prompt to reduce token usage.
        
        Args:
            prompt: Original prompt.
            target_tokens: Target token count.
            
        Returns:
            Compressed prompt.
        """
        if not settings.enable_prompt_compression:
            return prompt
        
        target_tokens = target_tokens or settings.max_prompt_tokens
        
        # Simple compression: truncate if too long
        # In production, use more sophisticated methods
        words = prompt.split()
        if len(words) > target_tokens:
            compressed = " ".join(words[:target_tokens])
            logger.info(f"Compressed prompt from {len(words)} to {target_tokens} words")
            return compressed + "..."
        
        return prompt


# Singleton instance
llm_service = LLMService()
