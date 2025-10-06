# Unhinged Python Scripts

**Primary scripting language for the Unhinged monorepo automation**

## Philosophy

We follow the **Japanese approach to development**: taking time for intentional, high-quality work using precise "hand tools" rather than rushing with generic, scalable solutions. Our Python scripts are designed to be:

- **Reusable and well-understood** - Clear, maintainable code
- **LLM-oriented** - Comprehensive documentation for AI assistance
- **Precise tools** - Surgical solutions for specific problems
- **Quality-focused** - Intentional design over quick hacks

## Directory Structure

```
scripts/python/
├── __init__.py              # Script registry and package initialization
├── README.md               # This file
├── fix_theme_properties.py # Theme property access pattern fixes
└── [future scripts]        # Additional automation tools
```

## Script Categories

### 🎨 Theme and Design System
- `fix_theme_properties.py` - Fix theme property access patterns to match design system structure

### 🏗️ Build System (Planned)
- Build automation and orchestration
- Dependency management
- Asset processing

### 🧪 Development Workflow (Planned)
- Code generation and scaffolding
- Development environment setup
- Testing utilities

### 🚀 Deployment (Planned)
- Deployment automation
- Environment configuration
- Health checks and monitoring

## Usage

### Direct Execution
```bash
# Run script directly
python scripts/python/fix_theme_properties.py --dry-run

# With custom patterns
python scripts/python/fix_theme_properties.py --pattern 'old\.pattern' --replacement 'new.pattern'
```

### Via Build System
```bash
# List available Python scripts
./build list-scripts

# Run script through build system
./build fix_theme_properties

# With parameters
./build fix_theme_properties --dry-run true
```

## Documentation Standards

All Python scripts in this directory must follow these standards:

### 1. File Header
```python
#!/usr/bin/env python3
"""
Script Name - Brief Description

Detailed description of what the script does, following Japanese precision philosophy.

Usage:
    python scripts/python/script_name.py [options]
    
Examples:
    python scripts/python/script_name.py --example
    
Author: Unhinged Team
Version: X.Y.Z
Date: YYYY-MM-DD
"""
```

### 2. Docstring Standards
- Use Google-style docstrings
- Include Args, Returns, and Examples sections
- Provide clear type hints
- Document exceptions and edge cases

### 3. Function Documentation
```python
def process_files(root_dir: Path, pattern: str) -> List[Path]:
    """
    Process files matching a pattern in the given directory.
    
    Args:
        root_dir: Root directory to search
        pattern: Glob pattern to match files
        
    Returns:
        List of Path objects for matching files
        
    Raises:
        FileNotFoundError: If root_dir doesn't exist
        
    Examples:
        >>> files = process_files(Path("src"), "*.py")
        >>> len(files) > 0
        True
    """
```

### 4. Error Handling
- Use proper exception handling
- Provide meaningful error messages
- Include context in error reporting
- Fail gracefully with helpful guidance

### 5. CLI Interface
- Use argparse for command-line interfaces
- Provide help text and examples
- Support both interactive and automated usage
- Include dry-run options where appropriate

## Integration with Build System

Python scripts are registered in `__init__.py` and automatically available through the build system:

```python
PYTHON_SCRIPTS = {
    "script_name": {
        "path": "scripts/python/script_name.py",
        "description": "What the script does",
        "category": "theme|build|workflow|deployment",
        "usage": "python scripts/python/script_name.py [options]",
        "examples": ["example command 1", "example command 2"]
    }
}
```

## Legacy Shell Scripts

Shell scripts in the `scripts/` directory are maintained for backward compatibility but considered **legacy**. New automation should use Python unless there's a compelling reason to use shell scripting.

### Migration Strategy
1. **Keep existing shell scripts functional** - Don't break existing workflows
2. **Mark as legacy** - Document that they're not the preferred approach
3. **Gradual migration** - Convert to Python when practical
4. **New features in Python** - All new automation uses Python

## Development Guidelines

### Adding New Scripts

1. **Create the script** following documentation standards
2. **Register in `__init__.py`** with proper metadata
3. **Test thoroughly** with various inputs and edge cases
4. **Document usage** with clear examples
5. **Update this README** if adding new categories

### Code Quality

- **Type hints** - Use throughout for better LLM understanding
- **Error handling** - Comprehensive exception management
- **Logging** - Clear progress and error reporting
- **Testing** - Include doctest examples where appropriate
- **Performance** - Efficient algorithms and resource usage

### Japanese Precision Principles

- **Intentional design** - Think through the problem thoroughly
- **Quality over speed** - Take time to do it right
- **Reusable tools** - Build for multiple use cases
- **Clear documentation** - Make it understandable for future developers
- **Maintainable code** - Write code that can be easily modified

## Examples

### Theme Property Fix Script
```bash
# See what would be changed
python scripts/python/fix_theme_properties.py --dry-run

# Apply fixes to frontend directory
python scripts/python/fix_theme_properties.py

# Custom pattern replacement
python scripts/python/fix_theme_properties.py \
  --pattern 'theme\.old\.pattern' \
  --replacement 'theme.new.pattern'

# Generate detailed report
python scripts/python/fix_theme_properties.py --report results.json
```

## Future Enhancements

- **Script templates** - Boilerplate for new scripts
- **Testing framework** - Automated testing for scripts
- **Performance monitoring** - Track script execution times
- **Configuration management** - Centralized script configuration
- **Parallel execution** - Run multiple scripts concurrently

---

**Remember**: We build tools with Japanese precision - intentional, high-quality, and built to last. Every script should be a testament to thoughtful engineering.
