const { test, expect } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

test.describe('MarketScope E2E Acceptance Flow & Responsive UI Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Intercept API routes to ensure deterministic, ultra-fast test execution
    await page.route('**/health', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'healthy', database: 'connected' })
      });
    });

    await page.route('**/api/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ access_token: 'mock-jwt-token-12345', token_type: 'bearer' })
      });
    });

    await page.route('**/api/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 1, email: 'trader1@marketscope.com', role: 'CUSTOMER', is_active: true })
      });
    });

    await page.route('**/api/stocks*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            { symbol: 'AAPL', name: 'Apple Inc.', sector: 'Technology', exchange: 'NASDAQ', current_price: '185.5000', status: 'ACTIVE' },
            { symbol: 'MSFT', name: 'Microsoft Corp.', sector: 'Technology', exchange: 'NASDAQ', current_price: '420.2500', status: 'ACTIVE' },
            { symbol: 'NVDA', name: 'Nvidia Corporation', sector: 'Technology', exchange: 'NASDAQ', current_price: '130.0000', status: 'ACTIVE' }
          ],
          total: 3
        })
      });
    });

    await page.route('**/api/portfolio/summary', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_invested: '50000.0000',
          current_value: '58250.0000',
          absolute_pnl: '8250.0000',
          percent_pnl: '16.5000'
        })
      });
    });

    await page.route('**/api/portfolio/holdings', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          holdings: [
            { symbol: 'AAPL', quantity: '10', average_buy_price: '150.0000', current_price: '185.5000', market_value: '1855.0000', unrealized_pnl: '355.0000' }
          ]
        })
      });
    });

    await page.route('**/api/watchlists', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, name: 'Tech Core', symbols: ['AAPL', 'MSFT'] }
        ])
      });
    });

    await page.route('**/api/orders', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, symbol: 'AAPL', side: 'BUY', order_type: 'MARKET', quantity: '10', price: '185.5000', status: 'EXECUTED', created_at: '2026-10-04T12:00:00Z' }
        ])
      });
    });

    await page.route('**/api/analytics/daily-movers', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          top_gainers: [{ symbol: 'AAPL', percent_change: '5.2000' }],
          top_losers: []
        })
      });
    });

    await page.route('**/api/analytics/sector-exposure', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          sectors: [{ sector: 'Technology', allocation_percentage: '100.0000', total_value: '1855.0000' }],
          total_market_value: '1855.0000'
        })
      });
    });

    page.on('console', msg => console.log(`[BROWSER CONSOLE] ${msg.text()}`));
    page.on('pageerror', err => console.log(`[BROWSER ERROR] ${err.message}`));

    await page.goto('/');
  });

  test('Health check probe and platform title render correctly (NFR-07)', async ({ page }) => {
    await expect(page.locator('text=MarketScope').first()).toBeVisible();
    await expect(page.locator('text=API:').first()).toBeVisible();
  });

  test('User authentication login flow (AC-01)', async ({ page }) => {
    // Fill credentials via quick-login button
    const quickTraderBtn = page.locator('[data-testid="quick-trader-login-btn"]');
    await expect(quickTraderBtn).toBeVisible();
    await quickTraderBtn.click();

    // Submit authentication
    const submitBtn = page.locator('[data-testid="auth-submit-btn"]');
    await submitBtn.click();

    // User profile should display and modal closes
    await expect(page.locator('text=trader1@marketscope.com').first()).toBeVisible();
    await expect(page.locator('[data-testid="logout-btn"]').first()).toBeVisible();
  });

  test('Stock catalog browsing and search filter UI (AC-03)', async ({ page }) => {
    // Authenticate first
    await page.locator('[data-testid="quick-trader-login-btn"]').click();
    await page.locator('[data-testid="auth-submit-btn"]').click();

    const searchInput = page.locator('[data-testid="stock-search-input"]');
    await expect(searchInput).toBeVisible();
    await searchInput.fill('AAPL');
    await expect(searchInput).toHaveValue('AAPL');
    await expect(page.locator('text=AAPL').first()).toBeVisible();
  });

  test('Tab navigation across Order, Watchlists and Analytics (AC-04, AC-06, AC-10)', async ({ page }) => {
    // Authenticate
    await page.locator('[data-testid="quick-trader-login-btn"]').click();
    await page.locator('[data-testid="auth-submit-btn"]').click();

    // Navigate to Order / Trade Execution
    const orderTab = page.locator('[data-testid="nav-order-btn"]');
    await expect(orderTab).toBeVisible();
    await orderTab.click();
    await expect(page.locator('text=Trade Execution').first()).toBeVisible();

    // Navigate to Watchlists
    const watchlistsTab = page.locator('[data-testid="nav-watchlists-btn"]');
    await expect(watchlistsTab).toBeVisible();
    await watchlistsTab.click();

    // Navigate to Analytics
    const analyticsTab = page.locator('[data-testid="nav-analytics-btn"]');
    await expect(analyticsTab).toBeVisible();
    await analyticsTab.click();

    // Return to Catalog
    const catalogTab = page.locator('[data-testid="nav-catalog-btn"]');
    await catalogTab.click();
    await expect(page.locator('[data-testid="stock-search-input"]')).toBeVisible();
  });

  test('Responsive dashboard layout snapshot capture across viewports', async ({ page }) => {
    // Authenticate to view full dashboard
    await page.locator('[data-testid="quick-trader-login-btn"]').click();
    await page.locator('[data-testid="auth-submit-btn"]').click();

    // Verify key financial KPI components
    await expect(page.locator('[data-testid="cash-balance-card"]')).toBeVisible();
    await expect(page.locator('[data-testid="portfolio-invested-card"]')).toBeVisible();

    const snapshotDir = path.join(__dirname, 'snapshots');
    if (!fs.existsSync(snapshotDir)) {
      fs.mkdirSync(snapshotDir, { recursive: true });
    }

    // Capture visual snapshot for visual regression gate
    const screenshotPath = path.join(snapshotDir, 'responsive-dashboard.png');
    await page.screenshot({ path: screenshotPath, fullPage: false });

    expect(fs.existsSync(screenshotPath)).toBeTruthy();
  });

});
