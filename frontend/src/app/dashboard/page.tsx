"use client";

import { useEffect, useState } from "react";

import MetricCard from "@/components/ui/MetricCard";
import SectionHeader from "@/components/ui/SectionHeader";
import { getWorkspaceAnalytics } from "@/lib/api";

const WORKSPACE_ID =
  "6314f325-3492-4273-b2a2-adaa9fb0e661";

export default function DashboardPage() {
  const [data, setData] =
    useState<Awaited<
      ReturnType<typeof getWorkspaceAnalytics>
    > | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    getWorkspaceAnalytics(WORKSPACE_ID)
      .then(setData)
      .catch((err: Error) =>
        setError(err.message),
      );
  }, []);

  return (
    <div className="nexus-grid min-h-full p-7">
      <div className="mx-auto max-w-[1500px] space-y-8">
        <section className="pt-2">
          <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
            Overview
          </div>

          <h1 className="mt-2 text-3xl font-semibold tracking-tight">
            Good to see you.
          </h1>

          <p className="mt-2 max-w-2xl text-sm text-[var(--muted)]">
            NEXUS turns documents and evidence into
            searchable knowledge, research, and
            decision intelligence.
          </p>
        </section>

        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
          <MetricCard
            label="Documents"
            value={data?.documents ?? "—"}
            detail="Source documents"
          />

          <MetricCard
            label="Claims"
            value={data?.claims ?? "—"}
            detail="Structured facts"
          />

          <MetricCard
            label="Evidence"
            value={data?.evidence ?? "—"}
            detail="Traceable support"
          />

          <MetricCard
            label="Entities"
            value={data?.entities ?? "—"}
            detail="Knowledge graph nodes"
          />

          <MetricCard
            label="Decisions"
            value={data?.decisions ?? "—"}
            detail="Tracked decisions"
          />
        </section>

        {error && (
          <div className="rounded-2xl border border-[var(--danger)]/20 bg-[var(--danger)]/5 p-4 text-sm text-[var(--danger)]">
            Backend connection failed: {error}
          </div>
        )}

        <section className="grid gap-5 lg:grid-cols-[1.35fr_0.65fr]">
          <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
            <SectionHeader
              eyebrow="Intelligence"
              title="Knowledge system"
              description="Current state of the workspace knowledge layer."
            />

            <div className="mt-7 grid grid-cols-2 gap-4 sm:grid-cols-4">
              {[
                ["Chunks", data?.chunks],
                ["Events", data?.events],
                ["Relations", data?.relationships],
                ["Assumptions", data?.assumptions],
              ].map(([label, value]) => (
                <div
                  key={String(label)}
                  className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-4"
                >
                  <div className="text-xs text-[var(--muted-2)]">
                    {label}
                  </div>
                  <div className="mt-2 text-xl font-semibold">
                    {value ?? "—"}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
            <SectionHeader
              eyebrow="System"
              title="Local intelligence"
              description="Your AI stack is running locally."
            />

            <div className="mt-7 space-y-3">
              <div className="flex items-center justify-between rounded-xl border border-[var(--border)] bg-[var(--panel-2)] px-4 py-3">
                <span className="text-sm">
                  Ollama
                </span>
                <span className="text-xs text-[var(--accent)]">
                  ONLINE
                </span>
              </div>

              <div className="flex items-center justify-between rounded-xl border border-[var(--border)] bg-[var(--panel-2)] px-4 py-3">
                <span className="text-sm">
                  Qwen3
                </span>
                <span className="text-xs text-[var(--muted)]">
                  1.7B
                </span>
              </div>

              <div className="flex items-center justify-between rounded-xl border border-[var(--border)] bg-[var(--panel-2)] px-4 py-3">
                <span className="text-sm">
                  PostgreSQL
                </span>
                <span className="text-xs text-[var(--accent)]">
                  CONNECTED
                </span>
              </div>
            </div>
          </div>
        </section>

        <section className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
          <SectionHeader
            eyebrow="Workflow"
            title="What do you want to investigate?"
            description="Jump directly into the intelligence workflow."
          />

          <div className="mt-6 grid gap-3 md:grid-cols-3">
            <a
              href="/research"
              className="rounded-2xl border border-[var(--border)] bg-[var(--panel-2)] p-5 transition hover:-translate-y-0.5 hover:border-[#2d3948]"
            >
              <div className="text-lg">✦</div>
              <div className="mt-3 text-sm font-semibold">
                Start AI Research
              </div>
              <p className="mt-1 text-xs leading-5 text-[var(--muted)]">
                Ask a question and let the research
                agent gather evidence.
              </p>
            </a>

            <a
              href="/search"
              className="rounded-2xl border border-[var(--border)] bg-[var(--panel-2)] p-5 transition hover:-translate-y-0.5 hover:border-[#2d3948]"
            >
              <div className="text-lg">⌕</div>
              <div className="mt-3 text-sm font-semibold">
                Search Knowledge
              </div>
              <p className="mt-1 text-xs leading-5 text-[var(--muted)]">
                Search across your documents and
                evidence layer.
              </p>
            </a>

            <a
              href="/decisions"
              className="rounded-2xl border border-[var(--border)] bg-[var(--panel-2)] p-5 transition hover:-translate-y-0.5 hover:border-[#2d3948]"
            >
              <div className="text-lg">◇</div>
              <div className="mt-3 text-sm font-semibold">
                Review Decisions
              </div>
              <p className="mt-1 text-xs leading-5 text-[var(--muted)]">
                Trace decisions back to assumptions,
                claims, and evidence.
              </p>
            </a>
          </div>
        </section>
      </div>
    </div>
  );
}