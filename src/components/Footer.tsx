export function Footer() {
  return (
    <footer className="site-footer">
      <a className="brand brand--footer" href="/">
        <span className="brand__mark" aria-hidden="true">
          ✳
        </span>
        <span>ASTRA</span>
      </a>
      <p>Астрономические данные и астрологические интерпретации — отдельно.</p>
      <nav className="footer-nav" aria-label="Разделы ASTRA">
        <a href="/horoscope/">Гороскоп</a>
        <a href="/calendar/">Календарь</a>
        <a href="/zodiac/">Знаки</a>
        <a href="/events/">События</a>
      </nav>
      <span className="footer-meta">© ASTRA · 2026</span>
    </footer>
  );
}
