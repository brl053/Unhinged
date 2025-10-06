#!/usr/bin/env python3
"""
Enhanced Vision Processor with Multi-Model Support
Handles image analysis, OCR, UI understanding, and contextual processing
"""

import os
import logging
import torch
import asyncio
from typing import Dict, Any, Optional, List, Union, Tuple
from PIL import Image
import numpy as np
from dataclasses import dataclass
from enum import Enum
import time
import base64
import io

from models.model_manager import model_manager, ModelType

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    BASIC_CAPTION = "basic_caption"
    DETAILED_DESCRIPTION = "detailed_description"
    OCR_EXTRACTION = "ocr_extraction"
    UI_ANALYSIS = "ui_analysis"
    SCREENSHOT_ANALYSIS = "screenshot_analysis"
    CONTEXTUAL_ANALYSIS = "contextual_analysis"

@dataclass
class VisionRequest:
    image: Image.Image
    analysis_type: AnalysisType
    prompt: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    max_tokens: int = 512
    temperature: float = 0.1
    preferred_model: Optional[ModelType] = None

@dataclass
class VisionResponse:
    success: bool
    description: str
    analysis_type: AnalysisType
    model_used: str
    confidence: float
    processing_time: float
    metadata: Dict[str, Any]
    error: Optional[str] = None

class EnhancedVisionProcessor:
    """
    Enhanced vision processor supporting multiple models and analysis types
    """
    
    def __init__(self):
        self.processing_stats = {}
        self.ocr_engines = self._initialize_ocr_engines()
    
    def _initialize_ocr_engines(self) -> Dict[str, Any]:
        """Initialize OCR engines for text extraction"""
        engines = {}
        
        try:
            import pytesseract
            engines['tesseract'] = pytesseract
            logger.info("✅ Tesseract OCR initialized")
        except ImportError:
            logger.warning("Tesseract not available")
        
        try:
            import easyocr
            engines['easyocr'] = easyocr.Reader(['en'])
            logger.info("✅ EasyOCR initialized")
        except ImportError:
            logger.warning("EasyOCR not available")
        
        return engines
    
    async def process_image(self, request: VisionRequest) -> VisionResponse:
        """
        Main image processing method with intelligent model routing
        """
        start_time = time.time()
        
        try:
            # Determine optimal model for the request
            model_type, model_info = self._select_optimal_model(request)
            
            if not model_info:
                return VisionResponse(
                    success=False,
                    description="",
                    analysis_type=request.analysis_type,
                    model_used="none",
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    metadata={},
                    error="No suitable model available"
                )
            
            # Process based on analysis type
            if request.analysis_type == AnalysisType.SCREENSHOT_ANALYSIS:
                result = await self._process_screenshot(request, model_type, model_info)
            elif request.analysis_type == AnalysisType.UI_ANALYSIS:
                result = await self._process_ui_analysis(request, model_type, model_info)
            elif request.analysis_type == AnalysisType.OCR_EXTRACTION:
                result = await self._process_ocr(request, model_type, model_info)
            elif request.analysis_type == AnalysisType.CONTEXTUAL_ANALYSIS:
                result = await self._process_contextual(request, model_type, model_info)
            else:
                result = await self._process_basic_analysis(request, model_type, model_info)
            
            # Update processing stats
            processing_time = time.time() - start_time
            self._update_stats(model_type, request.analysis_type, processing_time, result.success)
            
            result.processing_time = processing_time
            return result
            
        except Exception as e:
            logger.error(f"Vision processing failed: {e}")
            return VisionResponse(
                success=False,
                description="",
                analysis_type=request.analysis_type,
                model_used="error",
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={},
                error=str(e)
            )
    
    def _select_optimal_model(self, request: VisionRequest) -> Tuple[Optional[ModelType], Optional[Dict[str, Any]]]:
        """
        Select the best model for the given request
        """
        # If user specified a preferred model, try that first
        if request.preferred_model:
            model_info = model_manager.models.get(request.preferred_model)
            if model_info:
                return request.preferred_model, model_info
        
        # Select based on analysis type requirements
        if request.analysis_type in [AnalysisType.SCREENSHOT_ANALYSIS, AnalysisType.UI_ANALYSIS, AnalysisType.OCR_EXTRACTION]:
            # Prefer models with OCR and UI capabilities
            for model_type in [ModelType.QWEN2_VL_7B]:
                if model_type in model_manager.models:
                    config = model_manager.model_configs[model_type]
                    if config.supports_ocr and config.supports_ui:
                        return model_type, model_manager.models[model_type]
        
        # Fallback to primary model
        primary = model_manager.get_primary_model()
        if primary:
            return primary[0], primary[1]
        
        return None, None
    
    async def _process_screenshot(self, request: VisionRequest, model_type: ModelType, model_info: Dict[str, Any]) -> VisionResponse:
        """
        Process screenshot with UI understanding and OCR
        """
        if model_type == ModelType.QWEN2_VL_7B:
            return await self._process_with_qwen2vl(request, model_info, 
                "Analyze this screenshot in detail. Describe the UI elements, text content, layout, and any interactive components. Focus on the structure and functionality.")
        else:
            # Fallback to basic processing + OCR
            basic_result = await self._process_basic_analysis(request, model_type, model_info)
            ocr_text = self._extract_text_with_ocr(request.image)
            
            enhanced_description = f"{basic_result.description}\n\nExtracted Text: {ocr_text}"
            
            return VisionResponse(
                success=True,
                description=enhanced_description,
                analysis_type=request.analysis_type,
                model_used=f"{model_type.value}+ocr",
                confidence=basic_result.confidence * 0.8,  # Slightly lower confidence for fallback
                processing_time=0,
                metadata={
                    "ocr_text": ocr_text,
                    "fallback_used": True
                }
            )
    
    async def _process_ui_analysis(self, request: VisionRequest, model_type: ModelType, model_info: Dict[str, Any]) -> VisionResponse:
        """
        Process UI-specific analysis
        """
        ui_prompt = request.prompt or "Analyze this user interface. Identify all UI components, their types (buttons, forms, menus, etc.), layout structure, and describe the user workflow or functionality."
        
        if model_type == ModelType.QWEN2_VL_7B:
            return await self._process_with_qwen2vl(request, model_info, ui_prompt)
        else:
            return await self._process_basic_analysis(request, model_type, model_info)
    
    async def _process_ocr(self, request: VisionRequest, model_type: ModelType, model_info: Dict[str, Any]) -> VisionResponse:
        """
        Extract text from image using OCR
        """
        ocr_text = self._extract_text_with_ocr(request.image)
        
        # If we have a capable model, also get contextual understanding
        if model_type == ModelType.QWEN2_VL_7B:
            context_result = await self._process_with_qwen2vl(request, model_info, 
                f"Extract and organize all text from this image. Provide the text content and explain its structure and context. Raw OCR text: {ocr_text}")
            
            return VisionResponse(
                success=True,
                description=context_result.description,
                analysis_type=request.analysis_type,
                model_used=f"{model_type.value}+ocr",
                confidence=context_result.confidence,
                processing_time=0,
                metadata={
                    "raw_ocr_text": ocr_text,
                    "structured_extraction": True
                }
            )
        else:
            return VisionResponse(
                success=True,
                description=f"Extracted text: {ocr_text}",
                analysis_type=request.analysis_type,
                model_used="ocr_only",
                confidence=0.9 if ocr_text.strip() else 0.3,
                processing_time=0,
                metadata={"raw_ocr_text": ocr_text}
            )
    
    async def _process_contextual(self, request: VisionRequest, model_type: ModelType, model_info: Dict[str, Any]) -> VisionResponse:
        """
        Process image with additional context from documentation or codebase
        """
        context_prompt = self._build_contextual_prompt(request)
        
        if model_type == ModelType.QWEN2_VL_7B:
            return await self._process_with_qwen2vl(request, model_info, context_prompt)
        else:
            return await self._process_basic_analysis(request, model_type, model_info)
    
    def _build_contextual_prompt(self, request: VisionRequest) -> str:
        """
        Build a contextual prompt using available context
        """
        base_prompt = request.prompt or "Analyze this image in detail."
        
        if request.context:
            context_info = []
            
            if 'project_type' in request.context:
                context_info.append(f"This is from a {request.context['project_type']} project.")
            
            if 'ui_components' in request.context:
                context_info.append(f"Expected UI components: {', '.join(request.context['ui_components'])}")
            
            if 'documentation_context' in request.context:
                context_info.append(f"Project context: {request.context['documentation_context']}")
            
            if context_info:
                base_prompt += f"\n\nContext: {' '.join(context_info)}"
        
        return base_prompt
    
    async def _process_basic_analysis(self, request: VisionRequest, model_type: ModelType, model_info: Dict[str, Any]) -> VisionResponse:
        """
        Basic image analysis using available model
        """
        if model_type == ModelType.QWEN2_VL_7B:
            prompt = request.prompt or "Describe this image in detail."
            return await self._process_with_qwen2vl(request, model_info, prompt)
        elif model_type == ModelType.BLIP_BASE:
            return await self._process_with_blip(request, model_info)
        else:
            return VisionResponse(
                success=False,
                description="",
                analysis_type=request.analysis_type,
                model_used="unknown",
                confidence=0.0,
                processing_time=0,
                metadata={},
                error="Unsupported model type"
            )
    
    async def _process_with_qwen2vl(self, request: VisionRequest, model_info: Dict[str, Any], prompt: str) -> VisionResponse:
        """
        Process image using Qwen2-VL model
        """
        try:
            model = model_info['model']
            processor = model_info['processor']
            
            # Prepare the conversation format expected by Qwen2-VL
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": request.image},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Apply chat template
            text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            
            # Process inputs
            inputs = processor(
                text=[text],
                images=[request.image],
                padding=True,
                return_tensors="pt"
            )
            
            # Move to appropriate device
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=request.max_tokens,
                    temperature=request.temperature,
                    do_sample=request.temperature > 0,
                    pad_token_id=processor.tokenizer.eos_token_id
                )
            
            # Decode response
            generated_text = processor.batch_decode(outputs, skip_special_tokens=True)[0]
            
            # Extract the assistant's response
            response_start = generated_text.find("assistant\n")
            if response_start != -1:
                description = generated_text[response_start + len("assistant\n"):].strip()
            else:
                description = generated_text.strip()
            
            return VisionResponse(
                success=True,
                description=description,
                analysis_type=request.analysis_type,
                model_used=model_type.value,
                confidence=0.9,  # High confidence for Qwen2-VL
                processing_time=0,
                metadata={
                    "model_name": "Qwen2-VL-7B-Instruct",
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature
                }
            )
            
        except Exception as e:
            logger.error(f"Qwen2-VL processing failed: {e}")
            return VisionResponse(
                success=False,
                description="",
                analysis_type=request.analysis_type,
                model_used=model_type.value,
                confidence=0.0,
                processing_time=0,
                metadata={},
                error=str(e)
            )

    async def _process_with_blip(self, request: VisionRequest, model_info: Dict[str, Any]) -> VisionResponse:
        """
        Process image using BLIP model
        """
        try:
            model = model_info['model']
            processor = model_info['processor']

            # Process image
            inputs = processor(request.image, return_tensors="pt")

            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}

            # Generate caption
            with torch.no_grad():
                outputs = model.generate(**inputs, max_length=100, num_beams=5)

            description = processor.decode(outputs[0], skip_special_tokens=True)

            return VisionResponse(
                success=True,
                description=description,
                analysis_type=request.analysis_type,
                model_used=ModelType.BLIP_BASE.value,
                confidence=0.7,  # Moderate confidence for BLIP
                processing_time=0,
                metadata={
                    "model_name": "BLIP-Image-Captioning-Base",
                    "max_length": 100
                }
            )

        except Exception as e:
            logger.error(f"BLIP processing failed: {e}")
            return VisionResponse(
                success=False,
                description="",
                analysis_type=request.analysis_type,
                model_used=ModelType.BLIP_BASE.value,
                confidence=0.0,
                processing_time=0,
                metadata={},
                error=str(e)
# Global vision processor instance
vision_processor = EnhancedVisionProcessor()
