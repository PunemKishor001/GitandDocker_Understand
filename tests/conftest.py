
import json
import os
import urllib.request
import urllib.error

from datetime import datetime, timezone
from pathlib import Path

import allure
import pytest


# ==================================================
# PROJECT PATHS AND SCREENSHOTS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SCREENSHOT_DIR = PROJECT_ROOT / "reports" / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

APPLICATION_NAME = "saucedemo-automation"


# ==================================================
# BETTER STACK CONFIGURATION
# ==================================================

# Use the ingesting host shown in your Better Stack source.
# This is not the Live Tail dashboard URL.
BETTERSTACK_URL = os.getenv(
    "BETTERSTACK_URL",
    "https://s2791463.us-west-2a.betterstackdata.com",
)


# ==================================================
# BETTER STACK LOGGING FUNCTION
# ==================================================

def send_to_better_stack(message, level="info", **fields):
    """
    Send a JSON event to Better Stack.
    The source token must be supplied through an environment variable.
    """

    token = os.getenv("BETTERSTACK_SOURCE_TOKEN")

    if not token:
        print(
            "[Better Stack] SKIPPED: "
            "BETTERSTACK_SOURCE_TOKEN is not configured."
        )
        return

    payload = {
        "dt": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": message,
        "application": APPLICATION_NAME,
        "environment": os.getenv("TEST_ENV", "local"),
        "build_number": os.getenv("BUILD_NUMBER", "local"),
        "job_name": os.getenv("JOB_NAME", "local"),
        **fields,
    }

    request = urllib.request.Request(
        url=BETTERSTACK_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            response_body = response.read().decode(
                "utf-8", errors="replace"
            )

            print(
                f"[Better Stack] HTTP {response.status} "
                f"| {message}"
            )

            if response_body:
                print(f"[Better Stack] Response: {response_body}")

    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")

        print(
            f"[Better Stack] HTTP ERROR {exc.code} "
            f"| {message}"
        )

        if error_body:
            print(f"[Better Stack] Details: {error_body}")

    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"[Better Stack] CONNECTION ERROR: {exc}")

    except Exception as exc:
        print(f"[Better Stack] UNEXPECTED ERROR: {exc}")


# ==================================================
# PLAYWRIGHT PAGE FIXTURE
# ==================================================

@pytest.fixture
def page(browser, request):
    """
    Create a fresh browser context and page for each test.
    Capture a screenshot when the test call fails.
    """

    context = browser.new_context()
    page = context.new_page()

    try:
        yield page

    finally:
        report = getattr(request.node, "rep_call", None)

        if report is not None and report.failed:
            screenshot_path = (
                SCREENSHOT_DIR
                / f"{request.node.name}.png"
            )

            try:
                page.screenshot(
                    path=str(screenshot_path),
                    full_page=True,
                )

                allure.attach.file(
                    str(screenshot_path),
                    name=f"Failure Screenshot - {request.node.name}",
                    attachment_type=allure.attachment_type.PNG,
                )

                print(
                    f"[Screenshot] Saved: {screenshot_path}"
                )

            except Exception as exc:
                print(
                    f"[Screenshot] Capture failed: {exc}"
                )

        context.close()


# ==================================================
# CAPTURE PYTEST REPORTS
# ==================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Store the report for setup, call and teardown phases.
    """

    outcome = yield
    report = outcome.get_result()

    setattr(item, f"rep_{report.when}", report)


# ==================================================
# SEND TEST RESULTS TO BETTER STACK
# ==================================================

@pytest.hookimpl(trylast=True)
def pytest_runtest_logreport(report):
    """
    Send final test results and setup failures to Better Stack.
    Do not send duplicate results for teardown.
    """

    if report.when == "call":
        pass

    elif report.when == "setup" and report.failed:
        pass

    else:
        return

    outcome = report.outcome.upper()

    level = "error" if report.failed else "info"

    error_details = None

    if report.failed and report.longrepr:
        error_details = str(report.longrepr)[:5000]

    message = f"{outcome}: {report.nodeid}"

    print(f"[Pytest] Reporting {message}")

    send_to_better_stack(
        message=message,
        level=level,
        event_type="pytest_test_result",
        test_name=report.nodeid,
        test_outcome=outcome,
        test_phase=report.when,
        duration_seconds=round(report.duration, 3),
        error=error_details,
    )


# ==================================================
# SEND FINAL PYTEST SESSION SUMMARY
# ==================================================

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Send the overall Pytest run summary to Better Stack.
    """

    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    errors = len(terminalreporter.stats.get("error", []))
    skipped = len(terminalreporter.stats.get("skipped", []))

    total = passed + failed + errors + skipped

    if failed or errors or exitstatus != 0:
        outcome = "FAILED"
        level = "error"
    else:
        outcome = "PASSED"
        level = "info"

    summary = (
        f"Pytest run {outcome}: "
        f"total={total}, passed={passed}, "
        f"failed={failed}, errors={errors}, "
        f"skipped={skipped}"
    )

    print(f"[Pytest Summary] {summary}")

    send_to_better_stack(
        message=summary,
        level=level,
        event_type="pytest_session_summary",
        test_outcome=outcome,
        total_tests=total,
        passed=passed,
        failed=failed,
        errors=errors,
        skipped=skipped,
        pytest_exit_code=exitstatus,
    )
