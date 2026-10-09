import type { ZodiacSign } from './zodiac';

export type CompatibilityScore = {
  label: string;
  value: number;
};

export type CompatibilityDemo = {
  scores: [
    CompatibilityScore,
    CompatibilityScore,
    CompatibilityScore,
    CompatibilityScore,
    CompatibilityScore,
  ];
  strengths: string[];
  challenges: string[];
  recommendations: string[];
};

// Interface fixture only. These values are deliberately not calculated or presented as facts.
export const compatibilityDemo: CompatibilityDemo = {
  scores: [
    { label: 'Общий ритм', value: 76 },
    { label: 'Любовь', value: 82 },
    { label: 'Общение', value: 73 },
    { label: 'Страсть', value: 78 },
    { label: 'Долгосрочные отношения', value: 70 },
  ],
  strengths: [
    'Интерес к точке зрения другого помогает находить новые решения.',
    'Открытый разговор поддерживает взаимное уважение и близость.',
  ],
  challenges: [
    'Различия в темпе могут приводить к неверным ожиданиям.',
    'Невысказанные предположения иногда заменяют прямой диалог.',
  ],
  recommendations: [
    'Обсуждайте ожидания конкретно и без попытки угадать намерения.',
    'Оставляйте место как для совместных планов, так и для личного пространства.',
    'Воспринимайте разногласия как повод уточнить договорённости.',
  ],
};

export type CompatibilityPair = {
  first: ZodiacSign['id'];
  second: ZodiacSign['id'];
};
