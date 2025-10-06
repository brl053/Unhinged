#!/usr/bin/env python3
"""
Codebase Indexer for Context-Aware LLM Service
Indexes frontend codebase for UI component understanding
"""

import os
import logging
import time
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import hashlib
import json
import ast
import re

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class CodebaseIndexer:
    """
    Indexes frontend codebase for UI component understanding and context
    """
    
    def __init__(self, frontend_path: str = "/frontend", persist_directory: str = "/app/data/code_index"):
        self.frontend_path = Path(frontend_path)
        self.persist_directory = persist_directory
        self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            length_function=len
        )
        self.vectorstore = None
        self.file_hashes = {}
        self.component_registry = {}
        self.last_update = None
        
        # File extensions to index
        self.code_extensions = {
            '.tsx', '.ts', '.jsx', '.js', '.vue', '.svelte',
            '.css', '.scss', '.sass', '.less',
            '.json', '.yml', '.yaml'
        }
        
        # Ignore patterns
        self.ignore_patterns = {
            'node_modules', 'dist', 'build', '.git', 
            'coverage', 'test-results', '.next', '.nuxt'
        }
        
        # Initialize
        self._initialize_vectorstore()
        self._setup_file_watcher()
    
    def _initialize_vectorstore(self):
        """Initialize or load existing vector store"""
        try:
            if os.path.exists(self.persist_directory):
                logger.info("Loading existing codebase index...")
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                self._load_metadata()
            else:
                logger.info("Creating new codebase index...")
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                self._index_all_code()
                
        except Exception as e:
            logger.error(f"Failed to initialize codebase vectorstore: {e}")
            raise
    
    def _setup_file_watcher(self):
        """Setup file system watcher for automatic updates"""
        class CodeHandler(FileSystemEventHandler):
            def __init__(self, indexer):
                self.indexer = indexer
            
            def on_modified(self, event):
                if not event.is_directory and self.indexer._should_index_file(Path(event.src_path)):
                    self.indexer._handle_file_change(event.src_path)
            
            def on_created(self, event):
                if not event.is_directory and self.indexer._should_index_file(Path(event.src_path)):
                    self.indexer._handle_file_change(event.src_path)
            
            def on_deleted(self, event):
                if not event.is_directory:
                    self.indexer._handle_file_deletion(event.src_path)
        
        try:
            self.observer = Observer()
            self.observer.schedule(
                CodeHandler(self), 
                str(self.frontend_path), 
                recursive=True
            )
            self.observer.start()
            logger.info(f"Code file watcher started for {self.frontend_path}")
        except Exception as e:
            logger.warning(f"Could not start code file watcher: {e}")
            self.observer = None
    
    def _should_index_file(self, file_path: Path) -> bool:
        """Check if file should be indexed"""
        # Check extension
        if file_path.suffix.lower() not in self.code_extensions:
            return False
        
        # Check ignore patterns
        for part in file_path.parts:
            if part in self.ignore_patterns:
                return False
        
        return True
    
    def _index_all_code(self):
        """Index all code files in the frontend directory"""
        if not self.frontend_path.exists():
            logger.warning(f"Frontend path {self.frontend_path} does not exist")
            return
        
        logger.info(f"Indexing all code files in {self.frontend_path}")
        start_time = time.time()
        indexed_count = 0
        
        for file_path in self.frontend_path.rglob('*'):
            if file_path.is_file() and self._should_index_file(file_path):
                try:
                    self._index_code_file(file_path)
                    indexed_count += 1
                except Exception as e:
                    logger.error(f"Failed to index {file_path}: {e}")
        
        # Persist the vectorstore
        if self.vectorstore:
            self.vectorstore.persist()
        
        self._save_metadata()
        self.last_update = time.time()
        
        duration = time.time() - start_time
        logger.info(f"Indexed {indexed_count} code files in {duration:.2f}s")
    
    def _index_code_file(self, file_path: Path):
        """Index a single code file"""
        try:
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)
            
            # Skip if file hasn't changed
            if str(file_path) in self.file_hashes and self.file_hashes[str(file_path)] == file_hash:
                return
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Skip binary files
                return
            
            # Extract metadata based on file type
            metadata = self._extract_file_metadata(file_path, content)
            
            # Create document
            doc = Document(
                page_content=content,
                metadata={
                    'source': str(file_path),
                    'filename': file_path.name,
                    'directory': str(file_path.parent),
                    'file_type': file_path.suffix,
                    'indexed_at': time.time(),
                    'file_hash': file_hash,
                    **metadata
                }
            )
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Remove existing chunks for this file
            if self.vectorstore:
                existing_docs = self.vectorstore.get(where={"source": str(file_path)})
                if existing_docs['ids']:
                    self.vectorstore.delete(ids=existing_docs['ids'])
            
            # Add new chunks
            if chunks and self.vectorstore:
                self.vectorstore.add_documents(chunks)
            
            # Update file hash
            self.file_hashes[str(file_path)] = file_hash
            
            # Update component registry if it's a component file
            if metadata.get('is_component'):
                self.component_registry[metadata['component_name']] = {
                    'file_path': str(file_path),
                    'component_type': metadata.get('component_type', 'unknown'),
                    'props': metadata.get('props', []),
                    'exports': metadata.get('exports', [])
                }
            
            logger.debug(f"Indexed {file_path} ({len(chunks)} chunks)")
            
        except Exception as e:
            logger.error(f"Failed to index code file {file_path}: {e}")
            raise
    
    def _extract_file_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Extract metadata from code file"""
        metadata = {}
        
        if file_path.suffix in ['.tsx', '.jsx']:
            metadata.update(self._extract_react_metadata(file_path, content))
        elif file_path.suffix in ['.ts', '.js']:
            metadata.update(self._extract_js_metadata(file_path, content))
        elif file_path.suffix in ['.css', '.scss', '.sass', '.less']:
            metadata.update(self._extract_style_metadata(file_path, content))
        elif file_path.suffix == '.json':
            metadata.update(self._extract_json_metadata(file_path, content))
        
        return metadata
    
    def _extract_react_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Extract metadata from React component files"""
        metadata = {
            'language': 'typescript' if file_path.suffix == '.tsx' else 'javascript',
            'framework': 'react'
        }
        
        # Check if it's a component file
        component_patterns = [
            r'export\s+default\s+function\s+(\w+)',
            r'export\s+default\s+(\w+)',
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',
            r'function\s+(\w+)\s*\([^)]*\)\s*{',
        ]
        
        for pattern in component_patterns:
            match = re.search(pattern, content)
            if match:
                metadata['is_component'] = True
                metadata['component_name'] = match.group(1)
                break
        
        # Extract imports
        import_matches = re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', content)
        metadata['imports'] = import_matches
        
        # Extract props (simplified)
        props_match = re.search(r'interface\s+\w*Props\s*{([^}]+)}', content)
        if props_match:
            props_content = props_match.group(1)
            props = re.findall(r'(\w+)(?:\?)?:\s*([^;,\n]+)', props_content)
            metadata['props'] = [{'name': name, 'type': type_} for name, type_ in props]
        
        # Check for hooks usage
        hooks = re.findall(r'use(\w+)', content)
        metadata['hooks_used'] = list(set(hooks))
        
        return metadata
    
    def _extract_js_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Extract metadata from JavaScript/TypeScript files"""
        metadata = {
            'language': 'typescript' if file_path.suffix == '.ts' else 'javascript'
        }
        
        # Extract exports
        export_matches = re.findall(r'export\s+(?:const|function|class)\s+(\w+)', content)
        metadata['exports'] = export_matches
        
        # Extract imports
        import_matches = re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', content)
        metadata['imports'] = import_matches
        
        return metadata
    
    def _extract_style_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Extract metadata from style files"""
        metadata = {
            'language': 'css',
            'style_type': file_path.suffix[1:]  # Remove the dot
        }
        
        # Extract CSS classes
        class_matches = re.findall(r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)', content)
        metadata['css_classes'] = list(set(class_matches))
        
        # Extract CSS variables
        var_matches = re.findall(r'--([a-zA-Z_-][a-zA-Z0-9_-]*)', content)
        metadata['css_variables'] = list(set(var_matches))
        
        return metadata
    
    def _extract_json_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Extract metadata from JSON files"""
        metadata = {'language': 'json'}
        
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                metadata['json_keys'] = list(data.keys())
                
                # Special handling for package.json
                if file_path.name == 'package.json':
                    metadata['is_package_json'] = True
                    metadata['dependencies'] = list(data.get('dependencies', {}).keys())
                    metadata['dev_dependencies'] = list(data.get('devDependencies', {}).keys())
                    
        except json.JSONDecodeError:
            pass
        
        return metadata
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def _save_metadata(self):
        """Save metadata to disk"""
        try:
            metadata_dir = Path(self.persist_directory)
            metadata_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file hashes
            with open(metadata_dir / "file_hashes.json", 'w') as f:
                json.dump(self.file_hashes, f, indent=2)
            
            # Save component registry
            with open(metadata_dir / "component_registry.json", 'w') as f:
                json.dump(self.component_registry, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save codebase metadata: {e}")
    
    def _load_metadata(self):
        """Load metadata from disk"""
        try:
            metadata_dir = Path(self.persist_directory)
            
            # Load file hashes
            hash_file = metadata_dir / "file_hashes.json"
            if hash_file.exists():
                with open(hash_file, 'r') as f:
                    self.file_hashes = json.load(f)
            
            # Load component registry
            registry_file = metadata_dir / "component_registry.json"
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    self.component_registry = json.load(f)
                    
        except Exception as e:
            logger.error(f"Failed to load codebase metadata: {e}")
            self.file_hashes = {}
            self.component_registry = {}
    
    def _handle_file_change(self, file_path: str):
        """Handle file change event"""
        try:
            path = Path(file_path)
            if self._should_index_file(path):
                logger.info(f"Reindexing changed code file: {file_path}")
                self._index_code_file(path)
                if self.vectorstore:
                    self.vectorstore.persist()
                self._save_metadata()
                
        except Exception as e:
            logger.error(f"Failed to handle code file change {file_path}: {e}")
    
    def _handle_file_deletion(self, file_path: str):
        """Handle file deletion event"""
        try:
            if self.vectorstore:
                # Remove documents for deleted file
                existing_docs = self.vectorstore.get(where={"source": file_path})
                if existing_docs['ids']:
                    self.vectorstore.delete(ids=existing_docs['ids'])
                    self.vectorstore.persist()
            
            # Remove from metadata
            if file_path in self.file_hashes:
                del self.file_hashes[file_path]
            
            # Remove from component registry
            to_remove = []
            for comp_name, comp_info in self.component_registry.items():
                if comp_info['file_path'] == file_path:
                    to_remove.append(comp_name)
            
            for comp_name in to_remove:
                del self.component_registry[comp_name]
            
            self._save_metadata()
            logger.info(f"Removed deleted code file from index: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to handle code file deletion {file_path}: {e}")
    
    def search_codebase(self, query: str, k: int = 5, file_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search codebase for relevant content"""
        try:
            if not self.vectorstore:
                return []
            
            # Build filter if file types specified
            where_filter = {}
            if file_types:
                where_filter["file_type"] = {"$in": file_types}
            
            # Perform similarity search
            if where_filter:
                results = self.vectorstore.similarity_search_with_score(query, k=k, where=where_filter)
            else:
                results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'relevance_score': float(score),
                    'source': doc.metadata.get('source', 'unknown'),
                    'filename': doc.metadata.get('filename', 'unknown'),
                    'file_type': doc.metadata.get('file_type', 'unknown')
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Codebase search failed: {e}")
            return []
    
    def get_component_info(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific component"""
        return self.component_registry.get(component_name)
    
    def list_components(self) -> List[Dict[str, Any]]:
        """List all registered components"""
        return [
            {'name': name, **info} 
            for name, info in self.component_registry.items()
        ]
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get indexing statistics"""
        try:
            stats = {
                'total_files': len(self.file_hashes),
                'total_components': len(self.component_registry),
                'last_update': self.last_update,
                'frontend_path': str(self.frontend_path),
                'persist_directory': self.persist_directory,
                'file_watcher_active': self.observer is not None and self.observer.is_alive(),
                'indexed_extensions': list(self.code_extensions)
            }
            
            if self.vectorstore:
                collection = self.vectorstore._collection
                stats['total_chunks'] = collection.count()
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get codebase index stats: {e}")
            return {}
    
    def shutdown(self):
        """Shutdown the indexer"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        if self.vectorstore:
            self.vectorstore.persist()

# Global codebase indexer instance
codebase_indexer = CodebaseIndexer()
