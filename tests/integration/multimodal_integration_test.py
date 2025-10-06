#!/usr/bin/env python3
"""
Comprehensive Multimodal AI Integration Tests
Tests the complete gRPC-based architecture with Kotlin backend orchestration
"""

import asyncio
import pytest
import requests
import grpc
import time
import json
import os
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Test configuration
@dataclass
class TestConfig:
    kotlin_backend_url: str = "http://localhost:8080"
    vision_grpc_host: str = "localhost"
    vision_grpc_port: int = 50051
    context_grpc_host: str = "localhost"
    context_grpc_port: int = 50052
    test_timeout: int = 60
    service_startup_timeout: int = 120

@dataclass
class TestAsset:
    name: str
    path: str
    type: str
    expected_elements: List[str]
    expected_confidence_min: float

@dataclass
class TestResult:
    test_name: str
    success: bool
    response_time: float
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None

class MultimodalIntegrationTest:
    """
    Comprehensive integration test suite for multimodal AI architecture
    """
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.test_assets: List[TestAsset] = []
        self.test_results: List[TestResult] = []
        self.services_started = False
        
    async def setup_test_environment(self):
        """
        Set up the complete test environment with services and test data
        """
        print("🚀 Setting up multimodal integration test environment...")
        
        # Create test assets
        await self.create_test_assets()
        
        # Start services
        await self.start_services()
        
        # Wait for services to be ready
        await self.wait_for_services()
        
        print("✅ Test environment ready!")
    
    async def create_test_assets(self):
        """
        Create synthetic test assets for comprehensive testing
        """
        print("📁 Creating test assets...")
        
        # Create test directory
        test_dir = Path("tests/assets")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Create synthetic screenshot
        screenshot_path = test_dir / "test_screenshot.png"
        self.create_synthetic_screenshot(screenshot_path)
        self.test_assets.append(TestAsset(
            name="UI Screenshot",
            path=str(screenshot_path),
            type="screenshot",
            expected_elements=["button", "input", "text"],
            expected_confidence_min=0.7
        ))
        
        # Create synthetic document
        document_path = test_dir / "test_document.png"
        self.create_synthetic_document(document_path)
        self.test_assets.append(TestAsset(
            name="Document",
            path=str(document_path),
            type="document",
            expected_elements=["text", "heading"],
            expected_confidence_min=0.8
        ))
        
        # Create synthetic UI component
        ui_component_path = test_dir / "test_ui_component.png"
        self.create_synthetic_ui_component(ui_component_path)
        self.test_assets.append(TestAsset(
            name="UI Component",
            path=str(ui_component_path),
            type="ui_component",
            expected_elements=["form", "input"],
            expected_confidence_min=0.6
        ))
        
        # Create natural image
        natural_image_path = test_dir / "test_natural_image.png"
        self.create_synthetic_natural_image(natural_image_path)
        self.test_assets.append(TestAsset(
            name="Natural Image",
            path=str(natural_image_path),
            type="natural_image",
            expected_elements=["object", "scene"],
            expected_confidence_min=0.5
        ))
        
        print(f"✅ Created {len(self.test_assets)} test assets")
    
    def create_synthetic_screenshot(self, path: Path):
        """Create a synthetic screenshot with UI elements"""
        img = Image.new('RGB', (1200, 800), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw header
        draw.rectangle([0, 0, 1200, 80], fill='#2196F3')
        draw.text((20, 30), "Application Header", fill='white')
        
        # Draw navigation
        draw.rectangle([0, 80, 200, 800], fill='#f5f5f5')
        draw.text((20, 120), "Navigation", fill='black')
        draw.text((20, 160), "• Dashboard", fill='black')
        draw.text((20, 180), "• Settings", fill='black')
        draw.text((20, 200), "• Profile", fill='black')
        
        # Draw main content
        draw.rectangle([220, 100, 1180, 780], fill='white', outline='#ddd')
        draw.text((240, 120), "Main Content Area", fill='black')
        
        # Draw form elements
        draw.rectangle([240, 160, 600, 200], fill='white', outline='#ccc')
        draw.text((250, 175), "Input Field", fill='#666')
        
        draw.rectangle([240, 220, 350, 260], fill='#4CAF50')
        draw.text((270, 235), "Submit Button", fill='white')
        
        img.save(path)
    
    def create_synthetic_document(self, path: Path):
        """Create a synthetic document image"""
        img = Image.new('RGB', (800, 1000), color='white')
        draw = ImageDraw.Draw(img)
        
        # Title
        draw.text((50, 50), "Document Title", fill='black')
        draw.line([50, 80, 750, 80], fill='black', width=2)
        
        # Paragraphs
        paragraphs = [
            "This is a sample document for testing OCR and document analysis.",
            "It contains multiple paragraphs with different text formatting.",
            "The document includes headings, body text, and structured content.",
            "This helps test the document analysis capabilities of the system."
        ]
        
        y_pos = 120
        for para in paragraphs:
            draw.text((50, y_pos), para, fill='black')
            y_pos += 40
        
        # Subheading
        draw.text((50, y_pos + 20), "Section Heading", fill='black')
        draw.line([50, y_pos + 50, 300, y_pos + 50], fill='black')
        
        img.save(path)
    
    def create_synthetic_ui_component(self, path: Path):
        """Create a synthetic UI component"""
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # Form container
        draw.rectangle([20, 20, 380, 280], fill='white', outline='#ddd', width=2)
        draw.text((30, 30), "Login Form", fill='black')
        
        # Username field
        draw.text((30, 70), "Username:", fill='black')
        draw.rectangle([30, 90, 350, 120], fill='white', outline='#ccc')
        
        # Password field
        draw.text((30, 140), "Password:", fill='black')
        draw.rectangle([30, 160, 350, 190], fill='white', outline='#ccc')
        
        # Login button
        draw.rectangle([30, 220, 150, 250], fill='#2196F3')
        draw.text((70, 230), "Login", fill='white')
        
        img.save(path)
    
    def create_synthetic_natural_image(self, path: Path):
        """Create a synthetic natural image"""
        img = Image.new('RGB', (600, 400), color='skyblue')
        draw = ImageDraw.Draw(img)
        
        # Sky gradient (simplified)
        for y in range(200):
            color = (135, 206, 235 - y // 4)  # Sky blue gradient
            draw.line([(0, y), (600, y)], fill=color)
        
        # Ground
        draw.rectangle([0, 200, 600, 400], fill='green')
        
        # Sun
        draw.ellipse([450, 50, 550, 150], fill='yellow')
        
        # Tree (simplified)
        draw.rectangle([100, 120, 120, 200], fill='brown')  # Trunk
        draw.ellipse([70, 80, 150, 140], fill='darkgreen')  # Leaves
        
        # House (simplified)
        draw.rectangle([300, 150, 450, 250], fill='red')  # House
        draw.polygon([(275, 150), (375, 100), (475, 150)], fill='brown')  # Roof
        draw.rectangle([350, 180, 380, 220], fill='brown')  # Door
        
        img.save(path)
    
    async def start_services(self):
        """
        Start all required services for integration testing
        """
        print("🔧 Starting services...")
        
        # Note: In a real implementation, you would start the services here
        # For now, we assume they're already running or will be started externally
        
        # Start Kotlin backend (would be done via gradle or docker)
        # Start Python gRPC services (would be done via docker-compose)
        
        self.services_started = True
        print("✅ Services startup initiated")
    
    async def wait_for_services(self):
        """
        Wait for all services to be ready
        """
        print("⏳ Waiting for services to be ready...")
        
        start_time = time.time()
        timeout = self.config.service_startup_timeout
        
        while time.time() - start_time < timeout:
            try:
                # Check Kotlin backend
                kotlin_ready = await self.check_kotlin_backend_health()
                
                # Check gRPC services
                vision_ready = await self.check_vision_grpc_health()
                context_ready = await self.check_context_grpc_health()
                
                if kotlin_ready and vision_ready and context_ready:
                    print("✅ All services are ready!")
                    return
                
                print(f"⏳ Services status - Kotlin: {kotlin_ready}, Vision: {vision_ready}, Context: {context_ready}")
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"⏳ Waiting for services... ({e})")
                await asyncio.sleep(5)
        
        raise TimeoutError(f"Services did not become ready within {timeout} seconds")
    
    async def check_kotlin_backend_health(self) -> bool:
        """Check if Kotlin backend is healthy"""
        try:
            response = requests.get(
                f"{self.config.kotlin_backend_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    async def check_vision_grpc_health(self) -> bool:
        """Check if Vision gRPC service is healthy"""
        try:
            # This would use the actual gRPC health check
            # For now, simulate with a simple connection test
            channel = grpc.insecure_channel(
                f"{self.config.vision_grpc_host}:{self.config.vision_grpc_port}"
            )
            grpc.channel_ready_future(channel).result(timeout=5)
            channel.close()
            return True
        except:
            return False
    
    async def check_context_grpc_health(self) -> bool:
        """Check if Context gRPC service is healthy"""
        try:
            # This would use the actual gRPC health check
            # For now, simulate with a simple connection test
            channel = grpc.insecure_channel(
                f"{self.config.context_grpc_host}:{self.config.context_grpc_port}"
            )
            grpc.channel_ready_future(channel).result(timeout=5)
            channel.close()
            return True
        except:
            return False
