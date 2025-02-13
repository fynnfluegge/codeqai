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
        """
        Parses the given file bytes and extracts method nodes.

        Args:
            file_bytes (bytes): The content of the file to be parsed.

        Returns:
            list[TreesitterMethodNode]: A list of TreesitterMethodNode objects representing the methods in the file.
        """
        self.tree = self.parser.parse(file_bytes)
        result = []
        methods = self._query_all_methods(self.tree.root_node)
        for method in methods:
            method_name = self._query_method_name(method)
            doc_comment = self._query_doc_comment(method)
            result.append(TreesitterMethodNode(method_name, doc_comment, None, method))
        return result

    def _query_method_name(self, node: tree_sitter.Node):
        """
        Queries the method name from the given syntax tree node.

        Args:
            node (tree_sitter.Node): The syntax tree node to query.

        Returns:
            str or None: The method name if found, otherwise None.
        """
        if node.type == self.method_declaration_identifier:
            for child in node.children:
                if child.type == self.method_name_identifier:
                    return child.text.decode()
        return None

    def _query_all_methods(self, node: tree_sitter.Node):
        """
        Queries all method nodes within the given syntax tree node, including those within class definitions.

        Args:
            node (tree_sitter.Node): The root node to start the query from.

        Returns:
            list: A list of method nodes found within the given node.
        """
        methods = []
        for child in node.children:
            if child.type == self.method_declaration_identifier:
                methods.append(child)
            if child.type == "class_definition":
                class_body = child.children[-1]
                for child_node in class_body.children:
                    if child_node.type == self.method_declaration_identifier:
                        methods.append(child_node)
        return methods

    def _query_doc_comment(self, node: tree_sitter.Node):
        """
        Queries the documentation comment for the given function definition node.

        Args:
            node (tree_sitter.Node): The syntax tree node representing a function definition.

        Returns:
            str or None: The documentation comment string if found, otherwise None.
        """
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
