# UNHINGED REPOSITORY - MASTER LLM PROMPT
# ============================================================================
# CRITICAL: READ THIS BEFORE MAKING ANY CHANGES TO THE CODEBASE
# ============================================================================
#
# @llm-type quickstart
# @llm-legend Master guidance for LLM agents working in the Unhinged monorepo
# @llm-key Prevents file creation chaos and enforces architectural patterns
# @llm-map Entry point for LLM agents to understand repo structure and constraints
# @llm-axiom All LLM agents must read and follow these patterns before making changes
# @llm-contract Provides comprehensive guidance on file creation, build patterns, and cultural commandments
# @llm-token llm-master-prompt: Essential guidance for AI agents working in Unhinged codebase

## 🚨 CULTURAL COMMANDMENTS - VIOLATION = IMMEDIATE FAILURE

### 1. INDEPENDENCE IS EVERYTHING
- **WE ARE INDEPENDENT** - No external browsers (Firefox, Chrome, Safari)
- **WE ARE SELF-CONTAINED** - Native rendering or nothing
- **WE ARE HEADLESS-FIRST** - GUI is optional, system is primary
- **WE FAIL FAST** - Better to break than compromise independence

### 2. CENTRALIZED BUILD PHILOSOPHY
- **ONE BUILD SYSTEM** - Everything goes through `/build/`
- **ONE PYTHON ENV** - Use `build/python/venv/` for ALL Python operations
- **NO SCATTERED TOOLS** - No gradle wrappers, no npm in random places
- **GENERATED CONTENT** - Everything generated goes to `/generated/`

### 3. FILE CREATION DISCIPLINE
- **NO FILES IN ROOT** - Root directory is sacred, use proper subdirectories
- **NO TEMP FILES** - Use `/generated/` for temporary artifacts
- **NO BACKUP FILES** - Use git, not `.backup` files
- **NO DEMO CRUFT** - Clean up after yourself

### 4. DOCUMENTATION DISCIPLINE - WE KISS DRYly
- **USE LLM-DOCS STANDARD** - All files use @llm-type, @llm-legend, @llm-key patterns
- **NO SCATTERED READMES** - Only root README.md exists, everything else in `/docs/`
- **LEVERAGE /docs** - Use existing documentation structure and tooling
- **USE /build/docs-generation** - Leverage existing doc generation system

### 5. PRIME DIRECTIVE - CONFIDENCE CHECK
- **CROSS-CHECK IMPLEMENTATION** - When confidence < 75% or generating artifacts, validate against this prompt
- **VERIFY PATTERNS** - Check your work against established repo patterns
- **USE EXISTING TOOLING** - Don't reinvent, use `/build/docs-generation` and `/docs/`

## 📁 DIRECTORY STRUCTURE - SACRED BOUNDARIES

```
/
├── build/              # CENTRALIZED BUILD SYSTEM (Python-based)
│   ├── python/         # Centralized Python environment
│   ├── modules/        # Language-specific builders
│   ├── docs-generation/# Documentation automation (USE THIS!)
│   └── tools/          # Build utilities
├── control/            # SYSTEM CONTROL & GUI
│   ├── native_gui/     # GTK4 native GUI (NO WEBKIT!)
│   ├── static_html/    # HTML interfaces (for native rendering)
│   └── system/         # System control abstractions
├── generated/          # ALL GENERATED CONTENT (EVERYTHING GOES HERE)
│   ├── typescript/     # Generated TS clients
│   ├── python/         # Generated Python clients
│   ├── static_html/    # Generated HTML assets
│   └── reports/        # Build reports and analysis
├── proto/              # Protocol buffer definitions
├── services/           # Microservices (Python AI services)
├── platforms/          # Platform services (Kotlin persistence)
├── docs/               # DOCUMENTATION (USE THIS, NOT READMES!)
├── llm/                # LLM-specific content
│   └── quickstart/     # LLM agent guidance (THIS FILE!)
└── README.md           # ONLY README - entry point to /docs/
```

## 🛠️ BUILD SYSTEM PATTERNS

### Python Operations
```bash
# CORRECT: Use centralized Python
python3 build/python/run.py script.py

# WRONG: Random Python environments
cd some_dir && python script.py
```

### File Generation
```bash
# CORRECT: Generate to proper location
python3 build/build.py build proto-clients-all
# Output: generated/typescript/clients/

# WRONG: Generate anywhere else
protoc --js_out=frontend/src/generated/
```

### Build Commands
```bash
# CORRECT: Use build system
make build              # Fast development build
make generate          # Generate all artifacts
python3 build/build.py build dev-fast

# WRONG: Direct tool invocation
cd backend && ./gradlew build
cd frontend && npm run build
```

## 🚫 FORBIDDEN PATTERNS

### File Creation Anti-Patterns
- ❌ Creating files in repository root
- ❌ Creating `.backup` or `.old` files
- ❌ Creating `demo_*` or `test_*` files in root
- ❌ Creating temporary scripts outside `/build/`
- ❌ Creating package.json files outside designated areas

### Build Anti-Patterns
- ❌ Using external browsers for GUI
- ❌ Installing npm packages globally
- ❌ Creating gradle wrapper scripts
- ❌ Using system package managers for build deps
- ❌ Creating Docker files outside service directories

### Code Anti-Patterns
- ❌ Hardcoded paths that don't respect build structure
- ❌ Direct tool invocation bypassing build system
- ❌ Creating services without proper proto definitions
- ❌ Bypassing the centralized Python environment

## ✅ REQUIRED PATTERNS

### Before Making Changes
1. **Check build system** - Use `make status` to understand current state
2. **Use centralized tools** - All Python through `build/python/`
3. **Generate properly** - All generated content to `/generated/`
4. **Test build** - Run `make build` to verify changes

### File Creation Rules
1. **Generated content** → `/generated/`
2. **Build scripts** → `/build/`
3. **Documentation** → `/docs/`
4. **Services** → `/services/` or `/platforms/`
5. **Control logic** → `/control/`

### Build Integration
1. **Add to build-config.yml** if creating new build targets
2. **Update .gitignore** for new generated content
3. **Use build modules** for language-specific operations
4. **Cache appropriately** using build system caching

## 🔧 COMMON OPERATIONS

### Adding a New Service
```bash
# 1. Create service directory
mkdir services/new-service

# 2. Add proto definition
vim proto/new_service.proto

# 3. Generate clients
make generate-clients

# 4. Update build config
vim build-config.yml
```

### Adding Build Functionality
```bash
# 1. Create build module
vim build/modules/new_builder.py

# 2. Register in orchestrator
vim build/orchestrator.py

# 3. Add to config
vim build-config.yml

# 4. Test
python3 build/build.py build new-target
```

## 🎯 SUCCESS CRITERIA

### For LLM Agents
- [ ] No files created in repository root
- [ ] All Python operations use centralized environment
- [ ] All generated content goes to `/generated/`
- [ ] Build system integration for new functionality
- [ ] Proper .gitignore updates for new content
- [ ] Documentation updates for new patterns

### For Build System
- [ ] Single command builds (`make build`)
- [ ] Proper caching and incremental builds
- [ ] Clear error messages and recovery
- [ ] Independence from external tools
- [ ] Reproducible across environments

## 🚨 EMERGENCY PROCEDURES

### If You Violate These Rules
1. **STOP IMMEDIATELY** - Don't compound the error
2. **Clean up** - Remove any files created in wrong locations
3. **Use proper patterns** - Follow the established structure
4. **Test thoroughly** - Ensure build system still works

### If Build System Breaks
1. **Check status** - `make status` and `python3 build/build.py status`
2. **Clean and rebuild** - `make clean && make build`
3. **Check dependencies** - Ensure centralized Python env is intact
4. **Consult documentation** - Check `/build/README.md`

## 📚 REFERENCE DOCUMENTATION

- `/build/README.md` - Build system overview
- `/build/TODO.md` - Build system roadmap
- `Makefile` - Available commands and patterns
- `build-config.yml` - Build targets and configuration
- `.gitignore` - What should and shouldn't be committed

---

**REMEMBER: This machine is everything. We depend on nothing external. We build everything ourselves. We are independent.**
