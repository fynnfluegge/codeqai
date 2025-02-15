import os
import platform

import inquirer
import yaml

from codeqai.constants import EmbeddingsModel, LlmHost


def get_config_path():
    """
    Returns the configuration file path based on the operating system.

    This function determines the appropriate configuration directory based on the operating system
    and constructs the full path to the configuration file.

    Returns:
        str: The path to the configuration file.

    Raises:
        NotImplementedError: If the operating system is not supported.
    """
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
    """
    Loads the configuration from the configuration file.

    This function reads the configuration file specified by get_config_path() and parses its content
    using the YAML parser.

    Returns:
        dict: The configuration dictionary loaded from the file.
    """
    with open(get_config_path(), "r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    return config


def save_config(config):
    """
    Saves the configuration to the configuration file.

    Args:
        config (dict): The configuration dictionary to be saved.

    This function writes the provided configuration dictionary to the configuration file specified by get_config_path()
    using the YAML format.
    """
    with open(get_config_path(), "w", encoding="utf-8") as config_file:
        yaml.dump(config, config_file, default_flow_style=False)


def create_config():
    """
    Creates a new configuration interactively by prompting the user for input.

    This function prompts the user with a series of questions to configure the embeddings model and LLM host.
    Based on the user's responses, it constructs a configuration dictionary and saves it to the configuration file.

    Returns:
        dict: The configuration dictionary created based on user input.
    """
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
                message="Which remote LLM provider do you want to use?",
                choices=[
                    LlmHost.OPENAI.value,
                    LlmHost.AZURE_OPENAI.value,
                    LlmHost.ANTHROPIC.value,
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
                    message="Please enter the path to the LLM",
                    default="",
                ),
            ]

        elif config["llm-host"] == LlmHost.OLLAMA.value:
            questions = [
                inquirer.List(
                    "chat-model",
                    message="Which model do you want to use with Ollama?",
                    choices=[
                        "llama2:7b",
                        "llama2:13b",
                        "llama3.2:1b",
                        "llama3.2:3b",
                        "llama3.1:8b",
                        "codellama:7b",
                        "codellama:13b",
                        "gemma2:9b",
                        "gemma2:2b",
                        "deepseek-r1:1.5b",
                        "deepseek-r1:7b",
                        "deepseek-r1:8b",
                        "qwen2.5-coder:7b",
                        "qwen2.5-coder:3b",
                    ],
                    default="llama2:13b",
                ),
            ]

        elif config["llm-host"] == LlmHost.OPENAI.value:
            questions = [
                inquirer.List(
                    "chat-model",
                    message="Which OpenAI model do you want to use?",
                    choices=[
                        "gpt-3.5-turbo",
                        "gpt-4",
                        "gpt-4-turbo",
                        "gpt-4o",
                        "gpt-4o-mini",
                        "o1",
                        "o1-mini",
                        "o3-mini",
                    ],
                    default="gpt-3.5-turbo",
                ),
            ]

        elif config["llm-host"] == LlmHost.ANTHROPIC.value:
            questions = [
                inquirer.List(
                    "chat-model",
                    message="Which Anthropic model do you want to use?",
                    choices=[
                        "claude-3-opus-latest",
                        "claude-3-5-sonnet-latest",
                        "claude-3-5-haiku-latest",
                    ],
                    default="claude-3-opus-latest",
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
