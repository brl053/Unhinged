#!/usr/bin/env python3
"""
Multimodal Orchestrator
Coordinates between vision and text services for enhanced analysis workflows
"""

import os
import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import base64
from io import BytesIO

import httpx
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    BASIC_ANALYSIS = "basic_analysis"
    CONTEXTUAL_ANALYSIS = "contextual_analysis"
    ITERATIVE_REFINEMENT = "iterative_refinement"
    MULTI_MODEL_CONSENSUS = "multi_model_consensus"

@dataclass
class ServiceEndpoint:
    name: str
    url: str
    health_endpoint: str
    timeout: int = 30

@dataclass
class AnalysisRequest:
    image_data: bytes
    workflow_type: WorkflowType
    analysis_type: str = "screenshot"
    base_prompt: Optional[str] = None
    context_hints: Optional[Dict[str, Any]] = None
    max_iterations: int = 2
    require_consensus: bool = False

@dataclass
class AnalysisResult:
    success: bool
    description: str
    confidence: float
    processing_time: float
    workflow_used: WorkflowType
    models_used: List[str]
    iterations: int
    metadata: Dict[str, Any]
    error: Optional[str] = None

class MultimodalOrchestrator:
    """
    Orchestrates multimodal analysis workflows across vision and text services
    """
    
    def __init__(self):
        self.services = self._initialize_services()
        self.client = httpx.AsyncClient(timeout=60.0)
        self.service_health = {}
        self.workflow_stats = {}
        
        # Start health monitoring
        asyncio.create_task(self._monitor_service_health())
    
    def _initialize_services(self) -> Dict[str, ServiceEndpoint]:
        """Initialize service endpoints"""
        return {
            'vision_enhanced': ServiceEndpoint(
                name='Enhanced Vision AI',
                url=os.getenv('VISION_ENHANCED_URL', 'http://localhost:8001'),
                health_endpoint='/health'
            ),
            'vision_legacy': ServiceEndpoint(
                name='Legacy Vision AI',
                url=os.getenv('VISION_LEGACY_URL', 'http://localhost:8001'),
                health_endpoint='/health'
            ),
            'context_llm': ServiceEndpoint(
                name='Context-Aware LLM',
                url=os.getenv('CONTEXT_LLM_URL', 'http://localhost:8002'),
                health_endpoint='/health'
            )
        }
    
    async def _monitor_service_health(self):
        """Monitor health of all services"""
        while True:
            try:
                for service_name, endpoint in self.services.items():
                    try:
                        response = await self.client.get(
                            f"{endpoint.url}{endpoint.health_endpoint}",
                            timeout=5.0
                        )
                        self.service_health[service_name] = {
                            'healthy': response.status_code == 200,
                            'last_check': time.time(),
                            'response_time': response.elapsed.total_seconds()
                        }
                    except Exception as e:
                        self.service_health[service_name] = {
                            'healthy': False,
                            'last_check': time.time(),
                            'error': str(e)
                        }
                
                # Wait 30 seconds before next health check
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def analyze_image(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Main entry point for multimodal image analysis
        """
        start_time = time.time()
        
        try:
            # Select workflow based on request type
            if request.workflow_type == WorkflowType.BASIC_ANALYSIS:
                result = await self._basic_analysis_workflow(request)
            elif request.workflow_type == WorkflowType.CONTEXTUAL_ANALYSIS:
                result = await self._contextual_analysis_workflow(request)
            elif request.workflow_type == WorkflowType.ITERATIVE_REFINEMENT:
                result = await self._iterative_refinement_workflow(request)
            elif request.workflow_type == WorkflowType.MULTI_MODEL_CONSENSUS:
                result = await self._multi_model_consensus_workflow(request)
            else:
                raise ValueError(f"Unknown workflow type: {request.workflow_type}")
            
            # Update processing time
            result.processing_time = time.time() - start_time
            
            # Update workflow stats
            self._update_workflow_stats(request.workflow_type, result.success, result.processing_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return AnalysisResult(
                success=False,
                description="",
                confidence=0.0,
                processing_time=time.time() - start_time,
                workflow_used=request.workflow_type,
                models_used=[],
                iterations=0,
                metadata={},
                error=str(e)
            )
    
    async def _basic_analysis_workflow(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Basic analysis workflow using the best available vision model
        """
        # Select best available vision service
        vision_service = self._select_best_vision_service()
        
        if not vision_service:
            raise Exception("No vision services available")
        
        # Perform basic vision analysis
        vision_result = await self._call_vision_service(
            vision_service,
            request.image_data,
            request.analysis_type,
            request.base_prompt
        )
        
        return AnalysisResult(
            success=vision_result['success'],
            description=vision_result.get('description', ''),
            confidence=vision_result.get('confidence', 0.0),
            processing_time=0.0,  # Will be set by caller
            workflow_used=WorkflowType.BASIC_ANALYSIS,
            models_used=[vision_result.get('model_used', 'unknown')],
            iterations=1,
            metadata=vision_result.get('metadata', {}),
            error=vision_result.get('error')
        )
    
    async def _contextual_analysis_workflow(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Contextual analysis workflow that enhances prompts with project context
        """
        # Step 1: Generate contextual prompt
        enhanced_prompt = await self._generate_contextual_prompt(
            request.base_prompt or "Analyze this image in detail.",
            request.analysis_type,
            request.context_hints or {}
        )
        
        # Step 2: Perform vision analysis with enhanced prompt
        vision_service = self._select_best_vision_service()
        
        if not vision_service:
            raise Exception("No vision services available")
        
        vision_result = await self._call_vision_service(
            vision_service,
            request.image_data,
            request.analysis_type,
            enhanced_prompt
        )
        
        return AnalysisResult(
            success=vision_result['success'],
            description=vision_result.get('description', ''),
            confidence=vision_result.get('confidence', 0.0),
            processing_time=0.0,
            workflow_used=WorkflowType.CONTEXTUAL_ANALYSIS,
            models_used=[vision_result.get('model_used', 'unknown')],
            iterations=1,
            metadata={
                **vision_result.get('metadata', {}),
                'enhanced_prompt_used': True,
                'original_prompt': request.base_prompt,
                'enhanced_prompt': enhanced_prompt
            },
            error=vision_result.get('error')
        )
    
    async def _iterative_refinement_workflow(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Iterative refinement workflow that improves analysis through multiple passes
        """
        iterations = 0
        current_description = ""
        models_used = []
        all_metadata = {}
        
        # Initial analysis
        vision_service = self._select_best_vision_service()
        if not vision_service:
            raise Exception("No vision services available")
        
        # First pass with original or contextual prompt
        if request.context_hints:
            initial_prompt = await self._generate_contextual_prompt(
                request.base_prompt or "Analyze this image in detail.",
                request.analysis_type,
                request.context_hints
            )
        else:
            initial_prompt = request.base_prompt or "Analyze this image in detail."
        
        vision_result = await self._call_vision_service(
            vision_service,
            request.image_data,
            request.analysis_type,
            initial_prompt
        )
        
        if not vision_result['success']:
            return AnalysisResult(
                success=False,
                description="",
                confidence=0.0,
                processing_time=0.0,
                workflow_used=WorkflowType.ITERATIVE_REFINEMENT,
                models_used=[],
                iterations=0,
                metadata={},
                error=vision_result.get('error', 'Initial analysis failed')
            )
        
        current_description = vision_result.get('description', '')
        models_used.append(vision_result.get('model_used', 'unknown'))
        all_metadata.update(vision_result.get('metadata', {}))
        iterations = 1
        
        # Refinement iterations
        for i in range(min(request.max_iterations - 1, 2)):  # Max 2 additional iterations
            refinement_prompt = f"""
Based on this initial analysis: "{current_description}"

Please provide a more detailed and comprehensive analysis of the image, focusing on:
1. Any details that might have been missed
2. More specific technical information
3. Better organization of the information
4. Enhanced clarity and precision

Original analysis request: {initial_prompt}
"""
            
            refined_result = await self._call_vision_service(
                vision_service,
                request.image_data,
                request.analysis_type,
                refinement_prompt
            )
            
            if refined_result['success']:
                current_description = refined_result.get('description', current_description)
                models_used.append(refined_result.get('model_used', 'unknown'))
                all_metadata.update(refined_result.get('metadata', {}))
                iterations += 1
            else:
                break  # Stop if refinement fails
        
        return AnalysisResult(
            success=True,
            description=current_description,
            confidence=min(0.9, vision_result.get('confidence', 0.0) + (iterations - 1) * 0.1),
            processing_time=0.0,
            workflow_used=WorkflowType.ITERATIVE_REFINEMENT,
            models_used=models_used,
            iterations=iterations,
            metadata={
                **all_metadata,
                'refinement_iterations': iterations - 1,
                'initial_prompt': initial_prompt
            }
        )
    
    async def _multi_model_consensus_workflow(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Multi-model consensus workflow that combines results from multiple models
        """
        # Get available vision services
        available_services = [
            name for name, health in self.service_health.items()
            if health.get('healthy', False) and 'vision' in name
        ]
        
        if len(available_services) < 2:
            # Fall back to contextual analysis if not enough models
            return await self._contextual_analysis_workflow(request)
        
        # Prepare prompt
        if request.context_hints:
            prompt = await self._generate_contextual_prompt(
                request.base_prompt or "Analyze this image in detail.",
                request.analysis_type,
                request.context_hints
            )
        else:
            prompt = request.base_prompt or "Analyze this image in detail."
        
        # Run analysis on multiple models
        results = []
        models_used = []
        
        for service_name in available_services[:3]:  # Max 3 models
            try:
                result = await self._call_vision_service(
                    service_name,
                    request.image_data,
                    request.analysis_type,
                    prompt
                )
                
                if result['success']:
                    results.append(result)
                    models_used.append(result.get('model_used', service_name))
                    
            except Exception as e:
                logger.warning(f"Model {service_name} failed: {e}")
        
        if not results:
            raise Exception("All models failed")
        
        # Combine results (simplified consensus)
        combined_description = self._combine_analysis_results(results)
        avg_confidence = sum(r.get('confidence', 0.0) for r in results) / len(results)
        
        return AnalysisResult(
            success=True,
            description=combined_description,
            confidence=min(0.95, avg_confidence + 0.1),  # Slight boost for consensus
            processing_time=0.0,
            workflow_used=WorkflowType.MULTI_MODEL_CONSENSUS,
            models_used=models_used,
            iterations=1,
            metadata={
                'consensus_models': len(results),
                'individual_results': [r.get('description', '') for r in results]
            }
        )
    
    def _select_best_vision_service(self) -> Optional[str]:
        """Select the best available vision service"""
        # Prefer enhanced vision service if healthy
        if self.service_health.get('vision_enhanced', {}).get('healthy', False):
            return 'vision_enhanced'
        
        # Fall back to legacy service
        if self.service_health.get('vision_legacy', {}).get('healthy', False):
            return 'vision_legacy'
        
        return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _call_vision_service(
        self, 
        service_name: str, 
        image_data: bytes, 
        analysis_type: str, 
        prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Call vision service with retry logic"""
        service = self.services[service_name]
        
        # Prepare form data
        files = {'image': ('image.jpg', image_data, 'image/jpeg')}
        data = {
            'analysis_type': analysis_type,
            'max_tokens': 1024,
            'temperature': 0.1
        }
        
        if prompt:
            data['prompt'] = prompt
        
        # Make request
        response = await self.client.post(
            f"{service.url}/analyze",
            files=files,
            data=data,
            timeout=service.timeout
        )
        
        response.raise_for_status()
        return response.json()
    
    async def _generate_contextual_prompt(
        self, 
        base_prompt: str, 
        analysis_type: str, 
        context_hints: Dict[str, Any]
    ) -> str:
        """Generate contextual prompt using LLM service"""
        if not self.service_health.get('context_llm', {}).get('healthy', False):
            return base_prompt
        
        try:
            context_service = self.services['context_llm']
            
            response = await self.client.post(
                f"{context_service.url}/generate-prompt",
                json={
                    'base_prompt': base_prompt,
                    'analysis_type': analysis_type,
                    'context_types': ['documentation', 'ui_components'],
                    'max_context_items': 3,
                    'image_metadata': context_hints
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('enhanced_prompt', base_prompt)
            else:
                return base_prompt
                
        except Exception as e:
            logger.warning(f"Failed to generate contextual prompt: {e}")
            return base_prompt
    
    def _combine_analysis_results(self, results: List[Dict[str, Any]]) -> str:
        """Combine multiple analysis results into consensus description"""
        descriptions = [r.get('description', '') for r in results if r.get('description')]
        
        if not descriptions:
            return "No analysis results available"
        
        if len(descriptions) == 1:
            return descriptions[0]
        
        # Simple combination strategy - could be enhanced with LLM
        combined = f"Consensus Analysis (from {len(descriptions)} models):\n\n"
        
        for i, desc in enumerate(descriptions, 1):
            combined += f"Model {i} Analysis:\n{desc}\n\n"
        
        return combined
    
    def _update_workflow_stats(self, workflow_type: WorkflowType, success: bool, processing_time: float):
        """Update workflow statistics"""
        key = workflow_type.value
        
        if key not in self.workflow_stats:
            self.workflow_stats[key] = {
                'total_requests': 0,
                'successful_requests': 0,
                'total_time': 0.0,
                'avg_time': 0.0
            }
        
        stats = self.workflow_stats[key]
        stats['total_requests'] += 1
        stats['total_time'] += processing_time
        stats['avg_time'] = stats['total_time'] / stats['total_requests']
        
        if success:
            stats['successful_requests'] += 1
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        return self.service_health
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow statistics"""
        return self.workflow_stats
    
    async def shutdown(self):
        """Shutdown the orchestrator"""
        await self.client.aclose()

# Global orchestrator instance
orchestrator = MultimodalOrchestrator()
