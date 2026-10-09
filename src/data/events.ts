import type { CelestialEvent } from '../types/astronomy';

// All entries below are demonstrations, not observations or ephemeris calculations.
export const celestialEvents: CelestialEvent[] = [
  {
    id: 'mercury-retrograde-demo',
    type: 'period',
    category: 'retrograde',
    planet: 'Меркурий',
    title: 'Ретроградное движение',
    summary: 'Демонстрационный период для просмотра структуры карточек и временной шкалы.',
    glyph: '☿',
    start: '2026-09-24',
    end: '2026-10-17',
    sign: 'Весы',
    degree: 8,
    timezone: 'UTC',
    astronomical_data: 'Демо-данные. Фактические эфемериды и положение планеты не подключены.',
    astrological_interpretation:
      'Время внимательнее относиться к договорённостям и оставлять пространство для пересмотра планов.',
    affected_signs: ['aries', 'gemini', 'libra', 'sagittarius'],
    visualization_type: 'retrograde',
  },
  {
    id: 'new-moon-demo',
    type: 'point',
    category: 'moon',
    planet: 'Луна',
    title: 'Новолуние в Весах',
    summary: 'Пример точечного события в календаре и списке ASTRA.',
    glyph: '☾',
    start: '2026-10-10',
    end: '2026-10-10',
    sign: 'Весы',
    degree: 0,
    timezone: 'UTC',
    astronomical_data: 'Демо-запись без расчёта фазы, координат или эфемерид.',
    astrological_interpretation:
      'Интерпретация демонстрирует формат публикации и не описывает рассчитанное положение Луны.',
    affected_signs: ['cancer', 'libra', 'capricorn', 'aries'],
    visualization_type: 'lunar',
  },
  {
    id: 'full-moon-demo',
    type: 'point',
    category: 'moon',
    planet: 'Луна',
    title: 'Полнолуние в Тельце',
    summary: 'Демонстрационная запись точечного лунного события.',
    glyph: '☽',
    start: '2026-10-26',
    end: '2026-10-26',
    sign: 'Телец',
    degree: 0,
    timezone: 'UTC',
    astronomical_data: 'Демо-запись без расчёта фазы, координат или эфемерид.',
    astrological_interpretation:
      'Текст показывает пример интерпретационного поля; астрономическим выводом он не является.',
    affected_signs: ['taurus', 'scorpio', 'leo', 'aquarius'],
    visualization_type: 'lunar',
  },
  {
    id: 'eclipse-demo',
    type: 'point',
    category: 'eclipses',
    planet: 'Солнце и Луна',
    title: 'Затмение',
    summary: 'Макетная запись для проверки фильтра затмений.',
    glyph: '◒',
    start: '2026-11-05',
    end: '2026-11-05',
    sign: 'Скорпион',
    degree: 0,
    timezone: 'UTC',
    astronomical_data: 'Демо-запись. Затмение и его геометрия не рассчитывались.',
    astrological_interpretation:
      'Демонстрационная интерпретация отделена от неподключённых астрономических данных.',
    affected_signs: ['taurus', 'leo', 'scorpio', 'aquarius'],
    visualization_type: 'lunar',
  },
  {
    id: 'transition-demo',
    type: 'period',
    category: 'transitions',
    planet: 'Венера',
    title: 'Переход Венеры',
    summary: 'Демо-период показывает, как временной интервал отображается в календаре.',
    glyph: '♀',
    start: '2026-11-14',
    end: '2026-11-28',
    sign: 'Стрелец',
    degree: 0,
    timezone: 'UTC',
    astronomical_data: 'Демо-запись. Транзит и координаты не рассчитывались.',
    astrological_interpretation:
      'Пример интерпретации для периода; он не основан на фактическом положении планеты.',
    affected_signs: ['gemini', 'virgo', 'sagittarius', 'pisces'],
    visualization_type: 'transit',
  },
  {
    id: 'conjunction-demo',
    type: 'point',
    category: 'conjunctions',
    planet: 'Марс и Юпитер',
    title: 'Соединение Марса и Юпитера',
    summary: 'Макетная запись соединения для демонстрации категории событий.',
    glyph: '◌',
    start: '2026-12-03',
    end: '2026-12-03',
    sign: 'Козерог',
    degree: 0,
    timezone: 'UTC',
    astronomical_data: 'Демо-запись. Угловое расстояние и положение небесных тел не рассчитаны.',
    astrological_interpretation:
      'Интерпретационный текст является демонстрацией формата и не выводится из эфемерид.',
    affected_signs: ['aries', 'cancer', 'libra', 'capricorn'],
    visualization_type: 'transit',
  },
];

export const currentEvent = celestialEvents.find(
  (event) => event.id === 'mercury-retrograde-demo',
) as CelestialEvent;

const monthAbbreviations = [
  'ЯНВ',
  'ФЕВ',
  'МАР',
  'АПР',
  'МАЙ',
  'ИЮН',
  'ИЮЛ',
  'АВГ',
  'СЕН',
  'ОКТ',
  'НОЯ',
  'ДЕК',
];

export function formatEventDate(date: string) {
  const parsed = new Date(`${date}T00:00:00Z`);
  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'long',
    timeZone: 'UTC',
  }).format(parsed);
}

export function formatEventDateParts(date: string) {
  const parsed = new Date(`${date}T00:00:00Z`);
  return {
    day: String(parsed.getUTCDate()),
    month: monthAbbreviations[parsed.getUTCMonth()],
  };
}

export function formatEventRange(event: CelestialEvent) {
  if (event.start === event.end) return formatEventDate(event.start);
  return `${formatEventDate(event.start)} — ${formatEventDate(event.end)}`;
}

const today = new Date();
const todayKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

export const upcomingEvents = [...celestialEvents]
  .filter((event) => (event.type === 'period' ? event.end : event.start) >= todayKey)
  .sort((left, right) => {
    const leftDate = left.type === 'period' ? left.end : left.start;
    const rightDate = right.type === 'period' ? right.end : right.start;
    return leftDate.localeCompare(rightDate);
  })
  .slice(0, 3)
  .map((event) => {
    const cardDate = formatEventDateParts(event.type === 'period' ? event.end : event.start);
    return {
      id: event.id,
      date: cardDate.day,
      month: cardDate.month,
      title: event.title,
      kind: event.type === 'period' ? 'Демо-период' : 'Демо-событие',
      glyph: event.glyph,
    };
  });
