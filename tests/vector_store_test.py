import pytest
from langchain.embeddings import FakeEmbeddings

from codeqai.vector_store import VectorStore


@pytest.mark.usefixtures("vector_entries")
def test_index_documents(vector_entries):
    embeddings = FakeEmbeddings(size=1352)
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
    embeddings = FakeEmbeddings(size=1352)
    vector_store = VectorStore(name="test", embeddings=embeddings)
    vector_store.index_documents(vector_entries)
    vector_store.vector_cache = vector_cache
    print(len(vector_store.db.index_to_docstore_id))
    print(
        vector_store.db.index_to_docstore_id[
            len(vector_store.db.index_to_docstore_id) - 1
        ]
    )
    for vector_id in vector_store.db.index_to_docstore_id.values():
        vector_store.vector_cache[
            vector_store.db.docstore.search(vector_id).metadata["filename"]
        ].vector_ids.append(vector_id)
    vector_store.sync_documents(modified_vector_entries)
