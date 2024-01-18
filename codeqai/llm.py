import os
import subprocess
import sys

import inquirer
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.llms import LlamaCpp, Ollama

from codeqai import utils
from codeqai.constants import LlmHost


class LLM:
    def __init__(self, llm_host: LlmHost, chat_model: str, deployment=None):
        if llm_host == LlmHost.OPENAI:
            self.chat_model = ChatOpenAI(
                temperature=0.9, max_tokens=2048, model=chat_model
            )
        elif llm_host == LlmHost.AZURE_OPENAI and deployment:
            self.chat_model = AzureChatOpenAI(
                openai_api_base=os.getenv("OPENAI_API_BASE"),
                temperature=0.9,
                max_tokens=2048,
                deployment_name=deployment,
                model=chat_model,
            )
        elif llm_host == LlmHost.LLAMACPP:
            self.install_llama_cpp()
            self.chat_model = LlamaCpp(
                model_path=chat_model,
                temperature=0.9,
                max_tokens=2048,
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
                        env_vars[
                            "CMAKE_ARGS"
                        ] = "-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"

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
