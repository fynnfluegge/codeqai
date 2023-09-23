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
    UNKNOWN = "unknown"


class EmbeddingsModel(Enum):
    SENTENCETRANSFORMERS_ALL_MPNET_BASE_V2 = "SentenceTransformers-all-mpnet-base-v2"
    INSTRUCTOR_LARGE = "Instructor-Large"
    OLLAMA = "Ollama"
    OPENAI_TEXT_EMBEDDING_ADA_002 = "OpenAI-text-embedding-ada-002"
    AZURE_OPENAI = "Azure-OpenAI"


class LocalLLMModel(Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
