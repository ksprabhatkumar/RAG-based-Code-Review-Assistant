import tree_sitter_python as tspython
from tree_sitter import Language, Parser

def get_python_parser() -> Parser:
    """Initialize and return a tree-sitter Python parser."""
    py_language = Language(tspython.language(), "python")
    parser = Parser()
    parser.set_language(py_language)
    return parser

def parse_code(code: str):
    """Smoke test: parse a string of Python code into an AST."""
    parser = get_python_parser()
    tree = parser.parse(bytes(code, "utf8"))
    return tree
