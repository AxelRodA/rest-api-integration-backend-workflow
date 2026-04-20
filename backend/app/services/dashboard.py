from __future__ import annotations

import asyncio
from collections import Counter, defaultdict
from datetime import UTC, datetime

from pydantic import ValidationError

from app.clients.github import GitHubAPIError, GitHubClient
from app.core.cache import TTLCache
from app.core.config import settings
from app.schemas.dashboard import (
    ActivityItem,
    ContributorCard,
    DashboardPayload,
    DashboardSummary,
    IssueItem,
    LabelBreakdown,
    RepositoryCard,
)
from app.schemas.github import (
    GitHubContributor,
    GitHubEvent,
    GitHubIssue,
    GitHubRepo,
)


dashboard_cache: TTLCache[DashboardPayload] = TTLCache()


class DashboardUnavailableError(Exception):
    pass


def normalize_repositories(raw_repositories: str | None = None) -> list[str]:
    source = raw_repositories.split(",") if raw_repositories else settings.default_repositories
    normalized = []
    for item in source:
        value = item.strip()
        if not value or "/" not in value:
            continue
        owner, repo = value.split("/", 1)
        if owner and repo:
            normalized.append(f"{owner}/{repo}")
    return list(dict.fromkeys(normalized))


async def get_dashboard_payload(raw_repositories: str | None = None) -> DashboardPayload:
    repositories = normalize_repositories(raw_repositories)
    if not repositories:
        raise DashboardUnavailableError("No valid repositories were configured.")

    cache_key = "dashboard:" + ",".join(repositories)
    cached = dashboard_cache.get(cache_key)
    if cached:
        return cached

    client = GitHubClient()
    try:
        payload = await _build_payload(client, repositories)
    except DashboardUnavailableError:
        stale = dashboard_cache.get_stale(cache_key)
        if stale:
            stale.summary.warnings.append(
                "Live GitHub data is temporarily unavailable. Showing the latest cached dashboard snapshot."
            )
            return stale
        raise
    finally:
        await client.close()

    dashboard_cache.set(
        cache_key,
        payload,
        ttl_seconds=settings.cache_ttl_seconds,
        stale_ttl_seconds=settings.stale_cache_ttl_seconds,
    )
    return payload


async def _build_payload(
    client: GitHubClient, repositories: list[str]
) -> DashboardPayload:
    results = await asyncio.gather(
        *[_fetch_repository_bundle(client, full_name) for full_name in repositories],
        return_exceptions=True,
    )

    bundles: list[dict[str, object]] = []
    warnings: list[str] = []
    for full_name, result in zip(repositories, results, strict=False):
        if isinstance(result, Exception):
            warnings.append(f"{full_name}: {result}")
        else:
            bundles.append(result)

    if not bundles:
        raise DashboardUnavailableError(
            "GitHub data could not be loaded for any configured repository."
        )

    repos = [_to_repository_card(bundle["repo"]) for bundle in bundles]
    issues = _to_issue_items(bundles)
    contributors = _to_contributor_cards(bundles)
    activity = _to_activity_items(bundles)
    labels = _to_label_breakdown(issues)

    summary = DashboardSummary(
        repository_count=len(repos),
        total_stars=sum(repo.stars for repo in repos),
        total_forks=sum(repo.forks for repo in repos),
        total_watchers=sum(repo.watchers for repo in repos),
        open_issues=sum(1 for issue in issues if issue.state == "open"),
        closed_issues=sum(1 for issue in issues if issue.state == "closed"),
        active_contributors=len(contributors),
        top_language=_top_language(repos),
        last_refreshed_at=datetime.now(UTC),
        warnings=warnings,
    )

    return DashboardPayload(
        summary=summary,
        repos=sorted(repos, key=lambda repo: repo.stars, reverse=True),
        issues=sorted(issues, key=lambda issue: issue.updated_at, reverse=True),
        contributors=contributors,
        activity=sorted(activity, key=lambda item: item.created_at, reverse=True),
        labels=labels,
    )


async def _fetch_repository_bundle(
    client: GitHubClient, full_name: str
) -> dict[str, object]:
    owner, repo = full_name.split("/", 1)
    repo_raw, issues_raw, contributors_raw, activity_raw = await asyncio.gather(
        client.get_repo(owner, repo),
        client.list_issues(owner, repo),
        client.list_contributors(owner, repo),
        client.list_activity(owner, repo),
    )

    try:
        repository = GitHubRepo.model_validate(repo_raw)
        issues = [
            GitHubIssue.model_validate(item)
            for item in issues_raw
            if "pull_request" not in item
        ]
        contributors = [
            GitHubContributor.model_validate(item) for item in contributors_raw
        ]
        activity = [GitHubEvent.model_validate(item) for item in activity_raw]
    except ValidationError as exc:
        raise GitHubAPIError(f"GitHub response shape changed for {full_name}.") from exc

    return {
        "repo": repository,
        "issues": issues,
        "contributors": contributors,
        "activity": activity,
    }


def _to_repository_card(repo: GitHubRepo) -> RepositoryCard:
    health_score = 100
    if repo.archived:
        health_score -= 45
    if repo.open_issues_count > 250:
        health_score -= 20
    if repo.pushed_at:
        days_since_push = (datetime.now(UTC) - repo.pushed_at).days
        if days_since_push > 90:
            health_score -= 15
        if days_since_push > 365:
            health_score -= 20

    return RepositoryCard(
        id=repo.id,
        name=repo.name,
        full_name=repo.full_name,
        url=repo.html_url,
        description=repo.description,
        owner=repo.owner.login,
        language=repo.language,
        stars=repo.stargazers_count,
        forks=repo.forks_count,
        watchers=repo.watchers_count,
        open_issues=repo.open_issues_count,
        default_branch=repo.default_branch,
        health_score=max(0, min(100, health_score)),
        last_activity_at=repo.pushed_at,
        updated_at=repo.updated_at,
        archived=repo.archived,
    )


def _to_issue_items(bundles: list[dict[str, object]]) -> list[IssueItem]:
    items: list[IssueItem] = []
    now = datetime.now(UTC)
    for bundle in bundles:
        repo = bundle["repo"]
        for issue in bundle["issues"]:
            assert isinstance(repo, GitHubRepo)
            assert isinstance(issue, GitHubIssue)
            age_days = max(0, (now - issue.created_at).days)
            label_names = [label.name for label in issue.labels]
            priority = "normal"
            if issue.state == "open" and age_days > 180:
                priority = "attention"
            if any(label.lower() in {"bug", "security", "regression"} for label in label_names):
                priority = "high"

            items.append(
                IssueItem(
                    id=issue.id,
                    repo=repo.full_name,
                    number=issue.number,
                    title=issue.title,
                    state=issue.state,
                    url=issue.html_url,
                    labels=label_names,
                    author=issue.user.login if issue.user else None,
                    age_days=age_days,
                    updated_at=issue.updated_at,
                    priority=priority,
                )
            )
    return items


def _to_contributor_cards(bundles: list[dict[str, object]]) -> list[ContributorCard]:
    contributions: dict[str, int] = defaultdict(int)
    repos_by_login: dict[str, set[str]] = defaultdict(set)
    profile_by_login: dict[str, tuple[object, object]] = {}

    for bundle in bundles:
        repo = bundle["repo"]
        assert isinstance(repo, GitHubRepo)
        for contributor in bundle["contributors"]:
            assert isinstance(contributor, GitHubContributor)
            contributions[contributor.login] += contributor.contributions
            repos_by_login[contributor.login].add(repo.full_name)
            profile_by_login[contributor.login] = (
                contributor.avatar_url,
                contributor.html_url,
            )

    ranked = sorted(contributions.items(), key=lambda item: item[1], reverse=True)[:12]
    return [
        ContributorCard(
            login=login,
            avatar_url=profile_by_login[login][0],
            profile_url=profile_by_login[login][1],
            total_contributions=count,
            repositories=sorted(repos_by_login[login]),
            rank=index + 1,
        )
        for index, (login, count) in enumerate(ranked)
    ]


def _to_activity_items(bundles: list[dict[str, object]]) -> list[ActivityItem]:
    labels = {
        "PushEvent": "Code pushed",
        "IssuesEvent": "Issue updated",
        "PullRequestEvent": "Pull request activity",
        "ReleaseEvent": "Release published",
        "WatchEvent": "Repository starred",
        "ForkEvent": "Repository forked",
    }
    items: list[ActivityItem] = []
    for bundle in bundles:
        repo = bundle["repo"]
        assert isinstance(repo, GitHubRepo)
        for event in bundle["activity"]:
            assert isinstance(event, GitHubEvent)
            items.append(
                ActivityItem(
                    id=event.id,
                    repo=repo.full_name,
                    actor=event.actor.login,
                    event_type=event.type,
                    label=labels.get(event.type, event.type.replace("Event", "")),
                    created_at=event.created_at,
                )
            )
    return items[:80]


def _to_label_breakdown(issues: list[IssueItem]) -> list[LabelBreakdown]:
    counter: Counter[str] = Counter()
    for issue in issues:
        for label in issue.labels:
            counter[label] += 1
    return [
        LabelBreakdown(label=label, count=count)
        for label, count in counter.most_common(12)
    ]


def _top_language(repos: list[RepositoryCard]) -> str | None:
    counter = Counter(repo.language for repo in repos if repo.language)
    if not counter:
        return None
    return counter.most_common(1)[0][0]
