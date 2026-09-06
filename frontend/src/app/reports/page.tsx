"use client";

import {
  FormEvent,
  useState,
} from "react";

import AppShell from "@/components/layout/AppShell";
import SectionHeader from "@/components/ui/SectionHeader";
import {
  generateResearchReport,
  type ResearchReport,
} from "@/lib/api";

const WORKSPACE_ID =
  "6314f325-3492-4273-b2a2-adaa9fb0e661";

export default function ReportsPage() {
  const [question, setQuestion] =
    useState("");

  const [report, setReport] =
    useState<ResearchReport | null>(null);

  const [loading, setLoading] =
    useState(false);

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

    try {
      const result =
        await generateResearchReport(
          WORKSPACE_ID,
          trimmed,
        );

      setReport(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Report generation failed.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <div className="nexus-grid min-h-full p-7">
        <div className="mx-auto max-w-[1200px] space-y-7">
          <section>
            <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
              Research
            </div>

            <h1 className="mt-2 text-3xl font-semibold tracking-tight">
              Research Reports
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--muted)]">
              Turn a research question into a structured
              analyst-style report backed by verified
              evidence.
            </p>
          </section>

          <form
            onSubmit={handleSubmit}
            className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-5"
          >
            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              rows={4}
              placeholder="Ask NEXUS to analyze your documents, evidence, decisions, or any topic in this workspace."
              className="w-full resize-none rounded-xl border border-[var(--border)] bg-[var(--panel-2)] px-4 py-3 text-sm leading-6 outline-none placeholder:text-[var(--muted-2)] focus:border-[var(--accent)]/40"
            />

            <div className="mt-4 flex justify-end">
              <button
                type="submit"
                disabled={
                  loading || !question.trim()
                }
                className="rounded-xl bg-[var(--accent)] px-5 py-3 text-xs font-semibold text-black transition hover:opacity-90 disabled:opacity-40"
              >
                {loading
                  ? "Generating report..."
                  : "Generate report"}
              </button>
            </div>
          </form>

          {error && (
            <div className="rounded-2xl border border-[var(--danger)]/20 bg-[var(--danger)]/5 p-4 text-sm text-[var(--danger)]">
              {error}
            </div>
          )}

          {report && (
            <>
              <section className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
                <div className="flex items-start justify-between gap-5">
                  <SectionHeader
                    eyebrow="Report"
                    title={report.title}
                    description={report.question}
                  />

                  <div className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] px-4 py-3 text-right">
                    <div className="text-[10px] uppercase tracking-[0.14em] text-[var(--muted-2)]">
                      Confidence
                    </div>

                    <div className="mt-1 text-xl font-semibold text-[var(--accent)]">
                      {Math.round(
                        report.confidence * 100,
                      )}
                      %
                    </div>
                  </div>
                </div>

                <div className="mt-7 rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-5">
                  <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--muted-2)]">
                    Executive summary
                  </div>

                  <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-white/90">
                    {report.executive_summary}
                  </p>
                </div>
              </section>

              <section className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
                <SectionHeader
                  eyebrow="Findings"
                  title="Key findings"
                />

                <div className="mt-6 grid gap-4 md:grid-cols-2">
                  {report.findings.map(
                    (finding, index) => (
                      <div
                        key={`${finding.title}-${index}`}
                        className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-5"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <h3 className="text-sm font-semibold">
                            {finding.title}
                          </h3>

                          <span className="text-[10px] text-[var(--accent)]">
                            {Math.round(
                              finding.confidence *
                                100,
                            )}
                            %
                          </span>
                        </div>

                        <p className="mt-3 text-xs leading-6 text-[var(--muted)]">
                          {finding.explanation}
                        </p>
                      </div>
                    ),
                  )}
                </div>
              </section>

              <section className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
                <SectionHeader
                  eyebrow="Analysis"
                  title="Report sections"
                />

                <div className="mt-6 space-y-4">
                  {report.sections.map(
                    (section, index) => (
                      <div
                        key={`${section.title}-${index}`}
                        className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-5"
                      >
                        <h3 className="text-sm font-semibold">
                          {section.title}
                        </h3>

                        <p className="mt-3 whitespace-pre-wrap text-xs leading-6 text-[var(--muted)]">
                          {section.content}
                        </p>
                      </div>
                    ),
                  )}
                </div>
              </section>

              <section className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
                <SectionHeader
                  eyebrow="Evidence"
                  title="Supporting sources"
                  description={`${report.evidence.length} verified source passage${report.evidence.length === 1 ? "" : "s"}.`}
                />

                <div className="mt-6 space-y-4">
                  {report.evidence.map(
                    (item, index) => (
                      <div
                        key={`${item.document_id}-${item.page_number}-${index}`}
                        className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-5"
                      >
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-xs font-medium">
                            {item.document_title ??
                              "Knowledge source"}
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

              <section className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
                <SectionHeader
                  eyebrow="Trace"
                  title="Research trace"
                />

                <div className="mt-6 space-y-3">
                  {report.research_trace.map(
                    (event) => (
                      <div
                        key={`${event.step_number}-${event.action}`}
                        className="flex gap-4 rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-4"
                      >
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-[var(--accent)]/30 bg-[var(--accent-soft)] text-xs text-[var(--accent)]">
                          {event.step_number}
                        </div>

                        <div>
                          <div className="text-sm font-medium">
                            {event.tool ??
                              "Finished"}
                          </div>

                          <p className="mt-1 text-xs leading-5 text-[var(--muted)]">
                            {event.reason}
                          </p>

                          <p className="mt-2 text-[10px] text-[var(--muted-2)]">
                            {event.outcome}
                          </p>
                        </div>
                      </div>
                    ),
                  )}
                </div>
              </section>
            </>
          )}
        </div>
      </div>
    </AppShell>
  );
}