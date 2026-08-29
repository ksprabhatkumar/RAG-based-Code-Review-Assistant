from tree_sitter import Node
from .parser import get_python_parser

def find_enclosing_function(node: Node, target_line: int) -> Node:
    """Recursively traverse AST to find the function/class enclosing the changed line."""
    # Tree-sitter lines are 0-indexed, target_line is usually 1-indexed
    start_row, _ = node.start_point
    end_row, _ = node.end_point
    
    if start_row <= target_line <= end_row:
        if node.type in ['function_definition', 'class_definition']:
            return node
        
        for child in node.children:
            result = find_enclosing_function(child, target_line)
            if result:
                return result
    return None

def expand_hunk_to_ast(source_code: str, target_line: int) -> str:
    """Given a file and a changed line, return the full text of the enclosing function."""
    parser = get_python_parser()
    tree = parser.parse(bytes(source_code, "utf8"))
    
    # 0-index the line for tree-sitter
    enclosing_node = find_enclosing_function(tree.root_node, target_line - 1)
    
    if enclosing_node:
        return source_code.encode("utf8")[enclosing_node.start_byte:enclosing_node.end_byte].decode("utf8")
    return "No enclosing function found. Hunk is at module level."
