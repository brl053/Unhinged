#!/usr/bin/env python3
"""
Theme Property Access Fix Script - Japanese Precision Tooling

Fixes theme property access patterns to match the actual design system structure.
Operates on TypeScript/JavaScript files in the frontend directory with surgical precision.

Philosophy: Japanese approach to development - intentional, high-quality work using precise
"hand tools" rather than rushing with generic solutions. This script is designed to be
reusable, well-understood, and maintainable.

Usage:
    python fix_theme_properties.py [--dry-run] [--pattern PATTERN] [--replacement REPLACEMENT]
    
Examples:
    # Fix all known patterns
    python scripts/python/fix_theme_properties.py
    
    # Dry run to see what would change
    python scripts/python/fix_theme_properties.py --dry-run
    
    # Custom pattern replacement
    python scripts/python/fix_theme_properties.py --pattern 'theme\\.spatial\\.spacing' --replacement 'theme.spatial.base.spacing'

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-06
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict
import json

# Default patterns to fix - ONLY patterns that actually need changing
DEFAULT_PATTERNS = [
    # Spatial patterns - these need to be fixed to match design system structure
    (r'theme\.spatial\.spacing\.', 'theme.spatial.base.spacing.'),
    (r'theme\.spatial\.border\.', 'theme.spatial.base.border.'),
    (r'theme\.spatial\.radius\.', 'theme.spatial.base.radius.'),

    # Direct spatial unit access - these need base. prefix
    (r'theme\.spatial\.millipixel\b', 'theme.spatial.base.millipixel'),
    (r'theme\.spatial\.centipixel\b', 'theme.spatial.base.centipixel'),
    (r'theme\.spatial\.pixel\b', 'theme.spatial.base.pixel'),
    (r'theme\.spatial\.decapixel\b', 'theme.spatial.base.decapixel'),
    (r'theme\.spatial\.hectopixel\b', 'theme.spatial.base.hectopixel'),
    (r'theme\.spatial\.kilopixel\b', 'theme.spatial.base.kilopixel'),

    # Note: Typography, colors, motion, and platform patterns are already correct
    # and don't need to be changed. They were removed from this list.
]

def find_typescript_files(root_dir: Path) -> List[Path]:
    """
    Find all TypeScript and JavaScript files in the directory.
    
    Args:
        root_dir: Root directory to search
        
    Returns:
        List of Path objects for TypeScript/JavaScript files
    """
    extensions = ['*.ts', '*.tsx', '*.js', '*.jsx']
    files = []
    
    for ext in extensions:
        files.extend(root_dir.rglob(ext))
    
    # Exclude node_modules, build, and dist directories
    excluded_dirs = {'node_modules', 'build', 'dist', '.next', 'coverage'}
    files = [f for f in files if not any(excluded in str(f) for excluded in excluded_dirs)]
    
    return sorted(files)  # Sort for consistent processing order

def apply_fixes(content: str, patterns: List[Tuple[str, str]]) -> Tuple[str, int, Dict[str, int]]:
    """
    Apply regex replacements to content with detailed reporting.
    
    Args:
        content: File content to process
        patterns: List of (pattern, replacement) tuples
        
    Returns:
        Tuple of (new_content, total_changes, pattern_counts)
    """
    pattern_counts = {}
    new_content = content
    total_changes = 0
    
    for pattern, replacement in patterns:
        new_content, count = re.subn(pattern, replacement, new_content)
        if count > 0:
            pattern_counts[f"{pattern} -> {replacement}"] = count
            total_changes += count
    
    return new_content, total_changes, pattern_counts

def process_file(file_path: Path, patterns: List[Tuple[str, str]], dry_run: bool = False) -> Dict:
    """
    Process a single file with detailed reporting.
    
    Args:
        file_path: Path to file to process
        patterns: List of (pattern, replacement) tuples
        dry_run: If True, don't modify files
        
    Returns:
        Dictionary with processing results
    """
    result = {
        'file': str(file_path),
        'processed': False,
        'changes': 0,
        'patterns': {},
        'error': None
    }
    
    try:
        content = file_path.read_text(encoding='utf-8')
        new_content, num_changes, pattern_counts = apply_fixes(content, patterns)
        
        result['processed'] = True
        result['changes'] = num_changes
        result['patterns'] = pattern_counts
        
        if num_changes > 0:
            # Safe relative path handling
            try:
                rel_path = file_path.relative_to(Path.cwd())
            except ValueError:
                rel_path = file_path

            if dry_run:
                print(f"[DRY RUN] Would fix {num_changes} occurrences in: {rel_path}")
                for pattern_desc, count in pattern_counts.items():
                    print(f"  - {count}x: {pattern_desc}")
            else:
                file_path.write_text(new_content, encoding='utf-8')
                print(f"✅ Fixed {num_changes} occurrences in: {rel_path}")
                for pattern_desc, count in pattern_counts.items():
                    print(f"  - {count}x: {pattern_desc}")
        
    except Exception as e:
        result['error'] = str(e)
        # Safe relative path handling
        try:
            rel_path = file_path.relative_to(Path.cwd())
        except ValueError:
            rel_path = file_path
        print(f"❌ Error processing {rel_path}: {e}", file=sys.stderr)
    
    return result

def generate_report(results: List[Dict], dry_run: bool = False) -> None:
    """
    Generate a comprehensive report of the processing results.
    
    Args:
        results: List of processing result dictionaries
        dry_run: Whether this was a dry run
    """
    total_files = len(results)
    processed_files = sum(1 for r in results if r['processed'])
    modified_files = sum(1 for r in results if r['changes'] > 0)
    total_changes = sum(r['changes'] for r in results)
    error_files = sum(1 for r in results if r['error'])
    
    # Aggregate pattern statistics
    pattern_stats = {}
    for result in results:
        for pattern_desc, count in result['patterns'].items():
            pattern_stats[pattern_desc] = pattern_stats.get(pattern_desc, 0) + count
    
    print("\n" + "="*80)
    print(f"🎯 THEME PROPERTY FIX REPORT {'(DRY RUN)' if dry_run else ''}")
    print("="*80)
    print(f"📁 Files scanned: {total_files}")
    print(f"✅ Files processed: {processed_files}")
    print(f"🔧 Files {'would be ' if dry_run else ''}modified: {modified_files}")
    print(f"📝 Total changes: {total_changes}")
    if error_files > 0:
        print(f"❌ Files with errors: {error_files}")
    
    if pattern_stats:
        print(f"\n📊 Pattern Statistics:")
        for pattern_desc, count in sorted(pattern_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {count}x: {pattern_desc}")
    
    if dry_run and total_changes > 0:
        print(f"\n💡 Run without --dry-run to apply {total_changes} changes to {modified_files} files")
    elif not dry_run and total_changes > 0:
        print(f"\n🎉 Successfully applied {total_changes} changes to {modified_files} files")
    else:
        print(f"\n✨ No changes needed - all theme properties are correctly structured!")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Fix theme property access patterns with Japanese precision',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/python/fix_theme_properties.py
  python scripts/python/fix_theme_properties.py --dry-run
  python scripts/python/fix_theme_properties.py --pattern 'theme\\.spatial\\.spacing' --replacement 'theme.spatial.base.spacing'
        """
    )
    
    parser.add_argument('--dry-run', action='store_true', 
                        help='Show what would be changed without modifying files')
    parser.add_argument('--pattern', type=str,
                        help='Custom regex pattern to match')
    parser.add_argument('--replacement', type=str,
                        help='Custom replacement string')
    parser.add_argument('--root', type=str, default='frontend',
                        help='Root directory to process (default: frontend)')
    parser.add_argument('--report', type=str,
                        help='Save detailed report to JSON file')
    
    args = parser.parse_args()
    
    # Validate custom pattern arguments
    if bool(args.pattern) != bool(args.replacement):
        print("❌ Error: --pattern and --replacement must be used together", file=sys.stderr)
        sys.exit(1)
    
    # Determine patterns to use
    if args.pattern and args.replacement:
        patterns = [(args.pattern, args.replacement)]
        print(f"🎯 Using custom pattern: {args.pattern} -> {args.replacement}")
    else:
        patterns = DEFAULT_PATTERNS
        print(f"🔧 Using {len(patterns)} default theme property patterns")
    
    # Validate root directory
    root_dir = Path(args.root)
    if not root_dir.exists():
        print(f"❌ Error: Directory {root_dir} does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Find all files to process
    files = find_typescript_files(root_dir)
    print(f"📁 Found {len(files)} TypeScript/JavaScript files to process")
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No files will be modified")
    
    print("\n" + "-"*60)
    
    # Process all files
    results = []
    for file_path in files:
        result = process_file(file_path, patterns, args.dry_run)
        results.append(result)
    
    # Generate comprehensive report
    generate_report(results, args.dry_run)
    
    # Save detailed report if requested
    if args.report:
        report_path = Path(args.report)
        report_data = {
            'summary': {
                'total_files': len(results),
                'modified_files': sum(1 for r in results if r['changes'] > 0),
                'total_changes': sum(r['changes'] for r in results),
                'dry_run': args.dry_run,
            },
            'results': results,
            'patterns_used': [{'pattern': p, 'replacement': r} for p, r in patterns]
        }
        
        report_path.write_text(json.dumps(report_data, indent=2))
        print(f"\n📄 Detailed report saved to: {report_path}")

if __name__ == '__main__':
    main()
