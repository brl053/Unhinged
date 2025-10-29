#!/usr/bin/env python3
"""
@llm-type util.migrator
@llm-purpose Migrates LlmDocs from V1 to V2 format
@llm-contract V1 LlmDocs -> V2 LlmDocs
@llm-axiom Migration must preserve semantic meaning while reducing redundancy
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class LlmDocV1:
    """Represents a V1 LlmDoc comment block."""
    type: Optional[str] = None
    legend: Optional[str] = None
    key: Optional[str] = None
    map: Optional[str] = None
    axiom: Optional[str] = None
    contract: Optional[str] = None
    token: Optional[str] = None
    context: Optional[str] = None

@dataclass
class LlmDocV2:
    """Represents a V2 LlmDoc comment block."""
    type: str
    purpose: str
    contract: Optional[str] = None
    axiom: Optional[str] = None
    deps: Optional[str] = None

class LlmDocsV2Migrator:
    """Migrates LlmDocs from V1 to V2 format."""
    
    # Type mapping from V1 to V2 hierarchical types
    TYPE_MAPPING = {
        'service': 'service.api',
        'api-server': 'service.api',
        'worker': 'service.worker',
        'gateway': 'service.gateway',
        'auth': 'service.auth',
        
        'component': 'component.primitive',
        'container': 'component.container',
        'complex-component': 'component.complex',
        'system-component': 'component.system',
        
        'model': 'model.entity',
        'dto': 'model.dto',
        'config': 'model.config',
        'schema': 'model.schema',
        
        'function': 'util.function',
        'parser': 'util.parser',
        'validator': 'util.validator',
        'formatter': 'util.formatter',
        'converter': 'util.converter',
        
        'build-config': 'config.build',
        'deploy-config': 'config.deploy',
        'env-config': 'config.env',
        'app-config': 'config.app',
        
        'python-runner': 'util.runner',
        'cli': 'util.cli',
        'migrator': 'util.migrator',
    }
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.migrated_files = []
        self.errors = []
    
    def migrate_all_files(self) -> Dict[str, int]:
        """Migrate all files in the project."""
        stats = {'processed': 0, 'migrated': 0, 'errors': 0}
        
        # Find all source files with LlmDocs
        for file_path in self._find_llmdoc_files():
            try:
                if self._migrate_file(file_path):
                    stats['migrated'] += 1
                stats['processed'] += 1
            except Exception as e:
                self.errors.append(f"{file_path}: {str(e)}")
                stats['errors'] += 1
        
        return stats
    
    def _find_llmdoc_files(self) -> List[Path]:
        """Find all files containing LlmDocs."""
        extensions = ['.py', '.kt', '.js', '.ts', '.java', '.sh', '.yml', '.yaml']
        files = []
        
        for ext in extensions:
            files.extend(self.project_root.rglob(f'*{ext}'))
        
        # Filter files that contain @llm- tags
        llmdoc_files = []
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '@llm-' in content:
                        llmdoc_files.append(file_path)
            except (UnicodeDecodeError, PermissionError):
                continue
        
        return llmdoc_files
    
    def _migrate_file(self, file_path: Path) -> bool:
        """Migrate a single file from V1 to V2."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract all LlmDoc blocks
        llmdoc_blocks = self._extract_llmdoc_blocks(content)
        if not llmdoc_blocks:
            return False
        
        # Migrate each block
        migrated_content = content
        for original_block, v1_doc in llmdoc_blocks:
            v2_doc = self._convert_v1_to_v2(v1_doc, file_path)
            v2_block = self._format_v2_block(v2_doc, file_path.suffix)
            migrated_content = migrated_content.replace(original_block, v2_block)
        
        # Write back the migrated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(migrated_content)
        
        self.migrated_files.append(str(file_path))
        return True
    
    def _extract_llmdoc_blocks(self, content: str) -> List[Tuple[str, LlmDocV1]]:
        """Extract all LlmDoc blocks from content."""
        blocks = []
        
        # Pattern to match multi-line comment blocks with @llm- tags
        pattern = r'((?:"""[\s\S]*?""")|(?:\/\*[\s\S]*?\*\/)|(?:(?:^[ \t]*#.*\n)+))'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            block_text = match.group(1)
            if '@llm-' in block_text:
                v1_doc = self._parse_v1_block(block_text)
                if v1_doc.type:  # Only process blocks with at least a type
                    blocks.append((block_text, v1_doc))
        
        return blocks
    
    def _parse_v1_block(self, block_text: str) -> LlmDocV1:
        """Parse a V1 LlmDoc block."""
        v1_doc = LlmDocV1()
        
        # Extract each tag
        patterns = {
            'type': r'@llm-type\s+(\w+(?:\.\w+)*)',
            'legend': r'@llm-legend\s+(.+?)(?=@llm-|\n\n|\Z)',
            'key': r'@llm-key\s+(.+?)(?=@llm-|\n\n|\Z)',
            'map': r'@llm-map\s+(.+?)(?=@llm-|\n\n|\Z)',
            'axiom': r'@llm-axiom\s+(.+?)(?=@llm-|\n\n|\Z)',
            'contract': r'@llm-contract\s+(.+?)(?=@llm-|\n\n|\Z)',
            'token': r'@llm-token\s+(.+?)(?=@llm-|\n\n|\Z)',
            'context': r'@llm-context\s+(.+?)(?=@llm-|\n\n|\Z)'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, block_text, re.DOTALL | re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Clean up multi-line values
                value = re.sub(r'\s+', ' ', value)
                setattr(v1_doc, field, value)
        
        return v1_doc
    
    def _convert_v1_to_v2(self, v1_doc: LlmDocV1, file_path: Path) -> LlmDocV2:
        """Convert V1 LlmDoc to V2 format."""
        # Map type to hierarchical format
        v2_type = self.TYPE_MAPPING.get(v1_doc.type, v1_doc.type)
        if '.' not in v2_type:
            # Infer category from file path if not mapped
            v2_type = self._infer_type_from_path(file_path, v1_doc.type)
        
        # Create purpose from legend, key, or infer from type
        purpose = self._create_purpose(v1_doc)
        
        # Simplify contract if present
        contract = self._simplify_contract(v1_doc.contract) if v1_doc.contract else None
        
        # Keep axiom if present and meaningful
        axiom = v1_doc.axiom if v1_doc.axiom and len(v1_doc.axiom) > 20 else None
        
        return LlmDocV2(
            type=v2_type,
            purpose=purpose,
            contract=contract,
            axiom=axiom
        )
    
    def _infer_type_from_path(self, file_path: Path, original_type: str) -> str:
        """Infer hierarchical type from file path."""
        path_str = str(file_path).lower()
        
        if 'service' in path_str or 'api' in path_str:
            return 'service.api'
        elif 'component' in path_str:
            return 'component.primitive'
        elif 'model' in path_str or 'entity' in path_str:
            return 'model.entity'
        elif 'config' in path_str:
            return 'config.app'
        elif 'util' in path_str or 'tool' in path_str:
            return 'util.function'
        else:
            return f'misc.{original_type}'
    
    def _create_purpose(self, v1_doc: LlmDocV1) -> str:
        """Create concise purpose from V1 fields."""
        # Priority: legend > key > infer from type
        if v1_doc.legend:
            purpose = v1_doc.legend
        elif v1_doc.key:
            purpose = v1_doc.key
        else:
            purpose = f"Handles {v1_doc.type} operations"
        
        # Clean and truncate to 40-80 characters
        purpose = re.sub(r'\s+', ' ', purpose).strip()
        if len(purpose) > 80:
            purpose = purpose[:77] + "..."
        
        # Ensure it starts with a verb
        if not re.match(r'^[A-Z][a-z]*s\b', purpose):
            purpose = f"Provides {purpose.lower()}"
        
        return purpose
    
    def _simplify_contract(self, contract: str) -> str:
        """Simplify contract to Input -> Output format."""
        # Look for common patterns and simplify
        contract = re.sub(r'\s+', ' ', contract).strip()
        
        # Try to extract input/output pattern
        if ' -> ' in contract:
            return contract  # Already in good format
        elif 'returns' in contract.lower():
            # Extract return type
            match = re.search(r'returns?\s+(\w+(?:\s+\w+)*)', contract, re.IGNORECASE)
            if match:
                return f"Input -> {match.group(1)}"
        
        # Fallback: truncate if too long
        if len(contract) > 60:
            contract = contract[:57] + "..."
        
        return contract
    
    def _format_v2_block(self, v2_doc: LlmDocV2, file_extension: str) -> str:
        """Format V2 LlmDoc as comment block."""
        lines = [
            f'@llm-type {v2_doc.type}',
            f'@llm-purpose {v2_doc.purpose}'
        ]
        
        if v2_doc.contract:
            lines.append(f'@llm-contract {v2_doc.contract}')
        
        if v2_doc.axiom:
            lines.append(f'@llm-axiom {v2_doc.axiom}')
        
        if v2_doc.deps:
            lines.append(f'@llm-deps {v2_doc.deps}')
        
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
    
    def generate_migration_report(self) -> str:
        """Generate migration report."""
        report = [
            "# LlmDocs V1 to V2 Migration Report",
            "",
            f"## Summary",
            f"- Files processed: {len(self.migrated_files)}",
            f"- Errors: {len(self.errors)}",
            "",
        ]
        
        if self.migrated_files:
            report.extend([
                "## Migrated Files",
                ""
            ])
            for file_path in self.migrated_files:
                report.append(f"- {file_path}")
            report.append("")
        
        if self.errors:
            report.extend([
                "## Errors",
                ""
            ])
            for error in self.errors:
                report.append(f"- {error}")
        
        return '\n'.join(report)

def main():
    """Main migration function."""
    project_root = Path.cwd()
    migrator = LlmDocsV2Migrator(project_root)
    
    print("🔄 Starting LlmDocs V1 to V2 migration...")
    stats = migrator.migrate_all_files()
    
    print(f"✅ Migration complete!")
    print(f"   Processed: {stats['processed']} files")
    print(f"   Migrated: {stats['migrated']} files")
    print(f"   Errors: {stats['errors']} files")
    
    # Generate report
    report = migrator.generate_migration_report()
    report_path = "docs/architecture/llmdocs-v2-migration-report.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"📄 Migration report saved to {report_path}")
    
    return 0 if stats['errors'] == 0 else 1

if __name__ == "__main__":
    exit(main())
