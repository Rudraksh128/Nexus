import AppShell from "@/components/layout/AppShell";

export default function Page() {
  return (
    <AppShell>
      <div className="p-7">
        <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
          NEXUS
        </div>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight">
          Timeline
        </h1>
        <p className="mt-2 text-sm text-[var(--muted)]">
          This intelligence view is being connected to the live backend.
        </p>
      </div>
    </AppShell>
  );
}
