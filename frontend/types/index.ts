export type SourceCitation = {
  title: string;
  source: string;
  chunk_id?: string | null;
};

export type ChatResponse = {
  conversation_id: string;
  response: string;
  ticket_number?: string | null;
  requires_approval: boolean;
  approval_id?: string | null;
  sources: SourceCitation[];
};

export type Ticket = {
  id: string;
  ticket_number?: string | null;
  title: string;
  description: string;
  category: string;
  priority: string;
  urgency: string;
  status: string;
  source: string;
  created_at: string;
  updated_at: string;
  servicenow_sys_id?: string | null;
  conversation_id?: string | null;
};

export type Approval = {
  id: string;
  ticket_id?: string | null;
  conversation_id?: string | null;
  requested_by_user_id: string;
  action_type: string;
  reason: string;
  status: string;
  admin_comment?: string | null;
  created_at: string;
  updated_at: string;
};

export type KnowledgeDocument = {
  id: string;
  filename: string;
  title: string;
  source_type: string;
  status: string;
  chunk_count: number;
  created_at: string;
};

export type AgentLog = {
  id: string;
  conversation_id?: string | null;
  agent_name: string;
  input_summary?: string | null;
  output_summary?: string | null;
  metadata_json?: string | null;
  created_at: string;
};