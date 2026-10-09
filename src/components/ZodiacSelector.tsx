import { useEffect, useRef, useState } from 'react';
import { zodiacSigns } from '../data/zodiac';
import { demoForecastCopy, forecastScores } from '../data/forecast';
import { ZodiacIcon } from './ui/ZodiacIcon';

type ZodiacSelectorProps = { value: string; onChange: (id: string) => void };

export function ZodiacSelector({ value, onChange }: ZodiacSelectorProps) {
  return (
    <div className="zodiac-selector" role="group" aria-label="Выберите знак зодиака">
      {zodiacSigns.map((sign) => (
        <button
          className={`zodiac-option ${value === sign.id ? 'is-selected' : ''}`}
          type="button"
          key={sign.id}
          aria-pressed={value === sign.id}
          onClick={() => onChange(sign.id)}
        >
          <ZodiacIcon
            className="zodiac-option__symbol"
            glyph={sign.glyph}
            label={sign.name}
            size={36}
            decorative
          />
          <span>{sign.name}</span>
        </button>
      ))}
    </div>
  );
}

export function ForecastSection() {
  const [selected, setSelected] = useState('libra');
  const sectionRef = useRef<HTMLElement>(null);
  const sign = zodiacSigns.find((item) => item.id === selected) ?? zodiacSigns[6];

  useEffect(() => {
    const saved = window.localStorage.getItem('astra-zodiac-sign');
    if (saved && zodiacSigns.some((item) => item.id === saved)) setSelected(saved);
  }, []);

  useEffect(() => {
    const section = sectionRef.current;
    if (
      !section ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
      !('IntersectionObserver' in window)
    ) {
      return;
    }

    section.dataset.revealState = 'pending';
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return;
        section.dataset.revealState = 'visible';
        observer.disconnect();
      },
      { threshold: 0.08, rootMargin: '0px 0px -6% 0px' },
    );
    observer.observe(section);
    return () => observer.disconnect();
  }, []);

  function selectSign(id: string) {
    setSelected(id);
    window.localStorage.setItem('astra-zodiac-sign', id);
  }

  return (
    <section
      ref={sectionRef}
      className="section forecast-section"
      id="forecast"
      aria-labelledby="forecast-title"
      data-reveal
    >
      <div className="forecast-intro">
        <div>
          <p className="eyebrow">ВАШ ПРОГНОЗ · 08 ОКТЯБРЯ</p>
          <h2 id="forecast-title">
            Выберите
            <br className="desktop-break" /> свой знак зодиака
          </h2>
        </div>
        <p className="forecast-intro__hint">
          Прогноз на сегодня
          <br />
          <span>Сохранится на этом устройстве</span>
        </p>
      </div>
      <ZodiacSelector value={selected} onChange={selectSign} />
      <div className="forecast-card">
        <div className="forecast-sign-art" aria-hidden="true">
          <div className="forecast-sign-art__orbit">
            <ZodiacIcon
              className="forecast-sign-art__star"
              glyph={sign.glyph}
              label={sign.name}
              size={70}
              decorative
            />
          </div>
          <span>ASTRA · {sign.id.toUpperCase()}</span>
        </div>
        <div className="forecast-copy">
          <div className="forecast-copy__title">
            <ZodiacIcon
              className="forecast-copy__glyph"
              glyph={sign.glyph}
              label={sign.name}
              size={38}
              decorative
            />
            <div>
              <p className="eyebrow">ПЕРСОНАЛЬНАЯ ЗАМЕТКА</p>
              <h3>{sign.name}</h3>
              <p>{sign.dates}</p>
            </div>
          </div>
          <p className="forecast-copy__body">
            {demoForecastCopy[sign.id] ?? demoForecastCopy.default}
          </p>
          <p className="forecast-note">
            Демонстрационная интерпретация · не является расчётом по эфемеридам
          </p>
        </div>
        <div className="forecast-scores" aria-label="Демонстрационные показатели прогноза">
          {forecastScores.map((score) => (
            <div className="score-row" key={score.label}>
              <span>{score.label}</span>
              <span className="score-track" aria-hidden="true">
                <span
                  className={`score-track__fill score-track__fill--${score.tone}`}
                  style={{ width: `${score.value}%` }}
                />
              </span>
              <strong>{score.value}</strong>
            </div>
          ))}
        </div>
      </div>
      <div className="forecast-advice">
        <div>
          <span className="advice-icon advice-icon--time" aria-hidden="true">
            ◷
          </span>
          <p className="eyebrow">КЛЮЧЕВОЙ МОМЕНТ</p>
          <strong>14:30 — 17:00</strong>
          <span>Время для важных решений</span>
        </div>
        <div>
          <span className="advice-icon advice-icon--yes" aria-hidden="true">
            ✓
          </span>
          <p className="eyebrow">ЧТО СЕГОДНЯ СДЕЛАТЬ</p>
          <strong>Завершить отложенные задачи</strong>
          <span>Уделить время важному разговору</span>
        </div>
        <div>
          <span className="advice-icon advice-icon--no" aria-hidden="true">
            ×
          </span>
          <p className="eyebrow">ЧЕГО ЛУЧШЕ ИЗБЕГАТЬ</p>
          <strong>Не торопиться с выводами</strong>
          <span>Оставить место для уточнений</span>
        </div>
      </div>
      <div className="forecast-page-links">
        <a className="text-link" href={`/horoscope/?sign=${sign.id}#top`}>
          Открыть прогноз <span aria-hidden="true">↗</span>
        </a>
        <a className="text-link" href={`/zodiac/${sign.id}/`}>
          Профиль знака <span aria-hidden="true">↗</span>
        </a>
      </div>
    </section>
  );
}
