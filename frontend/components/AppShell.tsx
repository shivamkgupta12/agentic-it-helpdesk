import Link from "next/link";

type AppShellProps = {
  children: React.ReactNode;
};

const navItems = [
  { href: "/", label: "Home" },
  { href: "/chat", label: "User Chat" },
  { href: "/tickets", label: "My Tickets" },
  { href: "/admin", label: "Admin" },
  { href: "/admin/approvals", label: "Approvals" },
  { href: "/admin/knowledge", label: "Knowledge Base" },
  { href: "/admin/logs", label: "Agent Trace" },
];

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-950 text-sm font-bold text-white">
              AI
            </div>
            <div>
              <p className="font-semibold text-slate-950">Agentic IT Helpdesk</p>
              <p className="text-xs text-slate-500">Multi-Agent IT Support System</p>
            </div>
          </Link>

          <nav className="hidden items-center gap-1 md:flex">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-full px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-950"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
    </div>
  );
}