"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return null;
  const next = theme === "dark" ? "light" : "dark";
  return (
    <Button variant="outline" onClick={() => setTheme(next)}>
      Toggle {next}
    </Button>
  );
}




