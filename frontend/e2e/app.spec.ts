import { test, expect } from '@playwright/test';

test('research workflow, uncertainty and mobile layout', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Broadway Tenant')).toBeVisible();
  await expect(page.getByText('Why is the default composite blank?')).toBeVisible();
  await page.getByRole('button', { name: 'Use available-data model' }).click();
  await expect(page).toHaveURL(/wPolicy=0/);
  await expect(page.locator('.leaflet-overlay-pane path[fill-opacity="0.77"]').first()).toBeAttached({ timeout: 15000 });
  await page.getByRole('button', { name: 'Guided story' }).click();
  await expect(page.getByText('GUIDED ANALYSIS')).toBeVisible();
  await page.getByRole('button', { name: /Next/ }).click();
  await expect(page.getByText('The renter layer is visibly unavailable')).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await page.getByRole('button', { name: 'Research controls' }).click();
  await expect(page.locator('.controls')).toHaveClass(/open/);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test('author and methodology', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('header a')).toHaveAttribute('href', 'https://www.linkedin.com/in/hengyin-liao-0aab05245/');
  await page.getByRole('button', { name: 'Data & methodology' }).click();
  await expect(page.getByRole('dialog')).toContainText('Missing means unknown');
});
