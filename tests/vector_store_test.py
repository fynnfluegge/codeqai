from pathlib import Path

import pytest
from langchain.schema import Document
from langchain_core.embeddings import FakeEmbeddings

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


def mock_get_commit_hash(file):
    if file == "test.py":
        return "1234567892"
    elif file == "fixed_test.py":
        return "1234567891"
    elif file == "modified_test.py":
        return "1234567893"
    elif file == "new_test.py":
        return "1234567894"
    else:
        return "1234567890"


def parse_code_files_for_db(files):
    if files == ["test.py"]:
        return [
            Document(
                page_content="This is a test document.",
                metadata={
                    "filename": "test.py",
                    "commit_hash": "1234567892",
                },
            ),
            Document(
                page_content="Some further text.",
                metadata={
                    "filename": "test.py",
                    "commit_hash": "1234567892",
                },
            ),
        ]
    elif files == ["new_test.py"]:
        return [
            Document(
                page_content="This is a new test document.",
                metadata={
                    "filename": "new_test.py",
                    "commit_hash": "1234567894",
                },
            )
        ]
    elif files == ["fixed_test.py"]:
        return [
            Document(
                page_content="This is another test document.",
                metadata={
                    "filename": "fixed_test.py",
                    "commit_hash": "1234567891",
                },
            )
        ]
    else:
        return [
            Document(
                page_content="This is another test document.",
                metadata={
                    "filename": "modified_test.py",
                    "commit_hash": "1234567893",
                },
            )
        ]


@pytest.mark.usefixtures("file_names", "vector_entries", "vector_cache")
def test_sync_documents(file_names, vector_entries, vector_cache, mocker):
    mocker.patch(
        "codeqai.vector_store.get_commit_hash", side_effect=mock_get_commit_hash
    )
    mocker.patch(
        "codeqai.vector_store.parse_code_files_for_db",
        side_effect=parse_code_files_for_db,
    )
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
    vector_store.sync_documents(file_names)

    assert len(vector_store.db.index_to_docstore_id) == 5

    for vector_id in vector_store.db.index_to_docstore_id.values():
        filename = vector_store.db.docstore.search(vector_id).metadata["filename"]
        commit_hash = vector_store.db.docstore.search(vector_id).metadata["commit_hash"]
        cache_vector_ids = set(vector_store.vector_cache[filename].vector_ids)
        cache_commit_hash = vector_store.vector_cache[filename].commit_hash
        assert vector_id in cache_vector_ids
        assert commit_hash == cache_commit_hash
