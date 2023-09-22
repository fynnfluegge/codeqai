import tree_sitter

from codeqai.constants import Language
from codeqai.treesitter.treesitter import Treesitter, TreesitterMethodNode
from codeqai.treesitter.treesitter_registry import TreesitterRegistry


class TreesitterPython(Treesitter):
    def __init__(self):
        super().__init__(Language.PYTHON)

    def parse(self, file_bytes: bytes) -> list[TreesitterMethodNode]:
        super().parse(file_bytes)
        result = []
        methods = self._query_all_methods(self.tree.root_node)
        methods.reverse()
        while methods:
            if methods and methods[-1][1] == "method":
                doc_comment = self._query_doc_comment(methods[-1][0])
                if doc_comment:
                    self.process_method(methods, doc_comment[0], result)
                else:
                    self.process_method(methods, None, result)

        return result

    def _query_all_methods(self, node: tree_sitter.Node):
        query_code = """
        (function_definition
            name: (identifier) @method_name) @method
        """
        query = self.language.query(query_code)
        return query.captures(node)

    def _query_doc_comment(self, node: tree_sitter.Node):
        query_code = "(block . (expression_statement (string)) @doc_str)"
        query = self.language.query(query_code)
        return query.captures(node)


# Register the TreesitterPython class in the registry
TreesitterRegistry.register_treesitter(Language.PYTHON, TreesitterPython)
