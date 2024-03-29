<div align="center">

# codeqai

[![Build](https://github.com/fynnfluegge/codeqai/actions/workflows/build.yaml/badge.svg)](https://github.com/fynnfluegge/codeqai/actions/workflows/build.yaml)
[![Publish](https://github.com/fynnfluegge/codeqai/actions/workflows/publish.yaml/badge.svg)](https://github.com/fynnfluegge/codeqai/actions/workflows/publish.yaml)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

</div>

<div align="center">

Search your codebase semantically or chat with it from cli. Keep the vector database superfast up to date to the latest code changes.
100% local support without any dataleaks.  
Built with [langchain](https://github.com/langchain-ai/langchain), [treesitter](https://github.com/tree-sitter/tree-sitter), [sentence-transformers](https://github.com/UKPLab/sentence-transformers), [instructor-embedding](https://github.com/xlang-ai/instructor-embedding),
[faiss](https://github.com/facebookresearch/faiss), [lama.cpp](https://github.com/ggerganov/llama.cpp), [Ollama](https://github.com/jmorganca/ollama), [Streamlit](https://github.com/streamlit/streamlit).

</div>

## ✨ Features

- 🔎 &nbsp;Semantic code search
- 💬 &nbsp;GPT-like chat with your codebase
- ⚙️ &nbsp;Synchronize vector store and latest code changes with ease
- 💻 &nbsp;100% local embeddings and llms
  - sentence-transformers, instructor-embeddings, llama.cpp, Ollama
- 🌐 &nbsp;OpenAI, Azure OpenAI and Anthropic
- 🌳 &nbsp;Treesitter integration

> [!NOTE]  
> There will be better results if the code is well documented. You might consider [doc-comments-ai](https://github.com/fynnfluegge/doc-comments.ai) for code documentation generation.

## 🚀 Usage

#### Start semantic search:

```
codeqai search
```

<div align="center">
  
<img src="https://github.com/fynnfluegge/codeqai/assets/16321871/142576f6-a2d4-41b9-a353-d82da78bc3b8" width="800">

</div>

#### Start chat dialog:

```
codeqai chat
```

<div align="center">

<img src="https://github.com/fynnfluegge/codeqai/assets/16321871/84209b30-1940-4aa5-a9e2-03d699217adf" width="800">

</div>

#### Synchronize vector store with current git checkout:

```
codeqai sync
```

#### Start Streamlit app:

```
codeqai app
```

<div align="center">
  
  <img src="https://github.com/fynnfluegge/codeqai/assets/16321871/3a9105f1-066a-4cbd-a096-c8a7bd2068d3" width="800">
  
</div>

> [!NOTE]
> At first usage, the repository will be indexed with the configured embeddings model which might take a while.

## 📋 Requirements

- Python >=3.9,<3.12

## 📦 Installation

Install in an isolated environment with `pipx`:

```
pipx install codeqai
```

⚠ Make sure pipx is using Python >=3.9,<3.12.  
To specify the Python version explicitly with pipx, activate the desired Python version (e.g. with `pyenv shell 3.X.X`) and intall with:

```
pipx install codeqai --python $(which python)
```

If you are still facing issues using pipx you can also install directly from source through PyPI with:

```
pip install codeqai
```

However, it is recommended to use pipx to benefit from isolated environments for the dependencies.  
Visit the [Troubleshooting](https://github.com/fynnfluegge/codeqai?tab=readme-ov-file#-troubleshooting) section for solutions of known issues during installation.

> [!NOTE]  
> Some packages are not installed by default. At first usage it is asked to install `faiss-cpu` or `faiss-gpu`. Faiss-gpu is recommended if the hardware supports CUDA 7.5+.
> If local embeddings and llms are used it will be further asked to install sentence-transformers, instructor or llama.cpp.

## 🔧 Configuration

At first usage or by running

```
codeqai configure
```

the configuration process is initiated, where the embeddings and llms can be chosen.

> [!IMPORTANT]  
> If you want to change the embeddings model in the configuration later, delete the cached files in `~/.cache/codeqai`.
> Afterwards the vector store files are created again with the recent configured embeddings model. This is neccessary since the similarity search does not work if the models differ.

## 🌐 Remote models

If remote models are used, the following environment variables are required.
If the required environment variables are already set, they will be used, otherwise you will be prompted to enter them which are then stored in `~/.config/codeqai/.env`.

### OpenAI

```bash
export OPENAI_API_KEY = "your OpenAI api key"
```

### Azure OpenAI

```bash
export OPENAI_API_TYPE = "azure"
export AZURE_OPENAI_ENDPOINT = "https://<your-endpoint>.openai.azure.com/"
export OPENAI_API_KEY = "your Azure OpenAI api key"
export OPENAI_API_VERSION = "2023-05-15"
```

### Anthropic

```bash
export ANTHROPIC_API_KEY="your Anthropic api key"
```

> [!NOTE]  
> To change the environment variables later, update the `~/.config/codeqai/.env` manually.

## 📚 Supported Languages

- [x] Python
- [x] Typescript
- [x] Javascript
- [x] Java
- [x] Rust
- [x] Kotlin
- [x] Go
- [x] C++
- [x] C
- [x] C#
- [x] Ruby

## 💡 How it works

The entire git repo is parsed with treesitter to extract all methods with documentations and saved to a local FAISS vector database with either sentence-transformers, instructor-embeddings or OpenAI's text-embedding-ada-002.  
The vector database is saved to a file on your system and will be loaded later again after further usage.
Afterwards it is possible to do semantic search on the codebase based on the embeddings model.  
To chat with the codebase locally llama.cpp or Ollama is used by specifying the desired model.
For synchronization of recent changes in the repository, the git commit hashes of each file along with the vector Ids are saved to a cache.
When synchronizing the vector database with the latest git state, the cached commit hashes are compared to the current git hash of each file in the repository.
If the git commit hashes differ, the related vectors are deleted from the database and inserted again after recreating the vector embeddings.
Using llama.cpp the specified model needs to be available on the system in advance.
Using Ollama the Ollama container with the desired model needs to be running locally in advance on port 11434.
Also OpenAI or Azure-OpenAI can be used for remote chat models.

## ？FAQ

### Where do I get models for llama.cpp?

Install the `huggingface-cli` and download your desired model from the model hub.
For example

```
huggingface-cli download TheBloke/CodeLlama-13B-Python-GGUF codellama-13b-python.Q5_K_M.gguf
```

will download the `codellama-13b-python.Q5_K_M` model. After the download has finished the absolute path of the model `.gguf` file is printed to the console.

> [!IMPORTANT]  
> `llama.cpp` compatible models must be in the `.gguf` format.

## 🛟 Troubleshooting

- ### During installation with `pipx`

  ```
  pip failed to build package: tiktoken

  Some possibly relevant errors from pip install:
    error: subprocess-exited-with-error
    error: can't find Rust compiler
  ```

  Make sure the rust compiler is installed on your system from [here](https://www.rust-lang.org/tools/install).

- ### During installation of `faiss`
  ```
  × Building wheel for faiss-cpu (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [12 lines of output]
      running bdist_wheel
      ...
  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for faiss-cpu
  Failed to build faiss-cpu
  ERROR: Could not build wheels for faiss-cpu, which is required to install pyproject.toml-based projects
  ```
  Make sure to have codeqai installed with Python <3.12. There is no faiss wheel available yet for Python 3.12.

## 🌟 Contributing

If you are missing a feature or facing a bug don't hesitate to open an issue or raise a PR.
Any kind of contribution is highly appreciated!
