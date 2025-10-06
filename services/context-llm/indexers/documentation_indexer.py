#!/usr/bin/env python3
"""
Documentation Indexer for Context-Aware LLM Service
Indexes project documentation and provides contextual retrieval
"""

import os
import logging
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib
import json

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import markdown
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class DocumentationIndexer:
    """
    Indexes project documentation for contextual retrieval
    """
    
    def __init__(self, docs_path: str = "/docs", persist_directory: str = "/app/data/docs_index"):
        self.docs_path = Path(docs_path)
        self.persist_directory = persist_directory
        self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        self.vectorstore = None
        self.file_hashes = {}
        self.last_update = None
        
        # File type handlers
        self.handlers = {
            '.md': self._process_markdown,
            '.txt': self._process_text,
            '.json': self._process_json,
            '.yml': self._process_yaml,
            '.yaml': self._process_yaml
        }
        
        # Initialize
        self._initialize_vectorstore()
        self._setup_file_watcher()
    
    def _initialize_vectorstore(self):
        """Initialize or load existing vector store"""
        try:
            if os.path.exists(self.persist_directory):
                logger.info("Loading existing documentation index...")
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                self._load_file_hashes()
            else:
                logger.info("Creating new documentation index...")
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                self._index_all_documents()
                
        except Exception as e:
            logger.error(f"Failed to initialize vectorstore: {e}")
            raise
    
    def _setup_file_watcher(self):
        """Setup file system watcher for automatic updates"""
        class DocumentHandler(FileSystemEventHandler):
            def __init__(self, indexer):
                self.indexer = indexer
            
            def on_modified(self, event):
                if not event.is_directory:
                    self.indexer._handle_file_change(event.src_path)
            
            def on_created(self, event):
                if not event.is_directory:
                    self.indexer._handle_file_change(event.src_path)
            
            def on_deleted(self, event):
                if not event.is_directory:
                    self.indexer._handle_file_deletion(event.src_path)
        
        try:
            self.observer = Observer()
            self.observer.schedule(
                DocumentHandler(self), 
                str(self.docs_path), 
                recursive=True
            )
            self.observer.start()
            logger.info(f"File watcher started for {self.docs_path}")
        except Exception as e:
            logger.warning(f"Could not start file watcher: {e}")
            self.observer = None
    
    def _index_all_documents(self):
        """Index all documents in the documentation directory"""
        if not self.docs_path.exists():
            logger.warning(f"Documentation path {self.docs_path} does not exist")
            return
        
        logger.info(f"Indexing all documents in {self.docs_path}")
        start_time = time.time()
        indexed_count = 0
        
        for file_path in self.docs_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.handlers:
                try:
                    self._index_file(file_path)
                    indexed_count += 1
                except Exception as e:
                    logger.error(f"Failed to index {file_path}: {e}")
        
        # Persist the vectorstore
        if self.vectorstore:
            self.vectorstore.persist()
        
        self._save_file_hashes()
        self.last_update = time.time()
        
        duration = time.time() - start_time
        logger.info(f"Indexed {indexed_count} documents in {duration:.2f}s")
    
    def _index_file(self, file_path: Path):
        """Index a single file"""
        try:
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)
            
            # Skip if file hasn't changed
            if str(file_path) in self.file_hashes and self.file_hashes[str(file_path)] == file_hash:
                return
            
            # Process file based on extension
            handler = self.handlers.get(file_path.suffix.lower())
            if not handler:
                return
            
            content = handler(file_path)
            if not content:
                return
            
            # Create document
            doc = Document(
                page_content=content,
                metadata={
                    'source': str(file_path),
                    'filename': file_path.name,
                    'directory': str(file_path.parent),
                    'file_type': file_path.suffix,
                    'indexed_at': time.time(),
                    'file_hash': file_hash
                }
            )
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Remove existing chunks for this file
            if self.vectorstore:
                # Get existing documents for this file
                existing_docs = self.vectorstore.get(where={"source": str(file_path)})
                if existing_docs['ids']:
                    self.vectorstore.delete(ids=existing_docs['ids'])
            
            # Add new chunks
            if chunks and self.vectorstore:
                self.vectorstore.add_documents(chunks)
            
            # Update file hash
            self.file_hashes[str(file_path)] = file_hash
            
            logger.debug(f"Indexed {file_path} ({len(chunks)} chunks)")
            
        except Exception as e:
            logger.error(f"Failed to index file {file_path}: {e}")
            raise
    
    def _process_markdown(self, file_path: Path) -> str:
        """Process markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert markdown to text while preserving structure
            html = markdown.markdown(content)
            # For now, just return the raw markdown as it's more readable
            return content
            
        except Exception as e:
            logger.error(f"Failed to process markdown {file_path}: {e}")
            return ""
    
    def _process_text(self, file_path: Path) -> str:
        """Process text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to process text {file_path}: {e}")
            return ""
    
    def _process_json(self, file_path: Path) -> str:
        """Process JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert JSON to readable text
            return f"JSON file: {file_path.name}\n\n{json.dumps(data, indent=2)}"
            
        except Exception as e:
            logger.error(f"Failed to process JSON {file_path}: {e}")
            return ""
    
    def _process_yaml(self, file_path: Path) -> str:
        """Process YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return f"YAML file: {file_path.name}\n\n{content}"
            
        except Exception as e:
            logger.error(f"Failed to process YAML {file_path}: {e}")
            return ""
    
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
    
    def _save_file_hashes(self):
        """Save file hashes to disk"""
        try:
            hash_file = Path(self.persist_directory) / "file_hashes.json"
            hash_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(hash_file, 'w') as f:
                json.dump(self.file_hashes, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save file hashes: {e}")
    
    def _load_file_hashes(self):
        """Load file hashes from disk"""
        try:
            hash_file = Path(self.persist_directory) / "file_hashes.json"
            if hash_file.exists():
                with open(hash_file, 'r') as f:
                    self.file_hashes = json.load(f)
                    
        except Exception as e:
            logger.error(f"Failed to load file hashes: {e}")
            self.file_hashes = {}
    
    def _handle_file_change(self, file_path: str):
        """Handle file change event"""
        try:
            path = Path(file_path)
            if path.suffix.lower() in self.handlers:
                logger.info(f"Reindexing changed file: {file_path}")
                self._index_file(path)
                if self.vectorstore:
                    self.vectorstore.persist()
                self._save_file_hashes()
                
        except Exception as e:
            logger.error(f"Failed to handle file change {file_path}: {e}")
    
    def _handle_file_deletion(self, file_path: str):
        """Handle file deletion event"""
        try:
            if self.vectorstore:
                # Remove documents for deleted file
                existing_docs = self.vectorstore.get(where={"source": file_path})
                if existing_docs['ids']:
                    self.vectorstore.delete(ids=existing_docs['ids'])
                    self.vectorstore.persist()
            
            # Remove from file hashes
            if file_path in self.file_hashes:
                del self.file_hashes[file_path]
                self._save_file_hashes()
                
            logger.info(f"Removed deleted file from index: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to handle file deletion {file_path}: {e}")
    
    def search_documentation(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search documentation for relevant content"""
        try:
            if not self.vectorstore:
                return []
            
            # Perform similarity search
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'relevance_score': float(score),
                    'source': doc.metadata.get('source', 'unknown'),
                    'filename': doc.metadata.get('filename', 'unknown')
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Documentation search failed: {e}")
            return []
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get indexing statistics"""
        try:
            stats = {
                'total_files': len(self.file_hashes),
                'last_update': self.last_update,
                'docs_path': str(self.docs_path),
                'persist_directory': self.persist_directory,
                'file_watcher_active': self.observer is not None and self.observer.is_alive()
            }
            
            if self.vectorstore:
                # Get collection info
                collection = self.vectorstore._collection
                stats['total_chunks'] = collection.count()
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {}
    
    def shutdown(self):
        """Shutdown the indexer"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        if self.vectorstore:
            self.vectorstore.persist()

# Global documentation indexer instance
documentation_indexer = DocumentationIndexer()
