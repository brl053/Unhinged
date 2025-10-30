#!/usr/bin/env python3
"""
Unified Python Virtual Environment Setup

Consolidates all Python dependencies from scattered requirements.txt files
and creates a single virtual environment for the entire project.

Based on expert recommendation to eliminate dependency conflicts and
implement "One venv to rule them all" philosophy.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re

class UnifiedVenvManager:
    """Manages creation and maintenance of unified Python virtual environment."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.venv_path = project_root / ".venv"
        self.build_dir = project_root / "build"
        self.unified_requirements = self.build_dir / "requirements-unified.txt"
        
        # Requirements files to consolidate
        self.requirements_files = [
            "build/python/requirements.txt",
            "services/text-to-speech/requirements.txt", 
            "services/vision-ai/requirements.txt"
        ]
    
    def setup_unified_environment(self) -> bool:
        """Create unified virtual environment with consolidated dependencies."""
        print("🚀 Setting up unified Python virtual environment...")
        
        try:
            # Step 1: Consolidate requirements
            print("📋 Consolidating requirements from scattered files...")
            self._consolidate_requirements()
            
            # Step 2: Create virtual environment
            print("🔧 Creating virtual environment...")
            self._create_venv()
            
            # Step 3: Install dependencies
            print("📦 Installing consolidated dependencies...")
            self._install_dependencies()
            
            # Step 4: Install local packages
            print("🔗 Installing local event framework...")
            self._install_local_packages()
            
            # Step 5: Create activation script
            print("📝 Creating activation helpers...")
            self._create_activation_helpers()
            
            # Step 6: Update gitignore
            self._update_gitignore()
            
            print("✅ Unified Python environment ready!")
            print(f"   Virtual environment: {self.venv_path}")
            print(f"   Unified requirements: {self.unified_requirements}")
            print("\n🎯 To activate: source .venv/bin/activate")
            print("🎯 Or use: ./build/python/run.py <script.py>")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup unified environment: {e}")
            return False
    
    def _consolidate_requirements(self):
        """Consolidate all requirements.txt files into unified version."""
        all_deps = {}
        conflicts = []
        problematic_packages = set()

        for req_file in self.requirements_files:
            file_path = self.project_root / req_file
            if not file_path.exists():
                continue

            print(f"  📄 Processing {req_file}")
            deps = self._parse_requirements_file(file_path)

            for package, version in deps.items():
                # Skip packages known to have Python version conflicts
                if package in ['TTS', 'pyttsx3']:
                    problematic_packages.add(package)
                    print(f"    ⚠️  Skipping {package} (Python version constraints)")
                    continue

                if package in all_deps and all_deps[package] != version:
                    conflicts.append((package, all_deps[package], version, req_file))
                else:
                    all_deps[package] = version

        # Handle version conflicts by choosing latest compatible version
        if conflicts:
            print("⚠️  Resolving version conflicts:")
            for package, existing, new, source in conflicts:
                resolved = self._resolve_version_conflict(package, existing, new)
                all_deps[package] = resolved
                print(f"    {package}: {existing} vs {new} → {resolved}")

        # Remove duplicate numpy constraints
        if 'numpy>=1.24.0                 # Numerical computing' in all_deps and 'numpy<2.0.0' in all_deps:
            del all_deps['numpy>=1.24.0                 # Numerical computing']
            all_deps['numpy'] = '>=1.24.0,<2.0.0'

        # Write unified requirements
        self._write_unified_requirements(all_deps, problematic_packages)
    
    def _parse_requirements_file(self, file_path: Path) -> Dict[str, str]:
        """Parse requirements.txt file and extract package versions."""
        deps = {}
        
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Handle different version specifiers
                if '==' in line:
                    package, version = line.split('==', 1)
                    deps[package.strip()] = f"=={version.strip()}"
                elif '>=' in line:
                    package, version = line.split('>=', 1)
                    deps[package.strip()] = f">={version.strip()}"
                elif '>' in line:
                    package, version = line.split('>', 1)
                    deps[package.strip()] = f">{version.strip()}"
                else:
                    # Package without version specifier
                    deps[line.strip()] = ""
        
        return deps
    
    def _resolve_version_conflict(self, package: str, version1: str, version2: str) -> str:
        """Resolve version conflicts by choosing the more restrictive version."""
        # For exact versions (==), choose the newer one
        if version1.startswith('==') and version2.startswith('=='):
            v1 = version1[2:]
            v2 = version2[2:]
            # Simple version comparison - in production, use packaging.version
            if self._compare_versions(v1, v2) >= 0:
                return version1
            else:
                return version2
        
        # For mixed version types, prefer exact versions
        if version1.startswith('=='):
            return version1
        elif version2.startswith('=='):
            return version2
        
        # For range versions, use the more restrictive one
        return version1  # Default fallback
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Simple version comparison. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal."""
        # Split versions into parts and compare numerically
        parts1 = [int(x) for x in v1.split('.') if x.isdigit()]
        parts2 = [int(x) for x in v2.split('.') if x.isdigit()]
        
        # Pad shorter version with zeros
        max_len = max(len(parts1), len(parts2))
        parts1.extend([0] * (max_len - len(parts1)))
        parts2.extend([0] * (max_len - len(parts2)))
        
        for p1, p2 in zip(parts1, parts2):
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
        
        return 0
    
    def _write_unified_requirements(self, deps: Dict[str, str], problematic_packages: set):
        """Write consolidated dependencies to unified requirements file."""
        with open(self.unified_requirements, 'w') as f:
            f.write("# Unified Python Dependencies for Unhinged Platform\n")
            f.write("# Generated by build/setup-unified-venv.py\n")
            f.write("# DO NOT EDIT MANUALLY - Regenerate with setup script\n\n")

            if problematic_packages:
                f.write("# Packages skipped due to Python version constraints:\n")
                for pkg in sorted(problematic_packages):
                    f.write(f"# {pkg} - install manually if needed\n")
                f.write("\n")

            # Clean up package names and sort alphabetically
            clean_deps = {}
            for package, version in deps.items():
                # Remove inline comments from package names
                clean_package = package.split('#')[0].strip()
                if clean_package and not clean_package.startswith('#'):
                    clean_deps[clean_package] = version

            for package in sorted(clean_deps.keys()):
                version = clean_deps[package]
                f.write(f"{package}{version}\n")
    
    def _create_venv(self):
        """Create Python virtual environment."""
        if self.venv_path.exists():
            print(f"  🗑️  Removing existing venv at {self.venv_path}")
            shutil.rmtree(self.venv_path)
        
        # Create new virtual environment
        subprocess.run([
            sys.executable, "-m", "venv", str(self.venv_path)
        ], check=True)
    
    def _install_dependencies(self):
        """Install dependencies in virtual environment."""
        pip_path = self.venv_path / "bin" / "pip"
        
        # Upgrade pip first
        subprocess.run([
            str(pip_path), "install", "--upgrade", "pip"
        ], check=True)
        
        # Install from unified requirements
        subprocess.run([
            str(pip_path), "install", "-r", str(self.unified_requirements)
        ], check=True)
    
    def _install_local_packages(self):
        """Install local packages like the event framework."""
        pip_path = self.venv_path / "bin" / "pip"
        
        # Install event framework from local source
        event_framework_path = self.project_root / "libs" / "event-framework" / "python"
        if event_framework_path.exists():
            subprocess.run([
                str(pip_path), "install", "-e", str(event_framework_path)
            ], check=True)
            print("  ✅ Installed local event framework")
    
    def _create_activation_helpers(self):
        """Create helper scripts for environment activation."""
        # Update the existing run.py script
        run_script = self.build_dir / "python" / "run.py"
        if run_script.exists():
            # Update to use unified venv
            with open(run_script, 'r') as f:
                content = f.read()
            
            # Replace venv path references
            content = content.replace(
                'build/python/venv',
                '.venv'
            )
            
            with open(run_script, 'w') as f:
                f.write(content)
    
    def _update_gitignore(self):
        """Update .gitignore to exclude unified venv."""
        gitignore_path = self.project_root / ".gitignore"
        
        venv_entries = [".venv/", ".venv/*", "build/requirements-unified.txt"]
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                existing = f.read()
            
            # Add entries if not already present
            new_entries = []
            for entry in venv_entries:
                if entry not in existing:
                    new_entries.append(entry)
            
            if new_entries:
                with open(gitignore_path, 'a') as f:
                    f.write("\n# Unified Python Virtual Environment\n")
                    for entry in new_entries:
                        f.write(f"{entry}\n")

def main():
    """Main setup function."""
    project_root = Path(__file__).parent.parent
    manager = UnifiedVenvManager(project_root)
    
    success = manager.setup_unified_environment()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
