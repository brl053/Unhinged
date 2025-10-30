#!/bin/bash

echo "🔧 Installing Git hooks for static analysis..."

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

echo "🔍 Running static analysis on staged Python files..."

# Get list of staged Python files
STAGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -z "$STAGED_PY_FILES" ]; then
    echo "ℹ️  No Python files staged, skipping static analysis"
    exit 0
fi

# Find project root
PROJECT_ROOT=$(git rev-parse --show-toplevel)
cd "$PROJECT_ROOT"

# Check if static analysis manager exists
if [ ! -f "build/static_analysis_manager.py" ]; then
    echo "⚠️  Static analysis manager not found, skipping analysis"
    exit 0
fi

# Find Python executable - prioritize venv-production
PYTHON_CMD=""
if [ -f "venv-production/bin/python" ]; then
    PYTHON_CMD="./venv-production/bin/python"
else
    echo "❌ venv-production not found - run 'make setup-python' first"
    exit 1
fi

# Determine modules to check based on staged files
MODULES_TO_CHECK=""
for file in $STAGED_PY_FILES; do
    if [[ $file == control/gtk4_gui/* ]]; then
        MODULES_TO_CHECK="$MODULES_TO_CHECK control/gtk4_gui"
    elif [[ $file == libs/python/* ]]; then
        MODULES_TO_CHECK="$MODULES_TO_CHECK libs/python"
    elif [[ $file == services/* ]]; then
        MODULES_TO_CHECK="$MODULES_TO_CHECK services"
    fi
done

# Remove duplicates
MODULES_TO_CHECK=$(echo $MODULES_TO_CHECK | tr ' ' '\n' | sort -u | tr '\n' ' ')

if [ -z "$MODULES_TO_CHECK" ]; then
    echo "ℹ️  No modules to check, skipping static analysis"
    exit 0
fi

echo "📁 Checking modules: $MODULES_TO_CHECK"

# Run static analysis
$PYTHON_CMD build/static_analysis_manager.py $MODULES_TO_CHECK

ANALYSIS_EXIT_CODE=$?

if [ $ANALYSIS_EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ Static analysis failed!"
    echo "   Fix the issues above or use 'git commit --no-verify' to skip checks"
    echo ""
    echo "💡 To auto-fix many issues, run:"
    echo "   $PYTHON_CMD build/static_analysis_manager.py $MODULES_TO_CHECK"
    echo ""
    exit 1
fi

echo "✅ Static analysis passed!"
exit 0
EOF

# Make pre-commit hook executable
chmod +x .git/hooks/pre-commit

# Create post-commit hook to update checksums
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash

# Find project root
PROJECT_ROOT=$(git rev-parse --show-toplevel)
cd "$PROJECT_ROOT"

# Check if checksum manager exists
if [ ! -f "build/checksum_manager.py" ]; then
    exit 0
fi

# Find Python executable - use venv-production
PYTHON_CMD=""
if [ -f "venv-production/bin/python" ]; then
    PYTHON_CMD="./venv-production/bin/python"
else
    exit 0
fi

# Update checksums for committed Python files
COMMITTED_PY_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD | grep '\.py$')

if [ ! -z "$COMMITTED_PY_FILES" ]; then
    echo "💾 Updating checksums for committed Python files..."
    
    # Determine modules to update
    MODULES_TO_UPDATE=""
    for file in $COMMITTED_PY_FILES; do
        if [[ $file == control/gtk4_gui/* ]]; then
            MODULES_TO_UPDATE="$MODULES_TO_UPDATE control/gtk4_gui"
        elif [[ $file == libs/python/* ]]; then
            MODULES_TO_UPDATE="$MODULES_TO_UPDATE libs/python"
        elif [[ $file == services/* ]]; then
            MODULES_TO_UPDATE="$MODULES_TO_UPDATE services"
        fi
    done
    
    # Remove duplicates and update checksums
    MODULES_TO_UPDATE=$(echo $MODULES_TO_UPDATE | tr ' ' '\n' | sort -u | tr '\n' ' ')
    
    for module in $MODULES_TO_UPDATE; do
        $PYTHON_CMD -c "
from build.checksum_manager import ChecksumManager
cm = ChecksumManager()
cm.update_checksums('$module')
print('✅ Updated checksums for $module')
"
    done
fi
EOF

# Make post-commit hook executable
chmod +x .git/hooks/post-commit

echo "✅ Git hooks installed successfully!"
echo ""
echo "📋 Installed hooks:"
echo "   • pre-commit: Runs static analysis on staged Python files"
echo "   • post-commit: Updates checksums for committed files"
echo ""
echo "💡 To test the pre-commit hook:"
echo "   git add some_file.py"
echo "   git commit -m 'test commit'"
echo ""
echo "🚫 To skip static analysis for a commit:"
echo "   git commit --no-verify -m 'skip analysis'"
