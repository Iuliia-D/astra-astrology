import type { CelestialBody } from '../../types/astronomy';

type PlanetLabelsProps = { bodies: CelestialBody[] };

export function PlanetLabels({ bodies }: PlanetLabelsProps) {
  return (
    <g className="scene-labels" aria-hidden="true">
      {bodies.map((body) => {
        const x = 430 + Math.cos(body.angle) * body.orbit;
        const y = 320 + Math.sin(body.angle) * body.orbit;
        const duration = `${Math.round(90 + body.orbit * 1.15)}s`;
        return (
          <g key={body.id} className="scene-orbiting-label" style={{ animationDuration: duration }}>
            <text
              className="scene-orbiting-label__text"
              style={{ animationDuration: duration }}
              x={x + Math.sign(Math.cos(body.angle)) * (body.size + 10)}
              y={y + body.size + 12}
            >
              {body.name.toUpperCase()}
            </text>
          </g>
        );
      })}
    </g>
  );
}
