import { ZodiacIcon } from '../ui/ZodiacIcon';

const signs = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'];

export function ZodiacRing() {
  return (
    <g className="scene-zodiac" aria-hidden="true">
      {signs.map((sign, index) => {
        const angle = (index * Math.PI) / 6 - Math.PI / 2;
        const x = Number((430 + Math.cos(angle) * 248).toFixed(3));
        const y = Number((320 + Math.sin(angle) * 248).toFixed(3));
        const left = Number((x - 18).toFixed(3));
        const top = Number((y - 18).toFixed(3));
        return (
          <g key={sign} transform={`translate(${left} ${top})`}>
            <ZodiacIcon
              className="scene-zodiac-sign"
              glyph={sign}
              label={sign}
              size={36}
              decorative
            />
          </g>
        );
      })}
    </g>
  );
}
