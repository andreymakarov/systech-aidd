import { ThemeToggle } from "@/components/theme-toggle";
import { SummaryCards } from "@/components/dashboard/SummaryCards";
import { ActivityChart } from "@/components/dashboard/ActivityChart";
import { RecentDialogsTable } from "@/components/dashboard/RecentDialogsTable";
import { TopUsersTable } from "@/components/dashboard/TopUsersTable";
import { PeriodSwitcher } from "@/components/dashboard/PeriodSwitcher";
import { getStats, type Period } from "@/lib/stats";

export default async function HomePage({
  searchParams,
}: {
  searchParams?: Record<string, string | string[] | undefined>;
}) {
  const period = (searchParams?.period as Period) ?? "day";
  let data;
  try {
    data = await getStats(period);
  } catch (e) {
    data = undefined;
  }

  return (
    <main className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <div className="flex items-center gap-3">
          <PeriodSwitcher />
          <ThemeToggle />
        </div>
      </div>

      {data ? (
        <>
          <SummaryCards
            totalDialogs={data.summary.total_dialogs}
            activeUsers={data.summary.active_users}
            avgDialogLength={data.summary.avg_dialog_length}
          />

          <div className="grid gap-4 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <ActivityChart data={data.activity} />
            </div>
            <TopUsersTable items={data.top_users} />
          </div>

          <RecentDialogsTable items={data.recent_dialogs} />
        </>
      ) : (
        <div className="text-sm text-red-500">Failed to load dashboard data.</div>
      )}
    </main>
  );
}




