const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
    testDir: './tests/e2e',
    timeout: 30 * 1000,

    reporter: [
        ['html'],
        ['junit', { outputFile: 'playwright-results.xml' }]
    ]
});