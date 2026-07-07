import { AppShell } from "@/components/AppShell";
import { ApprovalCard } from "@/components/ApprovalCard";
import { getApprovals } from "@/lib/api";

export default async function ApprovalsPage() {
  const approvals = await getApprovals();

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-950">
          Approval Requests
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          Review sensitive actions such as password resets and access changes.
        </p>
      </div>

      <div className="space-y-4">
        {approvals.map((approval) => (
          <ApprovalCard key={approval.id} approval={approval} />
        ))}

        {!approvals.length ? (
          <div className="rounded-3xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
            No approval requests found.
          </div>
        ) : null}
      </div>
    </AppShell>
  );
}