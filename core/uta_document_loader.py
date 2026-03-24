"""
Document Ingestion Pipeline

Loads knowledge base documents from various sources and formats,
processes them into chunks, and ingests them into the vector store.
"""

import os
import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass

from core.uta_vectorstore_base import Document, DocumentType

logger = logging.getLogger(__name__)


@dataclass
class ChunkConfig:
    """Configuration for document chunking."""
    chunk_size: int = 800  # Characters per chunk (reduced for better semantic coherence)
    chunk_overlap: int = 150  # Overlap between chunks
    min_chunk_size: int = 100  # Minimum chunk size to keep
    separator: str = "\n\n"  # Primary separator for splitting
    # Hierarchical separators for semantic chunking (tried in order)
    semantic_separators: tuple = (
        "\n## ",      # H2 headers (major sections)
        "\n### ",     # H3 headers (subsections)  
        "\n#### ",    # H4 headers
        "\n---\n",    # Horizontal rules
        "\n\n",       # Double newline (paragraphs)
        "\n",         # Single newline
        ". ",         # Sentence boundaries
        " ",          # Words (last resort)
    )
    add_title_prefix: bool = True  # Prepend section titles to chunks for context


class DocumentLoader:
    """
    Loads documents from files and directories.
    
    Supports:
    - Markdown files (.md)
    - JSON files (.json)
    - Text files (.txt)
    - YAML files (.yaml, .yml)
    """
    
    @staticmethod
    def load_file(file_path: str) -> Dict[str, Any]:
        """
        Load a single file and return its content with metadata.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict with 'content', 'metadata', and 'doc_type'
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix == ".md":
            return DocumentLoader._load_markdown(path)
        elif suffix == ".json":
            return DocumentLoader._load_json(path)
        elif suffix in [".yaml", ".yml"]:
            return DocumentLoader._load_yaml(path)
        elif suffix == ".txt":
            return DocumentLoader._load_text(path)
        else:
            logger.warning(f"Unsupported file type: {suffix}")
            return DocumentLoader._load_text(path)
    
    @staticmethod
    def _load_markdown(path: Path) -> Dict[str, Any]:
        """Load markdown file."""
        content = path.read_text(encoding="utf-8")
        
        # Extract metadata from markdown
        metadata = {
            "source": str(path),
            "filename": path.name,
            "format": "markdown",
        }
        
        # Try to extract title from first heading
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            metadata["title"] = title_match.group(1)
        
        # Try to extract document ID from filename
        doc_id_match = re.match(r"(SOP|PLAYBOOK|KB|KI)-[\w-]+", path.stem, re.IGNORECASE)
        if doc_id_match:
            metadata["doc_id"] = doc_id_match.group(0)
        
        # Determine doc_type from filename or content
        doc_type = DocumentLoader._infer_doc_type(path.name, content)
        
        # Extract category from path or content
        category = DocumentLoader._infer_category(path, content)
        if category:
            metadata["category"] = category
        
        return {
            "content": content,
            "metadata": metadata,
            "doc_type": doc_type,
        }
    
    @staticmethod
    def _load_json(path: Path) -> Dict[str, Any]:
        """Load JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        metadata = {
            "source": str(path),
            "filename": path.name,
            "format": "json",
        }
        
        # Handle different JSON structures
        if "error_codes" in data:
            # Error codes file
            return {
                "content": json.dumps(data, indent=2),
                "metadata": metadata,
                "doc_type": DocumentType.ERROR_CODE,
                "structured_data": data,
            }
        elif "configuration_checks" in data:
            # Config checks file
            return {
                "content": json.dumps(data, indent=2),
                "metadata": metadata,
                "doc_type": DocumentType.CONFIG_CHECK,
                "structured_data": data,
            }
        elif "tickets" in data:
            # Sample tickets file
            return {
                "content": json.dumps(data, indent=2),
                "metadata": metadata,
                "doc_type": DocumentType.KB_ARTICLE,
                "structured_data": data,
            }
        else:
            return {
                "content": json.dumps(data, indent=2),
                "metadata": metadata,
                "doc_type": DocumentType.KB_ARTICLE,
            }
    
    @staticmethod
    def _load_yaml(path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            content = yaml.dump(data, default_flow_style=False)
        except ImportError:
            # Fallback to reading as text
            content = path.read_text(encoding="utf-8")
            data = {}
        
        metadata = {
            "source": str(path),
            "filename": path.name,
            "format": "yaml",
        }
        
        return {
            "content": content,
            "metadata": metadata,
            "doc_type": DocumentType.KB_ARTICLE,
        }
    
    @staticmethod
    def _load_text(path: Path) -> Dict[str, Any]:
        """Load text file."""
        content = path.read_text(encoding="utf-8")
        
        metadata = {
            "source": str(path),
            "filename": path.name,
            "format": "text",
        }
        
        return {
            "content": content,
            "metadata": metadata,
            "doc_type": DocumentType.KB_ARTICLE,
        }
    
    @staticmethod
    def _infer_doc_type(filename: str, content: str) -> DocumentType:
        """Infer document type from filename and content."""
        filename_lower = filename.lower()
        
        if "sop" in filename_lower:
            return DocumentType.SOP
        elif "playbook" in filename_lower:
            return DocumentType.PLAYBOOK
        elif "known_issue" in filename_lower or "ki-" in filename_lower:
            return DocumentType.KNOWN_ISSUE
        elif "error_code" in filename_lower:
            return DocumentType.ERROR_CODE
        elif "config" in filename_lower and "check" in filename_lower:
            return DocumentType.CONFIG_CHECK
        elif "expert" in filename_lower or "insight" in filename_lower:
            return DocumentType.EXPERT_INSIGHT
        else:
            return DocumentType.KB_ARTICLE
    
    @staticmethod
    def _infer_category(path: Path, content: str) -> Optional[str]:
        """Infer category from path or content."""
        # Check path components
        path_str = str(path).lower()
        
        categories = ["routing", "licensing", "connectivity", "migration", "ui", "integration"]
        for cat in categories:
            if cat in path_str:
                return cat
        
        # Check content for category indicators
        content_lower = content.lower()
        category_keywords = {
            "routing": ["queue", "routing", "skill", "overflow", "agent assignment"],
            "licensing": ["license", "sku", "feature flag", "permission", "role"],
            "connectivity": ["network", "firewall", "connection", "websocket", "timeout"],
            "migration": ["upgrade", "migration", "version", "deprecat"],
        }
        
        for cat, keywords in category_keywords.items():
            if any(kw in content_lower for kw in keywords):
                return cat
        
        return None


class DocumentChunker:
    """
    Splits documents into smaller chunks for vector storage.
    """
    
    def __init__(self, config: Optional[ChunkConfig] = None):
        """Initialize chunker with configuration."""
        self.config = config or ChunkConfig()
    
    def chunk_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        doc_type: DocumentType,
        doc_id_prefix: str,
    ) -> List[Document]:
        """
        Split a document into chunks.
        
        Args:
            content: Document content
            metadata: Document metadata
            doc_type: Type of document
            doc_id_prefix: Prefix for chunk IDs
            
        Returns:
            List of Document objects (chunks)
        """
        # For structured data like error codes, use special chunking
        if doc_type == DocumentType.ERROR_CODE:
            return self._chunk_error_codes(content, metadata, doc_id_prefix)
        elif doc_type == DocumentType.CONFIG_CHECK:
            return self._chunk_config_checks(content, metadata, doc_id_prefix)
        else:
            return self._chunk_text(content, metadata, doc_type, doc_id_prefix)
    
    def _chunk_text(
        self,
        content: str,
        metadata: Dict[str, Any],
        doc_type: DocumentType,
        doc_id_prefix: str,
    ) -> List[Document]:
        """
        Chunk text content using recursive semantic splitting.
        
        Uses hierarchical separators to maintain semantic coherence.
        Preserves section titles/headers as context in each chunk.
        """
        chunks = []
        
        # Extract document title if present
        doc_title = metadata.get("title", "")
        
        # Use recursive semantic chunking
        text_chunks = self._recursive_split(
            content, 
            list(self.config.semantic_separators),
            self.config.chunk_size
        )
        
        # Track section context for better embeddings
        current_section = doc_title
        
        for chunk_index, chunk_text in enumerate(text_chunks):
            chunk_text = chunk_text.strip()
            if len(chunk_text) < self.config.min_chunk_size:
                continue
            
            # Update section context from headers
            header_match = re.search(r'^#+\s+(.+)$', chunk_text, re.MULTILINE)
            if header_match:
                current_section = header_match.group(1)
            
            # Optionally prepend context to improve embeddings
            enriched_text = chunk_text
            if self.config.add_title_prefix and current_section:
                if not chunk_text.startswith("#"):
                    enriched_text = f"[Section: {current_section}]\n\n{chunk_text}"
            
            chunks.append(self._create_chunk(
                enriched_text,
                {**metadata, "section": current_section},
                doc_type,
                doc_id_prefix,
                chunk_index
            ))
        
        # Add overlap between chunks
        if len(chunks) > 1 and self.config.chunk_overlap > 0:
            chunks = self._add_overlap_context(chunks)
        
        return chunks
    
    def _recursive_split(
        self,
        text: str,
        separators: List[str],
        chunk_size: int,
    ) -> List[str]:
        """
        Recursively split text using hierarchical separators.
        
        Tries to split by the most meaningful separator first,
        falling back to finer-grained separators if needed.
        """
        if not text or len(text) <= chunk_size:
            return [text] if text.strip() else []
        
        if not separators:
            # Last resort: hard split by character
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        separator = separators[0]
        remaining_separators = separators[1:]
        
        # Split by current separator
        if separator in text:
            parts = text.split(separator)
            # Re-add separator to maintain context (except for space)
            if separator.strip():
                parts = [separator + p if i > 0 else p for i, p in enumerate(parts)]
        else:
            # Separator not found, try next level
            return self._recursive_split(text, remaining_separators, chunk_size)
        
        # Merge small parts, recursively split large ones
        result = []
        current_chunk = ""
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            if len(current_chunk) + len(part) <= chunk_size:
                current_chunk = f"{current_chunk}\n\n{part}".strip() if current_chunk else part
            else:
                if current_chunk:
                    result.append(current_chunk)
                
                if len(part) > chunk_size:
                    # Part is too large, recursively split with finer separators
                    sub_parts = self._recursive_split(part, remaining_separators, chunk_size)
                    result.extend(sub_parts)
                    current_chunk = ""
                else:
                    current_chunk = part
        
        if current_chunk:
            result.append(current_chunk)
        
        return result
    
    def _add_overlap_context(self, chunks: List[Document]) -> List[Document]:
        """Add overlapping context between adjacent chunks."""
        if len(chunks) <= 1:
            return chunks
        
        for i in range(1, len(chunks)):
            prev_content = chunks[i-1].content
            curr_content = chunks[i].content
            
            # Get last N chars from previous chunk
            overlap = prev_content[-self.config.chunk_overlap:]
            
            # Find a clean break point
            break_points = ['. ', '\n', ', ']
            for bp in break_points:
                idx = overlap.find(bp)
                if idx != -1:
                    overlap = overlap[idx+len(bp):]
                    break
            
            if overlap.strip():
                chunks[i] = Document(
                    id=chunks[i].id,
                    content=f"[...{overlap}]\n\n{curr_content}",
                    metadata=chunks[i].metadata,
                    doc_type=chunks[i].doc_type,
                )
        
        return chunks
    
    def _chunk_error_codes(
        self,
        content: str,
        metadata: Dict[str, Any],
        doc_id_prefix: str,
    ) -> List[Document]:
        """Create individual documents for each error code."""
        chunks = []
        
        try:
            data = json.loads(content)
            error_codes = data.get("error_codes", {})
            
            for category, codes in error_codes.items():
                for code_id, code_data in codes.items():
                    # Create a readable text representation
                    text = self._format_error_code(code_data)
                    
                    chunk_metadata = {
                        **metadata,
                        "error_code": code_id,
                        "category": code_data.get("category", category.lower()),
                        "severity": code_data.get("severity", "medium"),
                    }
                    
                    chunks.append(Document(
                        id=f"{doc_id_prefix}_error_{code_id}",
                        content=text,
                        metadata=chunk_metadata,
                        doc_type=DocumentType.ERROR_CODE,
                    ))
        except json.JSONDecodeError:
            # Fallback to text chunking
            logger.warning("Could not parse error codes JSON, using text chunking")
            return self._chunk_text(content, metadata, DocumentType.ERROR_CODE, doc_id_prefix)
        
        return chunks
    
    def _chunk_config_checks(
        self,
        content: str,
        metadata: Dict[str, Any],
        doc_id_prefix: str,
    ) -> List[Document]:
        """Create individual documents for each configuration check."""
        chunks = []
        
        try:
            data = json.loads(content)
            config_checks = data.get("configuration_checks", {})
            
            for category, checks in config_checks.items():
                for check in checks:
                    # Create a readable text representation
                    text = self._format_config_check(check)
                    
                    chunk_metadata = {
                        **metadata,
                        "check_id": check.get("id", ""),
                        "category": category,
                        "priority": check.get("priority", "medium"),
                    }
                    
                    chunks.append(Document(
                        id=f"{doc_id_prefix}_check_{check.get('id', '')}",
                        content=text,
                        metadata=chunk_metadata,
                        doc_type=DocumentType.CONFIG_CHECK,
                    ))
        except json.JSONDecodeError:
            logger.warning("Could not parse config checks JSON, using text chunking")
            return self._chunk_text(content, metadata, DocumentType.CONFIG_CHECK, doc_id_prefix)
        
        return chunks
    
    def _format_error_code(self, code_data: Dict[str, Any]) -> str:
        """Format error code data as readable text."""
        lines = [
            f"Error Code: {code_data.get('code', 'Unknown')}",
            f"Category: {code_data.get('category', 'Unknown')}",
            f"Meaning: {code_data.get('meaning', 'Unknown')}",
            f"Description: {code_data.get('description', '')}",
            "",
            "Common Causes:",
        ]
        
        for cause in code_data.get("common_causes", []):
            lines.append(f"  - {cause}")
        
        lines.append("")
        lines.append("Recommended Actions:")
        
        for action in code_data.get("recommended_actions", []):
            lines.append(f"  - {action}")
        
        if code_data.get("related_sop"):
            lines.append(f"\nRelated SOP: {code_data['related_sop']}")
        
        if code_data.get("kb_article"):
            lines.append(f"KB Article: {code_data['kb_article']}")
        
        return "\n".join(lines)
    
    def _format_config_check(self, check: Dict[str, Any]) -> str:
        """Format configuration check as readable text."""
        lines = [
            f"Configuration Check: {check.get('name', 'Unknown')}",
            f"ID: {check.get('id', 'Unknown')}",
            f"Priority: {check.get('priority', 'medium')}",
            f"Description: {check.get('description', '')}",
            "",
            "Applicable Signals:",
        ]
        
        for signal in check.get("applicable_signals", []):
            lines.append(f"  - {signal}")
        
        lines.append(f"\nHow to Check: {check.get('how_to_check', '')}")
        lines.append(f"Expected Result: {check.get('expected_result', '')}")
        
        lines.append("\nCommon Failures:")
        for failure in check.get("common_failures", []):
            lines.append(f"  - {failure}")
        
        lines.append(f"\nRemediation: {check.get('remediation', '')}")
        
        return "\n".join(lines)
    
    def _create_chunk(
        self,
        content: str,
        metadata: Dict[str, Any],
        doc_type: DocumentType,
        doc_id_prefix: str,
        chunk_index: int,
    ) -> Document:
        """Create a Document chunk."""
        return Document(
            id=f"{doc_id_prefix}_chunk_{chunk_index}",
            content=content.strip(),
            metadata={
                **metadata,
                "chunk_index": chunk_index,
            },
            doc_type=doc_type,
        )


class KnowledgeBaseIngester:
    """
    Main ingestion pipeline for loading the UTA knowledge base.
    
    Usage:
        from core import VectorStoreFactory
        from core.uta_document_loader import KnowledgeBaseIngester
        
        store = VectorStoreFactory.create("chroma")
        ingester = KnowledgeBaseIngester(store)
        
        # Ingest entire knowledge directory
        stats = ingester.ingest_directory("./data/uta_knowledge")
        print(f"Ingested {stats['documents']} documents in {stats['chunks']} chunks")
    """
    
    def __init__(
        self,
        vector_store,
        chunk_config: Optional[ChunkConfig] = None,
    ):
        """
        Initialize the ingester.
        
        Args:
            vector_store: VectorStore instance to ingest into
            chunk_config: Configuration for chunking
        """
        self.vector_store = vector_store
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker(chunk_config)
    
    def ingest_file(self, file_path: str) -> int:
        """
        Ingest a single file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Number of chunks created
        """
        logger.info(f"Ingesting file: {file_path}")
        
        # Load file
        file_data = self.loader.load_file(file_path)
        
        # Generate document ID prefix from filename
        path = Path(file_path)
        doc_id_prefix = path.stem.replace(" ", "_").replace("-", "_")
        
        # Chunk the document
        chunks = self.chunker.chunk_document(
            content=file_data["content"],
            metadata=file_data["metadata"],
            doc_type=file_data["doc_type"],
            doc_id_prefix=doc_id_prefix,
        )
        
        # Add to vector store
        if chunks:
            self.vector_store.add_documents(chunks)
            logger.info(f"Created {len(chunks)} chunks from {path.name}")
        
        return len(chunks)
    
    def ingest_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        extensions: Optional[List[str]] = None,
    ) -> Dict[str, int]:
        """
        Ingest all files in a directory.
        
        Args:
            directory_path: Path to the directory
            recursive: Whether to process subdirectories
            extensions: File extensions to process (default: .md, .json, .yaml, .yml, .txt)
            
        Returns:
            Statistics dict with 'files' and 'chunks' counts
        """
        extensions = extensions or [".md", ".json", ".yaml", ".yml", ".txt"]
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        logger.info(f"Ingesting directory: {directory_path}")
        
        stats = {"files": 0, "chunks": 0, "errors": 0}
        
        # Find files
        if recursive:
            files = list(directory.rglob("*"))
        else:
            files = list(directory.glob("*"))
        
        # Filter by extension
        files = [f for f in files if f.is_file() and f.suffix.lower() in extensions]
        
        logger.info(f"Found {len(files)} files to process")
        
        for file_path in files:
            try:
                chunks = self.ingest_file(str(file_path))
                stats["files"] += 1
                stats["chunks"] += chunks
            except Exception as e:
                logger.error(f"Error ingesting {file_path}: {e}")
                stats["errors"] += 1
        
        logger.info(
            f"Ingestion complete: {stats['files']} files, "
            f"{stats['chunks']} chunks, {stats['errors']} errors"
        )
        
        return stats
    
    def ingest_known_issues_separately(self, file_path: str) -> int:
        """
        Ingest known issues with special handling.
        Creates one document per known issue for precise retrieval.
        """
        logger.info(f"Ingesting known issues from: {file_path}")
        
        content = Path(file_path).read_text(encoding="utf-8")
        
        # Split by issue headers (### pattern followed by KI-XXXX)
        issue_pattern = r"####\s+(KI-\d{4}-\d{4}:.*?)(?=####\s+KI-|\Z)"
        issues = re.findall(issue_pattern, content, re.DOTALL)
        
        documents = []
        for issue_text in issues:
            # Extract issue ID
            id_match = re.match(r"(KI-\d{4}-\d{4})", issue_text)
            if id_match:
                issue_id = id_match.group(1)
            else:
                continue
            
            documents.append(Document(
                id=f"known_issue_{issue_id}",
                content=issue_text.strip(),
                metadata={
                    "source": file_path,
                    "issue_id": issue_id,
                },
                doc_type=DocumentType.KNOWN_ISSUE,
            ))
        
        if documents:
            self.vector_store.add_documents(documents)
            logger.info(f"Ingested {len(documents)} known issues")
        
        return len(documents)


# Convenience function for quick ingestion
def ingest_uta_knowledge_base(
    knowledge_dir: str = "./uta/knowledge",
    vector_provider: str = "chroma",
    persist_directory: Optional[str] = "./data/chroma",
) -> Dict[str, int]:
    """
    Quick function to ingest the entire UTA knowledge base.
    
    Args:
        knowledge_dir: Path to knowledge directory
        vector_provider: Vector store provider (chroma, cosmos, azure_search)
        persist_directory: Where to persist ChromaDB data
        
    Returns:
        Ingestion statistics
    """
    from core.uta_vectorstore_factory import VectorStoreFactory
    
    # Create vector store
    config = {}
    if vector_provider == "chroma":
        config = {"persist_directory": persist_directory}
    
    store = VectorStoreFactory.create(vector_provider, config)
    
    # Create ingester and run
    ingester = KnowledgeBaseIngester(store)
    stats = ingester.ingest_directory(knowledge_dir)
    
    return stats
