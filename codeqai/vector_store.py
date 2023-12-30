import inquirer
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores import FAISS
from yaspin import yaspin

from codeqai import utils
from codeqai.cache import VectorCache, get_cache_path, load_vector_cache


class VectorStore:
    def __init__(
        self, name: str, embeddings: Embeddings, documents: list[Document] = []
    ):
        self.name = name
        self.embeddings = embeddings
        self.install_faiss()
        if not documents:
            spinner = yaspin(text="💾 Loading vector store...", color="green")
            spinner.start()
            self.db = FAISS.load_local(
                index_name=self.name,
                folder_path=get_cache_path(),
                embeddings=self.embeddings,
            )
            self.db.delete([self.db.index_to_docstore_id[0]])
            self.db.save_local(index_name=self.name, folder_path=get_cache_path())
            self.vector_cache = load_vector_cache(f"{self.name}.json")
            spinner.stop()
        else:
            self.vector_cache = {}
            spinner = yaspin(text="💾 Indexing vector store...", color="green")
            spinner.start()
            self.db = FAISS.from_documents(documents, embeddings)
            self.db.save_local(index_name=self.name, folder_path=get_cache_path())
            index_to_docstore_id = self.db.index_to_docstore_id
            for i in range(len(documents)):
                document = self.db.docstore.search(index_to_docstore_id[i])
                if document:
                    print(self.vector_cache)
                    if self.vector_cache.get(document.metadata["filename"]):
                        self.vector_cache[
                            document.metadata["filename"]
                        ].vector_ids.append(index_to_docstore_id[i])
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
        for document in documents:
            if self.vector_cache.get(document.metadata["filename"]):
                if (
                    self.vector_cache[document.metadata["filename"]].commit_hash
                    != document.metadata["commit_hash"]
                ):
                    # This will delete all the vectors associated with the document
                    # incluing db.index_to_docstore_id, db.docstore and db.index
                    self.db.delete(
                        self.vector_cache[document.metadata["filename"]].vector_ids
                    )
                    self.db.add_document(document)
                    self.vector_cache[document.metadata["filename"]] = VectorCache(
                        document.metadata["filename"],
                        [self.db.index_to_docstore_id[-1]],
                        document.metadata["commit_hash"],
                    )
            else:
                self.db.add_document(document)
                self.vector_cache[document.metadata["filename"]] = VectorCache(
                    document.metadata["filename"],
                    [self.db.index_to_docstore_id[-1]],
                    document.metadata["commit_hash"],
                )

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
