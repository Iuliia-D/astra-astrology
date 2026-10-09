import { expect, test } from '@playwright/test';

test('horoscope selector updates the forecast and persists the chosen sign', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/horoscope/');
  await expect(page.getByRole('heading', { name: 'Гороскоп на сегодня' })).toBeVisible();
  await page.getByRole('button', { name: /Скорпион/ }).click();
  await expect(page.getByRole('heading', { name: 'Скорпион' })).toBeVisible();
  await expect(page.locator('.horoscope-card__overview')).toContainText('Сосредоточенность');
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(390);
  await page.reload();
  await expect(page.getByRole('button', { name: /Скорпион/ })).toHaveAttribute(
    'aria-pressed',
    'true',
  );
});

test('horoscope page renders its scene, key moment, event, and sign links on desktop', async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto('/horoscope/');
  await expect(page.locator('.horoscope-scene')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Ключевой момент дня' })).toBeVisible();
  await expect(page.getByRole('link', { name: /Овен/ })).toHaveAttribute(
    'href',
    '/horoscope/?sign=aries#top',
  );
  await expect(page.locator('.horoscope-event__link')).toHaveAttribute(
    'href',
    '/events/mercury-retrograde-demo/',
  );
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(1440);
});
