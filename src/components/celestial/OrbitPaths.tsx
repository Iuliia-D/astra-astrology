export function OrbitPaths() {
  return (
    <g className="scene-orbits" aria-hidden="true" transform="rotate(-13 430 320)">
      <ellipse cx="430" cy="320" rx="112" ry="58" />
      <ellipse cx="430" cy="320" rx="166" ry="86" />
      <ellipse cx="430" cy="320" rx="220" ry="114" />
      <ellipse cx="430" cy="320" rx="277" ry="145" />
      <ellipse cx="430" cy="320" rx="330" ry="174" />
      <circle className="scene-orbits__guide" cx="430" cy="320" r="250" />
      <path className="scene-orbits__axis" d="M72 320h716M430 40v560" />
    </g>
  );
}
