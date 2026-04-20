from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class GitHubOwner(BaseModel):
    model_config = ConfigDict(extra="ignore")

    login: str
    avatar_url: HttpUrl | None = None
    html_url: HttpUrl | None = None


class GitHubRepo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    full_name: str
    html_url: HttpUrl
    description: str | None = None
    stargazers_count: int = 0
    forks_count: int = 0
    watchers_count: int = 0
    open_issues_count: int = 0
    language: str | None = None
    default_branch: str
    archived: bool = False
    pushed_at: datetime | None = None
    updated_at: datetime
    owner: GitHubOwner


class GitHubLabel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    color: str | None = None


class GitHubIssue(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    number: int
    title: str
    state: str
    html_url: HttpUrl
    labels: list[GitHubLabel] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    user: GitHubOwner | None = None
    pull_request: dict[str, Any] | None = None


class GitHubContributor(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int | None = None
    login: str
    avatar_url: HttpUrl | None = None
    html_url: HttpUrl | None = None
    contributions: int = 0


class GitHubActor(BaseModel):
    model_config = ConfigDict(extra="ignore")

    login: str
    avatar_url: HttpUrl | None = None


class GitHubEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    type: str
    actor: GitHubActor
    created_at: datetime
