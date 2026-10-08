export function EventHighlight() {
  return (
    <g className="scene-event" aria-hidden="true">
      <circle cx="347" cy="302" r="27" fill="url(#eventGlow)" />
      <circle cx="347" cy="302" r="10" fill="url(#planetMercury)" />
      <circle cx="347" cy="302" r="19" fill="none" stroke="#9c9dff" strokeOpacity=".75" />
      <circle cx="347" cy="302" r="26" fill="none" stroke="#9c9dff" strokeOpacity=".22" />
      <path d="M347 272v-15h-34" fill="none" stroke="#a9b6ff" strokeOpacity=".65" />
      <text x="307" y="251">
        МЕРКУРИЙ
      </text>
    </g>
  );
}
