import { Card } from "@/components/ui/card";
import type { RecentDialog } from "@/lib/stats";
import { formatDuration } from "@/lib/stats";

interface RecentDialogsTableProps {
  items: RecentDialog[];
  className?: string;
}

export function RecentDialogsTable({ items, className }: RecentDialogsTableProps) {
  return (
    <Card className={className ? className + " p-4" : "p-4"}>
      <div className="mb-2 text-sm text-muted-foreground">Recent dialogs</div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-muted-foreground">
              <th className="py-2 pr-3">Dialog</th>
              <th className="py-2 pr-3">User</th>
              <th className="py-2 pr-3">Started</th>
              <th className="py-2 pr-3">Duration</th>
              <th className="py-2 pr-3">Messages</th>
              <th className="py-2 pr-0">Status</th>
            </tr>
          </thead>
          <tbody>
            {items.map((d) => (
              <tr key={d.dialog_id} className="border-t">
                <td className="py-2 pr-3 font-mono text-xs">{d.dialog_id}</td>
                <td className="py-2 pr-3">{d.user_id}</td>
                <td className="py-2 pr-3">{new Date(d.started_at).toLocaleString()}</td>
                <td className="py-2 pr-3">{formatDuration(d.duration_sec)}</td>
                <td className="py-2 pr-3">{d.num_messages}</td>
                <td className="py-2 pr-0">{d.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}


