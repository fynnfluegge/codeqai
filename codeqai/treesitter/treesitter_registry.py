from codeqai.constants import Language


class TreesitterRegistry:
    _registry = {}

    @classmethod
    def register_treesitter(cls, name, treesitter_class):
        cls._registry[name] = treesitter_class

    @classmethod
    def create_treesitter(cls, name: Language):
        treesitter_class = cls._registry.get(name)
        if treesitter_class:
            return treesitter_class()
        else:
            raise ValueError("Invalid tree type")
