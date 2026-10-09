import { expect, test } from '@playwright/test';

test('compatibility selectors update the pair and keep demo scores clearly labeled', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/compatibility/');
  await page.getByRole('combobox', { name: 'Первый знак' }).selectOption('scorpio');
  await page.getByRole('combobox', { name: 'Второй знак' }).selectOption('taurus');
  await expect(page.getByRole('heading', { name: 'Скорпион и Телец' })).toBeVisible();
  await expect(page.locator('.compatibility-summary')).toContainText(
    'не меняются в зависимости от выбранной пары',
  );
  await expect(page.locator('.compatibility-metric')).toHaveCount(4);
  await expect(page.locator('.desktop-nav [aria-current="page"]')).toHaveText('Совместимость');
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(390);
});

test('about and service routes explain the MVP and keep the footer at the viewport bottom', async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 1200 });
  await page.goto('/about/');
  await expect(
    page.getByRole('heading', { name: 'Небо как система данных и смыслов' }),
  ).toBeVisible();
  await expect(page.getByText(/Астрология не является научно подтверждённым/)).toBeVisible();
  await page.goto('/privacy/');
  await expect(page.getByRole('heading', { name: 'Конфиденциальность' })).toBeVisible();
  const footer = await page.locator('.site-footer').boundingBox();
  expect(footer).not.toBeNull();
  expect(footer!.y + footer!.height).toBeGreaterThanOrEqual(1199);
  await expect(page.locator('.footer-nav--legal a')).toHaveCount(4);
});
