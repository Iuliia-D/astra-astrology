export const zodiacSigns = [
  { id: 'aries', name: 'Овен', glyph: '♈', dates: '21 марта — 19 апреля' },
  { id: 'taurus', name: 'Телец', glyph: '♉', dates: '20 апреля — 20 мая' },
  { id: 'gemini', name: 'Близнецы', glyph: '♊', dates: '21 мая — 20 июня' },
  { id: 'cancer', name: 'Рак', glyph: '♋', dates: '21 июня — 22 июля' },
  { id: 'leo', name: 'Лев', glyph: '♌', dates: '23 июля — 22 августа' },
  { id: 'virgo', name: 'Дева', glyph: '♍', dates: '23 августа — 22 сентября' },
  { id: 'libra', name: 'Весы', glyph: '♎', dates: '23 сентября — 22 октября' },
  { id: 'scorpio', name: 'Скорпион', glyph: '♏', dates: '23 октября — 21 ноября' },
  { id: 'sagittarius', name: 'Стрелец', glyph: '♐', dates: '22 ноября — 21 декабря' },
  { id: 'capricorn', name: 'Козерог', glyph: '♑', dates: '22 декабря — 19 января' },
  { id: 'aquarius', name: 'Водолей', glyph: '♒', dates: '20 января — 18 февраля' },
  { id: 'pisces', name: 'Рыбы', glyph: '♓', dates: '19 февраля — 20 марта' },
] as const;

export type ZodiacSign = (typeof zodiacSigns)[number];

export function findZodiacSign(id: string): ZodiacSign {
  return zodiacSigns.find((sign) => sign.id === id) ?? zodiacSigns[6];
}
