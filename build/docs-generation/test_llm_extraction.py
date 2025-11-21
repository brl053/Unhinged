#!/usr/bin/env python3
"""
@llm-type config.build
@llm-does tdd test suite ensuring extraction and validation
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List

# Import our type contracts
from llm_types import ExtractionResult, LLMComment, ValidationIssue, ValidationResult


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
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
            f.write(content)
            temp_path = f.name
        self.temp_files.append(temp_path)
        return temp_path

    def test_extract_llm_context_from_python(self):
        """Test extraction of @llm-context from Python docstring."""
        content = '''#!/usr/bin/env python3
"""
@llm-type service.api
@llm-does user requests
"""
def process():
    pass
'''
        temp_path = self.create_temp_file(content, ".py")

        # Import from the module file
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location("extract_llm_comments", "extract-llm-comments.py")
        extract_llm_comments = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(extract_llm_comments)
        extract_comments_from_file = extract_llm_comments.extract_comments_from_file
        comments: list[LLMComment] = extract_comments_from_file(temp_path)

        # Assertions
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].type, "service")
        self.assertEqual(comments[0].legend, "Processes user requests")
        self.assertEqual(comments[0].llm_context, "Handles HTTP requests with rate limiting and caching")

    def test_extract_llm_context_from_typescript(self):
        """Test extraction of @llm-context from TypeScript JSDoc."""
        content = '''
"""
@llm-type component.primitive
@llm-does react component for user authentication
"""
export const AuthComponent = () => {
    return null;
};
'''
        temp_path = self.create_temp_file(content, ".tsx")

        import extract_llm_comments
        from extract_llm_comments import extract_comments_from_file

        comments: list[LLMComment] = extract_comments_from_file(temp_path)

        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].llm_context, "Manages login state and JWT token refresh")

    def test_parse_llm_tags_with_context(self):
        """Test parsing of all tags including @llm-context."""
        text = """
@llm-type util.validator
@llm-does user input
@llm-rule never trust user input
"""
        import extract_llm_comments
        from extract_llm_comments import parse_llm_tags

        tags = parse_llm_tags(text)

        self.assertEqual(tags["llm_type"], "validator")
        self.assertEqual(tags["llm_legend"], "Validates user input")
        self.assertEqual(tags["llm_context"], "Integrates with form handling and error display")
        self.assertIn("llm_axiom", tags)
        self.assertIn("llm_contract", tags)

    def test_save_extraction_results(self):
        """Test saving extraction results to JSON."""
        comments = [
            LLMComment(
                file_path="test.py", line_number=1, language="python", type="service", llm_context="Test context"
            )
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "extracted.json"
            import extract_llm_comments
            from extract_llm_comments import save_extraction_results

            result: ExtractionResult = save_extraction_results(comments, output_path)

            self.assertTrue(output_path.exists())
            self.assertEqual(result["files_with_comments"], 1)

            # Verify JSON structure
            with open(output_path) as f:
                data = json.load(f)
                self.assertIn("comments", data)
                self.assertEqual(data["comments"][0]["llm_context"], "Test context")


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
            llm_context="Provides core functionality",
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
            type="service",
            # Missing legend - should fail
        )

        import validate_llm_comments
        from validate_llm_comments import check_required_tags

        issues = check_required_tags(comment)
        self.assertGreater(len(issues), 0)
        self.assertEqual(issues[0]["severity"], "error")
        self.assertIn("legend", issues[0]["message"])

    def test_validate_all_comments(self):
        """Test batch validation of comments."""
        comments = [
            LLMComment(
                file_path="good.py",
                line_number=1,
                language="python",
                type="service",
                legend="Good service",
                llm_context="Well documented",
            ),
            LLMComment(
                file_path="bad.py",
                line_number=1,
                language="python",
                type="component",
                # Missing legend
            ),
        ]

        import validate_llm_comments
        from validate_llm_comments import validate_all_comments

        result: ValidationResult = validate_all_comments(comments)

        self.assertEqual(result["total_comments_validated"], 2)
        self.assertFalse(result["passed"])  # Should fail due to bad.py
        self.assertGreater(len(result["issues"]), 0)


class TestLLMContextWarmerImprovements(unittest.TestCase):
    """
    @llm-type config.build
    @llm-does test suite for llm context warmer improvements
    """

    def test_element_name_detection_from_service_path(self):
        """
        @llm-type config.build
        @llm-does test element name extraction from services directory
        """
        # Test data with unknown element name but clear service path
        comment = LLMComment(
            file_path="services/vision-ai/main.py",
            line_number=1,
            language="python",
            element_name="unknown",
            type="service",
            legend="Vision AI service for image analysis",
        )

        # This will be implemented in llm-context-warmer.py
        import importlib.util
        import sys

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
        @llm-type config.build
        @llm-does test element name extraction from python file
        """
        comment = LLMComment(
            file_path="scripts/docs/extract-llm-comments.py",
            line_number=1,
            language="python",
            element_name="unknown",
            type="tool",
            legend="LLM comment extraction tool",
        )

        import importlib.util
        import sys

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
        @llm-type config.build
        @llm-does test cross-reference detection between services using port
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
                map="Backend vision processing",
            ),
            LLMComment(
                file_path="frontend/src/services/VisionService.ts",
                line_number=1,
                language="typescript",
                element_name="VisionService",
                type="service",
                legend="Frontend vision client",
                key="Connects to vision-ai on port 8001",
                map="Frontend service layer",
            ),
        ]

        import importlib.util
        import sys

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
        @llm-type config.build
        @llm-does test validation of context completeness for service
        """
        comments = [
            LLMComment(
                file_path="services/audio-service/main.py",
                line_number=1,
                language="python",
                element_name="audio-service",
                type="service",
                legend="Audio processing service",
                llm_context=None,  # Missing context - should be flagged
            ),
            LLMComment(
                file_path="scripts/utils/helper.py",
                line_number=1,
                language="python",
                element_name="helper",
                type="function",
                legend="Utility function",
                llm_context=None,  # OK for utility functions
            ),
        ]

        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location("llm_context_warmer", "llm-context-warmer.py")
        warmer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(warmer_module)

        # Create warmer without loading file
        warmer = warmer_module.LLMContextWarmer.__new__(warmer_module.LLMContextWarmer)
        warmer.comments = []  # Empty for testing
        missing_context = warmer._validate_context_completeness([comment.__dict__ for comment in comments])

        # Should flag the service with missing context but not the utility function
        self.assertEqual(len(missing_context), 1)
        self.assertEqual(missing_context[0]["element_name"], "audio-service")

    def test_pagination_data_integrity(self):
        """
        @llm-type config.build
        @llm-does test that pagination maintains complete data integrity
        """
        # Create test comments
        test_comments = []
        for i in range(25):  # More than 2 pages worth
            test_comments.append(
                {
                    "file_path": f"test/file_{i}.py",
                    "line_number": 1,
                    "element_name": f"element_{i}",
                    "language": "python",
                    "llm_type": "function",
                    "llm_legend": f"Test function {i}",
                }
            )

        import importlib.util
        import sys

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
        self.assertEqual(page1["pagination"]["total_comments"], 25)
        self.assertEqual(page1["pagination"]["total_pages"], 3)
        self.assertTrue(page1["pagination"]["has_next"])
        self.assertFalse(page1["pagination"]["has_previous"])

        self.assertTrue(page2["pagination"]["has_next"])
        self.assertTrue(page2["pagination"]["has_previous"])

        self.assertFalse(page3["pagination"]["has_next"])
        self.assertTrue(page3["pagination"]["has_previous"])

        # Verify no data overlap or gaps
        all_elements = []
        all_elements.extend([c["element_name"] for c in page1["comments"]])
        all_elements.extend([c["element_name"] for c in page2["comments"]])
        all_elements.extend([c["element_name"] for c in page3["comments"]])

        # Should have all 25 elements with no duplicates
        self.assertEqual(len(all_elements), 25)
        self.assertEqual(len(set(all_elements)), 25)  # No duplicates

        # Verify correct page sizes
        self.assertEqual(len(page1["comments"]), 10)
        self.assertEqual(len(page2["comments"]), 10)
        self.assertEqual(len(page3["comments"]), 5)  # Last page partial


class TestLLMContextWarmerEnhancements(unittest.TestCase):
    """
    @llm-type config.build
    @llm-does test suite for final llm context warmer
    """

    def test_getting_started_section_generation(self):
        """
        @llm-type config.build
        @llm-does test generation of getting started section with
        """
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location("llm_context_warmer", "llm-context-warmer.py")
        warmer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(warmer_module)

        # Create warmer with mock data
        warmer = warmer_module.LLMContextWarmer.__new__(warmer_module.LLMContextWarmer)
        warmer.comments = [
            {
                "file_path": "Makefile",
                "llm_type": "config",
                "llm_legend": "Build system configuration",
                "llm_key": "Defines setup, dev, and deployment targets",
                "llm_map": "Entry point for all development workflows",
            },
            {
                "file_path": "docker-compose.yml",
                "llm_type": "config",
                "llm_legend": "Container orchestration configuration",
                "llm_key": "Defines all microservices and their dependencies",
                "llm_map": "Infrastructure layer for local development",
            },
        ]

        getting_started = warmer._generate_getting_started_section()

        # Should include setup commands and dependency information
        self.assertIsInstance(getting_started, dict)
        self.assertIn("quick_start_commands", getting_started)
        self.assertIn("prerequisites", getting_started)

        # Check content includes expected terms
        content_str = str(getting_started).lower()
        self.assertIn("setup", content_str)
        self.assertIn("make", content_str)
        self.assertIn("docker", content_str)

    def test_dependency_information_extraction(self):
        """
        @llm-type config.build
        @llm-does test extraction of dependency and setup information
        """
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location("llm_context_warmer", "llm-context-warmer.py")
        warmer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(warmer_module)

        # Create warmer with mock build system data
        warmer = warmer_module.LLMContextWarmer.__new__(warmer_module.LLMContextWarmer)
        warmer.comments = [
            {
                "file_path": "package.json",
                "llm_type": "config",
                "llm_legend": "Node.js dependencies and scripts",
                "llm_key": "Defines frontend build pipeline and dependencies",
            },
            {
                "file_path": "backend/build.gradle.kts",
                "llm_type": "config",
                "llm_legend": "Kotlin backend build configuration",
                "llm_key": "Defines JVM dependencies and build tasks",
            },
        ]

        dependencies = warmer._extract_dependency_information()

        # Should identify different dependency systems
        self.assertIsInstance(dependencies, dict)
        self.assertIn("frontend", dependencies)
        self.assertIn("backend", dependencies)
        self.assertGreater(len(dependencies), 0)

    def test_complete_legend_validation(self):
        """
        @llm-type config.build
        @llm-does test validation that legends are complete and
        """
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location("llm_context_warmer", "llm-context-warmer.py")
        warmer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(warmer_module)

        # Create warmer with test data including truncated legends
        warmer = warmer_module.LLMContextWarmer.__new__(warmer_module.LLMContextWarmer)

        comments = [
            {
                "file_path": "test1.py",
                "llm_type": "service",
                "llm_legend": "Complete service description with full details",
                "element_name": "complete_service",
            },
            {
                "file_path": "test2.py",
                "llm_type": "service",
                "llm_legend": "Truncated",  # Too short
                "element_name": "truncated_service",
            },
            {
                "file_path": "test3.py",
                "llm_type": "service",
                "llm_legend": "Extracts all",  # Appears truncated
                "element_name": "partial_service",
            },
        ]

        truncated_legends = warmer._validate_legend_completeness(comments)

        # Should identify truncated or incomplete legends
        self.assertGreater(len(truncated_legends), 0)
        self.assertTrue(any("truncated" in item["element_name"] for item in truncated_legends))
        self.assertTrue(any("partial" in item["element_name"] for item in truncated_legends))

    def test_enhanced_overview_with_getting_started(self):
        """
        @llm-type config.build
        @llm-does test that enhanced overview includes getting started
        """
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location("llm_context_warmer", "llm-context-warmer.py")
        warmer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(warmer_module)

        # Create warmer with comprehensive test data
        warmer = warmer_module.LLMContextWarmer.__new__(warmer_module.LLMContextWarmer)
        warmer.comments = [
            {
                "file_path": "Makefile",
                "llm_type": "config",
                "llm_legend": "Build system with setup and development targets",
                "llm_key": "Provides make setup, make dev, make test commands",
            }
        ]

        overview = warmer.generate_enhanced_project_overview()

        # Should include all sections addressing LLM feedback
        self.assertIn("getting_started", overview)
        self.assertIn("dependencies", overview)
        self.assertIn("quick_start_commands", overview["getting_started"])
        self.assertIn("prerequisites", overview["getting_started"])
        self.assertIn("frontend", overview["dependencies"])
        self.assertIn("backend", overview["dependencies"])


if __name__ == "__main__":
    unittest.main()
