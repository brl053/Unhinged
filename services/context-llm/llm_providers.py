#!/usr/bin/env python3
"""
LLM Providers for Context-Aware LLM Service
Supports multiple LLM backends including Ollama and OpenAI
"""

import os
import logging
import requests
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    text: str
    model: str
    tokens_used: Optional[int] = None
    processing_time: float = 0.0
    success: bool = True
    error: Optional[str] = None

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 500, 
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available"""
        pass

class OllamaProvider(LLMProvider):
    """Ollama LLM provider"""
    
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "openhermes"):
        self.base_url = base_url.rstrip('/')
        self.default_model = default_model
        self.session = requests.Session()
        self.session.timeout = 60
        
    def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 500, 
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> str:
        """Generate text using Ollama"""
        try:
            start_time = time.time()
            model_name = model or self.default_model
            
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9,
                    "stop": ["Human:", "Assistant:", "\n\n"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '').strip()
                
                processing_time = time.time() - start_time
                logger.debug(f"Ollama generation completed in {processing_time:.2f}s")
                
                return generated_text
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return ""
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []

class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self, api_key: str, default_model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.default_model = default_model
        self.base_url = "https://api.openai.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        
    def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 500, 
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> str:
        """Generate text using OpenAI"""
        try:
            start_time = time.time()
            model_name = model or self.default_model
            
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9
            }
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result['choices'][0]['message']['content'].strip()
                
                processing_time = time.time() - start_time
                logger.debug(f"OpenAI generation completed in {processing_time:.2f}s")
                
                return generated_text
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return ""
    
    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        try:
            response = self.session.get(f"{self.base_url}/models", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider"""
    
    def __init__(self, api_key: str, default_model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.default_model = default_model
        self.base_url = "https://api.anthropic.com/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        })
        
    def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 500, 
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> str:
        """Generate text using Anthropic Claude"""
        try:
            start_time = time.time()
            model_name = model or self.default_model
            
            payload = {
                "model": model_name,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/messages",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result['content'][0]['text'].strip()
                
                processing_time = time.time() - start_time
                logger.debug(f"Anthropic generation completed in {processing_time:.2f}s")
                
                return generated_text
            else:
                logger.error(f"Anthropic API error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            return ""
    
    def is_available(self) -> bool:
        """Check if Anthropic is available"""
        try:
            # Anthropic doesn't have a simple health check endpoint
            # We'll do a minimal request to test connectivity
            payload = {
                "model": self.default_model,
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "Hi"}]
            }
            response = self.session.post(
                f"{self.base_url}/messages",
                json=payload,
                timeout=5
            )
            return response.status_code in [200, 400]  # 400 might be rate limit but service is available
        except Exception:
            return False

def create_llm_provider() -> LLMProvider:
    """Factory function to create the best available LLM provider"""
    
    # Try OpenAI first if API key is available
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        provider = OpenAIProvider(openai_key)
        if provider.is_available():
            logger.info("Using OpenAI as LLM provider")
            return provider
    
    # Try Anthropic if API key is available
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key:
        provider = AnthropicProvider(anthropic_key)
        if provider.is_available():
            logger.info("Using Anthropic as LLM provider")
            return provider
    
    # Fall back to Ollama
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    provider = OllamaProvider(ollama_host)
    if provider.is_available():
        logger.info(f"Using Ollama as LLM provider: {ollama_host}")
        return provider
    
    # If nothing is available, return a dummy provider
    logger.warning("No LLM providers available, using dummy provider")
    return DummyProvider()

class DummyProvider(LLMProvider):
    """Dummy provider for when no real providers are available"""
    
    def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 500, 
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> str:
        return f"[Dummy response for prompt: {prompt[:50]}...]"
    
    def is_available(self) -> bool:
        return True
