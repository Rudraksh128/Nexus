"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type NavItem = {
  label: string;
  href: string;
};

const primaryItems: NavItem[] = [
  {
    label: "Dashboard",
    href: "/dashboard",
  },
  {
    label: "Workspaces",
    href: "/workspaces",
  },
  {
    label: "Documents",
    href: "/documents",
  },
  {
    label: "Upload",
    href: "/upload",
  },
];

const intelligenceItems: NavItem[] = [
  {
    label: "Universal Search",
    href: "/search",
  },
  {
    label: "AI Research",
    href: "/research",
  },
  {
    label: "Evidence",
    href: "/evidence",
  },
  {
    label: "Knowledge Graph",
    href: "/knowledge",
  },
  {
    label: "Timeline",
    href: "/timeline",
  },
  {
    label: "Contradictions",
    href: "/contradictions",
  },
  {
    label: "Decisions",
    href: "/decisions",
  },
  {
    label: "Research Reports",
    href: "/reports",
  },
  {
    label: "Analytics",
    href: "/analytics",
  },
];

function NavSection({
  title,
  items,
  pathname,
}: {
  title: string;
  items: NavItem[];
  pathname: string;
}) {
  return (
    <div className="space-y-2">
      <p className="px-3 text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--muted-2)]">
        {title}
      </p>

      <div className="space-y-1">
        {items.map((item) => {
          const active =
            pathname === item.href ||
            pathname.startsWith(`${item.href}/`);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={[
                "group flex items-center gap-3 rounded-xl px-3 py-2.5",
                "text-sm transition-all duration-200",
                active
                  ? "border border-[var(--accent)]/10 bg-[var(--accent-soft)] text-[var(--accent)] shadow-[inset_2px_0_0_var(--accent)]"
                  : "border border-transparent text-[var(--muted)] hover:bg-white/[0.035] hover:text-white",
              ].join(" ")}
            >
              <span
                className={[
                  "flex h-5 w-5 items-center justify-center text-base",
                  active
                    ? "text-[var(--accent)]"
                    : "text-[var(--muted-2)] group-hover:text-white",
                ].join(" ")}
              >
              </span>

              <span className="truncate">{item.label}</span>

              {item.label === "Contradictions" && (
                <span
                  className={[
                    "ml-auto rounded-full border px-1.5 py-0.5 text-[9px]",
                    active
                      ? "border-[var(--accent)]/20 text-[var(--accent)]"
                      : "border-[var(--border)] text-[var(--muted-2)]",
                  ].join(" ")}
                >
                  0
                </span>
              )}
            </Link>
          );
        })}
      </div>
    </div>
  );
}

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="nexus-scrollbar sticky top-0 flex h-screen w-[250px] shrink-0 flex-col overflow-y-auto border-r border-[var(--border)] bg-[rgba(8,10,15,0.9)] px-4 py-5 backdrop-blur-xl">
      <Link
        href="/dashboard"
        className="mb-8 flex items-center gap-3 px-2"
      >
        <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--accent)]/30 bg-[var(--accent-soft)] text-sm font-bold text-[var(--accent)] shadow-[0_0_25px_rgba(114,242,193,0.06)]">
          N
        </div>

        <div>
          <div className="text-sm font-semibold tracking-[0.18em]">
            NEXUS
          </div>

          <div className="text-[10px] text-[var(--muted-2)]">
            DECISION INTELLIGENCE
          </div>
        </div>
      </Link>

      <div className="space-y-7">
        <NavSection
          title="Workspace"
          items={primaryItems}
          pathname={pathname}
        />

        <NavSection
          title="Intelligence"
          items={intelligenceItems}
          pathname={pathname}
        />
      </div>

      <div className="mt-auto pt-8">
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-3 shadow-[0_10px_40px_rgba(0,0,0,0.15)]">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-xs text-[var(--muted)]">
              Local AI
            </span>

            <span className="flex items-center gap-1.5 text-[10px] font-medium text-[var(--accent)]">
              <span className="h-1.5 w-1.5 rounded-full bg-[var(--accent)] shadow-[0_0_8px_var(--accent)]" />
              ONLINE
            </span>
          </div>

          <p className="text-[11px] text-[var(--muted-2)]">
            Qwen3 Â· Ollama
          </p>
        </div>
      </div>
    </aside>
  );
}


