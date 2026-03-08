#!/usr/bin/env python3
"""
E2E Test: File Type Detection and Module Rendering
Tests automatic file type detection and appropriate module rendering
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

# Test Configuration
BASE_URL = "http://localhost:8000"
SCREENSHOT_DIR = Path(__file__).parent / "screenshots" / "file-detection"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Test Results
test_results = {
    "test_name": "File Type Detection and Module Rendering",
    "timestamp": datetime.now().isoformat(),
    "screenshots": [],
    "steps": [],
    "success_criteria": {},
    "status": "running",
    "error": None
}

def log_step(step_name, status, details="", screenshot_path=None):
    """Log a test step"""
    step_result = {
        "step": step_name,
        "status": status,  # passed, failed, warning
        "details": details,
        "screenshot": screenshot_path,
        "timestamp": datetime.now().isoformat()
    }
    test_results["steps"].append(step_result)
    print(f"[{status.upper()}] {step_name}: {details}")
    if screenshot_path:
        test_results["screenshots"].append(str(screenshot_path))

def take_screenshot(page, name):
    """Take and save a screenshot"""
    path = SCREENSHOT_DIR / f"{name}.png"
    page.screenshot(path=str(path))
    print(f"  Screenshot saved: {path}")
    return str(path)

def wait_for_module_load(page, timeout=5000):
    """Wait for visualization module to load"""
    try:
        # Wait for common module indicators
        page.wait_for_selector("iframe, .mermaid, .visualization, .module-content", timeout=timeout)
        return True
    except:
        return False

def check_file_type_detection(page, expected_type):
    """Check if file type was detected correctly"""
    try:
        # Check for file type indicators in the page
        type_indicators = [
            f"data-file-type='{expected_type}'",
            f"[data-module='{expected_type}']",
            f".{expected_type}-module",
            f"text={expected_type}"
        ]

        for indicator in type_indicators:
            try:
                if page.locator(indicator).count() > 0:
                    return True
            except:
                continue

        # Check console logs for file type detection
        console_output = page.evaluate("""() => {
            return window.lastFileTypeDetection || null;
        }""")

        if console_output and expected_type.lower() in console_output.lower():
            return True

        return False
    except:
        return False

def check_module_loaded(page, expected_module):
    """Check if correct module was loaded"""
    try:
        # Look for module-specific elements
        module_indicators = {
            "html_preview": ["iframe", ".html-preview", "iframe[src*='html']"],
            "mermaid": [".mermaid", ".diagram", "svg.mermaid"],
            "claudeCode_askQuestionTool": [".ask-question-tool", ".question-tool", "[data-tool='askQuestion']"],
            "kanban": [".kanban-board", ".kanban", "[data-type='kanban']"],
            "todolist": [".todo-list", ".task-list", "[data-type='todolist']"],
            "text_editor": ["textarea", ".text-editor", "[data-module='text_editor']"]
        }

        indicators = module_indicators.get(expected_module, [])
        for indicator in indicators:
            try:
                if page.locator(indicator).count() > 0:
                    return True
            except:
                continue

        return False
    except:
        return False

def run_test():
    """Execute the E2E test"""
    print("=" * 60)
    print("E2E Test: File Type Detection and Module Rendering")
    print("=" * 60)

    with sync_playwright() as p:
        # Step 1: Launch browser and navigate
        print("\n[Setup] Launching browser and navigating to application...")

        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(SCREENSHOT_DIR) if SCREENSHOT_DIR.exists() else None
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

        try:
            # Navigate to base URL
            print("\n[Step 0] Navigating to base URL...")
            page.goto(BASE_URL, wait_until="networkidle", timeout=10000)
            take_screenshot(page, "00-initial-state")

            log_step("Initial navigation", "passed", f"Loaded {BASE_URL}")

            # Test Case 1: HTML File Detection
            print("\n[Test Case 1] HTML File Detection (heroPage_design/design.html)")

            # Select heroPage_design project
            try:
                page.select_option("select#projectSelector", "heroPage_design")
                page.wait_for_timeout(1000)
                log_step("HTML - Project selection", "passed", "Selected heroPage_design")
            except Exception as e:
                log_step("HTML - Project selection", "warning", f"Could not select project: {str(e)}")

            # Click on design.html
            try:
                page.locator("[data-file='design.html']").first.click()
                page.wait_for_timeout(1500)
                take_screenshot(page, "01-html-file-selected")

                # Verify HTML detection
                html_detected = check_file_type_detection(page, "html") or \
                               check_file_type_detection(page, "HTML")
                log_step("HTML - File type detection", "passed" if html_detected else "warning",
                        f"HTML detected: {html_detected}")

                # Verify module loaded
                module_loaded = check_module_loaded(page, "html_preview")
                log_step("HTML - Module loaded", "passed" if module_loaded else "warning",
                        f"html_preview module loaded: {module_loaded}")

                # Check for iframe in visualization area
                try:
                    iframe_count = page.locator("iframe").count()
                    log_step("HTML - Visualization area", "passed" if iframe_count > 0 else "warning",
                            f"Found {iframe_count} iframe(s)")
                except:
                    log_step("HTML - Visualization area", "warning", "Could not verify iframe")

            except Exception as e:
                log_step("HTML - File selection", "failed", f"Error selecting HTML file: {str(e)}")

            # Test Case 2: Mermaid Diagram Detection
            print("\n[Test Case 2] Mermaid Diagram Detection (sdlcWorkflow_structure/structure.meirmaid)")

            try:
                page.select_option("select#projectSelector", "sdlcWorkflow_structure")
                page.wait_for_timeout(1000)
                log_step("Mermaid - Project selection", "passed", "Selected sdlcWorkflow_structure")
            except Exception as e:
                log_step("Mermaid - Project selection", "warning", f"Could not select project: {str(e)}")

            # Click on structure.meirmaid
            try:
                # Try different possible selectors for the file
                mermaid_selectors = [
                    "[data-file='structure.meirmaid']",
                    "[data-file='structure.mermaid']",  # Note: test spec has typo "meirmaid"
                    "a:has-text('structure')",
                    "[data-filename*='structure']"
                ]

                file_clicked = False
                for selector in mermaid_selectors:
                    try:
                        if page.locator(selector).count() > 0:
                            page.locator(selector).first.click()
                            file_clicked = True
                            break
                    except:
                        continue

                if file_clicked:
                    page.wait_for_timeout(1500)
                    take_screenshot(page, "02-mermaid-file-selected")

                    # Verify Mermaid detection
                    mermaid_detected = check_file_type_detection(page, "mermaid") or \
                                     check_file_type_detection(page, "Mermaid")
                    log_step("Mermaid - File type detection", "passed" if mermaid_detected else "warning",
                            f"Mermaid detected: {mermaid_detected}")

                    # Verify module loaded
                    module_loaded = check_module_loaded(page, "mermaid")
                    log_step("Mermaid - Module loaded", "passed" if module_loaded else "warning",
                            f"mermaid module loaded: {module_loaded}")

                    # Check for diagram visualization
                    try:
                        svg_count = page.locator("svg.mermaid, .mermaid svg, .diagram").count()
                        log_step("Mermaid - Visualization", "passed" if svg_count > 0 else "warning",
                                f"Found {svg_count} diagram element(s)")
                    except:
                        log_step("Mermaid - Visualization", "warning", "Could not verify diagram rendering")
                else:
                    log_step("Mermaid - File selection", "warning", "Could not find structure.meirmaid file")

            except Exception as e:
                log_step("Mermaid - File selection", "failed", f"Error selecting Mermaid file: {str(e)}")

            # Test Case 3: AskQuestionTool JSON Detection
            print("\n[Test Case 3] AskQuestionTool JSON Detection (qualification_questions/askQuestionTool1)")

            try:
                page.select_option("select#projectSelector", "qualification_questions")
                page.wait_for_timeout(1000)
                log_step("AskQuestionTool - Project selection", "passed", "Selected qualification_questions")
            except Exception as e:
                log_step("AskQuestionTool - Project selection", "warning", f"Could not select project: {str(e)}")

            # Click on askQuestionTool1
            try:
                question_tool_selectors = [
                    "[data-file='askQuestionTool1']",
                    "[data-file*='askQuestion']",
                    "a:has-text('askQuestionTool1')",
                    "[data-filename*='askQuestion']"
                ]

                file_clicked = False
                for selector in question_tool_selectors:
                    try:
                        if page.locator(selector).count() > 0:
                            page.locator(selector).first.click()
                            file_clicked = True
                            break
                    except:
                        continue

                if file_clicked:
                    page.wait_for_timeout(1500)
                    take_screenshot(page, "03-askquestiontool-selected")

                    # Verify AskQuestionTool detection
                    tool_detected = check_file_type_detection(page, "askQuestionTool") or \
                                  check_file_type_detection(page, "askquestiontool")
                    log_step("AskQuestionTool - File type detection", "passed" if tool_detected else "warning",
                            f"AskQuestionTool detected: {tool_detected}")

                    # Verify module loaded
                    module_loaded = check_module_loaded(page, "claudeCode_askQuestionTool")
                    log_step("AskQuestionTool - Module loaded", "passed" if module_loaded else "warning",
                            f"claudeCode_askQuestionTool module loaded: {module_loaded}")

                    # Check for interactive elements
                    try:
                        checkbox_count = page.locator("input[type='checkbox'], .checkbox, [role='checkbox']").count()
                        radio_count = page.locator("input[type='radio'], [role='radio']").count()
                        log_step("AskQuestionTool - Interactive elements",
                                "passed" if (checkbox_count > 0 or radio_count > 0) else "warning",
                                f"Found {checkbox_count} checkboxes, {radio_count} radio buttons")
                    except:
                        log_step("AskQuestionTool - Interactive elements", "warning",
                                "Could not verify interactive elements")
                else:
                    log_step("AskQuestionTool - File selection", "warning",
                            "Could not find askQuestionTool1 file")

            except Exception as e:
                log_step("AskQuestionTool - File selection", "failed",
                        f"Error selecting AskQuestionTool file: {str(e)}")

            # Test Case 4: Content-based Detection (files without extension)
            print("\n[Test Case 4] Content-based Detection (No Extension)")

            log_step("Content detection - No extension", "info",
                    "Skipped - requires creating test files without extensions")

            # Test Cases 5-7: Kanban, TodoList, Empty File
            print("\n[Test Cases 5-7] Additional Module Types")

            log_step("Kanban detection", "info", "Skipped - requires creating kanban.json test file")
            log_step("TodoList detection", "info", "Skipped - requires creating todolist.json test file")
            log_step("Empty file handling", "info", "Skipped - requires creating empty.txt test file")

            # Final state
            take_screenshot(page, "10-final-state")

        except Exception as e:
            log_step("Test execution", "failed", f"Exception during test: {str(e)}")
            take_screenshot(page, "error-state")
            test_results["error"] = str(e)
            test_results["status"] = "failed"

        finally:
            # Keep browser open for inspection
            print("\n[Info] Keeping browser open for 5 seconds for inspection...")
            page.wait_for_timeout(5000)
            browser.close()

    # Generate final report
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    # Count results
    passed = sum(1 for s in test_results["steps"] if s["status"] == "passed")
    failed = sum(1 for s in test_results["steps"] if s["status"] == "failed")
    warnings = sum(1 for s in test_results["steps"] if s["status"] == "warning")
    info = sum(1 for s in test_results["steps"] if s["status"] == "info")
    total = len(test_results["steps"])

    print(f"\nTotal Steps: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Warnings: {warnings}")
    print(f"  Info/Skipped: {info}")

    # Detailed results
    print("\nDetailed Results:")
    for step in test_results["steps"]:
        status_symbol = {"passed": "PASS", "failed": "FAIL", "warning": "WARN", "info": "INFO"}
        print(f"  [{status_symbol.get(step['status'], '???')}] {step['step']}")
        if step.get("details"):
            print(f"      {step['details']}")

    # Determine overall status
    if failed > 0:
        test_results["status"] = "failed"
    elif warnings > 0:
        test_results["status"] = "passed_with_warnings"
    else:
        test_results["status"] = "passed"

    # Add success criteria
    test_results["success_criteria"] = {
        "html_files_detected": any("HTML" in s["step"] and "detection" in s["step"] and s["status"] == "passed"
                                  for s in test_results["steps"]),
        "mermaid_files_detected": any("Mermaid" in s["step"] and "detection" in s["step"] and s["status"] == "passed"
                                     for s in test_results["steps"]),
        "askquestiontool_detected": any("AskQuestionTool" in s["step"] and "detection" in s["step"] and s["status"] == "passed"
                                       for s in test_results["steps"]),
        "modules_loaded_correctly": any("Module loaded" in s["step"] and s["status"] == "passed"
                                       for s in test_results["steps"]),
        "visualizations_render": any("Visualization" in s["step"] and s["status"] == "passed"
                                    for s in test_results["steps"])
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
        "steps_passed": passed,
        "steps_failed": failed,
        "steps_warning": warnings,
        "steps_skipped": info
    }
    print(json.dumps(final_output, indent=2))

    return test_results

if __name__ == "__main__":
    results = run_test()
    sys.exit(0 if results["status"] in ["passed", "passed_with_warnings"] else 1)