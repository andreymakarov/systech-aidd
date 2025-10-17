"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";

const PERIODS: Array<{ key: "day" | "week" | "month"; label: string }> = [
  { key: "day", label: "Day" },
  { key: "week", label: "Week" },
  { key: "month", label: "Month" },
];

export function PeriodSwitcher() {
  const router = useRouter();
  const search = useSearchParams();
  const current = (search.get("period") as "day" | "week" | "month") ?? "day";

  function setPeriod(p: "day" | "week" | "month") {
    const params = new URLSearchParams(search.toString());
    params.set("period", p);
    router.push(`/?${params.toString()}`);
  }

  return (
    <div className="inline-flex gap-2" role="group" aria-label="Select period">
      {PERIODS.map((p) => (
        <Button
          key={p.key}
          variant={current === p.key ? "default" : "secondary"}
          onClick={() => setPeriod(p.key)}
          aria-pressed={current === p.key}
        >
          {p.label}
        </Button>
      ))}
    </div>
  );
}


