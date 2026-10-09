export type CelestialBody = {
  id: string;
  name: string;
  /** Angle in radians for the schematic SVG position. */
  angle: number;
  /** Display radius in SVG units; not a physical orbital distance. */
  orbit: number;
  /** Name of a scene gradient token, not an astronomical property. */
  color: string;
  size: number;
};

export type CelestialEvent = {
  id: string;
  type: 'period' | 'point';
  category: 'moon' | 'retrograde' | 'eclipses' | 'transitions' | 'conjunctions';
  planet: string;
  title: string;
  summary: string;
  glyph: string;
  start: string;
  end: string;
  sign: string;
  degree: number;
  timezone: string;
  astronomical_data: string;
  astrological_interpretation: string;
  affected_signs: string[];
  visualization_type: 'retrograde' | 'lunar' | 'transit';
};
