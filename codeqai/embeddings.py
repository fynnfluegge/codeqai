import inquirer
from langchain.embeddings import (HuggingFaceEmbeddings,
                                  HuggingFaceInstructEmbeddings)
from langchain.embeddings.openai import OpenAIEmbeddings

from codeqai import utils
from codeqai.constants import EmbeddingsModel


class Embeddings:
    def __init__(
        self, local=False, model=EmbeddingsModel.OPENAI_TEXT_EMBEDDING_ADA_002
    ):
        self.model = model

        if not local:
            if model == EmbeddingsModel.OPENAI_TEXT_EMBEDDING_ADA_002:
                self.embeddings = OpenAIEmbeddings(
                    client=None, model="text_embedding_ada_002"
                )
        else:
            if model == EmbeddingsModel.OLLAMA:
                pass
            else:
                try:
                    import sentence_transformers  # noqa: F401
                except ImportError:
                    self._install_sentence_transformers()

                if model == EmbeddingsModel.SENTENCETRANSFORMERS_ALL_MPNET_BASE_V2:
                    self.embeddings = HuggingFaceEmbeddings()
                elif model == EmbeddingsModel.INSTRUCTOR_LARGE:
                    try:
                        from InstructorEmbedding import \
                            INSTRUCTOR  # noqa: F401
                    except ImportError:
                        self._install_instructor_embedding()
                        self.embeddings = HuggingFaceInstructEmbeddings()

    def _install_sentence_transformers(self):
        question = [
            inquirer.Confirm(
                "confirm",
                message=f"{utils.get_bold_text('SentenceTransformers')} not found in this python environment. Do you want to install it now?",
                default=True,
            ),
        ]

        answers = inquirer.prompt(question)
        if answers and answers["confirm"]:
            import subprocess
            import sys

            try:
                subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "sentence_transformers",
                    ],
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"Error during sentence_transformers installation: {e}")

    def _install_instructor_embedding(self):
        question = [
            inquirer.Confirm(
                "confirm",
                message=f"{utils.get_bold_text('InstructorEmbedding')} not found in this python environment. Do you want to install it now?",
                default=True,
            ),
        ]

        answers = inquirer.prompt(question)
        if answers and answers["confirm"]:
            import subprocess
            import sys

            try:
                subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "InstructorEmbedding",
                    ],
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"Error during sentence_transformers installation: {e}")
