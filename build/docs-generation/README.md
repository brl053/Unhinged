# 🤖 Documentation Automation Scripts

> **Purpose**: Python scripts that automatically generate and maintain project documentation
> **Location**: These are code generators, not documentation content
> **Output**: Generated documentation goes to `/docs/` directory

## 📋 Script Index

### Core Generators

#### `generate-makefile-docs.py`
**Purpose**: Analyzes the Makefile and generates comprehensive command reference
**Input**: `Makefile` (root directory)
**Output**: `docs/development/makefile-reference.md`
**Usage**: `python3 generate-makefile-docs.py`
**Features**:
- Extracts all Make targets with descriptions
- Categorizes commands by function
- Documents dependencies and usage patterns
- Generates quick reference tables

#### `generate-project-structure.py`
**Purpose**: Scans codebase and generates project structure documentation
**Input**: Entire project directory structure
**Output**: `docs/development/project-structure.md`
**Usage**: `python3 generate-project-structure.py`
**Features**:
- Analyzes directory organization
- Counts files by type
- Identifies services and components
- Documents key configuration files

#### `update-all-docs.py`
**Purpose**: Master orchestration script that runs all generators
**Input**: Various project files
**Output**: Multiple documentation files in `/docs/`
**Usage**: `python3 update-all-docs.py` or `make docs-update`
**Features**:
- Runs all documentation generators
- Validates generated content
- Creates update summary
- Handles error reporting

#### `watch-and-update.py`
**Purpose**: Monitors files for changes and triggers documentation updates
**Input**: Key project files (Makefile, docker-compose.yml, etc.)
**Output**: Triggers `update-all-docs.py` when changes detected
**Usage**: `python3 watch-and-update.py watch` or `make docs-watch`
**Features**:
- File change detection using SHA256 hashes
- Configurable watch intervals
- CI/CD integration setup
- Pre-commit hook generation

## 🔄 How It Works

### File Monitoring
The watch system monitors these key files:
```python
watch_files = {
    "Makefile": "makefile",                    # Command changes
    "docker-compose.yml": "structure",         # Service changes  
    "docker-compose.simple.yml": "structure",  # Service changes
    "package.json": "structure",               # Dependencies
    "backend/build.gradle.kts": "structure",   # Build config
    "proto/*.proto": "api",                    # API definitions
    "services/*/README.md": "services",        # Service docs
    "services/*/Dockerfile": "services"        # Service configs
}
```

### Update Trigger Flow
1. **File Change Detected** → Hash comparison identifies changes
2. **Update Triggered** → Runs `update-all-docs.py`
3. **Documentation Generated** → All relevant docs updated
4. **Validation** → Checks for consistency and completeness
5. **Summary Created** → `docs/LAST_UPDATE.md` updated

### Integration Points
- **Make targets** → `make docs-*` commands call these scripts
- **CI/CD** → GitHub Actions workflow generated
- **Pre-commit** → Git hooks for validation
- **Development** → Watch mode for continuous updates

## 🛠️ Development

### Adding New Generators
1. Create new Python script in this directory
2. Follow the pattern of existing generators
3. Add to `update-all-docs.py` orchestration
4. Add corresponding Make target in `Makefile`
5. Update this README

### Script Dependencies
- **Python 3.11+** - Required runtime
- **pathlib** - File system operations
- **subprocess** - Running external commands
- **hashlib** - File change detection
- **datetime** - Timestamps and logging

### Testing Scripts
```bash
# Test individual generators
python3 generate-makefile-docs.py
python3 generate-project-structure.py

# Test full update
python3 update-all-docs.py

# Test watch system (Ctrl+C to stop)
python3 watch-and-update.py watch 10
```

## 📁 Output Structure

These scripts generate documentation in `/docs/`:

```
/docs/
├── development/
│   ├── makefile-reference.md      # From generate-makefile-docs.py
│   └── project-structure.md       # From generate-project-structure.py
├── api/
│   └── generated-api-reference.md # From update-all-docs.py
├── services/
│   └── overview.md                # From update-all-docs.py
└── LAST_UPDATE.md                 # From update-all-docs.py
```

## 🔧 Configuration

### Watch Intervals
Default: 30 seconds
```bash
# Custom interval
make docs-watch INTERVAL=60
python3 watch-and-update.py watch 60
```

### File Patterns
Modify `watch_files` dictionary in `watch-and-update.py` to add new monitored files.

### Output Paths
Modify output paths in individual generator scripts to change where documentation is written.

---

**Note**: These are automation scripts, not documentation content. The actual documentation they generate is located in the `/docs/` directory.
