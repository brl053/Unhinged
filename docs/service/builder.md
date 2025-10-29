# Service - Builder

> **Generated from LlmDocs**: 2025-10-28 23:59:42
> **Category**: `service.builder`
> **Components**: 6

## Components

1. [unknown](#unknown) - `build/modules/typescript_builder.py`
2. [unknown](#unknown) - `build/modules/c_builder.py`
3. [unknown](#unknown) - `build/modules/python_builder.py`
4. [unknown](#unknown) - `build/modules/service_discovery_builder.py`
5. [unknown](#unknown) - `build/modules/polyglot_proto_engine.py`
6. [unknown](#unknown) - `build/modules/kotlin_builder.py`

## unknown

### Metadata

- **File**: `build/modules/typescript_builder.py`
- **Language**: python
- **Type**: `service.builder`

### Purpose

typescript/npm builds with webpack optimization and hot reloading

---

## unknown

### Metadata

- **File**: `build/modules/c_builder.py`
- **Language**: python
- **Type**: `service.builder`

### Purpose

c/c++ builds with cmake integration and SIMD optimization

### Rules & Constraints

⚠️ **Critical**: c builds must be deterministic and provide direct cpu instruction access

---

## unknown

### Metadata

- **File**: `build/modules/python_builder.py`
- **Language**: python
- **Type**: `service.builder`

### Purpose

python builds with virtual environment and dependency management

---

## unknown

### Metadata

- **File**: `build/modules/service_discovery_builder.py`
- **Language**: python
- **Type**: `service.builder`

### Purpose

service discovery registry generation from docker-compose and proto files

### Rules & Constraints

⚠️ **Critical**: service discovery must happen at build time for dashboard consistency

---

## unknown

### Metadata

- **File**: `build/modules/polyglot_proto_engine.py`
- **Language**: python
- **Type**: `service.builder`

### Purpose

polyglot protobuf client generation for multiple languages

---

## unknown

### Metadata

- **File**: `build/modules/kotlin_builder.py`
- **Language**: python
- **Type**: `service.builder`

### Purpose

kotlin/gradle builds with incremental compilation and parallel execution

### Rules & Constraints

⚠️ **Critical**: gradle builds must be deterministic and support incremental compilation

---

