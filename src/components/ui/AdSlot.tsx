export function AdSlot({ enabled = false }: { enabled?: boolean }) {
  if (!enabled) return null;
  return <aside className="ad-slot" aria-label="Рекламное место" />;
}
