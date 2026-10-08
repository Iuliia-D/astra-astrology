type EventCardProps = { date: string; month: string; title: string; kind: string; glyph: string };

export function EventCard({ date, month, title, kind, glyph }: EventCardProps) {
  return (
    <article className="event-card">
      <div className="event-card__date">
        <strong>{date}</strong>
        <span>{month}</span>
      </div>
      <span className="event-card__glyph" aria-hidden="true">
        {glyph}
      </span>
      <div className="event-card__copy">
        <h3>{title}</h3>
        <p>{kind}</p>
      </div>
      <span className="event-card__arrow" aria-hidden="true">
        ↗
      </span>
    </article>
  );
}
