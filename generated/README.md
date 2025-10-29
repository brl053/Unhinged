# Generated Directory

This directory contains **ALL** generated content from the build system.

## Philosophy: Generated Content is NOT Committed

**RULE:** Generated files are **NEVER** committed to version control.

### What Goes Here

- Protobuf generated clients (Python, TypeScript, Kotlin)
- Build artifacts and compiled outputs  
- Documentation generated from code
- Design system CSS/components
- Service discovery registries
- Any file created by the build system

### What's Committed

- **ONLY** this README.md and .gitkeep
- **NOTHING ELSE**

### Regeneration

All content in this directory can be regenerated with:

```bash
make generate
# or
python build/build.py build all
```

### Directory Structure

```
generated/
├── .gitkeep              # Preserves directory in git
├── README.md             # This file (explains philosophy)
├── c/                    # C library builds and CFFI bindings
├── design_system/        # Generated CSS and components
├── docs/                 # Generated documentation
├── javascript/           # Generated JS clients
├── kotlin/               # Generated Kotlin clients  
├── python/               # Generated Python clients
├── reports/              # Build reports and analysis
└── typescript/           # Generated TypeScript clients
```

**Remember: If it's generated, it doesn't belong in git.**
