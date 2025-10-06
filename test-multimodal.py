#!/usr/bin/env python3
"""
Multimodal AI Pipeline Testing Suite
Comprehensive testing for the multimodal AI processing pipeline
"""

import os
import sys
import time
import requests
import json
from typing import Dict, Any, List, Optional
from PIL import Image
import io
import base64

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def log_info(message: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def log_success(message: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def log_warning(message: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def log_error(message: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def log_test(message: str):
    print(f"{Colors.PURPLE}[TEST]{Colors.NC} {message}")

class MultimodalTester:
    """
    Comprehensive testing suite for the multimodal AI pipeline
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 300  # 5 minutes for long-running analysis
        self.test_results = []
        
    def create_test_image(self, width: int = 800, height: int = 600, text: str = "Test Image") -> bytes:
        """Create a test image for testing"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Create image
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add some UI-like elements
        # Header bar
        draw.rectangle([0, 0, width, 60], fill='#2196F3')
        
        # Navigation buttons
        draw.rectangle([20, 15, 120, 45], fill='#1976D2')
        draw.rectangle([140, 15, 240, 45], fill='#1976D2')
        draw.rectangle([260, 15, 360, 45], fill='#1976D2')
        
        # Main content area
        draw.rectangle([20, 80, width-20, height-80], fill='#F5F5F5')
        
        # Form elements
        draw.rectangle([40, 120, width-40, 160], fill='white')
        draw.rectangle([40, 180, width-40, 220], fill='white')
        draw.rectangle([40, 240, 200, 280], fill='#4CAF50')
        
        # Add text
        try:
            # Try to use a default font
            font = ImageFont.load_default()
            draw.text((50, 130), "Username:", fill='black', font=font)
            draw.text((50, 190), "Password:", fill='black', font=font)
            draw.text((60, 250), "Login", fill='white', font=font)
            draw.text((width//2 - 50, 30), text, fill='white', font=font)
        except:
            # Fallback without font
            draw.text((50, 130), "Username:", fill='black')
            draw.text((50, 190), "Password:", fill='black')
            draw.text((60, 250), "Login", fill='white')
            draw.text((width//2 - 50, 30), text, fill='white')
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        return img_buffer.getvalue()
    
    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record results"""
        log_test(f"Running: {test_name}")
        start_time = time.time()
        
        try:
            result = test_func()
            duration = time.time() - start_time
            
            if result:
                log_success(f"✅ {test_name} - {duration:.2f}s")
                self.test_results.append({
                    'name': test_name,
                    'status': 'PASS',
                    'duration': duration,
                    'error': None
                })
                return True
            else:
                log_error(f"❌ {test_name} - {duration:.2f}s")
                self.test_results.append({
                    'name': test_name,
                    'status': 'FAIL',
                    'duration': duration,
                    'error': 'Test returned False'
                })
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            log_error(f"❌ {test_name} - {duration:.2f}s - {str(e)}")
            self.test_results.append({
                'name': test_name,
                'status': 'ERROR',
                'duration': duration,
                'error': str(e)
            })
            return False
    
    def test_health_checks(self) -> bool:
        """Test health endpoints of all services"""
        endpoints = [
            '/health',
            '/service-status'
        ]
        
        for endpoint in endpoints:
            response = self.session.get(f"{self.base_url}{endpoint}")
            if response.status_code != 200:
                log_error(f"Health check failed for {endpoint}: {response.status_code}")
                return False
            
            data = response.json()
            if endpoint == '/service-status':
                if data.get('overall_health') != 'healthy':
                    log_warning(f"Some services are unhealthy: {data}")
        
        return True
    
    def test_basic_analysis(self) -> bool:
        """Test basic image analysis workflow"""
        test_image = self.create_test_image(text="Basic Analysis Test")
        
        files = {'image': ('test.png', test_image, 'image/png')}
        data = {
            'workflow_type': 'basic_analysis',
            'analysis_type': 'screenshot'
        }
        
        response = self.session.post(f"{self.base_url}/analyze", files=files, data=data)
        
        if response.status_code != 200:
            log_error(f"Basic analysis failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        if not result.get('success', False):
            log_error(f"Basic analysis unsuccessful: {result}")
            return False
        
        # Check required fields
        required_fields = ['description', 'confidence', 'processing_time', 'workflow_used']
        for field in required_fields:
            if field not in result:
                log_error(f"Missing required field: {field}")
                return False
        
        log_info(f"Analysis result: {result['description'][:100]}...")
        return True
    
    def test_contextual_analysis(self) -> bool:
        """Test contextual analysis workflow"""
        test_image = self.create_test_image(text="Contextual Analysis Test")
        
        files = {'image': ('test.png', test_image, 'image/png')}
        data = {
            'workflow_type': 'contextual_analysis',
            'analysis_type': 'screenshot',
            'base_prompt': 'Analyze this UI screenshot focusing on the login form and navigation elements.'
        }
        
        response = self.session.post(f"{self.base_url}/analyze", files=files, data=data)
        
        if response.status_code != 200:
            log_error(f"Contextual analysis failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        if not result.get('success', False):
            log_error(f"Contextual analysis unsuccessful: {result}")
            return False
        
        # Check that contextual analysis provides more detailed results
        if len(result.get('description', '')) < 50:
            log_warning("Contextual analysis description seems too short")
        
        log_info(f"Contextual analysis result: {result['description'][:100]}...")
        return True
    
    def test_screenshot_analysis(self) -> bool:
        """Test specialized screenshot analysis endpoint"""
        test_image = self.create_test_image(text="Screenshot Analysis Test")
        
        files = {'image': ('screenshot.png', test_image, 'image/png')}
        data = {'workflow_type': 'contextual_analysis'}
        
        response = self.session.post(f"{self.base_url}/analyze-screenshot", files=files, data=data)
        
        if response.status_code != 200:
            log_error(f"Screenshot analysis failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        if not result.get('success', False):
            log_error(f"Screenshot analysis unsuccessful: {result}")
            return False
        
        log_info(f"Screenshot analysis result: {result['analysis'][:100]}...")
        return True
    
    def test_direct_vision_analysis(self) -> bool:
        """Test direct vision service access"""
        test_image = self.create_test_image(text="Direct Vision Test")
        
        files = {'image': ('test.png', test_image, 'image/png')}
        data = {
            'analysis_type': 'screenshot',
            'prompt': 'Describe this user interface.'
        }
        
        response = self.session.post(f"{self.base_url}/vision/analyze", files=files, data=data)
        
        if response.status_code != 200:
            log_error(f"Direct vision analysis failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        if not result.get('success', False):
            log_error(f"Direct vision analysis unsuccessful: {result}")
            return False
        
        log_info(f"Direct vision result: {result['description'][:100]}...")
        return True
    
    def test_context_prompt_generation(self) -> bool:
        """Test contextual prompt generation"""
        data = {
            'base_prompt': 'Analyze this image',
            'analysis_type': 'screenshot',
            'context_types': ['documentation', 'ui_components'],
            'max_context_items': 3
        }
        
        response = self.session.post(f"{self.base_url}/context/generate-prompt", json=data)
        
        if response.status_code != 200:
            log_error(f"Prompt generation failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        if not result.get('success', False):
            log_error(f"Prompt generation unsuccessful: {result}")
            return False
        
        enhanced_prompt = result.get('enhanced_prompt', '')
        if len(enhanced_prompt) <= len(data['base_prompt']):
            log_warning("Enhanced prompt doesn't seem to be enhanced")
        
        log_info(f"Enhanced prompt: {enhanced_prompt[:100]}...")
        return True
    
    def test_context_search(self) -> bool:
        """Test context search functionality"""
        data = {
            'query': 'user interface components',
            'context_types': ['documentation', 'ui_components'],
            'max_results': 5
        }
        
        response = self.session.post(f"{self.base_url}/context/search", json=data)
        
        if response.status_code != 200:
            log_error(f"Context search failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        if not result.get('success', False):
            log_error(f"Context search unsuccessful: {result}")
            return False
        
        results = result.get('results', [])
        log_info(f"Found {len(results)} context results")
        return True
    
    def test_workflow_listing(self) -> bool:
        """Test workflow listing endpoint"""
        response = self.session.get(f"{self.base_url}/workflows")
        
        if response.status_code != 200:
            log_error(f"Workflow listing failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        workflows = result.get('workflows', [])
        
        if len(workflows) < 3:
            log_error(f"Expected at least 3 workflows, got {len(workflows)}")
            return False
        
        log_info(f"Available workflows: {[w['type'] for w in workflows]}")
        return True
    
    def test_api_documentation(self) -> bool:
        """Test API documentation endpoint"""
        response = self.session.get(f"{self.base_url}/api-docs")
        
        if response.status_code != 200:
            log_error(f"API docs failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        if 'endpoints' not in result:
            log_error("API docs missing endpoints")
            return False
        
        log_info(f"API documentation available with {len(result['endpoints'])} endpoints")
        return True
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        log_info("🧪 Starting Multimodal AI Pipeline Test Suite")
        log_info(f"Testing against: {self.base_url}")
        
        tests = [
            ("Health Checks", self.test_health_checks),
            ("Basic Analysis", self.test_basic_analysis),
            ("Contextual Analysis", self.test_contextual_analysis),
            ("Screenshot Analysis", self.test_screenshot_analysis),
            ("Direct Vision Analysis", self.test_direct_vision_analysis),
            ("Context Prompt Generation", self.test_context_prompt_generation),
            ("Context Search", self.test_context_search),
            ("Workflow Listing", self.test_workflow_listing),
            ("API Documentation", self.test_api_documentation)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
            else:
                failed += 1
            print()  # Add spacing between tests
        
        # Summary
        total = passed + failed
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print("=" * 60)
        log_info(f"Test Summary:")
        log_success(f"✅ Passed: {passed}")
        if failed > 0:
            log_error(f"❌ Failed: {failed}")
        else:
            log_success(f"❌ Failed: {failed}")
        log_info(f"📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            log_success("🎉 Multimodal AI Pipeline is working well!")
        elif success_rate >= 60:
            log_warning("⚠️  Multimodal AI Pipeline has some issues")
        else:
            log_error("🚨 Multimodal AI Pipeline has significant problems")
        
        return {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'success_rate': success_rate,
            'results': self.test_results
        }

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test the Multimodal AI Pipeline')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='Base URL of the API Gateway (default: http://localhost:8000)')
    parser.add_argument('--test', choices=['health', 'basic', 'contextual', 'screenshot', 'vision', 'context', 'all'],
                       default='all', help='Specific test to run (default: all)')
    
    args = parser.parse_args()
    
    tester = MultimodalTester(args.url)
    
    if args.test == 'all':
        summary = tester.run_all_tests()
        sys.exit(0 if summary['success_rate'] >= 80 else 1)
    else:
        # Run specific test
        test_map = {
            'health': tester.test_health_checks,
            'basic': tester.test_basic_analysis,
            'contextual': tester.test_contextual_analysis,
            'screenshot': tester.test_screenshot_analysis,
            'vision': tester.test_direct_vision_analysis,
            'context': tester.test_context_prompt_generation
        }
        
        if args.test in test_map:
            success = tester.run_test(args.test.title(), test_map[args.test])
            sys.exit(0 if success else 1)
        else:
            log_error(f"Unknown test: {args.test}")
            sys.exit(1)

if __name__ == '__main__':
    main()
