# Deterministic Polyglot Language Parsing System - Technical Specification

## 🎯 **Executive Summary**

**Objective:** Build a deterministic, test-driven regex pattern system for reliable source code parsing across all supported languages in the Unhinged build system.

**Core Innovation:** By constraining language features through `/build/constraints/`, we achieve 100% deterministic regex coverage, eliminating the traditional limitations of regex-based parsing.

**Priority:** HIGH - Foundation for enhanced LlmDocs system and build automation

## 🏗️ **System Architecture**

### **Directory Structure**
```
/build/
├── regex/                    # Polyglot regex pattern libraries
│   ├── python/
│   │   ├── patterns.py       # Core regex patterns
│   │   ├── parser.py         # Functional programming interface
│   │   └── test_patterns.py  # Comprehensive unit tests
│   ├── typescript/
│   │   ├── patterns.ts
│   │   ├── parser.ts
│   │   └── test_patterns.ts
│   ├── javascript/
│   ├── kotlin/
│   ├── c/
│   └── yaml/
├── constraints/              # Language feature constraint system
│   ├── python.yml           # Allowed Python language features
│   ├── typescript.yml       # Allowed TypeScript features
│   ├── javascript.yml       # Allowed JavaScript features
│   ├── kotlin.yml           # Allowed Kotlin features
│   ├── c.yml                # Allowed C/C++ features
│   └── yaml.yml             # Allowed YAML features
└── POLYGLOT_PARSING_SYSTEM_SPEC.md  # This specification
```

### **Core Principles**

1. **Deterministic Parsing:** 100% reliable results through language feature constraints
2. **Test-Driven Development:** Every regex pattern has comprehensive unit tests
3. **Functional Programming:** Pure functions with structured input/output
4. **Polyglot Consistency:** Uniform interfaces across all supported languages
5. **Build System Integration:** Seamless integration with existing `/build/` infrastructure

## 🔧 **Language Constraint System**

### **Constraint Schema Design**

Each language constraint file defines:
- **Allowed syntax features** (subset of full language)
- **Parsing boundaries** (what we need to extract)
- **Complexity limits** (maximum nesting, line length, etc.)
- **Exclusion patterns** (features we don't support)

### **Example: `/build/constraints/python.yml`**
```yaml
# Python Language Constraints for Deterministic Parsing
language: python
version: "3.8+"
description: "Constrained Python feature set for reliable regex parsing"

allowed_features:
  classes:
    - simple_class_definitions
    - inheritance_single_parent
    - decorators_standard
  functions:
    - function_definitions
    - method_definitions
    - decorators_standard
    - type_hints_basic
  imports:
    - import_statements
    - from_import_statements
    - relative_imports
  documentation:
    - llm_doc_tags
    - docstrings_standard
    - comments_inline

excluded_features:
  - metaclasses
  - complex_decorators_with_arguments
  - dynamic_class_creation
  - exec_eval_statements
  - complex_comprehensions_nested

parsing_limits:
  max_line_length: 120
  max_nesting_depth: 4
  max_function_parameters: 10

extraction_targets:
  - class_names_and_inheritance
  - function_signatures
  - import_dependencies
  - llm_documentation_tags
  - decorator_applications
```

### **Constraint Enforcement**

The constraint system ensures:
- **Predictable parsing** - Limited feature set = complete regex coverage
- **Maintainable patterns** - Smaller surface area = simpler regex
- **Reliable results** - Constrained input = deterministic output
- **Performance optimization** - Focused patterns = faster parsing

## 🐍 **Python Implementation Example**

### **`/build/regex/python/patterns.py`**
```python
"""
Deterministic Python source code parsing patterns
Constrained by /build/constraints/python.yml
"""

import re
from typing import List, Dict, Optional, NamedTuple
from dataclasses import dataclass

@dataclass
class ClassDefinition:
    name: str
    parent_class: Optional[str]
    decorators: List[str]
    line_number: int
    llm_tags: Dict[str, str]

@dataclass
class FunctionDefinition:
    name: str
    parameters: List[str]
    return_type: Optional[str]
    decorators: List[str]
    line_number: int
    is_method: bool
    llm_tags: Dict[str, str]

# Core regex patterns (deterministic within constraints)
CLASS_PATTERN = re.compile(
    r'^(?P<decorators>(?:@\w+\n)*)'
    r'class\s+(?P<name>\w+)'
    r'(?:\((?P<parent>\w+)\))?'
    r'\s*:',
    re.MULTILINE
)

FUNCTION_PATTERN = re.compile(
    r'^(?P<decorators>(?:@\w+\n)*)'
    r'(?P<indent>\s*)'
    r'def\s+(?P<name>\w+)'
    r'\((?P<params>[^)]*)\)'
    r'(?:\s*->\s*(?P<return_type>\w+))?'
    r'\s*:',
    re.MULTILINE
)

LLM_TAG_PATTERN = re.compile(
    r'#\s*@llm-(?P<tag>\w+)\s+(?P<value>.*?)$',
    re.MULTILINE
)

IMPORT_PATTERN = re.compile(
    r'^(?:from\s+(?P<module>\S+)\s+)?import\s+(?P<items>.+)$',
    re.MULTILINE
)
```

### **`/build/regex/python/parser.py`**
```python
"""
Functional programming interface for Python source parsing
Pure functions with structured input/output
"""

from typing import List, Dict, Any
from .patterns import (
    ClassDefinition, FunctionDefinition,
    CLASS_PATTERN, FUNCTION_PATTERN, LLM_TAG_PATTERN, IMPORT_PATTERN
)

def extract_classes(source_code: str) -> List[ClassDefinition]:
    """Extract all class definitions from Python source code"""
    classes = []
    lines = source_code.split('\n')
    
    for match in CLASS_PATTERN.finditer(source_code):
        line_num = source_code[:match.start()].count('\n') + 1
        
        # Extract LLM tags for this class
        class_start = match.start()
        class_end = _find_class_end(source_code, class_start)
        class_source = source_code[class_start:class_end]
        llm_tags = extract_llm_tags(class_source)
        
        classes.append(ClassDefinition(
            name=match.group('name'),
            parent_class=match.group('parent'),
            decorators=_parse_decorators(match.group('decorators')),
            line_number=line_num,
            llm_tags=llm_tags
        ))
    
    return classes

def extract_functions(source_code: str) -> List[FunctionDefinition]:
    """Extract all function definitions from Python source code"""
    functions = []
    
    for match in FUNCTION_PATTERN.finditer(source_code):
        line_num = source_code[:match.start()].count('\n') + 1
        is_method = len(match.group('indent')) > 0
        
        # Extract LLM tags for this function
        func_start = match.start()
        func_end = _find_function_end(source_code, func_start)
        func_source = source_code[func_start:func_end]
        llm_tags = extract_llm_tags(func_source)
        
        functions.append(FunctionDefinition(
            name=match.group('name'),
            parameters=_parse_parameters(match.group('params')),
            return_type=match.group('return_type'),
            decorators=_parse_decorators(match.group('decorators')),
            line_number=line_num,
            is_method=is_method,
            llm_tags=llm_tags
        ))
    
    return functions

def extract_llm_tags(source_code: str) -> Dict[str, str]:
    """Extract @llm-* documentation tags from source code"""
    tags = {}
    for match in LLM_TAG_PATTERN.finditer(source_code):
        tags[match.group('tag')] = match.group('value').strip()
    return tags

def extract_imports(source_code: str) -> List[Dict[str, Any]]:
    """Extract all import statements from Python source code"""
    imports = []
    for match in IMPORT_PATTERN.finditer(source_code):
        imports.append({
            'module': match.group('module'),
            'items': [item.strip() for item in match.group('items').split(',')],
            'line_number': source_code[:match.start()].count('\n') + 1
        })
    return imports

def parse_python_file(file_path: str) -> Dict[str, Any]:
    """Complete parsing of a Python file - main entry point"""
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    return {
        'file_path': file_path,
        'classes': extract_classes(source_code),
        'functions': extract_functions(source_code),
        'imports': extract_imports(source_code),
        'llm_tags': extract_llm_tags(source_code)
    }

# Helper functions
def _parse_decorators(decorator_text: str) -> List[str]:
    """Parse decorator text into list of decorator names"""
    if not decorator_text:
        return []
    return [line.strip()[1:] for line in decorator_text.strip().split('\n') if line.strip().startswith('@')]

def _parse_parameters(param_text: str) -> List[str]:
    """Parse function parameter text into list of parameter names"""
    if not param_text:
        return []
    return [param.strip().split(':')[0].strip() for param in param_text.split(',') if param.strip()]

def _find_class_end(source_code: str, start_pos: int) -> int:
    """Find the end position of a class definition"""
    # Simplified implementation - would need more sophisticated logic
    lines = source_code[start_pos:].split('\n')
    indent_level = len(lines[0]) - len(lines[0].lstrip())
    
    for i, line in enumerate(lines[1:], 1):
        if line.strip() and len(line) - len(line.lstrip()) <= indent_level:
            return start_pos + sum(len(l) + 1 for l in lines[:i])
    
    return len(source_code)

def _find_function_end(source_code: str, start_pos: int) -> int:
    """Find the end position of a function definition"""
    # Similar logic to _find_class_end but for functions
    return _find_class_end(source_code, start_pos)
```

## 🧪 **Test-Driven Development Approach**

### **`/build/regex/python/test_patterns.py`**
```python
"""
Comprehensive unit tests for Python parsing patterns
TDD approach - tests written before implementation
"""

import unittest
from .parser import extract_classes, extract_functions, extract_llm_tags, extract_imports

class TestPythonPatterns(unittest.TestCase):
    
    def test_simple_class_extraction(self):
        """Test extraction of simple class definitions"""
        source = '''
class SimpleClass:
    pass

class InheritedClass(BaseClass):
    pass
'''
        classes = extract_classes(source)
        self.assertEqual(len(classes), 2)
        self.assertEqual(classes[0].name, 'SimpleClass')
        self.assertIsNone(classes[0].parent_class)
        self.assertEqual(classes[1].name, 'InheritedClass')
        self.assertEqual(classes[1].parent_class, 'BaseClass')
    
    def test_decorated_class_extraction(self):
        """Test extraction of decorated classes"""
        source = '''
@dataclass
@llm-type service
class DecoratedClass:
    pass
'''
        classes = extract_classes(source)
        self.assertEqual(len(classes), 1)
        self.assertEqual(classes[0].decorators, ['dataclass'])
        self.assertEqual(classes[0].llm_tags['type'], 'service')
    
    def test_function_extraction(self):
        """Test extraction of function definitions"""
        source = '''
def simple_function():
    pass

def typed_function(param: str) -> int:
    return 42

    def method_function(self, param):
        pass
'''
        functions = extract_functions(source)
        self.assertEqual(len(functions), 3)
        self.assertEqual(functions[0].name, 'simple_function')
        self.assertFalse(functions[0].is_method)
        self.assertEqual(functions[1].return_type, 'int')
        self.assertTrue(functions[2].is_method)
    
    def test_llm_tag_extraction(self):
        """Test extraction of @llm-* documentation tags"""
        source = '''
# @llm-type control-system
# @llm-legend Main application controller
# @llm-key Core functionality
class Controller:
    pass
'''
        tags = extract_llm_tags(source)
        self.assertEqual(tags['type'], 'control-system')
        self.assertEqual(tags['legend'], 'Main application controller')
        self.assertEqual(tags['key'], 'Core functionality')
    
    def test_import_extraction(self):
        """Test extraction of import statements"""
        source = '''
import os
from typing import List, Dict
from .local_module import LocalClass
'''
        imports = extract_imports(source)
        self.assertEqual(len(imports), 3)
        self.assertIsNone(imports[0]['module'])
        self.assertEqual(imports[1]['module'], 'typing')
        self.assertEqual(imports[2]['module'], '.local_module')

if __name__ == '__main__':
    unittest.main()
```

## 🔗 **Integration Points**

### **LlmDocs System Integration**
- Enhanced @llm-* tag extraction across all languages
- Structured documentation parsing for build system
- Automated documentation generation with higher accuracy

### **Build System Integration**
- Source code analysis for dependency tracking
- Automated code generation validation
- Build target discovery and optimization

### **Quality Assurance Integration**
- Code pattern validation
- Architectural compliance checking
- Automated refactoring support

## 📊 **Success Metrics**

1. **100% Unit Test Coverage** - Every regex pattern thoroughly tested
2. **Deterministic Results** - Same input always produces same output
3. **Performance Benchmarks** - Sub-millisecond parsing for typical files
4. **Language Coverage** - All 6 supported languages fully implemented
5. **Build Integration** - Seamless integration with existing `/build/` system

## 🚀 **Implementation Timeline**

1. **Phase 1:** Design constraint system and Python implementation (3-4 days)
2. **Phase 2:** Implement Kotlin and TypeScript libraries (2-3 days)
3. **Phase 3:** Complete JavaScript, C/C++, and YAML libraries (2-3 days)
4. **Phase 4:** Integration testing and LlmDocs connection (1-2 days)

**Total Estimated Effort:** 8-12 days for complete system

This deterministic polyglot parsing system will provide GNU-library-quality language analysis capabilities, enabling advanced build automation and documentation generation across the entire Unhinged codebase.
