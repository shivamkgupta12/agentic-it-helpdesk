type BadgeProps = {
  children: React.ReactNode;
  tone?: "default" | "success" | "warning" | "danger" | "info";
};

const toneClassMap = {
  default: "bg-slate-100 text-slate-700 ring-slate-200",
  success: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  warning: "bg-amber-50 text-amber-700 ring-amber-200",
  danger: "bg-rose-50 text-rose-700 ring-rose-200",
  info: "bg-blue-50 text-blue-700 ring-blue-200",
};

export function Badge({ children, tone = "default" }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ring-1 ${toneClassMap[tone]}`}
    >
      {children}
    </span>
  );
}