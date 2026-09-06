"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import AppShell from "@/components/layout/AppShell";
import SectionHeader from "@/components/ui/SectionHeader";
import {
  createAssumption,
  createDecision,
  createDecisionDependency,
  getDecisionAnalysis,
  type Assumption,
  type Decision,
  type DecisionAnalysis,
} from "@/lib/api";

const WORKSPACE_ID =
  "6314f325-3492-4273-b2a2-adaa9fb0e661";

const EXISTING_DECISION_ID =
  "946f2b87-a474-41fa-9ec6-a97b32ef83d0";

export default function DecisionsPage() {
  const [decision, setDecision] =
    useState<Decision | null>(null);

  const [analysis, setAnalysis] =
    useState<DecisionAnalysis | null>(null);

  const [assumption, setAssumption] =
    useState<Assumption | null>(null);

  const [title, setTitle] =
    useState("");

  const [description, setDescription] =
    useState("");

  const [priority, setPriority] =
    useState<
      "low" | "medium" | "high" | "critical"
    >("medium");

  const [loading, setLoading] =
    useState(false);

  const [message, setMessage] =
    useState<string | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  async function loadAnalysis(
    decisionId: string,
  ) {
    try {
      const result =
        await getDecisionAnalysis(
          decisionId,
        );

      setAnalysis(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not load decision.",
      );
    }
  }

  useEffect(() => {
    void loadAnalysis(
      EXISTING_DECISION_ID,
    );
  }, []);

  async function handleCreateDecision(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!title.trim()) return;

    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const result =
        await createDecision(
          WORKSPACE_ID,
          title.trim(),
          description.trim(),
          priority,
          0.8,
        );

      setDecision(result);

      await loadAnalysis(result.id);

      setMessage(
        "Decision created successfully.",
      );

      setTitle("");
      setDescription("");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Decision creation failed.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateAssumption(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const result =
        await createAssumption(
          WORKSPACE_ID,
          "Employee performance remains satisfactory",
          "The available assessment evidence indicates satisfactory performance.",
          0.8,
        );

      setAssumption(result);

      const targetDecision =
        decision ??
        analysis?.decision ??
        null;

      if (targetDecision) {
        await createDecisionDependency(
          targetDecision.id,
          "depends_on",
          result.id,
          undefined,
          0.8,
        );

        await loadAnalysis(
          targetDecision.id,
        );
      }

      setMessage(
        "Assumption created and connected.",
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Assumption creation failed.",
      );
    } finally {
      setLoading(false);
    }
  }

  const activeDecision =
    decision ?? analysis?.decision ?? null;

  return (
    <AppShell>
      <div className="nexus-grid min-h-full p-7">
        <div className="mx-auto max-w-[1200px] space-y-7">
          <section className="pt-2">
            <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
              Decision Intelligence
            </div>

            <h1 className="mt-2 text-3xl font-semibold tracking-tight">
              Decisions
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--muted)]">
              Track decisions, their assumptions,
              supporting claims, and evidence-driven
              impact.
            </p>
          </section>

          {error && (
            <div className="rounded-2xl border border-[var(--danger)]/20 bg-[var(--danger)]/5 p-4 text-sm text-[var(--danger)]">
              {error}
            </div>
          )}

          {message && (
            <div className="rounded-2xl border border-[var(--accent)]/20 bg-[var(--accent-soft)] p-4 text-sm text-[var(--accent)]">
              {message}
            </div>
          )}

          <section className="grid gap-5 lg:grid-cols-[1fr_1fr]">
            <form
              onSubmit={handleCreateDecision}
              className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6"
            >
              <SectionHeader
                eyebrow="Create"
                title="New decision"
                description="Record a decision that can be traced to evidence and assumptions."
              />

              <div className="mt-6 space-y-4">
                <input
                  value={title}
                  onChange={(event) =>
                    setTitle(event.target.value)
                  }
                  placeholder="Decision title"
                  className="w-full rounded-xl border border-[var(--border)] bg-[var(--panel-2)] px-4 py-3 text-sm outline-none placeholder:text-[var(--muted-2)] focus:border-[var(--accent)]/40"
                />

                <textarea
                  value={description}
                  onChange={(event) =>
                    setDescription(
                      event.target.value,
                    )
                  }
                  placeholder="What is this decision about?"
                  rows={4}
                  className="w-full resize-none rounded-xl border border-[var(--border)] bg-[var(--panel-2)] px-4 py-3 text-sm leading-6 outline-none placeholder:text-[var(--muted-2)] focus:border-[var(--accent)]/40"
                />

                <select
                  value={priority}
                  onChange={(event) =>
                    setPriority(
                      event.target.value as
                        | "low"
                        | "medium"
                        | "high"
                        | "critical",
                    )
                  }
                  className="w-full rounded-xl border border-[var(--border)] bg-[var(--panel-2)] px-4 py-3 text-sm text-white outline-none"
                >
                  <option value="low">
                    Low priority
                  </option>
                  <option value="medium">
                    Medium priority
                  </option>
                  <option value="high">
                    High priority
                  </option>
                  <option value="critical">
                    Critical priority
                  </option>
                </select>

                <button
                  type="submit"
                  disabled={
                    loading || !title.trim()
                  }
                  className="w-full rounded-xl bg-[var(--accent)] px-5 py-3 text-xs font-semibold text-black transition hover:opacity-90 disabled:opacity-40"
                >
                  {loading
                    ? "Creating..."
                    : "Create decision"}
                </button>
              </div>
            </form>

            <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
              <SectionHeader
                eyebrow="Decision graph"
                title={
                  activeDecision?.title ??
                  "Current decision"
                }
                description="Live analysis of your decision dependencies."
              />

              {analysis ? (
                <div className="mt-6 space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-4">
                      <div className="text-[10px] uppercase tracking-[0.14em] text-[var(--muted-2)]">
                        Status
                      </div>
                      <div className="mt-2 text-sm font-semibold text-white">
                        {analysis.decision.status}
                      </div>
                    </div>

                    <div className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-4">
                      <div className="text-[10px] uppercase tracking-[0.14em] text-[var(--muted-2)]">
                        Impact
                      </div>
                      <div className="mt-2 text-sm font-semibold text-[var(--accent)]">
                        {analysis.impact_level}
                      </div>
                    </div>
                  </div>

                  <div className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-4">
                    <div className="text-xs text-[var(--muted)]">
                      Assumptions
                    </div>

                    <div className="mt-3 space-y-2">
                      {analysis.impacted_assumptions
                        .length === 0 ? (
                        <div className="text-xs text-[var(--muted-2)]">
                          No assumptions connected.
                        </div>
                      ) : (
                        analysis.impacted_assumptions.map(
                          (item) => (
                            <div
                              key={item.id}
                              className="rounded-lg border border-[var(--border)] px-3 py-2"
                            >
                              <div className="text-xs font-medium">
                                {item.name}
                              </div>
                              <div className="mt-1 text-[10px] text-[var(--muted-2)]">
                                {item.status}
                              </div>
                            </div>
                          ),
                        )
                      )}
                    </div>
                  </div>

                  <div className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-4">
                    <div className="text-xs text-[var(--muted)]">
                      Supporting claims
                    </div>

                    <div className="mt-3 space-y-2">
                      {analysis.impacted_claims
                        .length === 0 ? (
                        <div className="text-xs text-[var(--muted-2)]">
                          No claims connected.
                        </div>
                      ) : (
                        analysis.impacted_claims.map(
                          (claim) => (
                            <div
                              key={claim.id}
                              className="rounded-lg border border-[var(--border)] px-3 py-2"
                            >
                              <div className="text-xs font-medium">
                                {claim.predicate}
                              </div>
                              <div className="mt-1 text-[10px] text-[var(--muted)]">
                                {claim.object_text ??
                                  claim.normalized_value}
                              </div>
                            </div>
                          ),
                        )
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="mt-6 rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-6 text-sm text-[var(--muted)]">
                  Loading decision analysis...
                </div>
              )}
            </div>
          </section>

          <form
            onSubmit={handleCreateAssumption}
            className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6"
          >
            <SectionHeader
              eyebrow="Dependencies"
              title="Connect an assumption"
              description="Add the assumption behind the currently selected decision."
            />

            <div className="mt-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <div className="text-sm font-medium">
                  Employee performance remains satisfactory
                </div>

                <div className="mt-1 text-xs text-[var(--muted)]">
                  This uses the existing demo assumption
                  used by the Decision Intelligence
                  backend.
                </div>

                {assumption && (
                  <div className="mt-2 font-mono text-[10px] text-[var(--muted-2)]">
                    {assumption.id}
                  </div>
                )}
              </div>

              <button
                type="submit"
                disabled={
                  loading || !activeDecision
                }
                className="rounded-xl border border-[var(--border)] bg-[var(--panel-2)] px-5 py-3 text-xs font-semibold text-white transition hover:border-[var(--accent)]/30 hover:text-[var(--accent)] disabled:opacity-40"
              >
                Connect assumption
              </button>
            </div>
          </form>

          <section className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
            <SectionHeader
              eyebrow="Propagation"
              title="Decision impact model"
              description="The intelligence chain NEXUS tracks."
            />

            <div className="mt-6 grid gap-3 md:grid-cols-5">
              {[
                "Evidence",
                "Claim",
                "Assumption",
                "Decision",
                "Impact",
              ].map((item, index) => (
                <div
                  key={item}
                  className="relative rounded-xl border border-[var(--border)] bg-[var(--panel-2)] p-4"
                >
                  <div className="text-[10px] text-[var(--muted-2)]">
                    0{index + 1}
                  </div>

                  <div className="mt-2 text-sm font-medium">
                    {item}
                  </div>

                  {index < 4 && (
                    <div className="absolute -right-3 top-1/2 hidden -translate-y-1/2 text-[var(--muted-2)] md:block">
                      →
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </AppShell>
  );
}