import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


class TestFrontEndPages(StaticLiveServerTestCase):

    def setUp(self):
        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
        self.driver = webdriver.Chrome(chromedriver_path)

    def tearDown(self):
        self.driver.close()

    def test_error_message_for_invalid_login_credentials(self):
        """Test error message for invalid username/password."""
        self.driver.get("http://127.0.0.1:8000/login")
        username = self.driver.find_element_by_name("username")
        password = self.driver.find_element_by_name("password")
        login_btn = self.driver.find_element_by_id("login-btn")
        username.send_keys("foo")
        password.send_keys("123123")
        login_btn.click()
        self.assertIn(
            "Invalid username and/or password." in self.driver.page_source
        )

    def test_valid_login(self):
        """Test valid login using valid username/password."""
        self.driver.get("http://127.0.0.1:8000/login")
        username = self.driver.find_element_by_name("username")
        password = self.driver.find_element_by_name("password")
        login_btn = self.driver.find_element_by_id("login-btn")
        username.send_keys("foo")
        password.send_keys("123")
        login_btn.click()
        home_url = "http://127.0.0.1:8000/"
        current_url = self.driver.current_url
        self.assertEqual(current_url, home_url)
