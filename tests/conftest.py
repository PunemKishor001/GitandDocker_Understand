
import pytest
import allure
from pathlib import Path

SCREENSHOT_DIR = Path("reports/screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def page(browser, request):
    context = browser.new_context()
    page = context.new_page()

    yield page

    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        screenshot = SCREENSHOT_DIR / f"{request.node.name}.png"
        page.screenshot(path=str(screenshot), full_page=True)

        allure.attach.file(
            str(screenshot),
            name="Failure Screenshot",
            attachment_type=allure.attachment_type.PNG,
        )

    context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        item.rep_call = report
