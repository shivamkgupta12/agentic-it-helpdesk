import type {
  AgentLog,
  Approval,
  ChatResponse,
  KnowledgeDocument,
  Ticket,
} from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const error = await response.json();
      message = error.detail || message;
    } catch {
      // Keep fallback message.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function sendChatMessage(params: {
  message: string;
  conversationId?: string | null;
  userEmail?: string;
}): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({
      message: params.message,
      conversation_id: params.conversationId || null,
      user_email: params.userEmail || "employee@example.com",
    }),
  });
}

export async function getTickets(userEmail?: string): Promise<Ticket[]> {
  const query = userEmail ? `?user_email=${encodeURIComponent(userEmail)}` : "";
  return request<Ticket[]>(`/tickets${query}`);
}

export async function getTicket(id: string): Promise<Ticket> {
  return request<Ticket>(`/tickets/${id}`);
}

export async function getApprovals(status?: string): Promise<Approval[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request<Approval[]>(`/approvals${query}`);
}

export async function approveRequest(
  approvalId: string,
  adminComment: string,
): Promise<{
  approval_id: string;
  status: string;
  message: string;
  ticket_id?: string | null;
  ticket_number?: string | null;
}> {
  return request(`/approvals/${approvalId}/approve`, {
    method: "POST",
    body: JSON.stringify({
      admin_comment: adminComment,
    }),
  });
}

export async function rejectRequest(
  approvalId: string,
  adminComment: string,
): Promise<{
  approval_id: string;
  status: string;
  message: string;
  ticket_id?: string | null;
  ticket_number?: string | null;
}> {
  return request(`/approvals/${approvalId}/reject`, {
    method: "POST",
    body: JSON.stringify({
      admin_comment: adminComment,
    }),
  });
}

export async function requestMoreInfo(
  approvalId: string,
  adminComment: string,
): Promise<{
  approval_id: string;
  status: string;
  message: string;
}> {
  return request(`/approvals/${approvalId}/request-more-info`, {
    method: "POST",
    body: JSON.stringify({
      admin_comment: adminComment,
    }),
  });
}

export async function getKnowledgeDocuments(): Promise<KnowledgeDocument[]> {
  return request<KnowledgeDocument[]>("/knowledge");
}

export async function reindexKnowledgeBase(): Promise<{
  status: string;
  source_document_count: number;
  chunk_count: number;
}> {
  return request("/knowledge/reindex", {
    method: "POST",
  });
}

export async function getAgentLogs(): Promise<AgentLog[]> {
  return request<AgentLog[]>("/agent-logs");
}