import os

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from codeqai import repo, utils
from codeqai.constants import Language
from codeqai.treesitter.treesitter import Treesitter, TreesitterMethodNode


def parse_code_files(code_files: list[str]) -> list[Document]:
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
