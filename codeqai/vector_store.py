import os

import inquirer
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain_community.vectorstores import FAISS

from codeqai import utils
from codeqai.cache import VectorCache, get_cache_path, load_vector_cache
from codeqai.codeparser import parse_code_files
from codeqai.repo import get_commit_hash


class VectorStore:
    def __init__(self, name: str, embeddings: Embeddings):
        self.name = name
        self.embeddings = embeddings
        self.install_faiss()

    def load_documents(self):
        with open(
            os.path.join(get_cache_path(), f"{self.name}.faiss.bytes"), "rb"
        ) as file:
            index = file.read()

        self.db = FAISS.deserialize_from_bytes(
            embeddings=self.embeddings, serialized=index
        )
        self.vector_cache = load_vector_cache(f"{self.name}.json")
        self.retriever = self.db.as_retriever(search_type="mmr", search_kwargs={"k": 8})

    def index_documents(self, documents: list[Document]):
        self.vector_cache = {}
        self.db = FAISS.from_documents(documents, self.embeddings)
        index = self.db.serialize_to_bytes()
        with open(
            os.path.join(get_cache_path(), f"{self.name}.faiss.bytes"), "wb"
        ) as binary_file:
            binary_file.write(index)
        # Create vector cache
        index_to_docstore_id = self.db.index_to_docstore_id
        for i in range(len(documents)):
            document = self.db.docstore.search(index_to_docstore_id[i])
            if document:
                # Check if the document is already present in the vector cache
                # if yes, then add the vector id to the vector cache entry
                if self.vector_cache.get(document.metadata["filename"]):
                    self.vector_cache[document.metadata["filename"]].vector_ids.append(
                        index_to_docstore_id[i]
                    )
                # if no, then create a new entry in the vector cache
                else:
                    self.vector_cache[document.metadata["filename"]] = VectorCache(
                        document.metadata["filename"],
                        [index_to_docstore_id[i]],
                        document.metadata["commit_hash"],
                    )

        self.retriever = self.db.as_retriever(search_type="mmr", search_kwargs={"k": 8})

    def sync_documents(self, files):
        new_filenames = set()
        for file in files:
            filename = os.path.basename(file)
            new_filenames.add(filename)
            commit_hash = get_commit_hash(file)
            # Check if the document is already present in the vector cache
            # if yes, then check if the document has been modified or not
            if filename in self.vector_cache:
                # Check if the document has been modified, if yes delete all old vectors and add new vector
                if self.vector_cache[filename].commit_hash != commit_hash:
                    # This will delete all the vectors associated with the document
                    # incluing db.index_to_docstore_id, db.docstore and db.index
                    try:
                        self.db.delete(self.vector_cache[filename].vector_ids)
                    except Exception as e:
                        print(f"Error deleting vectors for file {filename}: {e}")

                    # Add the new document to the vector store and recreate the vector cache entry
                    self.vector_cache[filename] = VectorCache(
                        filename,
                        [],
                        commit_hash,
                    )
                    documents = parse_code_files([file])
                    for document in documents:
                        self.db.add_documents([document])
                        self.vector_cache[filename].vector_ids.append(
                            self.db.index_to_docstore_id[
                                len(self.db.index_to_docstore_id) - 1
                            ]
                        )

            # if no, then create a new entry in the vector cache and add the document to the vector store
            else:
                self.vector_cache[filename] = VectorCache(
                    filename,
                    [],
                    commit_hash,
                )
                documents = parse_code_files([file])
                for document in documents:
                    self.db.add_documents([document])
                    self.vector_cache[filename].vector_ids.append(
                        self.db.index_to_docstore_id[
                            len(self.db.index_to_docstore_id) - 1
                        ]
                    )

        # Remove old documents from the vector store
        deleted_files = []
        for cache_item in self.vector_cache.values():
            if cache_item.filename not in new_filenames:
                try:
                    self.db.delete(cache_item.vector_ids)
                except Exception as e:
                    print(f"Error deleting vectors for file {cache_item.filename}: {e}")
                deleted_files.append(cache_item.filename)

        # Remove old filenames from the vector cache
        for deleted_file in deleted_files:
            self.vector_cache.pop(deleted_file)

        index = self.db.serialize_to_bytes()
        with open(
            os.path.join(get_cache_path(), f"{self.name}.faiss.bytes"), "wb"
        ) as binary_file:
            binary_file.write(index)

    def similarity_search(self, query: str):
        return self.db.similarity_search(query, k=4)

    def install_faiss(self):
        try:
            import faiss  # noqa: F401
        except ImportError:
            question = [
                inquirer.Confirm(
                    "confirm",
                    message=f"{utils.get_bold_text('faiss')} package not found in this python environment. Do you want to install it now?",
                    default=True,
                ),
            ]

            answers = inquirer.prompt(question)
            if answers and answers["confirm"]:
                import subprocess
                import sys

                question = [
                    inquirer.List(
                        "faiss-installation",
                        message="Please select the appropriate option to install FAISS. Use gpu if your system supports CUDA",
                        choices=[
                            "faiss-cpu",
                            "faiss-gpu",
                        ],
                        default="faiss-cpu",
                    ),
                ]

                answers = inquirer.prompt(question)
                if answers and answers["faiss-installation"]:
                    try:
                        subprocess.run(
                            [
                                sys.executable,
                                "-m",
                                "pip",
                                "install",
                                answers["faiss-installation"],
                            ],
                            check=True,
                        )
                    except subprocess.CalledProcessError as e:
                        print(f"Error during faiss installation: {e}")
            else:
                exit("faiss package is required for codeqai to work.")
