import { AppShell } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { getTicket } from "@/lib/api";

type PageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function TicketDetailPage({ params }: PageProps) {
  const { id } = await params;
  const ticket = await getTicket(id);

  return (
    <AppShell>
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm text-slate-500">Ticket</p>
            <h1 className="mt-1 text-3xl font-semibold text-slate-950">
              {ticket.ticket_number || ticket.id}
            </h1>
            <p className="mt-2 text-slate-600">{ticket.title}</p>
          </div>

          <Badge tone="info">{ticket.status}</Badge>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-4">
          <Info label="Category" value={ticket.category} />
          <Info label="Priority" value={ticket.priority} />
          <Info label="Urgency" value={ticket.urgency} />
          <Info label="Source" value={ticket.source} />
        </div>

        <div className="mt-8 rounded-2xl bg-slate-50 p-5">
          <h2 className="font-semibold text-slate-950">Description</h2>
          <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">
            {ticket.description}
          </p>
        </div>

        {ticket.servicenow_sys_id ? (
          <div className="mt-6 rounded-2xl border border-slate-200 p-5">
            <h2 className="font-semibold text-slate-950">ServiceNow Metadata</h2>
            <p className="mt-2 text-sm text-slate-600">
              sys_id: {ticket.servicenow_sys_id}
            </p>
          </div>
        ) : null}
      </div>
    </AppShell>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-slate-200 p-4">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 font-medium text-slate-950">{value}</p>
    </div>
  );
}