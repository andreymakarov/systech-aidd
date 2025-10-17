import { Card } from "@/components/ui/card";
import type { TopUser } from "@/lib/stats";

interface TopUsersTableProps {
  items: TopUser[];
  className?: string;
}

export function TopUsersTable({ items, className }: TopUsersTableProps) {
  return (
    <Card className={className ? className + " p-4" : "p-4"}>
      <div className="mb-2 text-sm text-muted-foreground">Top users</div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-muted-foreground">
              <th className="py-2 pr-3">User</th>
              <th className="py-2 pr-3">Dialogs</th>
              <th className="py-2 pr-3">Messages</th>
              <th className="py-2 pr-0">Last active</th>
            </tr>
          </thead>
          <tbody>
            {items.map((u) => (
              <tr key={u.user_id} className="border-t">
                <td className="py-2 pr-3">{u.user_id}</td>
                <td className="py-2 pr-3">{u.dialogs_count}</td>
                <td className="py-2 pr-3">{u.messages_count}</td>
                <td className="py-2 pr-0">{new Date(u.last_active_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}



