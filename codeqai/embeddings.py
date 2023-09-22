from langchain.embeddings.openai import OpenAIEmbeddings


def get_embeddings(code_chunks: list[str]):
    embeddings = OpenAIEmbeddings(client=None, model="text-search-ada-doc-001")
    return embeddings.embed_documents(code_chunks)


def get_query_embedding(query: str):
    embeddings = OpenAIEmbeddings(client=None, model="text-search-ada-doc-001")
    return embeddings.embed_query(query)
