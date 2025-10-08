"""
Vector Store for SideDesk
ChromaDB integration for semantic search and RAG
Created by: Claude Sonnet 4.5
Date: 10-06-25
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
import os


class VectorStore:
    """
    Vector database wrapper using ChromaDB.
    Handles document storage and semantic search.
    """

    def __init__(
        self,
        persist_directory: str = "~/.sidedesk/embeddings",
        collection_name: str = "sidedesk_knowledge",
        embedding_model: str = "nomic-embed-text"
    ):
        """
        Initialize vector store.

        Args:
            persist_directory: Directory to store embeddings
            collection_name: Name of the collection
            embedding_model: Ollama model for embeddings
        """
        self.persist_directory = os.path.expanduser(
            persist_directory
        )
        self.collection_name = collection_name
        self.embedding_model = embedding_model

        os.makedirs(self.persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "SideDesk knowledge base"}
        )

    def AddDocuments(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        Add documents to vector store.

        Args:
            documents: List of document texts
            metadatas: Optional metadata for each document
            ids: Optional IDs for documents

        Returns:
            True if successful
        """
        try:
            if ids is None:
                ids = [f"doc_{i}" for i in range(len(documents))]

            if metadatas is None:
                metadatas = [{}] * len(documents)

            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception:
            return False

    def Search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Search query
            n_results: Number of results to return
            where: Optional metadata filter

        Returns:
            List of matching documents with metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )

            documents = []
            for i in range(len(results["ids"][0])):
                documents.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })

            return documents
        except Exception:
            return []

    def GetDocument(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document data or None
        """
        try:
            result = self.collection.get(ids=[doc_id])
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "document": result["documents"][0],
                    "metadata": result["metadatas"][0]
                }
            return None
        except Exception:
            return None

    def DeleteDocument(self, doc_id: str) -> bool:
        """
        Delete a document by ID.

        Args:
            doc_id: Document ID

        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception:
            return False

    def UpdateDocument(
        self,
        doc_id: str,
        document: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a document.

        Args:
            doc_id: Document ID
            document: New document text
            metadata: New metadata

        Returns:
            True if successful
        """
        try:
            update_args = {"ids": [doc_id]}
            if document is not None:
                update_args["documents"] = [document]
            if metadata is not None:
                update_args["metadatas"] = [metadata]

            self.collection.update(**update_args)
            return True
        except Exception:
            return False

    def Count(self) -> int:
        """
        Get number of documents in collection.

        Returns:
            Document count
        """
        try:
            return self.collection.count()
        except Exception:
            return 0

    def Clear(self) -> bool:
        """
        Clear all documents from collection.

        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = (
                self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={
                        "description": "SideDesk knowledge base"
                    }
                )
            )
            return True
        except Exception:
            return False

    def GetAllDocuments(
        self,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all documents from collection.

        Args:
            limit: Optional limit on number of documents

        Returns:
            List of all documents
        """
        try:
            result = self.collection.get(limit=limit)
            documents = []
            for i in range(len(result["ids"])):
                documents.append({
                    "id": result["ids"][i],
                    "document": result["documents"][i],
                    "metadata": result["metadatas"][i]
                })
            return documents
        except Exception:
            return []
