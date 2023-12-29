import argparse
import os
import subprocess

from dotenv import dotenv_values, load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from yaspin import yaspin

from codeqai import codeparser, repo, utils
from codeqai.config import (create_cache_dir, create_config, get_cache_path,
                            get_config_path, load_config)
from codeqai.constants import EmbeddingsModel, LlmHost
from codeqai.embeddings import Embeddings
from codeqai.llm import LLM
from codeqai.vector_store import VectorStore


def env_loader(env_path, required_keys=None):
    """
    Args :
    env_path = source path of .env file.
    required_keys = ["OPENAI_KEY"] #change this according to need

    #running/calling the function.
    configs = env_loader('.env', required_keys)
    """

    # create env file if does not exists
    # parse required keys in the file if it's not None
    if not os.path.exists(env_path) or os.path.getsize(env_path) == 0:
        with open(env_path, "w") as env_f:
            if required_keys:
                for key in required_keys:
                    env_f.write(f'{key}=""\n')
            else:
                pass

    configs = dotenv_values(env_path)
    changed = False
    for key, value in configs.items():
        env_key = os.getenv(key)
        if not value and not env_key:
            value = input(
                f"[+] Key {utils.get_bold_text(key)} is required. Please enter it's value: "
            )
            configs[key] = value
            changed = True
        elif not value and env_key:
            value = env_key
            configs[key] = value
            changed = True

    # update the .env file if config is changed/taken from user
    if changed:
        with open(env_path, "w") as env_f:
            for key, value in configs.items():
                env_f.write(f'{key}="{value}"\n')

    load_dotenv(env_path, override=True)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=["search", "chat", "configure", "sync"],
        help="Action to perform. 'search' will semantically search the codebase. 'chat' will chat with the codebase.",
    )
    args = parser.parse_args()

    if args.action == "configure":
        create_config()
        exit()

    # load config
    config = {}
    try:
        config = load_config()
    except FileNotFoundError:
        config = create_config()

    # lookup env variables
    required_keys = []
    if (
        config["llm-host"] == LlmHost.OPENAI.value
        or config["embeddings"] == EmbeddingsModel.OPENAI_TEXT_EMBEDDING_ADA_002.value
    ):
        required_keys.append("OPENAI_API_KEY")

    if (
        config["llm-host"] == LlmHost.AZURE_OPENAI.value
        or config["embeddings"] == EmbeddingsModel.AZURE_OPENAI.value
    ):
        required_keys.extend(
            [
                "OPENAI_API_TYPE",
                "OPENAI_API_BASE_URL",
                "OPENAI_API_KEY",
                "OPENAI_API_VERSION",
            ]
        )
    env_path = get_config_path().replace("config.yaml", ".env")
    env_loader(env_path, required_keys)

    repo_name = repo.get_git_root(os.getcwd()).split("/")[-1]

    # init cache
    create_cache_dir()

    embeddings_model = Embeddings(
        model=EmbeddingsModel[config["embeddings"].upper().replace("-", "_")],
        deployment=config["embeddings-deployment"]
        if "embeddings-deployment" in config
        else None,
    )

    # check if faiss.index exists
    if not os.path.exists(os.path.join(get_cache_path(), f"{repo_name}.faiss")):
        # sync repo
        spinner = yaspin(text="🔧 Parsing codebase...", color="green")
        files = repo.load_files()
        documents = codeparser.parse_code_files(files)
        spinner.stop()
        vector_store = VectorStore(
            repo_name,
            embeddings=embeddings_model.embeddings,
            documents=documents,
        )
        config[f"{repo_name}-commit"] = current_repo.head.commit.hexsha
        save_config(config)
        spinner.stop()
    else:
        vector_store = VectorStore(repo_name, embeddings=embeddings_model.embeddings)

    if args.action == "sync":
        git_command = [
            "git",
            "diff",
            "--name-only",
            config[f"{repo_name}-commit"],
            current_repo.head.commit.hexsha,
        ]
        result = subprocess.run(
            git_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode == 0:
            changed_files = result.stdout.splitlines()
            # TODO update files

    llm = LLM(
        llm_host=LlmHost[config["llm-host"].upper().replace("-", "_")],
        chat_model=config["chat-model"],
        deployment=config["model-deployment"] if "model-deployment" in config else None,
    )
    memory = ConversationSummaryMemory(
        llm=llm.chat_model, memory_key="chat_history", return_messages=True
    )
    qa = ConversationalRetrievalChain.from_llm(
        llm.chat_model, retriever=vector_store.retriever, memory=memory
    )

    console = Console()
    while True:
        choice = None
        if args.action == "search":
            search_pattern = input("🔎 Enter a search pattern: ")
            spinner = yaspin(text="🤖 Processing...", color="green")
            spinner.start()
            similarity_result = vector_store.similarity_search(search_pattern)
            spinner.stop()
            for doc in similarity_result:
                language = utils.get_programming_language(
                    utils.get_file_extension(doc.metadata["filename"])
                )

                syntax = Syntax(
                    doc.page_content,
                    language.value,
                    theme="monokai",
                    line_numbers=True,
                )
                print(doc.metadata["filename"] + " -> " + doc.metadata["method_name"])
                console.print(syntax)
                print()

            choice = input("[?] (C)ontinue search or (E)xit [C]:").strip().lower()

        elif args.action == "chat":
            question = input("💬 Ask anything about the codebase: ")
            spinner = yaspin(text="🤖 Processing...", color="green")
            spinner.start()
            result = qa(question)
            spinner.stop()
            markdown = Markdown(result["answer"])
            console.print(markdown)

            choice = (
                input("[?] (C)ontinue chat, (R)eset chat or (E)xit [C]:")
                .strip()
                .lower()
            )

            if choice == "r":
                memory.clear()
                print("Chat history cleared.")

        if choice == "" or choice == "c":
            continue
        elif choice == "e":
            break
        else:
            print("Invalid choice. Please enter 'C', 'E', or 'R'.")
