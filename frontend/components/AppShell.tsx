import Link from "next/link";
import { Bot, ClipboardList, Home, LockKeyhole, ScrollText, Settings, Upload } from "lucide-react";

const navItems = [
  { href: "/", label: "Home", icon: Home },
  { href: "/chat", label: "User Chat", icon: Bot },
  { href: "/tickets", label: "My Tickets", icon: ClipboardList },
  { href: "/admin", label: "Admin", icon: Settings },
  { href: "/admin/approvals", label: "Approvals", icon: LockKeyhole },
  { href: "/admin/knowledge", label: "Knowledge", icon: Upload },
  { href: "/admin/logs", label: "Agent Logs", icon: ScrollText },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-slate-200 bg-white p-6 lg:block">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
            Portfolio Project
          </p>
          <h1 className="mt-2 text-xl font-bold text-slate-950">
            Agentic IT Helpdesk
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Multi-agent AI support automation with RAG, approvals, and ServiceNow.
          </p>
        </div>

        <nav className="mt-8 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 hover:text-slate-950"
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-6 left-6 right-6 rounded-2xl bg-slate-950 p-4 text-white">
          <p className="text-sm font-semibold">Demo Mode</p>
          <p className="mt-1 text-xs text-slate-300">
            Employee: employee@example.com
            <br />
            Admin: admin@example.com
          </p>
        </div>
      </aside>

      <main className="lg:pl-72">
        <div className="mx-auto max-w-7xl p-5 lg:p-8">{children}</div>
      </main>
    </div>
  );
}