import { AppShell } from "@/components/AppShell";
import { AgentTrace } from "@/components/AgentTrace";
import { getAgentLogs } from "@/lib/api";

export default async function AgentLogsPage() {
  const logs = await getAgentLogs();

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-950">
          Agent Trace Logs
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          Inspect how the multi-agent workflow handled each request.
        </p>
      </div>

      <AgentTrace logs={logs} />
    </AppShell>
  );
}