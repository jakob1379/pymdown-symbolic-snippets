# pymdown-symbolic-snippets

Reference Python code in your docs by symbol, not by line number.
A Python-Markdown extension that makes `pymdownx.snippets` symbol-aware.

[![PyPI](https://img.shields.io/pypi/v/pymdown-symbolic-snippets)](https://pypi.org/project/pymdown-symbolic-snippets/)
[![Python 3.13 | 3.14](https://img.shields.io/badge/python-3.13%20%7C%203.14-3776ab)](pyproject.toml)
[![CI](https://github.com/jakob1379/pymdown-symbolic-snippets/actions/workflows/ci.yml/badge.svg)](https://github.com/jakob1379/pymdown-symbolic-snippets/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-2b6b4c)](LICENSE)

<p align="center">
  <img src=".github/assets/symbol-to-span.svg" width="960" alt="The snippet reference pymdown_symbolic_snippets.symbolic_snippets:SymbolResolver.resolve is found in the module's AST and rewritten to the line span symbolic_snippets.py:90:90,98:141, which renders as the class header plus the resolve method. After six lines are added above the class, the span becomes 96:96,104:147 and the rendered snippet is unchanged.">
</p>

```text
--8<-- "my_pkg.api:Client.send"
```

Raw line ranges like `file.py:88:121` rot as soon as code moves. This extension
parses the module with `ast` at build time, finds the symbol, and rewrites the
reference to the current line span before `pymdownx.snippets` reads it. Your
Markdown stays standard snippets syntax.

## Install

```bash
uv add pymdown-symbolic-snippets
```

Or:

```bash
pip install pymdown-symbolic-snippets
```

`zensical` is optional. This package works as a plain Python-Markdown extension;
install `zensical` only if you want to run Zensical builds.

## Configure

Register the extension **before** `pymdownx.snippets`.

### Python-Markdown

```python
import markdown

md = markdown.Markdown(
    extensions=[
        "pymdown_symbolic_snippets",
        "pymdownx.snippets",
    ],
    extension_configs={
        "pymdown_symbolic_snippets": {
            "module_roots": ["src"],
            "fail_on_unresolved": True,
        },
        "pymdownx.snippets": {
            "base_path": ["src"],
            "check_paths": True,
        },
    },
)
```

### Zensical (`site.toml`)

```toml
[project.markdown_extensions.pymdown_symbolic_snippets]
module_roots = ["src"]
fail_on_unresolved = true

[project.markdown_extensions.pymdownx.highlight]
anchor_linenums = true
line_spans = "__span"
pygments_lang_class = true

[project.markdown_extensions.pymdownx.snippets]
base_path = ["src"]
check_paths = true

[project.markdown_extensions.pymdownx.superfences]
```

If you define `project.markdown_extensions` explicitly, include every extension
you rely on. Leaving out `pymdownx.superfences`/`pymdownx.highlight` makes fenced
blocks render as plain text.

### Options

| Option | Default | What it does |
| --- | --- | --- |
| `module_roots` | `["."]` | Paths that dotted module names resolve from |
| `encoding` | `"utf-8"` | Encoding used when reading Python source modules |
| `fail_on_unresolved` | `true` | Fail the build when module or symbol resolution fails |

## Reference format

`<module.path>:<symbol>(.<nested>)[:start[:end]]`

Examples:

- `my_pkg.api:build_payload`
- `my_pkg.api:Client.send`
- `my_pkg.config:DEFAULT_TIMEOUT:-1:2`

Resolved output is rewritten to standard snippets format:

`path/to/file.py:start:end`

For method references without selectors, output uses a multi-range selector so
the class header and method body are included together:

`path/to/file.py:class_header_start:class_header_end,method_start:method_end`

### Selectors

- No selector: the whole symbol is used.
- Method with no selector: the class declaration line(s) plus that method's
  body, but not other methods in the class (for example, not `__init__`).
- `:start` starts at this line (relative to the symbol) and runs to the end of
  the symbol.
- `:start:end` uses only this relative line range inside the symbol.
- Positive numbers are 1-based: `1` is the first line of the symbol.
- `0` and negative numbers are offsets: `0` is the symbol start, `-1` is one
  line above it.
- Values past the file limits are clamped to valid file bounds.
- An invalid range (`end < start`) fails resolution.

## Backward compatibility

Existing `pymdownx.snippets` syntax keeps working unchanged. Symbolic resolution
only applies when the target matches a real Python module under `module_roots`.

```text
--8<-- "docs/intro.md"
--8<-- "docs/intro.md:intro"
--8<-- "src/my_pkg/api.py:12:20"
--8<-- "my_pkg.api:Client.send"
```

## How it compares

Research summary across `pymdown-extensions`, `mkdocs`, `mkdocs-material`, and
common include plugins:

| Tool / project | Symbol path include (`module:Class.method`) | AST/introspection-based resolution | Generic snippet include | Equivalent to this project |
| --- | --- | --- | --- | --- |
| [`pymdownx.snippets`](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/) | No | No | Yes (file, line ranges, named marker sections) | No |
| [`mkdocs`](https://www.mkdocs.org/user-guide/configuration/#markdown_extensions) | No | No | Not in core (delegates to extensions/plugins) | No |
| [`mkdocs-material`](https://squidfunk.github.io/mkdocs-material/reference/code-blocks/#embedding-external-files) | No | No | Yes via upstream `pymdownx.snippets` | No |
| [`mkdocstrings/python`](https://mkdocstrings.github.io/python/usage/configuration/general/#show_source) | Partial (API object rendering) | Yes (object collection) | No (not a general snippets include engine) | Partial |
| [`mkdocs-codeinclude-plugin`](https://github.com/rnorth/mkdocs-codeinclude-plugin) | No | No | Yes (token/brace-targeted blocks) | No |
| [`mkdocs-include-markdown-plugin`](https://github.com/mondeja/mkdocs-include-markdown-plugin) | No | No | Yes (delimiter-based includes) | No |
| `pymdown-symbolic-snippets` (this project) | Yes | Yes | Yes (rewrites to `pymdownx.snippets` line spans) | Yes |

Bottom line: existing options either slice by lines/markers or render API docs;
none provide first-class symbol-addressed snippet transclusion in the same
workflow as `pymdownx.snippets`.

## Proof project

This repo includes a working Zensical example that references this package's
own source:

- Config: [`examples/symbolic-snippets/site.toml`](examples/symbolic-snippets/site.toml)
- Docs page: [`examples/symbolic-snippets/docs/index.md`](examples/symbolic-snippets/docs/index.md)

Build it:

```bash
uv run zensical build --config-file examples/symbolic-snippets/site.toml
```

Tiny output example (from `examples/symbolic-snippets/site/index.html`):

```py
def parse_symbolic_reference(value: str) -> SymbolicReference | None:
    if ":" not in value:
        return None
```

## Development

### Tests

```bash
uv run pytest
```

The suite includes parser/resolver tests plus an E2E Zensical build test that
asserts resolved symbols are rendered in generated HTML.

### Release automation

GitHub Actions publishes to PyPI on strict semver tags:

- CI workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
- Release workflow: [`.github/workflows/release.yml`](.github/workflows/release.yml)
- Trigger: push a tag matching `vX.Y.Z`
- Guardrails: the tag must be strict semver and match `project.version` in
  `pyproject.toml`
- Gate: the test matrix (`3.13`, `3.14`) must pass before publish

One-time GitHub setup for trusted publishing:

1. Create environment `pypi` in repository settings.
2. Configure PyPI Trusted Publisher for this repository/workflow.

Release command:

```bash
git tag v0.1.0
git push upstream v0.1.0
```

## License

[MIT](LICENSE)
