# Augment Agent Instructions for Unhinged Project

> *"If I have seen further it is by standing on the shoulders of Giants."* - Isaac Newton

## The Legend/Key/Map Philosophy

This monorepo operates on the **Legend/Key/Map** philosophy:

- **Legend** = Documentation that explains the territory (this file, README.md, docs/)
- **Key** = Tools that unlock capabilities (tools/ directory)
- **Map** = Structure that shows relationships (architecture, file organization)

Every file, function, and decision should serve as either a Legend, Key, or Map for future travelers (LLMs and humans alike).

## Project Overview - The Map
Unhinged is a full-stack monorepo application with the following architecture:
- **Backend**: Kotlin/Spring Boot application (port 8080) - The API fortress
- **Frontend**: TypeScript/React application (port 3000) - The user interface realm
- **Database**: PostgreSQL 15 (port 5432) - The data kingdom
- **LLM**: Ollama service (port 11434) - The intelligence oracle

### The Sacred Directory Structure
```
Unhinged/
├── .augment/           # Agent wisdom and configuration
├── tools/              # The Keys (utilities that unlock capabilities)
├── docs/               # The Legend (maps for understanding)
├── secrets/            # Environment files (git-ignored sanctuary)
├── backend/            # Kotlin realm
├── frontend/           # TypeScript realm
├── database/           # PostgreSQL realm
└── llm/                # Ollama realm
```

## Development Workflow

### Initial Setup
1. Ensure Docker, Node.js, and JVM are installed
2. Run `docker-compose up --build` from root directory
3. Run `npm install && npm start` from `/frontend` directory
4. Access application at `localhost:8081` (as per README)

### Code Standards & Practices - The Way

#### Documentation Philosophy (Legend Pattern)
All code must follow the **Legend/Key/Map** documentation pattern:

```typescript
/**
 * LEGEND: Brief description of what this does
 * KEY: The specific problem this solves
 * MAP: How this fits in the overall architecture
 *
 * @param param Description
 * @returns Description
 * @example Usage example
 */
```

```bash
#!/bin/bash
# LEGEND: What this tool accomplishes
# KEY: The specific problem it solves
# MAP: Where it fits in the workflow
```

#### Backend (Kotlin) - The API Fortress
- Follow Kotlin official style guide with Legend/Key/Map comments
- Use ktlint for linting
- Write tests with JUnit5 following documentation patterns
- Maintain clean architecture with clear domain boundaries
- Use dependency injection appropriately
- Every service/controller must have Legend/Key/Map documentation

#### Frontend (TypeScript/React) - The Interface Realm
- Follow TypeScript standard conventions with enhanced documentation
- Use ESLint for code quality
- Write tests with Jest following patterns
- Implement component library with Legend/Key/Map philosophy:
  - `<StackChildren />` - Layout key for vertical stacking
  - `<InlineChildren />` - Layout key for horizontal flow
  - `<MaxWidthChildren />` - Layout key for responsive containers
  - `<Modal />` - Interaction key for overlays
  - `<Toast />` - Feedback key for notifications
  - `<Tooltip />` - Information key for contextual help

#### Database - The Data Kingdom
- Design message and user persistence layer (first iteration priority)
- Use proper PostgreSQL conventions with clear schema documentation
- Implement migrations with Legend/Key/Map comments explaining purpose
- Every table/view must document its role in the data kingdom

### Key Priorities (from README TODO)
1. **First iteration of persistence layer**
   - Design message and user models
   - Implement database schema
   - Create repository/DAO layers

2. **Component library development**
   - Build reusable UI components
   - Ensure consistent styling and behavior
   - Document component APIs

### Development Guidelines
- Always use package managers (npm for frontend, gradle for backend)
- Test changes thoroughly before committing
- Maintain Docker compatibility
- Follow monorepo best practices
- Keep services loosely coupled
- Document API changes

### Testing Strategy
- Backend: `./gradlew test` from backend directory
- Frontend: `npm test` from frontend directory
- Integration: Use docker-compose for full stack testing

### Common Tasks
- **Adding dependencies**: Use appropriate package managers
- **Database changes**: Update schema and migrations
- **API changes**: Update both backend and frontend
- **New components**: Follow established patterns
- **LLM integration**: Use Ollama service at `http://llm:11434`

## Agent Behavior - The Way of the Code

### Core Principles
- **Stand on Giants' Shoulders**: Always check existing patterns before creating new ones
- **Respect the Realms**: Honor monorepo structure and component boundaries
- **Efficiency Through Parallelism**: Use parallel tool calls whenever possible
- **Wisdom Before Action**: Ask for clarification on architectural decisions
- **Test the Path**: Always suggest testing after code changes
- **Consistency is King**: Maintain established conventions religiously

### The Legend/Key/Map Approach
1. **Read the Legend** - Check documentation and existing patterns first
2. **Find the Right Key** - Use tools/ directory for common tasks
3. **Navigate the Map** - Understand how changes fit the architecture
4. **Document the Journey** - Leave clear trails for future travelers

### LLM-Agnostic Principles
- Write code and documentation that any LLM can parse and understand
- Use consistent patterns that create predictable behavior
- Structure information for maximum clarity and minimal ambiguity
- Build tools that are self-documenting and self-explanatory

### Wisdom Integration
Every Augment Agent instance is initialized with the philosophical essence of computer science through `.augment/essence-of-computer-science.llm`. This foundational wisdom from the giants of our field should inform every decision:

- **Code quality and craftsmanship** - "The best programs are written so that computing machines can perform them quickly and so that human beings can understand them clearly." - Donald Knuth
- **Problem-solving strategies** - "Simplicity is prerequisite for reliability." - Edsger Dijkstra
- **Innovation approach** - "It's easier to ask forgiveness than it is to get permission." - Grace Hopper
- **Collaboration principles** - "Talk is cheap. Show me the code." - Linus Torvalds

The `.llm` format represents our commitment to LLM-agnostic wisdom preservation - ensuring that the philosophical foundations of computer science remain accessible to any form of intelligence, mechanical or organic.

*"We can only see a short distance ahead, but we can see plenty there that needs to be done."* - Alan Turing
