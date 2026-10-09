import type { ZodiacSign } from '../../data/zodiac';
import type { DailyHoroscope } from '../../types/horoscope';
import { GlassCard } from './Card';
import { ZodiacIcon } from './ZodiacIcon';

export function HoroscopeCard({
  sign,
  horoscope,
}: {
  sign: ZodiacSign;
  horoscope: DailyHoroscope;
}) {
  return (
    <GlassCard className="horoscope-card" aria-labelledby="horoscope-sign-title" data-reveal>
      <div className="horoscope-card__heading">
        <ZodiacIcon
          glyph={sign.glyph}
          label={sign.name}
          size={54}
          className="horoscope-card__icon"
        />
        <div>
          <p className="eyebrow">ДЕМО-ПРОГНОЗ · {horoscope.date}</p>
          <h2 id="horoscope-sign-title">{sign.name}</h2>
          <p className="horoscope-card__dates">{sign.dates}</p>
        </div>
      </div>
      <p className="horoscope-card__overview">{horoscope.overview}</p>
      <div className="horoscope-card__focus">
        <span className="status-dot" aria-hidden="true" />
        <div>
          <p className="eyebrow">АСТРОЛОГИЧЕСКИЙ АКЦЕНТ ДНЯ</p>
          <p>{horoscope.focus}</p>
        </div>
      </div>
      <p className="horoscope-card__note">
        Демонстрационная интерпретация · не является расчётом по эфемеридам
      </p>
    </GlassCard>
  );
}
