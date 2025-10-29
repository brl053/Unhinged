#!/usr/bin/env python3
"""
Documentation Watch and Update System

This script monitors key files for changes and automatically updates
documentation when changes are detected. It creates a continuous
documentation update loop.
"""

import os
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Set
import subprocess

class DocumentationWatcher:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.watch_files = {
            "Makefile": "makefile",
            "docker-compose.yml": "structure",
            "docker-compose.simple.yml": "structure",
            "package.json": "structure",
            "backend/build.gradle.kts": "structure",
            "proto/*.proto": "api",
            "services/*/README.md": "services",
            "services/*/Dockerfile": "services"
        }
        self.file_hashes = {}
        self.last_update = None
        
    def start_watching(self, interval: int = 30):
        """Start watching for file changes"""
        print("🔍 Starting documentation watch system...")
        print(f"📁 Watching: {self.root_path}")
        print(f"⏰ Check interval: {interval} seconds")
        print("")
        
        # Initial scan
        self._scan_files()
        print(f"📊 Monitoring {len(self.file_hashes)} files")
        print("")
        
        try:
            while True:
                if self._check_for_changes():
                    print(f"🔄 Changes detected at {datetime.now().strftime('%H:%M:%S')}")
                    self._update_documentation()
                    self._scan_files()  # Rescan after update
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Documentation watcher stopped")
    
    def _scan_files(self):
        """Scan all watched files and compute hashes"""
        new_hashes = {}
        
        for pattern, doc_type in self.watch_files.items():
            if '*' in pattern:
                # Handle glob patterns
                for file_path in self.root_path.glob(pattern):
                    if file_path.is_file():
                        hash_value = self._compute_file_hash(file_path)
                        new_hashes[str(file_path)] = hash_value
            else:
                # Handle specific files
                file_path = self.root_path / pattern
                if file_path.exists():
                    hash_value = self._compute_file_hash(file_path)
                    new_hashes[str(file_path)] = hash_value
        
        self.file_hashes = new_hashes
    
    def _check_for_changes(self) -> bool:
        """Check if any watched files have changed"""
        current_hashes = {}
        
        for pattern, doc_type in self.watch_files.items():
            if '*' in pattern:
                for file_path in self.root_path.glob(pattern):
                    if file_path.is_file():
                        hash_value = self._compute_file_hash(file_path)
                        current_hashes[str(file_path)] = hash_value
            else:
                file_path = self.root_path / pattern
                if file_path.exists():
                    hash_value = self._compute_file_hash(file_path)
                    current_hashes[str(file_path)] = hash_value
        
        # Check for changes
        changed_files = []
        for file_path, current_hash in current_hashes.items():
            if file_path not in self.file_hashes or self.file_hashes[file_path] != current_hash:
                changed_files.append(file_path)
        
        # Check for deleted files
        for file_path in self.file_hashes:
            if file_path not in current_hashes:
                changed_files.append(f"{file_path} (deleted)")
        
        if changed_files:
            print("📝 Changed files:")
            for file_path in changed_files:
                print(f"  - {file_path}")
            return True
        
        return False
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _update_documentation(self):
        """Update documentation using the master update script"""
        try:
            print("🚀 Updating documentation...")
            
            update_script = self.root_path / "scripts" / "docs" / "update-all-docs.py"
            if not update_script.exists():
                print("❌ Update script not found")
                return
            
            result = subprocess.run([
                sys.executable, str(update_script)
            ], capture_output=True, text=True, cwd=self.root_path)
            
            if result.returncode == 0:
                print("✅ Documentation updated successfully")
                self.last_update = datetime.now()
            else:
                print(f"❌ Documentation update failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error updating documentation: {e}")

class CIIntegration:
    """CI/CD integration for documentation updates"""
    
    @staticmethod
    def generate_github_workflow():
        """Generate GitHub Actions workflow for documentation updates"""
        workflow_content = """name: 📚 Update Documentation

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'Makefile'
      - 'docker-compose*.yml'
      - 'package.json'
      - 'backend/build.gradle.kts'
      - 'proto/**/*.proto'
      - 'services/**/README.md'
      - 'services/**/Dockerfile'
  
  pull_request:
    branches: [ main ]
    paths:
      - 'Makefile'
      - 'docker-compose*.yml'
      - 'package.json'
      - 'backend/build.gradle.kts'
      - 'proto/**/*.proto'
      - 'services/**/README.md'
      - 'services/**/Dockerfile'

jobs:
  update-docs:
    runs-on: ubuntu-latest
    
    steps:
    - name: 📥 Checkout code
      uses: actions/checkout@v4
      
    - name: 🐍 Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: 📚 Update documentation
      run: |
        chmod +x scripts/docs/*.py
        make docs-update
        
    - name: 🔍 Check for changes
      id: verify-changed-files
      run: |
        if [ -n "$(git status --porcelain)" ]; then
          echo "changed=true" >> $GITHUB_OUTPUT
        else
          echo "changed=false" >> $GITHUB_OUTPUT
        fi
        
    - name: 📝 Commit documentation updates
      if: steps.verify-changed-files.outputs.changed == 'true'
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add docs/
        git commit -m "📚 Auto-update documentation [skip ci]" || exit 0
        
    - name: 🚀 Push changes
      if: steps.verify-changed-files.outputs.changed == 'true'
      uses: ad-m/github-push-action@master
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        branch: ${{ github.ref }}
"""
        
        workflow_dir = Path(".github/workflows")
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_file = workflow_dir / "update-documentation.yml"
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
        
        print(f"✅ Generated GitHub workflow: {workflow_file}")
    
    @staticmethod
    def generate_pre_commit_hook():
        """Generate pre-commit hook for documentation validation"""
        hook_content = """#!/bin/bash
# Pre-commit hook to validate documentation

echo "🔍 Validating documentation..."

# Check if documentation is up to date
if ! make docs-validate; then
    echo "❌ Documentation validation failed"
    echo "💡 Run 'make docs-update' to fix documentation"
    exit 1
fi

echo "✅ Documentation validation passed"
exit 0
"""
        
        hooks_dir = Path(".git/hooks")
        if hooks_dir.exists():
            hook_file = hooks_dir / "pre-commit"
            with open(hook_file, 'w') as f:
                f.write(hook_content)
            
            # Make executable
            os.chmod(hook_file, 0o755)
            print(f"✅ Generated pre-commit hook: {hook_file}")
        else:
            print("⚠️ .git/hooks directory not found, skipping pre-commit hook")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "watch":
            # Start watching for changes
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            watcher = DocumentationWatcher()
            watcher.start_watching(interval)
            
        elif command == "ci-setup":
            # Set up CI integration
            print("🔧 Setting up CI integration...")
            CIIntegration.generate_github_workflow()
            CIIntegration.generate_pre_commit_hook()
            print("✅ CI integration setup complete")
            
        elif command == "validate":
            # Validate documentation
            from update_all_docs import DocumentationUpdater
            updater = DocumentationUpdater()
            success = updater._validate_docs()
            sys.exit(0 if success else 1)
            
        else:
            print(f"❌ Unknown command: {command}")
            print("Usage: python3 watch-and-update.py [watch|ci-setup|validate]")
            sys.exit(1)
    else:
        print("📚 Documentation Update Loop System")
        print("")
        print("Available commands:")
        print("  watch [interval]  - Watch for changes and update docs")
        print("  ci-setup         - Set up CI/CD integration")
        print("  validate         - Validate documentation")
        print("")
        print("Examples:")
        print("  python3 watch-and-update.py watch 60")
        print("  python3 watch-and-update.py ci-setup")

if __name__ == "__main__":
    main()
