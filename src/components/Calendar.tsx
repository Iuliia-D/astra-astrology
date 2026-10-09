import type { CelestialEvent } from '../types/astronomy';

type CalendarProps = {
  year: number;
  month: number;
  currentDay: number;
  eventDays?: number[];
  events?: readonly CelestialEvent[];
  currentDate?: string;
  selectedDate?: string;
};

const weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
const monthNames = [
  'ЯНВАРЬ',
  'ФЕВРАЛЬ',
  'МАРТ',
  'АПРЕЛЬ',
  'МАЙ',
  'ИЮНЬ',
  'ИЮЛЬ',
  'АВГУСТ',
  'СЕНТЯБРЬ',
  'ОКТЯБРЬ',
  'НОЯБРЬ',
  'ДЕКАБРЬ',
];

export function Calendar({
  year,
  month,
  currentDay,
  eventDays = [],
  events = [],
  currentDate,
  selectedDate,
}: CalendarProps) {
  const dayCount = new Date(Date.UTC(year, month + 1, 0)).getUTCDate();
  const mondayOffset = (new Date(Date.UTC(year, month, 1)).getUTCDay() + 6) % 7;
  const cellCount = Math.ceil((mondayOffset + dayCount) / 7) * 7;
  const days = Array.from({ length: cellCount }, (_, index) => {
    const day = index - mondayOffset + 1;
    return day > 0 && day <= dayCount ? day : null;
  });

  return (
    <div className="month-card">
      <div className="month-card__top">
        <span>{monthNames[month]}</span>
        <span>
          {year}{' '}
          <span className="month-arrows" aria-hidden="true">
            ‹ / ›
          </span>
        </span>
      </div>
      <div
        className="month-grid"
        role="grid"
        aria-label={`Календарь событий ${monthNames[month].toLowerCase()} ${year}`}
      >
        {weekdays.map((day) => (
          <span className="month-grid__weekday" key={day} role="columnheader">
            {day}
          </span>
        ))}
        {days.map((day, index) => {
          const dateKey = day
            ? `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
            : '';
          const dayEvents = events.filter(
            (event) => event.start === dateKey || event.end === dateKey,
          );
          const hasEvent = day !== null && (eventDays.includes(day) || dayEvents.length > 0);
          if (day === null)
            return <span className="month-grid__day" key={index} aria-hidden="true" />;

          return (
            <a
              className={`month-grid__day ${day === currentDay && currentDate === dateKey ? 'is-today' : ''} ${dateKey === selectedDate ? 'is-selected' : ''} ${hasEvent ? 'has-event' : ''}`}
              key={index}
              role="gridcell"
              href={`/calendar/?date=${dateKey}`}
              aria-current={day === currentDay && currentDate === dateKey ? 'date' : undefined}
              aria-label={`${day} ${monthNames[month].toLowerCase()}${dayEvents.length ? `, ${dayEvents.map((event) => event.title).join(', ')}` : hasEvent ? ', событие' : ''}`}
            >
              {day}
              {hasEvent && <i aria-hidden="true" />}
            </a>
          );
        })}
      </div>
      <div className="month-legend">
        <span>
          <i className="legend-dot legend-dot--moon" />
          Луна
        </span>
        <span>
          <i className="legend-dot legend-dot--planet" />
          Планетарные события
        </span>
      </div>
    </div>
  );
}
