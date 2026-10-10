from playwright.sync_api import Page, expect

class CheckOut:
    def __init__(self, page: Page):
        self.page = page
        self.title = page.get_by_text(
            "Your Cart", exact=True
        )
        self.title1 = page.get_by_text(
            "Checkout: Overview",exact=True
        )
        self.success_message = page.locator(".complete-header")
        self.check_out = page.get_by_role("button",name="checkout")
        self.First_Name = page.get_by_placeholder("First Name")
        self.Last_Name = page.get_by_placeholder("Last Name")
        self.Zip_Code = page.get_by_placeholder("Zip/Postal Code")
        self.Continue_Button = page.get_by_role("button",name="continue")
        self.Finish_Button = page.get_by_role("button",name="Finish")
        self.Back_Home = page.get_by_role("button",name="Back Home")

    def verify_checkout_page(self):
        expect(self.title).to_be_visible()

    def checkoutbutton(self):
        self.check_out.click()

    def Adress(self,FirstName,LastName,ZipCode):
        self.First_Name.fill(FirstName)
        self.Last_Name.fill(LastName)
        self.Zip_Code.fill(ZipCode)

    def ContinueButton(self):
        self.Continue_Button.click()

    def Overview_Page(self):
        expect(self.title1).to_be_visible()

    def FinishButton(self):
        self.Finish_Button.click()

    def verify_successmessage(self):
        expect(self.success_message).to_be_visible()
        expect(self.success_message).to_have_text("Thank you for your order!")

    def BackHome(self):
        self.Back_Home.click()

