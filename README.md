<div align="center">

# codeqai

[![Build](https://github.com/fynnfluegge/codeqai/actions/workflows/build.yaml/badge.svg)](https://github.com/fynnfluegge/codeqai/actions/workflows/build.yaml)
[![Publish](https://github.com/fynnfluegge/codeqai/actions/workflows/publish.yaml/badge.svg)](https://github.com/fynnfluegge/codeqai/actions/workflows/publish.yaml)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

</div>


<div align="center">

Search your codebase semantically or chat with it from cli. 100% local support without any dataleaks.

Built with [langchain](https://github.com/langchain-ai/langchain), [treesitter](https://github.com/tree-sitter/tree-sitter), [sentence-transformers](https://github.com/UKPLab/sentence-transformers), [instructor-embedding](https://github.com/xlang-ai/instructor-embedding), [faiss](https://github.com/facebookresearch/faiss), [lama.cpp](https://github.com/ggerganov/llama.cpp), [Ollama](https://github.com/jmorganca/ollama).

</div>

## ✨ Features
- 🔎 Semantic code search
- 💬 GPT-like chat with your codebase
- 💻 100% local embeddings and llms
- 🌐 Also OpenAI and Azure OpenAI support

# 🚀 Usage

# 💡 How it works
The entire git repo is parsed with treesitter to extract all methods with documentations and saved to a local FAISS vector database with either sentence-transformers, instructor or OpenAI's text-embedding-ada-002 embeddings.
Afterwards it is possible to do semantic search on your git repo codebase based on the embedding model. To chat with the codebase locally llama.cpp or Ollama can be used by specifying the desired model. OpenAI or Azure-OpenAI can be used for remote chat models. It is also possible to set up the FAISS db with local embeddings to do sematic search locally and use OpenAI as the chat model.
# FAQ

