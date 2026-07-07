import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { StatCard } from "@/components/StatCard";
import { getAgentLogs, getApprovals, getKnowledgeDocuments, getTickets } from "@/lib/api";

export default async function AdminPage() {
  const [tickets, approvals, documents, logs] = await Promise.all([
    getTickets(),
    getApprovals(),
    getKnowledgeDocuments(),
    getAgentLogs(),
  ]);

  const pendingApprovals = approvals.filter(
    (approval) => approval.status === "pending",
  );

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-950">
          Admin Dashboard
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          Monitor tickets, approvals, knowledge base, and agent activity.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Tickets" value={tickets.length} helper="Total created" />
        <StatCard
          label="Pending approvals"
          value={pendingApprovals.length}
          helper="Needs admin action"
        />
        <StatCard
          label="KB documents"
          value={documents.length}
          helper="Indexed documents"
        />
        <StatCard
          label="Agent steps"
          value={logs.length}
          helper="Trace log entries"
        />
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {[
          {
            title: "Review Approvals",
            text: "Approve, reject, or request more information for sensitive actions.",
            href: "/admin/approvals",
          },
          {
            title: "Manage Knowledge Base",
            text: "View indexed IT policy documents and reindex the vector store.",
            href: "/admin/knowledge",
          },
          {
            title: "Inspect Agent Trace",
            text: "See how the Supervisor, Triage, RAG, Ticket, and Approval agents acted.",
            href: "/admin/logs",
          },
        ].map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm hover:bg-slate-50"
          >
            <h2 className="font-semibold text-slate-950">{card.title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">{card.text}</p>
          </Link>
        ))}
      </div>
    </AppShell>
  );
}