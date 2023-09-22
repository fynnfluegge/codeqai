import tree_sitter

from codeqai.constants import Language
from codeqai.treesitter.treesitter import Treesitter, TreesitterMethodNode
from codeqai.treesitter.treesitter_registry import TreesitterRegistry


class TreesitterRust(Treesitter):
    def __init__(self):
        super().__init__(Language.RUST)

    def parse(self, file_bytes: bytes) -> list[TreesitterMethodNode]:
        super().parse(file_bytes)
        result = []
        methods = self._query_all_methods(self.tree.root_node)
        for method in methods:
            method_name = self._query_method_name(method["method"])
            doc_comment = method["doc_comment"]
            result.append(
                TreesitterMethodNode(method_name, doc_comment, method["method"])
            )
        return result

    def _query_method_name(self, node: tree_sitter.Node):
        if node.type == "function_item":
            for child in node.children:
                if child.type == "identifier":
                    return child.text.decode()
        return None

    def _query_all_methods(self, node: tree_sitter.Node):
        methods = []
        if node.type == "function_item":
            doc_comment_nodes = []
            if (
                node.prev_named_sibling
                and node.prev_named_sibling.type == "line_comment"
            ):
                current_doc_comment_node = node.prev_named_sibling
                while (
                    current_doc_comment_node
                    and current_doc_comment_node.type == "line_comment"
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


# Register the TreesitterJava class in the registry
TreesitterRegistry.register_treesitter(Language.RUST, TreesitterRust)
