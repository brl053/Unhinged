#!/usr/bin/env python3
"""
@llm-type util.migrator
@llm-does transforms 8-tag LlmDocs to 3-tag evolved format
@llm-rule must preserve semantic meaning while eliminating redundancy
"""

import re
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import argparse

@dataclass
class LegacyLlmDoc:
    """Represents current 8-tag LlmDoc format."""
    type: Optional[str] = None
    legend: Optional[str] = None
    key: Optional[str] = None
    map: Optional[str] = None
    axiom: Optional[str] = None
    contract: Optional[str] = None
    token: Optional[str] = None
    context: Optional[str] = None

@dataclass
class EvolvedLlmDoc:
    """Represents evolved 3-tag LlmDoc format."""
    type: str
    does: str
    rule: Optional[str] = None

class LlmDocsEvolutionEngine:
    """Transforms LlmDocs from 8-tag redundant format to 3-tag evolved format."""
    
    # Type hierarchy mapping
    TYPE_HIERARCHY = {
        'service': 'service.api',
        'service-launcher': 'service.launcher',
        'service-utilities': 'service.util',
        'service-shared': 'service.shared',
        'api-server': 'service.api',
        'worker': 'service.worker',
        'auth': 'service.auth',
        
        'component': 'component.primitive',
        'component-specification': 'component.spec',
        'container': 'component.container',
        'complex-component': 'component.complex',
        
        'function': 'util.function',
        'parser': 'util.parser',
        'validator': 'util.validator',
        'formatter': 'util.formatter',
        'converter': 'util.converter',
        'migrator': 'util.migrator',
        'runner': 'util.runner',
        'cli': 'util.cli',
        'tool': 'util.tool',
        
        'model': 'model.entity',
        'data-model': 'model.entity',
        'dto': 'model.dto',
        'config': 'model.config',
        'schema': 'model.schema',
        
        'build-module': 'config.build',
        'build-config': 'config.build',
        'build-orchestrator': 'config.build',
        'deploy-config': 'config.deploy',
        'env-config': 'config.env',
        'app-config': 'config.app',
        
        'python-runner': 'util.runner',
        'python-setup': 'util.setup',
        'python-executor': 'util.executor',
    }
    
    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.processed_files = []
        self.errors = []
        self.backup_dir = project_root / ".llmdocs-backup"
        
    def run_migration(self) -> Dict[str, int]:
        """Execute complete migration with backup and validation."""
        print("🔄 Starting LlmDocs Evolution (8-tag → 3-tag)")
        
        # Create backup
        if not self.dry_run:
            self._create_backup()
        
        # Find all files with LlmDocs
        files_to_migrate = self._find_llmdoc_files()
        print(f"📁 Found {len(files_to_migrate)} files with LlmDocs")
        
        # Process each file
        stats = {'processed': 0, 'migrated': 0, 'errors': 0, 'skipped': 0}
        
        for file_path in files_to_migrate:
            try:
                result = self._migrate_file(file_path)
                if result == 'migrated':
                    stats['migrated'] += 1
                elif result == 'skipped':
                    stats['skipped'] += 1
                stats['processed'] += 1
                
                if stats['processed'] % 10 == 0:
                    print(f"  📊 Progress: {stats['processed']}/{len(files_to_migrate)} files")
                    
            except Exception as e:
                self.errors.append(f"{file_path}: {str(e)}")
                stats['errors'] += 1
        
        return stats
    
    def _create_backup(self):
        """Create backup of all files before migration."""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        print(f"💾 Creating backup in {self.backup_dir}")
        shutil.copytree(self.project_root, self.backup_dir, 
                       ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', 'node_modules'))
    
    def _find_llmdoc_files(self) -> List[Path]:
        """Find all files containing LlmDocs."""
        extensions = ['.py', '.kt', '.js', '.ts', '.java', '.sh', '.yml', '.yaml']
        files = []
        
        for ext in extensions:
            files.extend(self.project_root.rglob(f'*{ext}'))
        
        # Filter files that contain @llm- tags
        llmdoc_files = []
        for file_path in files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '@llm-' in content:
                        llmdoc_files.append(file_path)
            except (UnicodeDecodeError, PermissionError):
                continue
        
        return llmdoc_files
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            '.git/', '__pycache__/', 'node_modules/', '.llmdocs-backup/',
            'generated/', 'build/tools/llmdocs-v2-migrator.py'
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)
    
    def _migrate_file(self, file_path: Path) -> str:
        """Migrate a single file from 8-tag to 3-tag format."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract all LlmDoc blocks
        llmdoc_blocks = self._extract_llmdoc_blocks(content)
        if not llmdoc_blocks:
            return 'skipped'
        
        # Migrate each block
        migrated_content = content
        migration_count = 0
        
        for original_block, legacy_doc in llmdoc_blocks:
            evolved_doc = self._transform_legacy_to_evolved(legacy_doc, file_path)
            evolved_block = self._format_evolved_block(evolved_doc, file_path.suffix)
            migrated_content = migrated_content.replace(original_block, evolved_block)
            migration_count += 1
        
        # Write migrated content
        if not self.dry_run and migration_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(migrated_content)
            self.processed_files.append(str(file_path))
        
        return 'migrated' if migration_count > 0 else 'skipped'
    
    def _extract_llmdoc_blocks(self, content: str) -> List[Tuple[str, LegacyLlmDoc]]:
        """Extract all LlmDoc blocks from content."""
        blocks = []
        
        # Pattern to match multi-line comment blocks with @llm- tags
        patterns = [
            r'("""[\s\S]*?""")',  # Python docstrings
            r'(\/\*[\s\S]*?\*\/)',  # C-style comments
            r'((?:^[ \t]*#.*\n)+)',  # Shell/YAML comments
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                block_text = match.group(1)
                if '@llm-' in block_text:
                    legacy_doc = self._parse_legacy_block(block_text)
                    if legacy_doc.type:  # Only process blocks with at least a type
                        blocks.append((block_text, legacy_doc))
        
        return blocks
    
    def _parse_legacy_block(self, block_text: str) -> LegacyLlmDoc:
        """Parse legacy 8-tag LlmDoc block."""
        legacy_doc = LegacyLlmDoc()
        
        patterns = {
            'type': r'@llm-type\s+([^\n]+)',
            'legend': r'@llm-legend\s+([^\n@]+)',
            'key': r'@llm-key\s+([^\n@]+)',
            'map': r'@llm-map\s+([^\n@]+)',
            'axiom': r'@llm-axiom\s+([^\n@]+)',
            'contract': r'@llm-contract\s+([^\n@]+)',
            'token': r'@llm-token\s+([^\n@]+)',
            'context': r'@llm-context\s+([^\n@]+)'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, block_text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                setattr(legacy_doc, field, value)
        
        return legacy_doc
    
    def _transform_legacy_to_evolved(self, legacy_doc: LegacyLlmDoc, file_path: Path) -> EvolvedLlmDoc:
        """Transform legacy 8-tag format to evolved 3-tag format."""
        # 1. Transform type to hierarchical
        evolved_type = self._get_hierarchical_type(legacy_doc.type, file_path)
        
        # 2. Extract action from legend/key (eliminate redundancy)
        evolved_does = self._extract_action(legacy_doc)
        
        # 3. Extract critical rule from axiom (only if truly critical)
        evolved_rule = self._extract_critical_rule(legacy_doc.axiom)
        
        return EvolvedLlmDoc(
            type=evolved_type,
            does=evolved_does,
            rule=evolved_rule
        )
    
    def _get_hierarchical_type(self, legacy_type: str, file_path: Path) -> str:
        """Convert flat type to hierarchical type."""
        if not legacy_type:
            return self._infer_type_from_path(file_path)
        
        # Direct mapping
        if legacy_type in self.TYPE_HIERARCHY:
            return self.TYPE_HIERARCHY[legacy_type]
        
        # Infer from file path if not mapped
        return self._infer_type_from_path(file_path, legacy_type)
    
    def _infer_type_from_path(self, file_path: Path, fallback_type: str = 'misc') -> str:
        """Infer hierarchical type from file path."""
        path_str = str(file_path).lower()
        
        if 'service' in path_str:
            return 'service.api'
        elif 'component' in path_str:
            return 'component.primitive'
        elif 'model' in path_str or 'entity' in path_str:
            return 'model.entity'
        elif 'config' in path_str:
            return 'config.app'
        elif 'util' in path_str or 'tool' in path_str:
            return 'util.function'
        elif 'build' in path_str:
            return 'config.build'
        else:
            return f'misc.{fallback_type}'
    
    def _extract_action(self, legacy_doc: LegacyLlmDoc) -> str:
        """Extract clean action description from redundant legend/key/map."""
        # Priority: legend > key > map
        source_text = legacy_doc.legend or legacy_doc.key or legacy_doc.map or "handles operations"
        
        # Clean and extract first meaningful phrase (3-7 words)
        cleaned = re.sub(r'\s+', ' ', source_text).strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            'provides ', 'implements ', 'handles ', 'manages ', 'creates ', 
            'builds ', 'generates ', 'validates ', 'processes ', 'executes '
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):]
                break
        
        # Take first 3-7 words
        words = cleaned.split()[:7]
        result = ' '.join(words)
        
        # Ensure it's not too long
        if len(result) > 60:
            result = result[:57] + "..."
        
        return result.lower()
    
    def _extract_critical_rule(self, axiom: str) -> Optional[str]:
        """Extract only critical business rules from axioms."""
        if not axiom or len(axiom) < 20:
            return None
        
        # Only keep axioms that contain critical business constraints
        critical_keywords = [
            'must not', 'must be', 'cannot', 'required', 'forbidden', 
            'always', 'never', 'only', 'exactly', 'minimum', 'maximum'
        ]
        
        axiom_lower = axiom.lower()
        if any(keyword in axiom_lower for keyword in critical_keywords):
            # Simplify the rule
            simplified = re.sub(r'\s+', ' ', axiom).strip()
            if len(simplified) > 80:
                simplified = simplified[:77] + "..."
            return simplified.lower()
        
        return None
    
    def _format_evolved_block(self, evolved_doc: EvolvedLlmDoc, file_extension: str) -> str:
        """Format evolved 3-tag LlmDoc as comment block."""
        lines = [
            f'@llm-type {evolved_doc.type}',
            f'@llm-does {evolved_doc.does}'
        ]
        
        if evolved_doc.rule:
            lines.append(f'@llm-rule {evolved_doc.rule}')
        
        # Format according to file type
        if file_extension == '.py':
            content = '\n'.join(lines)
            return f'"""\n{content}\n"""'
        elif file_extension in ['.js', '.ts', '.kt', '.java']:
            content = '\n'.join(f' * {line}' for line in lines)
            return f'/*\n{content}\n */'
        else:  # Shell, YAML, etc.
            content = '\n'.join(f'# {line}' for line in lines)
            return content
    
    def generate_report(self, stats: Dict[str, int]) -> str:
        """Generate migration report."""
        report = [
            "# LlmDocs Evolution Report (8-tag → 3-tag)",
            "",
            f"## Summary",
            f"- Files processed: {stats['processed']}",
            f"- Files migrated: {stats['migrated']}",
            f"- Files skipped: {stats['skipped']}",
            f"- Errors: {stats['errors']}",
            "",
        ]
        
        if self.processed_files:
            report.extend([
                "## Migrated Files",
                ""
            ])
            for file_path in self.processed_files[:20]:  # Show first 20
                report.append(f"- {file_path}")
            
            if len(self.processed_files) > 20:
                report.append(f"- ... and {len(self.processed_files) - 20} more files")
            report.append("")
        
        if self.errors:
            report.extend([
                "## Errors",
                ""
            ])
            for error in self.errors[:10]:  # Show first 10 errors
                report.append(f"- {error}")
            
            if len(self.errors) > 10:
                report.append(f"- ... and {len(self.errors) - 10} more errors")
        
        return '\n'.join(report)

def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description='LlmDocs Evolution Engine (8-tag → 3-tag)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--project-root', type=Path, default=Path.cwd(), help='Project root directory')
    
    args = parser.parse_args()
    
    engine = LlmDocsEvolutionEngine(args.project_root, dry_run=args.dry_run)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    
    stats = engine.run_migration()
    
    print(f"\n✅ Migration complete!")
    print(f"   Processed: {stats['processed']} files")
    print(f"   Migrated: {stats['migrated']} files")
    print(f"   Skipped: {stats['skipped']} files")
    print(f"   Errors: {stats['errors']} files")
    
    # Generate report
    report = engine.generate_report(stats)
    report_path = "docs/architecture/llmdocs-evolution-report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"📄 Migration report saved to {report_path}")
    
    if not args.dry_run and stats['migrated'] > 0:
        print(f"💾 Backup created in {engine.backup_dir}")
        print("   Use 'git checkout .' to rollback if needed")
    
    return 0 if stats['errors'] == 0 else 1

if __name__ == "__main__":
    exit(main())
