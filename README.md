<div align="center">

# codeqai

[![Build](https://github.com/fynnfluegge/codeqai/actions/workflows/build.yaml/badge.svg)](https://github.com/fynnfluegge/codeqai/actions/workflows/build.yaml)
[![Publish](https://github.com/fynnfluegge/codeqai/actions/workflows/publish.yaml/badge.svg)](https://github.com/fynnfluegge/codeqai/actions/workflows/publish.yaml)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

</div>

<div align="center">

Search your codebase semantically or chat with it from cli. 100% local support without any dataleaks.

Built with [langchain](https://github.com/langchain-ai/langchain), [treesitter](https://github.com/tree-sitter/tree-sitter), [sentence-transformers](https://github.com/UKPLab/sentence-transformers), [instructor-embedding](https://github.com/xlang-ai/instructor-embedding), [faiss](https://github.com/facebookresearch/faiss), [lama.cpp](https://github.com/ggerganov/llama.cpp), [Ollama](https://github.com/jmorganca/ollama).


https://github.com/fynnfluegge/codeqai/assets/16321871/fec083f0-9fec-4896-8c58-c3b2726485c2


</div>

## ✨ Features
- 🔎 Semantic code search
- 💬 GPT-like chat with your codebase
- 💻 100% local embeddings and llms
  - sentence-transformers, instructor-embeddings, llama.cpp, Ollama 
- 🌐 OpenAI and Azure OpenAI support

> [!NOTE]  
> There will be better results if the code is well documented. You might consider [doc-comments-ai](https://github.com/fynnfluegge/doc-comments.ai) for code documentation generation.

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
At first usage it is asked to install faiss-cpu or faiss-gpu. Faiss-gpu is recommended if the hardware supports CUDA 7.5+.
If local embeddings and llms are used it will be further asked to install sentence-transformers, instructor or llama.cpp later.

## ⚙️ Configuration
At first usage or by running
```
codeqai configure
```
the configuration process is initiated, where the embeddings and llms can be chosen.

## OpenAI
```bash
export OPENAI_API_KEY = "your OpenAI api key"
```

## Azure OpenAI
```bash
export OPENAI_API_TYPE = "azure"
export OPENAI_API_BASE = "https://<your-endpoint.openai.azure.com/"
export OPENAI_API_KEY = "your AzureOpenAI api key"
export OPENAI_API_VERSION = "2023-05-15"
```

## 💡 How it works
The entire git repo is parsed with treesitter to extract all methods with documentations and saved to a local FAISS vector database with either sentence-transformers, instructor-embeddings or OpenAI's text-embedding-ada-002.
The vector database is saved to a file on your system and will be loaded later again after further usage.  
Afterwards it is possible to do semantic search on the codebase based on the embeddings model.  
To chat with the codebase locally llama.cpp or Ollama is used by specifying the desired model.
Using llama.cpp the specified model needs to be available on the system in advance. 
Using Ollama the Ollama container with the desired model needs to be running locally in advance on port 11434.
Also OpenAI or Azure-OpenAI can be used for remote chat models.  

## 📚 Supported Languages
- [x] Python
- [x] Typescript
- [x] Javascript
- [x] Java
- [x] Rust
- [x] Kotlin
- [x] Go
- [ ] C++
- [ ] C
- [ ] Lua
- [ ] Scala

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

