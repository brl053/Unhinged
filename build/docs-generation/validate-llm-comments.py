#!/usr/bin/env python3
"""
@llm-type util.validator
@llm-does llmdocs validation and quality assurance for evolved format compliance
@llm-rule validation must enforce evolved format standards and provide actionable feedback
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
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
        
        # Required tags for different element types - Evolved 3-tag format
        self.required_tags = {
            'service': ['llm_type', 'llm_does'],
            'function': ['llm_type', 'llm_does'],
            'class': ['llm_type', 'llm_does'],
            'repository': ['llm_type', 'llm_does'],
            'endpoint': ['llm_type', 'llm_does'],
            'config': ['llm_type', 'llm_does']
        }
        
        # Valid values for llm_type - Evolved hierarchical format
        self.valid_types = {
            # Flat types (legacy compatibility)
            'function', 'class', 'service', 'config', 'type-definition',
            'constant', 'interface', 'endpoint', 'repository', 'entity',
            'component', 'validator', 'contract', 'test', 'tool',
            # Hierarchical types (evolved format)
            'service.api', 'service.worker', 'service.launcher', 'service.shared', 'service.util',
            'component.primitive', 'component.container', 'component.complex', 'component.spec',
            'util.function', 'util.parser', 'util.validator', 'util.formatter', 'util.converter',
            'util.migrator', 'util.runner', 'util.cli', 'util.tool', 'util.executor', 'util.setup',
            'model.entity', 'model.dto', 'model.config', 'model.schema',
            'config.build', 'config.deploy', 'config.env', 'config.app',
            'misc.virtualization-boundary', 'misc.control-system', 'misc.control-tool',
            'misc.control-orchestrator', 'misc.control-monitor', 'misc.control-plane-package',
            'misc.control-plane', 'misc.platform'
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
            extractor_path = Path("build/docs-generation/extract-llm-comments.py")
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
        # Check required tags based on type - Evolved format
        if comment.llm_type:
            required = self.required_tags.get(comment.llm_type, ['llm_type', 'llm_does'])

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
        
        # Check content quality - Evolved format
        if comment.llm_does and len(comment.llm_does) < 10:
            self.issues.append(ValidationIssue(
                file_path=comment.file_path,
                line_number=comment.line_number,
                element_name=comment.element_name,
                issue_type="short_does",
                message=f"@llm-does too short ({len(comment.llm_does)} chars). Minimum: 10",
                severity="warning"
            ))

        if comment.llm_rule and len(comment.llm_rule) < 15:
            self.issues.append(ValidationIssue(
                file_path=comment.file_path,
                line_number=comment.line_number,
                element_name=comment.element_name,
                issue_type="short_rule",
                message=f"@llm-rule too short ({len(comment.llm_rule)} chars). Minimum: 15",
                severity="warning"
            ))
        
        # Check for placeholder text
        placeholders = ['TODO', 'FIXME', '[Business purpose]', '[Technical implementation]']
        for field_name in ['llm_does', 'llm_rule']:
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
        # Check for type consistency - Evolved format
        type_actions = defaultdict(set)
        for comment in comments:
            if comment.llm_type and comment.llm_does:
                type_actions[comment.llm_type].add(comment.llm_does.lower())

        # Warn if same type has very different actions (potential inconsistency)
        for type_name, actions in type_actions.items():
            if len(actions) > 5:  # Many different actions for same type
                sample_comment = next(c for c in comments if c.llm_type == type_name)
                self.issues.append(ValidationIssue(
                    file_path=sample_comment.file_path,
                    line_number=sample_comment.line_number,
                    element_name=sample_comment.element_name,
                    issue_type="type_action_diversity",
                    message=f"Type '{type_name}' has {len(actions)} different actions - consider more specific types",
                    severity="info"
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

# ============================================================================
# TDD Interface Functions
# ============================================================================

def validate_comment(comment) -> List[Dict]:
    """
@llm-type util.function
@llm-does individual comment for completeness and quality
"""
    validator = LLMCommentValidator()
    validator.issues = []
    validator._validate_comment(comment)
    return [asdict(issue) for issue in validator.issues]

def validate_all_comments(comments: List) -> Dict:
    """
@llm-type util.function
@llm-does batch of comments and returns summary
"""
    from datetime import datetime

    validator = LLMCommentValidator()
    validator.issues = []

    for comment in comments:
        validator._validate_comment(comment)

    validator._validate_consistency(comments)
    validator._validate_coverage(comments)

    return {
        'issues': [asdict(issue) for issue in validator.issues],
        'total_comments_validated': len(comments),
        'passed': len([i for i in validator.issues if i.severity == 'error']) == 0,
        'validation_timestamp': datetime.now().isoformat()
    }

def check_required_tags(comment) -> List[Dict]:
    """
@llm-type util.function
@llm-does comment has all required tags for its
"""
    validator = LLMCommentValidator()
    validator.issues = []

    if comment.type:
        required = validator.required_tags.get(comment.type, ['type', 'legend'])

        for tag in required:
            attr_name = f'llm_{tag}' if not tag.startswith('llm_') else tag
            if not hasattr(comment, attr_name) or not getattr(comment, attr_name, None):
                validator.issues.append(ValidationIssue(
                    file_path=comment.file_path,
                    line_number=comment.line_number,
                    element_name=getattr(comment, 'element_name', 'unknown'),
                    issue_type="missing_tag",
                    message=f"Missing required @{tag.replace('_', '-')} tag for {comment.type}",
                    severity="error"
                ))

    return [asdict(issue) for issue in validator.issues]

def check_tag_format(comment) -> List[Dict]:
    """
@llm-type util.function
@llm-does tag content meets quality standards
"""
    validator = LLMCommentValidator()
    validator.issues = []

    # Check for empty required fields
    if hasattr(comment, 'legend') and comment.legend is not None and len(comment.legend.strip()) == 0:
        validator.issues.append(ValidationIssue(
            file_path=comment.file_path,
            line_number=comment.line_number,
            element_name=getattr(comment, 'element_name', 'unknown'),
            issue_type="empty_tag",
            message="@llm-legend cannot be empty",
            severity="error"
        ))

    return [asdict(issue) for issue in validator.issues]

if __name__ == "__main__":
    exit(main())
