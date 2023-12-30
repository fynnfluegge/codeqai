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
        index_to_docstore_id = self.db.index_to_docstore_id
        for i in range(len(documents)):
            document = self.db.docstore.search(index_to_docstore_id[i])
            if document:
                if self.vector_cache.get(document.metadata["filename"]):
                    self.vector_cache[document.metadata["filename"]].vector_ids.append(
                        index_to_docstore_id[i]
                    )
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
        for document in documents:
            print(document.metadata["filename"])
            new_filenames.add(document.metadata["filename"])
            if document.metadata["filename"] in self.vector_cache:
                # check if the file has been modified
                if (
                    self.vector_cache[document.metadata["filename"]].commit_hash
                    != document.metadata["commit_hash"]
                ):
                    # This will delete all the vectors associated with the document
                    # incluing db.index_to_docstore_id, db.docstore and db.index
                    self.db.delete(
                        self.vector_cache[document.metadata["filename"]].vector_ids
                    )
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
            else:
                # add new file to vector store
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

        # remove old files from cache and vector store
        old_filenames = []
        for cache_item in self.vector_cache.values():
            if cache_item.filename not in new_filenames:
                self.db.delete(cache_item.vector_ids)
                old_filenames.append(cache_item.filename)

        for old_filename in old_filenames:
            self.vector_cache.pop(old_filename)

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
