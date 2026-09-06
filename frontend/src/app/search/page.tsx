"use client";

import { useState, type KeyboardEvent } from "react";

import AppShell from "@/components/layout/AppShell";
import { NEXUS_CONFIG } from "@/lib/config";
import { searchKnowledge, type SearchResult } from "@/lib/api";

const WORKSPACE_ID = NEXUS_CONFIG.WORKSPACE_ID;

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch() {
    const trimmed = query.trim();

    if (!trimmed) return;

    setLoading(true);
    setSearched(true);
    setError("");
    setResults([]);

    try {
      const data = await searchKnowledge(trimmed, WORKSPACE_ID);

      const extractedResults =
        data?.results ??
        [];

      setResults(
        Array.isArray(extractedResults)
          ? extractedResults
          : [],
      );
    } catch (err) {
      console.error("Search error:", err);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to NEXUS search.",
      );
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(
    event: KeyboardEvent<HTMLInputElement>,
  ) {
    if (event.key === "Enter") {
      handleSearch();
    }
  }

  function selectExample(example: string) {
    setQuery(example);
  }

  return (
    <AppShell>
    <main className="min-h-screen bg-[#07090d] px-6 py-8 text-white">
      <div className="mx-auto max-w-[1500px]">

        {/* Header */}
        <div className="mb-10">
          <div className="mb-3 text-sm font-semibold tracking-[0.22em] text-emerald-400">
            INTELLIGENCE RETRIEVAL
          </div>

          <h1 className="text-4xl font-bold tracking-tight">
            Search
          </h1>

          <p className="mt-3 text-lg text-slate-400">
            Search across your documents using semantic and
            lexical retrieval.
          </p>
        </div>

        {/* Search bar */}
        <div className="flex gap-3">
          <input
            value={query}
            onChange={(event) =>
              setQuery(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Search your evidence..."
            className="h-16 flex-1 rounded-2xl border border-slate-700 bg-[#0d1118] px-5 text-lg outline-none transition focus:border-emerald-400"
          />

          <button
            onClick={handleSearch}
            disabled={loading || !query.trim()}
            className="h-16 rounded-2xl bg-emerald-300 px-9 text-lg font-medium text-black transition hover:bg-emerald-200 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {/* Summary */}
        <div className="mt-8 flex items-center justify-between">
          <div>
            <div className="text-lg font-semibold">
              {loading
                ? "Searching NEXUS..."
                : `${results.length} result${
                    results.length === 1
                      ? ""
                      : "s"
                  }`}
            </div>

            <div className="mt-1 text-sm text-slate-500">
              Ranked by NEXUS hybrid retrieval
            </div>
          </div>

          {searched && (
            <div className="text-sm text-slate-500">
              Workspace: {WORKSPACE_ID.slice(0, 8)}...
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="mt-6 rounded-2xl border border-red-900/60 bg-red-950/20 p-5">
            <div className="font-semibold text-red-300">
              Search error
            </div>

            <div className="mt-2 text-sm text-red-200/70">
              {error}
            </div>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="mt-6 rounded-2xl border border-slate-800 bg-[#0d1118] px-6 py-16 text-center">
            <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-slate-700 border-t-emerald-400" />

            <div className="text-lg font-semibold">
              Searching your evidence
            </div>

            <div className="mt-2 text-sm text-slate-500">
              Running semantic and lexical retrieval...
            </div>
          </div>
        )}

        {/* Initial state */}
        {!loading && !searched && (
          <div className="mt-6 rounded-2xl border border-slate-800 bg-[#0d1118] px-6 py-16 text-center">
            <div className="text-lg font-semibold">
              Search your NEXUS knowledge
            </div>

            <div className="mt-2 text-slate-500">
              Search across your indexed evidence.
            </div>

            <div className="mt-5 flex flex-wrap justify-center gap-3">
              {[
                "ATUL SHANKER",
                "assessment period",
                "Reporting Authority",
                "Grade Pay",
              ].map((example) => (
                <button
                  key={example}
                  onClick={() =>
                    selectExample(example)
                  }
                  className="rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-300 transition hover:border-emerald-400 hover:text-emerald-300"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* No results */}
        {!loading &&
          searched &&
          results.length === 0 &&
          !error && (
            <div className="mt-6 rounded-2xl border border-slate-800 bg-[#0d1118] px-6 py-16 text-center">
              <div className="text-lg font-semibold">
                No evidence found
              </div>

              <div className="mt-2 text-slate-500">
                Try another query or use terminology from
                your documents.
              </div>
            </div>
          )}

        {/* Results */}
        {!loading && results.length > 0 && (
          <div className="mt-6 space-y-4">
            {results.map((result, index) => (
              <article
                key={
                  result.chunk_id ??
                  result.document_id ??
                  index
                }
                className="rounded-2xl border border-slate-800 bg-[#0d1118] p-6 transition hover:border-slate-600"
              >
                <div className="flex items-start justify-between gap-5">
                  <div>
                    <div className="text-lg font-semibold">
                      {result.document_title ??
                        "NEXUS Evidence"}
                    </div>

                    <div className="mt-1 text-sm text-slate-500">
                      {result.page_number
                        ? `Page ${result.page_number}`
                        : "Document evidence"}
                    </div>
                  </div>

                  {result.rerank_score != null && (
                    <div className="rounded-lg border border-slate-700 px-3 py-2 text-right">
                      <div className="text-xs uppercase tracking-wider text-slate-500">
                        Rerank
                      </div>

                      <div className="font-semibold text-emerald-300">
                        {result.rerank_score.toFixed(3)}
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-5 rounded-xl bg-black/20 p-5">
                  <p className="whitespace-pre-wrap leading-7 text-slate-300">
                    {result.text ??
                      "No evidence text returned."}
                  </p>
                </div>

                <div className="mt-5 flex flex-wrap gap-2">
                  {result.retrieval_sources?.map(
                    (source) => (
                      <span
                        key={source}
                        className="rounded-full border border-emerald-900/60 bg-emerald-950/20 px-3 py-1 text-xs uppercase tracking-wider text-emerald-300"
                      >
                        {source}
                      </span>
                    ),
                  )}

                  {result.vector_similarity != null && (
                    <span className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400">
                      Vector{" "}
                      {result.vector_similarity.toFixed(
                        3,
                      )}
                    </span>
                  )}

                  {result.lexical_score != null && (
                    <span className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400">
                      Lexical{" "}
                      {result.lexical_score.toFixed(
                        3,
                      )}
                    </span>
                  )}

                  {result.rrf_score != null && (
                    <span className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400">
                      RRF{" "}
                      {result.rrf_score.toFixed(3)}
                    </span>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </main>
    </AppShell>
  );
}
