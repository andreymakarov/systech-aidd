export type Period = "day" | "week" | "month";

export interface SummaryStats {
  total_dialogs: number;
  active_users: number;
  avg_dialog_length: number;
}

export interface ActivityPoint {
  ts: string; // ISO string from API
  dialogs: number;
  messages: number;
}

export interface RecentDialog {
  dialog_id: string;
  user_id: string;
  started_at: string; // ISO string
  duration_sec: number;
  num_messages: number;
  status: string;
}

export interface TopUser {
  user_id: string;
  dialogs_count: number;
  messages_count: number;
  last_active_at: string; // ISO string
}

export interface DashboardStats {
  period: Period;
  summary: SummaryStats;
  activity: ActivityPoint[];
  recent_dialogs: RecentDialog[];
  top_users: TopUser[];
}

// Use internal URL for server-side requests, public URL for client-side
const getApiBaseUrl = (): string => {
  // Server-side: use internal Docker service name
  if (typeof window === 'undefined') {
    return process.env["STATS_API_URL_INTERNAL"] ?? "http://backend:8000/api/v1";
  }
  // Client-side: use public URL
  return process.env["NEXT_PUBLIC_STATS_API_URL"] ?? "http://localhost:8000/api/v1";
};

export const API_BASE_URL: string = getApiBaseUrl();

export async function getStats(period: Period): Promise<DashboardStats> {
  const url = `${getApiBaseUrl()}/stats?period=${period}`;
  const res = await fetch(url, { next: { revalidate: 60 } });
  if (!res.ok) {
    throw new Error(`Failed to load stats (${res.status})`);
  }
  const data = (await res.json()) as DashboardStats;
  return data;
}

export function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}


