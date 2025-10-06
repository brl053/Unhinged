#!/usr/bin/env python3
"""
Enhanced Model Manager for Multimodal Vision Processing
Supports multiple vision models with intelligent routing and fallback
"""

import os
import logging
import torch
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass
import time
from PIL import Image

# Model imports
from transformers import (
    Qwen2VLForConditionalGeneration, 
    AutoTokenizer, 
    AutoProcessor,
    BlipProcessor, 
    BlipForConditionalGeneration
)

logger = logging.getLogger(__name__)

class ModelType(Enum):
    QWEN2_VL_7B = "qwen2-vl-7b"
    BLIP_BASE = "blip-base"
    GPT4V_API = "gpt4v-api"
    CLAUDE_API = "claude-api"
    GEMINI_API = "gemini-api"

@dataclass
class ModelConfig:
    name: str
    model_type: ModelType
    model_path: str
    max_tokens: int
    vram_requirement: int  # GB
    supports_ocr: bool
    supports_ui: bool
    priority: int  # Lower = higher priority

@dataclass
class ModelLoadResult:
    success: bool
    model: Any = None
    processor: Any = None
    tokenizer: Any = None
    error: Optional[str] = None
    load_time: float = 0.0

class EnhancedModelManager:
    """
    Manages multiple vision models with intelligent routing and fallback
    """
    
    def __init__(self):
        self.models: Dict[ModelType, Dict[str, Any]] = {}
        self.model_configs = self._get_model_configs()
        self.device = self._get_optimal_device()
        self.current_primary = None
        self.load_stats = {}
        
    def _get_model_configs(self) -> Dict[ModelType, ModelConfig]:
        """Define available model configurations"""
        return {
            ModelType.QWEN2_VL_7B: ModelConfig(
                name="Qwen2-VL-7B-Instruct",
                model_type=ModelType.QWEN2_VL_7B,
                model_path="Qwen/Qwen2-VL-7B-Instruct",
                max_tokens=2048,
                vram_requirement=14,
                supports_ocr=True,
                supports_ui=True,
                priority=1
            ),
            ModelType.BLIP_BASE: ModelConfig(
                name="BLIP-Image-Captioning-Base",
                model_type=ModelType.BLIP_BASE,
                model_path="Salesforce/blip-image-captioning-base",
                max_tokens=100,
                vram_requirement=4,
                supports_ocr=False,
                supports_ui=False,
                priority=3
            )
        }
    
    def _get_optimal_device(self) -> str:
        """Determine the best device for model inference"""
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"CUDA available with {gpu_memory:.1f}GB GPU memory")
            return "cuda"
        else:
            logger.warning("CUDA not available, using CPU")
            return "cpu"
    
    def load_model(self, model_type: ModelType, quantize: bool = False) -> ModelLoadResult:
        """Load a specific model with error handling and performance tracking"""
        start_time = time.time()
        config = self.model_configs.get(model_type)
        
        if not config:
            return ModelLoadResult(
                success=False,
                error=f"Unknown model type: {model_type}"
            )
        
        try:
            logger.info(f"Loading {config.name}...")
            
            if model_type == ModelType.QWEN2_VL_7B:
                result = self._load_qwen2_vl(config, quantize)
            elif model_type == ModelType.BLIP_BASE:
                result = self._load_blip(config)
            else:
                return ModelLoadResult(
                    success=False,
                    error=f"Model type {model_type} not implemented"
                )
            
            if result.success:
                self.models[model_type] = {
                    'model': result.model,
                    'processor': result.processor,
                    'tokenizer': result.tokenizer,
                    'config': config,
                    'loaded_at': time.time()
                }
                
                load_time = time.time() - start_time
                self.load_stats[model_type] = {
                    'load_time': load_time,
                    'quantized': quantize,
                    'device': self.device
                }
                
                logger.info(f"✅ {config.name} loaded successfully in {load_time:.2f}s")
                
                # Set as primary if it's the highest priority loaded model
                if not self.current_primary or config.priority < self.model_configs[self.current_primary].priority:
                    self.current_primary = model_type
                    logger.info(f"Set {config.name} as primary model")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to load {config.name}: {e}")
            return ModelLoadResult(
                success=False,
                error=str(e),
                load_time=time.time() - start_time
            )
    
    def _load_qwen2_vl(self, config: ModelConfig, quantize: bool) -> ModelLoadResult:
        """Load Qwen2-VL model with optional quantization"""
        try:
            # Load tokenizer and processor
            tokenizer = AutoTokenizer.from_pretrained(
                config.model_path,
                trust_remote_code=True
            )
            processor = AutoProcessor.from_pretrained(
                config.model_path,
                trust_remote_code=True
            )
            
            # Load model with appropriate settings
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.bfloat16 if self.device == "cuda" else torch.float32,
            }
            
            if quantize and self.device == "cuda":
                from transformers import BitsAndBytesConfig
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.bfloat16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                model_kwargs["quantization_config"] = quantization_config
                model_kwargs["device_map"] = "auto"
            else:
                model_kwargs["device_map"] = "auto" if self.device == "cuda" else None
            
            model = Qwen2VLForConditionalGeneration.from_pretrained(
                config.model_path,
                **model_kwargs
            )
            
            if not quantize and self.device == "cuda":
                model = model.cuda()
            
            return ModelLoadResult(
                success=True,
                model=model,
                processor=processor,
                tokenizer=tokenizer
            )
            
        except Exception as e:
            return ModelLoadResult(success=False, error=str(e))
    
    def _load_blip(self, config: ModelConfig) -> ModelLoadResult:
        """Load BLIP model"""
        try:
            processor = BlipProcessor.from_pretrained(config.model_path)
            model = BlipForConditionalGeneration.from_pretrained(config.model_path)
            
            if self.device == "cuda":
                model = model.cuda()
            
            return ModelLoadResult(
                success=True,
                model=model,
                processor=processor
            )
            
        except Exception as e:
            return ModelLoadResult(success=False, error=str(e))
    
    def get_model_info(self, model_type: ModelType) -> Dict[str, Any]:
        """Get information about a loaded model"""
        if model_type not in self.models:
            return {"loaded": False, "error": "Model not loaded"}
        
        config = self.models[model_type]['config']
        stats = self.load_stats.get(model_type, {})
        
        return {
            "loaded": True,
            "name": config.name,
            "supports_ocr": config.supports_ocr,
            "supports_ui": config.supports_ui,
            "max_tokens": config.max_tokens,
            "priority": config.priority,
            "device": self.device,
            "load_time": stats.get('load_time', 0),
            "quantized": stats.get('quantized', False),
            "loaded_at": self.models[model_type]['loaded_at']
        }
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of all available models and their status"""
        models = []
        for model_type, config in self.model_configs.items():
            info = self.get_model_info(model_type)
            info.update({
                "model_type": model_type.value,
                "vram_requirement": config.vram_requirement
            })
            models.append(info)
        return models
    
    def get_primary_model(self) -> Optional[Tuple[ModelType, Dict[str, Any]]]:
        """Get the current primary model"""
        if self.current_primary and self.current_primary in self.models:
            return self.current_primary, self.models[self.current_primary]
        return None
    
    def unload_model(self, model_type: ModelType) -> bool:
        """Unload a specific model to free memory"""
        if model_type in self.models:
            del self.models[model_type]
            if model_type in self.load_stats:
                del self.load_stats[model_type]
            
            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info(f"Unloaded {model_type.value}")
            
            # Update primary model if needed
            if self.current_primary == model_type:
                self.current_primary = None
                # Find next best model
                for mt in sorted(self.models.keys(), key=lambda x: self.model_configs[x].priority):
                    self.current_primary = mt
                    break
            
            return True
        return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        gpu_info = {}
        if torch.cuda.is_available():
            gpu_info = {
                "gpu_available": True,
                "gpu_name": torch.cuda.get_device_name(0),
                "gpu_memory_total": torch.cuda.get_device_properties(0).total_memory / 1024**3,
                "gpu_memory_allocated": torch.cuda.memory_allocated(0) / 1024**3,
                "gpu_memory_cached": torch.cuda.memory_reserved(0) / 1024**3
            }
        else:
            gpu_info = {"gpu_available": False}
        
        return {
            "device": self.device,
            "models_loaded": len(self.models),
            "primary_model": self.current_primary.value if self.current_primary else None,
            "available_models": len(self.model_configs),
            **gpu_info
        }

# Global model manager instance
model_manager = EnhancedModelManager()

# Global model manager instance
model_manager = EnhancedModelManager()
