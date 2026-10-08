import type { CelestialBody } from '../types/astronomy';

// Visual-only mock positions for the first-stage schematic, not ephemeris output.
export const demoSceneBodies: CelestialBody[] = [
  { id: 'venus', name: 'Венера', angle: -2.75, orbit: 119, color: 'planetBlue', size: 9 },
  { id: 'mars', name: 'Марс', angle: -0.38, orbit: 135, color: 'planetAmber', size: 11 },
  { id: 'earth', name: 'Земля', angle: 2.62, orbit: 145, color: 'planetIce', size: 8 },
  { id: 'jupiter', name: 'Юпитер', angle: 0.25, orbit: 201, color: 'planetJupiter', size: 16 },
  { id: 'saturn', name: 'Сатурн', angle: 0.84, orbit: 158, color: 'planetMars', size: 11 },
];
