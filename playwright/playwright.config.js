import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",

  timeout: 120000,

  expect: {
    timeout: 10000,
  },

  reporter: [["list"], ["html", { open: "never" }]],

  retries: process.env.CI ? 2 : 0,

  forbidOnly: !!process.env.CI,

  use: {
    baseURL: "http://127.0.0.1:5178",
    headless: true,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },

  projects: [
    {
      name: "chromium",
      use: {
        browserName: "chromium",
      },
    },
  ],

  webServer: {
    command: "npm --prefix ../frontend run dev -- --host 127.0.0.1 --port 5178",
    url: "http://127.0.0.1:5178/contacts",
    reuseExistingServer: true,
    timeout: 120000,
  },
});