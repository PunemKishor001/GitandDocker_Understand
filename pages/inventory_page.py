from playwright.sync_api import Page, expect


class InventoryPage:
    def __init__(self, page: Page):
        self.page = page
        self.title = page.get_by_text(
            "Products", exact=True
        )
        self.cart_link = page.locator(".shopping_cart_link")
        self.add_backpack_button = page.locator(
            '[data-test="add-to-cart-sauce-labs-backpack"]'
        )
        self.cart_badge = page.locator(
            ".shopping_cart_badge"
        )

    def verify_inventory_page(self):
        expect(self.title).to_be_visible()

    def add_backpack_to_cart(self):
        self.add_backpack_button.click()

    def open_cart(self):
        self.cart_link.click()