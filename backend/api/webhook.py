from fastapi import APIRouter, Request, BackgroundTasks
from .github_client import GitHubManager
from ingestion.diff_parser import parse_diff
from retrieval.indexer import HybridRetriever
from generation.generator import generate_review
from ingestion.ast_expander import expand_hunk_to_ast
from api.database import SessionLocal, ReviewLog

router = APIRouter()
github_manager = GitHubManager()

# For MVP, we will mock the retriever globally. In prod, this happens on app startup.
retriever = HybridRetriever()
retriever.index_documents(
    documents=["Use type hints for all function arguments.", "Never hardcode secrets like api_key."],
    ids=["style_guide_001", "sec_001"]
)

def process_pr_review(repo_name: str, pr_number: int, commit_id: str):
    """Background task to run the full RAG pipeline on a PR."""
    print(f"Starting TRUE RAG review for {repo_name} PR #{pr_number}")
    
    diff_text = github_manager.get_pr_diff(repo_name, pr_number)
    hunks = parse_diff(diff_text)
    
    for hunk in hunks:
        # 1. Fetch the actual file content from GitHub
        source_code = github_manager.get_file_content(repo_name, commit_id, hunk['file'])
        if not source_code:
            continue
            
        # 2. Expand hunk to AST (Full function context)
        expanded_code = expand_hunk_to_ast(source_code, hunk['start_line'])
        
        # 3. Retrieve Context from Vector DB
        context = retriever.retrieve(expanded_code)
        
        # 4. Generate Review
        result = generate_review(hunk, expanded_code, context)
        print(f"\n--- AI RESULT ---\n{result}\n-----------------\n")
        
        # 5. Post to GitHub if an issue was found
        if result['status'] == 'success':
            review_data = result['review']
            if review_data.get('explanation') and review_data.get('cited_chunk_ids'):
                # Format a nice markdown comment
                citations = ", ".join(review_data['cited_chunk_ids'])
                body = (
                    f"🤖 **RAG Code Reviewer**\n\n"
                    f"**Category:** {review_data['category'].capitalize()} | **Severity:** {review_data['severity'].capitalize()}\n\n"
                    f"{review_data['explanation']}\n\n"
                    f"**Suggested Fix:**\n```python\n{review_data['suggested_fix']}\n```\n\n"
                    f"*(📚 Grounded in context: `{citations}`)*"
                )
                
                # --- NEW: Save to Database ---
                db = SessionLocal()
                new_log = ReviewLog(
                    repo=repo_name,
                    pr_number=pr_number,
                    file_path=hunk['file'],
                    line_number=hunk['start_line'],
                    category=review_data['category'],
                    severity=review_data['severity'],
                    comment=review_data['explanation'],
                    cited_chunks=review_data['cited_chunk_ids']
                )
                db.add(new_log)
                db.commit()
                db.close()
                # -----------------------------
                
                github_manager.post_inline_comment(
                    repo_full_name=repo_name,
                    pr_number=pr_number,
                    commit_id=commit_id,
                    file_path=hunk['file'],
                    line=hunk['start_line'],
                    body=body
                )

@router.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """Receive webhook events from GitHub."""
    payload = await request.json()
    
    # We only care about Pull Requests being opened or synchronized (updated)
    if "pull_request" in payload:
        action = payload.get("action")
        if action in ["opened", "synchronize"]:
            repo_name = payload["repository"]["full_name"]
            pr_number = payload["pull_request"]["number"]
            
            # Get the latest commit SHA
            commit_id = payload["pull_request"]["head"]["sha"]
            
            # Run the heavy RAG processing in the background so GitHub gets a fast 200 OK
            background_tasks.add_task(process_pr_review, repo_name, pr_number, commit_id)
            
            return {"status": "processing", "pr": pr_number}
            
    return {"status": "ignored"}
