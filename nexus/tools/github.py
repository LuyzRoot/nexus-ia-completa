import logging
import httpx

logger = logging.getLogger(__name__)

class GitHubTool:
    """GitHub API interactions"""
    
    def __init__(self, token: str = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {"Authorization": f"token {token}"} if token else {}
    
    async def get_repo(self, owner: str, repo: str) -> dict:
        """Get repository info"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}",
                    headers=self.headers
                )
                return response.json()
        except Exception as e:
            logger.error(f"GitHub error: {e}")
            return {"error": str(e)}
    
    async def create_issue(self, owner: str, repo: str, title: str, body: str) -> dict:
        """Create GitHub issue"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/repos/{owner}/{repo}/issues",
                    json={"title": title, "body": body},
                    headers=self.headers
                )
                return response.json()
        except Exception as e:
            logger.error(f"GitHub error: {e}")
            return {"error": str(e)}
