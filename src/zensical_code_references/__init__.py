import warnings

from pymdown_symbolic_snippets import SymbolicSnippetsExtension, __version__

warnings.warn(
    "zensical_code_references is deprecated; use pymdown_symbolic_snippets instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["SymbolicSnippetsExtension", "__version__"]
