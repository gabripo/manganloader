import os
import time
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

SELENIUM_LOAD_TIME_SHORT_S = 1
SELENIUM_LOAD_TIME_LONG_S = 5
class SeleniumManager():
    def __init__(
            self,
            driver_type: str = None,
            download_directory: str = None,
            unlimited_downloads_allowed: bool = False,
            headless_mode: bool = False,
            docker_support: bool = False,
            ):
        self.driver_type = None        
        self.driver_options = None
        self.service = None
        self.driver = None

        self.set_driver_type(driver_type)
        self.generate_driver_options({
            'download_directory': download_directory,
            'unlimited_downloads': unlimited_downloads_allowed,
            'headless_mode': headless_mode,
            'docker_support': docker_support,
        })

    def set_driver_type(self, driver_type: str = None):
        if not SeleniumManager.check_supported_driver_type(driver_type):
            return
        self.driver_type = driver_type

    def generate_driver_options(self, options_dict: dict = {}):
        if self.driver_type is None:
            print("Driver type not specified!")
            return
        if self.driver_type == "chrome":
            self.driver_options = webdriver.ChromeOptions()

            if options_dict.get('unlimited_downloads', False):
                output_directory = options_dict.get('download_directory', os.getcwd())
                self.driver_options.add_experimental_option("prefs", {
                        "download.default_directory": output_directory,
                        "download.prompt_for_download": False,
                        "download.directory_upgrade": True,
                        "safebrowsing.enabled": True,
                        "profile.default_content_setting_values.automatic_downloads": 1,
                        "profile.default_content_setting_values.popups": 0,
                    })

            if options_dict.get('headless_mode', False):
                self.driver_options.add_argument("--headless")

            if options_dict.get('docker_support', False):
                self.driver_options.add_argument("--no-sandbox")
                self.driver_options.add_argument("--disable-dev-shm-usage")

            if options_dict.get('disable_cors', False):
                self.driver_options.add_argument("--disable-web-security")

    def clear_driver_options(self):
        self.driver_options = None
        
    def create_service(self):
        if not SeleniumManager.check_supported_driver_type(self.driver_type):
            return    
        if self.driver_type == "chrome":
            self.service = ChromeService(ChromeDriverManager().install())
        else:
            print("No service has been created!")
            
    def create_driver(self):
        if not SeleniumManager.check_supported_driver_type(self.driver_type):
            return
        self.create_service()
        if self.driver_type == "chrome":
            if self.driver_options is not None:
                self.driver = webdriver.Chrome(
                    service=self.service,
                    options=self.driver_options
                    )
            else:
                self.driver = webdriver.Chrome(service=self.service)
        else:
            print("No driver has been created!")

    def get_driver(self):
        if not self.is_driver_available():
            return
        return self.driver
    
    def find_images(self):
        if not self.is_driver_available():
            return
        return self.driver.find_elements(By.TAG_NAME, 'img')
    
    def find_links(self):
        if not self.is_driver_available():
            return
        return self.driver.find_elements(By.TAG_NAME, 'a')
    
    @classmethod
    def find_button_by_text(self, driver = None, button_text: str = None):
        if driver is None:
            print(f"Invalid driver! Impossible to search the button with text {button_text}")
            return
        if button_text is None:
            print("Button name to search for was not specified!")
            return
        
        try:
            button = driver.find_element(
                    By.XPATH,
                    f"//button[contains(text(), '{button_text}')]",
                )
            return button
        except Exception as exc:
            print(f"Impossible to find button named {button_text} : {exc}")

    @classmethod
    def find_element_by_xpath(self, driver = None, element_xpath: str = None):
        if driver is None:
            print(f"Invalid driver! Impossible to search element with XPATH {element_xpath}")
            return
        if element_xpath is None:
            print("XPATH to search for was not specified!")
            return
        
        try:
            element = driver.find_element(
                    By.XPATH,
                    f"{element_xpath}",
                )
            return element
        except Exception as exc:
            print(f"Impossible to find element with XPATH {element_xpath} : {exc}")

    @classmethod
    def scroll_down(self, driver = None, sleep_time: float = SELENIUM_LOAD_TIME_SHORT_S):
        if driver is None:
            print(f"Invalid driver! Impossible to scroll down!")
            return
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            time.sleep(sleep_time)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        driver.execute_script("window.scrollTo(0, 0);") # scroll back when finished

    @classmethod
    def save_image_element_with_driver(
        self,
        driver,
        img_element,
        output_folder: str,
        filename: str,
        ) -> str:        
        try:
            img_width = driver.execute_script("return arguments[0].naturalWidth", img_element)
            img_height = driver.execute_script("return arguments[0].naturalHeight", img_element)

            img_data = driver.execute_script(f"""
            var canvas = document.createElement('canvas');
            var context = canvas.getContext('2d');
            var img = arguments[0];
            canvas.width = {img_width};
            canvas.height = {img_height};
            context.drawImage(img, 0, 0);
            return canvas.toDataURL('image/png').substring(22);
            """, img_element)

            img_path = os.path.join(output_folder, filename)
            with open(img_path, 'wb') as img_file:
                img_file.write(base64.b64decode(img_data))
            return img_path
        except Exception as exc:
            print(f"Error while executing Javascript with input image {img_element.get_attribute('src')}")
    
    @classmethod
    def javascript_actions(self, driver, javascript_args: dict = {}):
        if 'buttons' in javascript_args.keys():
            buttons_to_press = javascript_args['buttons']
            for button_name in buttons_to_press:
                button = SeleniumManager.find_button_by_text(driver, button_text=button_name)
                driver.execute_script("arguments[0].click();", button)
                time.sleep(SELENIUM_LOAD_TIME_SHORT_S)

        if 'buttons_xpath' in javascript_args.keys():
            buttons_xpath_to_press = javascript_args['buttons_xpath']
            for button_xpath in buttons_xpath_to_press:
                button = SeleniumManager.find_element_by_xpath(driver, element_xpath=button_xpath)
                driver.execute_script("arguments[0].click();", button)
                time.sleep(SELENIUM_LOAD_TIME_SHORT_S)

        if 'scrolls' in javascript_args.keys():
            num_scrolls = max(1, javascript_args['scrolls'])
            for _ in range(num_scrolls):
                SeleniumManager.scroll_down(driver=driver, sleep_time=SELENIUM_LOAD_TIME_SHORT_S)
        
    @staticmethod
    def check_supported_driver_type(driver_type):
        supported_driver_types = {
            'chrome',
        }
        is_driver_type_supported = driver_type in supported_driver_types
        if not is_driver_type_supported:
            print(f"Driver type {driver_type} is not supported!")
        return is_driver_type_supported
    
    def is_driver_available(self):
        if self.driver is None:
            print("No driver available!")
            return False
        return True

    