"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { getKnowledgeDocuments, reindexKnowledgeBase } from "@/lib/api";
import type { KnowledgeDocument } from "@/types";

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function loadDocuments() {
    const docs = await getKnowledgeDocuments();
    setDocuments(docs);
  }

  async function handleReindex() {
    setIsLoading(true);
    setMessage(null);

    try {
      const result = await reindexKnowledgeBase();
      setMessage(
        `Reindexed ${result.source_document_count} documents into ${result.chunk_count} chunks.`,
      );
      await loadDocuments();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Reindex failed.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadDocuments();
  }, []);

  return (
    <AppShell>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-950">
            Knowledge Base
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Internal IT documents indexed into ChromaDB for RAG.
          </p>
        </div>

        <button
          onClick={() => void handleReindex()}
          disabled={isLoading}
          className="rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-50"
        >
          {isLoading ? "Reindexing..." : "Reindex KB"}
        </button>
      </div>

      {message ? (
        <div className="mb-4 rounded-2xl bg-blue-50 p-4 text-sm text-blue-700">
          {message}
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2">
        {documents.map((doc) => (
          <div
            key={doc.id}
            className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="font-semibold text-slate-950">{doc.title}</h2>
                <p className="mt-1 text-sm text-slate-500">{doc.filename}</p>
              </div>
              <Badge tone="success">{doc.status}</Badge>
            </div>

            <p className="mt-4 text-sm text-slate-600">
              Chunks indexed: {doc.chunk_count}
            </p>
            <p className="mt-1 text-sm text-slate-600">
              Source type: {doc.source_type}
            </p>
          </div>
        ))}

        {!documents.length ? (
          <div className="rounded-3xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500 md:col-span-2">
            No knowledge documents found. Click Reindex KB.
          </div>
        ) : null}
      </div>
    </AppShell>
  );
}