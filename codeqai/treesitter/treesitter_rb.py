import tree_sitter

from codeqai.constants import Language
from codeqai.treesitter.treesitter import Treesitter, TreesitterMethodNode
from codeqai.treesitter.treesitter_registry import TreesitterRegistry


class TreesitterRuby(Treesitter):
    def __init__(self):
        super().__init__(
            Language.RUBY, "method", "identifier", "comment"
        )

    def parse(self, file_bytes: bytes) -> list[TreesitterMethodNode]:
        return super().parse(file_bytes)

# Register the TreesitterJava class in the registry
TreesitterRegistry.register_treesitter(Language.RUBY, TreesitterRuby)