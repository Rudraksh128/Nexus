import { NEXUS_CONFIG } from "./config";

const API_BASE = NEXUS_CONFIG.API_BASE_URL;

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${API_BASE}${path}`,
    {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options?.headers ?? {}),
      },
      cache: "no-store",
    },
  );

  if (!response.ok) {
    const message = await response.text();

    throw new Error(
      message ||
        `NEXUS API error: ${response.status}`,
    );
  }

  return response.json();
}

export async function getHealth() {
  return request<{
    status: string;
  }>("/health");
}

export async function getKnowledgeGraph(
  workspaceId = NEXUS_CONFIG.WORKSPACE_ID,
) {
  return request<{
    workspace_id: string;
    nodes: unknown[];
    edges: unknown[];
    claims: unknown[];
    counts: {
      nodes: number;
      edges: number;
      claims: number;
    };
  }>(
    `/knowledge/graph?workspace_id=${encodeURIComponent(
      workspaceId,
    )}`,
  );
}

export type SearchResult = {
  chunk_id?: string; document_id?: string; document_title?: string; page_number?: number;
  text?: string; vector_similarity?: number | null; lexical_score?: number | null;
  rrf_score?: number | null; rerank_score?: number | null; retrieval_sources?: string[];
};

export async function searchKnowledge(
  query: string,
  workspaceId = NEXUS_CONFIG.WORKSPACE_ID,
) {
  const params = new URLSearchParams({
    workspace_id: workspaceId,
    q: query,
    limit: "10",
  });

  return request<{ results?: SearchResult[] }>(
    `/search?${params.toString()}`,
  );
}

export type ResearchResponse = {
  question: string; answer: string; confidence: number;
  steps: { tool: string; reason: string; arguments: Record<string, unknown> }[];
  trace: { step_number: number; action: string; tool: string | null; reason: string; outcome: string }[];
  evidence: { source_type: string; document_id: string | null; document_title: string | null; page_number: number | null; text: string; relevance: number | null }[];
};

export async function runResearch(
  workspaceId: string,
  question: string,
) {
  return request<ResearchResponse>("/research", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      workspace_id: workspaceId,
      question,
    }),
  });
}

export type DocumentSummary = {
  id: string;
  title: string;
  source_type: string;
  created_at: string;
  pages: number;
  chunks: number;
};

export type UploadDocumentResult = {
  status: "ingested" | "already_exists";
  document_id: string;
  filename: string;
  message?: string;
  pages?: number;
  chunks?: number;
  embeddings?: number;
};

export async function getDocuments(
  workspaceId = NEXUS_CONFIG.WORKSPACE_ID,
) {
  return request<{ documents: DocumentSummary[]; count: number }>(
    `/documents?workspace_id=${encodeURIComponent(workspaceId)}`,
  );
}

export async function uploadDocument(
  workspaceId: string,
  file: File,
) {
  const formData = new FormData();
  formData.set("workspace_id", workspaceId);
  formData.set("file", file);

  return request<UploadDocumentResult>("/documents/upload", {
    method: "POST",
    body: formData,
  });
}

export type WorkspaceAnalytics = {
  documents: number;
  chunks: number;
  entities: number;
  claims: number;
  evidence: number;
  events: number;
  relationships: number;
  assumptions: number;
  decisions: number;
  decision_impacts: number;
};

export async function getWorkspaceAnalytics(workspaceId: string) {
  return request<WorkspaceAnalytics>(
    `/analytics/workspace/${encodeURIComponent(workspaceId)}`,
  );
}

export type ResearchReport = {
  title: string; question: string; confidence: number; executive_summary: string;
  findings: { title: string; confidence: number; explanation: string }[];
  sections: { title: string; content: string }[];
  evidence: { document_id: string | null; document_title: string | null; page_number: number | null; text: string }[];
  research_trace: { step_number: number; action: string; tool: string | null; reason: string; outcome: string }[];
};
export type Decision = { id: string; title: string; status: string; priority: string; description: string | null; confidence: number | null };
export type Assumption = { id: string; name: string; status: string; description: string | null; confidence: number | null };
export type DecisionAnalysis = { decision: Decision; impact_level: string; impacted_assumptions: Assumption[]; impacted_claims: { id: string; predicate: string; object_text: string | null; normalized_value: string | null }[] };

export async function generateResearchReport(
  workspaceId: string,
  question: string,
) {
  return request<ResearchReport>("/reports/research", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ workspace_id: workspaceId, question }),
  });
}

export async function createDecision(
  workspaceId: string,
  title: string,
  description: string,
  priority: "low" | "medium" | "high" | "critical",
  confidence?: number,
) {
  return request<Decision>("/decisions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      workspace_id: workspaceId,
      title,
      description: description || null,
      priority,
      confidence,
    }),
  });
}

export async function createAssumption(
  workspaceId: string,
  name: string,
  description: string,
  confidence?: number,
) {
  return request<Assumption>("/decisions/assumptions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      workspace_id: workspaceId,
      name,
      description: description || null,
      confidence,
    }),
  });
}

export async function createDecisionDependency(
  decisionId: string,
  dependencyType: string,
  assumptionId?: string,
  claimId?: string,
  confidence?: number,
) {
  return request<{ id: string }>(
    `/decisions/${encodeURIComponent(decisionId)}/dependencies`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dependency_type: dependencyType,
        assumption_id: assumptionId,
        claim_id: claimId,
        confidence,
      }),
    },
  );
}

export async function getDecisionAnalysis(decisionId: string) {
  return request<DecisionAnalysis>(
    `/decisions/${encodeURIComponent(decisionId)}/analysis`,
  );
}
// ============================================================
// TIMELINE
// ============================================================

export type TimelineItem = {
  id: string;
  title: string;
  description: string | null;
  event_type: string;
  event_date: string | null;
  document_id: string | null;
  document_title: string | null;
  confidence: number | null;
};

export async function getTimeline(
  workspaceId = NEXUS_CONFIG.WORKSPACE_ID,
) {
  return request<{ events: TimelineItem[]; count?: number }>(
    `/timeline?workspace_id=${encodeURIComponent(workspaceId)}`,
  );
}


// ============================================================
// CONTRADICTIONS
// ============================================================

export type Contradiction = {
  id: string;
  subject: string;
  predicate: string;
  claim_a: string;
  claim_b: string;
  document_a: string | null;
  document_b: string | null;
  confidence: number | null;
  severity: string | null;
};

export async function getContradictions(
  workspaceId = NEXUS_CONFIG.WORKSPACE_ID,
) {
  return request<{
    contradictions: Contradiction[];
    count?: number;
  }>(
    `/contradictions?workspace_id=${encodeURIComponent(workspaceId)}`,
  );
}