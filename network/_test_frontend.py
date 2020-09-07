import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from . models import User


class TestFrontEndPages(StaticLiveServerTestCase):

    def setUp(self):
        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
        self.driver = webdriver.Chrome(chromedriver_path)

        User.objects.create_user(
            username="pith",
            password="5678"
        )
        # Log in user
        self.assertTrue(self.client.login(username="pith", password="5678"))
        cookie = self.client.cookies["sessionid"]
        self.driver.get("http://127.0.0.1:8000/")
        self.driver.add_cookie({
            "name": "sessionid",
            "value": cookie.value,
            "secure": False,
            "path": "/"
        })

    def tearDown(self):
        self.driver.close()

    def login(self, **kwargs):
        self.driver.get("http://127.0.0.1:8000/login")
        username = self.driver.find_element_by_name("username")
        password = self.driver.find_element_by_name("password")
        login_btn = self.driver.find_element_by_id("login-btn")
        username.send_keys(kwargs["username"])
        password.send_keys(kwargs["password"])
        login_btn.click()

    def test_error_message_for_invalid_login_credentials(self):
        """Test error message for invalid username/password."""
        self.driver.get("http://127.0.0.1:8000/login")
        username = self.driver.find_element_by_name("username")
        password = self.driver.find_element_by_name("password")
        login_btn = self.driver.find_element_by_id("login-btn")
        username.send_keys("foo")
        password.send_keys("123123")
        login_btn.click()
        error_msg = self.driver.find_element_by_id("error-message").text
        self.assertEqual(error_msg, "Invalid username and/or password.")

    def test_valid_login(self):
        """Test valid login using valid username/password."""
        home_url = "http://127.0.0.1:8000/login?next=/"
        current_url = self.driver.current_url
        self.assertEqual(current_url, home_url)

    def test_display_error_message_for_username_already_exists(self):
        """
        Test if error message is displayed while trying to register
        with an existing username.
        """
        self.driver.get("http://127.0.0.1:8000/register")
        username = self.driver.find_element_by_name("username")
        register_btn = self.driver.find_element_by_id("register-btn")
        username.send_keys("foo")
        register_btn.click()
        error_msg = self.driver.find_element_by_id("error-message").text
        self.assertEqual(error_msg, "Username already taken.")
