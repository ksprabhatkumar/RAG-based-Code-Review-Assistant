import argparse
import json
from ingestion.diff_parser import parse_diff
from ingestion.ast_expander import expand_hunk_to_ast
from retrieval.indexer import HybridRetriever
from generation.generator import generate_review

def main():
    parser = argparse.ArgumentParser(description="RAG Code Reviewer CLI")
    parser.add_argument("--diff", type=str, required=True, help="Path to the diff file")
    parser.add_argument("--repo", type=str, required=True, help="Path to the local repo (for full file lookup)")
    args = parser.parse_args()

    # 1. Setup Retrieval (Mocking indexing a style guide for Phase 1)
    retriever = HybridRetriever()
    retriever.index_documents(
        documents=["Use type hints for all function arguments.", "Avoid deeply nested for loops."],
        ids=["style_guide_001", "style_guide_002"]
    )

    # 2. Parse Diff
    with open(args.diff, 'r') as f:
        diff_text = f.read()
    hunks = parse_diff(diff_text)
    
    print(f"Found {len(hunks)} changed hunks. Analyzing...")

    # 3. Process each hunk
    results = []
    for hunk in hunks:
        # Load the actual current file from the local repo
        file_path = f"{args.repo}/{hunk['file']}"
        try:
            with open(file_path, 'r') as f:
                source_code = f.read()
        except FileNotFoundError:
            continue

        # Expand to AST
        expanded_code = expand_hunk_to_ast(source_code, hunk['start_line'])
        
        # Retrieve Context
        query = expanded_code # Using the code itself as the query for MVP
        context = retriever.retrieve(query)
        
        # Generate Review
        review = generate_review(hunk, expanded_code, context)
        results.append(review)

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
