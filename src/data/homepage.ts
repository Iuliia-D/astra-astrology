import { currentEvent, upcomingEvents } from './events';

export const forecastCopy =
  'Сегодня полезно не торопиться с выводами и оставить немного пространства для новых идей. Выберите свой знак, чтобы увидеть персональную заметку дня.';

export { currentEvent, upcomingEvents };

const nextEvent = upcomingEvents[0];

export const metrics = [
  { label: 'Лунная фаза', value: 'Растущий серп', detail: 'Освещённость 34%', tone: 'violet' },
  { label: 'Солнечный знак', value: 'Весы', detail: 'Воздух · кардинальный', tone: 'blue' },
  {
    label: 'Ближайшее событие',
    value: nextEvent?.title ?? 'Нет событий',
    detail: nextEvent ? `${nextEvent.date} ${nextEvent.month} · демо` : 'Скоро',
    tone: 'cyan',
  },
];
