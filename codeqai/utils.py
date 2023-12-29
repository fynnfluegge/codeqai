import os

import langchain.text_splitter as text_splitter

from codeqai.constants import Language


def get_programming_language(file_extension: str) -> Language:
    """
    Returns the programming language based on the provided file extension.

    Args:
        file_extension (str): The file extension to determine the programming language of.

    Returns:
        Language: The programming language corresponding to the file extension. If the file extension is not found
        in the language mapping, returns Language.UNKNOWN.
    """
    language_mapping = {
        ".py": Language.PYTHON,
        ".js": Language.JAVASCRIPT,
        ".jsx": Language.JAVASCRIPT,
        ".mjs": Language.JAVASCRIPT,
        ".cjs": Language.JAVASCRIPT,
        ".ts": Language.TYPESCRIPT,
        ".tsx": Language.TYPESCRIPT,
        ".java": Language.JAVA,
        ".kt": Language.KOTLIN,
        ".rs": Language.RUST,
        ".go": Language.GO,
        ".cpp": Language.CPP,
        ".c": Language.C,
        ".cs": Language.C_SHARP,
    }
    return language_mapping.get(file_extension, Language.UNKNOWN)


def get_file_extension(file_name: str) -> str:
    """
    Returns the extension of a file from its given name.

    Parameters:
        file_name (str): The name of the file.

    Returns:
        str: The extension of the file.

    """
    return os.path.splitext(file_name)[-1]


def get_langchain_language(language: Language) -> text_splitter.Language | None:
    if language == Language.PYTHON:
        return text_splitter.Language.PYTHON
    elif language == Language.JAVASCRIPT:
        return text_splitter.Language.JS
    elif language == Language.TYPESCRIPT:
        return text_splitter.Language.TS
    elif language == Language.JAVA:
        return text_splitter.Language.JAVA
    elif language == Language.KOTLIN:
        return text_splitter.Language.KOTLIN
    elif language == Language.RUST:
        return text_splitter.Language.RUST
    elif language == Language.GO:
        return text_splitter.Language.GO
    elif language == Language.CPP:
        return text_splitter.Language.CPP
    elif language == Language.C_SHARP:
        return text_splitter.Language.CSHARP

    return None


def get_bold_text(text):
    return f"\033[01m{text}\033[0m"
