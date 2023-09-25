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

> [!NOTE]  
> You will get better results if your code is well documented. You might consider [doc-comments-ai](https://github.com/fynnfluegge/doc-comments.ai) for code documentation generation.

## 🚀 Usage
Start semantic search:
```
codeqai search
```
Start chat dialog:
```
codeqai chat
```

## 📋 Requirements 
- Python >= 3.9

## 🔧 Installation
```
pipx install codeqai
```
At first usage you can choose to install faiss-cpu or faiss-gpu.
If you are using local embeddings and llms you will be further asked to install sentence-transformers, instructor or llama.cpp later, based on your configuration.

## ⚙️ Configuration
At first usage or by running
```
codeqai configure
```
you are prompted to the configuration process, where you can choose the embeddings and llms.

## 💡 How it works
The entire git repo is parsed with treesitter to extract all methods with documentations and saved to a local FAISS vector database with either sentence-transformers, instructor or OpenAI's text-embedding-ada-002 embeddings.
Afterwards it is possible to do semantic search on your git repo codebase based on the embedding model. To chat with the codebase locally llama.cpp or Ollama can be used by specifying the desired model. OpenAI or Azure-OpenAI can be used for remote chat models. It is also possible to set up the FAISS db with local embeddings to do sematic search locally and use OpenAI as the chat model.

## FAQ
### Where do I get models for llama.cpp?
Install the `huggingface-cli` and download your desired model from the model hub.
For example
```
huggingface-cli download TheBloke/CodeLlama-13B-Python-GGUF codellama-13b-python.Q5_K_M.gguf
```
will download the `codellama-13b-python.Q5_K_M` model. After the download has finished the absolute path of the model `.gguf` file is printed to the console.
> [!IMPORTANT]  
> `llama.cpp` compatible models must be in the `.gguf` format.

