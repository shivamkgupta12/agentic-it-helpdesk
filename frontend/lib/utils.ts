import clsx from "clsx";

export function cn(...classes: Array<string | undefined | null | false>) {
  return clsx(classes);
}

export function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("en-AU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function statusClass(status: string) {
  const normalized = status.toLowerCase();

  if (["open", "new", "pending"].includes(normalized)) {
    return "bg-blue-50 text-blue-700 ring-blue-200";
  }

  if (["approved", "resolved", "closed"].includes(normalized)) {
    return "bg-emerald-50 text-emerald-700 ring-emerald-200";
  }

  if (["rejected", "critical"].includes(normalized)) {
    return "bg-red-50 text-red-700 ring-red-200";
  }

  if (["needs_more_info", "on hold"].includes(normalized)) {
    return "bg-amber-50 text-amber-700 ring-amber-200";
  }

  return "bg-slate-50 text-slate-700 ring-slate-200";
}