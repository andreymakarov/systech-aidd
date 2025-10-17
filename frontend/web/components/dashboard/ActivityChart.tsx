"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "@/components/ui/card";
import type { ActivityPoint } from "@/lib/stats";

interface ActivityChartProps {
  data: ActivityPoint[];
  className?: string;
}

export function ActivityChart({ data, className }: ActivityChartProps) {
  return (
    <Card className={className ? className + " p-4" : "p-4"}>
      <div className="mb-2 text-sm text-muted-foreground">Activity</div>
      <div className="h-64 w-full">
        <ResponsiveContainer>
          <AreaChart data={data} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
            <defs>
              <linearGradient id="dialogs" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="messages" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22c55e" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="ts" tick={{ fontSize: 12 }} hide={data.length > 30} />
            <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
            <Tooltip labelFormatter={(v) => new Date(v as string).toLocaleString()} />
            <Legend />
            <Area type="monotone" dataKey="dialogs" name="Dialogs" stroke="#6366f1" fill="url(#dialogs)" />
            <Area type="monotone" dataKey="messages" name="Messages" stroke="#22c55e" fill="url(#messages)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}


