"""
FAISS Vector Database Service for Face Embeddings
"""

import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple, Optional
from app.core.config import settings


class FaissVectorDB:
    """
    FAISS-based vector database for storing and searching face embeddings
    """
    
    def __init__(
        self, 
        dimension: int = None,
        index_path: str = None,
        embeddings_path: str = None
    ):
        self.dimension = dimension or settings.FAISS_DIMENSION
        self.index_path = index_path or settings.FAISS_INDEX_PATH
        self.embeddings_path = embeddings_path or settings.FACE_EMBEDDINGS_PATH
        
        # Initialize or load index
        self.index = None
        self.student_ids = []  # Maps FAISS index to student IDs
        self.embeddings_data = {}  # Stores additional metadata
        
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        if os.path.exists(self.index_path) and os.path.exists(self.embeddings_path):
            self._load_index()
        else:
            self._create_index()
    
    def _create_index(self):
        """Create new FAISS index"""
        # Use L2 distance for face embeddings
        # For cosine similarity, embeddings should be normalized
        self.index = faiss.IndexFlatL2(self.dimension)
        # Alternatively use IndexFlatIP for inner product (cosine similarity with normalized vectors)
        # self.index = faiss.IndexFlatIP(self.dimension)
        
        self.student_ids = []
        self.embeddings_data = {}
        print(f"Created new FAISS index with dimension {self.dimension}")
    
    def _load_index(self):
        """Load existing FAISS index and metadata"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(self.index_path)
            
            # Load embeddings metadata
            with open(self.embeddings_path, 'rb') as f:
                data = pickle.load(f)
                self.student_ids = data.get('student_ids', [])
                self.embeddings_data = data.get('embeddings_data', {})
            
            print(f"Loaded FAISS index with {self.index.ntotal} embeddings")
        except Exception as e:
            print(f"Error loading index: {e}")
            self._create_index()
    
    def save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)
            
            # Save metadata
            with open(self.embeddings_path, 'wb') as f:
                pickle.dump({
                    'student_ids': self.student_ids,
                    'embeddings_data': self.embeddings_data
                }, f)
            
            print(f"Saved FAISS index with {self.index.ntotal} embeddings")
        except Exception as e:
            print(f"Error saving index: {e}")
            raise
    
    def add_embedding(
        self, 
        embedding: np.ndarray, 
        student_id: int,
        metadata: dict = None
    ) -> int:
        """
        Add face embedding to the index
        
        Args:
            embedding: Face embedding vector
            student_id: Student ID
            metadata: Additional metadata
            
        Returns:
            Index ID of the added embedding
        """
        # Ensure embedding is the right shape
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        
        # Normalize embedding for cosine similarity
        embedding = embedding / np.linalg.norm(embedding, axis=1, keepdims=True)
        
        # Add to FAISS index
        self.index.add(embedding.astype(np.float32))
        
        # Store student ID mapping
        faiss_id = len(self.student_ids)
        self.student_ids.append(student_id)
        
        # Store metadata
        if metadata:
            self.embeddings_data[faiss_id] = metadata
        
        # Save to disk
        self.save_index()
        
        return faiss_id
    
    def add_multiple_embeddings(
        self,
        embeddings: List[np.ndarray],
        student_id: int,
        metadata: dict = None
    ):
        """
        Add multiple face embeddings for a single student
        
        Args:
            embeddings: List of face embedding vectors
            student_id: Student ID
            metadata: Additional metadata
        """
        for embedding in embeddings:
            self.add_embedding(embedding, student_id, metadata)
    
    def search(
        self, 
        query_embedding: np.ndarray, 
        k: int = 1,
        threshold: float = None
    ) -> List[Tuple[int, float]]:
        """
        Search for similar face embeddings
        
        Args:
            query_embedding: Query face embedding
            k: Number of nearest neighbors to return
            threshold: Distance threshold for matching
            
        Returns:
            List of (student_id, distance) tuples
        """
        print(f"[FAISS] Searching with {self.index.ntotal} embeddings in index")
        
        if self.index.ntotal == 0:
            print("[FAISS] Index is empty, no embeddings to search")
            return []
        
        threshold = threshold or settings.FACE_RECOGNITION_THRESHOLD
        print(f"[FAISS] Using threshold: {threshold}")
        
        # Ensure query is the right shape
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Normalize query
        query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
        
        # Search
        distances, indices = self.index.search(query_embedding.astype(np.float32), k)
        
        print(f"[FAISS] Search results - distances: {distances[0]}, indices: {indices[0]}")
        
        # Filter results by threshold and map to student IDs
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0 and idx < len(self.student_ids):
                # For L2 distance, lower is better
                # Convert to similarity score (0-1)
                similarity = 1 / (1 + dist)
                
                print(f"[FAISS] Found match - idx: {idx}, student_id: {self.student_ids[idx]}, dist: {dist:.4f}, similarity: {similarity:.4f}, threshold: {threshold}")
                
                if dist < threshold:
                    student_id = self.student_ids[idx]
                    results.append((student_id, float(similarity)))
                    print(f"[FAISS] Match accepted - student_id: {student_id}, similarity: {similarity:.4f}")
                else:
                    print(f"[FAISS] Match rejected - distance {dist:.4f} >= threshold {threshold}")
        
        print(f"[FAISS] Returning {len(results)} matches")
        return results
    
    def remove_student_embeddings(self, student_id: int):
        """
        Remove all embeddings for a student
        Note: FAISS doesn't support direct deletion, so we rebuild the index
        
        Args:
            student_id: Student ID to remove
        """
        # Get indices to keep
        keep_indices = [i for i, sid in enumerate(self.student_ids) if sid != student_id]
        
        if len(keep_indices) == len(self.student_ids):
            print(f"No embeddings found for student {student_id}")
            return
        
        # Rebuild index with remaining embeddings
        if len(keep_indices) > 0:
            # Extract embeddings to keep
            embeddings_to_keep = []
            for i in keep_indices:
                # Get embedding from index
                embedding = faiss.rev_swig_ptr(self.index.reconstruct(i), self.dimension)
                embeddings_to_keep.append(embedding)
            
            # Create new index
            self._create_index()
            
            # Re-add embeddings
            embeddings_array = np.array(embeddings_to_keep, dtype=np.float32)
            self.index.add(embeddings_array)
            
            # Update student IDs
            self.student_ids = [self.student_ids[i] for i in keep_indices]
            
            # Update metadata
            new_embeddings_data = {}
            for new_idx, old_idx in enumerate(keep_indices):
                if old_idx in self.embeddings_data:
                    new_embeddings_data[new_idx] = self.embeddings_data[old_idx]
            self.embeddings_data = new_embeddings_data
        else:
            # No embeddings left, create empty index
            self._create_index()
        
        # Save
        self.save_index()
        print(f"Removed embeddings for student {student_id}")
    
    def get_student_embedding_count(self, student_id: int) -> int:
        """Get number of embeddings for a student"""
        return self.student_ids.count(student_id)
    
    def get_total_embeddings(self) -> int:
        """Get total number of embeddings in the index"""
        return self.index.ntotal
    
    def clear_index(self):
        """Clear all embeddings from the index"""
        self._create_index()
        self.save_index()


# Global FAISS instance
_faiss_instance: Optional[FaissVectorDB] = None


def get_faiss_db() -> FaissVectorDB:
    """Get or create global FAISS instance"""
    global _faiss_instance
    if _faiss_instance is None:
        _faiss_instance = FaissVectorDB()
    return _faiss_instance
