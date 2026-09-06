"use client";

import { useEffect, useState } from "react";

import AppShell from "@/components/layout/AppShell";
import MetricCard from "@/components/ui/MetricCard";
import SectionHeader from "@/components/ui/SectionHeader";
import {
  getWorkspaceAnalytics,
  type WorkspaceAnalytics,
} from "@/lib/api";

const WORKSPACE_ID =
  "6314f325-3492-4273-b2a2-adaa9fb0e661";

export default function AnalyticsPage() {
  const [data, setData] =
    useState<WorkspaceAnalytics | null>(
      null,
    );

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    getWorkspaceAnalytics(
      WORKSPACE_ID,
    )
      .then(setData)
      .catch((err: Error) =>
        setError(err.message),
      );
  }, []);

  const metrics = data
    ? [
        ["Documents", data.documents],
        ["Chunks", data.chunks],
        ["Entities", data.entities],
        ["Claims", data.claims],
        ["Evidence", data.evidence],
        ["Events", data.events],
        ["Relationships", data.relationships],
        ["Assumptions", data.assumptions],
        ["Decisions", data.decisions],
        [
          "Decision impacts",
          data.decision_impacts,
        ],
      ]
    : [];

  return (
    <AppShell>
      <div className="nexus-grid min-h-full p-7">
        <div className="mx-auto max-w-[1400px] space-y-7">
          <section>
            <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
              Workspace Analytics
            </div>

            <h1 className="mt-2 text-3xl font-semibold tracking-tight">
              Analytics
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--muted)]">
              A live view of the knowledge and decision
              intelligence state of your workspace.
            </p>
          </section>

          {error && (
            <div className="rounded-2xl border border-[var(--danger)]/20 bg-[var(--danger)]/5 p-4 text-sm text-[var(--danger)]">
              {error}
            </div>
          )}

          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5">
            {metrics.map(
              ([label, value]) => (
                <MetricCard
                  key={String(label)}
                  label={String(label)}
                  value={value}
                />
              ),
            )}
          </section>

          <section className="grid gap-5 lg:grid-cols-2">
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
              <SectionHeader
                eyebrow="Knowledge"
                title="Knowledge density"
                description="Relative distribution of the current knowledge layer."
              />

              <div className="mt-7 space-y-5">
                {data &&
                  [
                    [
                      "Claims",
                      data.claims,
                      Math.max(
                        data.claims,
                        data.evidence,
                        1,
                      ),
                    ],
                    [
                      "Evidence",
                      data.evidence,
                      Math.max(
                        data.claims,
                        data.evidence,
                        1,
                      ),
                    ],
                    [
                      "Entities",
                      data.entities,
                      Math.max(
                        data.entities,
                        data.relationships,
                        1,
                      ),
                    ],
                    [
                      "Relationships",
                      data.relationships,
                      Math.max(
                        data.entities,
                        data.relationships,
                        1,
                      ),
                    ],
                  ].map(
                    ([label, value, maximum]) => (
                      <div key={String(label)}>
                        <div className="mb-2 flex items-center justify-between text-xs">
                          <span className="text-[var(--muted)]">
                            {label}
                          </span>
                          <span className="text-white">
                            {value}
                          </span>
                        </div>

                        <div className="h-2 overflow-hidden rounded-full bg-white/[0.05]">
                          <div
                            className="h-full rounded-full bg-[var(--accent)]"
                            style={{
                              width: `${Math.min(
                                100,
                                (Number(value) /
                                  Number(maximum)) *
                                  100,
                              )}%`,
                            }}
                          />
                        </div>
                      </div>
                    ),
                  )}
              </div>
            </div>

            <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
              <SectionHeader
                eyebrow="Decision layer"
                title="Decision readiness"
                description="Current state of tracked assumptions and impacts."
              />

              <div className="mt-7 grid grid-cols-2 gap-4">
                <div className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-5">
                  <div className="text-xs text-[var(--muted)]">
                    Decisions
                  </div>

                  <div className="mt-3 text-3xl font-semibold">
                    {data?.decisions ?? "—"}
                  </div>
                </div>

                <div className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-5">
                  <div className="text-xs text-[var(--muted)]">
                    Assumptions
                  </div>

                  <div className="mt-3 text-3xl font-semibold">
                    {data?.assumptions ?? "—"}
                  </div>
                </div>

                <div className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-5">
                  <div className="text-xs text-[var(--muted)]">
                    Impacts
                  </div>

                  <div className="mt-3 text-3xl font-semibold text-[var(--accent)]">
                    {data?.decision_impacts ??
                      "—"}
                  </div>
                </div>

                <div className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-5">
                  <div className="text-xs text-[var(--muted)]">
                    Evidence / Claim
                  </div>

                  <div className="mt-3 text-3xl font-semibold">
                    {data
                      ? (
                          data.evidence /
                          Math.max(
                            data.claims,
                            1,
                          )
                        ).toFixed(2)
                      : "—"}
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
            <SectionHeader
              eyebrow="System"
              title="NEXUS operating model"
              description="How the workspace transforms raw documents into decisions."
            />

            <div className="mt-7 grid gap-3 md:grid-cols-4">
              {[
                [
                  "01",
                  "Ingest",
                  "Documents become pages, chunks, and embeddings.",
                ],
                [
                  "02",
                  "Understand",
                  "Entities, claims, events, and relationships are extracted.",
                ],
                [
                  "03",
                  "Research",
                  "Agents retrieve, verify, and synthesize evidence.",
                ],
                [
                  "04",
                  "Decide",
                  "Assumptions and decisions remain traceable to evidence.",
                ],
              ].map(
                ([number, title, description]) => (
                  <div
                    key={number}
                    className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-5"
                  >
                    <div className="text-[10px] text-[var(--accent)]">
                      {number}
                    </div>

                    <div className="mt-3 text-sm font-semibold">
                      {title}
                    </div>

                    <p className="mt-2 text-xs leading-5 text-[var(--muted)]">
                      {description}
                    </p>
                  </div>
                ),
              )}
            </div>
          </section>
        </div>
      </div>
    </AppShell>
  );
}