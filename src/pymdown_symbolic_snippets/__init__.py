from importlib.metadata import version

from .symbolic_snippets import SymbolicSnippetsExtension

__version__ = version("pymdown-symbolic-snippets")

__all__ = ["SymbolicSnippetsExtension", "__version__"]
