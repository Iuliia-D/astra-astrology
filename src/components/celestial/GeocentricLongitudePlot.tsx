type Position = { name: string; longitude: number; latitude: number };

const labels: Record<string, string> = {
  Sun: 'Солнце', Moon: 'Луна', Mercury: 'Меркурий', Venus: 'Венера', Mars: 'Марс',
  Jupiter: 'Юпитер', Saturn: 'Сатурн', Uranus: 'Уран', Neptune: 'Нептун', Pluto: 'Плутон',
};

export function GeocentricLongitudePlot({ positions }: { positions: Position[] }) {
  const visible = positions.filter((position) => Number.isFinite(position.longitude));
  const left = 178;
  const right = 816;
  const width = right - left;
  const top = 84;
  const row = 48;

  return (
    <svg className="geocentric-plot" viewBox="0 0 860 610" role="img" aria-label="Рассчитанные геоцентрические тропические долготы небесных тел">
      <text x={left} y="32" className="geocentric-plot__title">ГЕОЦЕНТРИЧЕСКАЯ ЭКЛИПТИЧЕСКАЯ ДОЛГОТА</text>
      <text x={left} y="55" className="geocentric-plot__subtitle">Рассчитанные положения · тропический зодиак</text>
      {[0, 90, 180, 270, 360].map((degree) => {
        const x = left + width * degree / 360;
        return (
          <g key={degree}>
            <line x1={x} y1={top - 16} x2={x} y2={top + row * (visible.length - 1) + 12} className="geocentric-plot__grid" />
            <text x={x} y={top - 27} textAnchor={degree === 360 ? 'end' : degree === 0 ? 'start' : 'middle'} className="geocentric-plot__axis">{degree}°</text>
          </g>
        );
      })}
      {visible.map((position, index) => {
        const y = top + row * index;
        const longitude = ((position.longitude % 360) + 360) % 360;
        const x = left + width * longitude / 360;
        const labelX = x > right - 55 ? x - 9 : x + 9;
        return (
          <g key={position.name}>
            <text x="16" y={y + 4} className="geocentric-plot__body">{labels[position.name] ?? position.name}</text>
            <line x1={left} y1={y} x2={right} y2={y} className="geocentric-plot__track" />
            <circle cx={x} cy={y} r="5" className="geocentric-plot__point" />
            <text x={labelX} y={y - 10} textAnchor={labelX < x ? 'end' : 'start'} className="geocentric-plot__value">{longitude.toFixed(2)}°</text>
          </g>
        );
      })}
      <text x={left} y={top + row * visible.length + 35} className="geocentric-plot__foot">Координаты из опубликованного расчёта эфемерид</text>
    </svg>
  );
}
