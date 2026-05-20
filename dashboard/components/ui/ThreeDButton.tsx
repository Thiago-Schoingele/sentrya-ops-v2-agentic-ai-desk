"use client";

import type { ButtonHTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

interface ThreeDButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: ReactNode;
  variant?: "default" | "critical" | "quiet";
}

export function ThreeDButton({ className, children, icon, variant = "default", ...props }: ThreeDButtonProps) {
  return (
    <button
      className={cn(
        "group inline-flex min-h-10 items-center justify-center gap-2 rounded-md border px-3.5 py-2 text-sm font-medium text-silver transition duration-200",
        "border-white/10 bg-gradient-to-b from-control2 to-control shadow-control",
        "hover:-translate-y-0.5 hover:border-accent/45 hover:from-[#4a586b] hover:to-[#303b4a]",
        "active:translate-y-0 active:shadow-press focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/45",
        variant === "critical" && "border-critical/35 from-[#514047] to-[#332831] text-[#f0d1d1] hover:border-critical/60",
        variant === "quiet" && "from-[#27313e] to-[#202936] text-muted",
        className
      )}
      {...props}
    >
      {icon ? <span className="text-accent transition group-hover:text-silver">{icon}</span> : null}
      {children}
    </button>
  );
}
