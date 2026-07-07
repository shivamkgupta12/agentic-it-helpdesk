import type { SourceCitation } from "@/types";

type SourceListProps = {
  sources: SourceCitation[];
};

export function SourceList({ sources }: SourceListProps) {
  if (!sources.length) return null;

  const uniqueSources = sources.filter(
    (source, index, self) =>
      index === self.findIndex((item) => item.title === source.title),
  );

  return (
    <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
      <p className="text-sm font-semibold text-slate-900">Sources used</p>
      <div className="mt-2 space-y-2">
        {uniqueSources.map((source) => (
          <div key={`${source.title}-${source.chunk_id}`} className="text-sm">
            <p className="font-medium text-slate-700">{source.title}</p>
            <p className="text-xs text-slate-500">{source.source}</p>
          </div>
        ))}
      </div>
    </div>
  );
}