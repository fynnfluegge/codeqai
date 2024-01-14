from pathlib import Path

import pytest
from langchain.embeddings import FakeEmbeddings

from codeqai.cache import get_cache_path
from codeqai.vector_store import VectorStore


@pytest.mark.usefixtures("vector_entries")
def test_index_documents(vector_entries):
    Path(get_cache_path()).mkdir(parents=True, exist_ok=True)
    embeddings = FakeEmbeddings(size=1024)
    vector_store = VectorStore(name="test", embeddings=embeddings)
    vector_store.index_documents(vector_entries)
    assert len(vector_store.vector_cache) == 3
    assert len(vector_store.db.index_to_docstore_id) == 4
    assert (
        vector_store.db.docstore.search(vector_store.db.index_to_docstore_id[0])
        == vector_entries[0]
    )
    assert (
        vector_store.db.docstore.search(vector_store.db.index_to_docstore_id[1])
        == vector_entries[1]
    )
    assert (
        vector_store.db.docstore.search(vector_store.db.index_to_docstore_id[2])
        == vector_entries[2]
    )
    assert (
        vector_store.db.docstore.search(vector_store.db.index_to_docstore_id[3])
        == vector_entries[3]
    )


@pytest.mark.usefixtures("modified_vector_entries", "vector_entries", "vector_cache")
def test_sync_documents(modified_vector_entries, vector_entries, vector_cache):
    Path(get_cache_path()).mkdir(parents=True, exist_ok=True)
    embeddings = FakeEmbeddings(size=1024)
    vector_store = VectorStore(name="test", embeddings=embeddings)
    vector_store.index_documents(vector_entries)
    assert len(vector_store.db.index_to_docstore_id) == 4
    vector_store.vector_cache = vector_cache

    for vector_id in vector_store.db.index_to_docstore_id.values():
        vector_store.vector_cache[
            vector_store.db.docstore.search(vector_id).metadata["filename"]
        ].vector_ids.append(vector_id)
    vector_store.sync_documents(modified_vector_entries)

    assert len(vector_store.db.index_to_docstore_id) == 5

    for vector_id in vector_store.db.index_to_docstore_id.values():
        filename = vector_store.db.docstore.search(vector_id).metadata["filename"]
        commit_hash = vector_store.db.docstore.search(vector_id).metadata["commit_hash"]
        cache_vector_ids = set(vector_store.vector_cache[filename].vector_ids)
        cache_commit_hash = vector_store.vector_cache[filename].commit_hash
        assert vector_id in cache_vector_ids
        assert commit_hash == cache_commit_hash
