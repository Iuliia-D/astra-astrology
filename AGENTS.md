# Repository Guidelines

## Project purpose

ASTRA is a modern Russian-language astrology product presented as a digital astronomical system or contemporary observatory. Build a serious, premium digital experience with restrained Apple/ChatGPT-like minimalism and an astronomical interface. Avoid the look of an esoteric shop, mystical portal, or cheap horoscope. Keep astronomy (computed facts) clearly separate from astrology (interpretation); never present astrology as scientifically proven. Do not begin implementation of the site until the user requests it.

## Technology and engineering principles

Preferred stack: Astro, React, TypeScript in strict mode, Tailwind CSS, SVG/CSS for visualizations, Docker, Vitest, and Playwright. Use Three.js/WebGL only when the feature warrants its cost. Use ESLint and Prettier. Keep dependencies lean. Do not use runtime AI APIs in the MVP, and never use an LLM to calculate celestial positions, aspects, retrograde motion, or other astronomical values. Use a reliable astronomy/ephemeris library; where practical, precompute results into structured JSON. Keep astronomy calculations independent of UI and editorial content.

## Architecture and routes

Keep UI, data, astronomy calculations, astrological interpretation, SEO, analytics, and editorial content in distinct modules. Use reusable components and typed data models; do not embed large content collections in React components. Core routes: `/`, `/horoscope/`, `/calendar/`, `/zodiac/[sign]/`, `/compatibility/`, `/events/`, `/events/[slug]/`, and `/about/`. Later legal routes may include privacy, personal-data, terms, and advertising information. Build zodiac pages from one data-driven template, not twelve separately authored implementations.

Establish reusable components as needed: Header, Footer, Button, Card, GlassCard, ZodiacSelector, ZodiacIcon, HoroscopeCard, MetricIndicator, EventCard, EventTimeline, Calendar, CelestialScene, AdSlot, SEO, and SectionHeader. `CelestialScene` must be reusable and layered logically: StarField, Constellations, ZodiacRing, OrbitPaths, Planets, PlanetLabels, and EventHighlight. Build it from SVG/CSS/Canvas/WebGL as appropriate; do not use one raster image as its primary implementation. Zodiac symbols must be SVG, never emoji.

## Astronomy and content models

Store factual `astronomical_data` separately from `astrological_interpretation`, and do not combine them in one paragraph. Use structured, validated records for events. An event may include `id`, `type`, `planet`, `title`, `start`, `end`, `sign`, `degree`, `timezone`, `astronomical_data`, `astrological_interpretation`, `affected_signs`, and `visualization_type`. Distinguish point events from period events. Event detail pages should show dates, a CelestialScene, astronomical facts, astrological interpretation, and impacts across all twelve signs, with an “Астрономия | Астрология” view toggle.

## Design system and visual direction

Use these design tokens: background `#070911`, secondary background `#0B0F1A`, surface `#111625`, glass `rgba(255,255,255,0.04)`, primary text `#F4F5F7`, secondary text `#9299AA`, muted text `#5D6475`, primary accent `#8B8DFF`, secondary accent `#7DD3FC`, and border `rgba(255,255,255,0.08)`. Use Inter with Cyrillic support. Desktop type: H1 64–72px, H2 40–48px, H3 24–28px, body 16–18px, secondary 14–15px, technical labels 11–12px uppercase with letter spacing. Mobile H1: 40–44px. Use a desktop max width near 1440px, content width 1200–1280px, and a 12-column desktop grid. Support 320px through wide desktop, using 390px as the primary mobile reference; prevent horizontal overflow. Use 20px large-card radii, 12–16px small-card radii, 10–12px button radii, and pill-shaped tags. Icons should be fine outline, Lucide-like, and 16–20px.

Favor deep black/navy/purple, credible cosmic depth, fine orbit lines and coordinate grids, star fields and planets, restrained glow, translucent panels, and clean typography. Avoid excess gold, candles, tarot, witchcraft/occult styling, cartoon moons, excessive glow, clutter, heavy borders, and visual noise. Preserve the approved concept; raise UX or visual-direction changes for user approval before implementing them.

## Motion, accessibility, and performance

Keep motion slow and subtle: stars may cycle over 20–60 seconds; orbit motion should be slow; hover transitions 200–300ms; page transitions 300–500ms; large reveals 600–1000ms. Honor `prefers-reduced-motion`; avoid aggressive continuous motion. Support keyboard navigation, visible focus, appropriate accessible names, semantic HTML, and sufficient contrast. Prioritize fast initial rendering, minimal JavaScript, lazy loading, and optimized images. Do not load Three.js on routes that do not need it.

## Product requirements

The homepage section order is: global current event, CelestialScene, personal horoscope, metrics, calendar, events, materials. Its hero uses the label `ASTROLOGICAL MAP`, date, heading “Что происходит на небе сегодня”, short description, CTA “Открыть свой прогноз”, secondary CTA “Смотреть календарь”, a large CelestialScene, and a current-event glass card. The personal forecast selects one of twelve signs without registration and persists the choice in `localStorage`; include date, main forecast, Love/Work/Energy/Finance, key moment, suggested action, things to avoid, points to watch, and the global event's influence.

Calendar supports month and list views with events marked on dates and no mobile overflow. Events are a Cosmic Timeline with All, Moon, Retrograde, Eclipses, Transitions, and Conjunctions filters. Zodiac detail includes sign, dates, element, modality, rulers, CelestialScene, traits, strengths, challenges, relationships, work, money, compatibility, and a current-sign section. Compatibility selects two signs and gives overall, Love, Communication, Passion, Long-term, attraction, tension, and balancing guidance in structured data. About explains the project, data sources/calculation, interpretation process, and FAQ, clearly distinguishing astronomy and astrology.

## SEO, advertising, and analytics

Every page needs a title, meta description, canonical URL, Open Graph metadata, and semantic HTML. Provide sitemap, `robots.txt`, clean URLs, and structured data where appropriate. Include an `AdSlot` abstraction, but hide it on the MVP when no real advertisement is configured; never render empty ad rectangles. Provide `track(eventName, payload)` as an analytics abstraction without an external analytics provider in the MVP, leaving room for self-hosted analytics later.

## Security and configuration

Add a correct `.gitignore` when project files are introduced. Never commit `.env` secrets, tokens, passwords, API keys, or private data. Keep local configuration out of version control and document sanitized examples when needed.

## Development workflow and validation

Do not attempt the whole product in one stage. Before each major stage, inspect the current implementation, understand its architecture, preserve working features, and reuse existing components. After each stage, run the relevant checks, verify responsive layouts, check browser console errors, horizontal overflow, accessibility, and fidelity to approved references. When a technical choice would change UX or visual direction, explain the tradeoff and wait for user approval. Do not start the next major stage without user confirmation.

The first implementation stage is limited to: the base Astro + React + TypeScript + Tailwind project; ESLint and Prettier; foundational directories and design tokens; reusable base components; CelestialScene foundation; homepage `/`; responsive desktop/mobile behavior; and necessary tests/checks. Do not fully implement other routes in that stage. When the user requests checks, run the appropriate project commands and report their results.

## Git and delivery

The existing GitHub remote is `https://github.com/Iuliia-D/astra-astrology.git`. Keep the primary branch named `master`; do not rename it, create another remote, or create a new GitHub repository. For a logically complete implementation stage, inspect the changes, run required checks, make a clear commit, and push to `master` when the user has authorized that stage. Never commit secrets or private data. For the current documentation-only update, do not create application source, commit, or push unless explicitly requested.
