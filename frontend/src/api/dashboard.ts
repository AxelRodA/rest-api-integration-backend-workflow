import type {
  ActivityItem,
  ContributorCard,
  DashboardData,
  DashboardSummary,
  IssueItem,
  RepositoryCard
} from "../types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(path, API_BASE_URL);
  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (value) url.searchParams.set(key, value);
  });

  const response = await fetch(url);
  if (!response.ok) {
    let message = "The dashboard API is unavailable.";
    try {
      const body = await response.json();
      message = body?.error?.message ?? body?.detail ?? message;
    } catch {
      message = `${message} Status ${response.status}.`;
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export async function fetchDashboardData(search: string): Promise<DashboardData> {
  const params = search ? { search } : undefined;
  const [summary, repos, issues, contributors, activity] = await Promise.all([
    request<DashboardSummary>("/api/dashboard/summary"),
    request<RepositoryCard[]>("/api/dashboard/repos", params),
    request<IssueItem[]>("/api/dashboard/issues", params),
    request<ContributorCard[]>("/api/dashboard/contributors"),
    request<ActivityItem[]>("/api/dashboard/activity")
  ]);

  return { summary, repos, issues, contributors, activity };
}
