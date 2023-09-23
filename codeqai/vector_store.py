import inquirer
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.vectorstores import FAISS

from codeqai import utils
from codeqai.config import get_cache_path


class VectorStore:
    def __init__(
        self, name: str, embeddings: Embeddings, documents: list[Document] = []
    ):
        self.name = name
        self.embeddings = embeddings
        self.install_faiss()
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

    def similarity_search(self, query: str):
        return self.db.similarity_search(query, k=4)

    def install_faiss(self):
        try:
            import faiss
        except ImportError:
            question = [
                inquirer.Confirm(
                    "confirm",
                    message=f"{utils.get_bold_text('FAISS')} not found in this python environment. Do you want to install it now?",
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
                        message=f"Please select the appropriate option to install FAISS.",
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
