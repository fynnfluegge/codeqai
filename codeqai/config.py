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
                    "SentenceTransformers-all-mpnet-base-v2",
                    "Instructor-Large",
                    "Ollama",
                ],
                default="SentenceTransformers-all-mpnet-base-v2",
            ),
            inquirer.List(
                "llm",
                message="Which local LLM do you want to use?",
                choices=["Llamacpp", "Ollama", "Huggingface"],
                default="Llamacpp",
            ),
        ]
    else:
        questions = [
            inquirer.List(
                "embeddings",
                message="Which embeddings do you want to use?",
                choices=["OpenAI-text-embedding-ada-002", "Azure-OpenAI"],
                default="OpenAI-text-embedding-ada-002",
            ),
            inquirer.List(
                "llm",
                message="Which LLM do you want to use?",
                choices=["GPT-3.5-Turbo", "GPT-4"],
                default="GPT-3.5-Turbo",
            ),
        ]

    answers = inquirer.prompt(questions)

    if confirm and answers:
        config = {
            "local": confirm["confirm"],
            "embeddings": answers["embeddings"],
            "llm": answers["llm"],
        }
        save_config(config)

        return config

    return {}
