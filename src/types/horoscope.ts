import type { ZodiacSign } from '../data/zodiac';

export type HoroscopeMetric = {
  label: string;
  value: string;
  detail: string;
  tone: 'violet' | 'blue' | 'cyan';
};

export type DailyHoroscope = {
  date: string;
  overview: string;
  focus: string;
  metrics: [HoroscopeMetric, HoroscopeMetric, HoroscopeMetric, HoroscopeMetric];
  keyMoment: { time: string; description: string; progress: number };
  guidance: { do: string; avoid: string; notice: string };
  eventRelation: string;
};

export type DailyHoroscopes = Record<ZodiacSign['id'], DailyHoroscope>;
