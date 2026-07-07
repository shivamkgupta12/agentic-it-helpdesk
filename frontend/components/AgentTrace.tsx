import type { AgentLog } from "@/types";
import { Badge } from "@/components/Badge";

type AgentTraceProps = {
  logs: AgentLog[];
};

export function AgentTrace({ logs }: AgentTraceProps) {
  return (
    <div className="space-y-4">
      {logs.map((log, index) => (
        <div
          key={log.id}
          className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-950 text-xs font-semibold text-white">
                  {index + 1}
                </div>
                <h2 className="font-semibold text-slate-950">
                  {log.agent_name}
                </h2>
              </div>
              <p className="mt-2 text-xs text-slate-500">
                Conversation: {log.conversation_id || "N/A"}
              </p>
            </div>
            <Badge>{new Date(log.created_at).toLocaleString()}</Badge>
          </div>

          {log.input_summary ? (
            <div className="mt-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Input
              </p>
              <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                {log.input_summary}
              </p>
            </div>
          ) : null}

          {log.output_summary ? (
            <div className="mt-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Output
              </p>
              <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                {log.output_summary}
              </p>
            </div>
          ) : null}

          {log.metadata_json ? (
            <details className="mt-4 rounded-2xl bg-slate-50 p-4">
              <summary className="cursor-pointer text-sm font-medium text-slate-700">
                Metadata
              </summary>
              <pre className="mt-3 overflow-auto text-xs text-slate-600">
                {formatJson(log.metadata_json)}
              </pre>
            </details>
          ) : null}
        </div>
      ))}

      {!logs.length ? (
        <div className="rounded-3xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
          No agent logs found yet.
        </div>
      ) : null}
    </div>
  );
}

function formatJson(value: string) {
  try {
    return JSON.stringify(JSON.parse(value), null, 2);
  } catch {
    return value;
  }
}