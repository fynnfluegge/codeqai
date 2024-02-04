import inquirer
from langchain_community.embeddings import (HuggingFaceEmbeddings,
                                            HuggingFaceInstructEmbeddings)
from langchain_openai import OpenAIEmbeddings

from codeqai import utils
from codeqai.constants import EmbeddingsModel


class Embeddings:
    def __init__(
        self,
        model=EmbeddingsModel.OPENAI_TEXT_EMBEDDING_ADA_002,
        deployment=None,
    ):
        if model == EmbeddingsModel.OPENAI_TEXT_EMBEDDING_ADA_002:
            self.embeddings = OpenAIEmbeddings(
                client=None, model="text-embedding-ada-002"
            )
        elif model == EmbeddingsModel.AZURE_OPENAI and deployment:
            self.embeddings = OpenAIEmbeddings(client=None, deployment=deployment)
        else:
            try:
                import sentence_transformers  # noqa: F401
            except ImportError:
                self._install_sentence_transformers()

            if model == EmbeddingsModel.SENTENCETRANSFORMERS_ALL_MPNET_BASE_V2:
                self.embeddings = HuggingFaceEmbeddings()
            elif model == EmbeddingsModel.SENTENCETRANSFORMERS_ALL_MINILM_L6_V2:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=EmbeddingsModel.SENTENCETRANSFORMERS_ALL_MINILM_L6_V2.value.replace(
                        "SentenceTransformers-", ""
                    )
                )
            elif model == EmbeddingsModel.INSTRUCTOR_LARGE:
                try:
                    from InstructorEmbedding import INSTRUCTOR  # noqa: F401
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
        else:
            exit("sentence_transformers is required for local embeddings.")

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
        else:
            exit("InstructorEmbedding is required for local embeddings.")
