import { useEffect, useMemo, useState } from 'react';
import {
  celestialEvents,
  formatEventDate,
  formatEventDateParts,
  formatEventRange,
} from '../data/events';
import { EventCard } from './ui/EventCard';
import { Calendar } from './Calendar';

type CalendarExplorerProps = { initialToday: string };
type CalendarView = 'month' | 'list';

function dateAtNoon(date: string) {
  return new Date(`${date}T12:00:00`);
}

export function CalendarExplorer({ initialToday }: CalendarExplorerProps) {
  const [today, setToday] = useState(initialToday);
  const [selectedDate, setSelectedDate] = useState(initialToday);
  const [visibleMonth, setVisibleMonth] = useState(() => dateAtNoon(initialToday));
  const [view, setView] = useState<CalendarView>('month');

  useEffect(() => {
    const now = new Date();
    const localToday = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    setToday(localToday);
    const queryDate = new URLSearchParams(window.location.search).get('date');
    const selected = queryDate && /^\d{4}-\d{2}-\d{2}$/.test(queryDate) ? queryDate : localToday;
    const parsed = dateAtNoon(selected);
    if (!Number.isNaN(parsed.valueOf())) {
      setSelectedDate(selected);
      setVisibleMonth(parsed);
    }
  }, []);

  const year = visibleMonth.getFullYear();
  const month = visibleMonth.getMonth();
  const monthStart = `${year}-${String(month + 1).padStart(2, '0')}-01`;
  const monthEnd = `${year}-${String(month + 1).padStart(2, '0')}-${String(new Date(year, month + 1, 0).getDate()).padStart(2, '0')}`;
  const monthEvents = useMemo(
    () => celestialEvents.filter((event) => event.start <= monthEnd && event.end >= monthStart),
    [monthEnd, monthStart],
  );
  const selectedEvents = celestialEvents.filter(
    (event) => event.start <= selectedDate && event.end >= selectedDate,
  );
  const currentDate = today;
  const currentDay =
    currentDate.slice(0, 7) === `${year}-${String(month + 1).padStart(2, '0')}`
      ? Number(currentDate.slice(8, 10))
      : -1;

  function moveMonth(offset: number) {
    setVisibleMonth(
      (current) => new Date(current.getFullYear(), current.getMonth() + offset, 1, 12),
    );
  }

  function goToToday() {
    const now = new Date();
    const localToday = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    setToday(localToday);
    setSelectedDate(localToday);
    setVisibleMonth(dateAtNoon(localToday));
  }

  return (
    <div className="calendar-explorer">
      <div className="calendar-toolbar">
        <div className="calendar-toolbar__month">
          <button
            type="button"
            className="icon-button"
            onClick={() => moveMonth(-1)}
            aria-label="Предыдущий месяц"
          >
            ‹
          </button>
          <p>
            {new Intl.DateTimeFormat('ru-RU', { month: 'long', year: 'numeric' }).format(
              visibleMonth,
            )}
          </p>
          <button
            type="button"
            className="icon-button"
            onClick={() => moveMonth(1)}
            aria-label="Следующий месяц"
          >
            ›
          </button>
        </div>
        <button type="button" className="calendar-today" onClick={goToToday}>
          Сегодня · {formatEventDate(today)}
        </button>
        <div className="calendar-view-toggle" role="group" aria-label="Вид календаря">
          <button type="button" aria-pressed={view === 'month'} onClick={() => setView('month')}>
            Месяц
          </button>
          <button type="button" aria-pressed={view === 'list'} onClick={() => setView('list')}>
            Список
          </button>
        </div>
      </div>

      {view === 'month' ? (
        <div className="calendar-explorer__month">
          <Calendar
            year={year}
            month={month}
            currentDay={currentDay}
            currentDate={currentDate}
            selectedDate={selectedDate}
            events={celestialEvents}
          />
          <aside className="calendar-selected-day">
            <p className="eyebrow">ВЫБРАННАЯ ДАТА</p>
            <h2>{formatEventDate(selectedDate)}</h2>
            {selectedEvents.length ? (
              <div className="calendar-selected-day__events">
                {selectedEvents.map((event) => (
                  <a key={event.id} href={`/events/${event.id}/`}>
                    <span>{event.type === 'period' ? 'ПЕРИОД' : 'СОБЫТИЕ'} · ДЕМО</span>
                    <strong>{event.title}</strong>
                  </a>
                ))}
              </div>
            ) : (
              <p>Для этой даты демонстрационные события не заданы.</p>
            )}
            <a className="text-link" href="/events/">
              Вся хронология <span aria-hidden="true">↗</span>
            </a>
          </aside>
        </div>
      ) : (
        <section className="calendar-event-list" aria-label="События выбранного месяца">
          <div className="calendar-event-list__heading">
            <h2>События месяца</h2>
            <span>{monthEvents.length} · демонстрационные записи</span>
          </div>
          {monthEvents.length ? (
            monthEvents.map((event) => {
              const date = formatEventDateParts(event.type === 'period' ? event.end : event.start);
              return (
                <a className="calendar-event-row" href={`/events/${event.id}/`} key={event.id}>
                  <EventCard
                    date={date.day}
                    month={date.month}
                    title={event.title}
                    kind={`${event.type === 'period' ? 'Период' : 'Точечное событие'} · демо`}
                    glyph={event.glyph}
                  />
                  <span className="calendar-event-row__range">{formatEventRange(event)}</span>
                </a>
              );
            })
          ) : (
            <p className="calendar-empty">В этом месяце демонстрационных событий пока нет.</p>
          )}
        </section>
      )}
      <p className="calendar-demo-note">
        Календарь содержит демонстрационные даты. Эфемериды пока не подключены.
      </p>
    </div>
  );
}
