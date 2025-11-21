#!/bin/bash
#
# @llm-type build.script
# @llm-does install quality gate enforcement as Git pre-commit hook
#
# This script installs the quality gate enforcement system that CANNOT be bypassed.
# It replaces the standard pre-commit hook with our custom enforcement.
#
# Usage:
#   ./scripts/install_quality_gates.sh

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"
PRE_COMMIT_HOOK="$GIT_HOOKS_DIR/pre-commit"

echo "=================================="
echo "Installing Quality Gate Enforcement"
echo "=================================="
echo ""

# Create hooks directory if it doesn't exist
mkdir -p "$GIT_HOOKS_DIR"

# Create the pre-commit hook
cat > "$PRE_COMMIT_HOOK" << 'EOF'
#!/bin/bash
#
# Unhinged Quality Gate Enforcement
# This hook CANNOT be bypassed with SKIP or --no-verify
#
# If you try to bypass this hook, the commit will fail.
# Fix the issues instead of bypassing quality gates.

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"

# Check for --no-verify bypass attempt
if [[ "$*" == *"--no-verify"* ]]; then
    echo ""
    echo "=================================="
    echo "🚫 --no-verify DETECTED"
    echo "=================================="
    echo ""
    echo "You attempted to bypass quality gates with --no-verify"
    echo ""
    echo "WHY THIS IS BLOCKED:"
    echo "Quality gates prevent technical debt and ensure code quality."
    echo ""
    echo "WHAT TO DO:"
    echo "1. Remove --no-verify from your git commit command"
    echo "2. Fix the quality gate failures"
    echo "3. Commit normally"
    echo ""
    exit 1
fi

# Check for SKIP environment variable
if [[ -n "$SKIP" ]]; then
    echo ""
    echo "=================================="
    echo "🚫 SKIP DETECTED: $SKIP"
    echo "=================================="
    echo ""
    echo "You attempted to bypass quality gates with SKIP"
    echo ""
    echo "WHY THIS IS BLOCKED:"
    echo "Quality gates prevent technical debt and ensure code quality."
    echo ""
    echo "WHAT TO DO:"
    echo "1. Remove SKIP from your environment"
    echo "2. Fix the quality gate failures"
    echo "3. Commit normally"
    echo ""
    exit 1
fi

# Run quality gate enforcement
echo ""
echo "Running quality gate enforcement..."
echo ""

python3 "$REPO_ROOT/libs/python/drivers/git/quality_gates.py"
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "=================================="
    echo "❌ COMMIT BLOCKED"
    echo "=================================="
    echo ""
    echo "Quality gates failed. Fix the issues above and commit again."
    echo ""
    echo "DO NOT attempt to bypass with SKIP or --no-verify"
    echo ""
    exit 1
fi

echo ""
echo "✅ Quality gates passed. Proceeding with commit."
echo ""
exit 0
EOF

# Make the hook executable
chmod +x "$PRE_COMMIT_HOOK"

echo "✅ Quality gate enforcement installed"
echo ""
echo "Location: $PRE_COMMIT_HOOK"
echo ""
echo "IMPORTANT:"
echo "- This hook CANNOT be bypassed with SKIP or --no-verify"
echo "- All commits must pass quality gates"
echo "- Fix issues instead of bypassing checks"
echo ""
echo "To verify installation:"
echo "  cat $PRE_COMMIT_HOOK"
echo ""

