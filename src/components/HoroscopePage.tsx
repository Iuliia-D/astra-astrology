import { useEffect, useRef, useState } from 'react';
import { getPublishedForecast } from '../data/horoscopes';
import { findZodiacSign, zodiacSigns } from '../data/zodiac';
import { CelestialScene } from './CelestialScene';
import { ZodiacSelector } from './ZodiacSelector';
import { EventCard } from './ui/EventCard';
import { HoroscopeCard } from './ui/HoroscopeCard';
import { MetricIndicator } from './ui/MetricIndicator';
import { SectionHeader } from './ui/SectionHeader';

const storageKey = 'astra-zodiac-sign';

export function HoroscopePage() {
  const [selected, setSelected] = useState('libra');
  const pageRef = useRef<HTMLElement>(null);
  const sign = findZodiacSign(selected);
  const today = new Intl.DateTimeFormat('sv-SE', {
    timeZone: 'Europe/Moscow',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date());
  const todayLabel = new Intl.DateTimeFormat('ru-RU', {
    timeZone: 'Europe/Moscow',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date());
  const horoscope = getPublishedForecast(sign.id, today);
  const astronomicalPositions = horoscope?.astronomy?.visualization?.positions;

  useEffect(() => {
    const requestedSign = new URLSearchParams(window.location.search).get('sign');
    const savedSign = window.localStorage.getItem(storageKey);
    const initialSign = requestedSign ?? savedSign;
    if (initialSign && zodiacSigns.some((item) => item.id === initialSign)) {
      setSelected(initialSign);
      window.localStorage.setItem(storageKey, initialSign);
    }
  }, []);

  useEffect(() => {
    const page = pageRef.current;
    if (
      !page ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
      !('IntersectionObserver' in window)
    ) {
      return;
    }

    const targets = page.querySelectorAll<HTMLElement>('[data-reveal]');
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          (entry.target as HTMLElement).dataset.revealState = 'visible';
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.08, rootMargin: '0px 0px -6% 0px' },
    );

    targets.forEach((target) => {
      target.dataset.revealState = 'pending';
      observer.observe(target);
    });

    return () => observer.disconnect();
  }, []);

  function selectSign(id: string) {
    setSelected(id);
    window.localStorage.setItem(storageKey, id);
    if (new URLSearchParams(window.location.search).has('sign')) {
      window.history.replaceState(null, '', '/horoscope/');
    }
  }

  return (
    <main className="horoscope-page section" id="top" ref={pageRef}>
      <header className="horoscope-intro">
        <p className="eyebrow">ВАШ ПРОГНОЗ</p>
        <h1>Гороскоп на сегодня</h1>
        <p>Ежедневные заметки для всех знаков зодиака — выберите свой, чтобы открыть прогноз.</p>
      </header>

      <section
        className="horoscope-selector-section"
        id="horoscope-selector"
        aria-label="Выбор знака"
      >
        <ZodiacSelector value={sign.id} onChange={selectSign} />
      </section>

      {horoscope ? (
        <>
          <HoroscopeCard sign={sign} horoscope={horoscope} />

          <section className="horoscope-metrics" aria-label="Показатели дня" data-reveal>
            {horoscope.metrics.map((metric) => (
              <MetricIndicator key={metric.label} {...metric} />
            ))}
          </section>

          {astronomicalPositions?.length ? (
            <section
              className="horoscope-scene-section"
              aria-label="Рассчитанные положения небесных тел"
              data-reveal
            >
              <div className="horoscope-scene-section__caption">
                <span className="eyebrow">РАСЧЁТНЫЕ КООРДИНАТЫ · DE432s · {horoscope.date}</span>
                <span>Геоцентрическая эклиптическая долгота · без масштаба расстояний</span>
              </div>
              <CelestialScene
                className="horoscope-scene"
                astronomicalPositions={astronomicalPositions}
              />
            </section>
          ) : null}

          {horoscope.keyMoment && (
            <section className="key-moment" aria-labelledby="key-moment-title" data-reveal>
              <SectionHeader label="РИТМ ДНЯ" title="Ключевой момент дня" id="key-moment-title" />
              <div className="key-moment__content">
                <div className="key-moment__time">
                  <span className="eyebrow">ТОЧНОЕ РАСЧЁТНОЕ ВРЕМЯ · МОСКВА</span>
                  <strong>{horoscope.keyMoment.time}</strong>
                </div>
                <div className="key-moment__timeline">
                  {horoscope.keyMoment.progress !== undefined && (
                    <div
                      className="key-moment__track"
                      role="progressbar"
                      aria-label="Положение ключевого момента в течение дня"
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-valuenow={horoscope.keyMoment.progress}
                    >
                      <span style={{ width: `${horoscope.keyMoment.progress}%` }} />
                    </div>
                  )}
                  <p>{horoscope.keyMoment.description}</p>
                </div>
              </div>
            </section>
          )}

          {(horoscope.guidance.do || horoscope.guidance.avoid || horoscope.guidance.notice) && (
            <section className="horoscope-guidance" aria-label="Рекомендации на день" data-reveal>
              {horoscope.guidance.do && (
                <article className="guidance-card">
                  <p className="eyebrow">ЧТО СДЕЛАТЬ</p>
                  <p>{horoscope.guidance.do}</p>
                </article>
              )}
              {horoscope.guidance.avoid && (
                <article className="guidance-card">
                  <p className="eyebrow">ЧЕГО ИЗБЕГАТЬ</p>
                  <p>{horoscope.guidance.avoid}</p>
                </article>
              )}
              {horoscope.guidance.notice && (
                <article className="guidance-card">
                  <p className="eyebrow">НА ЧТО ОБРАТИТЬ ВНИМАНИЕ</p>
                  <p>{horoscope.guidance.notice}</p>
                </article>
              )}
            </section>
          )}

          {horoscope.event && (
            <section
              className="horoscope-event"
              aria-labelledby="horoscope-event-title"
              data-reveal
            >
              <SectionHeader label="РАСЧЁТНОЕ СОБЫТИЕ" title="Что происходит на небе" />
              <a className="horoscope-event__link" href={`/events/${horoscope.event.slug}/`}>
                <EventCard
                  date={
                    horoscope.event.start_utc
                      ? new Intl.DateTimeFormat('ru-RU', {
                          day: '2-digit',
                          month: 'short',
                          timeZone: 'Europe/Moscow',
                        }).format(new Date(horoscope.event.start_utc))
                      : horoscope.date
                  }
                  month="Europe/Moscow"
                  title={horoscope.event.title}
                  kind="Связано с рассчитанным событием"
                  glyph="◎"
                />
              </a>
              {horoscope.eventRelation && (
                <div className="horoscope-event__context">
                  <p>{horoscope.eventRelation}</p>
                  <p className="horoscope-event__note">
                    Астрономические факты и астрологическая интерпретация хранятся отдельно.
                  </p>
                </div>
              )}
            </section>
          )}
        </>
      ) : (
        <section
          className="horoscope-card horoscope-card--unavailable"
          role="status"
          aria-live="polite"
        >
          <p className="eyebrow">НЕТ ОПУБЛИКОВАННОГО ПРОГНОЗА</p>
          <h2>
            {sign.name} · {todayLabel}
          </h2>
          <p>
            На эту дату нет опубликованного прогноза для выбранного знака. Демонстрационные данные
            не отображаются.
          </p>
        </section>
      )}

      <nav
        className="other-signs"
        id="other-signs"
        aria-label="Быстрый переход к прогнозу другого знака"
        data-reveal
      >
        <p className="eyebrow">ДРУГИЕ ЗНАКИ</p>
        <div>
          {zodiacSigns
            .filter((item) => item.id !== sign.id)
            .map((item) => (
              <a
                key={item.id}
                href={`/horoscope/?sign=${item.id}#top`}
                aria-label={`Открыть прогноз: ${item.name}`}
              >
                {item.name}
              </a>
            ))}
        </div>
      </nav>
    </main>
  );
}
