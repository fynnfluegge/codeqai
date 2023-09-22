import tree_sitter

from codeqai.constants import Language
from codeqai.treesitter.treesitter import Treesitter, TreesitterMethodNode
from codeqai.treesitter.treesitter_registry import TreesitterRegistry


class TreesitterJava(Treesitter):
    def __init__(self):
        super().__init__(Language.JAVA)

    def parse(self, file_bytes: bytes) -> list[TreesitterMethodNode]:
        super().parse(file_bytes)
        methods = self._query_all_methods(self.tree.root_node)
        return self.parse_methods(methods)

    def _query_all_methods(self, node: tree_sitter.Node):
        query_code = """
        (block_comment) @doc_comment
        (method_declaration
            name: (identifier) @method_name) @method
        """
        query = self.language.query(query_code)
        return query.captures(node)


# Register the TreesitterJava class in the registry
TreesitterRegistry.register_treesitter(Language.JAVA, TreesitterJava)
