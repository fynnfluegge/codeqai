import inquirer
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores import FAISS
from yaspin import yaspin

from codeqai import utils
from codeqai.cache import VectorCache, get_cache_path, load_vector_cache


class VectorStore:
    def __init__(self, name: str, embeddings: Embeddings):
        self.name = name
        self.embeddings = embeddings
        self.install_faiss()

    def load_documents(self):
        spinner = yaspin(text="💾 Loading vector store...", color="green")
        spinner.start()
        self.db = FAISS.load_local(
            index_name=self.name,
            folder_path=get_cache_path(),
            embeddings=self.embeddings,
        )
        self.vector_cache = load_vector_cache(f"{self.name}.json")
        spinner.stop()
        self.retriever = self.db.as_retriever(search_type="mmr", search_kwargs={"k": 8})

    def index_documents(self, documents: list[Document]):
        self.vector_cache = {}
        spinner = yaspin(text="💾 Indexing vector store...", color="green")
        spinner.start()
        self.db = FAISS.from_documents(documents, self.embeddings)
        self.db.save_local(index_name=self.name, folder_path=get_cache_path())

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

        spinner.stop()
        self.retriever = self.db.as_retriever(search_type="mmr", search_kwargs={"k": 8})

    def sync_documents(self, documents: list[Document]):
        spinner = yaspin(text="💾 Syncing vector store...", color="green")
        spinner.start()

        new_filenames = set()
        modified_filenames = set()

        for document in documents:
            new_filenames.add(document.metadata["filename"])
            # Check if the document is already present in the vector cache
            # if yes, then check if the document has been modified or not
            if document.metadata["filename"] in self.vector_cache:
                # Check if the document has been modified, if yes delete all old vectors and add new vector
                if (
                    self.vector_cache[document.metadata["filename"]].commit_hash
                    != document.metadata["commit_hash"]
                ):
                    modified_filenames.add(document.metadata["filename"])
                    # This will delete all the vectors associated with the document
                    # incluing db.index_to_docstore_id, db.docstore and db.index
                    self.db.delete(
                        self.vector_cache[document.metadata["filename"]].vector_ids
                    )
                    # Add the new document to the vector store and recreate the vector cache entry
                    self.db.add_documents([document])
                    self.vector_cache[document.metadata["filename"]] = VectorCache(
                        document.metadata["filename"],
                        [
                            self.db.index_to_docstore_id[
                                len(self.db.index_to_docstore_id) - 1
                            ]
                        ],
                        document.metadata["commit_hash"],
                    )
                # In this case the document was already present.
                # Now it needs to be further checkd if the document has been modified or not
                # since the commit hash might has been replaced already in the first if condition
                else:
                    if document.metadata["filename"] in modified_filenames:
                        self.db.add_documents([document])
                        self.vector_cache[
                            document.metadata["filename"]
                        ].vector_ids.append(
                            self.db.index_to_docstore_id[
                                len(self.db.index_to_docstore_id) - 1
                            ]
                        )

            # if no, then create a new entry in the vector cache and add the document to the vector store
            else:
                self.db.add_documents([document])
                self.vector_cache[document.metadata["filename"]] = VectorCache(
                    document.metadata["filename"],
                    [
                        self.db.index_to_docstore_id[
                            len(self.db.index_to_docstore_id) - 1
                        ]
                    ],
                    document.metadata["commit_hash"],
                )

        # Remove old documents from the vector store
        old_filenames = []
        for cache_item in self.vector_cache.values():
            if cache_item.filename not in new_filenames:
                self.db.delete(cache_item.vector_ids)
                old_filenames.append(cache_item.filename)

        # Remove old filenames from the vector cache
        for old_filename in old_filenames:
            self.vector_cache.pop(old_filename)

        self.db.save_local(index_name=self.name, folder_path=get_cache_path())
        spinner.stop()

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
                        message="Please select the appropriate option to install FAISS.",
                        choices=[
                            "faiss-cpu",
                            "faiss-gpu (Only if your system supports CUDA))",
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
