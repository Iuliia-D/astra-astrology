import type { CelestialEvent } from '../types/astronomy';

// Demonstration content only; replace with sourced ephemeris data before production use.
export const currentEvent: CelestialEvent = {
  id: 'mercury-retrograde-demo',
  type: 'period',
  planet: 'Меркурий',
  title: 'Ретроградное движение',
  start: '24 сентября',
  end: '17 октября',
  sign: 'Весы',
  degree: 8,
  timezone: 'UTC',
  astronomical_data: 'Демонстрационная запись. Фактические эфемериды не подключены.',
  astrological_interpretation:
    'Время внимательнее относиться к договорённостям и оставлять пространство для пересмотра планов.',
  affected_signs: ['aries', 'gemini', 'libra', 'sagittarius'],
  visualization_type: 'retrograde',
};

export const forecastCopy =
  'Сегодня полезно не торопиться с выводами и оставить немного пространства для новых идей. Выберите свой знак, чтобы увидеть персональную заметку дня.';

export const upcomingEvents = [
  { date: '10', month: 'ОКТ', title: 'Новолуние в Весах', kind: 'Лунное событие', glyph: '☾' },
  {
    date: '17',
    month: 'ОКТ',
    title: 'Завершение ретроградного периода',
    kind: 'Планетарный транзит',
    glyph: '☿',
  },
  { date: '26', month: 'ОКТ', title: 'Полнолуние в Тельце', kind: 'Лунное событие', glyph: '☽' },
];

export const metrics = [
  { label: 'Лунная фаза', value: 'Растущий серп', detail: 'Освещённость 34%', tone: 'violet' },
  { label: 'Солнечный знак', value: 'Весы', detail: 'Воздух · кардинальный', tone: 'blue' },
  { label: 'Ближайшее событие', value: 'Новолуние', detail: 'Через 2 дня', tone: 'cyan' },
];
