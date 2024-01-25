import tree_sitter

from codeqai.constants import Language
from codeqai.treesitter.treesitter import Treesitter
from codeqai.treesitter.treesitter_registry import TreesitterRegistry


class TreesitterCsharp(Treesitter):
    def __init__(self):
        super().__init__(
            Language.C_SHARP, "method_declaration", "identifier", "comment"
        )

    def _query_method_name(self, node: tree_sitter.Node):
        first_match = None
        if node.type == self.method_declaration_identifier:
            for child in node.children:
                # if the return type is an object type, then the method name
                # is the second match
                if child.type == self.method_name_identifier and not first_match:
                    first_match = child.text.decode()
                elif child.type == self.method_name_identifier and first_match:
                    return child.text.decode()
        return first_match

    def _query_all_methods(self, node: tree_sitter.Node):
        methods = []
        if node.type == self.method_declaration_identifier:
            doc_comment_nodes = []
            if (
                node.prev_named_sibling
                and node.prev_named_sibling.type == self.doc_comment_identifier
            ):
                current_doc_comment_node = node.prev_named_sibling
                while (
                    current_doc_comment_node
                    and current_doc_comment_node.type == self.doc_comment_identifier
                ):
                    doc_comment_nodes.append(current_doc_comment_node.text.decode())
                    if current_doc_comment_node.prev_named_sibling:
                        current_doc_comment_node = (
                            current_doc_comment_node.prev_named_sibling
                        )
                    else:
                        current_doc_comment_node = None

            doc_comment_str = ""
            doc_comment_nodes.reverse()
            for doc_comment_node in doc_comment_nodes:
                doc_comment_str += doc_comment_node + "\n"
            if doc_comment_str.strip() != "":
                methods.append({"method": node, "doc_comment": doc_comment_str.strip()})
            else:
                methods.append({"method": node, "doc_comment": None})
        else:
            for child in node.children:
                methods.extend(self._query_all_methods(child))
        return methods


TreesitterRegistry.register_treesitter(Language.C_SHARP, TreesitterCsharp)
