const constellations = [
  {
    points: '74,160 113,136 136,175 168,164 186,205',
    lines: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
    ],
  },
  {
    points: '690,105 728,128 756,102 785,147 822,136',
    lines: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
    ],
  },
  {
    points: '120,490 148,457 179,478 211,452 232,481',
    lines: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
    ],
  },
  {
    points: '666,492 698,463 726,483 757,451 790,475 819,460',
    lines: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
      [4, 5],
    ],
  },
];

export function Constellations() {
  return (
    <g className="scene-constellations" aria-hidden="true">
      {constellations.map((shape, index) => {
        const points = shape.points.split(' ').map((point) => point.split(',').map(Number));
        return (
          <g key={index}>
            {shape.lines.map(([from, to]) => (
              <line
                key={`${from}-${to}`}
                x1={points[from][0]}
                y1={points[from][1]}
                x2={points[to][0]}
                y2={points[to][1]}
              />
            ))}
            {points.map(([x, y], pointIndex) => (
              <circle key={pointIndex} cx={x} cy={y} r="1.7" />
            ))}
          </g>
        );
      })}
    </g>
  );
}
