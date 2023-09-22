import os

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationSummaryMemory
from yaspin import yaspin

from codeqai import codeparser, repo
from codeqai.config import (create_cache_dir, create_config, get_cache_path,
                            load_config)
from codeqai.vector_store import VectorStore


def run():
    # load config
    config = None
    try:
        config = load_config()
    except FileNotFoundError:
        config = create_config()

    repo_name = repo.get_git_root(os.getcwd()).split("/")[-1]

    # init cache
    create_cache_dir()

    # check if faiss.index exists
    if not os.path.exists(os.path.join(get_cache_path(), f"{repo_name}.index")):
        # sync repo
        files = repo.load_files()
        documents = codeparser.parse_code_files(files)
        vector_store = VectorStore(
            repo_name,
            OpenAIEmbeddings(client=None, model="text-search-ada-doc-001"),
            documents=documents,
        )
    else:
        vector_store = VectorStore(
            repo_name, OpenAIEmbeddings(client=None, model="text-search-ada-doc-001")
        )

    llm = ChatOpenAI(temperature=0.9, max_tokens=2048, model="gpt-3.5-turbo")
    memory = ConversationSummaryMemory(
        llm=llm, memory_key="chat_history", return_messages=True
    )
    qa = ConversationalRetrievalChain.from_llm(
        llm, retriever=vector_store.retriever, memory=memory
    )
    while True:
        question = input("🤖 Ask me anything about the codebase: ")

        spinner = yaspin(text=f"🤖 Processing question...")
        spinner.start()

        result = qa(question)

        spinner.stop()
        print(result["answer"])

        choice = (
            input("Do you want to (C)ontinue chat, (R)eset chat or (E)xit [C]?")
            .strip()
            .lower()
        )

        if choice == "" or choice == "c":
            continue
        elif choice == "e":
            break
        elif choice == "r":
            print("Resetting chat...")
            memory.clear()
        else:
            print("Invalid choice. Please enter 'C', 'E', or 'R'.")
