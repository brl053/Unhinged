#!/usr/bin/env python3
"""
LLM Comment Extraction System

Parses @llm-* tags from code comments across all programming languages
in the Unhinged monorepo and generates architectural documentation.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class LLMComment:
    """Represents a parsed LLM comment with all metadata"""
    file_path: str
    line_number: int
    element_name: str
    language: str
    llm_type: Optional[str] = None
    llm_legend: Optional[str] = None
    llm_key: Optional[str] = None
    llm_map: Optional[str] = None
    llm_axiom: Optional[str] = None
    llm_contract: Optional[str] = None
    llm_token: Optional[str] = None
    llm_context: Optional[str] = None  # NEW: @llm-context support
    raw_comment: str = ""
    context: str = ""

class LanguageParser:
    """Base class for language-specific comment parsers"""
    
    def __init__(self, file_extensions: List[str], comment_patterns: Dict[str, str]):
        self.file_extensions = file_extensions
        self.comment_patterns = comment_patterns
    
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file"""
        return any(file_path.endswith(ext) for ext in self.file_extensions)
    
    def extract_comments(self, content: str, file_path: str) -> List[LLMComment]:
        """Extract LLM comments from file content"""
        raise NotImplementedError

class TypeScriptParser(LanguageParser):
    """Parser for TypeScript/JavaScript JSDoc comments"""
    
    def __init__(self):
        super().__init__(
            ['.ts', '.js', '.tsx', '.jsx'],
            {
                'block': r'/\*\*(.*?)\*/',
                'line': r'//\s*(.*?)$'
            }
        )
    
    def extract_comments(self, content: str, file_path: str) -> List[LLMComment]:
        comments = []
        lines = content.split('\n')
        
        # Find JSDoc blocks
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for JSDoc start
            if line.startswith('/**'):
                comment_lines = []
                start_line = i + 1
                i += 1
                
                # Collect comment content
                while i < len(lines) and not lines[i].strip().endswith('*/'):
                    comment_line = lines[i].strip()
                    if comment_line.startswith('*'):
                        comment_line = comment_line[1:].strip()
                    comment_lines.append(comment_line)
                    i += 1
                
                # Get the element this comment describes
                element_name, context = self._find_next_element(lines, i + 1)
                
                # Parse LLM tags
                llm_comment = self._parse_llm_tags(
                    '\n'.join(comment_lines), 
                    file_path, 
                    start_line, 
                    element_name,
                    'typescript',
                    context
                )
                
                if llm_comment:
                    comments.append(llm_comment)
            
            i += 1
        
        return comments
    
    def _find_next_element(self, lines: List[str], start_idx: int) -> Tuple[str, str]:
        """Find the next code element after a comment"""
        for i in range(start_idx, min(start_idx + 5, len(lines))):
            line = lines[i].strip()
            if not line or line.startswith('//'):
                continue
            
            # Look for function, class, interface, etc.
            patterns = [
                r'(?:export\s+)?(?:async\s+)?function\s+(\w+)',
                r'(?:export\s+)?class\s+(\w+)',
                r'(?:export\s+)?interface\s+(\w+)',
                r'(?:export\s+)?const\s+(\w+)',
                r'(?:export\s+)?let\s+(\w+)',
                r'(\w+)\s*[:=]\s*(?:async\s+)?\(',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1), line
        
        return "unknown", ""
    
    def _parse_llm_tags(self, comment_text: str, file_path: str, line_number: int, 
                       element_name: str, language: str, context: str) -> Optional[LLMComment]:
        """Parse @llm-* tags from comment text"""
        if '@llm-' not in comment_text:
            return None
        
        llm_comment = LLMComment(
            file_path=file_path,
            line_number=line_number,
            element_name=element_name,
            language=language,
            raw_comment=comment_text,
            context=context
        )
        
        # Extract each LLM tag
        tag_patterns = {
            'llm_type': r'@llm-type\s+(\w+)',
            'llm_legend': r'@llm-legend\s+(.+?)(?=@llm-|\n\n|\Z)',
            'llm_key': r'@llm-key\s+(.+?)(?=@llm-|\n\n|\Z)',
            'llm_map': r'@llm-map\s+(.+?)(?=@llm-|\n\n|\Z)',
            'llm_axiom': r'@llm-axiom\s+(.+?)(?=@llm-|\n\n|\Z)',
            'llm_contract': r'@llm-contract\s+(.+?)(?=@llm-|\n\n|\Z)',
            'llm_token': r'@llm-token\s+(.+?)(?=@llm-|\n\n|\Z)',
            'llm_context': r'@llm-context\s+(.+?)(?=@llm-|\n\n|\Z)'  # NEW
        }
        
        for attr, pattern in tag_patterns.items():
            match = re.search(pattern, comment_text, re.DOTALL | re.IGNORECASE)
            if match:
                value = match.group(1).strip().replace('\n', ' ')
                setattr(llm_comment, attr, value)
        
        return llm_comment

class PythonParser(LanguageParser):
    """Parser for Python docstrings"""
    
    def __init__(self):
        super().__init__(
            ['.py'],
            {
                'docstring': r'"""(.*?)"""',
                'single_quote': r"'''(.*?)'''"
            }
        )
    
    def extract_comments(self, content: str, file_path: str) -> List[LLMComment]:
        comments = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for docstring start
            if '"""' in line or "'''" in line:
                quote_type = '"""' if '"""' in line else "'''"
                comment_lines = []
                start_line = i + 1
                
                # Handle single-line docstring
                if line.count(quote_type) >= 2:
                    docstring = line.split(quote_type)[1]
                    comment_lines = [docstring]
                    element_name, context = self._find_element_for_docstring(lines, i)
                else:
                    # Multi-line docstring
                    i += 1
                    while i < len(lines) and quote_type not in lines[i]:
                        comment_lines.append(lines[i].strip())
                        i += 1
                    
                    element_name, context = self._find_element_for_docstring(lines, start_line - 1)
                
                # Parse LLM tags
                llm_comment = self._parse_llm_tags(
                    '\n'.join(comment_lines),
                    file_path,
                    start_line,
                    element_name,
                    'python',
                    context
                )
                
                if llm_comment:
                    comments.append(llm_comment)
            
            i += 1
        
        return comments
    
    def _find_element_for_docstring(self, lines: List[str], docstring_line: int) -> Tuple[str, str]:
        """Find the Python element (class, function) that owns this docstring"""
        # Look backwards for def or class
        for i in range(docstring_line - 1, max(0, docstring_line - 5), -1):
            line = lines[i].strip()
            
            patterns = [
                r'def\s+(\w+)',
                r'class\s+(\w+)',
                r'async\s+def\s+(\w+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1), line
        
        return "unknown", ""
    
    def _parse_llm_tags(self, comment_text: str, file_path: str, line_number: int,
                       element_name: str, language: str, context: str) -> Optional[LLMComment]:
        """Parse @llm-* tags from Python docstring"""
        if '@llm-' not in comment_text:
            return None
        
        # Use same parsing logic as TypeScript
        return TypeScriptParser()._parse_llm_tags(
            comment_text, file_path, line_number, element_name, language, context
        )

class KotlinParser(LanguageParser):
    """Parser for Kotlin KDoc comments"""
    
    def __init__(self):
        super().__init__(
            ['.kt', '.kts'],
            {
                'kdoc': r'/\*\*(.*?)\*/'
            }
        )
    
    def extract_comments(self, content: str, file_path: str) -> List[LLMComment]:
        # Similar to TypeScript but with Kotlin-specific patterns
        comments = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('/**'):
                comment_lines = []
                start_line = i + 1
                i += 1
                
                while i < len(lines) and not lines[i].strip().endswith('*/'):
                    comment_line = lines[i].strip()
                    if comment_line.startswith('*'):
                        comment_line = comment_line[1:].strip()
                    comment_lines.append(comment_line)
                    i += 1
                
                element_name, context = self._find_next_kotlin_element(lines, i + 1)
                
                llm_comment = TypeScriptParser()._parse_llm_tags(
                    '\n'.join(comment_lines),
                    file_path,
                    start_line,
                    element_name,
                    'kotlin',
                    context
                )
                
                if llm_comment:
                    comments.append(llm_comment)
            
            i += 1
        
        return comments
    
    def _find_next_kotlin_element(self, lines: List[str], start_idx: int) -> Tuple[str, str]:
        """Find the next Kotlin element after a comment"""
        for i in range(start_idx, min(start_idx + 5, len(lines))):
            line = lines[i].strip()
            if not line or line.startswith('//'):
                continue
            
            patterns = [
                r'(?:suspend\s+)?fun\s+(\w+)',
                r'class\s+(\w+)',
                r'interface\s+(\w+)',
                r'object\s+(\w+)',
                r'val\s+(\w+)',
                r'var\s+(\w+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1), line
        
        return "unknown", ""

class YAMLParser(LanguageParser):
    """Parser for YAML comments"""
    
    def __init__(self):
        super().__init__(
            ['.yml', '.yaml'],
            {
                'line': r'#\s*(.*?)$'
            }
        )
    
    def extract_comments(self, content: str, file_path: str) -> List[LLMComment]:
        comments = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Look for comment blocks
            if line.strip().startswith('#') and '@llm-' in line:
                comment_lines = []
                start_line = i + 1
                
                # Collect consecutive comment lines
                while i < len(lines) and lines[i].strip().startswith('#'):
                    comment_line = lines[i].strip()[1:].strip()
                    comment_lines.append(comment_line)
                    i += 1
                
                # Find the YAML key this comment describes
                element_name = self._find_next_yaml_key(lines, i)
                
                llm_comment = TypeScriptParser()._parse_llm_tags(
                    '\n'.join(comment_lines),
                    file_path,
                    start_line,
                    element_name,
                    'yaml',
                    lines[i].strip() if i < len(lines) else ""
                )
                
                if llm_comment:
                    comments.append(llm_comment)
            else:
                i += 1
        
        return comments
    
    def _find_next_yaml_key(self, lines: List[str], start_idx: int) -> str:
        """Find the next YAML key after comments"""
        for i in range(start_idx, min(start_idx + 3, len(lines))):
            line = lines[i].strip()
            if ':' in line and not line.startswith('#'):
                key = line.split(':')[0].strip()
                return key
        return "unknown"

class LLMCommentExtractor:
    """Main extractor that coordinates all language parsers"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.parsers = [
            TypeScriptParser(),
            PythonParser(),
            KotlinParser(),
            YAMLParser()
        ]
        self.ignore_dirs = {
            '.git', 'node_modules', 'build', 'target', 'dist',
            '.gradle', '__pycache__', '.pytest_cache', 'coverage'
        }
    
    def extract_all_comments(self) -> List[LLMComment]:
        """Extract all LLM comments from the entire codebase"""
        all_comments = []
        
        for root, dirs, files in os.walk(self.root_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.root_path)
                
                # Find appropriate parser
                parser = self._get_parser_for_file(file_path)
                if not parser:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    comments = parser.extract_comments(content, rel_path)
                    all_comments.extend(comments)
                    
                except Exception as e:
                    print(f"Warning: Could not parse {rel_path}: {e}")
        
        return all_comments
    
    def _get_parser_for_file(self, file_path: str) -> Optional[LanguageParser]:
        """Get the appropriate parser for a file"""
        for parser in self.parsers:
            if parser.can_parse(file_path):
                return parser
        return None

class ArchitecturalDocGenerator:
    """Generates architectural documentation from LLM comments"""

    def __init__(self, comments: List[LLMComment]):
        self.comments = comments

    def generate_code_philosophy_doc(self) -> str:
        """Generate docs/architecture/code-philosophy.md from axioms and design reasoning"""
        doc = []

        doc.append("# 🏛️ Code Philosophy - Unhinged Platform")
        doc.append("")
        doc.append("> **Purpose**: Fundamental design principles extracted from codebase")
        doc.append("> **Source**: Auto-generated from @llm-axiom and @llm-token comments")
        doc.append(f"> **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.append("")

        # Extract axioms
        axioms = [c for c in self.comments if c.llm_axiom]
        if axioms:
            doc.append("## 🎯 Fundamental Axioms")
            doc.append("")
            doc.append("These are the non-negotiable principles that guide all development:")
            doc.append("")

            for comment in axioms:
                doc.append(f"### {comment.element_name} ({comment.language})")
                doc.append(f"**File**: `{comment.file_path}`")
                doc.append(f"**Axiom**: {comment.llm_axiom}")
                if comment.llm_legend:
                    doc.append(f"**Context**: {comment.llm_legend}")
                doc.append("")

        # Extract domain vocabulary
        tokens = [c for c in self.comments if c.llm_token]
        if tokens:
            doc.append("## 📚 Domain Vocabulary")
            doc.append("")
            doc.append("Project-specific terminology and concepts:")
            doc.append("")

            for comment in tokens:
                doc.append(f"### {comment.element_name}")
                doc.append(f"**Definition**: {comment.llm_token}")
                doc.append(f"**Source**: `{comment.file_path}` ({comment.language})")
                doc.append("")

        return '\n'.join(doc)

    def generate_architectural_overview(self) -> str:
        """Generate architectural overview from @llm-map comments"""
        doc = []

        doc.append("# 🗺️ Architectural Overview - Auto-Generated")
        doc.append("")
        doc.append("> **Purpose**: System architecture extracted from code comments")
        doc.append("> **Source**: Auto-generated from @llm-map and @llm-type comments")
        doc.append(f"> **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.append("")

        # Group by type
        by_type = defaultdict(list)
        for comment in self.comments:
            if comment.llm_type and comment.llm_map:
                by_type[comment.llm_type].append(comment)

        for component_type, components in by_type.items():
            doc.append(f"## {component_type.title()} Components")
            doc.append("")

            for comment in components:
                doc.append(f"### {comment.element_name}")
                doc.append(f"**File**: `{comment.file_path}`")
                doc.append(f"**Language**: {comment.language}")
                if comment.llm_legend:
                    doc.append(f"**Purpose**: {comment.llm_legend}")
                doc.append(f"**Architecture**: {comment.llm_map}")
                if comment.llm_key:
                    doc.append(f"**Implementation**: {comment.llm_key}")
                doc.append("")

        return '\n'.join(doc)

def main():
    """Main function to extract and analyze LLM comments"""
    extractor = LLMCommentExtractor()
    comments = extractor.extract_all_comments()

    print(f"✅ Extracted {len(comments)} LLM comments from codebase")

    # Group by type for analysis
    by_type = defaultdict(list)
    by_language = defaultdict(list)

    for comment in comments:
        if comment.llm_type:
            by_type[comment.llm_type].append(comment)
        by_language[comment.language].append(comment)

    print(f"📊 Found comments in {len(by_language)} languages")
    for lang, lang_comments in by_language.items():
        print(f"  - {lang}: {len(lang_comments)} comments")

    print(f"📊 Comment types distribution:")
    for comment_type, type_comments in by_type.items():
        print(f"  - {comment_type}: {len(type_comments)} comments")

    # Generate architectural documentation
    doc_generator = ArchitecturalDocGenerator(comments)

    # Generate code philosophy document
    philosophy_doc = doc_generator.generate_code_philosophy_doc()
    philosophy_path = "docs/architecture/code-philosophy.md"
    os.makedirs(os.path.dirname(philosophy_path), exist_ok=True)
    with open(philosophy_path, 'w') as f:
        f.write(philosophy_doc)
    print(f"📖 Generated {philosophy_path}")

    # Generate architectural overview
    arch_doc = doc_generator.generate_architectural_overview()
    arch_path = "docs/architecture/code-architecture.md"
    with open(arch_path, 'w') as f:
        f.write(arch_doc)
    print(f"🏗️ Generated {arch_path}")

    # Save raw results
    output_path = "docs/architecture/extracted-comments.json"
    with open(output_path, 'w') as f:
        json.dump([asdict(comment) for comment in comments], f, indent=2)
    print(f"💾 Saved detailed results to {output_path}")

    return comments

# ============================================================================
# TDD Interface Functions
# ============================================================================

def extract_comments_from_file(file_path: str) -> List[LLMComment]:
    """Extract LLM comments from a single file.

    @llm-type function
    @llm-legend Extracts all @llm-* comments from a single source file using appropriate language parser
    @llm-context TDD interface function for testing individual file processing
    """
    extractor = LLMCommentExtractor()
    parser = extractor._get_parser_for_file(file_path)
    if not parser:
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        rel_path = os.path.relpath(file_path, extractor.root_path)
        return parser.extract_comments(content, rel_path)
    except Exception:
        return []

def extract_comments_from_codebase(root_path: Path) -> List[LLMComment]:
    """Extract LLM comments from entire codebase.

    @llm-type function
    @llm-legend Extracts all @llm-* comments from entire codebase using multi-language parsers
    @llm-context TDD interface function for testing full codebase processing
    """
    extractor = LLMCommentExtractor(str(root_path))
    return extractor.extract_all_comments()

def parse_llm_tags(text: str) -> Dict[str, str]:
    """Parse @llm-* tags from comment text.

    @llm-type function
    @llm-legend Parses individual @llm-* tags from comment text using regex patterns
    @llm-context TDD interface function for testing tag parsing logic
    """
    if '@llm-' not in text:
        return {}

    tag_patterns = {
        'llm_type': r'@llm-type\s+(\w+)',
        'llm_legend': r'@llm-legend\s+(.+?)(?=@llm-|\n\n|\Z)',
        'llm_key': r'@llm-key\s+(.+?)(?=@llm-|\n\n|\Z)',
        'llm_map': r'@llm-map\s+(.+?)(?=@llm-|\n\n|\Z)',
        'llm_axiom': r'@llm-axiom\s+(.+?)(?=@llm-|\n\n|\Z)',
        'llm_contract': r'@llm-contract\s+(.+?)(?=@llm-|\n\n|\Z)',
        'llm_token': r'@llm-token\s+(.+?)(?=@llm-|\n\n|\Z)',
        'llm_context': r'@llm-context\s+(.+?)(?=@llm-|\n\n|\Z)'
    }

    result = {}
    for attr, pattern in tag_patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            value = match.group(1).strip().replace('\n', ' ')
            result[attr] = value

    return result

def save_extraction_results(comments: List[LLMComment], output_path: Path) -> Dict:
    """Save extraction results to JSON file.

    @llm-type function
    @llm-legend Saves extracted comments to JSON with metadata
    @llm-context TDD interface function for testing result serialization
    """
    from datetime import datetime

    result = {
        'comments': [asdict(comment) for comment in comments],
        'total_files_scanned': len(set(c.file_path for c in comments)),
        'files_with_comments': len(set(c.file_path for c in comments if c.llm_type)),
        'extraction_timestamp': datetime.now().isoformat()
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    return result

if __name__ == "__main__":
    main()
