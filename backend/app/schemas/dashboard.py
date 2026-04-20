from datetime import datetime

from pydantic import BaseModel, HttpUrl


class RepositoryCard(BaseModel):
    id: int
    name: str
    full_name: str
    url: HttpUrl
    description: str | None
    owner: str
    language: str | None
    stars: int
    forks: int
    watchers: int
    open_issues: int
    default_branch: str
    health_score: int
    last_activity_at: datetime | None
    updated_at: datetime
    archived: bool


class IssueItem(BaseModel):
    id: int
    repo: str
    number: int
    title: str
    state: str
    url: HttpUrl
    labels: list[str]
    author: str | None
    age_days: int
    updated_at: datetime
    priority: str


class ContributorCard(BaseModel):
    login: str
    avatar_url: HttpUrl | None
    profile_url: HttpUrl | None
    total_contributions: int
    repositories: list[str]
    rank: int


class ActivityItem(BaseModel):
    id: str
    repo: str
    actor: str
    event_type: str
    label: str
    created_at: datetime


class LabelBreakdown(BaseModel):
    label: str
    count: int


class DashboardSummary(BaseModel):
    repository_count: int
    total_stars: int
    total_forks: int
    total_watchers: int
    open_issues: int
    closed_issues: int
    active_contributors: int
    top_language: str | None
    last_refreshed_at: datetime
    warnings: list[str] = []


class DashboardPayload(BaseModel):
    summary: DashboardSummary
    repos: list[RepositoryCard]
    issues: list[IssueItem]
    contributors: list[ContributorCard]
    activity: list[ActivityItem]
    labels: list[LabelBreakdown]
