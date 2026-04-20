export interface DashboardSummary {
  repository_count: number;
  total_stars: number;
  total_forks: number;
  total_watchers: number;
  open_issues: number;
  closed_issues: number;
  active_contributors: number;
  top_language: string | null;
  last_refreshed_at: string;
  warnings: string[];
}

export interface RepositoryCard {
  id: number;
  name: string;
  full_name: string;
  url: string;
  description: string | null;
  owner: string;
  language: string | null;
  stars: number;
  forks: number;
  watchers: number;
  open_issues: number;
  default_branch: string;
  health_score: number;
  last_activity_at: string | null;
  updated_at: string;
  archived: boolean;
}

export interface IssueItem {
  id: number;
  repo: string;
  number: number;
  title: string;
  state: "open" | "closed";
  url: string;
  labels: string[];
  author: string | null;
  age_days: number;
  updated_at: string;
  priority: "normal" | "attention" | "high";
}

export interface ContributorCard {
  login: string;
  avatar_url: string | null;
  profile_url: string | null;
  total_contributions: number;
  repositories: string[];
  rank: number;
}

export interface ActivityItem {
  id: string;
  repo: string;
  actor: string;
  event_type: string;
  label: string;
  created_at: string;
}

export interface DashboardData {
  summary: DashboardSummary;
  repos: RepositoryCard[];
  issues: IssueItem[];
  contributors: ContributorCard[];
  activity: ActivityItem[];
}
