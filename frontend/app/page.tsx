import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { Badge } from "@/components/Badge";

export default function HomePage() {
  return (
    <AppShell>
      <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
        <div>
          <Badge tone="info">Enterprise AI Portfolio Project</Badge>

          <h1 className="mt-6 max-w-4xl text-5xl font-semibold tracking-tight text-slate-950">
            Agentic IT Helpdesk for automated enterprise support.
          </h1>

          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
            A production-style multi-agent IT support system using LangGraph,
            Azure OpenAI, RAG, human approval workflows, ServiceNow integration,
            and a full-stack SaaS-style interface.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/chat"
              className="rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-sm hover:bg-slate-800"
            >
              Try employee chat
            </Link>
            <Link
              href="/admin"
              className="rounded-full border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-100"
            >
              View admin dashboard
            </Link>
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-semibold text-slate-900">Workflow Preview</p>

          <div className="mt-5 space-y-3">
            {[
              "Supervisor Agent routes the workflow",
              "Triage Agent classifies issue and risk",
              "Knowledge Agent retrieves internal docs",
              "Resolution Agent suggests safe steps",
              "Ticket Agent creates ServiceNow incident",
              "Human Approval Agent pauses sensitive actions",
              "Summary Agent creates user/admin notes",
            ].map((item, index) => (
              <div
                key={item}
                className="flex items-center gap-3 rounded-2xl bg-slate-50 p-3"
              >
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-950 text-xs font-semibold text-white">
                  {index + 1}
                </div>
                <p className="text-sm text-slate-700">{item}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mt-12 grid gap-4 md:grid-cols-3">
        {[
          {
            title: "RAG + Citations",
            text: "Answers are grounded in internal IT policy and troubleshooting documents.",
          },
          {
            title: "ServiceNow Ready",
            text: "Supports real ServiceNow incidents and local mock fallback mode.",
          },
          {
            title: "Human Approval",
            text: "Sensitive requests pause for admin review before tickets are created.",
          },
        ].map((card) => (
          <div
            key={card.title}
            className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <h2 className="font-semibold text-slate-950">{card.title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">{card.text}</p>
          </div>
        ))}
      </section>
    </AppShell>
  );
}