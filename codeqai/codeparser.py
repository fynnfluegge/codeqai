import os

import inquirer
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from codeqai import repo, utils
from codeqai.constants import Language
from codeqai.treesitter.treesitter import Treesitter, TreesitterMethodNode


def parse_code_files_for_db(code_files: list[str]) -> list[Document]:
    """
    Parses a list of code files and returns a list of Document objects for database storage.

    Args:
        code_files (list[str]): List of paths to code files to be parsed.

    Returns:
        list[Document]: List of Document objects containing parsed code information.
    """
    documents = []
    code_splitter = None
    for code_file in code_files:
        with open(code_file, "r", encoding="utf-8") as file:
            file_bytes = file.read().encode()
            commit_hash = repo.get_commit_hash(code_file)

            file_extension = utils.get_file_extension(code_file)
            programming_language = utils.get_programming_language(file_extension)
            if programming_language == Language.UNKNOWN:
                continue

            langchain_language = utils.get_langchain_language(programming_language)

            if langchain_language:
                code_splitter = RecursiveCharacterTextSplitter.from_language(
                    language=langchain_language,
                    chunk_size=512,
                    chunk_overlap=128,
                )

            treesitter_parser = Treesitter.create_treesitter(programming_language)
            treesitterNodes: list[TreesitterMethodNode] = treesitter_parser.parse(
                file_bytes
            )
            for node in treesitterNodes:
                method_source_code = node.method_source_code
                filename = os.path.basename(code_file)

                if node.doc_comment and programming_language != Language.PYTHON:
                    method_source_code = node.doc_comment + "\n" + method_source_code

                splitted_documents = [method_source_code]
                if code_splitter:
                    splitted_documents = code_splitter.split_text(method_source_code)

                for splitted_document in splitted_documents:
                    document = Document(
                        page_content=splitted_document,
                        metadata={
                            "filename": filename,
                            "method_name": node.name,
                            "commit_hash": commit_hash,
                        },
                    )
                    documents.append(document)

    return documents


def parse_code_files_for_finetuning(code_files: list[str], max_tokens) -> list[dict]:
    """
    Parses a list of code files for fine-tuning and returns a list of dictionaries containing method information.

    Args:
        code_files (list[str]): List of paths to code files to be parsed.
        max_tokens (int): Maximum number of tokens allowed for output.

    Returns:
        list[dict]: List of dictionaries containing method information, including method name, code, description, and language.
    """
    input_tokens = 0
    output_tokens = 0
    documents = []
    for code_file in code_files:
        with open(code_file, "r", encoding="utf-8") as file:
            file_bytes = file.read().encode()

            file_extension = utils.get_file_extension(code_file)
            programming_language = utils.get_programming_language(file_extension)
            if programming_language == Language.UNKNOWN:
                continue

            treesitter_parser = Treesitter.create_treesitter(programming_language)
            treesitterNodes: list[TreesitterMethodNode] = treesitter_parser.parse(
                file_bytes
            )
            for node in treesitterNodes:
                method_source_code = node.method_source_code

                if node.doc_comment and programming_language == Language.PYTHON:
                    method_source_code = method_source_code.replace(
                        node.doc_comment, ""
                    )

                document = {
                    "method_name": node.name,
                    "code": method_source_code,
                    "description": node.doc_comment,
                    "language": programming_language.value,
                }
                documents.append(document)

                if node.doc_comment is not None:
                    input_tokens += utils.count_tokens(node.doc_comment)
                    output_tokens += max_tokens

    questions = [
        inquirer.Confirm(
            "confirm",
            message=f"Estimated input tokens for distillation needed: {input_tokens}. "
            + f"Maximum output tokens nedeed: {output_tokens}. Proceed?",
            default=True,
        ),
    ]

    confirm = inquirer.prompt(questions)

    if confirm and confirm["confirm"]:
        pass
    else:
        exit()

    return documents
