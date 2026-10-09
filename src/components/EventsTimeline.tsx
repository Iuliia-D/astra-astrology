import { useMemo, useState } from 'react';
import { celestialEvents, formatEventDateParts, formatEventRange } from '../data/events';
import { EventCard } from './ui/EventCard';

const filters = [
  { id: 'all', label: 'Все' },
  { id: 'moon', label: 'Луна' },
  { id: 'retrograde', label: 'Ретроградность' },
  { id: 'eclipses', label: 'Затмения' },
  { id: 'transitions', label: 'Переходы' },
  { id: 'conjunctions', label: 'Соединения' },
] as const;

type FilterId = (typeof filters)[number]['id'];

export function EventsTimeline() {
  const [filter, setFilter] = useState<FilterId>('all');
  const events = useMemo(
    () => celestialEvents.filter((event) => filter === 'all' || event.category === filter),
    [filter],
  );

  return (
    <div className="events-timeline">
      <div className="events-filters" role="group" aria-label="Фильтр событий">
        {filters.map((item) => (
          <button
            type="button"
            key={item.id}
            aria-pressed={filter === item.id}
            onClick={() => setFilter(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>
      <p className="events-timeline__notice">
        Демонстрационная хронология · астрономические даты не рассчитываются
      </p>
      <div className="events-list events-timeline__list" aria-live="polite">
        {events.length ? (
          events.map((event) => {
            const date = formatEventDateParts(event.type === 'period' ? event.end : event.start);
            return (
              <a className="events-timeline__item" href={`/events/${event.id}/`} key={event.id}>
                <EventCard
                  date={date.day}
                  month={date.month}
                  title={event.title}
                  kind={`${event.type === 'period' ? 'Период' : 'Точечное событие'} · демо`}
                  glyph={event.glyph}
                />
                <span className="events-timeline__range">{formatEventRange(event)}</span>
              </a>
            );
          })
        ) : (
          <p className="calendar-empty">В этой категории пока нет демонстрационных событий.</p>
        )}
      </div>
      <a className="text-link events-timeline__calendar-link" href="/calendar/">
        Открыть календарь <span aria-hidden="true">↗</span>
      </a>
    </div>
  );
}
