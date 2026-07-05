import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "danger";
};

export function Button({
  className,
  variant = "primary",
  ...props
}: ButtonProps) {
  const styles = {
    primary: "bg-slate-950 text-white hover:bg-slate-800",
    secondary: "bg-white text-slate-900 ring-1 ring-slate-200 hover:bg-slate-50",
    danger: "bg-red-600 text-white hover:bg-red-700",
  };

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50",
        styles[variant],
        className
      )}
      {...props}
    />
  );
}