import argparse
import os
import subprocess

from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory
from rich.console import Console
from rich.syntax import Syntax
from yaspin import yaspin

from codeqai import codeparser, repo, utils
from codeqai.config import (create_cache_dir, create_config, get_cache_path,
                            load_config, save_config)
from codeqai.constants import EmbeddingsModel, LllmHost
from codeqai.embeddings import Embeddings
from codeqai.llm import LLM
from codeqai.vector_store import VectorStore


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

    current_repo = repo.get_git_root(os.getcwd())
    repo_name = current_repo.split("/")[-1]

    # init cache
    create_cache_dir()

    embeddings_model = Embeddings(
        local=True,
        model=EmbeddingsModel[config["embeddings"].upper().replace("-", "_")],
    )

    # check if faiss.index exists
    if not os.path.exists(os.path.join(get_cache_path(), f"{repo_name}.faiss")):
        # sync repo
        spinner = yaspin(text="🔧 Parsing codebase...", color="green")
        files = repo.load_files()
        documents = codeparser.parse_code_files(files)
        spinner.stop()
        spinner = yaspin(text="💾 Indexing vector store...", color="green")
        spinner.start()
        vector_store = VectorStore(
            repo_name,
            embeddings=embeddings_model.embeddings,
            documents=documents,
        )
        config[f"{repo_name}-commit"] = current_repo.head.commit.hexsha
        save_config(config)
        spinner.stop()
    else:
        spinner = yaspin(text="💾 Loading vector store...", color="green")
        spinner.start()
        vector_store = VectorStore(repo_name, embeddings=embeddings_model.embeddings)
        spinner.stop()

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
        llm_host=LllmHost[config["llm-host"].upper().replace("-", "_")],
        chat_model=config["chat-model"],
    )
    memory = ConversationSummaryMemory(
        llm=llm.chat_model, memory_key="chat_history", return_messages=True
    )
    qa = ConversationalRetrievalChain.from_llm(
        llm.chat_model, retriever=vector_store.retriever, memory=memory
    )

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
                    doc.page_content, language.value, theme="monokai", line_numbers=True
                )
                console = Console()
                console.print(syntax)

            choice = input("[?] (C)ontinue search or (E)xit [C]:").strip().lower()

        elif args.action == "chat":
            question = input("💬 Ask anything about the codebase: ")
            spinner = yaspin(text="🤖 Processing...", color="green")
            spinner.start()
            result = qa(question)
            spinner.stop()
            print(result["answer"])

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
