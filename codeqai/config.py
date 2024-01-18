import json
import os
import platform
from pathlib import Path

import inquirer
import yaml

from codeqai.constants import EmbeddingsModel, LlmHost


def get_config_path():
    system = platform.system()

    if system == "Linux" or system == "Darwin":
        user_home = os.path.expanduser("~")
        config_dir = os.path.join(user_home, ".config", "codeqai")
    elif system == "Windows":
        user_home = os.path.expanduser("~")
        config_dir = os.path.join(user_home, "AppData", "Roaming", "codeqai")
    else:
        raise NotImplementedError(f"Unsupported platform: {system}")

    config_file_path = os.path.join(config_dir, "config.yaml")

    return config_file_path


def load_config():
    with open(get_config_path(), "r") as config_file:
        config = yaml.safe_load(config_file)
    return config


def save_config(config):
    with open(get_config_path(), "w") as config_file:
        yaml.dump(config, config_file, default_flow_style=False)


def create_config():
    os.makedirs(os.path.dirname(get_config_path()), exist_ok=True)

    questions = [
        inquirer.Confirm(
            "confirm",
            message="Do you want to use local embedding models?",
            default=False,
        ),
    ]

    confirm = inquirer.prompt(questions)

    if confirm and confirm["confirm"]:
        questions = [
            inquirer.List(
                "embeddings",
                message="Which local embeddings model do you want to use?",
                choices=[
                    EmbeddingsModel.INSTRUCTOR_LARGE.value,
                    EmbeddingsModel.SENTENCETRANSFORMERS_ALL_MPNET_BASE_V2.value,
                    EmbeddingsModel.SENTENCETRANSFORMERS_ALL_MINILM_L6_V2.value,
                ],
                default=EmbeddingsModel.INSTRUCTOR_LARGE.value,
            ),
        ]
    else:
        questions = [
            inquirer.List(
                "embeddings",
                message="Which remote embeddings do you want to use?",
                choices=[
                    EmbeddingsModel.OPENAI_TEXT_EMBEDDING_ADA_002.value,
                    EmbeddingsModel.AZURE_OPENAI.value,
                ],
                default=EmbeddingsModel.OPENAI_TEXT_EMBEDDING_ADA_002.value,
            ),
        ]

    answersEmbedding = inquirer.prompt(questions)

    questions = [
        inquirer.Confirm(
            "confirm", message="Do you want to use local chat models?", default=False
        ),
    ]

    confirm = inquirer.prompt(questions)

    if confirm and confirm["confirm"]:
        questions = [
            inquirer.List(
                "llm-host",
                message="Which local LLM host do you want to use?",
                choices=[
                    LlmHost.LLAMACPP.value,
                    LlmHost.OLLAMA.value,
                ],
                default=LlmHost.LLAMACPP.value,
            ),
        ]
    else:
        questions = [
            inquirer.List(
                "llm-host",
                message="Which remote LLM do you want to use?",
                choices=[
                    LlmHost.OPENAI.value,
                    LlmHost.AZURE_OPENAI.value,
                ],
                default=LlmHost.OPENAI.value,
            ),
        ]

    answersLlm = inquirer.prompt(questions)

    if confirm and answersEmbedding and answersLlm:
        config = {
            "embeddings": answersEmbedding["embeddings"],
            "llm-host": answersLlm["llm-host"],
        }

        if config["embeddings"] == EmbeddingsModel.AZURE_OPENAI.value:
            questions = [
                inquirer.Text(
                    "deployment",
                    message="Please enter the Azure OpenAI embeddings deployment name.",
                    default="",
                ),
            ]
            deployment_answer = inquirer.prompt(questions)
            if deployment_answer and deployment_answer["deployment"]:
                config["embeddings-deployment"] = deployment_answer["deployment"]

        if config["llm-host"] == LlmHost.AZURE_OPENAI.value:
            questions = [
                inquirer.Text(
                    "deployment",
                    message="Please enter the Azure OpenAI model deployment name",
                    default="",
                ),
            ]
            deployment_answer = inquirer.prompt(questions)
            if deployment_answer and deployment_answer["deployment"]:
                config["model-deployment"] = deployment_answer["deployment"]
                config["chat-model"] = deployment_answer["deployment"]

        elif config["llm-host"] == LlmHost.LLAMACPP.value:
            questions = [
                inquirer.Text(
                    "chat-model",
                    message="Please enter the path to the LLM model",
                    default="",
                ),
            ]

        elif config["llm-host"] == LlmHost.OLLAMA.value:
            questions = [
                inquirer.List(
                    "chat-model",
                    message="Which Ollama chat model do you want to use?",
                    choices=[
                        "llama2",
                        "llama2:13b",
                        "llama2:70b",
                        "codellama",
                    ],
                    default="llama2:13b",
                ),
            ]

        elif config["llm-host"] == "OpenAI":
            questions = [
                inquirer.List(
                    "chat-model",
                    message="Which OpenAI chat model do you want to use?",
                    choices=[
                        "gpt-3.5-turbo",
                        "gpt-3.5-turbo-16k",
                        "gpt-4",
                    ],
                    default="gpt-3.5-turbo",
                ),
            ]

        # Check if "chat-model" is already present in the case of Azure_OpenAI
        if "chat-model" not in config:
            answersChatmodel = inquirer.prompt(questions)
            if answersChatmodel and answersChatmodel["chat-model"]:
                config["chat-model"] = answersChatmodel["chat-model"]

        save_config(config)

        return config

    return {}
