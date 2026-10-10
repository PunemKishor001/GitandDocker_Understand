import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from config.settings import USERNAME, PASSWORD


@pytest.mark.smoke
def test_add_product_to_cart(page):
    login = LoginPage(page)
    inventory = InventoryPage(page)

    login.open()
    login.login(USERNAME, PASSWORD)

    inventory.verify_inventory_page()
    inventory.add_backpack_to_cart()

    assert inventory.cart_badge.inner_text() == "1"