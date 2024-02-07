import argparse
import os
import subprocess
import warnings

from dotenv import dotenv_values, load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from yaspin import yaspin

from codeqai import codeparser, repo, utils
from codeqai.bootstrap import bootstrap
from codeqai.cache import create_cache_dir, get_cache_path, save_vector_cache
from codeqai.config import create_config, get_config_path, load_config
from codeqai.constants import EmbeddingsModel, LlmHost
from codeqai.embeddings import Embeddings
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
    if not subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"], capture_output=True
    ).stdout:
        print("Not a git repository. Exiting.")
        exit()
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=["app", "search", "chat", "configure", "sync"],
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
                "OPENAI_API_BASE",
                "OPENAI_API_KEY",
                "OPENAI_API_VERSION",
            ]
        )
    env_path = get_config_path().replace("config.yaml", ".env")
    env_loader(env_path, required_keys)

    repo_name = repo.repo_name()

    # init cache
    create_cache_dir()

    embeddings_model = Embeddings(
        model=EmbeddingsModel[config["embeddings"].upper().replace("-", "_")],
        deployment=(
            config["embeddings-deployment"]
            if "embeddings-deployment" in config
            else None
        ),
    )

    # check if faiss.index exists
    if not os.path.exists(os.path.join(get_cache_path(), f"{repo_name}.faiss.bytes")):
        print(
            f"No vector store found for {utils.get_bold_text(repo_name)}. Initial indexing may take a few minutes."
        )
        spinner = yaspin(text="🔧 Parsing codebase...", color="green")
        spinner.start()
        files = repo.load_files()
        documents = codeparser.parse_code_files(files)
        spinner.stop()
        spinner = yaspin(text="💾 Indexing vector store...", color="green")
        vector_store = VectorStore(
            repo_name,
            embeddings=embeddings_model.embeddings,
        )
        spinner.start()
        vector_store.index_documents(documents)
        save_vector_cache(vector_store.vector_cache, f"{repo_name}.json")
        spinner.stop()

    if args.action == "app":
        subprocess.run(["streamlit", "run", "codeqai/streamlit.py"])
    else:
        spinner = yaspin(text="💾 Loading vector store...", color="green")
        spinner.start()
        vector_store, memory, qa = bootstrap(config, repo_name, embeddings_model)
        spinner.stop()

        if args.action == "sync":
            spinner = yaspin(text="💾 Syncing vector store...", color="green")
            spinner.start()
            files = repo.load_files()
            vector_store.sync_documents(files)
            save_vector_cache(vector_store.vector_cache, f"{repo_name}.json")
            spinner.stop()
            print("✅ Vector store synced with current git checkout.")

        console = Console()
        while True:
            choice = None
            if args.action == "sync":
                break
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

                    start_line, indentation = utils.find_starting_line_and_indent(
                        doc.metadata["filename"], doc.page_content
                    )

                    syntax = Syntax(
                        indentation + doc.page_content,
                        language.value,
                        theme="monokai",
                        line_numbers=True,
                        start_line=start_line,
                        indent_guides=True,
                    )
                    print(
                        doc.metadata["filename"] + " -> " + doc.metadata["method_name"]
                    )
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
            else:
                print("Invalid action.")
                exit()

            if choice == "" or choice == "c":
                continue
            elif choice == "e":
                break
            else:
                print("Invalid choice. Please enter 'C', 'E', or 'R'.")
