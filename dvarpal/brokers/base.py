import logging
import os
import time
from abc import ABC, abstractmethod

import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from dvarpal.config import SessionConfig


class BaseSessionManager(ABC):

    def __init__(self, config: SessionConfig):
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._access_token = ''
        self._config = config

    def generate_access_token(self):

        # check if session_token file exists. If it exists, load token from file.
        self._load_access_token_from_file()

        if self._access_token is not None and self.is_session_valid():
            self._logger.info("Access token is still valid. Nothing to do.")
            return

        access_token = self._get_access_token()
        self._access_token = access_token
        self._logger.info(f'New access token acquired: {access_token}')
        self._save_access_token(access_token)

    def get_access_token(self):
        return self._access_token

    def is_session_valid(self) -> bool:
        url = self._config.session_validation_url
        headers = {
            **self._build_auth_header(),
            "Accept": "application/json",
        }

        try:
            response = requests.get(url, headers=headers)
            body = response.text
            self._logger.info(f"Ping response: http-status: {response.status_code} > body: {body}")
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException as e:
            self._logger.error("Ping failed!", e)

        return False

    def _save_access_token(self, access_token: str):
        try:
            with open(self._config.access_token_file, 'w') as file:
                file.write(access_token)
            self._logger.info(f"Access token successfully written to {self._config.access_token_file}")
        except Exception as e:
            raise Exception(f"Failed to save access token to file {self._config.access_token_file}", e)

    def _load_access_token_from_file(self):
        if not os.path.exists(self._config.access_token_file):
            return

        with open(self._config.access_token_file, 'r') as file:
            content = file.read()
        self._access_token = content
        self._logger.info(f'Loaded access token from file {self._config.access_token_file}')

    def _create_driver(self) -> webdriver.Firefox:
        options = Options()
        # Explicitly use Firefox ESR
        options.binary_location = "/usr/bin/firefox-esr"
        if self._config.browser_headless:
            options.add_argument("--headless")
        options.set_preference("general.useragent.override", self._config.browser_useragent)
        return webdriver.Firefox(options=options)

    def _get_access_code(self) -> str:
        driver = self._create_driver()
        try:
            driver.get(self._build_authn_url())
            time.sleep(5)
            self._logger.info('==> browser launched')

            code = self._perform_browser_login(driver)
            self._logger.debug(f'access_code: {code}')
        finally:
            if driver is not None:
                driver.close()
                driver.quit()

        return code

    def _get_access_token(self) -> str:
        code = self._get_access_code()
        return self._exchange_code_for_token(code)

    @abstractmethod
    def _build_authn_url(self) -> str:
        """Builds the broker's login/authorization dialog URL."""

    @abstractmethod
    def _perform_browser_login(self, driver: webdriver.Firefox) -> str:
        """Drives the broker's login form to completion and returns the
        authorization code / request token scraped from the redirect URL."""

    @abstractmethod
    def _exchange_code_for_token(self, code: str) -> str:
        """Exchanges the authorization code / request token for an access token."""

    @abstractmethod
    def _build_auth_header(self) -> dict:
        """Builds the Authorization header used to validate the session."""
