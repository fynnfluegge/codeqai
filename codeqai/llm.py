import os
import subprocess
import sys

import inquirer
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import LlamaCpp, Ollama
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from codeqai import utils
from codeqai.constants import LlmHost


class LLM:
    def __init__(
        self, llm_host: LlmHost, chat_model: str, max_tokens=2048, deployment=None
    ):
        """
        Initializes the LLM class with the specified parameters.

        Args:
            llm_host (LlmHost): The host for the language model (e.g., OPENAI, AZURE_OPENAI, ANTHROPIC, LLAMACPP, OLLAMA).
            chat_model (str): The chat model to use.
            max_tokens (int, optional): The maximum number of tokens for the model. Defaults to 2048.
            deployment (str, optional): The deployment name for Azure OpenAI. Defaults to None.

        Raises:
            ValueError: If the required environment variable for Azure OpenAI is not set.
        """
        if llm_host == LlmHost.OPENAI:
            self.chat_model = ChatOpenAI(
                temperature=0.9, max_tokens=max_tokens, model=chat_model
            )
        elif llm_host == LlmHost.AZURE_OPENAI and deployment:
            azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            if azure_openai_endpoint:
                self.chat_model = AzureChatOpenAI(
                    azure_endpoint=azure_openai_endpoint,
                    temperature=0.9,
                    max_tokens=max_tokens,
                    model=chat_model,
                )
            else:
                raise ValueError(
                    "Azure OpenAI requires environment variable AZURE_OPENAI_ENDPOINT to be set."
                )
        elif llm_host == LlmHost.ANTHROPIC:
            self.chat_model = ChatAnthropic(
                temperature=0.9,
                max_tokens_to_sample=max_tokens,
                model_name=chat_model,
                timeout=30,
                api_key=None,  # API key is set to environment variable ANTHROPIC_API_KEY
            )
        elif llm_host == LlmHost.LLAMACPP:
            self.install_llama_cpp()
            self.chat_model = LlamaCpp(
                model_path=chat_model,
                temperature=0.9,
                max_tokens=max_tokens,
                verbose=False,
            )
        elif llm_host == LlmHost.OLLAMA:
            self.chat_model = Ollama(
                base_url="http://localhost:11434",
                model=chat_model,
                callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            )

    def install_llama_cpp(self):
        try:
            from llama_cpp import Llama  # noqa: F401
        except ImportError:
            question = [
                inquirer.Confirm(
                    "confirm",
                    message=f"Local LLM interface package not found. Install {utils.get_bold_text('llama-cpp-python')}?",
                    default=True,
                ),
            ]

            answers = inquirer.prompt(question)
            if answers and answers["confirm"]:
                import platform

                def check_command(command):
                    try:
                        subprocess.run(
                            command,
                            check=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        )
                        return True
                    except subprocess.CalledProcessError:
                        return False
                    except FileNotFoundError:
                        return False

                def install_llama(backend):
                    env_vars = {"FORCE_CMAKE": "1"}

                    if backend == "cuBLAS":
                        env_vars["CMAKE_ARGS"] = "-DLLAMA_CUBLAS=on"
                    elif backend == "hipBLAS":
                        env_vars["CMAKE_ARGS"] = "-DLLAMA_HIPBLAS=on"
                    elif backend == "Metal":
                        env_vars["CMAKE_ARGS"] = "-DLLAMA_METAL=on"
                    else:  # Default to OpenBLAS
                        env_vars["CMAKE_ARGS"] = (
                            "-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"
                        )

                    try:
                        subprocess.run(
                            [
                                sys.executable,
                                "-m",
                                "pip",
                                "install",
                                "llama-cpp-python",
                            ],
                            env={**os.environ, **env_vars},
                            check=True,
                        )
                    except subprocess.CalledProcessError as e:
                        print(f"Error during installation with {backend}: {e}")

                def supports_metal():
                    # Check for macOS version
                    if platform.system() == "Darwin":
                        mac_version = tuple(map(int, platform.mac_ver()[0].split(".")))
                        # Metal requires macOS 10.11 or later
                        if mac_version >= (10, 11):
                            return True
                    return False

                # Check system capabilities
                if check_command(["nvidia-smi"]):
                    install_llama("cuBLAS")
                elif check_command(["rocminfo"]):
                    install_llama("hipBLAS")
                elif supports_metal():
                    install_llama("Metal")
                else:
                    install_llama("OpenBLAS")

                print("Finished downloading `Code-Llama` interface.")

                # Check if on macOS
                if platform.system() == "Darwin":
                    # Check if it's Apple Silicon
                    if platform.machine() != "arm64":
                        print(
                            "Warning: You are using Apple Silicon (M1/M2) Mac but your Python is not of 'arm64' architecture."
                        )
                        print(
                            "The llama.ccp x86 version will be 10x slower on Apple Silicon (M1/M2) Mac."
                        )
                        print(
                            "\nTo install the correct version of Python that supports 'arm64' architecture visit:"
                            "https://github.com/conda-forge/miniforge"
                        )

            else:
                exit("llama-cpp-python is required for local LLM.")
