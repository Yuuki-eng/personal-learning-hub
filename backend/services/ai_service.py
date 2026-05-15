import os
import json
import asyncio
from pathlib import Path
from typing import Optional
import numpy as np
import faiss
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from openai import OpenAI
from config import CHROMA_DIR, DOCUMENTS_DIR


class RAGService:
    def __init__(self):
        self.index_path = CHROMA_DIR / "faiss.index"
        self.docs_path = CHROMA_DIR / "docs.json"
        self.documents: list[dict] = []
        self.index: Optional[faiss.IndexFlatL2] = None
        self.dimension = 1536
        self._last_api_key = ""
        self._last_base_url = ""
        self._last_embedding_model = "text-embedding-3-small"
        self._load()

    def _load(self):
        if self.docs_path.exists():
            with open(self.docs_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
        if self.index_path.exists() and self.documents:
            self.index = faiss.read_index(str(self.index_path))
            self.dimension = self.index.d
        else:
            self.dimension = 1536
            self.index = faiss.IndexFlatL2(self.dimension)

    def _save(self):
        faiss.write_index(self.index, str(self.index_path))
        with open(self.docs_path, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False)

    def _get_client(self, api_key: str, base_url: str) -> OpenAI:
        return OpenAI(api_key=api_key, base_url=base_url)

    def _embed(self, texts: list[str], api_key: str, base_url: str, model: str = "text-embedding-3-small") -> list[list[float]]:
        client = self._get_client(api_key, base_url)
        resp = client.embeddings.create(input=texts, model=model)
        return [d.embedding for d in resp.data]

    def _add_document_sync(self, file_path: str, file_name: str, api_key: str, base_url: str, embedding_model: str = "text-embedding-3-small") -> int:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding="utf-8")

        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)

        if not chunks:
            return 0

        texts = [c.page_content for c in chunks]
        embeddings = self._embed(texts, api_key, base_url, embedding_model)
        vecs = np.array(embeddings, dtype="float32")

        if self.index.d != vecs.shape[1]:
            self.dimension = vecs.shape[1]
            self.index = faiss.IndexFlatL2(self.dimension)
            if self.documents:
                old_embs = [np.array(d["embedding"], dtype="float32") for d in self.documents if "embedding" in d]
                if old_embs:
                    self.index.add(np.array(old_embs, dtype="float32"))

        self.index.add(vecs)

        for i, chunk in enumerate(chunks):
            meta = {}
            if chunk.metadata:
                for k, v in chunk.metadata.items():
                    if isinstance(v, (str, int, float, bool, type(None))):
                        meta[k] = v
            self.documents.append({
                "content": chunk.page_content,
                "source": file_name,
                "metadata": meta,
                "embedding": embeddings[i],
            })

        self._save()
        return len(chunks)

    async def add_document(self, file_path: str, file_name: str, api_key: str, base_url: str, embedding_model: str = "text-embedding-3-small") -> int:
        self._last_api_key = api_key
        self._last_base_url = base_url
        self._last_embedding_model = embedding_model
        return await asyncio.to_thread(
            self._add_document_sync, file_path, file_name, api_key, base_url, embedding_model
        )

    def _search_sync(self, query: str, api_key: str, base_url: str, top_k: int = 3, embedding_model: str = "text-embedding-3-small") -> list[str]:
        if not self.documents or self.index.ntotal == 0:
            return []

        q_emb = np.array(self._embed([query], api_key, base_url, embedding_model), dtype="float32")
        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(q_emb, k)

        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.documents):
                results.append(self.documents[idx]["content"])
        return results

    async def search(self, query: str, api_key: str, base_url: str, top_k: int = 3, embedding_model: str = "text-embedding-3-small") -> list[str]:
        return await asyncio.to_thread(
            self._search_sync, query, api_key, base_url, top_k, embedding_model
        )

    def _remove_by_source_sync(self, source_name: str):
        new_docs = [d for d in self.documents if d.get("source") != source_name]
        removed_count = len(self.documents) - len(new_docs)
        self.documents = new_docs

        if self.documents:
            self.index = faiss.IndexFlatL2(self.dimension)
            stored_embs = [np.array(d["embedding"], dtype="float32") for d in self.documents if "embedding" in d]
            if stored_embs:
                self.index.add(np.array(stored_embs, dtype="float32"))
        else:
            self.index = faiss.IndexFlatL2(self.dimension)

        self._save()
        return removed_count

    async def remove_by_source(self, source_name: str):
        return await asyncio.to_thread(self._remove_by_source_sync, source_name)

    def get_documents_info(self) -> list[dict]:
        sources = {}
        for d in self.documents:
            name = d.get("source", "unknown")
            if name not in sources:
                sources[name] = 0
            sources[name] += 1
        return [{"name": k, "chunks_count": v} for k, v in sources.items()]

    def clear(self):
        self.documents = []
        self.index = faiss.IndexFlatL2(self.dimension)
        self._save()


rag_service = RAGService()
