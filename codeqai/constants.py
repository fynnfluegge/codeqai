from enum import Enum


class Language(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    KOTLIN = "kotlin"
    C_SHARP = "c_sharp"
    OBJECTIVE_C = "objective_c"
    SCALA = "scala"
    LUA = "lua"
    HASKELL = "haskell"
    UNKNOWN = "unknown"


class EmbeddingsModel(Enum):
    SENTENCETRANSFORMERS_ALL_MPNET_BASE_V2 = "SentenceTransformers-all-mpnet-base-v2"
    SENTENCETRANSFORMERS_ALL_MINILM_L6_V2 = "SentenceTransformers-all-MiniLM-L6-v2"
    INSTRUCTOR_LARGE = "Instructor-Large"
    OPENAI_TEXT_EMBEDDING_ADA_002 = "OpenAI-text-embedding-ada-002"
    AZURE_OPENAI = "Azure-OpenAI"


class LlmHost(Enum):
    LLAMACPP = "Llamacpp"
    OLLAMA = "Ollama"
    OPENAI = "OpenAI"
    AZURE_OPENAI = "Azure-OpenAI"
