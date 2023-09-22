import os
import re

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from codeqai import utils
from codeqai.constants import Language
from codeqai.treesitter.treesitter import Treesitter, TreesitterMethodNode


def parse_code_files(code_files: list[str]) -> list[Document]:
    source_code_documents, docstring_documents = [], []
    source_code_splitter = None
    docstring_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512, chunk_overlap=128
    )
    for code_file in code_files:
        with open(code_file, "r") as file:
            file_bytes = file.read().encode()

            file_extension = utils.get_file_extension(code_file)
            programming_language = utils.get_programming_language(file_extension)
            if programming_language == Language.UNKNOWN:
                print(
                    f"Skipping file {code_file} with unsupported programming language"
                )

            langchain_language = utils.get_langchain_language(programming_language)

            if langchain_language:
                source_code_splitter = RecursiveCharacterTextSplitter.from_language(
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
                if programming_language == Language.PYTHON:
                    docstring_pattern = r"(\'\'\'(.*?)\'\'\'|\"\"\"(.*?)\"\"\")"
                    method_source_code = re.sub(
                        docstring_pattern, "", node.method_source_code, flags=re.DOTALL
                    )
                source_code_documents.append(
                    Document(
                        page_content=method_source_code,
                        metadata={
                            "file_name": filename,
                            "method_name": node.name,
                        },
                    )
                )
                if node.doc_comment:
                    docstring_documents.append(
                        Document(
                            page_content=node.doc_comment,
                            metadata={
                                "file_name": filename,
                                "method_name": node.name,
                            },
                        )
                    )

    splitted_source_code_documents = source_code_documents
    if source_code_splitter:
        splitted_source_code_documents = source_code_splitter.split_documents(
            source_code_documents
        )

    splitted_docstring_documents = docstring_splitter.split_documents(
        docstring_documents
    )

    return splitted_source_code_documents + splitted_docstring_documents
