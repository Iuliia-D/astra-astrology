import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://127.0.0.1:4321',
    ...devices['Desktop Chrome'],
    ...(process.env.PLAYWRIGHT_CHANNEL === 'chrome' ? { channel: 'chrome' as const } : {}),
  },
  webServer: process.env.PLAYWRIGHT_EXTERNAL_SERVER
    ? undefined
    : {
        command: 'npm run dev -- --host 127.0.0.1',
        port: 4321,
        reuseExistingServer: !process.env.CI,
        env: { ASTRO_TELEMETRY_DISABLED: '1' },
      },
});
