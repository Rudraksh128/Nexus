"use client";

import Sidebar from "@/components/layout/Sidebar";

export default function AppShell({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <div className="flex min-h-screen">
        <Sidebar />

        <div className="min-w-0 flex-1">
          <header className="sticky top-0 z-30 border-b border-[var(--border)] bg-[rgba(8,10,15,0.82)] px-6 py-4 backdrop-blur-xl">
            <div className="flex items-center justify-between gap-4">
              <div>
                <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--muted-2)]">
                  Workspace
                </div>

                <div className="mt-1 text-sm font-medium">
                  NEXUS Test Workspace
                </div>
              </div>

              <div className="flex items-center gap-2 rounded-full border border-[var(--accent)]/20 bg-[var(--accent-soft)] px-3 py-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-[var(--accent)] shadow-[0_0_10px_var(--accent)]" />
                <span className="text-[10px] font-semibold tracking-[0.12em] text-[var(--accent)]">
                  SYSTEM ONLINE
                </span>
              </div>
            </div>
          </header>

          <main>{children}</main>
        </div>
      </div>
    </div>
  );
}
