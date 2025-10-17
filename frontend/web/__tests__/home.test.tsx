import React from "react";
import { render, screen } from "@testing-library/react";
import * as Stats from "@/lib/stats";
import HomePage from "@/app/page";

describe("HomePage", () => {
  it("renders dashboard sections with mocked data", async () => {
    const mock: Stats.DashboardStats = {
      period: "day",
      summary: { total_dialogs: 10, active_users: 3, avg_dialog_length: 5 },
      activity: [
        { ts: new Date().toISOString(), dialogs: 2, messages: 5 },
        { ts: new Date().toISOString(), dialogs: 3, messages: 7 },
      ],
      recent_dialogs: [
        {
          dialog_id: "d1",
          user_id: "u1",
          started_at: new Date().toISOString(),
          duration_sec: 120,
          num_messages: 6,
          status: "ok",
        },
      ],
      top_users: [
        { user_id: "u1", dialogs_count: 5, messages_count: 20, last_active_at: new Date().toISOString() },
      ],
    };

    vi.spyOn(Stats, "getStats").mockResolvedValue(mock);

    // @ts-expect-error - async server component default export
    render(await HomePage({ searchParams: { period: "day" } }));

    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/Total dialogs/i)).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText(/Top users/i)).toBeInTheDocument();
    expect(screen.getByText(/Recent dialogs/i)).toBeInTheDocument();
  });
});




