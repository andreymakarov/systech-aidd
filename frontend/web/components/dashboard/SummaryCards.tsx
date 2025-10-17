import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface SummaryCardsProps {
  totalDialogs: number;
  activeUsers: number;
  avgDialogLength: number; // minutes or seconds as provided
  className?: string;
}

export function SummaryCards({
  totalDialogs,
  activeUsers,
  avgDialogLength,
  className,
}: SummaryCardsProps) {
  return (
    <div className={cn("grid gap-4 sm:grid-cols-2 lg:grid-cols-3", className)}>
      <Card className="p-4">
        <div className="text-sm text-muted-foreground">Total dialogs</div>
        <div className="mt-1 text-2xl font-semibold">{totalDialogs}</div>
      </Card>
      <Card className="p-4">
        <div className="text-sm text-muted-foreground">Active users</div>
        <div className="mt-1 text-2xl font-semibold">{activeUsers}</div>
      </Card>
      <Card className="p-4">
        <div className="text-sm text-muted-foreground">Avg dialog length</div>
        <div className="mt-1 text-2xl font-semibold">{avgDialogLength}</div>
      </Card>
    </div>
  );
}



