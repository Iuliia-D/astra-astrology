const stars = Array.from({ length: 116 }, (_, index) => ({
  x: (index * 137 + 31) % 860,
  y: (index * 83 + 17) % 640,
  r: index % 13 === 0 ? 1.55 : index % 4 === 0 ? 1 : 0.62,
  opacity: 0.2 + ((index * 19) % 70) / 100,
}));

export function StarField() {
  return (
    <g className="scene-stars" aria-hidden="true">
      {stars.map((star, index) => (
        <circle
          key={index}
          cx={star.x}
          cy={star.y}
          r={star.r}
          fill="white"
          opacity={star.opacity}
        />
      ))}
    </g>
  );
}
