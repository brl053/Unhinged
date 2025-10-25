
# Initialize GUI event logger
gui_logger = create_gui_logger("unhinged-llm-client", "1.0.0")

"""
@llm-type service
@llm-legend llm_client.py - microservice component
@llm-key Core functionality for llm_client
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token llm_client: microservice component
"""
"""
🤖 LLM Service Client - Real Service Integration

Connects the mobile-first native GUI to actual LLM services.
Provides both HTTP REST API and gRPC integration with service discovery.
"""

import asyncio
import json
import time
from typing import Optional, Dict, Any, Callable, AsyncIterator
from pathlib import Path
from dataclasses import dataclass
from unhinged_events import create_gui_logger

# Try to import HTTP libraries (optional)
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    gui_logger.warn(" aiohttp not available - using fallback mode")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    gui_logger.warn(" requests not available - using fallback mode")

# Try to import gRPC (optional)
try:
    import grpc
    # Import from generated proto clients
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent.parent
    proto_clients_path = str(project_root / "generated" / "python" / "clients")
    unhinged_proto_path = str(project_root / "generated" / "python" / "clients" / "unhinged_proto_clients")

    # Add both paths to ensure relative imports work
    if proto_clients_path not in sys.path:
        sys.path.insert(0, proto_clients_path)
    if unhinged_proto_path not in sys.path:
        sys.path.insert(0, unhinged_proto_path)

    from unhinged_proto_clients import llm_pb2, llm_pb2_grpc, common_pb2
    GRPC_AVAILABLE = True
    gui_logger.info(" gRPC and proto clients available", {"status": "success"})
except ImportError as e:
    GRPC_AVAILABLE = False
    gui_logger.warn(f" gRPC not available - using HTTP fallback: {e}")


@dataclass
class LLMServiceConfig:
    """LLM service configuration"""
    name: str
    base_url: str
    grpc_port: Optional[int] = None
    api_key: Optional[str] = None
    model: str = "llama3.2"
    timeout: int = 30


class LLMServiceClient:
    """
    Production-ready LLM service client with multiple backends.
    
    Supports:
    - Ollama (local LLM service)
    - Persistence Platform (Independent Kotlin - NO SPRING BOOT)
    - gRPC LLM service
    - Service discovery and health checks
    """
    
    # Service configurations based on docker-compose.production.yml
    SERVICE_CONFIGS = {
        "ollama": LLMServiceConfig(
            name="Ollama",
            base_url="http://localhost:1500",  # External port from compose
            model="llama3.2"
        ),
        "persistence": LLMServiceConfig(
            name="Persistence Platform",
            base_url="http://localhost:8190",  # Independent Kotlin platform (external port)
            model="llama3.2"
        ),
        "grpc_llm": LLMServiceConfig(
            name="gRPC LLM Service",
            base_url="http://localhost:1510",
            grpc_port=1510,
            model="llama3.2"
        )
    }
    
    def __init__(self, preferred_service: str = "ollama"):
        self.preferred_service = preferred_service
        self.current_service: Optional[LLMServiceConfig] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.grpc_channel: Optional[Any] = None
        self.grpc_stub: Optional[Any] = None
        
        # Service discovery
        self.available_services: Dict[str, bool] = {}
        
    
    async def initialize(self):
        """Initialize the client and discover available services"""
        if AIOHTTP_AVAILABLE:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        else:
            self.session = None
            gui_logger.warn(" aiohttp not available - using fallback HTTP client")

        # Discover available services
        await self._discover_services()

        # Select best available service
        self._select_service()

    
    async def _discover_services(self):
        """Discover which LLM services are available"""
        gui_logger.debug(" Discovering LLM services...", {"event_type": "scanning"})

        if not AIOHTTP_AVAILABLE and not REQUESTS_AVAILABLE:
            gui_logger.warn(" No HTTP libraries available - all services marked as unavailable")
            for service_id in self.SERVICE_CONFIGS:
                self.available_services[service_id] = False
            return

        for service_id, config in self.SERVICE_CONFIGS.items():
            try:
                # Test HTTP health endpoint
                if service_id == "ollama":
                    health_url = f"{config.base_url}/api/tags"
                elif service_id == "backend":
                    health_url = f"{config.base_url}/health"
                else:
                    health_url = f"{config.base_url}/health"

                if AIOHTTP_AVAILABLE and self.session:
                    async with self.session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status == 200:
                            self.available_services[service_id] = True
                        else:
                            self.available_services[service_id] = False
                elif REQUESTS_AVAILABLE:
                    # Fallback to requests
                    response = requests.get(health_url, timeout=5)
                    if response.status_code == 200:
                        self.available_services[service_id] = True
                    else:
                        self.available_services[service_id] = False
                else:
                    self.available_services[service_id] = False

            except Exception as e:
                self.available_services[service_id] = False
    
    def _select_service(self):
        """Select the best available service"""
        # Try preferred service first
        if self.preferred_service in self.available_services and self.available_services[self.preferred_service]:
            self.current_service = self.SERVICE_CONFIGS[self.preferred_service]
            return
        
        # Fallback to any available service
        for service_id, available in self.available_services.items():
            if available:
                self.current_service = self.SERVICE_CONFIGS[service_id]
                return
        
        gui_logger.error(" No LLM services available")
        self.current_service = None
    
    async def send_message(self, message: str, conversation_history: list = None) -> str:
        """Send a message to the LLM service and get response"""
        if not self.current_service:
            if not AIOHTTP_AVAILABLE and not REQUESTS_AVAILABLE:
                return "❌ No HTTP libraries available. Please install aiohttp or requests: pip install aiohttp requests"
            return "❌ No LLM service available. Please start services with 'make up' or 'make dev-up'"

        try:
            if self.current_service.name == "Ollama":
                return await self._send_ollama_message(message, conversation_history)
            elif self.current_service.name == "Backend API":
                return await self._send_backend_message(message, conversation_history)
            elif self.current_service.name == "gRPC LLM Service":
                return await self._send_grpc_message(message, conversation_history)
            else:
                return "❌ Unknown service type"

        except Exception as e:
            gui_logger.error(f" LLM service error: {e}")
            return f"❌ Service error: {str(e)}"
    
    async def _send_ollama_message(self, message: str, history: list = None) -> str:
        """Send message to Ollama service"""
        url = f"{self.current_service.base_url}/api/generate"
        
        # Build prompt with history
        prompt = message
        if history:
            context = "\n".join([f"User: {h.get('user', '')}\nAssistant: {h.get('assistant', '')}" 
                               for h in history[-5:]])  # Last 5 exchanges
            prompt = f"Context:\n{context}\n\nUser: {message}\nAssistant:"
        
        payload = {
            "model": self.current_service.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("response", "No response from Ollama")
            else:
                error_text = await response.text()
                return f"❌ Ollama error ({response.status}): {error_text[:100]}..."
    
    async def _send_backend_message(self, message: str, history: list = None) -> str:
        """Send message to Backend API"""
        url = f"{self.current_service.base_url}/api/v1/chat"
        
        payload = {
            "prompt": message,
            "sessionId": "mobile-chat-session",
            "userId": "mobile-user",
            "model": self.current_service.model,
            "history": history or []
        }
        
        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("response", data.get("message", "No response from backend"))
            else:
                error_text = await response.text()
                return f"❌ Backend error ({response.status}): {error_text[:100]}..."
    
    async def _send_grpc_message(self, message: str, history: list = None) -> str:
        """Send message via gRPC (if available)"""
        if not GRPC_AVAILABLE:
            return "❌ gRPC not available"
        
        try:
            # Setup gRPC connection if needed
            if not self.grpc_channel:
                self.grpc_channel = grpc.aio.insecure_channel(f"localhost:{self.current_service.grpc_port}")
                self.grpc_stub = llm_pb2_grpc.LLMServiceStub(self.grpc_channel)
            
            # Build request
            request = llm_pb2.CompletionRequest()
            request.model = self.current_service.model
            request.session_id = "mobile-chat-session"
            
            # Add message
            chat_message = request.messages.add()
            chat_message.role = "user"
            chat_message.content = message
            
            # Add history
            if history:
                for exchange in history[-5:]:  # Last 5 exchanges
                    if "user" in exchange:
                        user_msg = request.messages.add()
                        user_msg.role = "user"
                        user_msg.content = exchange["user"]
                    if "assistant" in exchange:
                        assistant_msg = request.messages.add()
                        assistant_msg.role = "assistant"
                        assistant_msg.content = exchange["assistant"]
            
            # Send request
            response = await self.grpc_stub.GenerateCompletion(request)
            
            if response.success:
                return response.content
            else:
                return f"❌ gRPC error: {response.error_message}"
                
        except Exception as e:
            return f"❌ gRPC connection error: {str(e)}"
    
    async def stream_message(self, message: str, callback: Callable[[str], None], history: list = None):
        """Stream LLM response (for real-time typing effect)"""
        if not self.current_service:
            callback("❌ No LLM service available")
            return
        
        try:
            if self.current_service.name == "Ollama":
                await self._stream_ollama_message(message, callback, history)
            else:
                # Fallback to non-streaming
                response = await self.send_message(message, history)
                # Simulate streaming by sending chunks
                words = response.split()
                for i, word in enumerate(words):
                    callback(word + (" " if i < len(words) - 1 else ""))
                    await asyncio.sleep(0.05)  # 50ms delay between words
                    
        except Exception as e:
            callback(f"❌ Streaming error: {str(e)}")
    
    async def _stream_ollama_message(self, message: str, callback: Callable[[str], None], history: list = None):
        """Stream response from Ollama"""
        url = f"{self.current_service.base_url}/api/generate"
        
        prompt = message
        if history:
            context = "\n".join([f"User: {h.get('user', '')}\nAssistant: {h.get('assistant', '')}" 
                               for h in history[-5:]])
            prompt = f"Context:\n{context}\n\nUser: {message}\nAssistant:"
        
        payload = {
            "model": self.current_service.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'response' in data:
                                callback(data['response'])
                            if data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                error_text = await response.text()
                callback(f"❌ Streaming error: {error_text[:100]}...")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status"""
        return {
            "current_service": self.current_service.name if self.current_service else None,
            "available_services": self.available_services,
            "preferred_service": self.preferred_service,
            "grpc_available": GRPC_AVAILABLE
        }
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
        
        if self.grpc_channel:
            await self.grpc_channel.close()
        
