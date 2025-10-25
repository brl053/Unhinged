# 🤖 LLM Quickstart Guide

## Overview

This guide helps LLM agents quickly understand and contribute to the Unhinged codebase using the LlmDocs annotation system.

## LlmDocs Annotation System

All code uses structured annotations for AI comprehension:

```python
"""
@llm-type [component-type]
@llm-legend [high-level-purpose]
@llm-key [core-functionality]
@llm-map [architectural-position]
@llm-axiom [design-principles]
@llm-contract [interface-contracts]
@llm-token [searchable-identifier]
"""
```

## Quick Commands

- `make docs-update` - Regenerate all documentation
- `make docs-context-overview` - Generate LLM context
- `make docs-comments` - Extract LLM annotations
- `make context` - Generate AI context summary

## Architecture Overview

- **Native GUI**: C graphics-based desktop application
- **Voice Pipeline**: Native audio → Whisper → AI response
- **Service Architecture**: Docker + direct service integration
- **Build System**: Polyglot build with caching

## Getting Started

1. Run `make setup` for initial setup
2. Run `make start` for voice-first experience
3. Use `make docs-context-overview` for full context
4. Follow LlmDocs patterns for new code

## Key Principles

- **Independence**: Minimal external dependencies
- **Native-first**: OS capabilities over libraries
- **Voice-first**: Immediate voice interaction
- **LlmDocs**: Structured AI-readable annotations
