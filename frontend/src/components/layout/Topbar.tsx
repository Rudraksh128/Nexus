"use client";

import { useState } from "react";

export default function Topbar() {
  const [workspaceOpen, setWorkspaceOpen] =
    useState(false);

  return (
    <header className="flex h-[72px] items-center justify-between border-b border-[var(--border)] bg-[rgba(8,10,15,0.7)] px-7 backdrop-blur-xl">
      <div>
        <div className="text-sm font-medium">
          Intelligence Workspace
        </div>

        <div className="mt-0.5 text-xs text-[var(--muted-2)]">
          Analyze what changed. Understand what matters.
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative">
          <button
            type="button"
            onClick={() =>
              setWorkspaceOpen((value) => !value)
            }
            className="flex items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--panel)] px-3 py-2 text-xs text-[var(--muted)] transition hover:border-[#2b3747] hover:text-white"
          >
            <span className="h-2 w-2 rounded-full bg-[var(--accent)]" />
            Default Workspace
            <span className="text-[var(--muted-2)]">
              ▾
            </span>
          </button>

          {workspaceOpen && (
            <div className="absolute right-0 top-12 z-50 w-52 rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-2 shadow-2xl">
              <div className="rounded-lg bg-white/[0.03] px-3 py-2 text-xs text-white">
                Default Workspace
              </div>
            </div>
          )}
        </div>

        <button
          type="button"
          aria-label="Settings"
          className="flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--panel)] text-sm text-[var(--muted)] hover:text-white"
        >
          ⚙
        </button>

        <div
          aria-label="User profile"
          className="flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--panel)] text-xs font-semibold"
        >
          R
        </div>
      </div>
    </header>
  );
}