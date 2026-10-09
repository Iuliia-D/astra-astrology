import type { CelestialBody } from '../../types/astronomy';

type PlanetsProps = { bodies: CelestialBody[] };

export function Planets({ bodies }: PlanetsProps) {
  return (
    <g className="scene-planets" aria-hidden="true">
      {bodies.map((body) => {
        const x = 430 + Math.cos(body.angle) * body.orbit;
        const y = 320 + Math.sin(body.angle) * body.orbit;
        return (
          <g
            key={body.id}
            className="scene-orbiting-body"
            style={{ animationDuration: `${Math.round(90 + body.orbit * 1.15)}s` }}
          >
            <circle
              cx={x}
              cy={y}
              r={body.size + 7}
              fill={`url(#${body.color})`}
              opacity=".12"
              filter="url(#softGlow)"
            />
            <circle cx={x} cy={y} r={body.size} fill={`url(#${body.color})`} />
            <circle
              cx={x - body.size * 0.3}
              cy={y - body.size * 0.35}
              r={body.size * 0.25}
              fill="white"
              opacity=".45"
            />
          </g>
        );
      })}
    </g>
  );
}
