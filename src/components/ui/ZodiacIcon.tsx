type ZodiacIconProps = {
  glyph: string;
  label: string;
  size?: number;
  className?: string;
  decorative?: boolean;
};

const paths: Record<string, string> = {
  '♈': 'M10 31V19a6 6 0 0 1 12 0v12 M22 19a6 6 0 0 1 12 0v12',
  '♉': 'M14 20a6 6 0 1 0 12 0a6 6 0 0 0-12 0 M12 10c0 5 3 8 8 8s8-3 8-8 M20 18v11',
  '♊': 'M11 10h18 M11 30h18 M14 10v20 M26 10v20',
  '♋': 'M12 17c0-5 5-7 9-4l7 5c4 3 0 9-4 6l-8-5c-4-3-8 1-6 5 M28 23c0 5-5 7-9 4l-7-5c-4-3 0-9 4-6l8 5c4 3 8-1 6-5',
  '♌': 'M20 23a6 6 0 1 0 0-12a6 6 0 0 0 0 12 M21 23c2 8 9 10 13 4c2-3 1-7-2-7s-4 5-2 8',
  '♍': 'M10 11v19 M10 14c0-5 8-5 8 1v15 M18 15c0-5 8-5 8 1v14c0 4 5 4 6 0',
  '♎': 'M12 22a8 8 0 0 1 16 0 M9 26h22 M12 31h16',
  '♏': 'M9 11v19 M9 14c0-5 8-5 8 1v15 M17 15c0-5 8-5 8 1v14c0 4 5 4 7 0 M27 28l5 5l5-5 M32 33v-8',
  '♐': 'M12 29L29 12 M19 11h11v11 M12 21l8 8',
  '♑': 'M10 12c7-4 10 1 11 7l2 12c1 4 7 3 7-1c0-3-4-4-6-1 M14 14l4 16',
  '♒': 'M8 17l5-4l5 4l5-4l5 4l5-4 M8 27l5-4l5 4l5-4l5 4l5-4',
  '♓': 'M14 12c-8 8-8 8 0 16 M26 12c8 8 8 8 0 16 M12 20h16 M12 17v6 M28 17v6',
};

export function ZodiacIcon({
  glyph,
  label,
  size = 24,
  className = '',
  decorative = false,
}: ZodiacIconProps) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 40 40"
      role={decorative ? undefined : 'img'}
      aria-label={decorative ? undefined : label}
      aria-hidden={decorative || undefined}
    >
      <circle cx="20" cy="20" r="18" fill="none" stroke="currentColor" strokeOpacity=".2" />
      <path
        d={paths[glyph] ?? paths['♎']}
        fill="none"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
