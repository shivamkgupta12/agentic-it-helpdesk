import Link from "next/link";
import type { Ticket } from "@/types";
import { Badge } from "@/components/Badge";

type TicketTableProps = {
  tickets: Ticket[];
};

function statusTone(status: string): "default" | "success" | "warning" | "info" {
  const normalized = status.toLowerCase();

  if (normalized.includes("resolved") || normalized.includes("closed")) {
    return "success";
  }

  if (normalized.includes("pending") || normalized.includes("hold")) {
    return "warning";
  }

  if (normalized.includes("open") || normalized.includes("new")) {
    return "info";
  }

  return "default";
}

export function TicketTable({ tickets }: TicketTableProps) {
  return (
    <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Ticket
            </th>
            <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Category
            </th>
            <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Priority
            </th>
            <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Status
            </th>
            <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Source
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {tickets.map((ticket) => (
            <tr key={ticket.id} className="hover:bg-slate-50">
              <td className="px-5 py-4">
                <Link
                  href={`/tickets/${ticket.id}`}
                  className="font-medium text-slate-950 hover:underline"
                >
                  {ticket.ticket_number || ticket.id}
                </Link>
                <p className="mt-1 text-sm text-slate-500">{ticket.title}</p>
              </td>
              <td className="px-5 py-4 text-sm text-slate-700">
                {ticket.category}
              </td>
              <td className="px-5 py-4 text-sm text-slate-700">
                {ticket.priority}
              </td>
              <td className="px-5 py-4">
                <Badge tone={statusTone(ticket.status)}>{ticket.status}</Badge>
              </td>
              <td className="px-5 py-4 text-sm text-slate-700">
                {ticket.source}
              </td>
            </tr>
          ))}

          {!tickets.length ? (
            <tr>
              <td colSpan={5} className="px-5 py-8 text-center text-sm text-slate-500">
                No tickets found.
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}