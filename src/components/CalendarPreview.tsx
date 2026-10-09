import { Calendar } from './Calendar';

export function CalendarPreview() {
  return (
    <section
      className="section calendar-section"
      id="calendar"
      aria-labelledby="calendar-title"
      data-reveal
    >
      <div className="section-heading">
        <div>
          <p className="eyebrow">АСТРОЛОГИЧЕСКИЙ КАЛЕНДАРЬ</p>
          <h2 id="calendar-title">Октябрь 2026</h2>
        </div>
        <a className="text-link" href="#events">
          Полный календарь <span aria-hidden="true">↗</span>
        </a>
      </div>
      <div className="calendar-layout">
        <Calendar year={2026} month={9} currentDay={8} eventDays={[10, 17, 26]} />
        <aside className="calendar-feature">
          <div className="calendar-feature__planet" aria-hidden="true">
            <div />
          </div>
          <p className="eyebrow">ASTRA · НАВИГАЦИЯ</p>
          <h3>Небо в контексте</h3>
          <p>Фазы Луны и движения планет — в одном календаре.</p>
          <a className="feature-arrow" href="#events" aria-label="Перейти к ближайшим событиям">
            →
          </a>
        </aside>
      </div>
    </section>
  );
}
