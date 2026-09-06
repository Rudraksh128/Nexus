type MetricCardProps = {
    label: string;
    value: number | string;
    detail?: string;
  };
  
  export default function MetricCard({
    label,
    value,
    detail,
  }: MetricCardProps) {
    return (
      <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-5">
        <div className="text-xs uppercase tracking-[0.14em] text-[var(--muted-2)]">
          {label}
        </div>
  
        <div className="mt-3 text-3xl font-semibold tracking-tight">
          {value}
        </div>
  
        {detail && (
          <div className="mt-2 text-xs text-[var(--muted)]">
            {detail}
          </div>
        )}
      </div>
    );
  }