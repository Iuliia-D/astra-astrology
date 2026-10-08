import type { HTMLAttributes, ReactNode } from 'react';

type CardProps = HTMLAttributes<HTMLElement> & { children: ReactNode; className?: string };

export function Card({ children, className = '', ...props }: CardProps) {
  return (
    <article className={`card ${className}`.trim()} {...props}>
      {children}
    </article>
  );
}

export function GlassCard({ children, className = '', ...props }: CardProps) {
  return (
    <article className={`glass-card ${className}`.trim()} {...props}>
      {children}
    </article>
  );
}
