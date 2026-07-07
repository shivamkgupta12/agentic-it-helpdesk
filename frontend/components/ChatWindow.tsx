"use client";

import { useState } from "react";
import { sendChatMessage } from "@/lib/api";
import type { ChatResponse, SourceCitation } from "@/types";
import { Badge } from "@/components/Badge";
import { SourceList } from "@/components/SourceList";

type Message = {
  role: "user" | "assistant";
  content: string;
  ticketNumber?: string | null;
  approvalId?: string | null;
  requiresApproval?: boolean;
  sources?: SourceCitation[];
};

const demoPrompts = [
  "My VPN keeps disconnecting and I cannot access the internal dashboard.",
  "I tried the VPN troubleshooting steps but it is still disconnecting. Please create a ticket.",
  "I forgot my password. Can you reset it?",
  "I need Figma installed on my laptop.",
  "What is the status of my ticket INC0010003?",
];

export function ChatWindow() {
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! Describe your IT issue. I can troubleshoot, search internal docs, create tickets, and route sensitive actions for approval.",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);

  async function submitMessage(messageText: string) {
    const trimmed = messageText.trim();
    if (!trimmed || isLoading) return;

    setInput("");
    setIsLoading(true);

    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: trimmed,
      },
    ]);

    try {
      const response: ChatResponse = await sendChatMessage({
        message: trimmed,
        conversationId,
      });

      setConversationId(response.conversation_id);

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: response.response,
          ticketNumber: response.ticket_number,
          approvalId: response.approval_id,
          requiresApproval: response.requires_approval,
          sources: response.sources,
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? `Error: ${error.message}`
              : "Something went wrong.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
      <section className="rounded-3xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 p-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h1 className="text-xl font-semibold text-slate-950">
                Employee IT Chat
              </h1>
              <p className="text-sm text-slate-500">
                Multi-agent support workflow with RAG, tickets, and approvals.
              </p>
            </div>
            <Badge tone="success">Live Backend</Badge>
          </div>
        </div>

        <div className="h-[560px] space-y-4 overflow-y-auto p-5">
          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-3xl rounded-2xl p-4 text-sm leading-6 ${
                  message.role === "user"
                    ? "bg-slate-950 text-white"
                    : "bg-slate-50 text-slate-800"
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>

                {message.ticketNumber ? (
                  <div className="mt-4">
                    <Badge tone="success">Ticket: {message.ticketNumber}</Badge>
                  </div>
                ) : null}

                {message.requiresApproval ? (
                  <div className="mt-4">
                    <Badge tone="warning">
                      Approval required
                      {message.approvalId ? `: ${message.approvalId}` : ""}
                    </Badge>
                  </div>
                ) : null}

                {message.sources ? <SourceList sources={message.sources} /> : null}
              </div>
            </div>
          ))}

          {isLoading ? (
            <div className="flex justify-start">
              <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">
                Agents are working...
              </div>
            </div>
          ) : null}
        </div>

        <form
          className="border-t border-slate-200 p-5"
          onSubmit={(event) => {
            event.preventDefault();
            void submitMessage(input);
          }}
        >
          <div className="flex gap-3">
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Describe an IT issue..."
              className="min-w-0 flex-1 rounded-2xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-slate-950"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Send
            </button>
          </div>
        </form>
      </section>

      <aside className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="font-semibold text-slate-950">Demo prompts</h2>
        <div className="mt-4 space-y-3">
          {demoPrompts.map((prompt) => (
            <button
              key={prompt}
              onClick={() => void submitMessage(prompt)}
              className="w-full rounded-2xl border border-slate-200 p-3 text-left text-sm text-slate-700 hover:bg-slate-50"
            >
              {prompt}
            </button>
          ))}
        </div>
      </aside>
    </div>
  );
}