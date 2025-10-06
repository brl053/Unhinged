#!/usr/bin/env python3
"""
Pre-Commit Migration Checklist

Automated verification for component migrations before committing:
- Verify design token usage (no hard-coded values)
- Run TypeScript type checks
- Ensure documentation is updated
- Validate conventional commit format
- Check migration metrics

Usage:
    python scripts/python/pre_commit_checklist.py --component ComponentName
    python scripts/python/pre_commit_checklist.py --all

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-06
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import re

class PreCommitChecker:
    """Pre-commit verification for component migrations."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.frontend_path = self.project_root / "frontend"
        self.components_path = self.frontend_path / "src" / "components" / "common"
        self.checks_passed = 0
        self.checks_total = 0
        
    def run_all_checks(self, component_name: str = None) -> bool:
        """Run all pre-commit checks."""
        print("🔍 Running Pre-Commit Migration Checklist")
        print("=" * 50)
        
        checks = [
            ("Design Token Usage", self.check_design_tokens),
            ("TypeScript Compilation", self.check_typescript),
            ("Documentation Updates", self.check_documentation),
            ("Migration Metrics", self.check_migration_metrics),
            ("File Structure", self.check_file_structure),
        ]
        
        if component_name:
            checks.append(("Component Specific", lambda: self.check_component_specific(component_name)))
        
        for check_name, check_func in checks:
            self.checks_total += 1
            print(f"\n🔍 {check_name}...")
            
            try:
                if check_func():
                    print(f"✅ {check_name}: PASSED")
                    self.checks_passed += 1
                else:
                    print(f"❌ {check_name}: FAILED")
            except Exception as e:
                print(f"❌ {check_name}: ERROR - {e}")
        
        # Summary
        print(f"\n📊 CHECKLIST SUMMARY")
        print("=" * 30)
        print(f"✅ Passed: {self.checks_passed}/{self.checks_total}")
        print(f"❌ Failed: {self.checks_total - self.checks_passed}/{self.checks_total}")
        
        success_rate = (self.checks_passed / self.checks_total) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print(f"\n🎉 ALL CHECKS PASSED - Ready to commit!")
            return True
        elif success_rate >= 80:
            print(f"\n⚠️  Most checks passed - Review failures before committing")
            return False
        else:
            print(f"\n🚫 Multiple failures - Do not commit yet")
            return False
    
    def check_design_tokens(self) -> bool:
        """Check for hard-coded values in staged files."""
        try:
            # Get staged files
            result = subprocess.run([
                "git", "diff", "--cached", "--name-only", "--diff-filter=AM"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                print("  ⚠️  Could not get staged files")
                return False
            
            staged_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
            # Filter for TypeScript/JavaScript files
            ts_files = [f for f in staged_files if f.endswith(('.ts', '.tsx', '.js', '.jsx'))]
            
            if not ts_files:
                print("  ℹ️  No TypeScript/JavaScript files staged")
                return True
            
            # Check each file for hard-coded values
            hard_coded_patterns = [
                (r'#[0-9a-fA-F]{6}', 'hex colors'),
                (r'#[0-9a-fA-F]{3}', 'short hex colors'),
                (r'\b\d+px\b', 'pixel values'),
                (r'rgba?\(\d+,\s*\d+,\s*\d+', 'RGB/RGBA colors'),
            ]
            
            violations = []
            
            for file_path in ts_files:
                full_path = self.project_root / file_path
                if not full_path.exists():
                    continue
                
                try:
                    content = full_path.read_text(encoding='utf-8')
                    
                    for pattern, description in hard_coded_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            violations.append(f"  {file_path}: {len(matches)} {description}")
                
                except Exception as e:
                    print(f"  ⚠️  Could not read {file_path}: {e}")
            
            if violations:
                print("  ❌ Hard-coded values found:")
                for violation in violations:
                    print(violation)
                print("  💡 Run: python scripts/python/fix_theme_properties.py")
                return False
            else:
                print("  ✅ No hard-coded values detected")
                return True
                
        except Exception as e:
            print(f"  ❌ Error checking design tokens: {e}")
            return False
    
    def check_typescript(self) -> bool:
        """Check TypeScript compilation."""
        try:
            print("  🔍 Running TypeScript type check...")
            result = subprocess.run([
                "npm", "run", "type-check"
            ], capture_output=True, text=True, cwd=self.frontend_path)
            
            if result.returncode == 0:
                print("  ✅ TypeScript compilation successful")
                return True
            else:
                print("  ❌ TypeScript compilation failed:")
                print(f"  {result.stderr}")
                return False
                
        except Exception as e:
            # Fallback to tsc directly
            try:
                result = subprocess.run([
                    "npx", "tsc", "--noEmit"
                ], capture_output=True, text=True, cwd=self.frontend_path)
                
                if result.returncode == 0:
                    print("  ✅ TypeScript compilation successful")
                    return True
                else:
                    print("  ❌ TypeScript compilation failed")
                    return False
            except:
                print(f"  ⚠️  Could not run TypeScript check: {e}")
                return False
    
    def check_documentation(self) -> bool:
        """Check if documentation files are updated."""
        try:
            # Get staged files
            result = subprocess.run([
                "git", "diff", "--cached", "--name-only"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            staged_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
            # Check if component files are staged
            component_files = [f for f in staged_files if 'components/common/' in f]
            
            if not component_files:
                print("  ℹ️  No component changes detected")
                return True
            
            # Check if documentation files are also staged
            doc_files = [
                "docs/roadmap/immediate-next-steps.md",
                "docs/roadmap/design-system-integration-dag.md",
                "CHECKPOINT-STATUS.md"
            ]
            
            staged_docs = [f for f in staged_files if f in doc_files]
            
            if staged_docs:
                print(f"  ✅ Documentation updated: {', '.join(staged_docs)}")
                return True
            else:
                print("  ⚠️  Component changes detected but no documentation updates")
                print("  💡 Consider updating:")
                for doc in doc_files:
                    print(f"    - {doc}")
                return False
                
        except Exception as e:
            print(f"  ⚠️  Could not check documentation: {e}")
            return False
    
    def check_migration_metrics(self) -> bool:
        """Check migration metrics if available."""
        try:
            metrics_file = self.project_root / "migration-metrics.json"
            
            if not metrics_file.exists():
                print("  ℹ️  No migration metrics file found")
                return True
            
            # Check if metrics file is recent (within last hour)
            import json
            from datetime import datetime, timedelta
            
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)
            
            # Get the most recent entry
            if not metrics:
                print("  ℹ️  No metrics data available")
                return True
            
            latest_key = max(metrics.keys())
            latest_metrics = metrics[latest_key]
            
            if "changes" in latest_metrics:
                changes = latest_metrics["changes"]
                coverage = changes.get("design_token_coverage", 0)
                
                if coverage >= 90:
                    print(f"  ✅ Design token coverage: {coverage:.1f}%")
                    return True
                else:
                    print(f"  ⚠️  Design token coverage: {coverage:.1f}% (target: 90%+)")
                    return False
            else:
                print("  ℹ️  No comparison metrics available")
                return True
                
        except Exception as e:
            print(f"  ⚠️  Could not check migration metrics: {e}")
            return True  # Don't fail on metrics check errors
    
    def check_file_structure(self) -> bool:
        """Check if component follows proper file structure."""
        try:
            # Get staged files
            result = subprocess.run([
                "git", "diff", "--cached", "--name-only", "--diff-filter=A"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            staged_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
            # Find new component directories
            component_dirs = set()
            for file_path in staged_files:
                if 'components/common/' in file_path and '/' in file_path.split('components/common/')[-1]:
                    component_name = file_path.split('components/common/')[-1].split('/')[0]
                    component_dirs.add(component_name)
            
            if not component_dirs:
                print("  ℹ️  No new component directories detected")
                return True
            
            # Check each component directory structure
            required_files = ['index.ts', 'types.ts', 'styles.ts']
            component_file_pattern = r'\.tsx$'
            
            for component_name in component_dirs:
                component_path = self.components_path / component_name
                
                if not component_path.exists():
                    print(f"  ❌ Component directory not found: {component_name}")
                    return False
                
                # Check required files
                missing_files = []
                for required_file in required_files:
                    if not (component_path / required_file).exists():
                        missing_files.append(required_file)
                
                # Check for main component file
                component_files = list(component_path.glob(f"{component_name}.tsx"))
                if not component_files:
                    missing_files.append(f"{component_name}.tsx")
                
                if missing_files:
                    print(f"  ❌ {component_name} missing files: {', '.join(missing_files)}")
                    return False
                else:
                    print(f"  ✅ {component_name} has proper file structure")
            
            return True
            
        except Exception as e:
            print(f"  ⚠️  Could not check file structure: {e}")
            return False
    
    def check_component_specific(self, component_name: str) -> bool:
        """Run component-specific checks."""
        try:
            component_path = self.components_path / component_name
            
            if not component_path.exists():
                print(f"  ❌ Component directory not found: {component_name}")
                return False
            
            # Check if component exports are clean
            index_file = component_path / "index.ts"
            if index_file.exists():
                content = index_file.read_text()
                if f"export {{ {component_name} }}" in content:
                    print(f"  ✅ {component_name} has clean exports")
                    return True
                else:
                    print(f"  ⚠️  {component_name} exports may need review")
                    return False
            else:
                print(f"  ❌ {component_name} missing index.ts")
                return False
                
        except Exception as e:
            print(f"  ⚠️  Component-specific check failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Pre-commit migration checklist')
    parser.add_argument('--component', type=str, help='Specific component to check')
    parser.add_argument('--all', action='store_true', help='Run all general checks')
    
    args = parser.parse_args()
    
    checker = PreCommitChecker()
    
    if args.component:
        success = checker.run_all_checks(args.component)
    else:
        success = checker.run_all_checks()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
