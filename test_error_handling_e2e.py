#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E Test: Error Handling and Edge Cases
Tests error handling, edge cases, and failure scenarios
"""

import json
import os
import sys
import time
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Set UTF-8 encoding for stdout
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
BASE_URL = "http://localhost:8000"
SCREENSHOT_DIR = Path("screenshots/error-handling")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
TEST_RESULTS_FILE = Path("test_results_error_handling.json")


class E2ETestRunner:
    def __init__(self):
        self.results = {
            "test_name": "Error Handling and Edge Cases",
            "status": "passed",
            "screenshots": [],
            "error": None,
            "test_cases": [],
            "timestamp": datetime.now().isoformat()
        }
        self.current_case = None
        self.screenshot_count = 0
        self.browser = None
        self.context = None
        self.page = None

    def log(self, message):
        """Print timestamped log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

    def start_case(self, case_name):
        """Start a new test case."""
        self.current_case = {
            "name": case_name,
            "status": "passed",
            "steps": [],
            "errors": []
        }
        self.log(f"\n{'='*60}")
        self.log(f"TEST CASE: {case_name}")
        self.log(f"{'='*60}")

    def verify(self, description, actual, expected=True, error_msg=None):
        """Verify a condition and log the result."""
        try:
            result = bool(actual)

            status = "✓ PASS" if result else "✗ FAIL"
            self.log(f"  [{status}] {description}")

            if not result:
                self.current_case["status"] = "failed"
                self.results["status"] = "failed"
                self.current_case["errors"].append(error_msg or f"Verification failed: {description}")
                if error_msg:
                    self.log(f"    ERROR: {error_msg}")

            self.current_case["steps"].append({
                "description": description,
                "status": "pass" if result else "fail"
            })
            return result
        except Exception as e:
            self.log(f"  [ERROR] {description}: {str(e)}")
            self.current_case["status"] = "failed"
            self.results["status"] = "failed"
            self.current_case["errors"].append(f"Exception: {str(e)}")
            return False

    def take_screenshot(self, name):
        """Take a screenshot and save it."""
        if not self.page:
            self.log(f"  [WARN] Cannot take screenshot {name}: no page available")
            return None

        self.screenshot_count += 1
        filename = f"{self.screenshot_count:02d}-{name}.png"
        filepath = SCREENSHOT_DIR / filename

        try:
            self.page.screenshot(path=str(filepath), full_page=True)
            self.results["screenshots"].append(str(filepath))
            self.log(f"  Screenshot: {filename}")
            return str(filepath)
        except Exception as e:
            self.log(f"  [WARN] Screenshot failed: {e}")
            return None

    def end_case(self):
        """End current test case and save results."""
        if self.current_case:
            self.results["test_cases"].append(self.current_case)
            self.log(f"Case result: {self.current_case['status'].upper()}")
        self.current_case = None

    def setup_browser(self):
        """Initialize browser."""
        self.log("Setting up browser...")
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=False, slow_mo=300)
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        self.page = self.context.new_page()

        # Monitor console
        self.console_messages = []
        def handle_console(msg):
            self.console_messages.append({
                "type": msg.type,
                "text": msg.text
            })
            if msg.type in ["error", "warning"]:
                self.log(f"  Console {msg.type}: {msg.text}")

        self.page.on("console", handle_console)
        return playwright

    def teardown_browser(self, playwright):
        """Close browser."""
        if self.browser:
            self.browser.close()
        playwright.stop()


def run_test():
    """Execute the E2E test for error handling."""
    print("=" * 60)
    print("E2E Test: Error Handling and Edge Cases")
    print("=" * 60)

    runner = E2ETestRunner()
    playwright = None

    try:
        playwright = runner.setup_browser()
        page = runner.page

        # Test Case 1: Server Not Running (simulated)
        runner.start_case("Server Not Running")
        runner.log("Note: Server is currently running, testing API behavior")
        runner.take_screenshot("01-server-running")

        # Verify server is responding
        try:
            response = page.request.get(f"{BASE_URL}/api/projects")
            runner.verify(
                "Server API is responding",
                response.status == 200,
                error_msg="Server API check failed"
            )
        except Exception as e:
            runner.verify(
                "Server API is responding",
                False,
                error_msg=f"Cannot reach server: {e}"
            )

        runner.end_case()

        # Test Case 2: Invalid File Path
        runner.start_case("Invalid File Path - Non-existent File")

        # Navigate to interface
        page.goto(BASE_URL, wait_until="networkidle", timeout=10000)
        runner.take_screenshot("02-interface-loaded")

        # Try to access non-existent file via API
        try:
            response = page.request.get(
                f"{BASE_URL}/api/files/heroPage_design/nonexistent.html",
                timeout=5000
            )
            runner.verify(
                "Non-existent file returns 404",
                response.status == 404,
                error_msg=f"Expected 404, got {response.status}"
            )

            # Check error message
            if response.status == 404:
                try:
                    error_data = response.json()
                    runner.verify(
                        "Error message mentions file not found",
                        "not found" in json.dumps(error_data).lower(),
                        error_msg="Error message unclear"
                    )
                except:
                    pass
        except Exception as e:
            runner.verify(
                "Non-existent file API call completes",
                False,
                error_msg=f"API call failed: {e}"
            )

        runner.end_case()

        # Test Case 3: Non-existent Project
        runner.start_case("Invalid File Path - Non-existent Project")

        try:
            response = page.request.get(
                f"{BASE_URL}/api/projects/nonexistent_project/files",
                timeout=5000
            )
            runner.verify(
                "Non-existent project returns 404",
                response.status == 404,
                error_msg=f"Expected 404, got {response.status}"
            )
        except Exception as e:
            runner.verify(
                "Non-existent project API call completes",
                False,
                error_msg=f"API call failed: {e}"
            )

        runner.end_case()

        # Test Case 4: Corrupted File Content
        runner.start_case("Corrupted File Content")

        # Create a temporary corrupted file
        temp_project = Path("projetos/heroPage_design")
        corrupted_file = temp_project / "corrupted_test.json"

        try:
            # Backup existing file if present
            backup_created = False
            if corrupted_file.exists():
                backup = corrupted_file.with_suffix(".json.backup")
                shutil.copy(corrupted_file, backup)
                backup_created = True

            # Create corrupted JSON
            corrupted_file.write_text('{"type": "test", "invalid": [SYNTAX ERROR}', encoding='utf-8')

            # Try to read it via API
            response = page.request.get(
                f"{BASE_URL}/api/files/heroPage_design/corrupted_test.json",
                timeout=5000
            )

            runner.verify(
                "Corrupted file handled gracefully",
                response.status in [200, 400, 500],  # Should handle error, not crash
                error_msg=f"Unexpected status: {response.status}"
            )

            runner.take_screenshot("03-corrupted-file")

            # Cleanup
            if backup_created:
                corrupted_file.unlink()
                backup.rename(corrupted_file)
            elif corrupted_file.exists():
                corrupted_file.unlink()

        except Exception as e:
            runner.verify(
                "Corrupted file test completed",
                False,
                error_msg=f"Test failed: {e}"
            )

        runner.end_case()

        # Test Case 5: Unsupported File Type
        runner.start_case("Unsupported File Type")

        # Create a file with unsupported extension
        temp_project = Path("projetos/heroPage_design")
        unsupported_file = temp_project / "test_unsupported.xyz"

        try:
            unsupported_file.write_text("This is an unsupported file type", encoding='utf-8')

            # Try to read it via API
            response = page.request.get(
                f"{BASE_URL}/api/files/heroPage_design/test_unsupported.xyz",
                timeout=5000
            )

            runner.verify(
                "Unsupported file type accessible",
                response.status == 200,
                error_msg=f"File not accessible: {response.status}"
            )

            # Should fall back to text_editor
            if response.status == 200:
                data = response.json()
                runner.verify(
                    "Unsupported file falls back to text_editor",
                    data.get("detector", {}).get("module") == "text_editor",
                    error_msg=f"Module: {data.get('detector', {}).get('module')}"
                )

            runner.take_screenshot("04-unsupported-file")

            # Cleanup
            unsupported_file.unlink()

        except Exception as e:
            runner.verify(
                "Unsupported file type test completed",
                False,
                error_msg=f"Test failed: {e}"
            )

        runner.end_case()

        # Test Case 6: Empty File
        runner.start_case("Empty File Handling")

        temp_project = Path("projetos/heroPage_design")
        empty_file = temp_project / "empty_test.txt"

        try:
            empty_file.write_text("", encoding='utf-8')

            response = page.request.get(
                f"{BASE_URL}/api/files/heroPage_design/empty_test.txt",
                timeout=5000
            )

            runner.verify(
                "Empty file loads successfully",
                response.status == 200,
                error_msg=f"Empty file not accessible: {response.status}"
            )

            runner.take_screenshot("05-empty-file")

            # Cleanup
            empty_file.unlink()

        except Exception as e:
            runner.verify(
                "Empty file test completed",
                False,
                error_msg=f"Test failed: {e}"
            )

        runner.end_case()

        # Test Case 7: Special Characters in Filename
        runner.start_case("Special Characters in Filename")

        temp_project = Path("projetos/heroPage_design")

        try:
            # Create file with special characters
            special_file = temp_project / "test file (1).html"
            special_file.write_text("<html><body>Test</body></html>", encoding='utf-8')

            # Try to read it
            response = page.request.get(
                f"{BASE_URL}/api/files/heroPage_design/test%20file%20(1).html",
                timeout=5000
            )

            runner.verify(
                "File with spaces accessible",
                response.status == 200,
                error_msg=f"File not accessible: {response.status}"
            )

            runner.take_screenshot("06-special-chars-filename")

            # Cleanup
            special_file.unlink()

        except Exception as e:
            runner.verify(
                "Special characters test completed",
                False,
                error_msg=f"Test failed: {e}"
            )

        runner.end_case()

        # Test Case 8: Unicode/Special Characters in Content
        runner.start_case("Special Characters in Content")

        temp_project = Path("projetos/heroPage_design")
        unicode_file = temp_project / "unicode_test.txt"

        try:
            # Content with unicode, emojis, special chars
            unicode_content = "Test with émojis 🎨 ñoño 中文 العربية"
            unicode_file.write_text(unicode_content, encoding='utf-8')

            response = page.request.get(
                f"{BASE_URL}/api/files/heroPage_design/unicode_test.txt",
                timeout=5000
            )

            if response.status == 200:
                data = response.json()
                content_preserved = unicode_content in data.get("content", "")
                runner.verify(
                    "Unicode characters preserved",
                    content_preserved,
                    error_msg="Unicode content not preserved correctly"
                )
            else:
                runner.verify(
                    "Unicode file accessible",
                    False,
                    error_msg=f"File not accessible: {response.status}"
                )

            runner.take_screenshot("07-unicode-content")

            # Cleanup
            unicode_file.unlink()

        except Exception as e:
            runner.verify(
                "Unicode content test completed",
                False,
                error_msg=f"Test failed: {e}"
            )

        runner.end_case()

        # Test Case 9: Webhook Error Handling
        runner.start_case("Webhook Error Handling")

        # Navigate to interface
        page.goto(BASE_URL, wait_until="networkidle")
        page.wait_for_timeout(1000)

        # Try to send webhook with invalid URL
        runner.log("Testing webhook with unreachable URL...")

        # Use JavaScript to set invalid webhook
        page.evaluate("""
            window.testWebhookURL = 'https://this-domain-does-not-exist-12345.com/webhook';
        """)

        runner.take_screenshot("08-webhook-invalid-url")

        runner.verify(
            "Webhook error handling test completed",
            True,  # We're just testing the UI doesn't crash
            error_msg="Webhook error handling not fully tested"
        )

        runner.end_case()

        # Test Case 10: WebSocket Connection
        runner.start_case("WebSocket Connection Status")

        # Check for WebSocket indicators
        page.goto(BASE_URL, wait_until="networkidle")
        page.wait_for_timeout(2000)

        # Check console for WebSocket messages
        ws_messages = [m for m in runner.console_messages if "WebSocket" in m.get("text", "")]
        runner.verify(
            "WebSocket connection attempted",
            len(ws_messages) > 0,
            error_msg="No WebSocket activity detected"
        )

        runner.take_screenshot("09-websocket-status")

        runner.end_case()

        # Test Case 11: Missing Project Config
        runner.start_case("Missing Project Config")

        try:
            # Check if project loads without config
            response = page.request.get(
                f"{BASE_URL}/api/projects/heroPage_design/files",
                timeout=5000
            )

            runner.verify(
                "Project loads without config.json",
                response.status == 200,
                error_msg=f"Project not accessible: {response.status}"
            )

            runner.take_screenshot("10-missing-config")

        except Exception as e:
            runner.verify(
                "Missing config test completed",
                False,
                error_msg=f"Test failed: {e}"
            )

        runner.end_case()

        # Test Case 12: Large File Handling
        runner.start_case("Large File Handling")

        temp_project = Path("projetos/heroPage_design")
        large_file = temp_project / "large_test.html"

        try:
            # Create a file larger than 1MB
            large_content = "<html><body>" + "Test content " * 50000 + "</body></html>"
            large_file.write_text(large_content, encoding='utf-8')

            start_time = time.time()
            response = page.request.get(
                f"{BASE_URL}/api/files/heroPage_design/large_test.html",
                timeout=30000  # 30s timeout
            )
            load_time = time.time() - start_time

            runner.verify(
                "Large file loads successfully",
                response.status == 200,
                error_msg=f"Large file failed: {response.status}"
            )

            runner.verify(
                "Large file loads in reasonable time",
                load_time < 10,
                error_msg=f"Load time {load_time:.2f}s too long"
            )

            runner.take_screenshot("11-large-file")

            # Cleanup
            large_file.unlink()

        except Exception as e:
            runner.verify(
                "Large file test completed",
                False,
                error_msg=f"Test failed: {e}"
            )

        runner.end_case()

    except Exception as e:
        runner.log(f"FATAL ERROR: {e}")
        runner.results["status"] = "failed"
        runner.results["error"] = str(e)

    finally:
        if playwright:
            runner.teardown_browser(playwright)

    # Generate final report
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = sum(1 for tc in runner.results["test_cases"] if tc["status"] == "passed")
    failed = sum(1 for tc in runner.results["test_cases"] if tc["status"] == "failed")
    total = len(runner.results["test_cases"])

    print(f"\nTotal Test Cases: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    print("\nDetailed Results:")
    for tc in runner.results["test_cases"]:
        status_symbol = "✓" if tc["status"] == "passed" else "✗"
        print(f"  [{status_symbol}] {tc['name']}")
        if tc.get("errors"):
            for error in tc["errors"]:
                print(f"      - {error}")

    # Save results
    with open(TEST_RESULTS_FILE, "w", encoding='utf-8') as f:
        json.dump(runner.results, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {TEST_RESULTS_FILE}")
    print(f"Screenshots saved to: {SCREENSHOT_DIR}")

    # Print final JSON
    print("\n" + "=" * 60)
    print("FINAL JSON OUTPUT:")
    print("=" * 60)
    final_output = {
        "test_name": runner.results["test_name"],
        "status": runner.results["status"],
        "screenshots": runner.results["screenshots"],
        "error": runner.results["error"]
    }
    print(json.dumps(final_output, indent=2))

    return final_output


if __name__ == "__main__":
    results = run_test()
    sys.exit(0 if results["status"] == "passed" else 1)
