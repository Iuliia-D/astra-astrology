import { expect, test } from '@playwright/test';

test('zodiac catalog opens the shared sign profile and today forecast', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/zodiac/');
  await expect(page.getByRole('heading', { name: 'Знаки зодиака' })).toBeVisible();
  await expect(page.locator('.zodiac-directory-card')).toHaveCount(12);
  await page.locator('.zodiac-directory-card').first().click();
  await expect(page).toHaveURL(/\/zodiac\/aries\/$/);
  await expect(page.getByRole('heading', { name: 'Овен', exact: true })).toBeVisible();
  await expect(page.getByRole('link', { name: /Гороскоп на сегодня/ })).toHaveAttribute(
    'href',
    '/horoscope/?sign=aries#top',
  );
  await expect(page.locator('.desktop-nav [aria-current="page"]')).toHaveText('Знаки');
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(390);
});

test('calendar switches views, navigates months, and links marked dates to event details', async ({
  page,
}) => {
  await page.setViewportSize({ width: 768, height: 1000 });
  await page.goto('/calendar/');
  await page.getByRole('button', { name: 'Список' }).click();
  await expect(page.locator('.calendar-event-row')).toHaveCount(3);
  await page.getByRole('button', { name: 'Следующий месяц' }).click();
  await expect(page.locator('.calendar-toolbar__month')).toContainText('ноябрь 2026');
  await expect(page.locator('.calendar-event-row')).toHaveCount(2);
  await page.locator('.calendar-view-toggle button').first().click();
  await page.locator('a.month-grid__day[href="/calendar/?date=2026-11-05"]').click();
  await expect(page.locator('.calendar-selected-day h2')).toContainText('5 ноября');
  await expect(page.locator('.calendar-selected-day__events a')).toHaveAttribute(
    'href',
    '/events/eclipse-demo/',
  );
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(768);
});

test('event filters lead to a detail page with separated astronomy and astrology panels', async ({
  page,
}) => {
  await page.goto('/events/');
  await page.getByRole('button', { name: 'Затмения' }).click();
  await expect(page.locator('.events-timeline__item')).toHaveCount(1);
  await page.locator('.events-timeline__item').click();
  await expect(page).toHaveURL(/\/events\/eclipse-demo\/$/);
  await expect(page.locator('.event-data-content h2')).toHaveText('Астрономические данные');
  await page.getByRole('button', { name: 'Астрология' }).click();
  await expect(page.locator('.event-data-content h2')).toHaveText('Астрологическая интерпретация');
  await expect(page.locator('.event-related-signs > div:last-child a')).toHaveCount(4);
  await expect(page.locator('.desktop-nav [aria-current="page"]')).toHaveText('События');
});
