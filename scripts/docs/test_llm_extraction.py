#!/usr/bin/env python3
"""Test suite for LLM comment extraction and validation.

@llm-type test
@llm-legend TDD test suite ensuring extraction and validation correctness
@llm-context Defines expected behavior for all LLM comment processing functions
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from typing import List, Dict

# Import our type contracts
from llm_types import LLMComment, ExtractionResult, ValidationResult, ValidationIssue

class TestLLMExtraction(unittest.TestCase):
    """Test extraction of LLM comments from source files."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_files = []
    
    def tearDown(self):
        """Clean up test files."""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def create_temp_file(self, content: str, suffix: str) -> str:
        """Create temporary file with content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            f.write(content)
            temp_path = f.name
        self.temp_files.append(temp_path)
        return temp_path
    
    def test_extract_llm_context_from_python(self):
        """Test extraction of @llm-context from Python docstring."""
        content = '''#!/usr/bin/env python3
"""
@llm-type service
@llm-legend Processes user requests
@llm-context Handles HTTP requests with rate limiting and caching
"""
def process():
    pass
'''
        temp_path = self.create_temp_file(content, '.py')
        
        # Import from the module file
        import sys
        import importlib.util
        spec = importlib.util.spec_from_file_location("extract_llm_comments", "extract-llm-comments.py")
        extract_llm_comments = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(extract_llm_comments)
        extract_comments_from_file = extract_llm_comments.extract_comments_from_file
        comments: List[LLMComment] = extract_comments_from_file(temp_path)
        
        # Assertions
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].type, "service")
        self.assertEqual(comments[0].legend, "Processes user requests")
        self.assertEqual(comments[0].llm_context, "Handles HTTP requests with rate limiting and caching")
    
    def test_extract_llm_context_from_typescript(self):
        """Test extraction of @llm-context from TypeScript JSDoc."""
        content = '''
/**
 * @llm-type component
 * @llm-legend React component for user authentication
 * @llm-context Manages login state and JWT token refresh
 */
export const AuthComponent = () => {
    return null;
};
'''
        temp_path = self.create_temp_file(content, '.tsx')
        
        import extract_llm_comments
        from extract_llm_comments import extract_comments_from_file
        comments: List[LLMComment] = extract_comments_from_file(temp_path)
        
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].llm_context, "Manages login state and JWT token refresh")
    
    def test_parse_llm_tags_with_context(self):
        """Test parsing of all tags including @llm-context."""
        text = """
@llm-type validator
@llm-legend Validates user input
@llm-key Checks format and business rules
@llm-map Part of validation pipeline
@llm-axiom Never trust user input
@llm-contract Returns ValidationResult or throws
@llm-token user-validator
@llm-context Integrates with form handling and error display
"""
        import extract_llm_comments
        from extract_llm_comments import parse_llm_tags
        tags = parse_llm_tags(text)
        
        self.assertEqual(tags['llm_type'], 'validator')
        self.assertEqual(tags['llm_legend'], 'Validates user input')
        self.assertEqual(tags['llm_context'], 'Integrates with form handling and error display')
        self.assertIn('llm_axiom', tags)
        self.assertIn('llm_contract', tags)
    
    def test_save_extraction_results(self):
        """Test saving extraction results to JSON."""
        comments = [
            LLMComment(
                file_path="test.py",
                line_number=1,
                language="python",
                type="service",
                llm_context="Test context"
            )
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "extracted.json"
            import extract_llm_comments
            from extract_llm_comments import save_extraction_results
            result: ExtractionResult = save_extraction_results(comments, output_path)
            
            self.assertTrue(output_path.exists())
            self.assertEqual(result['files_with_comments'], 1)
            
            # Verify JSON structure
            with open(output_path) as f:
                data = json.load(f)
                self.assertIn('comments', data)
                self.assertEqual(data['comments'][0]['llm_context'], 'Test context')

class TestLLMValidation(unittest.TestCase):
    """Test validation of LLM comments."""
    
    def test_validate_comment_with_context(self):
        """Test validation accepts @llm-context."""
        comment = LLMComment(
            file_path="test.py",
            line_number=1,
            language="python",
            type="service",
            legend="Test service",
            llm_context="Provides core functionality"
        )
        
        import validate_llm_comments
        from validate_llm_comments import validate_comment
        issues = validate_comment(comment)
        self.assertEqual(len(issues), 0)  # No issues
    
    def test_check_required_tags(self):
        """Test required tags validation."""
        comment = LLMComment(
            file_path="test.py",
            line_number=1,
            language="python",
            type="service"
            # Missing legend - should fail
        )
        
        import validate_llm_comments
        from validate_llm_comments import check_required_tags
        issues = check_required_tags(comment)
        self.assertGreater(len(issues), 0)
        self.assertEqual(issues[0]['severity'], "error")
        self.assertIn("legend", issues[0]['message'])
    
    def test_validate_all_comments(self):
        """Test batch validation of comments."""
        comments = [
            LLMComment(
                file_path="good.py",
                line_number=1,
                language="python",
                type="service",
                legend="Good service",
                llm_context="Well documented"
            ),
            LLMComment(
                file_path="bad.py",
                line_number=1,
                language="python",
                type="component"
                # Missing legend
            )
        ]
        
        import validate_llm_comments
        from validate_llm_comments import validate_all_comments
        result: ValidationResult = validate_all_comments(comments)
        
        self.assertEqual(result['total_comments_validated'], 2)
        self.assertFalse(result['passed'])  # Should fail due to bad.py
        self.assertGreater(len(result['issues']), 0)

class TestLLMContextWarmerImprovements(unittest.TestCase):
    """
    @llm-type test
    @llm-legend Test suite for LLM context warmer improvements based on feedback
    @llm-context Validates element name detection, cross-references, and context completeness
    """

    def test_element_name_detection_from_service_path(self):
        """
        @llm-type test
        @llm-legend Test element name extraction from services directory paths
        @llm-context Addresses LLM feedback about unknown element names in service files
        """
        # Test data with unknown element name but clear service path
        comment = LLMComment(
            file_path="services/vision-ai/main.py",
            line_number=1,
            language="python",
            element_name="unknown",
            type="service",
            legend="Vision AI service for image analysis"
        )

        # This will be implemented in llm-context-warmer.py
        import sys
        import importlib.util
        spec = importlib.util.spec_from_file_location("llm_context_warmer", "llm-context-warmer.py")
        warmer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(warmer_module)

        # Create warmer without loading file
        warmer = warmer_module.LLMContextWarmer.__new__(warmer_module.LLMContextWarmer)
        warmer.comments = []  # Empty for testing
        improved_name = warmer._improve_element_name(comment.__dict__)

        # Should extract "vision-ai" from the service path
        self.assertEqual(improved_name, "vision-ai")

    def test_element_name_detection_from_python_file(self):
        """
        @llm-type test
        @llm-legend Test element name extraction from Python file names
        @llm-context Ensures Python modules get proper names instead of unknown
        """
        comment = LLMComment(
            file_path="scripts/docs/extract-llm-comments.py",
            line_number=1,
            language="python",
            element_name="unknown",
            type="tool",
            legend="LLM comment extraction tool"
        )

        import sys
        import importlib.util
        spec = importlib.util.spec_from_file_location("llm_context_warmer", "llm-context-warmer.py")
        warmer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(warmer_module)

        # Create warmer without loading file
        warmer = warmer_module.LLMContextWarmer.__new__(warmer_module.LLMContextWarmer)
        warmer.comments = []  # Empty for testing
        improved_name = warmer._improve_element_name(comment.__dict__)

        # Should extract "extract-llm-comments" from the file name
        self.assertEqual(improved_name, "extract-llm-comments")

    def test_find_related_services_by_port_references(self):
        """
        @llm-type test
        @llm-legend Test cross-reference detection between services using port numbers
        @llm-context Addresses LLM feedback about lack of cross-reference navigation
        """
        comments = [
            LLMComment(
                file_path="services/vision-ai/main.py",
                line_number=1,
                language="python",
                element_name="vision-ai",
                type="service",
                legend="Vision AI service",
                key="Serves on port 8001",
                map="Backend vision processing"
            ),
            LLMComment(
                file_path="frontend/src/services/VisionService.ts",
                line_number=1,
                language="typescript",
                element_name="VisionService",
                type="service",
                legend="Frontend vision client",
                key="Connects to vision-ai on port 8001",
                map="Frontend service layer"
            )
        ]

        import sys
        import importlib.util
        spec = importlib.util.spec_from_file_location("llm_context_warmer", "llm-context-warmer.py")
        warmer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(warmer_module)

        # Create warmer without loading file
        warmer = warmer_module.LLMContextWarmer.__new__(warmer_module.LLMContextWarmer)
        warmer.comments = [comment.__dict__ for comment in comments]

        related = warmer._find_related_services(comments[0].__dict__)

        # Should find VisionService as related due to port 8001 reference
        self.assertGreater(len(related), 0)
        self.assertIn("VisionService", str(related))

    def test_context_completeness_validation(self):
        """
        @llm-type test
        @llm-legend Test validation of context completeness for service components
        @llm-context Addresses LLM feedback about null llm_context fields where context should exist
        """
        comments = [
            LLMComment(
                file_path="services/audio-service/main.py",
                line_number=1,
                language="python",
                element_name="audio-service",
                type="service",
                legend="Audio processing service",
                llm_context=None  # Missing context - should be flagged
            ),
            LLMComment(
                file_path="scripts/utils/helper.py",
                line_number=1,
                language="python",
                element_name="helper",
                type="function",
                legend="Utility function",
                llm_context=None  # OK for utility functions
            )
        ]

        import sys
        import importlib.util
        spec = importlib.util.spec_from_file_location("llm_context_warmer", "llm-context-warmer.py")
        warmer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(warmer_module)

        # Create warmer without loading file
        warmer = warmer_module.LLMContextWarmer.__new__(warmer_module.LLMContextWarmer)
        warmer.comments = []  # Empty for testing
        missing_context = warmer._validate_context_completeness([comment.__dict__ for comment in comments])

        # Should flag the service with missing context but not the utility function
        self.assertEqual(len(missing_context), 1)
        self.assertEqual(missing_context[0]['element_name'], 'audio-service')

    def test_pagination_data_integrity(self):
        """
        @llm-type test
        @llm-legend Test that pagination maintains complete data integrity across pages
        @llm-context Ensures no data loss or corruption when browsing paginated comments
        """
        # Create test comments
        test_comments = []
        for i in range(25):  # More than 2 pages worth
            test_comments.append({
                'file_path': f'test/file_{i}.py',
                'line_number': 1,
                'element_name': f'element_{i}',
                'language': 'python',
                'llm_type': 'function',
                'llm_legend': f'Test function {i}'
            })

        import sys
        import importlib.util
        spec = importlib.util.spec_from_file_location("llm_context_warmer", "llm-context-warmer.py")
        warmer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(warmer_module)

        # Create warmer without loading file
        warmer = warmer_module.LLMContextWarmer.__new__(warmer_module.LLMContextWarmer)
        warmer.comments = test_comments
        warmer.page_size = 10

        # Get all pages
        page1 = warmer.paginate_comments(1)
        page2 = warmer.paginate_comments(2)
        page3 = warmer.paginate_comments(3)

        # Verify pagination metadata
        self.assertEqual(page1['pagination']['total_comments'], 25)
        self.assertEqual(page1['pagination']['total_pages'], 3)
        self.assertTrue(page1['pagination']['has_next'])
        self.assertFalse(page1['pagination']['has_previous'])

        self.assertTrue(page2['pagination']['has_next'])
        self.assertTrue(page2['pagination']['has_previous'])

        self.assertFalse(page3['pagination']['has_next'])
        self.assertTrue(page3['pagination']['has_previous'])

        # Verify no data overlap or gaps
        all_elements = []
        all_elements.extend([c['element_name'] for c in page1['comments']])
        all_elements.extend([c['element_name'] for c in page2['comments']])
        all_elements.extend([c['element_name'] for c in page3['comments']])

        # Should have all 25 elements with no duplicates
        self.assertEqual(len(all_elements), 25)
        self.assertEqual(len(set(all_elements)), 25)  # No duplicates

        # Verify correct page sizes
        self.assertEqual(len(page1['comments']), 10)
        self.assertEqual(len(page2['comments']), 10)
        self.assertEqual(len(page3['comments']), 5)  # Last page partial

if __name__ == '__main__':
    unittest.main()
