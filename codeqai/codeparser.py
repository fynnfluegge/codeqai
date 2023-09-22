import re

from langchain.schema import Document

from codeqai import utils
from codeqai.constants import Language
from codeqai.treesitter.treesitter import Treesitter, TreesitterMethodNode


def parse_code_files(code_files: list[str]) -> list[Document]:
    documents = []
    for code_file in code_files:
        with open(code_file, "r") as file:
            file_bytes = file.read().encode()

            file_extension = utils.get_file_extension(code_file)
            programming_language = utils.get_programming_language(file_extension)

            treesitter_parser = Treesitter.create_treesitter(programming_language)
            treesitterNodes: list[TreesitterMethodNode] = treesitter_parser.parse(
                file_bytes
            )
            for node in treesitterNodes:
                method_source_code = node.method_source_code
                if programming_language == Language.PYTHON:
                    docstring_pattern = r"(\'\'\'(.*?)\'\'\'|\"\"\"(.*?)\"\"\")"
                    method_source_code = re.sub(
                        docstring_pattern, "", node.method_source_code, flags=re.DOTALL
                    )
                documents.append(
                    Document(
                        page_content=method_source_code,
                        metadata={
                            "file_name": code_file,
                            "method_name": node.name,
                        },
                    )
                )
                if node.doc_comment:
                    documents.append(
                        Document(
                            page_content=node.doc_comment,
                            metadata={
                                "file_name": code_file,
                                "method_name": node.name,
                            },
                        )
                    )

    return documents
