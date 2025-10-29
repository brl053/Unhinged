# Util - Validator

> **Generated from LlmDocs**: 2025-10-28 23:59:42
> **Category**: `util.validator`
> **Components**: 13

## Components

1. [test_parse_llm_tags_with_context](#test-parse-llm-tags-with-context) - `build/docs-generation/test_llm_extraction.py`
2. [unknown](#unknown) - `build/docs-generation/validate-llm-comments.py`
3. [unknown](#unknown) - `build/validators/port_validator.py`
4. [unknown](#unknown) - `build/validators/resource_validator.py`
5. [unknown](#unknown) - `build/validators/kotlin_validator.py`
6. [KotlinValidator](#kotlinvalidator) - `build/validators/kotlin_validator.py`
7. [FilePatternValidator](#filepatternvalidator) - `build/validators/polyglot_validator.py`
8. [GeneratedContentValidator](#generatedcontentvalidator) - `build/validators/polyglot_validator.py`
9. [unknown](#unknown) - `build/validators/dependency_validator.py`
10. [unknown](#unknown) - `build/validators/python_validator.py`
11. [PythonValidator](#pythonvalidator) - `build/validators/python_validator.py`
12. [PythonFormatterValidator](#pythonformattervalidator) - `build/validators/python_validator.py`
13. [unknown](#unknown) - `libs/design_system/build/component_validator.py`

## test_parse_llm_tags_with_context

### Metadata

- **File**: `build/docs-generation/test_llm_extraction.py`
- **Language**: python
- **Type**: `util.validator`

### Purpose

user input

### Rules & Constraints

⚠️ **Critical**: never trust user input

---

## unknown

### Metadata

- **File**: `build/docs-generation/validate-llm-comments.py`
- **Language**: python
- **Type**: `util.validator`

### Purpose

llmdocs validation and quality assurance for evolved format compliance

### Rules & Constraints

⚠️ **Critical**: validation must enforce evolved format standards and provide actionable feedback

---

## unknown

### Metadata

- **File**: `build/validators/port_validator.py`
- **Language**: python
- **Type**: `util.validator`

### Purpose

port conflict detection and auto-resolution across docker-compose files

### Rules & Constraints

⚠️ **Critical**: port conflicts must be resolved at build time, never at runtime

---

## unknown

### Metadata

- **File**: `build/validators/resource_validator.py`
- **Language**: python
- **Type**: `util.validator`

### Purpose

resource allocation validation for memory, disk, and cpu limits

### Rules & Constraints

⚠️ **Critical**: resource allocation must be validated at build time to prevent runtime failures

---

## unknown

### Metadata

- **File**: `build/validators/kotlin_validator.py`
- **Language**: python
- **Type**: `util.validator`

### Purpose

kotlin-specific validation for build patterns and code

---

## KotlinValidator

### Metadata

- **File**: `build/validators/kotlin_validator.py`
- **Language**: python
- **Type**: `util.validator`

### Purpose

kotlin-specific validation for build patterns and code

---

## FilePatternValidator

### Metadata

- **File**: `build/validators/polyglot_validator.py`
- **Language**: python
- **Type**: `util.validator`

### Purpose

file creation patterns and prevents scattered cruft

---

## GeneratedContentValidator

### Metadata

- **File**: `build/validators/polyglot_validator.py`
- **Language**: python
- **Type**: `util.validator`

### Purpose

that generated content is properly located in

---

## unknown

### Metadata

- **File**: `build/validators/dependency_validator.py`
- **Language**: python
- **Type**: `util.validator`

### Purpose

dependency validation and conflict resolution across package managers

### Rules & Constraints

⚠️ **Critical**: dependency conflicts must be resolved at build time to prevent runtime failures

---

## unknown

### Metadata

- **File**: `build/validators/python_validator.py`
- **Language**: python
- **Type**: `util.validator`

### Purpose

python-specific validation for code quality, imports, and

---

## PythonValidator

### Metadata

- **File**: `build/validators/python_validator.py`
- **Language**: python
- **Type**: `util.validator`

### Purpose

python-specific validation for code quality and unhinged

---

## PythonFormatterValidator

### Metadata

- **File**: `build/validators/python_validator.py`
- **Language**: python
- **Type**: `util.validator`

### Purpose

python code formatting validation using black and

---

## unknown

### Metadata

- **File**: `libs/design_system/build/component_validator.py`
- **Language**: python
- **Type**: `util.validator`

### Purpose

component specification validator ensuring yaml specs con...

### Rules & Constraints

⚠️ **Critical**: all component specifications must be validated before generator consumption

---

