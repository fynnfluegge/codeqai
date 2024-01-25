from codeqai.constants import Language
from codeqai.treesitter.treesitter import Treesitter
from codeqai.treesitter.treesitter_registry import TreesitterRegistry


class TreesitterKotlin(Treesitter):
    def __init__(self):
        super().__init__(
            Language.KOTLIN, "function_declaration", "simple_identifier", "comment"
        )


TreesitterRegistry.register_treesitter(Language.KOTLIN, TreesitterKotlin)
