import os
import subprocess
import time

import streamlit as st
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory

from codeqai import codeparser, repo, utils
from codeqai.cache import save_vector_cache
from codeqai.config import load_config
from codeqai.constants import EmbeddingsModel, LlmHost
from codeqai.embeddings import Embeddings
from codeqai.llm import LLM
from codeqai.vector_store import VectorStore


def semantic_search(repo_name: str):
    st.title("CodeQAI")
    st.subheader(f"🔎 Semantic search in {repo_name}")
    input = st.text_input("Enter a search pattern: ")
    if input:
        similarity_result = vector_store.similarity_search(input)
        for doc in similarity_result:
            language = utils.get_programming_language(
                utils.get_file_extension(doc.metadata["filename"])
            )

            start_line, indentation = utils.find_starting_line_and_indent(
                doc.metadata["filename"], doc.page_content
            )

            st.write(doc.metadata["filename"] + " -> " + doc.metadata["method_name"])
            # TODO add start_line to the code, open PR on streamlit
            st.code(
                indentation + doc.page_content,
                language=language.value,
                line_numbers=False,
            )


# TODO use artificial stream until
def stream_response(response: str):
    for word in response.split():
        yield word + " "
        time.sleep(0.01)


def chat(memory: ConversationSummaryMemory, repo_name: str):
    st.title("CodeQAI")
    st.subheader(f"💬 Ask anything about the codebase of {repo_name}")

    if st.button("Clear Chat"):
        st.session_state["chat"] = []
        st.session_state.messages = []
        memory.clear()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if input := st.chat_input("Start chat..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": input})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(input)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            result = qa(input)
            response = st.write_stream(stream_response(result["answer"]))
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})


config = load_config()
repo_name = repo.get_git_root(os.getcwd()).split("/")[-1]

embeddings_model = Embeddings(
    model=EmbeddingsModel[config["embeddings"].upper().replace("-", "_")],
    deployment=(
        config["embeddings-deployment"] if "embeddings-deployment" in config else None
    ),
)

vector_store = VectorStore(repo_name, embeddings=embeddings_model.embeddings)
vector_store.load_documents()

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


selected_chat = st.sidebar.radio("Select Mode", ["Search", "Chat"])
if st.sidebar.button("Sync with current git checkout"):
    files = repo.load_files()
    documents = codeparser.parse_code_files(files)
    vector_store.sync_documents(documents)
    save_vector_cache(vector_store.vector_cache, f"{repo_name}.json")
    st.sidebar.write(
        "✅ Synced with git commit hash\n"
        + subprocess.run(
            ["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE, text=True
        ).stdout.strip()
    )

if selected_chat == "Search":
    semantic_search(repo_name)
else:
    chat(memory, repo_name)
