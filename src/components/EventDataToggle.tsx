import { useState } from 'react';
import type { CelestialEvent } from '../types/astronomy';
import { formatEventRange } from '../data/events';

type EventDataToggleProps = { event: CelestialEvent };

export function EventDataToggle({ event }: EventDataToggleProps) {
  const [mode, setMode] = useState<'astronomy' | 'astrology'>('astronomy');

  return (
    <section className="event-data-panel" aria-label="Данные события">
      <div className="event-data-toggle" role="group" aria-label="Режим данных">
        <button
          type="button"
          aria-pressed={mode === 'astronomy'}
          onClick={() => setMode('astronomy')}
        >
          Астрономия
        </button>
        <button
          type="button"
          aria-pressed={mode === 'astrology'}
          onClick={() => setMode('astrology')}
        >
          Астрология
        </button>
      </div>
      {mode === 'astronomy' ? (
        <div className="event-data-content">
          <p className="eyebrow">ФАКТИЧЕСКИЙ СЛОЙ · ДЕМО</p>
          <h2>Астрономические данные</h2>
          <dl>
            <div>
              <dt>Временной интервал</dt>
              <dd>{formatEventRange(event)}</dd>
            </div>
            <div>
              <dt>Объект</dt>
              <dd>{event.planet}</dd>
            </div>
            <div>
              <dt>Система отсчёта</dt>
              <dd>{event.timezone}</dd>
            </div>
            <div>
              <dt>Положение в модели</dt>
              <dd>
                {event.sign} · {event.degree}°
              </dd>
            </div>
          </dl>
          <p className="event-data-note">{event.astronomical_data}</p>
        </div>
      ) : (
        <div className="event-data-content">
          <p className="eyebrow">ИНТЕРПРЕТАЦИОННЫЙ СЛОЙ · ДЕМО</p>
          <h2>Астрологическая интерпретация</h2>
          <p>{event.astrological_interpretation}</p>
          <p className="event-data-note">
            Астрология не является научно доказанным методом. Этот текст приведён как демонстрация
            формата.
          </p>
        </div>
      )}
    </section>
  );
}
