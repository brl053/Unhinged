#!/bin/bash
#
# @llm-type build.script
# @llm-does install quality gate enforcement via Git config
#
# This script configures Git to use the centralized hooks in libs/python/drivers/git/hooks
#
# Usage:
#   ./scripts/install_quality_gates.sh

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=================================="
echo "Installing Quality Gate Enforcement"
echo "=================================="
echo ""

# Configure Git to use centralized hooks directory
cd "$REPO_ROOT"
git config --local core.hooksPath libs/python/drivers/git/hooks

echo "✅ Git configured to use centralized hooks"
echo ""
echo "Hooks directory: libs/python/drivers/git/hooks"
echo "Configuration: git config --local core.hooksPath"
echo ""
echo "Verification:"
git config --local --get core.hooksPath
echo ""

exit 0

# OLD APPROACH - DEPRECATED
# This was creating hooks in .git/hooks/ which is not version controlled
# New approach uses git config core.hooksPath to point to version-controlled hooks
cat > /dev/null << 'EOF'
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

