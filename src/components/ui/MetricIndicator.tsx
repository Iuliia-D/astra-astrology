type MetricIndicatorProps = { label: string; value: string; detail: string; tone?: string };

export function MetricIndicator({ label, value, detail, tone = 'violet' }: MetricIndicatorProps) {
  return (
    <div className="metric-card">
      <span className={`metric-card__icon metric-card__icon--${tone}`} aria-hidden="true">
        ✳
      </span>
      <div>
        <p className="metric-card__label">{label}</p>
        <strong>{value}</strong>
        <p className="metric-card__detail">{detail}</p>
      </div>
    </div>
  );
}
