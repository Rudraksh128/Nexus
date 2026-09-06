"use client";

import { FormEvent, useState } from "react";

import AppShell from "@/components/layout/AppShell";
import SectionHeader from "@/components/ui/SectionHeader";
import { NEXUS_CONFIG } from "@/lib/config";
import { runResearch } from "@/lib/api";

const WORKSPACE_ID = NEXUS_CONFIG.WORKSPACE_ID;

type ResearchResponse = {
  question: string;
  answer: string;
  confidence: number;
  steps: {
    tool: string;
    reason: string;
    arguments: Record<string, unknown>;
  }[];
  trace: {
    step_number: number;
    action: string;
    tool: string | null;
    reason: string;
    outcome: string;
  }[];
  evidence: {
    source_type: string;
    document_id: string | null;
    document_title: string | null;
    page_number: number | null;
    text: string;
    relevance: number | null;
  }[];
};

export default function ResearchPage() {
  const [question, setQuestion] = useState("");
  const [result, setResult] =
    useState<ResearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] =
    useState<string | null>(null);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const trimmed = question.trim();

    if (!trimmed) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await runResearch(
        WORKSPACE_ID,
        trimmed,
      );

      setResult(response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Research request failed.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <div className="nexus-grid min-h-full p-7">
        <div className="mx-auto max-w-[1200px] space-y-7">
          <section className="pt-2">
            <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
              Agentic Research
            </div>

            <h1 className="mt-2 text-3xl font-semibold tracking-tight">
              Ask NEXUS.
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--muted)]">
              Ask a question and let NEXUS search,
              reason over evidence, and produce a
              grounded answer.
            </p>
          </section>

          <form
            onSubmit={handleSubmit}
            className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-5"
          >
            <div className="flex items-center justify-between">
              <label
                htmlFor="research-question"
                className="text-xs font-medium text-[var(--muted)]"
              >
                Research question
              </label>

              <span className="text-[10px] uppercase tracking-[0.16em] text-[var(--muted-2)]">
                Local AI · Qwen3
              </span>
            </div>

            <textarea
              id="research-question"
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              placeholder="Ask a question about your uploaded documents..."
              rows={5}
              className="mt-4 w-full resize-none rounded-xl border border-[var(--border)] bg-[var(--panel-2)] px-4 py-3 text-sm leading-6 outline-none placeholder:text-[var(--muted-2)] focus:border-[var(--accent)]/40"
            />

            <div className="mt-4 flex items-center justify-between">
              <p className="text-xs text-[var(--muted-2)]">
                NEXUS will expose the research trace
                and supporting evidence.
              </p>

              <button
                type="submit"
                disabled={
                  loading || !question.trim()
                }
                className="rounded-xl bg-[var(--accent)] px-5 py-2.5 text-xs font-semibold text-black transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {loading
                  ? "Investigating..."
                  : "Investigate"}
              </button>
            </div>
          </form>

          {error && (
            <div className="rounded-2xl border border-[var(--danger)]/20 bg-[var(--danger)]/5 p-4 text-sm text-[var(--danger)]">
              {error}
            </div>
          )}

          {loading && (
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
              <div className="flex items-center gap-3">
                <div className="h-2 w-2 animate-pulse rounded-full bg-[var(--accent)]" />
                <span className="text-sm text-[var(--muted)]">
                  NEXUS is researching your question...
                </span>
              </div>

              <div className="mt-5 grid gap-3 md:grid-cols-3">
                {[
                  "Planning research",
                  "Collecting evidence",
                  "Synthesizing answer",
                ].map((label) => (
                  <div
                    key={label}
                    className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-4"
                  >
                    <div className="text-xs text-[var(--muted)]">
                      {label}
                    </div>
                    <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
                      <div className="h-full w-2/3 animate-pulse rounded-full bg-[var(--accent)]/50" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result && (
            <>
              <section className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
                <div className="flex items-start justify-between gap-5">
                  <SectionHeader
                    eyebrow="Answer"
                    title="Research result"
                    description={result.question}
                  />

                  <div className="shrink-0 rounded-xl border border-[var(--border)] bg-[var(--panel-2)] px-3 py-2 text-right">
                    <div className="text-[10px] uppercase tracking-[0.16em] text-[var(--muted-2)]">
                      Confidence
                    </div>
                    <div className="mt-1 text-lg font-semibold text-[var(--accent)]">
                      {Math.round(
                        result.confidence * 100,
                      )}
                      %
                    </div>
                  </div>
                </div>

                <div className="mt-7 rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-5">
                  <p className="whitespace-pre-wrap text-sm leading-7 text-white/90">
                    {result.answer}
                  </p>
                </div>
              </section>

              <section className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
                <SectionHeader
                  eyebrow="Trace"
                  title="Research trace"
                  description="How NEXUS reached the answer."
                />

                <div className="mt-6 space-y-3">
                  {result.trace.map((event) => (
                    <div
                      key={`${event.step_number}-${event.action}`}
                      className="flex gap-4 rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-4"
                    >
                      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-[var(--accent)]/30 bg-[var(--accent-soft)] text-xs text-[var(--accent)]">
                        {event.step_number}
                      </div>

                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-sm font-medium">
                            {event.tool
                              ? event.tool
                              : "Finished"}
                          </span>

                          <span className="rounded-full border border-[var(--border)] px-2 py-0.5 text-[9px] uppercase tracking-[0.12em] text-[var(--muted-2)]">
                            {event.action}
                          </span>
                        </div>

                        <p className="mt-1 text-xs leading-5 text-[var(--muted)]">
                          {event.reason}
                        </p>

                        <p className="mt-2 text-[11px] text-[var(--muted-2)]">
                          {event.outcome}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              <section className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
                <SectionHeader
                  eyebrow="Sources"
                  title="Verified evidence"
                  description={`${result.evidence.length} supporting source passage${result.evidence.length === 1 ? "" : "s"}.`}
                />

                <div className="mt-6 space-y-4">
                  {result.evidence.map(
                    (item, index) => (
                      <div
                        key={`${item.document_id}-${item.page_number}-${index}`}
                        className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-5"
                      >
                        <div className="flex flex-wrap items-center gap-2 text-xs">
                          <span className="font-medium text-white">
                            {item.document_title ??
                              "Unknown source"}
                          </span>

                          {item.page_number !==
                            null && (
                            <span className="rounded-full border border-[var(--border)] px-2 py-0.5 text-[10px] text-[var(--muted)]">
                              Page{" "}
                              {item.page_number}
                            </span>
                          )}
                        </div>

                        <p className="mt-4 whitespace-pre-wrap text-xs leading-6 text-[var(--muted)]">
                          {item.text}
                        </p>
                      </div>
                    ),
                  )}
                </div>
              </section>

              {result.steps.length > 0 && (
                <section className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
                  <SectionHeader
                    eyebrow="Execution"
                    title="Tools used"
                    description="Actions selected by the research agent."
                  />

                  <div className="mt-6 flex flex-wrap gap-2">
                    {result.steps.map(
                      (step, index) => (
                        <div
                          key={`${step.tool}-${index}`}
                          className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] px-3 py-2"
                        >
                          <div className="text-xs font-medium">
                            {step.tool}
                          </div>
                          <div className="mt-1 text-[10px] text-[var(--muted-2)]">
                            {step.reason}
                          </div>
                        </div>
                      ),
                    )}
                  </div>
                </section>
              )}
            </>
          )}
        </div>
      </div>
    </AppShell>
  );
}
