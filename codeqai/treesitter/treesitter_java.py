from codeqai.constants import Language
from codeqai.treesitter.treesitter import Treesitter
from codeqai.treesitter.treesitter_registry import TreesitterRegistry


class TreesitterJava(Treesitter):
    def __init__(self):
        super().__init__(
            Language.JAVA, "method_declaration", "identifier", "block_comment"
        )


TreesitterRegistry.register_treesitter(Language.JAVA, TreesitterJava)
