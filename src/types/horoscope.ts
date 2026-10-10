import type { ZodiacSign } from '../data/zodiac';

export type HoroscopeMetric = {
  label: string;
  value: string;
  detail: string;
  tone: 'violet' | 'blue' | 'cyan';
  editorial_tone?: string | null;
  source_content_id?: string;
  source_content_version?: number;
};

export type DailyHoroscope = {
  date: string;
  overview: string;
  focus: string | null;
  metrics: HoroscopeMetric[];
  keyMoment: { time: string; description: string; progress?: number } | null;
  guidance: { do: string | null; avoid: string | null; notice: string | null };
  eventRelation: string | null;
  source?: 'demo' | 'backend';
  event?: { slug: string; title: string; start_utc: string | null; source_event_id: string } | null;
  astronomy?: {
    ephemeris_version: string | null;
    positions: { name: string; longitude: number; latitude: number; sign?: string; degree_in_sign?: number; speed_deg_day?: number }[];
    events: string[];
    visualization: { positions: { name: string; longitude: number; latitude: number }[] } | null;
  };
  publication?: {
    id: string;
    revision: number;
    published_at_utc: string;
    timezone: string;
    algorithm_version: string;
    ruleset_version: string;
    main_word_count: number;
    main_length_warning: string | null;
  };
};

export type DailyHoroscopes = Record<ZodiacSign['id'], DailyHoroscope>;
