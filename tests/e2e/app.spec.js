const { test, expect } = require('@playwright/test');

test('application loads successfully', async ({ page }) => {
    await page.goto(process.env.BASE_URL);

    await expect(page).toHaveTitle(/Jenkins Capstone/);
});

test('health endpoint is healthy', async ({ request }) => {
    const response = await request.get(`${process.env.BASE_URL}/health`);

    expect(response.status()).toBe(200);
    expect(await response.text()).toBe('healthy');
});