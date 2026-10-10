import time
import json

import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.checkout_page import CheckOut
from config.settings import USERNAME, PASSWORD

from pathlib import Path


Data_File = (Path(__file__).resolve().parents[1]/"test_data"/"user.json")
with open(Data_File,"r",encoding="utf-8") as file:
    TEST_DATA = json.load(file)


@pytest.mark.NewFeature
def test_valid_login(page):
    login = LoginPage(page)
    inventory = InventoryPage(page)
    check_out = CheckOut(page)

    login.open()
    login.login(USERNAME, PASSWORD)

    inventory.verify_inventory_page()
    inventory.add_backpack_to_cart()
    inventory.open_cart()

    check_out.verify_checkout_page()
    check_out.checkoutbutton()
    # Read address details from JSON
    address = TEST_DATA["AdressDetails"]

    check_out.Adress(
        FirstName=address["FirstName"],
        LastName=address["LastName"],
        ZipCode=address["ZipCode"]
    )
    check_out.ContinueButton()
    check_out.Overview_Page()
    check_out.FinishButton(A)
    check_out.verify_successmessage()
    check_out.BackHome()
    time.sleep(10)
