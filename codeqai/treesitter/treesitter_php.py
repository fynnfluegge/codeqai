from codeqai.constants import Language
from codeqai.treesitter.treesitter import Treesitter
from codeqai.treesitter.treesitter_registry import TreesitterRegistry


class TreesitterPHP(Treesitter):
    def __init__(self):
        super().__init__(
            Language.PHP, "method_declaration", "name", "comment"
        )


TreesitterRegistry.register_treesitter(Language.PHP, TreesitterPHP)
