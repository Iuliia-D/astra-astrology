import { ZodiacIcon } from '../ui/ZodiacIcon';

const signs = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'];

export function ZodiacRing() {
  return (
    <g className="scene-zodiac" aria-hidden="true">
      {signs.map((sign, index) => {
        const angle = (index * Math.PI) / 6 - Math.PI / 2;
        const x = 430 + Math.cos(angle) * 248;
        const y = 320 + Math.sin(angle) * 248;
        return (
          <g key={sign} transform={`translate(${x - 18} ${y - 18})`}>
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
