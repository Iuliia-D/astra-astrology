import type { CelestialBody } from '../types/astronomy';
import { demoSceneBodies } from '../data/celestialScene';
import { Constellations } from './celestial/Constellations';
import { EventHighlight } from './celestial/EventHighlight';
import { OrbitPaths } from './celestial/OrbitPaths';
import { PlanetLabels } from './celestial/PlanetLabels';
import { Planets } from './celestial/Planets';
import { StarField } from './celestial/StarField';
import { ZodiacRing } from './celestial/ZodiacRing';

type CelestialSceneProps = { className?: string; bodies?: CelestialBody[] };

export function CelestialScene({ className = '', bodies = demoSceneBodies }: CelestialSceneProps) {
  return (
    <div
      className={`celestial-scene ${className}`}
      role="img"
      aria-label="Схематичная астрономическая карта с орбитами, планетами и зодиакальным кругом"
    >
      <div className="celestial-scene__nebula" aria-hidden="true" />
      <svg
        viewBox="0 0 860 640"
        preserveAspectRatio="xMidYMid meet"
        aria-hidden="true"
        focusable="false"
      >
        <defs>
          <radialGradient id="sunCore">
            <stop stopColor="#fffce0" />
            <stop offset=".24" stopColor="#ffe2a0" />
            <stop offset=".56" stopColor="#fcb760" />
            <stop offset="1" stopColor="#ffb050" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="planetBlue">
            <stop stopColor="#eff1ff" />
            <stop offset=".35" stopColor="#a0aaff" />
            <stop offset="1" stopColor="#484f91" />
          </radialGradient>
          <radialGradient id="planetAmber">
            <stop stopColor="#ffe0b5" />
            <stop offset="1" stopColor="#a75d35" />
          </radialGradient>
          <radialGradient id="planetIce">
            <stop stopColor="#d4f4ff" />
            <stop offset="1" stopColor="#5b7794" />
          </radialGradient>
          <radialGradient id="planetJupiter">
            <stop stopColor="#efd1ad" />
            <stop offset=".55" stopColor="#ae8261" />
            <stop offset="1" stopColor="#493c3b" />
          </radialGradient>
          <radialGradient id="planetMars">
            <stop stopColor="#eebc98" />
            <stop offset="1" stopColor="#854b42" />
          </radialGradient>
          <radialGradient id="planetMercury">
            <stop stopColor="#e8e7ff" />
            <stop offset="1" stopColor="#858bdb" />
          </radialGradient>
          <radialGradient id="eventGlow">
            <stop stopColor="#938cff" stopOpacity=".65" />
            <stop offset="1" stopColor="#938cff" stopOpacity="0" />
          </radialGradient>
          <filter id="softGlow">
            <feGaussianBlur stdDeviation="8" />
          </filter>
        </defs>
        <StarField />
        <Constellations />
        <OrbitPaths />
        <ZodiacRing />
        <g className="scene-sun" aria-hidden="true">
          <circle cx="430" cy="320" r="73" fill="url(#sunCore)" />
          <circle cx="430" cy="320" r="24" fill="#ffe9b8" />
          <circle cx="430" cy="320" r="18" fill="#fff4cb" />
          <text x="430" y="363" textAnchor="middle">
            СОЛНЦЕ
          </text>
        </g>
        <Planets bodies={bodies} />
        <PlanetLabels bodies={bodies} />
        <EventHighlight />
      </svg>
      <div className="scene-coordinates" aria-hidden="true">
        <span>α 14h 52m</span>
        <span>δ +08° 12′</span>
        <span>J2000 · SCHEMATIC</span>
      </div>
    </div>
  );
}
