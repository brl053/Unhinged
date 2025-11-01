# Expert Review Request: DAG Execution System Design

**Date:** October 31, 2025  
**Subject:** Technical Review Request - Minimal DAG System Architecture  
**Project:** Unhinged Voice-First AI Platform  

---

Dear Technical Expert,

We are writing to request your professional guidance on the architectural design of a DAG (Directed Acyclic Graph) execution system for the Unhinged project. Your expertise would be invaluable in ensuring we pursue an appropriately scoped and well-designed solution.

## System Context

The Unhinged project is a voice-first AI control center that orchestrates complex workflows involving speech-to-text processing, LLM interactions, image generation, and other AI/ML services. We need a DAG execution system to coordinate these workflows, where users can define processing pipelines that might include:

- Voice input → Speech-to-text → LLM processing → Text-to-speech output
- Image analysis → Content generation → Multi-modal response workflows
- Conditional branching based on AI service outputs
- Parallel processing of multiple AI tasks

The system must handle both user-defined workflows and dynamically generated workflows created by the LLM itself.

## Core Requirements

We believe a minimal DAG system requires exactly three fundamental objects:

1. **Node** - Represents a computation unit (AI service call, data transformation, etc.)
2. **Edge** - Represents data flow and dependencies between nodes
3. **Graph/DAG** - Represents the complete workflow definition

## Request for Validation

**Primary Question:** Are we over-engineering this solution, or is our approach appropriately minimal?

We have developed a comprehensive protobuf schema with extensive configuration options, multiple node types, complex edge semantics, and detailed execution state tracking. However, we're concerned we may have created unnecessary complexity for what should be a straightforward system.

## Specific Guidance Needed

We would greatly appreciate your expert opinion on:

### 1. Essential Fields for Core Objects

**For a Node, what are the absolute minimum required fields?**
- Node ID and name?
- Node type/configuration?
- Input/output port definitions?
- Execution parameters?

**For an Edge, what is truly essential?**
- Source and target node references?
- Data type information?
- Conditional routing logic?

**For a Graph/DAG, what must be included?**
- Node and edge collections?
- Execution configuration?
- Metadata and versioning?

### 2. Required vs. Nice-to-Have Features

Which of these capabilities are essential for an initial implementation versus features that could be added later?

- **Execution State Tracking:** Real-time monitoring of node execution status
- **Retry Logic:** Automatic retry of failed nodes with backoff strategies  
- **Conditional Branching:** Routing based on node output conditions
- **Parallel Execution:** Concurrent execution of independent nodes
- **Resource Management:** Memory/CPU limits and scheduling constraints
- **Checkpointing:** Ability to resume failed executions from intermediate states
- **Data Transformation:** Edge-level data mapping and filtering
- **Metrics Collection:** Performance and cost tracking
- **Schema Validation:** Input/output data validation

### 3. Architectural Approach

**Is our protobuf schema approach sound for this use case?**

We chose Protocol Buffers for:
- Strong typing and schema evolution
- Multi-language code generation
- JSON serialization for document storage
- Integration with existing Unhinged services

**Alternative approaches we considered:**
- Simple JSON schema with runtime validation
- Domain-specific language (DSL) with custom parser
- YAML-based configuration with minimal structure

**Should we consider a simpler data model?** Perhaps starting with basic JSON objects and evolving toward more sophisticated schemas as requirements become clearer?

## Specific Technical Concerns

1. **Complexity vs. Usability:** Have we created a system that's too complex for typical voice-first AI workflows?

2. **Implementation Burden:** Will the comprehensive schema create excessive development overhead for basic use cases?

3. **Evolution Path:** Is there a simpler starting point that could naturally evolve into a more sophisticated system?

4. **Performance Implications:** Are we introducing unnecessary overhead with extensive metadata and state tracking?

## Request for Recommendation

Based on your experience with workflow systems and distributed computing, what would you recommend as the absolute minimum viable DAG system for our use case?

We would be grateful for:
- A critique of our current approach
- Recommendations for simplification
- Identification of truly essential vs. optional features
- Guidance on appropriate implementation phases

Your expert perspective would help ensure we build a system that is both powerful enough for our needs and simple enough to implement and maintain effectively.

Thank you for considering our request. We would be happy to provide additional technical details or answer any questions about the Unhinged project context.

Respectfully,

**The Unhinged Development Team**

---

**Attachments:**
- Current protobuf schema: `proto/graph.proto`
- Project architecture overview: `README.md`
- Existing service patterns: `proto/common.proto`
