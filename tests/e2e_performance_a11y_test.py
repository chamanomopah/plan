#!/usr/bin/env python3
"""
E2E Test: Performance and Accessibility
Tests performance metrics, accessibility features, responsive design, and browser compatibility.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

# Configuration
BASE_URL = "http://localhost:8000"
SCREENSHOT_DIR = Path("C:/Users/JOSE/Downloads/n8n_cc_workflows/plan/screenshots/performance-a11y")
RESULTS_FILE = Path("C:/Users/JOSE/Downloads/n8n_cc_workflows/plan/e2e_performance_a11y_results.json")

class PerformanceA11yTest:
    def __init__(self):
        self.results = {
            "test_name": "Performance and Accessibility",
            "status": "passed",
            "screenshots": [],
            "error": None,
            "test_cases": [],
            "start_time": datetime.now().isoformat(),
            "end_time": None
        }
        self.test_cases_results = []

    async def run_all_tests(self):
        """Run all test cases"""
        async with async_playwright() as p:
            # Test with Chrome/Chromium
            print("Starting tests with Chromium...")
            await self.test_with_browser(p, "chromium", "Chromium")

            # Test with Firefox
            print("\nStarting tests with Firefox...")
            await self.test_with_browser(p, "firefox", "Firefox")

            # Try Safari (webkit) if available
            print("\nStarting tests with WebKit...")
            try:
                await self.test_with_browser(p, "webkit", "WebKit")
            except Exception as e:
                print(f"WebKit not available or failed: {e}")

        self.results["end_time"] = datetime.now().isoformat()
        self.results["test_cases"] = self.test_cases_results
        self._save_results()
        return self.results

    async def test_with_browser(self, playwright, browser_type, browser_name):
        """Run tests with a specific browser"""
        browser = await playwright[browser_type].launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        try:
            # Track console errors
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            # Test Case 1: Initial Load Performance
            await self.test_initial_load(page, browser_name)

            # Test Case 2: File Switching Performance
            await self.test_file_switching(page, browser_name)

            # Test Case 3: Real-time Update Performance
            await self.test_realtime_updates(page, browser_name)

            # Test Case 4: Webhook Performance
            await self.test_webhook_performance(page, browser_name)

            # Test Case 5: Memory Usage
            await self.test_memory_usage(page, browser_name)

            # Test Case 6: Accessibility
            await self.test_accessibility(page, browser_name)

            # Test Case 7: Responsive Design
            await self.test_responsive_design(page, browser_name, context)

            # Test Case 8: Browser Compatibility (already testing with this browser)
            await self.test_browser_compatibility(page, browser_name, console_errors)

        except Exception as e:
            print(f"Error during {browser_name} tests: {e}")
            self.results["status"] = "failed"
            self.results["error"] = f"{browser_name}: {str(e)}"
        finally:
            await browser.close()

    async def capture_screenshot(self, page, name, browser_name="chromium"):
        """Capture a screenshot and add to results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}_{browser_name}.png"
        filepath = SCREENSHOT_DIR / filename
        await page.screenshot(path=str(filepath))
        self.results["screenshots"].append(str(filepath))
        print(f"  Screenshot saved: {filename}")
        return filepath

    async def test_initial_load(self, page, browser_name):
        """Test Case 1: Initial Load Performance"""
        print(f"\n[{browser_name}] Test Case 1: Initial Load Performance")
        test_result = {"name": "Initial Load Performance", "status": "passed", "checks": []}

        try:
            # Clear cache and start fresh
            await page.context().clear_cookies()
            await page.context().clear_permissions()

            # Measure page load time
            start_time = time.time()
            response = await page.goto(BASE_URL, wait_until="domcontentloaded")
            load_time = time.time() - start_time

            # Wait for page to be fully interactive
            await page.wait_for_load_state("networkidle")
            interactive_time = time.time() - start_time

            test_result["checks"].append({
                "check": "Page load time",
                "expected": "<= 2s",
                "actual": f"{load_time:.2f}s",
                "passed": load_time <= 2.0
            })

            test_result["checks"].append({
                "check": "Time to interactive",
                "expected": "<= 3s",
                "actual": f"{interactive_time:.2f}s",
                "passed": interactive_time <= 3.0
            })

            # Check for WebSocket connection
            await page.wait_for_selector("body", timeout=5000)

            # Verify elements are loaded
            try:
                await page.wait_for_selector("[data-testid='project-dropdown'], select, #project-select", timeout=3000)
                test_result["checks"].append({"check": "Project dropdown loaded", "passed": True})
            except:
                test_result["checks"].append({"check": "Project dropdown loaded", "passed": False})

            await self.capture_screenshot(page, "01_initial_load", browser_name)

            if any(not c.get("passed", True) for c in test_result["checks"]):
                test_result["status"] = "failed"

        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)

        self.test_cases_results.append(test_result)
        print(f"  Status: {test_result['status']}")

    async def test_file_switching(self, page, browser_name):
        """Test Case 2: File Switching Performance"""
        print(f"\n[{browser_name}] Test Case 2: File Switching Performance")
        test_result = {"name": "File Switching Performance", "status": "passed", "checks": []}

        try:
            # Select a project first
            await page.wait_for_timeout(500)

            # Try to select a project from dropdown
            try:
                dropdown = page.locator("select, [data-testid='project-dropdown'], #project-select").first
                if await dropdown.count() > 0:
                    await dropdown.select_option(index=0)
                    await page.wait_for_timeout(500)
            except:
                pass

            # Measure file switching speed
            file_items = page.locator("[data-testid*='file'], .file-item, [role='listitem'], li")
            count = await file_items.count()

            if count > 0:
                # Click first file and measure time
                start_time = time.time()
                await file_items.first.click()
                switch_time_1 = time.time() - start_time
                await page.wait_for_timeout(300)

                test_result["checks"].append({
                    "check": "First file switch time",
                    "expected": "<= 500ms",
                    "actual": f"{switch_time_1*1000:.0f}ms",
                    "passed": switch_time_1 <= 0.5
                })

                # Click second file if available
                if count > 1:
                    start_time = time.time()
                    await file_items.nth(1).click()
                    switch_time_2 = time.time() - start_time
                    await page.wait_for_timeout(300)

                    test_result["checks"].append({
                        "check": "Second file switch time",
                        "expected": "<= 500ms",
                        "actual": f"{switch_time_2*1000:.0f}ms",
                        "passed": switch_time_2 <= 0.5
                    })

                await self.capture_screenshot(page, "02_file_switching", browser_name)
            else:
                test_result["checks"].append({
                    "check": "Files available for testing",
                    "expected": "At least 1 file",
                    "actual": "No files found",
                    "passed": False
                })

            if any(not c.get("passed", True) for c in test_result["checks"]):
                test_result["status"] = "failed"

        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)

        self.test_cases_results.append(test_result)
        print(f"  Status: {test_result['status']}")

    async def test_realtime_updates(self, page, browser_name):
        """Test Case 3: Real-time Update Performance"""
        print(f"\n[{browser_name}] Test Case 3: Real-time Update Performance")
        test_result = {"name": "Real-time Update Performance", "status": "passed", "checks": []}

        try:
            # Check for WebSocket connection indicators
            await page.wait_for_timeout(1000)

            # Look for connection status indicators
            connection_status = page.locator("[data-testid*='connection'], [data-testid*='status'], .status, .connection")
            if await connection_status.count() > 0:
                test_result["checks"].append({"check": "Connection status indicator found", "passed": True})
            else:
                test_result["checks"].append({"check": "Connection status indicator found", "passed": False, "note": "No visible status indicator"})

            # Check for update mechanism in page scripts
            has_websocket = await page.evaluate("""() => {
                return typeof WebSocket !== 'undefined' || window.__ws__ !== undefined;
            }""")
            test_result["checks"].append({
                "check": "WebSocket support detected",
                "passed": has_websocket
            })

            await self.capture_screenshot(page, "03_realtime_status", browser_name)

            if any(not c.get("passed", True) for c in test_result["checks"]):
                test_result["status"] = "failed"

        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)

        self.test_cases_results.append(test_result)
        print(f"  Status: {test_result['status']}")

    async def test_webhook_performance(self, page, browser_name):
        """Test Case 4: Webhook Performance"""
        print(f"\n[{browser_name}] Test Case 4: Webhook Performance")
        test_result = {"name": "Webhook Performance", "status": "passed", "checks": []}

        try:
            # Look for webhook-related UI elements
            webhook_elements = page.locator("[data-testid*='webhook'], button:has-text('Send'), button:has-text('Webhook'), .webhook")
            count = await webhook_elements.count()

            if count > 0:
                test_result["checks"].append({"check": "Webhook UI elements found", "passed": True})
                await self.capture_screenshot(page, "04_webhook_ui", browser_name)
            else:
                test_result["checks"].append({
                    "check": "Webhook UI elements found",
                    "passed": False,
                    "note": "No webhook buttons found in current view"
                })

            # Check for loading indicators
            loading_indicators = page.locator(".loading, .spinner, [data-testid='loading'], [role='progressbar']")
            test_result["checks"].append({
                "check": "Loading indicators available",
                "passed": await loading_indicators.count() > 0
            })

            if any(not c.get("passed", True) for c in test_result["checks"]):
                test_result["status"] = "failed"

        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)

        self.test_cases_results.append(test_result)
        print(f"  Status: {test_result['status']}")

    async def test_memory_usage(self, page, browser_name):
        """Test Case 5: Memory Usage"""
        print(f"\n[{browser_name}] Test Case 5: Memory Usage")
        test_result = {"name": "Memory Usage", "status": "passed", "checks": []}

        try:
            # Get initial memory metrics
            metrics = await page.evaluate("""() => {
                if (performance.memory) {
                    return {
                        usedJSHeapSize: performance.memory.usedJSHeapSize,
                        totalJSHeapSize: performance.memory.totalJSHeapSize,
                        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                    };
                }
                return null;
            }""")

            if metrics:
                test_result["checks"].append({
                    "check": "Memory metrics available",
                    "passed": True,
                    "usedMB": metrics.get("usedJSHeapSize", 0) / 1024 / 1024
                })
            else:
                test_result["checks"].append({
                    "check": "Memory metrics available",
                    "passed": False,
                    "note": "performance.memory not available in this browser"
                })

            # Simulate file switching to check for memory leaks
            for i in range(5):
                try:
                    file_items = page.locator("[data-testid*='file'], .file-item, [role='listitem'], li")
                    if await file_items.count() > 0:
                        await file_items.nth(i % await file_items.count()).click()
                        await page.wait_for_timeout(200)
                except:
                    pass

            await self.capture_screenshot(page, "05_memory_test", browser_name)

            if any(not c.get("passed", True) for c in test_result["checks"]):
                test_result["status"] = "failed"

        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)

        self.test_cases_results.append(test_result)
        print(f"  Status: {test_result['status']}")

    async def test_accessibility(self, page, browser_name):
        """Test Case 6: Accessibility"""
        print(f"\n[{browser_name}] Test Case 6: Accessibility")
        test_result = {"name": "Accessibility", "status": "passed", "checks": []}

        try:
            # Check for ARIA labels
            aria_elements = await page.evaluate("""() => {
                const elements = document.querySelectorAll('[aria-label], [aria-labelledby], [role]');
                return {
                    ariaLabel: document.querySelectorAll('[aria-label]').length,
                    ariaLabelledby: document.querySelectorAll('[aria-labelledby]').length,
                    roles: document.querySelectorAll('[role]').length,
                    total: elements.length
                };
            }""")

            test_result["checks"].append({
                "check": "ARIA attributes present",
                "expected": "> 0",
                "actual": aria_elements["total"],
                "passed": aria_elements["total"] > 0,
                "details": aria_elements
            })

            # Check for alt text on images
            images_alt = await page.evaluate("""() => {
                const images = document.querySelectorAll('img');
                const withAlt = Array.from(images).filter(img => img.alt || img.getAttribute('aria-label'));
                return {
                    total: images.length,
                    withAlt: withAlt.length,
                    percentage: images.length > 0 ? (withAlt.length / images.length * 100).toFixed(1) : 0
                };
            }""")

            test_result["checks"].append({
                "check": "Images have alt text",
                "expected": "100%",
                "actual": f"{images_alt['percentage']}%",
                "passed": images_alt["total"] == 0 or images_alt["percentage"] == "100.0",
                "details": images_alt
            })

            # Check for form labels
            form_labels = await page.evaluate("""() => {
                const inputs = document.querySelectorAll('input, select, textarea');
                const withLabels = Array.from(inputs).filter(input => {
                    return input.labels && input.labels.length > 0 ||
                           input.getAttribute('aria-label') ||
                           input.getAttribute('aria-labelledby') ||
                           input.closest('label');
                });
                return {
                    total: inputs.length,
                    withLabels: withLabels.length,
                    percentage: inputs.length > 0 ? (withLabels.length / inputs.length * 100).toFixed(1) : 100
                };
            }""")

            test_result["checks"].append({
                "check": "Form inputs have labels",
                "expected": "100%",
                "actual": f"{form_labels['percentage']}%",
                "passed": form_labels["total"] == 0 or form_labels["percentage"] == "100.0",
                "details": form_labels
            })

            # Check for focus management
            await page.keyboard.press("Tab")
            focused = await page.evaluate("""() => {
                const el = document.activeElement;
                return {
                    tagName: el?.tagName,
                    hasFocusIndicator: el ? window.getComputedStyle(el).outline !== 'none' : false
                };
            }""")

            test_result["checks"].append({
                "check": "Keyboard navigation works",
                "passed": focused["tagName"] != "BODY"
            })

            # Check for headings structure
            headings = await page.evaluate("""() => {
                const levels = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
                return {
                    total: levels.length,
                    hasH1: document.querySelectorAll('h1').length > 0
                };
            }""")

            test_result["checks"].append({
                "check": "Page has proper heading structure",
                "passed": headings["hasH1"],
                "details": headings
            })

            # Check for skip links
            skip_links = await page.evaluate("""() => {
                return document.querySelectorAll('a[href^="#"], .skip-link, [data-testid*="skip"]').length;
            }""")

            test_result["checks"].append({
                "check": "Skip links present",
                "passed": skip_links > 0,
                "count": skip_links
            })

            # Check for live regions
            live_regions = await page.evaluate("""() => {
                return document.querySelectorAll('[aria-live], [aria-atomic]').length;
            }""")

            test_result["checks"].append({
                "check": "ARIA live regions for dynamic content",
                "passed": live_regions > 0,
                "count": live_regions
            })

            await self.capture_screenshot(page, "06_accessibility", browser_name)

            if any(not c.get("passed", True) for c in test_result["checks"]):
                test_result["status"] = "failed"

        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)

        self.test_cases_results.append(test_result)
        print(f"  Status: {test_result['status']}")

    async def test_responsive_design(self, page, browser_name, context):
        """Test Case 7: Responsive Design"""
        print(f"\n[{browser_name}] Test Case 7: Responsive Design")
        test_result = {"name": "Responsive Design", "status": "passed", "checks": []}

        try:
            viewports = [
                {"name": "Desktop (1920x1080)", "width": 1920, "height": 1080},
                {"name": "Laptop (1366x768)", "width": 1366, "height": 768},
                {"name": "Tablet (768x1024)", "width": 768, "height": 1024},
                {"name": "Mobile (375x667)", "width": 375, "height": 667}
            ]

            for vp in viewports:
                await page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
                await page.wait_for_timeout(500)

                # Check for horizontal scroll
                has_scroll = await page.evaluate("""() => {
                    return document.body.scrollWidth > document.body.clientWidth;
                }""")

                # Check if main content is visible
                content_visible = await page.evaluate("""() => {
                    const main = document.querySelector('main, [role="main"], .main-content, #app');
                    if (!main) return false;
                    const rect = main.getBoundingClientRect();
                    return rect.width > 0 && rect.height > 0;
                }""")

                passed = not has_scroll and content_visible
                test_result["checks"].append({
                    "check": f"Responsive: {vp['name']}",
                    "passed": passed,
                    "hasHorizontalScroll": has_scroll,
                    "contentVisible": content_visible
                })

                # Capture screenshot for mobile
                if vp["name"] == "Mobile (375x667)":
                    await self.capture_screenshot(page, "07_responsive_mobile", browser_name)

            # Reset to desktop
            await page.set_viewport_size({"width": 1920, "height": 1080})
            await self.capture_screenshot(page, "08_responsive_desktop", browser_name)

            if any(not c.get("passed", True) for c in test_result["checks"]):
                test_result["status"] = "failed"

        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)

        self.test_cases_results.append(test_result)
        print(f"  Status: {test_result['status']}")

    async def test_browser_compatibility(self, page, browser_name, console_errors):
        """Test Case 8: Browser Compatibility"""
        print(f"\n[{browser_name}] Test Case 8: Browser Compatibility")
        test_result = {"name": f"Browser Compatibility ({browser_name})", "status": "passed", "checks": []}

        try:
            # Check for console errors
            test_result["checks"].append({
                "check": "No console errors",
                "passed": len(console_errors) == 0,
                "errorCount": len(console_errors),
                "errors": console_errors[:5]  # First 5 errors
            })

            # Check WebSocket connection
            ws_connected = await page.evaluate("""() => {
                // Check for WebSocket in window or common patterns
                return typeof WebSocket !== 'undefined';
            }""")
            test_result["checks"].append({
                "check": "WebSocket support",
                "passed": ws_connected
            })

            # Check if main features are working
            interactive_elements = await page.evaluate("""() => {
                const buttons = document.querySelectorAll('button:not([disabled])');
                const inputs = document.querySelectorAll('input:not([disabled]), select:not([disabled])');
                return {
                    buttons: buttons.length,
                    inputs: inputs.length
                };
            }""")
            test_result["checks"].append({
                "check": "Interactive elements available",
                "passed": interactive_elements["buttons"] > 0 or interactive_elements["inputs"] > 0,
                "details": interactive_elements
            })

            await self.capture_screenshot(page, f"09_browser_{browser_name.lower()}", browser_name)

            if any(not c.get("passed", True) for c in test_result["checks"]):
                test_result["status"] = "failed"

        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = str(e)

        self.test_cases_results.append(test_result)
        print(f"  Status: {test_result['status']}")

    def _save_results(self):
        """Save results to JSON file"""
        with open(RESULTS_FILE, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {RESULTS_FILE}")


async def main():
    test = PerformanceA11yTest()
    results = await test.run_all_tests()
    print("\n" + "="*60)
    print(f"FINAL STATUS: {results['status'].upper()}")
    print(f"Screenshots captured: {len(results['screenshots'])}")
    if results['error']:
        print(f"Error: {results['error']}")
    print("="*60)
    return results


if __name__ == "__main__":
    asyncio.run(main())
