import { describe, expect, it } from 'vitest';
import { celestialEvents, currentEvent, formatEventDate } from './events';
import { zodiacSigns } from './zodiac';

describe('celestial event data', () => {
  it('keeps unique, explicitly demo events in one shared collection', () => {
    expect(new Set(celestialEvents.map((event) => event.id)).size).toBe(celestialEvents.length);
    expect(celestialEvents).toContain(currentEvent);
    expect(celestialEvents.every((event) => event.astronomical_data.includes('Демо'))).toBe(true);
  });

  it('uses valid date ranges and known related zodiac signs', () => {
    const signIds = new Set<string>(zodiacSigns.map((sign) => sign.id));
    for (const event of celestialEvents) {
      expect(event.start).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      expect(event.end >= event.start).toBe(true);
      expect(event.affected_signs.every((sign) => signIds.has(sign))).toBe(true);
    }
  });

  it('formats the shared Mercury demo period from its canonical dates', () => {
    expect(formatEventDate(currentEvent.start)).toContain('24 сентября');
    expect(formatEventDate(currentEvent.end)).toContain('17 октября');
  });
});
