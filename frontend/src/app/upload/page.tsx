"use client";

import Link from "next/link";
import { type ChangeEvent, type DragEvent, useRef, useState } from "react";

import AppShell from "@/components/layout/AppShell";
import { NEXUS_CONFIG } from "@/lib/config";
import { uploadDocument } from "@/lib/api";

const ACCEPTED_TYPES = ".pdf,.txt,.md,.docx,.csv,.json,.xlsx";

export default function UploadPage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function selectFile(nextFile: File | null) { setFile(nextFile); setError(""); setMessage(""); }
  function handleFileChange(event: ChangeEvent<HTMLInputElement>) { selectFile(event.target.files?.[0] ?? null); }
  function handleDrop(event: DragEvent<HTMLDivElement>) { event.preventDefault(); setDragging(false); selectFile(event.dataTransfer.files?.[0] ?? null); }

  async function handleUpload() {
    if (!file) { setError("Choose a document before starting ingestion."); return; }
    try {
      setUploading(true); setError(""); setMessage("");
      const result = await uploadDocument(NEXUS_CONFIG.WORKSPACE_ID, file);
      setMessage(result.status === "already_exists" ? "This document is already indexed in the workspace." : `${result.filename} indexed successfully — ${result.pages ?? 0} pages, ${result.chunks ?? 0} chunks, and ${result.embeddings ?? 0} embeddings.`);
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Document ingestion failed.");
    } finally { setUploading(false); }
  }

  return (
    <AppShell>
      <main className="min-h-screen px-6 py-8 text-white"><div className="mx-auto max-w-[1100px]">
        <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end"><div><div className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-400">Knowledge ingestion</div><h1 className="mt-3 text-4xl font-bold tracking-tight">Upload</h1><p className="mt-3 max-w-2xl text-lg text-slate-400">Add source material to turn it into searchable evidence and connected knowledge.</p></div><Link href="/documents" className="text-sm text-emerald-300 hover:text-emerald-200">View indexed documents →</Link></div>
        <section className="mt-8 rounded-2xl border border-slate-800 bg-[#0d1118] p-6 sm:p-8"><h2 className="text-xl font-semibold">Add a source document</h2><p className="mt-2 text-sm leading-6 text-slate-400">NEXUS extracts pages, chunks text, creates embeddings, and derives entities, claims, and relationships automatically.</p>
          <div role="button" tabIndex={0} onClick={() => inputRef.current?.click()} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); inputRef.current?.click(); } }} onDragEnter={(event) => { event.preventDefault(); setDragging(true); }} onDragOver={(event) => event.preventDefault()} onDragLeave={() => setDragging(false)} onDrop={handleDrop} className={`mt-7 cursor-pointer rounded-2xl border border-dashed p-10 text-center transition ${dragging ? "border-emerald-400 bg-emerald-400/10" : "border-slate-700 bg-black/15 hover:border-emerald-400/70"}`}><div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border border-slate-700 text-2xl text-emerald-300">+</div><div className="mt-4 font-semibold">Drop a file here, or choose a file</div><p className="mt-2 text-sm text-slate-500">PDF, TXT, MD, DOCX, CSV, JSON, or XLSX</p><input ref={inputRef} type="file" accept={ACCEPTED_TYPES} className="hidden" onChange={handleFileChange} /></div>
          {file && <div className="mt-5 flex flex-col gap-3 rounded-xl border border-slate-700 bg-black/15 p-4 sm:flex-row sm:items-center sm:justify-between"><div className="min-w-0"><div className="truncate font-medium">{file.name}</div><div className="mt-1 text-xs text-slate-500">{formatFileSize(file.size)}</div></div><button type="button" onClick={() => selectFile(null)} className="text-left text-sm text-slate-400 hover:text-white">Remove</button></div>}
          {error && <div className="mt-5 rounded-xl border border-red-900/60 bg-red-950/20 px-4 py-3 text-sm text-red-200">{error}</div>}
          {message && <div className="mt-5 rounded-xl border border-emerald-900/60 bg-emerald-950/20 px-4 py-3 text-sm text-emerald-200">{message}</div>}
          <div className="mt-7 flex justify-end"><button type="button" onClick={() => void handleUpload()} disabled={!file || uploading} className="rounded-xl bg-emerald-300 px-5 py-3 text-sm font-semibold text-black transition hover:bg-emerald-200 disabled:cursor-not-allowed disabled:opacity-50">{uploading ? "Indexing document…" : "Ingest document"}</button></div>
        </section>
        <div className="mt-6 grid gap-4 md:grid-cols-3"><ProcessCard title="1. Parse" description="Normalize source content into pages." /><ProcessCard title="2. Index" description="Create chunks and semantic embeddings." /><ProcessCard title="3. Connect" description="Extract claims and knowledge relationships." /></div>
      </div></main>
    </AppShell>
  );
}

function ProcessCard({ title, description }: { title: string; description: string }) { return <div className="rounded-xl border border-slate-800 bg-[#0d1118] p-5"><h2 className="font-semibold">{title}</h2><p className="mt-2 text-sm text-slate-500">{description}</p></div>; }
function formatFileSize(bytes: number) { return `${(bytes / 1024 / 1024).toFixed(2)} MB`; }
