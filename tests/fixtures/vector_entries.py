import pytest
from langchain.schema import Document

from codeqai.cache import VectorCache


@pytest.fixture
def vector_entries():
    return [
        Document(
            page_content="This is a test document.",
            metadata={
                "filename": "test.py",
                "commit_hash": "1234567890",
            },
        ),
        Document(
            page_content="Some further text.",
            metadata={
                "filename": "test.py",
                "commit_hash": "1234567890",
            },
        ),
        Document(
            page_content="This is another test document.",
            metadata={
                "filename": "another_test.py",
                "commit_hash": "1234567891",
            },
        ),
        Document(
            page_content="This is another test document.",
            metadata={
                "filename": "fixed_test.py",
                "commit_hash": "1234567891",
            },
        ),
    ]


@pytest.fixture()
def modified_vector_entries():
    return [
        Document(
            page_content="This is another test document.",
            metadata={
                "filename": "fixed_test.py",
                "commit_hash": "1234567891",
            },
        ),
        Document(
            page_content="This is a modified test document.",
            metadata={
                "filename": "test.py",
                "commit_hash": "1234567892",
            },
        ),
        Document(
            page_content="Some further modified text.",
            metadata={
                "filename": "test.py",
                "commit_hash": "1234567892",
            },
        ),
        Document(
            page_content="This is another modified test document.",
            metadata={
                "filename": "modified_test.py",
                "commit_hash": "1234567893",
            },
        ),
        Document(
            page_content="This is a new test document.",
            metadata={
                "filename": "new_test.py",
                "commit_hash": "1234567894",
            },
        ),
    ]


@pytest.fixture()
def vector_cache():
    return {
        "test.py": VectorCache(
            filename="test.py",
            vector_ids=[],
            commit_hash="1234567890",
        ),
        "another_test.py": VectorCache(
            filename="another_test.py",
            vector_ids=[],
            commit_hash="1234567891",
        ),
        "fixed_test.py": VectorCache(
            filename="fixed_test.py",
            vector_ids=[],
            commit_hash="1234567891",
        ),
    }
