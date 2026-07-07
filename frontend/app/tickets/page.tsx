import { AppShell } from "@/components/AppShell";
import { TicketTable } from "@/components/TicketTable";
import { getTickets } from "@/lib/api";

export default async function TicketsPage() {
  const tickets = await getTickets("employee@example.com");

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-950">My Tickets</h1>
        <p className="mt-2 text-sm text-slate-500">
          Tickets created by the AI support workflow.
        </p>
      </div>

      <TicketTable tickets={tickets} />
    </AppShell>
  );
}