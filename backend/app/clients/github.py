from __future__ import annotations

import asyncio
from typing import Any

import httpx

from app.core.config import settings


class GitHubAPIError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class GitHubClient:
    def __init__(self) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "repository-activity-dashboard",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"

        self._client = httpx.AsyncClient(
            base_url=settings.github_base_url,
            headers=headers,
            timeout=httpx.Timeout(settings.github_timeout_seconds),
            follow_redirects=True,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def get_repo(self, owner: str, repo: str) -> dict[str, Any]:
        return await self._request("GET", f"/repos/{owner}/{repo}")

    async def list_issues(
        self, owner: str, repo: str, state: str = "all", per_page: int = 60
    ) -> list[dict[str, Any]]:
        return await self._request(
            "GET",
            f"/repos/{owner}/{repo}/issues",
            params={"state": state, "per_page": per_page, "sort": "updated"},
        )

    async def list_contributors(
        self, owner: str, repo: str, per_page: int = 30
    ) -> list[dict[str, Any]]:
        return await self._request(
            "GET",
            f"/repos/{owner}/{repo}/contributors",
            params={"per_page": per_page},
        )

    async def list_activity(
        self, owner: str, repo: str, per_page: int = 40
    ) -> list[dict[str, Any]]:
        return await self._request(
            "GET",
            f"/repos/{owner}/{repo}/events",
            params={"per_page": per_page},
        )

    async def _request(
        self, method: str, path: str, params: dict[str, Any] | None = None
    ) -> Any:
        last_error: Exception | None = None

        for attempt in range(settings.github_retry_attempts + 1):
            try:
                response = await self._client.request(method, path, params=params)
                if response.status_code == 403:
                    remaining = response.headers.get("x-ratelimit-remaining")
                    if remaining == "0":
                        raise GitHubAPIError(
                            "GitHub API rate limit exceeded. Try again later or configure GITHUB_TOKEN.",
                            status_code=response.status_code,
                        )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if status_code < 500:
                    raise GitHubAPIError(
                        f"GitHub API returned {status_code} for {path}.",
                        status_code=status_code,
                    ) from exc
                last_error = exc
            except (httpx.TimeoutException, httpx.NetworkError, GitHubAPIError) as exc:
                last_error = exc

            if attempt < settings.github_retry_attempts:
                await asyncio.sleep(0.25 * (attempt + 1))

        raise GitHubAPIError(f"GitHub API request failed for {path}.") from last_error
