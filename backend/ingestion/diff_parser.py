import re
from typing import List, Dict

def parse_diff(diff_text: str) -> List[Dict]:
    """Parse a unified diff into structured hunks of added/modified lines."""
    hunks = []
    current_file = None
    
    lines = diff_text.split('\n')
    for line in lines:
        if line.startswith('+++ b/'):
            current_file = line[6:]
        elif line.startswith('@@') and current_file:
            # Extract the starting line number for the added code
            match = re.search(r'\+([0-9]+)', line)
            if match:
                start_line = int(match.group(1))
                hunks.append({
                    "file": current_file,
                    "start_line": start_line,
                    "added_lines": [] # We will just track the start line for MVP AST expansion
                })
    return hunks
