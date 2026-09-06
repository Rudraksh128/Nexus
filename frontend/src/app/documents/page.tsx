"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import AppShell from "@/components/layout/AppShell";
import { NEXUS_CONFIG } from "@/lib/config";
import { getDocuments, type DocumentSummary } from "@/lib/api";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDocuments() {
    try {
      setLoading(true);
      setError("");
      const result = await getDocuments();
      setDocuments(result.documents);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load indexed documents.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    getDocuments()
      .then((result) => setDocuments(result.documents))
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Unable to load indexed documents."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <main className="min-h-screen px-6 py-8 text-white">
        <div className="mx-auto max-w-[1500px]">
          <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-400">Source library</div>
              <h1 className="mt-3 text-4xl font-bold tracking-tight">Documents</h1>
              <p className="mt-3 max-w-2xl text-lg text-slate-400">Browse the source material already indexed in this workspace.</p>
            </div>
            <Link href="/upload" className="rounded-xl bg-emerald-300 px-5 py-3 text-center text-sm font-semibold text-black transition hover:bg-emerald-200">Upload document</Link>
          </div>

          <div className="mt-8 flex items-center justify-between rounded-2xl border border-slate-800 bg-[#0d1118] px-5 py-4">
            <div>
              <div className="text-sm font-semibold">{loading ? "Loading documents…" : `${documents.length} indexed document${documents.length === 1 ? "" : "s"}`}</div>
              <div className="mt-1 text-xs text-slate-500">Workspace: {NEXUS_CONFIG.WORKSPACE_ID.slice(0, 8)}…</div>
            </div>
            <button type="button" onClick={() => void loadDocuments()} disabled={loading} className="rounded-lg border border-slate-700 px-3 py-2 text-xs text-slate-300 transition hover:border-emerald-400 hover:text-emerald-300 disabled:cursor-not-allowed disabled:opacity-50">Refresh</button>
          </div>

          {error && <div className="mt-5 rounded-2xl border border-red-900/60 bg-red-950/20 p-5 text-sm text-red-200">{error}</div>}
          {loading && <div className="mt-5 rounded-2xl border border-slate-800 bg-[#0d1118] px-6 py-16 text-center text-slate-400">Loading your indexed sources…</div>}

          {!loading && !error && documents.length === 0 && (
            <div className="mt-5 rounded-2xl border border-dashed border-slate-700 bg-[#0d1118] px-6 py-16 text-center">
              <h2 className="text-lg font-semibold">No documents indexed yet</h2>
              <p className="mt-2 text-sm text-slate-500">Upload a source document to create searchable evidence and knowledge.</p>
              <Link href="/upload" className="mt-6 inline-block rounded-lg border border-emerald-500/50 px-4 py-2 text-sm text-emerald-300 transition hover:bg-emerald-400/10">Go to upload</Link>
            </div>
          )}

          {!loading && documents.length > 0 && (
            <div className="mt-5 overflow-hidden rounded-2xl border border-slate-800 bg-[#0d1118]">
              {documents.map((document) => (
                <article key={document.id} className="flex flex-col gap-4 border-b border-slate-800 p-5 last:border-b-0 md:flex-row md:items-center md:justify-between">
                  <div className="min-w-0"><h2 className="truncate text-base font-semibold">{document.title}</h2><p className="mt-1 text-sm text-slate-500">Indexed {formatDate(document.created_at)}</p></div>
                  <div className="flex flex-wrap gap-2 text-xs"><Badge>{document.source_type.toUpperCase()}</Badge><Badge>{document.pages} page{document.pages === 1 ? "" : "s"}</Badge><Badge>{document.chunks} chunk{document.chunks === 1 ? "" : "s"}</Badge></div>
                </article>
              ))}
            </div>
          )}
        </div>
      </main>
    </AppShell>
  );
}

function Badge({ children }: { children: React.ReactNode }) {
  return <span className="rounded-full border border-slate-700 px-3 py-1 text-slate-400">{children}</span>;
}

function formatDate(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "at an unknown time" : date.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}
