from fastapi import APIRouter, Query

from app.schemas.dashboard import (
    ActivityItem,
    ContributorCard,
    DashboardSummary,
    IssueItem,
    RepositoryCard,
)
from app.services.dashboard import get_dashboard_payload


router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(repositories: str | None = Query(default=None)):
    payload = await get_dashboard_payload(repositories)
    return payload.summary


@router.get("/repos", response_model=list[RepositoryCard])
async def dashboard_repos(
    repositories: str | None = Query(default=None),
    search: str | None = Query(default=None),
    language: str | None = Query(default=None),
):
    payload = await get_dashboard_payload(repositories)
    repos = payload.repos
    if search:
        term = search.lower()
        repos = [
            repo
            for repo in repos
            if term in repo.full_name.lower()
            or (repo.description and term in repo.description.lower())
        ]
    if language:
        repos = [
            repo
            for repo in repos
            if repo.language and repo.language.lower() == language.lower()
        ]
    return repos


@router.get("/issues", response_model=list[IssueItem])
async def dashboard_issues(
    repositories: str | None = Query(default=None),
    state: str | None = Query(default=None, pattern="^(open|closed)$"),
    priority: str | None = Query(default=None, pattern="^(normal|attention|high)$"),
    search: str | None = Query(default=None),
    limit: int = Query(default=30, ge=1, le=100),
):
    payload = await get_dashboard_payload(repositories)
    issues = payload.issues
    if state:
        issues = [issue for issue in issues if issue.state == state]
    if priority:
        issues = [issue for issue in issues if issue.priority == priority]
    if search:
        term = search.lower()
        issues = [
            issue
            for issue in issues
            if term in issue.title.lower() or term in issue.repo.lower()
        ]
    return issues[:limit]


@router.get("/contributors", response_model=list[ContributorCard])
async def dashboard_contributors(
    repositories: str | None = Query(default=None),
    limit: int = Query(default=12, ge=1, le=50),
):
    payload = await get_dashboard_payload(repositories)
    return payload.contributors[:limit]


@router.get("/activity", response_model=list[ActivityItem])
async def dashboard_activity(
    repositories: str | None = Query(default=None),
    repo: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    limit: int = Query(default=30, ge=1, le=100),
):
    payload = await get_dashboard_payload(repositories)
    activity = payload.activity
    if repo:
        activity = [item for item in activity if item.repo.lower() == repo.lower()]
    if event_type:
        activity = [
            item for item in activity if item.event_type.lower() == event_type.lower()
        ]
    return activity[:limit]
