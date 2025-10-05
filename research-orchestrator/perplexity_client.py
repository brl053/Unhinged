"""
Perplexity AI API Client
"""
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import settings, get_api_key


@dataclass
class ResearchQuery:
    """Structured research query"""
    topic: str
    focus: str
    depth: str
    context: Dict[str, Any]
    custom_instructions: Optional[str] = None


@dataclass
class ResearchResponse:
    """Structured research response"""
    content: str
    citations: List[str]
    related_questions: List[str]
    metadata: Dict[str, Any]
    raw_response: Dict[str, Any]


class PerplexityClient:
    """Client for Perplexity AI API"""
    
    def __init__(self):
        self.api_key = get_api_key()
        self.base_url = settings.perplexity_api_base
        self.console = Console()
        
        if not self.api_key:
            raise ValueError("Perplexity API key not found. Run setup first.")
    
    def research(self, query: ResearchQuery) -> ResearchResponse:
        """Conduct research using Perplexity AI"""
        
        # Build the research prompt
        prompt = self._build_research_prompt(query)
        
        # Make API request
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Researching {query.topic}...", total=None)
            
            response = self._make_api_request(prompt, query.context.get("model", settings.default_model))
            
            progress.update(task, description="Processing response...")
            
        # Parse and structure response
        return self._parse_response(response, query)
    
    def _build_research_prompt(self, query: ResearchQuery) -> str:
        """Build a comprehensive research prompt"""
        
        # Base system prompt based on depth
        system_prompts = {
            "senior-ic": """You are a senior individual contributor (IC) providing comprehensive technical documentation. 
            Focus on practical implementation details, best practices, architectural considerations, and real-world challenges. 
            Provide code examples, performance considerations, and potential pitfalls.""",
            
            "architect": """You are a technical architect providing high-level system design guidance. 
            Focus on architecture patterns, technology stack decisions, scalability considerations, and integration strategies.""",
            
            "implementation": """You are a technical expert providing detailed implementation guidance. 
            Focus on step-by-step instructions, code examples, configuration details, and troubleshooting."""
        }
        
        # Focus-specific instructions
        focus_instructions = {
            "react-wrapper": """
            Specifically for React wrapper development:
            - Component architecture and prop design
            - TypeScript interfaces and type definitions
            - React hooks integration patterns
            - State management considerations
            - Event handling and lifecycle methods
            - Performance optimization for React
            - Testing with React Testing Library
            - Accessibility considerations
            - Bundle size and tree-shaking
            - SSR/SSG compatibility
            """,
            
            "api-integration": """
            Specifically for API integration:
            - Authentication and authorization patterns
            - Request/response handling
            - Error handling and retry logic
            - Rate limiting and throttling
            - Caching strategies
            - Data transformation and validation
            - Real-time updates (WebSocket/SSE)
            - Testing API integrations
            """,
            
            "platform-integration": """
            Specifically for Unhinged Platform integration:
            - Platform authentication and user management
            - Theme system integration
            - Real-time collaboration features
            - Platform-specific APIs and services
            - Deployment and configuration
            - Performance monitoring and analytics
            """
        }
        
        # Build the complete prompt
        system_prompt = system_prompts.get(query.depth, system_prompts["senior-ic"])
        focus_instruction = focus_instructions.get(query.focus, "")
        
        prompt = f"""
        {system_prompt}
        
        {focus_instruction}
        
        Research Topic: {query.topic}
        
        Please provide comprehensive technical documentation covering:
        1. Overview and core concepts
        2. Architecture and design patterns
        3. Implementation details with code examples
        4. Best practices and recommendations
        5. Performance and security considerations
        6. Testing strategies
        7. Common pitfalls and solutions
        8. Integration considerations
        9. Deployment and operational aspects
        10. Future considerations and roadmap
        
        Structure this as a technical specification document suitable for {query.depth} level engineers.
        
        {query.custom_instructions or ""}
        """
        
        return prompt.strip()
    
    def _make_api_request(self, prompt: str, model: str) -> Dict[str, Any]:
        """Make request to Perplexity API"""
        
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a senior technical expert providing comprehensive, accurate, and detailed technical documentation."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature,
            "top_p": 0.9,
            "return_citations": True,
            "search_domain_filter": [
                "github.com",
                "stackoverflow.com", 
                "developer.mozilla.org",
                "docs.microsoft.com",
                "reactjs.org",
                "typescript-lang.org",
                "npmjs.com"
            ],
            "return_images": False,
            "return_related_questions": True,
            "search_recency_filter": "month",
            "top_k": 0,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]API request failed: {e}[/red]")
            raise
        except json.JSONDecodeError as e:
            self.console.print(f"[red]Failed to parse API response: {e}[/red]")
            raise
    
    def _parse_response(self, response: Dict[str, Any], query: ResearchQuery) -> ResearchResponse:
        """Parse and structure the API response"""
        
        try:
            # Extract main content
            content = response["choices"][0]["message"]["content"]
            
            # Extract citations
            citations = response.get("citations", [])
            
            # Extract related questions
            related_questions = response.get("related_questions", [])
            
            # Build metadata
            metadata = {
                "model": response.get("model", "unknown"),
                "usage": response.get("usage", {}),
                "query_topic": query.topic,
                "query_focus": query.focus,
                "query_depth": query.depth,
                "timestamp": time.time()
            }
            
            return ResearchResponse(
                content=content,
                citations=citations,
                related_questions=related_questions,
                metadata=metadata,
                raw_response=response
            )
            
        except KeyError as e:
            self.console.print(f"[red]Unexpected API response format: {e}[/red]")
            raise
    
    def quick_query(self, question: str, model: str = None) -> str:
        """Quick research query for simple questions"""
        
        model = model or "llama-3.1-sonar-small-128k-online"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Getting quick answer...", total=None)
            
            response = self._make_api_request(question, model)
            
        return response["choices"][0]["message"]["content"]
    
    def test_connection(self) -> bool:
        """Test API connection and key validity"""
        try:
            response = self.quick_query("Test query: What is Python?")
            return bool(response)
        except Exception as e:
            self.console.print(f"[red]Connection test failed: {e}[/red]")
            return False
