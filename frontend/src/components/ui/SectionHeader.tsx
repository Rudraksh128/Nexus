export default function SectionHeader({
    eyebrow,
    title,
    description,
  }: {
    eyebrow?: string;
    title: string;
    description?: string;
  }) {
    return (
      <div>
        {eyebrow && (
          <div className="mb-2 text-[10px] font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
            {eyebrow}
          </div>
        )}
  
        <h2 className="text-xl font-semibold tracking-tight">
          {title}
        </h2>
  
        {description && (
          <p className="mt-1 text-sm text-[var(--muted)]">
            {description}
          </p>
        )}
      </div>
    );
  }