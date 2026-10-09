import { expect, test, type Page } from '@playwright/test';

function collectBrowserErrors(page: Page) {
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(message.text());
  });
  return errors;
}

test('homepage is responsive and remembers a zodiac selection', async ({ page }) => {
  const browserErrors = collectBrowserErrors(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Что происходит на небе сегодня' })).toBeVisible();
  await page.getByRole('button', { name: /Скорпион/ }).click();
  await expect(page.getByRole('heading', { name: 'Скорпион' })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(390);
  await page.reload();
  await expect(page.getByRole('button', { name: /Скорпион/ })).toHaveAttribute(
    'aria-pressed',
    'true',
  );
  expect(browserErrors).toEqual([]);
});

test('homepage renders at a 1440px viewport without horizontal overflow', async ({ page }) => {
  const browserErrors = collectBrowserErrors(page);
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto('/');
  await expect(page.locator('.celestial-scene')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(1440);
  expect(browserErrors).toEqual([]);
});

test('page has accessible landmarks, keyboard focus, and reduced-motion support', async ({
  page,
}) => {
  await page.goto('/');
  expect(await page.locator('html').getAttribute('lang')).toBe('ru');
  expect(await page.getByRole('heading', { level: 1 }).count()).toBe(1);
  expect(
    await page.evaluate(
      () =>
        Array.from(document.querySelectorAll('a, button, summary')).filter(
          (element) => !element.getAttribute('aria-label') && !element.textContent?.trim(),
        ).length,
    ),
  ).toBe(0);
  await page.keyboard.press('Tab');
  expect(
    await page.evaluate(() => (document.activeElement as HTMLElement).matches(':focus-visible')),
  ).toBe(true);
  await page.emulateMedia({ reducedMotion: 'reduce' });
  expect(await page.evaluate(() => matchMedia('(prefers-reduced-motion: reduce)').matches)).toBe(
    true,
  );
  expect(
    await page
      .locator('.scene-stars circle')
      .first()
      .evaluate((element) => getComputedStyle(element).animationDuration),
  ).toMatch(/0s|1e-05s|0\.00001s|0\.01ms/);
});
