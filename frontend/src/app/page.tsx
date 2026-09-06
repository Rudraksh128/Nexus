"use client";

import { useEffect, useState } from "react";

import AppShell from "@/components/layout/AppShell";
import { getHealth, getKnowledgeGraph } from "@/lib/api";

type Graph = {
  counts: {
    nodes: number;
    edges: number;
    claims: number;
  };
};

export default function HomePage() {
  const [graph, setGraph] =
    useState<Graph | null>(null);

  const [healthy, setHealthy] =
    useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [health, knowledge] =
          await Promise.all([
            getHealth(),
            getKnowledgeGraph(),
          ]);

        setHealthy(health.status === "healthy");
        setGraph(knowledge);
      } catch {
        setHealthy(false);
      }
    }

    load();
  }, []);

  const nodes = graph?.counts.nodes ?? 0;
  const edges = graph?.counts.edges ?? 0;
  const claims = graph?.counts.claims ?? 0;

  return (
    <AppShell>
      <div className="nexus-grid min-h-screen p-7">

        <div className="mx-auto max-w-[1500px]">

          <section className="mb-10">
            <div className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-400">
              Overview
            </div>

            <h1 className="mt-3 text-4xl font-bold">
              Good to see you.
            </h1>

            <p className="mt-3 max-w-3xl text-lg text-slate-400">
              NEXUS turns documents and evidence into
              searchable knowledge, research, and
              decision intelligence.
            </p>
          </section>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">

            <Metric
              label="Entities"
              value={nodes}
              description="Knowledge graph nodes"
            />

            <Metric
              label="Relations"
              value={edges}
              description="Connected relationships"
            />

            <Metric
              label="Claims"
              value={claims}
              description="Structured facts"
            />

            <Metric
              label="Evidence"
              value={claims}
              description="Traceable support"
            />

            <Metric
              label="System"
              value={healthy ? "ONLINE" : "OFFLINE"}
              description="NEXUS API"
              status={healthy}
            />

          </div>

          <div className="mt-6 grid gap-6 lg:grid-cols-3">

            <section className="lg:col-span-2 rounded-2xl border border-slate-800 bg-[#0d1118] p-6">

              <div className="text-xs uppercase tracking-[0.2em] text-emerald-400">
                Intelligence
              </div>

              <h2 className="mt-2 text-2xl font-semibold">
                Knowledge system
              </h2>

              <p className="mt-2 text-sm text-slate-400">
                Current state of the workspace knowledge
                layer.
              </p>

              <div className="mt-7 grid gap-4 sm:grid-cols-3">

                <MiniMetric
                  label="Entities"
                  value={nodes}
                />

                <MiniMetric
                  label="Relations"
                  value={edges}
                />

                <MiniMetric
                  label="Claims"
                  value={claims}
                />

              </div>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-[#0d1118] p-6">

              <div className="text-xs uppercase tracking-[0.2em] text-emerald-400">
                System
              </div>

              <h2 className="mt-2 text-2xl font-semibold">
                Local intelligence
              </h2>

              <p className="mt-2 text-sm text-slate-400">
                Your AI stack is running locally.
              </p>

              <div className="mt-7 space-y-3">

                <SystemRow
                  name="Ollama"
                  status="ONLINE"
                />

                <SystemRow
                  name="Qwen3"
                  status="1.7B"
                />

                <SystemRow
                  name="PostgreSQL"
                  status="CONNECTED"
                />

              </div>
            </section>

          </div>

          <section className="mt-6 rounded-2xl border border-slate-800 bg-[#0d1118] p-6">

            <div className="text-xs uppercase tracking-[0.2em] text-emerald-400">
              Workflow
            </div>

            <h2 className="mt-2 text-2xl font-semibold">
              NEXUS pipeline
            </h2>

            <div className="mt-7 grid gap-4 md:grid-cols-5">

              {[
                ["01", "Documents", "Ingest"],
                ["02", "Evidence", "Extract"],
                ["03", "Knowledge", "Connect"],
                ["04", "Research", "Reason"],
                ["05", "Decisions", "Act"],
              ].map(([number, title, description]) => (
                <div
                  key={number}
                  className="rounded-xl border border-slate-800 bg-[#090c11] p-5"
                >
                  <div className="text-xs text-emerald-400">
                    {number}
                  </div>

                  <div className="mt-4 font-semibold">
                    {title}
                  </div>

                  <div className="mt-1 text-xs text-slate-500">
                    {description}
                  </div>
                </div>
              ))}

            </div>
          </section>

        </div>
      </div>
    </AppShell>
  );
}

function Metric({
  label,
  value,
  description,
  status,
}: {
  label: string;
  value: number | string;
  description: string;
  status?: boolean;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-[#0d1118] p-6">
      <div className="text-xs uppercase tracking-[0.18em] text-slate-500">
        {label}
      </div>

      <div
        className={[
          "mt-4 text-3xl font-bold",
          status
            ? "text-emerald-300"
            : "",
        ].join(" ")}
      >
        {value}
      </div>

      <div className="mt-2 text-sm text-slate-500">
        {description}
      </div>
    </div>
  );
}

function MiniMetric({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-[#090c11] p-5">
      <div className="text-sm text-slate-500">
        {label}
      </div>

      <div className="mt-2 text-2xl font-semibold">
        {value}
      </div>
    </div>
  );
}

function SystemRow({
  name,
  status,
}: {
  name: string;
  status: string;
}) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-[#090c11] px-4 py-4">
      <span>{name}</span>

      <span className="text-xs text-emerald-300">
        {status}
      </span>
    </div>
  );
}