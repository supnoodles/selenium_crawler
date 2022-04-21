from .personal_details import PaymentDetails, ContactDetails, LoginDetails
from .notifications.telegram_bot import TelegramBot
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common import exceptions
from selenium.webdriver.support.ui import Select
import time
import random

class GlobalScrape:
    """
    Shared variables across many crawlers.
    """
    def __init__(self,
                 path: str,
                 contact: ContactDetails,
                 payment: PaymentDetails,
                 login: LoginDetails = None,
                 bot: TelegramBot = None,
                 headless : bool = False
                 ) -> None:
        """
        path: absolute path to chromedriver.exe on your system.
        contact, payment, login: Dataclasses used to fill out forms.
        bot: telegram notification bot (optional)
        headless: run without head if True (optional)
        """
        self.PATH = Service(executable_path=path)
        self.options = '--headless' if headless else None
        self.driver = webdriver.Chrome(options=self.options, service=self.PATH)
        self.driver.implicitly_wait(5)
        self.bot = bot
        self.contact_details = contact
        self.payment_details = payment
        self.login = login if login else None
        # reduces number of code when calling to selenium API
        self.find_by_CSS = lambda val: self.driver.find_element(by=By.CSS_SELECTOR,value=val)
        self.find_by_NAME = lambda val: self.driver.find_element(by=By.NAME,value=val)
        self.find_by_TAG_NAME = lambda val: self.driver.find_element(by=By.TAG_NAME,value=val)
        self.find_by_XPATH = lambda val: self.driver.find_element(by=By.XPATH,value=val)
        self.find_by_LINK_TEXT = lambda val: self.driver.find_element(by=By.LINK_TEXT,value=val)
        self.find_by_PARTIAL_LINK_TEXT = lambda val: self.driver.find_element(by=By.PARTIAL_LINK_TEXT,value=val)
        # these ones return lists
        self.find_many_by_CSS = lambda val: self.driver.find_elements(by=By.CSS_SELECTOR,value=val)

class Game(GlobalScrape):
    """
    crawler for https://www.game.co.uk/
    """
    def __init__(self,
                 path: str,
                 contact: ContactDetails,
                 payment: PaymentDetails,
                 bot: TelegramBot = None,
                 headless: bool = False
                 ) -> None:
        """
        inputs described in parent class.
        """
        super().__init__(path,contact,payment,bot=bot,headless=headless)

    def close_cookie_policy(self) -> None:
        """
        Safely checks whether there is a cookie policy that must be closed.
        """
        try:
            self.find_by_CSS('.cookiePolicy_inner--actions .cookiePolicy_inner-link').click()
        except exceptions.NoSuchElementException:
            print("Couldn't find Cookie Policy Popup. Proceeding.")
    
    def is_ps5_available(self) -> bool:
        """
        helper function used to check whether the ps5 is available.
        """
        search = self.find_by_CSS('#playstation-5 a')
        if "Out of Stock" in search.text:
            return False
        else:
            return True

    def ps5_refresh(self, url) -> None:
        availability = self.is_ps5_available('#playstation-5 a')
        while not availability:
            time.sleep(random.uniform(7.5,18.2))
            self.driver.refresh()
            time.sleep(2)
            availability = self.is_ps5_available('#playstation-5 a')
        # Onto the Product Page
        self.bot.send_notif("ps5", url) if self.bot is not None else None
        self.find_by_CSS('#playstation-5 a').click()  
    
    def is_product_available(self) -> bool:
        """
        helper function used to check whether stock is available (on product page).
        """
        search = self.find_many_by_CSS('#mainPDPButtons .btnMint a')
        if len(search) == 0:
            return False
        preorder = self.find_many_by_CSS('#mainPDPButtons .btnMint .btnName')
        if "Pre-order" in preorder[0].text:
            return False
        return True
    
    def product_refresh(self, url) -> None:
        availability = self.is_product_available()
        while not availability:
            time.sleep(random.uniform(7.5,18.2))
            self.driver.refresh()
            time.sleep(2)
            availability = self.is_product_available()
        self.bot.send_notif("TBC", url) if self.bot is not None else None
        self.find_by_CSS('#mainPDPButtons .btnMint a').click()

    def fill_checkout_p1(self):
        """
        Fills out page 1 of checkout.
        """
        search = self.find_by_CSS('#mat-select-0')
        search.click()
        search.send_keys(Keys.RETURN)
        
        search = self.find_by_CSS('#mat-input-0')
        search.click()
        search.clear()
        search.send_keys(self.contact_details.f_name)

        search = self.find_by_CSS('#mat-input-1')
        search.click()
        search.clear()
        search.send_keys(self.contact_details.l_name)

        search = self.find_by_CSS('#mat-input-2')
        search.click()
        search.clear()
        search.send_keys(self.contact_details.email)

        search = self.find_by_CSS('#mat-input-3')
        search.click()
        search.clear()
        search.send_keys(self.contact_details.number)

        self.find_by_CSS('.mat-raised-button.mat-accent-cta.game-full-width .mat-button-wrapper').click()

    def fill_checkout_p2(self):
        """
        fills out page 2 of checkout
        """
        self.find_by_PARTIAL_LINK_TEXT('Address Entry').click()

        search = self.find_by_CSS('#mat-select-1')
        search.click()
        search.send_keys(Keys.RETURN)

        search = self.find_by_CSS('#mat-input-5')
        search.click()
        search.send_keys(self.contact_details.street_num + ' ' + self.contact_details.street_name)
        
        search = self.find_by_CSS('#mat-input-8')
        search.click()
        search.send_keys(self.contact_details.county)

        search = self.find_by_CSS('#mat-input-10')
        search.click()
        search.send_keys(self.contact_details.post_code)

        self.find_by_CSS('.mat-raised-button.mat-accent-cta.game-full-width .mat-button-wrapper').click()

    def fill_checkout_p3(self):
        """
        fills out page 3 of checkout
        """
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        self.find_by_CSS('.mat-raised-button.mat-accent-cta .mat-button-wrapper').click()

    def fill_checkout_p4(self):
        """
        fills out page 4 of checkout
        """
        iframe = self.find_by_CSS('.mat-expansion-panel-body .mat-form-field-infix iframe')
        self.driver.switch_to.frame(iframe)
        
        search = self.find_by_NAME('credit-card-number')
        search.send_keys(self.payment_details.card_number)
        self.driver.switch_to.default_content()

        search = self.find_by_CSS('#mat-input-15')
        search.click()
        search.send_keys(self.payment_details.name_on_card)
      
        search = self.find_by_CSS('#mat-input-16')
        search.click()
        search.send_keys(self.payment_details.expiry_date)

        search = self.find_by_CSS('#mat-input-17')
        search.click()
        search.send_keys(self.payment_details.cv2)

        self.find_by_CSS('.save-card .mat-button-wrapper').click()

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        self.find_by_CSS('.game-pt-sm .mat-checkbox-inner-container').click()

    def final_checkout_btn(self):
        """
        clicks the final checkout button.
        """
        self.find_by_CSS('button .game-plr-xxl').click()

    def main(self, url):
        """
        Begins the web crawler process, using the helper functions defined within the class.
        url: absolute url to product page on the game website. Otherwise, the page for the PS5.
        """
        self.driver.get(url)
        self.close_cookie_policy()

        # special condition if searching for a PS5
        # loop refresh until ps5 stock available
        # todo: implement better logic for random refreshing.
        # Also avoid using explicit waits with the implicit driver wait that's already been set.
        if url in 'https://www.game.co.uk/playstation-5':
            try:
                self.ps5_refresh(url)
            except exceptions.NoSuchElementException:
                print("couldnt find target on initial url (ps5)")
                return
        else:
            try:
                self.product_refresh(url)
            except exceptions.NoSuchElementException:
                print("couldnt find target on initial url")
                return

        self.driver.save_screenshot('src/screenshots/Game/stock_avail.png')

        # there's a same page popup to complete
        try:
            search = self.find_by_CSS('.modal-content-scroll-wrapper')
            if "in your basket" not in search.text:
                print("something went wrong when trying to add to basket")
                return
        except exceptions.NoSuchElementException:
            print("couldnt find element in same-page popup")
            return
        
        # proceed to checkout
        try:
            self.find_by_CSS('.modal-content-bottom .secure-checkout').click()
            self.find_by_LINK_TEXT('SECURE CHECKOUT').click()
            self.find_by_LINK_TEXT('Checkout as Guest').click()
        except exceptions.NoSuchElementException:
            print("something went wrong when trying to get to checkout page")
            return
        
        # fill out details 1) Contact Details
        try:
            self.fill_checkout_p1()
        except exceptions.NoSuchElementException:
            print("smth went wrong on contact details page")
            return

        # fill out details 2) Delivery Address
        try:
            self.fill_checkout_p2()
        except exceptions.NoSuchElementException:
            print("smth went wrong on delivery address page")
            return

        # fill out details 3)Delivery Options
        try:
            self.fill_checkout_p3()
        except exceptions.NoSuchElementException:
            print("smth went on wrong on delivery options page")
            return
        
        # fill out details 4)Payment
        try:
            self.fill_checkout_p4()
            self.driver.save_screenshot('screenshots/Game/final_payment.png')
            self.bot.send_final_notif() if self.bot is not None else None
            self.final_checkout_btn()
        except exceptions.NoSuchElementException:
            print("smth went wrong on payment page")
            return

class Argos(GlobalScrape):
    """
    crawler for https://www.argos.co.uk/
    """
    def __init__(self,
                 path: str,
                 contact: ContactDetails,
                 payment: PaymentDetails,
                 login: LoginDetails,
                 bot : TelegramBot = None,
                 headless: bool = False
                 ) -> None:
        """
        inputs defined in parent class.
        """
        super().__init__(path,contact,payment,login, bot, headless)

    def close_cookie_policy(self):
        """
        Safely checks whether there is a cookie policy that must be closed.
        """
        try:
            self.find_by_CSS('.consent_prompt_footer #consent_prompt_submit').click()
        except exceptions.NoSuchElementException:
            print("couldn't find cookie policy to close. Proceeding.")

    def add_to_trolley(self,value: str):
        self.find_by_CSS(value).click()

    def check_trolley_popup(self):
        popups = self.driver.find_elements(by=By.XPATH,value='/html/body/div[1]/div/div[2]/main/div[2]/section[1]/div[2]/div[1]/div/div[2]/div[2]/button')
        if len(popups) == 1:
            popups[0].click()

    def dropdown_select_adress(self):
        select = Select(self.driver.find_element(by=By.CSS_SELECTOR,value='#addressResults'))
        select.select_by_visible_text(self.contact_details.number + ', '+\
                                        self.contact_details.street_name + ', '+\
                                        self.contact_details.town.upper())

    def enter_number(self):
        search = self.find_by_CSS('#delivery_phone')
        search.click()
        search.send_keys(self.contact_details.number)

    def select_delivery_slot(self):
        delivery_slots = self.driver.find_elements(by=By.CSS_SELECTOR,value='.smallItemsSlotTable tbody :not(.noSlot).blockContent')
        delivery_slots[0].click()
        self.find_by_CSS('#contextualSubmitContinueEcomm').click()

    def dropdown_select_card_type(self):
        dic = {"VISA Credit": "VISAC", "VISA": "VISAD", "VISA Electron": "ELECTRON",\
            "Mastercard": "MASTERCARD", "Maestro": "MAESTRO", "American Express": "AMEX"}
        payment_value = dic[self.payment_details.card_type]

        Select(self.find_by_CSS('#cardTypeSelect')).select_by_value(payment_value)

    def dropdown_select_card_month(self):
        expiry_month = self.payment_details.expiry_date[:2]
        Select(self.find_by_CSS('#expiryDateMonth')).select_by_value(expiry_month)
        
    def dropdown_select_card_year(self):
        expiry_year = self.payment_details.expiry_date[3:]
        Select(self.find_by_CSS('#expiryDateYear')).select_by_value('20' + expiry_year)

    def main(self, url):
        self.driver.get(url)
        self.close_cookie_policy()
        
        # Keep searching for add to trolley button (refreshing page), until it is there.
        while True:
            try:
                self.add_to_trolley('.xs-8--none button')
            except exceptions.NoSuchElementException:
                time.sleep(random.uniform(7.5,18.2))
                self.driver.refresh()
                time.sleep(2)
            else:
                break
        
        # proceed to checkout page
        try:
            self.find_by_LINK_TEXT('Continue without insurance').click()

            search = self.find_by_XPATH('/html/body/div[1]/div/div[2]/main/div[2]/section[1]/div[2]/div/div/div[2]/div/form/div[2]/div/input')
            search.click()
            search.send_keys(self.contact_details.post_code)

            self.find_by_XPATH('/html/body/div[1]/div/div[2]/main/div[2]/section[1]/div[2]/div/div/div[2]/div/form/div[3]/button[2]').click()
            self.check_trolley_popup()
            self.find_by_XPATH('/html/body/div[1]/div/div[2]/main/div[2]/section[3]/div[2]/div[2]/div/div/div/button/span[2]').click()
        except exceptions.NoSuchElementException:
            print("smth went wrong when trying to continue to checkout")
            return
        except exceptions.ElementClickInterceptedException:
            return

        # log in
        try:
            search = self.find_by_CSS('.form-group__input-wrapper #email')
            search.click()
            search.send_keys(self.login.user)

            search = self.find_by_CSS('.form-group__input-wrapper #password')
            search.click()
            search.send_keys(self.login.pw)

            self.find_by_XPATH('/html/body/div[1]/div[2]/main/div/div/form/button/div/div[1]').click()
            self.find_by_XPATH('/html/body/div[1]/div/div[2]/main/div[2]/section[3]/div[2]/div[2]/div/div/div/button/span[2]').click()
        except exceptions.NoSuchElementException:
            print("smth went wrong when trying to login")
            return
        
        # proceed to checkout
        try:
            if "TrolleyYourDetails" in self.driver.current_url:
                self.find_by_CSS('.well.border-straight-xs.gutter .btn.btn-block.btn-secondary').click()
                self.enter_number()
                self.dropdown_select_adress()
                self.find_by_CSS('#deliveryAddress .btn.btn-block.btn-primary').click()
                self.find_by_CSS('.panel-body .btn.btn-block.btn-primary').click()
            self.select_delivery_slot()
        except exceptions.NoSuchElementException:
            print("smth went wrong after logging in and continuing to check out")
            return
        
        #payment
        try:
            # complete first payment page
            self.dropdown_select_card_type()
            self.find_by_CSS('#continue-to-payment-details').click()
            # payment page 2 (within iframe)
            # select iframe
            iframe = self.find_by_NAME('iFrame_a')
            self.driver.switch_to.frame(iframe)
            # card num
            search = self.find_by_CSS('#hps-pan')
            search.click()
            search.send_keys(self.payment_details.card_number)
            #expiry date
            self.dropdown_select_card_month()
            self.dropdown_select_card_year()
            #name on card
            search = self.find_by_CSS('#nameOnCard')
            search.click()
            search.send_keys(self.payment_details.name_on_card)
            #security code
            search = self.find_by_CSS('#hps-cvv')
            search.click()
            search.send_keys(self.payment_details.cv2)
            #click pay now
            self.bot.send_final_notif()
            self.driver.save_screenshot('src/screenshots/Argos/final.png')
            time.sleep(15)
            self.find_by_CSS('#hps-continue').click()
        except exceptions.NoSuchElementException:
            print("smth went wrong on payment page")
            return

