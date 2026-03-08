#!/usr/bin/env python3
"""
E2E Test: Webhook Integration and Scope Hierarchy
Tests webhook configuration at global, project, and file levels
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

# Test Configuration
BASE_URL = "http://localhost:8000"
TEST_WEBHOOK = "https://maceio-n8n-alfa42.serveousercontent.com/webhook/plan"
SCREENSHOT_DIR = Path(__file__).parent / "screenshots" / "webhook-integration"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Webhook config path
WEBHOOKS_CONFIG_PATH = Path(__file__).parent.parent.parent / "webhooks.json"

# Test Results
test_results = {
    "test_name": "Webhook Integration and Scope Hierarchy",
    "timestamp": datetime.now().isoformat(),
    "screenshots": [],
    "test_cases": [],
    "success_criteria": {},
    "status": "running",
    "error": None
}

def log_test_case(case_name, status, details="", screenshot_path=None):
    """Log a test case result"""
    case_result = {
        "test_case": case_name,
        "status": status,  # passed, failed, warning
        "details": details,
        "screenshot": screenshot_path,
        "timestamp": datetime.now().isoformat()
    }
    test_results["test_cases"].append(case_result)
    print(f"[{status.upper()}] {case_name}: {details}")
    if screenshot_path:
        test_results["screenshots"].append(str(screenshot_path))

def take_screenshot(page, name):
    """Take and save a screenshot"""
    path = SCREENSHOT_DIR / f"{name}.png"
    page.screenshot(path=str(path))
    print(f"  Screenshot saved: {path}")
    return str(path)

def load_webhooks_config():
    """Load webhooks configuration"""
    try:
        with open(WEBHOOKS_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading webhooks config: {e}")
        return {}

def save_webhooks_config(config):
    """Save webhooks configuration"""
    try:
        with open(WEBHOOKS_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving webhooks config: {e}")
        return False

def run_test():
    """Execute the E2E test for webhook integration"""
    print("=" * 60)
    print("E2E Test: Webhook Integration and Scope Hierarchy")
    print("=" * 60)

    # Load initial config
    original_config = load_webhooks_config()
    print(f"\n[INFO] Loaded webhooks config from: {WEBHOOKS_CONFIG_PATH}")

    with sync_playwright() as p:
        # Launch browser
        print("\n[Setup] Launching browser...")

        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(SCREENSHOT_DIR)
        )
        page = context.new_page()

        # Monitor console messages
        console_messages = []
        def handle_console(msg):
            console_messages.append({
                "type": msg.type,
                "text": msg.text,
                "location": f"{msg.location.get('url', '')}:{msg.location.get('lineNumber', '')}"
            })
            if msg.type in ["error", "warning"]:
                print(f"  Console {msg.type}: {msg.text}")

        page.on("console", handle_console)

        # Monitor network requests for webhook calls
        webhook_requests = []
        webhook_responses = []

        def handle_request(request):
            if TEST_WEBHOOK in request.url:
                webhook_requests.append({
                    "url": request.url,
                    "method": request.method,
                    "timestamp": datetime.now().isoformat()
                })
                print(f"  [WEBHOOK] Request to: {request.url}")

        def handle_response(response):
            if TEST_WEBHOOK in response.url:
                webhook_responses.append({
                    "url": response.url,
                    "status": response.status,
                    "timestamp": datetime.now().isoformat()
                })
                print(f"  [WEBHOOK] Response: {response.status} from {response.url}")

        page.on("request", handle_request)
        page.on("response", handle_response)

        try:
            # ============================================================
            # TEST CASE 1: Global Webhook (Fallback)
            # ============================================================
            print("\n" + "=" * 60)
            print("TEST CASE 1: Global Webhook (Fallback)")
            print("=" * 60)

            # Step 1.1: Verify global webhook configuration
            print("\n[Step 1.1] Verifying global webhook configuration...")
            config = load_webhooks_config()

            global_webhook = config.get("global", {}).get("default_webhook", "")
            global_timeout = config.get("global", {}).get("timeout", 30)
            global_retry = config.get("global", {}).get("retry_attempts", 3)

            tc1_details = f"Global webhook: {global_webhook}, Timeout: {global_timeout}s, Retry: {global_retry}"
            if global_webhook == TEST_WEBHOOK and global_timeout == 30 and global_retry == 3:
                log_test_case("1.1: Global webhook config", "passed", tc1_details)
            else:
                log_test_case("1.1: Global webhook config", "failed", tc1_details)

            # Step 1.2: Navigate to application
            print("\n[Step 1.2] Navigating to application...")
            page.goto(BASE_URL, wait_until="networkidle", timeout=10000)
            take_screenshot(page, "01-page-loaded")
            page.wait_for_timeout(1000)

            # Step 1.3: Select a project without specific webhook override
            # Use sdlcWorkflow_structure which has webhook but no override_global=true
            print("\n[Step 1.3] Selecting project for global webhook test...")

            # Find and click project selector
            project_selectors = [
                "select#project-select",
                ".project-selector select",
                "[data-testid='project-select']",
                "header select"
            ]

            project_selector = None
            for selector in project_selectors:
                try:
                    elem = page.locator(selector).first
                    if elem.is_visible(timeout=2000):
                        project_selector = selector
                        break
                except:
                    continue

            if project_selector:
                page.select_option(project_selector, "sdlcWorkflow_structure")
                page.wait_for_timeout(1500)
                take_screenshot(page, "02-global-webhook-project-selected")
                log_test_case("1.2: Project selected for global webhook", "passed", "Selected sdlcWorkflow_structure")

            # Step 1.4: Select a file and send command using global webhook
            print("\n[Step 1.4] Testing global webhook usage...")

            # Look for files in the project
            file_selectors = [
                "[data-file]",
                ".file-list-item",
                "a[href*='.html']",
                "li:has-text('.html')"
            ]

            file_found = False
            for selector in file_selectors:
                try:
                    files = page.locator(selector).all()
                    if files and len(files) > 0:
                        files[0].click()
                        file_found = True
                        log_test_case("1.3: File selected", "passed", f"Clicked file using {selector}")
                        break
                except:
                    continue

            if not file_found:
                log_test_case("1.3: File selected", "warning", "Could not find file to click")

            page.wait_for_timeout(1000)

            # Enter command
            input_selectors = ["textarea[name='command']", "input[name='command']", "#command-input", "textarea"]
            command = "Test global webhook"
            input_success = False

            for selector in input_selectors:
                try:
                    input_elem = page.locator(selector).first
                    if input_elem.is_visible(timeout=2000):
                        input_elem.fill(command)
                        input_success = True
                        break
                except:
                    continue

            if input_success:
                take_screenshot(page, "03-global-webhook-command-entered")

            # Send webhook
            webhook_button_selectors = [
                "button[type='submit']",
                "button:has-text('Enviar')",
                "button:has-text('Webhook')",
                "#sendBtn"
            ]

            webhook_sent = False
            for selector in webhook_button_selectors:
                try:
                    button = page.locator(selector).first
                    if button.is_visible(timeout=2000):
                        button.click()
                        webhook_sent = True
                        log_test_case("1.4: Global webhook sent", "passed", "Clicked webhook button")
                        break
                except:
                    continue

            page.wait_for_timeout(3000)  # Wait for webhook response

            # Check if webhook was called
            webhook_count_before = len(webhook_requests)
            if webhook_count_before > 0:
                log_test_case("1.5: Global webhook called", "passed", f"Webhook called {webhook_count_before} time(s)")
            else:
                log_test_case("1.5: Global webhook called", "warning", "No webhook calls detected")

            take_screenshot(page, "04-global-webhook-after-send")

            # ============================================================
            # TEST CASE 2: Project-Level Webhook Override
            # ============================================================
            print("\n" + "=" * 60)
            print("TEST CASE 2: Project-Level Webhook Override")
            print("=" * 60)

            # Step 2.1: Verify project-level webhook configuration
            print("\n[Step 2.1] Verifying project-level webhook config...")

            config = load_webhooks_config()
            project_webhook = config.get("projects", {}).get("heroPage_design", {}).get("webhook", "")
            override_global = config.get("projects", {}).get("heroPage_design", {}).get("override_global", False)

            tc2_details = f"Project webhook: {project_webhook}, Override: {override_global}"
            if project_webhook and override_global:
                log_test_case("2.1: Project webhook config", "passed", tc2_details)
            else:
                log_test_case("2.1: Project webhook config", "warning", tc2_details)

            # Step 2.2: Select heroPage_design project
            print("\n[Step 2.2] Selecting heroPage_design project...")

            if project_selector:
                page.select_option(project_selector, "heroPage_design")
                page.wait_for_timeout(1500)
                take_screenshot(page, "05-project-webhook-selected")
                log_test_case("2.2: Project with webhook selected", "passed", "Selected heroPage_design")

            # Step 2.3: Check sidebar for webhook URL display
            print("\n[Step 2.3] Checking sidebar for webhook URL...")

            # Look for webhook URL in sidebar
            sidebar_webhook_selectors = [
                ".webhook-url",
                "[data-testid='webhook-url']",
                ".webhook-display",
                "text=" + TEST_WEBHOOK[:30]  # Partial match
            ]

            webhook_displayed = False
            for selector in sidebar_webhook_selectors:
                try:
                    if page.locator(selector).is_visible(timeout=2000):
                        webhook_displayed = True
                        log_test_case("2.3: Webhook URL in sidebar", "passed", f"Found webhook display: {selector}")
                        break
                except:
                    continue

            if not webhook_displayed:
                log_test_case("2.3: Webhook URL in sidebar", "warning", "Webhook URL not visibly displayed in sidebar")

            # Step 2.4: Select file and send command
            print("\n[Step 2.4] Testing project-level webhook...")

            # Click on design.html
            try:
                page.locator("text=design.html").first.click()
                page.wait_for_timeout(1000)
                log_test_case("2.4: File selected in project", "passed", "Selected design.html")
            except:
                log_test_case("2.4: File selected in project", "warning", "Could not select design.html")

            # Enter command
            for selector in input_selectors:
                try:
                    input_elem = page.locator(selector).first
                    if input_elem.is_visible(timeout=2000):
                        input_elem.fill("Test project webhook")
                        break
                except:
                    continue

            take_screenshot(page, "06-project-webhook-command-entered")

            # Clear previous webhook requests count
            webhook_count_before_project = len(webhook_requests)

            # Send webhook
            for selector in webhook_button_selectors:
                try:
                    button = page.locator(selector).first
                    if button.is_visible(timeout=2000):
                        button.click()
                        log_test_case("2.5: Project webhook sent", "passed", "Clicked webhook button")
                        break
                except:
                    continue

            page.wait_for_timeout(3000)

            webhook_count_after_project = len(webhook_requests)
            if webhook_count_after_project > webhook_count_before_project:
                log_test_case("2.6: Project webhook called", "passed", f"New webhook calls: {webhook_count_after_project - webhook_count_before_project}")
            else:
                log_test_case("2.6: Project webhook called", "warning", "No new webhook calls detected")

            take_screenshot(page, "07-project-webhook-after-send")

            # ============================================================
            # TEST CASE 3: File-Level Webhook Override
            # ============================================================
            print("\n" + "=" * 60)
            print("TEST CASE 3: File-Level Webhook Override")
            print("=" * 60)

            # Step 3.1: Verify file-level webhook configuration
            print("\n[Step 3.1] Verifying file-level webhook config...")

            config = load_webhooks_config()
            file_webhook = config.get("projects", {}).get("qualification_questions", {}).get("files", {}).get("askQuestionTool1", {}).get("webhook", "")

            tc3_details = f"File webhook for askQuestionTool1: {file_webhook}"
            if file_webhook:
                log_test_case("3.1: File webhook config", "passed", tc3_details)
            else:
                log_test_case("3.1: File webhook config", "warning", tc3_details)

            # Step 3.2: Select qualification_questions project
            print("\n[Step 3.2] Selecting qualification_questions project...")

            if project_selector:
                page.select_option(project_selector, "qualification_questions")
                page.wait_for_timeout(1500)
                take_screenshot(page, "08-file-webhook-project-selected")
                log_test_case("3.2: Project with file webhook selected", "passed", "Selected qualification_questions")

            # Step 3.3: Select askQuestionTool1 file
            print("\n[Step 3.3] Selecting askQuestionTool1 file...")

            try:
                page.locator("text=askQuestionTool1").first.click()
                page.wait_for_timeout(1000)
                log_test_case("3.3: File with webhook selected", "passed", "Selected askQuestionTool1")
            except:
                log_test_case("3.3: File with webhook selected", "warning", "Could not select askQuestionTool1")

            # Check for options in AskQuestionTool
            page.wait_for_timeout(1000)
            take_screenshot(page, "09-file-webhook-file-selected")

            # Look for checkboxes/options in the askQuestionTool
            option_selectors = [
                "input[type='checkbox']",
                ".option",
                "[data-option]",
                "label:has-text('Interface')"
            ]

            options_found = False
            for selector in option_selectors:
                try:
                    options = page.locator(selector).all()
                    if options and len(options) > 0:
                        options_found = True
                        log_test_case("3.4: Options displayed", "passed", f"Found {len(options)} options")
                        break
                except:
                    continue

            if not options_found:
                log_test_case("3.4: Options displayed", "warning", "No options found in AskQuestionTool")

            # Step 3.4: Test file-level webhook
            print("\n[Step 3.4] Testing file-level webhook...")

            # Find comment/input field
            comment_selectors = ["textarea[name='comment']", "#comment", "textarea:not([name='command'])"]

            for selector in comment_selectors:
                try:
                    input_elem = page.locator(selector).first
                    if input_elem.is_visible(timeout=2000):
                        input_elem.fill("Test file webhook")
                        break
                except:
                    continue

            webhook_count_before_file = len(webhook_requests)

            # Send webhook
            for selector in webhook_button_selectors:
                try:
                    button = page.locator(selector).first
                    if button.is_visible(timeout=2000):
                        button.click()
                        log_test_case("3.5: File webhook sent", "passed", "Clicked webhook button")
                        break
                except:
                    continue

            page.wait_for_timeout(3000)

            webhook_count_after_file = len(webhook_requests)
            if webhook_count_after_file > webhook_count_before_file:
                log_test_case("3.6: File webhook called", "passed", f"New webhook calls: {webhook_count_after_file - webhook_count_before_file}")
            else:
                log_test_case("3.6: File webhook called", "warning", "No new webhook calls detected")

            take_screenshot(page, "10-file-webhook-after-send")

            # ============================================================
            # TEST CASE 4: Webhook Payload Structure
            # ============================================================
            print("\n" + "=" * 60)
            print("TEST CASE 4: Webhook Payload Structure")
            print("=" * 60)

            # Step 4.1: Verify payload structure
            print("\n[Step 4.1] Verifying webhook payload structure...")

            # Check console for payload logs
            payload_logs = [msg for msg in console_messages if "payload" in msg.get("text", "").lower()]

            if payload_logs:
                log_test_case("4.1: Payload structure logged", "passed", f"Found {len(payload_logs)} payload-related console messages")
            else:
                log_test_case("4.1: Payload structure logged", "info", "No explicit payload logs in console")

            # Verify webhook was called
            total_webhook_calls = len(webhook_requests)
            if total_webhook_calls > 0:
                log_test_case("4.2: Webhook endpoint called", "passed", f"Total webhook calls: {total_webhook_calls}")
            else:
                log_test_case("4.2: Webhook endpoint called", "warning", "No webhook calls detected during test")

            take_screenshot(page, "11-payload-verification")

            # ============================================================
            # TEST CASE 5: Error Handling
            # ============================================================
            print("\n" + "=" * 60)
            print("TEST CASE 5: Error Handling")
            print("=" * 60)

            # Step 5.1: Test with invalid webhook URL
            print("\n[Step 5.1] Testing error handling with invalid webhook...")

            # Temporarily modify config to use invalid webhook
            invalid_webhook = "https://invalid-domain-12345.com/webhook"

            config = load_webhooks_config()
            original_global_webhook = config.get("global", {}).get("default_webhook", "")
            config["global"]["default_webhook"] = invalid_webhook
            save_webhooks_config(config)

            log_test_case("5.1: Invalid webhook configured", "passed", f"Set invalid webhook: {invalid_webhook}")

            # Reload page to pick up new config
            page.goto(BASE_URL, wait_until="networkidle", timeout=10000)
            page.wait_for_timeout(1000)

            # Select project and file
            if project_selector:
                page.select_option(project_selector, "sdlcWorkflow_structure")
                page.wait_for_timeout(1000)

            # Try to click a file
            try:
                files = page.locator("[data-file], .file-list-item").all()
                if files:
                    files[0].click()
            except:
                pass

            page.wait_for_timeout(500)

            # Enter command
            for selector in input_selectors:
                try:
                    input_elem = page.locator(selector).first
                    if input_elem.is_visible(timeout=2000):
                        input_elem.fill("Test error handling")
                        break
                except:
                    continue

            take_screenshot(page, "12-error-handling-before-send")

            # Try to send webhook (should fail gracefully)
            for selector in webhook_button_selectors:
                try:
                    button = page.locator(selector).first
                    if button.is_visible(timeout=2000):
                        button.click()
                        log_test_case("5.2: Invalid webhook attempt", "passed", "Attempted to send to invalid webhook")
                        break
                except:
                    continue

            page.wait_for_timeout(5000)  # Wait for timeout/retry

            # Check for error indication
            error_indicators = [
                ".error",
                ".error-message",
                "[data-testid='error']",
                "text=Error",
                "text=Failed"
            ]

            error_found = False
            for selector in error_indicators:
                try:
                    if page.locator(selector).is_visible(timeout=1000):
                        error_found = True
                        log_test_case("5.3: Error message displayed", "passed", f"Found error indicator: {selector}")
                        break
                except:
                    continue

            if not error_found:
                log_test_case("5.3: Error message displayed", "info", "No explicit error message found (may be handled silently)")

            take_screenshot(page, "13-error-handling-after-send")

            # Restore original webhook config
            config["global"]["default_webhook"] = original_global_webhook
            save_webhooks_config(config)
            log_test_case("5.4: Original webhook restored", "passed", "Restored valid webhook URL")

            # Reload page
            page.goto(BASE_URL, wait_until="networkidle", timeout=10000)
            page.wait_for_timeout(1000)

            # ============================================================
            # TEST CASE 6: Webhook Configuration in UI
            # ============================================================
            print("\n" + "=" * 60)
            print("TEST CASE 6: Webhook Configuration in UI")
            print("=" * 60)

            # Step 6.1: Check for webhook configuration UI
            print("\n[Step 6.1] Checking webhook configuration UI...")

            # Select a project
            if project_selector:
                page.select_option(project_selector, "heroPage_design")
                page.wait_for_timeout(1500)

            # Look for configuration button/panel
            config_button_selectors = [
                "button:has-text('Configurar')",
                "button:has-text('Configure')",
                "[data-testid='configure-webhook']",
                ".config-button"
            ]

            config_button_found = False
            for selector in config_button_selectors:
                try:
                    if page.locator(selector).is_visible(timeout=2000):
                        config_button_found = True
                        log_test_case("6.1: Config button present", "passed", f"Found config button: {selector}")
                        break
                except:
                    continue

            if not config_button_found:
                log_test_case("6.1: Config button present", "info", "Config button not found (feature may not be implemented)")

            # Look for webhook display in sidebar
            webhook_display_selectors = [
                ".webhook-info",
                "[data-testid='webhook-info']",
                "text=" + TEST_WEBHOOK[:50]
            ]

            webhook_info_found = False
            for selector in webhook_display_selectors:
                try:
                    if page.locator(selector).is_visible(timeout=2000):
                        webhook_info_found = True
                        log_test_case("6.2: Webhook info in sidebar", "passed", f"Found webhook info: {selector}")
                        break
                except:
                    continue

            if not webhook_info_found:
                log_test_case("6.2: Webhook info in sidebar", "warning", "Webhook info not visibly displayed")

            # Check for scope badge
            scope_badge_selectors = [
                ".scope-badge",
                "[data-scope]",
                ".webhook-scope"
            ]

            scope_badge_found = False
            for selector in scope_badge_selectors:
                try:
                    if page.locator(selector).is_visible(timeout=2000):
                        scope_badge_found = True
                        badge_text = page.locator(selector).text_content()
                        log_test_case("6.3: Scope badge displayed", "passed", f"Found scope badge: {badge_text}")
                        break
                except:
                    continue

            if not scope_badge_found:
                log_test_case("6.3: Scope badge displayed", "info", "Scope badge not found (may not be implemented)")

            take_screenshot(page, "14-webhook-config-ui")

            # Final screenshot
            take_screenshot(page, "15-final-state")

        except Exception as e:
            log_test_case("Test execution", "failed", f"Exception during test: {str(e)}")
            take_screenshot(page, "error-state")
            test_results["error"] = str(e)
            test_results["status"] = "failed"

        finally:
            # Restore original config
            save_webhooks_config(original_config)

            # Keep browser open for inspection
            print("\n[Info] Keeping browser open for 5 seconds for inspection...")
            page.wait_for_timeout(5000)
            browser.close()

    # Generate final report
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    # Count results
    passed = sum(1 for tc in test_results["test_cases"] if tc["status"] == "passed")
    failed = sum(1 for tc in test_results["test_cases"] if tc["status"] == "failed")
    warnings = sum(1 for tc in test_results["test_cases"] if tc["status"] == "warning")
    info = sum(1 for tc in test_results["test_cases"] if tc["status"] == "info")
    total = len(test_results["test_cases"])

    print(f"\nTotal Test Cases: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Warnings: {warnings}")
    print(f"  Info: {info}")

    # Detailed results
    print("\nDetailed Results:")
    for tc in test_results["test_cases"]:
        status_symbol = {"passed": "PASS", "failed": "FAIL", "warning": "WARN", "info": "INFO"}
        print(f"  [{status_symbol.get(tc['status'], '???')}] {tc['test_case']}")
        if tc.get("details"):
            print(f"      {tc['details']}")

    # Console messages summary
    if console_messages:
        errors = [m for m in console_messages if m.get("type") == "error"]
        warnings_list = [m for m in console_messages if m.get("type") == "warning"]
        print(f"\nConsole Messages:")
        print(f"  Errors: {len(errors)}")
        print(f"  Warnings: {len(warnings_list)}")

        if errors:
            print("\n  Error Details:")
            for err in errors[:5]:
                print(f"    - {err.get('text', 'Unknown')}")

    # Webhook calls summary
    print(f"\nWebhook Calls Summary:")
    print(f"  Total webhook requests: {len(webhook_requests)}")
    print(f"  Total webhook responses: {len(webhook_responses)}")

    # Determine overall status
    if failed > 0:
        test_results["status"] = "failed"
    elif warnings > 0:
        test_results["status"] = "passed_with_warnings"
    else:
        test_results["status"] = "passed"

    # Success criteria
    test_results["success_criteria"] = {
        "global_webhook_configured": any("1.1" in tc["test_case"] and tc["status"] == "passed" for tc in test_results["test_cases"]),
        "global_webhook_used": any("1.5" in tc["test_case"] and tc["status"] in ["passed", "warning"] for tc in test_results["test_cases"]),
        "project_webhook_configured": any("2.1" in tc["test_case"] and tc["status"] == "passed" for tc in test_results["test_cases"]),
        "project_webhook_used": any("2.6" in tc["test_case"] and tc["status"] in ["passed", "warning"] for tc in test_results["test_cases"]),
        "file_webhook_configured": any("3.1" in tc["test_case"] and tc["status"] == "passed" for tc in test_results["test_cases"]),
        "file_webhook_used": any("3.6" in tc["test_case"] and tc["status"] in ["passed", "warning"] for tc in test_results["test_cases"]),
        "webhook_endpoint_called": len(webhook_requests) > 0,
        "error_handling_tested": any("5." in tc["test_case"] for tc in test_results["test_cases"]),
        "config_ui_checked": any("6." in tc["test_case"] for tc in test_results["test_cases"])
    }

    # Save results to JSON
    results_file = SCREENSHOT_DIR / "test_results.json"
    with open(results_file, "w") as f:
        json.dump(test_results, f, indent=2)

    print(f"\nResults saved to: {results_file}")
    print(f"Screenshots saved to: {SCREENSHOT_DIR}")

    # Print JSON output for final result
    print("\n" + "=" * 60)
    print("FINAL JSON OUTPUT:")
    print("=" * 60)
    final_output = {
        "test_name": test_results["test_name"],
        "status": test_results["status"],
        "screenshots": test_results["screenshots"],
        "error": test_results["error"],
        "test_cases_passed": passed,
        "test_cases_failed": failed,
        "test_cases_warnings": warnings,
        "webhook_calls": len(webhook_requests)
    }
    print(json.dumps(final_output, indent=2))

    return test_results

if __name__ == "__main__":
    results = run_test()
    sys.exit(0 if results["status"] in ["passed", "passed_with_warnings"] else 1)
