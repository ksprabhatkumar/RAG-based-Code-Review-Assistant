import os
import httpx
from github import Github

def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Missing GITHUB_TOKEN")
        return

    g = Github(token)
    repo = g.get_repo("ksprabhatkumar/rag-reviewer-demo")
    
    print("Creating Pull Request...")
    # Get default branch to merge into
    base_branch = repo.default_branch
    
    try:
        pr = repo.create_pull(
            title="Test RAG Webhook",
            body="Triggering the magical local webhook test without ngrok!",
            head="test-webhook-2",
            base=base_branch
        )
        print(f"✅ Created PR #{pr.number}")
    except Exception as e:
        print(f"Failed to create PR (maybe it already exists?): {e}")
        # If it fails, let's just fetch the existing PR
        pulls = repo.get_pulls(state='open', head='ksprabhatkumar:test-webhook-2')
        if pulls.totalCount > 0:
            pr = pulls[0]
            print(f"Using existing PR #{pr.number}")
        else:
            return

    commit_sha = pr.head.sha
    print(f"Commit SHA: {commit_sha}")
    
    # 2. Trigger the local webhook!
    payload = {
        "action": "opened",
        "pull_request": {
            "number": pr.number,
            "head": {"sha": commit_sha}
        },
        "repository": {
            "full_name": "ksprabhatkumar/rag-reviewer-demo"
        }
    }
    
    print("Firing local Webhook to http://127.0.0.1:8000/webhook ...")
    response = httpx.post("http://127.0.0.1:8000/webhook", json=payload)
    print(f"Webhook Response [{response.status_code}]: {response.json()}")

if __name__ == "__main__":
    main()
