import { useState } from 'react';
import { compatibilityDemo } from '../data/compatibility';
import { zodiacSigns } from '../data/zodiac';
import { ZodiacIcon } from './ui/ZodiacIcon';

export function CompatibilityExplorer() {
  const [first, setFirst] = useState('aries');
  const [second, setSecond] = useState('libra');
  const firstSign = zodiacSigns.find((sign) => sign.id === first) ?? zodiacSigns[0];
  const secondSign = zodiacSigns.find((sign) => sign.id === second) ?? zodiacSigns[6];

  return (
    <div className="compatibility-explorer">
      <section className="compatibility-selectors" aria-label="Выбор знаков">
        {[
          { value: first, onChange: setFirst, label: 'Первый знак' },
          { value: second, onChange: setSecond, label: 'Второй знак' },
        ].map((field, index) => (
          <label className="compatibility-select" key={field.label}>
            <span className="eyebrow">{field.label.toUpperCase()}</span>
            <span className="compatibility-select__control">
              <ZodiacIcon
                glyph={index === 0 ? firstSign.glyph : secondSign.glyph}
                label=""
                size={26}
                decorative
              />
              <select
                value={field.value}
                onChange={(event) => field.onChange(event.target.value)}
                aria-label={field.label}
              >
                {zodiacSigns.map((sign) => (
                  <option key={sign.id} value={sign.id}>
                    {sign.name}
                  </option>
                ))}
              </select>
            </span>
          </label>
        ))}
      </section>

      <section className="compatibility-summary glass-card" aria-labelledby="compatibility-result">
        <div>
          <p className="eyebrow">ДЕМО-ПРИМЕР · НЕ РАСЧЁТ ОТНОШЕНИЙ</p>
          <h2 id="compatibility-result">
            {firstSign.name} и {secondSign.name}
          </h2>
          <p>
            Шкалы и текст ниже показывают формат раздела и не меняются в зависимости от выбранной
            пары. ASTRA не делает выводов о реальных отношениях.
          </p>
        </div>
        <div className="compatibility-score">
          <span>Общий пример</span>
          <strong>
            {compatibilityDemo.scores[0].value}
            <small>/100</small>
          </strong>
          <div className="compatibility-score__track" aria-hidden="true">
            <span style={{ width: `${compatibilityDemo.scores[0].value}%` }} />
          </div>
        </div>
      </section>

      <section className="compatibility-metrics" aria-label="Демонстрационные показатели">
        {compatibilityDemo.scores.slice(1).map((score) => (
          <article className="compatibility-metric" key={score.label}>
            <span>{score.label}</span>
            <strong>
              {score.value}
              <small>/100</small>
            </strong>
            <div className="compatibility-score__track" aria-hidden="true">
              <span style={{ width: `${score.value}%` }} />
            </div>
          </article>
        ))}
      </section>

      <div className="compatibility-content-grid">
        <section className="profile-panel">
          <p className="eyebrow">РЕСУРСЫ</p>
          <h2>Что может сближать</h2>
          <ul>
            {compatibilityDemo.strengths.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
        <section className="profile-panel">
          <p className="eyebrow">ЗОНЫ ВНИМАНИЯ</p>
          <h2>Возможные сложности</h2>
          <ul>
            {compatibilityDemo.challenges.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
        <section className="profile-panel profile-panel--wide">
          <p className="eyebrow">ПРАКТИЧЕСКИЕ ИДЕИ</p>
          <h2>Как поддержать диалог</h2>
          <ul>
            {compatibilityDemo.recommendations.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}
