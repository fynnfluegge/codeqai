from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores import FAISS

from codeqai.config import get_cache_path


class VectorStore:
    def __init__(
        self, name: str, embeddings: Embeddings, documents: list[Document] = []
    ):
        self.name = name
        self.embeddings = embeddings
        # TODO install faiss
        if not documents:
            self.db = FAISS.load_local(
                index_name=self.name,
                folder_path=get_cache_path(),
                embeddings=self.embeddings,
            )
        else:
            self.db = FAISS.from_documents(documents, embeddings)
            self.db.save_local(index_name=self.name, folder_path=get_cache_path())
        self.retriever = self.db.as_retriever(search_type="mmr", search_kwargs={"k": 8})
