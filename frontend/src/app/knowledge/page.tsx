"use client";
import { NEXUS_CONFIG } from "@/lib/config";
import { useEffect, useMemo, useState } from "react";

type Entity = {
  id: string;
  label: string;
  type: string;
  description?: string | null;
};

type Edge = {
  id: string;
  source: string;
  target: string;
  label: string;
  confidence?: number | null;
};

type Claim = {
  id: string;
  subject_entity_id?: string | null;
  object_entity_id?: string | null;
  predicate: string;
  object_text?: string | null;
  value_type?: string | null;
  normalized_value?: string | null;
  value_unit?: string | null;
  confidence?: number | null;
};

type GraphResponse = {
  workspace_id: string;
  nodes: Entity[];
  edges: Edge[];
  claims: Claim[];
  counts: {
    nodes: number;
    edges: number;
    claims: number;
  };
};

const WORKSPACE_ID = NEXUS_CONFIG.WORKSPACE_ID;
const API_URL = NEXUS_CONFIG.API_BASE_URL;

export default function KnowledgePage() {
  const [data, setData] = useState<GraphResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [selectedEntity, setSelectedEntity] =
    useState<Entity | null>(null);

  useEffect(() => {
    loadKnowledge();
  }, []);

  async function loadKnowledge() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_URL}/knowledge/graph?workspace_id=${WORKSPACE_ID}`,
        {
          cache: "no-store",
        }
      );

      if (!response.ok) {
        throw new Error(
          `Knowledge API returned ${response.status}`
        );
      }

      const result = await response.json();

      setData(result);
    } catch (err) {
      console.error(err);

      setError(
        "Unable to connect to the NEXUS knowledge service."
      );
    } finally {
      setLoading(false);
    }
  }

  const entities = data?.nodes ?? [];
  const edges = data?.edges ?? [];
  const claims = data?.claims ?? [];

  const entityTypes = useMemo(() => {
    const types = new Set<string>();

    entities.forEach((entity) => {
      if (entity.type) {
        types.add(entity.type);
      }
    });

    return Array.from(types).sort();
  }, [entities]);

  const filteredEntities = useMemo(() => {
    const query = search.trim().toLowerCase();

    return entities.filter((entity) => {
      const matchesSearch =
        !query ||
        entity.label.toLowerCase().includes(query) ||
        entity.type.toLowerCase().includes(query) ||
        (entity.description ?? "")
          .toLowerCase()
          .includes(query);

      const matchesType =
        typeFilter === "ALL" ||
        entity.type === typeFilter;

      return matchesSearch && matchesType;
    });
  }, [entities, search, typeFilter]);

  const meaningfulEntities = useMemo(() => {
    return filteredEntities.filter((entity) => {
      const type = entity.type.toLowerCase();

      return (
        !type.includes("date") &&
        !type.includes("number") &&
        !type.includes("numeric") &&
        !type.includes("unknown")
      );
    });
  }, [filteredEntities]);

  const selectedConnections = useMemo(() => {
    if (!selectedEntity) return [];

    return edges.filter(
      (edge) =>
        edge.source === selectedEntity.id ||
        edge.target === selectedEntity.id
    );
  }, [edges, selectedEntity]);

  const selectedClaims = useMemo(() => {
    if (!selectedEntity) return [];

    return claims.filter(
      (claim) =>
        claim.subject_entity_id === selectedEntity.id ||
        claim.object_entity_id === selectedEntity.id
    );
  }, [claims, selectedEntity]);

  function getEntityName(id: string) {
    return (
      entities.find((entity) => entity.id === id)
        ?.label ?? "Unknown entity"
    );
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-[#07090d] text-white p-8">
        <div className="animate-pulse">
          <div className="h-4 w-40 bg-white/10 rounded mb-5" />
          <div className="h-12 w-72 bg-white/10 rounded mb-4" />
          <div className="h-5 w-[500px] bg-white/10 rounded mb-10" />

          <div className="grid grid-cols-3 gap-4">
            <div className="h-28 bg-white/5 rounded-2xl" />
            <div className="h-28 bg-white/5 rounded-2xl" />
            <div className="h-28 bg-white/5 rounded-2xl" />
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-[#07090d] text-white p-8">
        <div className="max-w-2xl border border-red-500/20 bg-red-500/5 rounded-2xl p-8">
          <p className="text-xs tracking-[0.25em] text-red-400 mb-3">
            KNOWLEDGE SERVICE
          </p>

          <h1 className="text-2xl font-semibold mb-3">
            Knowledge graph unavailable
          </h1>

          <p className="text-slate-400 mb-6">
            {error}
          </p>

          <button
            onClick={loadKnowledge}
            className="px-5 py-3 rounded-xl bg-emerald-300 text-black font-medium hover:bg-emerald-200 transition"
          >
            Retry connection
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#07090d] text-white p-6 md:p-8">
      {/* HEADER */}
      <section className="flex flex-col xl:flex-row xl:items-end xl:justify-between gap-6 mb-8">
        <div>
          <p className="text-xs font-semibold tracking-[0.28em] text-emerald-300 mb-3">
            NEXUS INTELLIGENCE
          </p>

          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight">
            Knowledge
          </h1>

          <p className="text-slate-400 mt-3 max-w-2xl">
            Explore entities, relationships and claims extracted
            from your documents.
          </p>
        </div>

        <div className="flex gap-3">
          <StatCard
            value={data?.counts.nodes ?? 0}
            label="ENTITIES"
          />

          <StatCard
            value={data?.counts.edges ?? 0}
            label="RELATIONS"
          />

          <StatCard
            value={data?.counts.claims ?? 0}
            label="CLAIMS"
          />
        </div>
      </section>

      {/* CONTROLS */}
      <section className="border border-slate-800 bg-[#0b0f15] rounded-2xl p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <input
              value={search}
              onChange={(e) =>
                setSearch(e.target.value)
              }
              placeholder="Search entities, types or descriptions..."
              className="w-full bg-[#080b10] border border-slate-800 focus:border-emerald-300/70 outline-none rounded-xl px-4 py-3 text-sm transition"
            />
          </div>

          <select
            value={typeFilter}
            onChange={(e) =>
              setTypeFilter(e.target.value)
            }
            className="md:w-56 bg-[#080b10] border border-slate-800 rounded-xl px-4 py-3 text-sm outline-none focus:border-emerald-300/70"
          >
            <option value="ALL">
              All entity types
            </option>

            {entityTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>

          <button
            onClick={loadKnowledge}
            className="px-5 py-3 rounded-xl border border-slate-700 hover:border-emerald-300/50 hover:bg-white/5 transition text-sm"
          >
            Refresh
          </button>
        </div>

        <div className="flex items-center justify-between mt-3 text-xs text-slate-500">
          <span>
            Showing {meaningfulEntities.length} meaningful
            entities
          </span>

          <span>
            {edges.length} relationships · {claims.length} claims
          </span>
        </div>
      </section>

      {/* MAIN GRID */}
      <section className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_380px] gap-6">
        {/* GRAPH */}
        <div className="border border-slate-800 bg-[#0b0f15] rounded-2xl overflow-hidden">
          <div className="px-6 py-5 border-b border-slate-800">
            <p className="text-xs tracking-[0.2em] text-emerald-300 mb-2">
              KNOWLEDGE GRAPH
            </p>

            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">
                  Entity network
                </h2>

                <p className="text-sm text-slate-500 mt-1">
                  Select an entity to inspect its connections.
                </p>
              </div>

              <div className="text-right">
                <div className="text-2xl font-semibold">
                  {meaningfulEntities.length}
                </div>

                <div className="text-[10px] tracking-widest text-slate-500">
                  NODES
                </div>
              </div>
            </div>
          </div>

          <GraphCanvas
            entities={meaningfulEntities}
            edges={edges}
            selectedEntity={selectedEntity}
            onSelect={setSelectedEntity}
          />
        </div>

        {/* INSPECTOR */}
        <aside className="border border-slate-800 bg-[#0b0f15] rounded-2xl overflow-hidden">
          <div className="px-6 py-5 border-b border-slate-800">
            <p className="text-xs tracking-[0.2em] text-emerald-300 mb-2">
              ENTITY INSPECTOR
            </p>

            <h2 className="text-xl font-semibold">
              {selectedEntity
                ? selectedEntity.label
                : "Select an entity"}
            </h2>
          </div>

          {!selectedEntity ? (
            <div className="p-8 text-center">
              <div className="w-14 h-14 mx-auto rounded-full border border-slate-700 flex items-center justify-center mb-5 text-emerald-300">
                ◇
              </div>

              <p className="text-slate-300">
                Explore the knowledge network
              </p>

              <p className="text-sm text-slate-500 mt-2">
                Click any node to inspect relationships and
                extracted claims.
              </p>
            </div>
          ) : (
            <div className="p-5 space-y-6">
              <div>
                <span className="inline-flex px-3 py-1 rounded-full bg-emerald-300/10 text-emerald-300 text-xs">
                  {selectedEntity.type}
                </span>

                {selectedEntity.description && (
                  <p className="text-sm text-slate-400 mt-4 leading-6">
                    {selectedEntity.description}
                  </p>
                )}
              </div>

              {/* CONNECTIONS */}
              <div>
                <div className="flex justify-between mb-3">
                  <h3 className="text-sm font-semibold">
                    Connections
                  </h3>

                  <span className="text-xs text-slate-500">
                    {selectedConnections.length}
                  </span>
                </div>

                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {selectedConnections.length === 0 ? (
                    <p className="text-sm text-slate-600">
                      No relationships found.
                    </p>
                  ) : (
                    selectedConnections.map((edge) => {
                      const isSource =
                        edge.source === selectedEntity.id;

                      const otherId = isSource
                        ? edge.target
                        : edge.source;

                      return (
                        <div
                          key={edge.id}
                          className="rounded-xl border border-slate-800 bg-[#080b10] p-3"
                        >
                          <div className="text-sm font-medium">
                            {getEntityName(otherId)}
                          </div>

                          <div className="text-xs text-emerald-300 mt-1">
                            {isSource ? "→" : "←"}{" "}
                            {edge.label}
                          </div>

                          {edge.confidence != null && (
                            <div className="text-[11px] text-slate-600 mt-2">
                              Confidence{" "}
                              {Math.round(
                                edge.confidence * 100
                              )}
                              %
                            </div>
                          )}
                        </div>
                      );
                    })
                  )}
                </div>
              </div>

              {/* CLAIMS */}
              <div>
                <div className="flex justify-between mb-3">
                  <h3 className="text-sm font-semibold">
                    Extracted claims
                  </h3>

                  <span className="text-xs text-slate-500">
                    {selectedClaims.length}
                  </span>
                </div>

                <div className="space-y-2 max-h-72 overflow-y-auto">
                  {selectedClaims.length === 0 ? (
                    <p className="text-sm text-slate-600">
                      No claims linked to this entity.
                    </p>
                  ) : (
                    selectedClaims.map((claim) => (
                      <div
                        key={claim.id}
                        className="rounded-xl border border-slate-800 bg-[#080b10] p-3"
                      >
                        <div className="text-xs text-emerald-300 uppercase tracking-wide">
                          {claim.predicate}
                        </div>

                        <div className="text-sm text-slate-300 mt-2">
                          {claim.object_text ||
                            claim.normalized_value ||
                            "Structured claim"}
                        </div>

                        {claim.value_unit && (
                          <div className="text-xs text-slate-600 mt-1">
                            Unit: {claim.value_unit}
                          </div>
                        )}

                        {claim.confidence != null && (
                          <div className="text-[11px] text-slate-600 mt-2">
                            Confidence{" "}
                            {Math.round(
                              claim.confidence * 100
                            )}
                            %
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}
        </aside>
      </section>

      {/* RELATIONSHIP TABLE */}
      <section className="border border-slate-800 bg-[#0b0f15] rounded-2xl mt-6 overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-800">
          <p className="text-xs tracking-[0.2em] text-emerald-300 mb-2">
            RELATIONSHIP INDEX
          </p>

          <h2 className="text-xl font-semibold">
            Discovered relationships
          </h2>
        </div>

        <div className="max-h-[420px] overflow-auto">
          {edges.length === 0 ? (
            <div className="p-8 text-center text-slate-500">
              No relationships found.
            </div>
          ) : (
            edges.map((edge) => (
              <div
                key={edge.id}
                className="px-6 py-4 border-b border-slate-900 hover:bg-white/[0.02] transition"
              >
                <div className="grid grid-cols-[1fr_auto_1fr] gap-4 items-center">
                  <button
                    onClick={() =>
                      setSelectedEntity(
                        entities.find(
                          (entity) =>
                            entity.id === edge.source
                        ) ?? null
                      )
                    }
                    className="text-left font-medium hover:text-emerald-300 transition truncate"
                  >
                    {getEntityName(edge.source)}
                  </button>

                  <div className="text-center">
                    <div className="text-xs text-emerald-300 whitespace-nowrap">
                      {edge.label}
                    </div>

                    <div className="text-slate-600">
                      →
                    </div>
                  </div>

                  <button
                    onClick={() =>
                      setSelectedEntity(
                        entities.find(
                          (entity) =>
                            entity.id === edge.target
                        ) ?? null
                      )
                    }
                    className="text-left font-medium hover:text-emerald-300 transition truncate"
                  >
                    {getEntityName(edge.target)}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </section>
    </main>
  );
}

function StatCard({
  value,
  label,
}: {
  value: number;
  label: string;
}) {
  return (
    <div className="min-w-[105px] border border-slate-800 bg-[#0b0f15] rounded-2xl px-5 py-4">
      <div className="text-2xl font-semibold">
        {value}
      </div>

      <div className="text-[10px] tracking-widest text-slate-500 mt-1">
        {label}
      </div>
    </div>
  );
}

function GraphCanvas({
  entities,
  edges,
  selectedEntity,
  onSelect,
}: {
  entities: Entity[];
  edges: Edge[];
  selectedEntity: Entity | null;
  onSelect: (entity: Entity) => void;
}) {
  const width = 900;
  const height = 560;

  const visibleIds = new Set(
    entities.map((entity) => entity.id)
  );

  const visibleEdges = edges.filter(
    (edge) =>
      visibleIds.has(edge.source) &&
      visibleIds.has(edge.target)
  );

  const positions = useMemo(() => {
    const result: Record<
      string,
      { x: number; y: number }
    > = {};

    entities.forEach((entity, index) => {
      const angle =
        (index / Math.max(entities.length, 1)) *
        Math.PI *
        2;

      const radius =
        entities.length <= 8
          ? 150
          : Math.min(
              220,
              100 + entities.length * 4
            );

      result[entity.id] = {
        x:
          width / 2 +
          Math.cos(angle) * radius +
          Math.sin(index * 2.4) * 70,

        y:
          height / 2 +
          Math.sin(angle) * radius +
          Math.cos(index * 1.7) * 80,
      };
    });

    return result;
  }, [entities]);

  const connectedIds = new Set<string>();

  if (selectedEntity) {
    visibleEdges.forEach((edge) => {
      if (edge.source === selectedEntity.id) {
        connectedIds.add(edge.target);
      }

      if (edge.target === selectedEntity.id) {
        connectedIds.add(edge.source);
      }
    });
  }

  return (
    <div className="relative overflow-auto bg-[radial-gradient(circle_at_center,rgba(52,211,153,0.06),transparent_45%)]">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full min-w-[760px] h-[560px]"
      >
        <defs>
          <pattern
            id="grid"
            width="32"
            height="32"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 32 0 L 0 0 0 32"
              fill="none"
              stroke="rgba(148,163,184,0.06)"
              strokeWidth="1"
            />
          </pattern>
        </defs>

        <rect
          width="100%"
          height="100%"
          fill="url(#grid)"
        />

        {/* EDGES */}
        {visibleEdges.map((edge) => {
          const source = positions[edge.source];
          const target = positions[edge.target];

          if (!source || !target) return null;

          const highlighted =
            selectedEntity &&
            (edge.source === selectedEntity.id ||
              edge.target === selectedEntity.id);

          return (
            <g key={edge.id}>
              <line
                x1={source.x}
                y1={source.y}
                x2={target.x}
                y2={target.y}
                stroke={
                  highlighted
                    ? "rgba(110,231,183,0.9)"
                    : "rgba(100,116,139,0.35)"
                }
                strokeWidth={
                  highlighted ? 2.5 : 1
                }
              />

              {highlighted && (
                <text
                  x={(source.x + target.x) / 2}
                  y={(source.y + target.y) / 2 - 6}
                  textAnchor="middle"
                  fontSize="9"
                  fill="#6ee7b7"
                >
                  {edge.label}
                </text>
              )}
            </g>
          );
        })}

        {/* NODES */}
        {entities.map((entity) => {
          const position = positions[entity.id];

          const selected =
            selectedEntity?.id === entity.id;

          const connected =
            connectedIds.has(entity.id);

          const faded =
            selectedEntity &&
            !selected &&
            !connected;

          return (
            <g
              key={entity.id}
              transform={`translate(${position.x},${position.y})`}
              onClick={() => onSelect(entity)}
              className="cursor-pointer"
              opacity={faded ? 0.25 : 1}
            >
              <circle
                r={selected ? 28 : 23}
                fill={
                  selected
                    ? "rgba(110,231,183,0.16)"
                    : "rgba(15,23,42,0.95)"
                }
                stroke={
                  selected || connected
                    ? "#6ee7b7"
                    : "rgba(100,116,139,0.7)"
                }
                strokeWidth={
                  selected ? 2.5 : 1.2
                }
              />

              <circle
                r="5"
                fill="#6ee7b7"
              />

              <text
                y="40"
                textAnchor="middle"
                fill="white"
                fontSize="11"
                fontWeight="600"
              >
                {truncate(entity.label, 24)}
              </text>

              <text
                y="54"
                textAnchor="middle"
                fill="#64748b"
                fontSize="8"
              >
                {truncate(entity.type, 18)}
              </text>
            </g>
          );
        })}
      </svg>

      {entities.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-slate-400">
              No graph entities found
            </div>

            <div className="text-sm text-slate-600 mt-2">
              Upload and process documents to populate NEXUS.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function truncate(
  value: string,
  length: number
) {
  if (value.length <= length) return value;

  return value.slice(0, length - 1) + "…";
}
