from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory

from codeqai.constants import EmbeddingsModel, LlmHost
from codeqai.embeddings import Embeddings
from codeqai.llm import LLM
from codeqai.vector_store import VectorStore


def bootstrap(config, repo_name, embeddings_model=None):
    if embeddings_model is None:
        embeddings_model = Embeddings(
            model=EmbeddingsModel[config["embeddings"].upper().replace("-", "_")],
            deployment=(
                config["embeddings-deployment"]
                if "embeddings-deployment" in config
                else None
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

    return vector_store, memory, qa
