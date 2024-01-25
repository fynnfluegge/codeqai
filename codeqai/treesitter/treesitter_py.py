import tree_sitter

from codeqai.constants import Language
from codeqai.treesitter.treesitter import Treesitter, TreesitterMethodNode
from codeqai.treesitter.treesitter_registry import TreesitterRegistry


class TreesitterPython(Treesitter):
    def __init__(self):
        super().__init__(
            Language.PYTHON, "function_definition", "identifier", "expression_statement"
        )

    def parse(self, file_bytes: bytes) -> list[TreesitterMethodNode]:
        self.tree = self.parser.parse(file_bytes)
        result = []
        methods = self._query_all_methods(self.tree.root_node)
        for method in methods:
            method_name = self._query_method_name(method)
            doc_comment = self._query_doc_comment(method)
            result.append(TreesitterMethodNode(method_name, doc_comment, None, method))
        return result

    def _query_method_name(self, node: tree_sitter.Node):
        if node.type == self.method_declaration_identifier:
            for child in node.children:
                if child.type == self.method_name_identifier:
                    return child.text.decode()
        return None

    def _query_all_methods(self, node: tree_sitter.Node):
        methods = []
        for child in node.children:
            if child.type == self.method_declaration_identifier:
                methods.append(child)
        return methods

    def _query_doc_comment(self, node: tree_sitter.Node):
        query_code = """
            (function_definition
                body: (block . (expression_statement (string)) @function_doc_str))
        """
        doc_str_query = self.language.query(query_code)
        doc_strs = doc_str_query.captures(node)

        if doc_strs:
            return doc_strs[0][0].text.decode()
        else:
            return None


TreesitterRegistry.register_treesitter(Language.PYTHON, TreesitterPython)
