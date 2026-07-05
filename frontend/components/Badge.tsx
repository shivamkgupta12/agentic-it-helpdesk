import { statusClass } from "@/lib/utils";

export function Badge({ children }: { children: React.ReactNode }) {
  const value = String(children);

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ring-1 ${statusClass(
        value
      )}`}
    >
      {children}
    </span>
  );
}