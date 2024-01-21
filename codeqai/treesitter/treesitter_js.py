from codeqai.constants import Language
from codeqai.treesitter.treesitter import Treesitter
from codeqai.treesitter.treesitter_registry import TreesitterRegistry


class TreesitterJavascript(Treesitter):
    def __init__(self):
        super().__init__(
            Language.JAVASCRIPT, "function_declaration", "identifier", "comment"
        )


TreesitterRegistry.register_treesitter(Language.JAVASCRIPT, TreesitterJavascript)
