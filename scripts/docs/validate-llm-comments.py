#!/usr/bin/env python3
"""
LLM Comment Validation System

Validates consistency and quality of @llm-* comments across the codebase.
Integrates with the existing documentation validation workflow.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ValidationIssue:
    """Represents a validation issue found in LLM comments"""
    file_path: str
    line_number: int
    element_name: str
    issue_type: str
    message: str
    severity: str  # 'error', 'warning', 'info'

class LLMCommentValidator:
    """Validates LLM comments for consistency and completeness"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.issues = []
        
        # Required tags for different element types
        self.required_tags = {
            'service': ['llm_type', 'llm_legend', 'llm_key', 'llm_map'],
            'function': ['llm_type', 'llm_legend'],
            'class': ['llm_type', 'llm_legend', 'llm_key'],
            'repository': ['llm_type', 'llm_legend', 'llm_key', 'llm_map'],
            'endpoint': ['llm_type', 'llm_legend', 'llm_contract'],
            'config': ['llm_type', 'llm_legend', 'llm_key']
        }
        
        # Valid values for llm_type
        self.valid_types = {
            'function', 'class', 'service', 'config', 'type-definition',
            'constant', 'interface', 'endpoint', 'repository', 'entity'
        }
        
        # Quality thresholds
        self.min_legend_length = 20
        self.min_key_length = 15
        self.min_map_length = 15
    
    def validate_all_comments(self) -> List[ValidationIssue]:
        """Validate all LLM comments in the codebase"""
        self.issues = []
        
        # Import the extractor to get comments
        try:
            import sys
            import importlib.util

            # Load the extractor module dynamically
            extractor_path = self.root_path / "scripts" / "docs" / "extract-llm-comments.py"
            spec = importlib.util.spec_from_file_location("extract_llm_comments", extractor_path)
            extractor_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(extractor_module)

            extractor = extractor_module.LLMCommentExtractor(str(self.root_path))
            comments = extractor.extract_all_comments()
            
            print(f"🔍 Validating {len(comments)} LLM comments...")
            
            for comment in comments:
                self._validate_comment(comment)
            
            # Additional validations
            self._validate_consistency(comments)
            self._validate_coverage(comments)
            
        except ImportError as e:
            self.issues.append(ValidationIssue(
                file_path="scripts/docs/extract-llm-comments.py",
                line_number=1,
                element_name="import",
                issue_type="dependency",
                message=f"Cannot import LLM comment extractor: {e}",
                severity="error"
            ))
        
        return self.issues
    
    def _validate_comment(self, comment):
        """Validate a single LLM comment"""
        # Check required tags based on type
        if comment.llm_type:
            required = self.required_tags.get(comment.llm_type, ['llm_type', 'llm_legend'])
            
            for tag in required:
                if not getattr(comment, tag, None):
                    self.issues.append(ValidationIssue(
                        file_path=comment.file_path,
                        line_number=comment.line_number,
                        element_name=comment.element_name,
                        issue_type="missing_tag",
                        message=f"Missing required @{tag.replace('_', '-')} tag for {comment.llm_type}",
                        severity="error"
                    ))
        
        # Validate llm_type value
        if comment.llm_type and comment.llm_type not in self.valid_types:
            self.issues.append(ValidationIssue(
                file_path=comment.file_path,
                line_number=comment.line_number,
                element_name=comment.element_name,
                issue_type="invalid_type",
                message=f"Invalid @llm-type '{comment.llm_type}'. Valid types: {', '.join(sorted(self.valid_types))}",
                severity="error"
            ))
        
        # Check content quality
        if comment.llm_legend and len(comment.llm_legend) < self.min_legend_length:
            self.issues.append(ValidationIssue(
                file_path=comment.file_path,
                line_number=comment.line_number,
                element_name=comment.element_name,
                issue_type="short_legend",
                message=f"@llm-legend too short ({len(comment.llm_legend)} chars). Minimum: {self.min_legend_length}",
                severity="warning"
            ))
        
        if comment.llm_key and len(comment.llm_key) < self.min_key_length:
            self.issues.append(ValidationIssue(
                file_path=comment.file_path,
                line_number=comment.line_number,
                element_name=comment.element_name,
                issue_type="short_key",
                message=f"@llm-key too short ({len(comment.llm_key)} chars). Minimum: {self.min_key_length}",
                severity="warning"
            ))
        
        # Check for placeholder text
        placeholders = ['TODO', 'FIXME', '[Business purpose]', '[Technical implementation]']
        for field_name in ['llm_legend', 'llm_key', 'llm_map', 'llm_axiom', 'llm_contract']:
            field_value = getattr(comment, field_name, None)
            if field_value:
                for placeholder in placeholders:
                    if placeholder in field_value:
                        self.issues.append(ValidationIssue(
                            file_path=comment.file_path,
                            line_number=comment.line_number,
                            element_name=comment.element_name,
                            issue_type="placeholder_text",
                            message=f"Placeholder text '{placeholder}' found in @{field_name.replace('_', '-')}",
                            severity="warning"
                        ))
    
    def _validate_consistency(self, comments):
        """Validate consistency across comments"""
        # Check for duplicate tokens
        tokens = defaultdict(list)
        for comment in comments:
            if comment.llm_token:
                # Extract token name (before colon)
                token_parts = comment.llm_token.split(':')
                if len(token_parts) >= 2:
                    token_name = token_parts[0].strip()
                    tokens[token_name].append(comment)
        
        for token_name, token_comments in tokens.items():
            if len(token_comments) > 1:
                # Check if definitions are consistent
                definitions = set()
                for comment in token_comments:
                    token_parts = comment.llm_token.split(':', 1)
                    if len(token_parts) >= 2:
                        definitions.add(token_parts[1].strip())
                
                if len(definitions) > 1:
                    for comment in token_comments:
                        self.issues.append(ValidationIssue(
                            file_path=comment.file_path,
                            line_number=comment.line_number,
                            element_name=comment.element_name,
                            issue_type="inconsistent_token",
                            message=f"Token '{token_name}' has inconsistent definitions across files",
                            severity="warning"
                        ))
    
    def _validate_coverage(self, comments):
        """Validate coverage of LLM comments across the codebase"""
        # This is a simplified coverage check
        # In a real implementation, you'd analyze all code files
        
        coverage_by_language = defaultdict(int)
        for comment in comments:
            coverage_by_language[comment.language] += 1
        
        # Check if we have reasonable coverage
        if len(comments) < 5:
            self.issues.append(ValidationIssue(
                file_path="",
                line_number=0,
                element_name="coverage",
                issue_type="low_coverage",
                message=f"Only {len(comments)} LLM comments found. Consider adding more for better AI comprehension",
                severity="info"
            ))
    
    def generate_validation_report(self) -> str:
        """Generate a human-readable validation report"""
        if not self.issues:
            return "✅ All LLM comments are valid and consistent!"
        
        report = []
        report.append("# 🔍 LLM Comment Validation Report")
        report.append("")
        
        # Group issues by severity
        by_severity = defaultdict(list)
        for issue in self.issues:
            by_severity[issue.severity].append(issue)
        
        # Summary
        report.append("## 📊 Summary")
        report.append("")
        report.append(f"**Total Issues**: {len(self.issues)}")
        for severity in ['error', 'warning', 'info']:
            count = len(by_severity[severity])
            if count > 0:
                emoji = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[severity]
                report.append(f"**{severity.title()}s**: {emoji} {count}")
        report.append("")
        
        # Detailed issues
        for severity in ['error', 'warning', 'info']:
            issues = by_severity[severity]
            if not issues:
                continue
            
            emoji = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[severity]
            report.append(f"## {emoji} {severity.title()}s")
            report.append("")
            
            for issue in issues:
                report.append(f"### {issue.file_path}:{issue.line_number}")
                report.append(f"**Element**: {issue.element_name}")
                report.append(f"**Issue**: {issue.message}")
                report.append(f"**Type**: {issue.issue_type}")
                report.append("")
        
        return '\n'.join(report)
    
    def get_exit_code(self) -> int:
        """Get appropriate exit code based on validation results"""
        if any(issue.severity == 'error' for issue in self.issues):
            return 1
        return 0

def main():
    """Main validation function"""
    validator = LLMCommentValidator()
    issues = validator.validate_all_comments()
    
    # Generate report
    report = validator.generate_validation_report()
    print(report)
    
    # Save detailed report
    report_path = "docs/architecture/llm-comment-validation.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Detailed report saved to {report_path}")
    
    # Return appropriate exit code
    return validator.get_exit_code()

if __name__ == "__main__":
    exit(main())
