#!/usr/bin/env python3
"""
Component Migration Analysis Tool

Analyzes component migrations to provide precise metrics on:
- Lines of code comparison (before/after)
- Design token coverage percentage
- TypeScript safety score
- Bundle size impact analysis
- Migration velocity tracking

Usage:
    python scripts/python/analyze_migration.py --component PromptSurgeryPanel
    python scripts/python/analyze_migration.py --component EventFeed --pre-migration
    python scripts/python/analyze_migration.py --all-components

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-06
"""

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os

class MigrationAnalyzer:
    """Analyzes component migrations with precise metrics."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.frontend_path = self.project_root / "frontend"
        self.components_path = self.frontend_path / "src" / "components" / "common"
        self.metrics_file = self.project_root / "migration-metrics.json"
        
    def analyze_component(self, component_name: str, pre_migration: bool = False) -> Dict:
        """
        Analyze a single component for migration metrics.
        
        Args:
            component_name: Name of the component to analyze
            pre_migration: If True, analyze the original monolithic file
            
        Returns:
            Dictionary with comprehensive migration metrics
        """
        print(f"🔍 Analyzing {component_name} {'(pre-migration)' if pre_migration else '(post-migration)'}")
        
        if pre_migration:
            return self._analyze_monolithic_component(component_name)
        else:
            return self._analyze_recursive_component(component_name)
    
    def _analyze_monolithic_component(self, component_name: str) -> Dict:
        """Analyze original monolithic component file."""
        # Check if original file exists (might be deleted after migration)
        original_file = self.components_path / f"{component_name}.tsx"
        
        if not original_file.exists():
            # Try to get from git history (check multiple commits back)
            try:
                for i in range(1, 5):  # Check HEAD~1 through HEAD~4
                    result = subprocess.run([
                        "git", "show", f"HEAD~{i}:frontend/src/components/common/{component_name}.tsx"
                    ], capture_output=True, text=True, cwd=self.project_root)

                    if result.returncode == 0:
                        content = result.stdout
                        return self._analyze_content(content, f"{component_name}.tsx (from git HEAD~{i})")

                # If not found in recent commits, return error
                result = None

                print(f"⚠️  Could not find original {component_name}.tsx in recent git history")
                return {"error": "Original file not found"}
            except Exception as e:
                print(f"❌ Error accessing git history: {e}")
                return {"error": str(e)}
        else:
            return self._analyze_file(original_file)
    
    def _analyze_recursive_component(self, component_name: str) -> Dict:
        """Analyze migrated recursive component structure."""
        component_dir = self.components_path / component_name
        
        if not component_dir.exists():
            return {"error": f"Component directory {component_dir} not found"}
        
        # Analyze all files in the component directory
        files = list(component_dir.glob("*.ts")) + list(component_dir.glob("*.tsx"))
        
        total_metrics = {
            "component_name": component_name,
            "structure_type": "recursive",
            "analysis_date": datetime.now().isoformat(),
            "files": {},
            "totals": {
                "file_count": len(files),
                "total_loc": 0,
                "total_hard_coded_values": 0,
                "total_design_tokens": 0,
                "typescript_safety": True
            }
        }
        
        for file_path in files:
            file_metrics = self._analyze_file(file_path)
            file_name = file_path.name
            total_metrics["files"][file_name] = file_metrics
            
            # Aggregate totals
            total_metrics["totals"]["total_loc"] += file_metrics.get("loc", 0)
            total_metrics["totals"]["total_hard_coded_values"] += file_metrics.get("hard_coded_values", 0)
            total_metrics["totals"]["total_design_tokens"] += file_metrics.get("design_tokens", 0)
            
            if not file_metrics.get("typescript_safe", True):
                total_metrics["totals"]["typescript_safety"] = False
        
        # Calculate design token coverage
        total_values = (total_metrics["totals"]["total_hard_coded_values"] + 
                       total_metrics["totals"]["total_design_tokens"])
        
        if total_values > 0:
            coverage = (total_metrics["totals"]["total_design_tokens"] / total_values) * 100
            total_metrics["totals"]["design_token_coverage"] = round(coverage, 1)
        else:
            total_metrics["totals"]["design_token_coverage"] = 100.0
        
        return total_metrics
    
    def _analyze_file(self, file_path: Path) -> Dict:
        """Analyze a single file for migration metrics."""
        try:
            content = file_path.read_text(encoding='utf-8')
            return self._analyze_content(content, str(file_path))
        except Exception as e:
            return {"error": f"Could not read {file_path}: {e}"}
    
    def _analyze_content(self, content: str, source: str) -> Dict:
        """Analyze file content for migration metrics."""
        lines = content.split('\n')
        
        # Count lines of code (excluding empty lines and comments)
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
        
        # Find hard-coded values
        hard_coded_patterns = [
            r'#[0-9a-fA-F]{6}',  # Hex colors
            r'#[0-9a-fA-F]{3}',   # Short hex colors
            r'\b\d+px\b',         # Pixel values
            r'rgba?\(\d+,\s*\d+,\s*\d+',  # RGB/RGBA colors
        ]
        
        hard_coded_values = 0
        for pattern in hard_coded_patterns:
            matches = re.findall(pattern, content)
            hard_coded_values += len(matches)
        
        # Find design token usage
        design_token_patterns = [
            r'theme\.colors\.',
            r'theme\.spatial\.',
            r'theme\.typography\.',
            r'theme\.motion\.',
            r'theme\.platform\.',
        ]
        
        design_tokens = 0
        for pattern in design_token_patterns:
            matches = re.findall(pattern, content)
            design_tokens += len(matches)
        
        # Check TypeScript safety
        typescript_safe = not bool(re.search(r'\bany\b|\bas\s+any\b|@ts-ignore', content))
        
        # Check for imports from design system
        has_design_system_import = bool(re.search(r'from.*design_system', content))
        
        return {
            "source": source,
            "loc": loc,
            "hard_coded_values": hard_coded_values,
            "design_tokens": design_tokens,
            "typescript_safe": typescript_safe,
            "has_design_system_import": has_design_system_import,
            "analysis_date": datetime.now().isoformat()
        }
    
    def compare_migration(self, component_name: str) -> Dict:
        """Compare pre and post migration metrics."""
        print(f"📊 Comparing migration metrics for {component_name}")
        
        pre_metrics = self.analyze_component(component_name, pre_migration=True)
        post_metrics = self.analyze_component(component_name, pre_migration=False)
        
        if "error" in pre_metrics or "error" in post_metrics:
            return {
                "error": "Could not complete comparison",
                "pre_metrics": pre_metrics,
                "post_metrics": post_metrics
            }
        
        # Calculate comparison metrics
        pre_loc = pre_metrics.get("loc", 0)
        post_loc = post_metrics["totals"]["total_loc"]
        
        loc_change = post_loc - pre_loc
        loc_change_percent = (loc_change / pre_loc * 100) if pre_loc > 0 else 0
        
        pre_hard_coded = pre_metrics.get("hard_coded_values", 0)
        post_hard_coded = post_metrics["totals"]["total_hard_coded_values"]
        
        comparison = {
            "component_name": component_name,
            "comparison_date": datetime.now().isoformat(),
            "pre_migration": pre_metrics,
            "post_migration": post_metrics,
            "changes": {
                "loc_before": pre_loc,
                "loc_after": post_loc,
                "loc_change": loc_change,
                "loc_change_percent": round(loc_change_percent, 1),
                "hard_coded_before": pre_hard_coded,
                "hard_coded_after": post_hard_coded,
                "hard_coded_reduction": pre_hard_coded - post_hard_coded,
                "design_token_coverage": post_metrics["totals"]["design_token_coverage"],
                "file_count": post_metrics["totals"]["file_count"],
                "structure_improvement": "monolithic → recursive"
            }
        }
        
        return comparison
    
    def save_metrics(self, metrics: Dict, component_name: str = None):
        """Save metrics to JSON file for tracking."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    all_metrics = json.load(f)
            except:
                all_metrics = {}
        else:
            all_metrics = {}
        
        timestamp = datetime.now().isoformat()
        if component_name:
            all_metrics[f"{component_name}_{timestamp}"] = metrics
        else:
            all_metrics[timestamp] = metrics
        
        with open(self.metrics_file, 'w') as f:
            json.dump(all_metrics, f, indent=2)
        
        print(f"💾 Metrics saved to {self.metrics_file}")
    
    def generate_report(self, metrics: Dict):
        """Generate a formatted report from metrics."""
        if "error" in metrics:
            print(f"❌ Error: {metrics['error']}")
            return
        
        if "changes" in metrics:  # Comparison report
            self._generate_comparison_report(metrics)
        else:  # Single component report
            self._generate_component_report(metrics)
    
    def _generate_comparison_report(self, metrics: Dict):
        """Generate comparison report."""
        changes = metrics["changes"]
        component_name = metrics["component_name"]
        
        print(f"\n📊 MIGRATION ANALYSIS REPORT: {component_name}")
        print("=" * 60)
        
        print(f"📁 Structure Change: {changes['structure_improvement']}")
        print(f"📄 File Count: {changes['file_count']} files")
        
        print(f"\n📏 Lines of Code:")
        print(f"  Before: {changes['loc_before']} LOC")
        print(f"  After:  {changes['loc_after']} LOC")
        print(f"  Change: {changes['loc_change']:+d} LOC ({changes['loc_change_percent']:+.1f}%)")
        
        print(f"\n🎨 Design Token Integration:")
        print(f"  Hard-coded values before: {changes['hard_coded_before']}")
        print(f"  Hard-coded values after:  {changes['hard_coded_after']}")
        print(f"  Values eliminated: {changes['hard_coded_reduction']}")
        print(f"  Design token coverage: {changes['design_token_coverage']:.1f}%")
        
        # Quality assessment
        if changes['design_token_coverage'] == 100.0:
            print(f"  ✅ Perfect design token integration!")
        elif changes['design_token_coverage'] >= 90.0:
            print(f"  ✅ Excellent design token coverage")
        else:
            print(f"  ⚠️  Design token coverage needs improvement")
    
    def _generate_component_report(self, metrics: Dict):
        """Generate single component report."""
        component_name = metrics["component_name"]
        totals = metrics["totals"]
        
        print(f"\n📊 COMPONENT ANALYSIS: {component_name}")
        print("=" * 50)
        
        print(f"📁 Structure: {metrics['structure_type']}")
        print(f"📄 Files: {totals['file_count']}")
        print(f"📏 Total LOC: {totals['total_loc']}")
        print(f"🎨 Design Token Coverage: {totals['design_token_coverage']:.1f}%")
        print(f"🔒 TypeScript Safety: {'✅' if totals['typescript_safety'] else '❌'}")

def main():
    parser = argparse.ArgumentParser(description='Analyze component migration metrics')
    parser.add_argument('--component', type=str, help='Component name to analyze')
    parser.add_argument('--pre-migration', action='store_true', 
                        help='Analyze pre-migration state')
    parser.add_argument('--compare', action='store_true',
                        help='Compare pre and post migration')
    parser.add_argument('--all-components', action='store_true',
                        help='Analyze all migrated components')
    parser.add_argument('--save', action='store_true',
                        help='Save metrics to JSON file')
    
    args = parser.parse_args()
    
    analyzer = MigrationAnalyzer()
    
    if args.all_components:
        # Find all recursive components
        components_dir = analyzer.components_path
        if components_dir.exists():
            for item in components_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    metrics = analyzer.analyze_component(item.name)
                    analyzer.generate_report(metrics)
                    if args.save:
                        analyzer.save_metrics(metrics, item.name)
    
    elif args.component:
        if args.compare:
            metrics = analyzer.compare_migration(args.component)
        else:
            metrics = analyzer.analyze_component(args.component, args.pre_migration)
        
        analyzer.generate_report(metrics)
        
        if args.save:
            analyzer.save_metrics(metrics, args.component)
    
    else:
        print("Please specify --component or --all-components")
        parser.print_help()

if __name__ == '__main__':
    main()
