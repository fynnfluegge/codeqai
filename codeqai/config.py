import os
import platform
from pathlib import Path

import inquirer
import yaml


def get_cache_path():
    system = platform.system()

    if system == "Linux" or system == "Darwin":
        user_home = os.path.expanduser("~")
        cache_dir = os.path.join(user_home, ".cache", "codeqai")
    elif system == "Windows":
        user_home = os.path.expanduser("~")
        cache_dir = os.path.join(user_home, "AppData", "Local", "codeqai")
    else:
        raise NotImplementedError(f"Unsupported platform: {system}")

    return cache_dir


def create_cache_dir():
    if not os.path.exists(get_cache_path()):
        path = Path(get_cache_path())
        path.mkdir(parents=True, exist_ok=True)


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
            "confirm", message="Do you want to use local models?", default=False
        ),
    ]

    confirm = inquirer.prompt(questions)

    if confirm and confirm["confirm"]:
        questions = [
            inquirer.List(
                "embeddings",
                message="Which local embeddings model do you want to use?",
                choices=[
                    "Instructor-Large",
                    "SentenceTransformers-all-mpnet-base-v2",
                    "SentenceTransformers-all-MiniLM-L6-v2",
                ],
                default="Instructor-Large",
            ),
            inquirer.List(
                "llm-host",
                message="Which local LLM host do you want to use?",
                choices=[
                    "Llamacpp",
                    "Ollama",
                ],
                default="Llamacpp",
            ),
        ]
    else:
        questions = [
            inquirer.List(
                "embeddings",
                message="Which remote embeddings do you want to use?",
                choices=["OpenAI-text-embedding-ada-002", "Azure-OpenAI"],
                default="OpenAI-text-embedding-ada-002",
            ),
            inquirer.List(
                "llm-host",
                message="Which remote LLM do you want to use?",
                choices=[
                    "OpenAI",
                    "Azure-OpenAI",
                ],
                default="OpenAI",
            ),
        ]

    answers = inquirer.prompt(questions)

    if confirm and answers:
        config = {
            "local": confirm["confirm"],
            "embeddings": answers["embeddings"],
            "llm-host": answers["llm-host"],
        }

        if answers["embeddings"] == "Azure-OpenAI":
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

        if answers["llm-host"] == "Azure-OpenAI":
            questions = [
                inquirer.Text(
                    "deployment",
                    message="Please enter the Azure OpenAI model deployment name.",
                    default="",
                ),
            ]
            deployment_answer = inquirer.prompt(questions)
            if deployment_answer and deployment_answer["deployment"]:
                config["model-deployment"] = deployment_answer["deployment"]

        if answers["llm-host"] == "Llamacpp":
            questions = [
                inquirer.Text(
                    "chat-model",
                    message="Please enter the path to the LLM model.",
                    default="",
                ),
            ]
        elif answers["llm-host"] == "Ollama":
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
                    default="gpt-3.5-turbo",
                ),
            ]
        elif answers["llm-host"] == "OpenAI":
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

        answers = inquirer.prompt(questions)
        if answers and answers["chat-model"]:
            config["chat-model"] = answers["chat-model"]

        save_config(config)

        return config

    return {}
