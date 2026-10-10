
import time
import uuid
from pathlib import Path

import allure
import pytest

from utils.grafana_logger import log_event

SCREENSHOT_DIR = Path("reports/screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def page(browser, request):
    context = browser.new_context()
    page = context.new_page()
    test_run_id = str(uuid.uuid4())

    log_event(
        "test_started",
        test_name=request.node.nodeid,
        test_run_id=test_run_id,
    )

    def on_request(req):
        req._observability_start = time.perf_counter()

    def on_response(response):
        req = response.request
        start = getattr(
            req, "_observability_start", time.perf_counter()
        )
        elapsed_ms = round(
            (time.perf_counter() - start) * 1000, 2
        )

        status = response.status
        level = (
            "ERROR" if status >= 500
            else "WARNING" if status >= 400
            else "INFO"
        )

        log_event(
            "http_response",
            level=level,
            test_name=request.node.nodeid,
            test_run_id=test_run_id,
            method=req.method,
            url=req.url,
            status_code=status,
            response_time_ms=elapsed_ms,
        )

        if elapsed_ms > 3000:
            log_event(
                "slow_request",
                level="WARNING",
                test_name=request.node.nodeid,
                test_run_id=test_run_id,
                url=req.url,
                response_time_ms=elapsed_ms,
            )

    def on_request_failed(req):
        log_event(
            "request_failed",
            level="ERROR",
            test_name=request.node.nodeid,
            test_run_id=test_run_id,
            method=req.method,
            url=req.url,
            error=req.failure,
        )

    page.on("request", on_request)
    page.on("response", on_response)
    page.on("requestfailed", on_request_failed)

    try:
        yield page
    finally:
        report = getattr(request.node, "rep_call", None)

        if report and report.failed:
            screenshot = (
                SCREENSHOT_DIR / f"{request.node.name}.png"
            )

            try:
                page.screenshot(
                    path=str(screenshot),
                    full_page=True,
                )

                allure.attach.file(
                    str(screenshot),
                    name="Failure Screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )

                log_event(
                    "screenshot_captured",
                    test_name=request.node.nodeid,
                    test_run_id=test_run_id,
                )

            except Exception as exc:
                log_event(
                    "screenshot_failed",
                    level="ERROR",
                    test_name=request.node.nodeid,
                    error=str(exc),
                )

        log_event(
            "test_finished",
            test_name=request.node.nodeid,
            test_run_id=test_run_id,
            outcome=report.outcome if report else "unknown",
        )

        context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        item.rep_call = report

        if report.failed:
            excinfo = call.excinfo

            log_event(
                "test_failed",
                level="ERROR",
                test_name=item.nodeid,
                exception_type=(
                    excinfo.typename if excinfo else "Unknown"
                ),
                error=(
                    str(excinfo.value) if excinfo else "Unknown"
                ),
                stack_trace=(
                    str(excinfo.getrepr())
                    if excinfo else None
                ),
            )

        elif report.passed:
            log_event(
                "test_passed",
                test_name=item.nodeid,
            )
