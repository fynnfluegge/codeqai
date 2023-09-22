import os
import platform
from pathlib import Path

import inquirer
import yaml


def get_cache_path():
    system = platform.system()

    if system == "Linux" or system == "Darwin":
        user_home = os.path.expanduser("~")
        cache_dir = os.path.join(user_home, ".cache", "codeqa")
    elif system == "Windows":
        user_home = os.path.expanduser("~")
        cache_dir = os.path.join(user_home, "AppData", "Local", "codeqa")
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
        config_dir = os.path.join(user_home, ".config", "codeqa")
    elif system == "Windows":
        user_home = os.path.expanduser("~")
        config_dir = os.path.join(user_home, "AppData", "Roaming", "codeqa")
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
        inquirer.List(
            "embeddings",
            message="Which embeddings do you want to use?",
            choices=["USE", "BERT"],
            default="USE",
        ),
        inquirer.List(
            "llm",
            message="Which LLM do you want to use?",
            choices=["GPT-2", "GPT-3"],
            default="GPT-2",
        ),
    ]

    answers = inquirer.prompt(questions)

    if answers:
        config = {
            "local": answers["confirm"],
            "embeddings": answers["embeddings"],
            "llm": answers["llm"],
        }
        save_config(config)

        return config
