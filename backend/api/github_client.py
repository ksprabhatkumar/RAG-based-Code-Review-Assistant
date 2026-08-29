import os
from github import Github
from github.PullRequest import PullRequest

class GitHubManager:
    def __init__(self):
        # Uses the Fine-Grained PAT we discussed earlier
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable is missing")
        self.client = Github(token)

    def get_pr_diff(self, repo_full_name: str, pr_number: int) -> str:
        """Fetch the raw diff string for a given Pull Request."""
        repo = self.client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        
        # GitHub's API requires us to request a specific media type to get the diff
        headers = {"Accept": "application/vnd.github.v3.diff"}
        _, data = pr._requester.requestJsonAndCheck("GET", pr.url, headers=headers)
        
        # PyGithub hack to get the raw diff string from the response
        diff_text = data.get("data", "") if isinstance(data, dict) else str(data)
        return diff_text

    def get_file_content(self, repo_full_name: str, commit_id: str, file_path: str) -> str:
        """Fetch the raw source code of a file at a specific commit."""
        repo = self.client.get_repo(repo_full_name)
        try:
            file_content = repo.get_contents(file_path, ref=commit_id)
            return file_content.decoded_content.decode("utf-8")
        except Exception as e:
            print(f"Error fetching file {file_path}: {e}")
            return ""

    def post_inline_comment(self, repo_full_name: str, pr_number: int, commit_id: str, file_path: str, line: int, body: str):
        """Post a comment on a specific line of code in the PR."""
        repo = self.client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        
        pr.create_review_comment(
            body=body,
            commit=repo.get_commit(commit_id),
            path=file_path,
            line=line
        )
