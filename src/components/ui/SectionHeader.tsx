import type { ReactNode } from 'react';

export function SectionHeader({
  label,
  title,
  children,
}: {
  label: string;
  title: string;
  children?: ReactNode;
}) {
  return (
    <div className="section-heading">
      <div>
        <p className="eyebrow">{label}</p>
        <h2>{title}</h2>
      </div>
      {children && <div className="section-heading__aside">{children}</div>}
    </div>
  );
}
