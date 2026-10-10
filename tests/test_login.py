import time

import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from config.settings import USERNAME, PASSWORD


@pytest.mark.smoke
def test_valid_login(page):
    login = LoginPage(page)
    inventory = InventoryPage(page)

    login.open()
    login.login(USERNAME, PASSWORD)

    inventory.verify_inventory_page()
    inventory.add_backpack_to_cart()
    inventory.open_cart()
    time.sleep(10)


@pytest.mark.regression
def test_invalid_login(page):
    login = LoginPage(page)

    login.open()
    login.login("invalid_user", "wrong_password")

    login.verify_login_error(
        "Username and password do not match"
    )