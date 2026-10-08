import { describe, expect, it } from 'vitest';
import { findZodiacSign, zodiacSigns } from './zodiac';

describe('zodiac data', () => {
  it('contains twelve unique signs with SVG-friendly symbols', () => {
    expect(zodiacSigns).toHaveLength(12);
    expect(new Set(zodiacSigns.map((sign) => sign.id)).size).toBe(12);
    expect(zodiacSigns.every((sign) => sign.glyph.length > 0)).toBe(true);
  });

  it('falls back to Libra when a saved selection is invalid', () => {
    expect(findZodiacSign('not-a-sign').id).toBe('libra');
  });
});
