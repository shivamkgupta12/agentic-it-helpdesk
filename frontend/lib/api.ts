import type {
  AgentLog,
  Approval,
  ApprovalDecisionResponse,
  ChatRequest,
  ChatResponse,
  KnowledgeDocument,
  Ticket,
  TicketStatus,
} from "@/types/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `API request failed: ${response.status} ${response.statusText} ${errorText}`
    );
  }

  return response.json() as Promise<T>;
}

export const api = {
  sendChatMessage(payload: ChatRequest) {
    return request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  getTickets(userEmail?: string) {
    const query = userEmail ? `?user_email=${encodeURIComponent(userEmail)}` : "";
    return request<Ticket[]>(`/tickets${query}`);
  },

  getTicket(ticketId: string) {
    return request<Ticket>(`/tickets/${ticketId}`);
  },

  getTicketStatus(ticketNumber: string) {
    return request<TicketStatus>(`/tickets/status/${ticketNumber}`);
  },

  addTicketComment(ticketNumber: string, comment: string, internal = false) {
    return request<Ticket>(`/tickets/${ticketNumber}/comments`, {
      method: "POST",
      body: JSON.stringify({ comment, internal }),
    });
  },

  getApprovals(status?: string) {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    return request<Approval[]>(`/approvals${query}`);
  },

  approveRequest(approvalId: string, adminComment: string) {
    return request<ApprovalDecisionResponse>(
      `/approvals/${approvalId}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ admin_comment: adminComment }),
      }
    );
  },

  rejectRequest(approvalId: string, adminComment: string) {
    return request<ApprovalDecisionResponse>(
      `/approvals/${approvalId}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ admin_comment: adminComment }),
      }
    );
  },

  requestMoreInfo(approvalId: string, adminComment: string) {
    return request<ApprovalDecisionResponse>(
      `/approvals/${approvalId}/request-more-info`,
      {
        method: "POST",
        body: JSON.stringify({ admin_comment: adminComment }),
      }
    );
  },

  getKnowledgeDocuments() {
    return request<KnowledgeDocument[]>("/knowledge");
  },

  reindexKnowledgeBase() {
    return request<{
      status: string;
      source_document_count: number;
      chunk_count: number;
    }>("/knowledge/reindex", {
      method: "POST",
    });
  },

  getAgentLogs() {
    return request<AgentLog[]>("/agent-logs");
  },
};