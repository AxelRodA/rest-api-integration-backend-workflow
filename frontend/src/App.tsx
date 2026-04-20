import {
  Activity,
  AlertTriangle,
  Code2,
  ExternalLink,
  GitFork,
  RefreshCw,
  Search,
  Star,
  Users
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { fetchDashboardData } from "./api/dashboard";
import type {
  ActivityItem,
  ContributorCard,
  DashboardData,
  IssueItem,
  RepositoryCard
} from "./types";

const numberFormat = new Intl.NumberFormat("en", { notation: "compact" });
const dateFormat = new Intl.DateTimeFormat("en", {
  month: "short",
  day: "numeric",
  hour: "numeric",
  minute: "2-digit"
});

function App() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [search, setSearch] = useState("");
  const [issueState, setIssueState] = useState<"all" | "open" | "closed">("all");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadDashboard(nextSearch = search) {
    setIsLoading(true);
    setError(null);
    try {
      setData(await fetchDashboardData(nextSearch.trim()));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected dashboard error.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard("");
  }, []);

  const filteredIssues = useMemo(() => {
    if (!data) return [];
    if (issueState === "all") return data.issues;
    return data.issues.filter((issue) => issue.state === issueState);
  }, [data, issueState]);

  return (
    <main className="min-h-screen px-4 py-6 text-slate-100 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <header className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-mint/30 bg-mint/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-mint">
              <Activity size={14} />
              Backend workflow monitor
            </div>
            <h1 className="text-3xl font-bold tracking-normal text-white sm:text-5xl">
              REST API Integration and Backend Workflow
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300">
              A repository activity dashboard that turns public GitHub API
              responses into client-ready metrics, normalized records, and
              operational views.
            </p>
          </div>

          <div className="dashboard-card flex flex-col gap-3 p-3 sm:min-w-[360px]">
            <div className="flex items-center gap-2 rounded-md border border-line bg-ink/70 px-3 py-2">
              <Search className="h-4 w-4 text-slate-400" />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") loadDashboard();
                }}
                placeholder="Search repositories or issues"
                className="w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-500"
              />
            </div>
            <button
              onClick={() => loadDashboard()}
              className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-mint px-4 text-sm font-bold text-ink transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={isLoading}
            >
              <RefreshCw size={16} className={isLoading ? "animate-spin" : ""} />
              Refresh data
            </button>
          </div>
        </header>

        {error && <ErrorBanner message={error} onRetry={() => loadDashboard()} />}
        {data?.summary.warnings.map((warning) => (
          <WarningBanner key={warning} message={warning} />
        ))}

        {isLoading && !data ? (
          <LoadingState />
        ) : data ? (
          <>
            <SummaryGrid data={data} />

            <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
              <RepositoryTable repos={data.repos} />
              <ContributorLeaderboard contributors={data.contributors} />
            </section>

            <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
              <IssuesPanel
                issues={filteredIssues}
                state={issueState}
                onStateChange={setIssueState}
              />
              <ActivityFeed activity={data.activity} />
            </section>
          </>
        ) : null}
      </div>
    </main>
  );
}

function SummaryGrid({ data }: { data: DashboardData }) {
  const metrics = [
    {
      label: "Repositories",
      value: data.summary.repository_count,
      icon: Code2,
      accent: "text-mint"
    },
    {
      label: "Stars",
      value: data.summary.total_stars,
      icon: Star,
      accent: "text-amber"
    },
    {
      label: "Forks",
      value: data.summary.total_forks,
      icon: GitFork,
      accent: "text-sky-300"
    },
    {
      label: "Open issues",
      value: data.summary.open_issues,
      icon: AlertTriangle,
      accent: "text-coral"
    },
    {
      label: "Contributors",
      value: data.summary.active_contributors,
      icon: Users,
      accent: "text-violet-300"
    }
  ];

  return (
    <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
      {metrics.map((metric) => {
        const Icon = metric.icon;
        return (
          <article key={metric.label} className="dashboard-card p-5">
            <div className="flex items-center justify-between">
              <span className="metric-label">{metric.label}</span>
              <Icon className={`h-5 w-5 ${metric.accent}`} />
            </div>
            <div className="metric-value">{numberFormat.format(metric.value)}</div>
          </article>
        );
      })}
    </section>
  );
}

function RepositoryTable({ repos }: { repos: RepositoryCard[] }) {
  return (
    <section className="dashboard-card overflow-hidden">
      <PanelHeader title="Repository Portfolio" subtitle="Normalized GitHub repository records" />
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="border-y border-line bg-ink/60 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th className="px-5 py-3">Repository</th>
              <th className="px-5 py-3">Language</th>
              <th className="px-5 py-3">Stars</th>
              <th className="px-5 py-3">Issues</th>
              <th className="px-5 py-3">Health</th>
              <th className="px-5 py-3">Updated</th>
            </tr>
          </thead>
          <tbody>
            {repos.map((repo) => (
              <tr key={repo.id} className="border-b border-line/70 last:border-0">
                <td className="px-5 py-4">
                  <a
                    href={repo.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 font-semibold text-white hover:text-mint"
                  >
                    {repo.full_name}
                    <ExternalLink size={14} />
                  </a>
                  <p className="mt-1 max-w-md truncate text-slate-400">
                    {repo.description ?? "No description provided"}
                  </p>
                </td>
                <td className="px-5 py-4 text-slate-300">{repo.language ?? "Mixed"}</td>
                <td className="px-5 py-4 text-slate-300">{numberFormat.format(repo.stars)}</td>
                <td className="px-5 py-4 text-slate-300">{repo.open_issues}</td>
                <td className="px-5 py-4">
                  <HealthScore score={repo.health_score} />
                </td>
                <td className="px-5 py-4 text-slate-400">
                  {dateFormat.format(new Date(repo.updated_at))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {repos.length === 0 && <EmptyState label="No repositories match the current search." />}
    </section>
  );
}

function ContributorLeaderboard({ contributors }: { contributors: ContributorCard[] }) {
  return (
    <section className="dashboard-card">
      <PanelHeader title="Contributor Leaderboard" subtitle="Aggregated across tracked repositories" />
      <div className="divide-y divide-line/70">
        {contributors.map((contributor) => (
          <a
            key={contributor.login}
            href={contributor.profile_url ?? "#"}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-4 px-5 py-4 transition hover:bg-white/5"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-md border border-line bg-ink text-sm font-bold text-mint">
              {contributor.rank}
            </div>
            {contributor.avatar_url ? (
              <img
                src={contributor.avatar_url}
                alt=""
                className="h-10 w-10 rounded-md border border-line"
              />
            ) : (
              <div className="h-10 w-10 rounded-md border border-line bg-ink" />
            )}
            <div className="min-w-0 flex-1">
              <p className="truncate font-semibold text-white">{contributor.login}</p>
              <p className="truncate text-xs text-slate-400">
                {contributor.repositories.length} tracked repositories
              </p>
            </div>
            <div className="text-right">
              <p className="font-bold text-white">
                {numberFormat.format(contributor.total_contributions)}
              </p>
              <p className="text-xs text-slate-500">commits</p>
            </div>
          </a>
        ))}
      </div>
      {contributors.length === 0 && <EmptyState label="Contributor data is not available." />}
    </section>
  );
}

function IssuesPanel({
  issues,
  state,
  onStateChange
}: {
  issues: IssueItem[];
  state: "all" | "open" | "closed";
  onStateChange: (state: "all" | "open" | "closed") => void;
}) {
  return (
    <section className="dashboard-card">
      <div className="flex flex-col gap-4 border-b border-line p-5 sm:flex-row sm:items-center sm:justify-between">
        <PanelTitle title="Issue Workflow" subtitle="Filtered, prioritized issue queue" />
        <div className="grid grid-cols-3 rounded-md border border-line bg-ink p-1 text-sm">
          {(["all", "open", "closed"] as const).map((item) => (
            <button
              key={item}
              onClick={() => onStateChange(item)}
              className={`rounded px-3 py-1.5 font-semibold capitalize transition ${
                state === item ? "bg-mint text-ink" : "text-slate-400 hover:text-white"
              }`}
            >
              {item}
            </button>
          ))}
        </div>
      </div>
      <div className="divide-y divide-line/70">
        {issues.map((issue) => (
          <a
            key={issue.id}
            href={issue.url}
            target="_blank"
            rel="noreferrer"
            className="block px-5 py-4 transition hover:bg-white/5"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0">
                <p className="line-clamp-2 font-semibold text-white">{issue.title}</p>
                <p className="mt-1 text-xs text-slate-400">
                  {issue.repo} #{issue.number} · {issue.age_days} days old
                </p>
              </div>
              <PriorityBadge priority={issue.priority} />
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {issue.labels.slice(0, 4).map((label) => (
                <span
                  key={label}
                  className="rounded border border-line bg-ink px-2 py-1 text-xs text-slate-300"
                >
                  {label}
                </span>
              ))}
            </div>
          </a>
        ))}
      </div>
      {issues.length === 0 && <EmptyState label="No issues match this view." />}
    </section>
  );
}

function ActivityFeed({ activity }: { activity: ActivityItem[] }) {
  return (
    <section className="dashboard-card">
      <PanelHeader title="Recent Activity" subtitle="Business-friendly event labels" />
      <div className="divide-y divide-line/70">
        {activity.map((item) => (
          <div key={item.id} className="px-5 py-4">
            <div className="flex items-start gap-3">
              <span className="mt-1 h-2.5 w-2.5 rounded-full bg-mint" />
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-white">{item.label}</p>
                <p className="mt-1 truncate text-sm text-slate-400">
                  {item.actor} in {item.repo}
                </p>
              </div>
              <time className="whitespace-nowrap text-xs text-slate-500">
                {dateFormat.format(new Date(item.created_at))}
              </time>
            </div>
          </div>
        ))}
      </div>
      {activity.length === 0 && <EmptyState label="No recent activity returned by GitHub." />}
    </section>
  );
}

function PanelHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="border-b border-line p-5">
      <PanelTitle title={title} subtitle={subtitle} />
    </div>
  );
}

function PanelTitle({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div>
      <h2 className="text-lg font-bold text-white">{title}</h2>
      <p className="mt-1 text-sm text-slate-400">{subtitle}</p>
    </div>
  );
}

function HealthScore({ score }: { score: number }) {
  const color =
    score >= 80 ? "bg-mint" : score >= 55 ? "bg-amber" : "bg-coral";
  return (
    <div className="flex items-center gap-3">
      <div className="h-2 w-24 overflow-hidden rounded-full bg-ink">
        <div className={`h-full ${color}`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-sm font-semibold text-white">{score}</span>
    </div>
  );
}

function PriorityBadge({ priority }: { priority: IssueItem["priority"] }) {
  const styles = {
    normal: "border-slate-500/40 text-slate-300",
    attention: "border-amber/50 text-amber",
    high: "border-coral/50 text-coral"
  };
  return (
    <span className={`rounded border px-2 py-1 text-xs font-bold uppercase ${styles[priority]}`}>
      {priority}
    </span>
  );
}

function ErrorBanner({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="dashboard-card flex flex-col gap-3 border-coral/40 bg-coral/10 p-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-3">
        <AlertTriangle className="h-5 w-5 text-coral" />
        <p className="text-sm text-red-100">{message}</p>
      </div>
      <button
        onClick={onRetry}
        className="rounded-md border border-coral/50 px-3 py-2 text-sm font-semibold text-red-100 hover:bg-coral/20"
      >
        Retry
      </button>
    </div>
  );
}

function WarningBanner({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-amber/40 bg-amber/10 p-4 text-sm text-amber">
      {message}
    </div>
  );
}

function LoadingState() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: 8 }).map((_, index) => (
        <div key={index} className="dashboard-card h-36 animate-pulse bg-white/5" />
      ))}
    </div>
  );
}

function EmptyState({ label }: { label: string }) {
  return <div className="px-5 py-10 text-center text-sm text-slate-400">{label}</div>;
}

export default App;
