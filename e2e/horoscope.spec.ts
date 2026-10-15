import { expect, test } from '@playwright/test';

test('horoscope selector updates the forecast and persists the chosen sign', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/horoscope/');
  await expect(page.getByRole('heading', { name: 'Гороскоп на сегодня' })).toBeVisible();
  await page.getByRole('button', { name: /Скорпион/ }).click();
  await expect(page.getByRole('status')).toContainText('Скорпион');
  await expect(page.getByRole('status')).toContainText('Демонстрационные данные не отображаются.');
  await expect(page.locator('.horoscope-card__overview')).toHaveCount(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(390);
  await page.reload();
  await expect(page.getByRole('button', { name: /Скорпион/ })).toHaveAttribute(
    'aria-pressed',
    'true',
  );
});

test('horoscope page hides unpublished event blocks and preserves sign links on desktop', async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto('/horoscope/');
  await expect(page.getByRole('status')).toBeVisible();
  await expect(page.locator('.horoscope-scene')).toHaveCount(0);
  await expect(page.getByRole('heading', { name: 'Ключевой момент дня' })).toHaveCount(0);
  await expect(page.locator('.horoscope-event__link')).toHaveCount(0);
  await expect(page.getByText('16:30 — 18:00')).toHaveCount(0);
  await expect(page.getByRole('link', { name: /Овен/ })).toHaveAttribute(
    'href',
    '/horoscope/?sign=aries#top',
  );
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(1440);
});
