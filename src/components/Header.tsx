type CurrentPage =
  'home' | 'horoscope' | 'calendar' | 'zodiac' | 'zodiacDetail' | 'events' | 'eventDetail';

export function Header({ currentPage = 'home' }: { currentPage?: CurrentPage }) {
  const activeKey =
    currentPage === 'home' || currentPage === 'horoscope'
      ? 'today'
      : currentPage.startsWith('zodiac')
        ? 'zodiac'
        : currentPage.startsWith('event')
          ? 'events'
          : 'calendar';
  const links = [
    {
      key: 'today',
      label: 'Сегодня',
      href: currentPage === 'home' ? '#top' : currentPage === 'horoscope' ? '/horoscope/' : '/',
    },
    { key: 'calendar', label: 'Календарь', href: '/calendar/' },
    { key: 'zodiac', label: 'Знаки', href: '/zodiac/' },
    { key: 'events', label: 'События', href: '/events/' },
  ].map((link) => ({ ...link, active: link.key === activeKey }));
  const homeHref = currentPage === 'home' ? '#top' : '/#top';

  return (
    <header className="site-header">
      <a className="brand" href={homeHref} aria-label="ASTRA — на главную">
        <span className="brand__mark" aria-hidden="true">
          ✳
        </span>
        <span>ASTRA</span>
      </a>
      <nav className="desktop-nav" aria-label="Основная навигация">
        {links.map((link) => (
          <a
            key={link.key}
            href={link.href}
            className={link.active ? 'is-active' : ''}
            aria-current={link.active ? 'page' : undefined}
          >
            {link.label}
          </a>
        ))}
      </nav>
      <div className="header-tools">
        <span className="icon-button search-button" aria-hidden="true">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="10.8" cy="10.8" r="6.3" />
            <path d="m16 16 4 4" />
          </svg>
        </span>
        <span className="header-date">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <rect x="3.5" y="5" width="17" height="16" rx="3" />
            <path d="M7.5 3v4M16.5 3v4M4 9.5h16" />
          </svg>
          <span>08 октября 2026</span>
          <span aria-hidden="true">⌄</span>
        </span>
        <details className="mobile-menu">
          <summary aria-label="Открыть меню">
            <span />
            <span />
          </summary>
          <nav aria-label="Мобильная навигация">
            {links.map((link) => (
              <a key={link.key} href={link.href} aria-current={link.active ? 'page' : undefined}>
                {link.label}
              </a>
            ))}
          </nav>
        </details>
      </div>
    </header>
  );
}
