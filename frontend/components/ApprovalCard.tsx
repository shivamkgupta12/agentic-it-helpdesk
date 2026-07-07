"use client";

import { useState } from "react";
import type { Approval } from "@/types";
import { approveRequest, rejectRequest, requestMoreInfo } from "@/lib/api";
import { Badge } from "@/components/Badge";

type ApprovalCardProps = {
  approval: Approval;
};

export function ApprovalCard({ approval }: ApprovalCardProps) {
  const [comment, setComment] = useState("");
  const [status, setStatus] = useState(approval.status);
  const [result, setResult] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleAction(action: "approve" | "reject" | "more-info") {
    setIsLoading(true);
    setResult(null);

    try {
      if (action === "approve") {
        const response = await approveRequest(approval.id, comment);
        setStatus(response.status);
        setResult(
          response.ticket_number
            ? `${response.message} Ticket: ${response.ticket_number}`
            : response.message,
        );
      }

      if (action === "reject") {
        const response = await rejectRequest(approval.id, comment);
        setStatus(response.status);
        setResult(response.message);
      }

      if (action === "more-info") {
        const response = await requestMoreInfo(approval.id, comment);
        setStatus(response.status);
        setResult(response.message);
      }
    } catch (error) {
      setResult(error instanceof Error ? error.message : "Action failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="font-semibold text-slate-950">{approval.action_type}</h2>
          <p className="mt-1 text-xs text-slate-500">Approval ID: {approval.id}</p>
        </div>
        <Badge tone={status === "pending" ? "warning" : "default"}>{status}</Badge>
      </div>

      <div className="mt-4 rounded-2xl bg-slate-50 p-4">
        <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">
          {approval.reason}
        </p>
      </div>

      {status === "pending" ? (
        <div className="mt-4">
          <textarea
            value={comment}
            onChange={(event) => setComment(event.target.value)}
            placeholder="Admin comment..."
            className="min-h-24 w-full rounded-2xl border border-slate-300 p-3 text-sm outline-none focus:border-slate-950"
          />

          <div className="mt-3 flex flex-wrap gap-2">
            <button
              disabled={isLoading}
              onClick={() => void handleAction("approve")}
              className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
            >
              Approve
            </button>
            <button
              disabled={isLoading}
              onClick={() => void handleAction("reject")}
              className="rounded-full bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700 disabled:opacity-50"
            >
              Reject
            </button>
            <button
              disabled={isLoading}
              onClick={() => void handleAction("more-info")}
              className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
            >
              Request more info
            </button>
          </div>
        </div>
      ) : null}

      {result ? (
        <div className="mt-4 rounded-2xl bg-blue-50 p-3 text-sm text-blue-700">
          {result}
        </div>
      ) : null}
    </div>
  );
}