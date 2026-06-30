import hashlib
import time

import pyotp
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

from dvarpal.brokers.base import BaseSessionManager


class ZerodhaSessionManager(BaseSessionManager):

    def _build_authn_url(self) -> str:
        return f'{self._config.authn_url}?v=3&api_key={self._config.client_id}'

    def _perform_browser_login(self, driver: webdriver.Firefox) -> str:
        user_id = driver.find_element(By.ID, "userid")
        user_id.send_keys(self._config.user_id)
        password = driver.find_element(By.ID, "password")
        password.send_keys(self._config.password)
        self._logger.info('==> user_id and password entered')
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)

        # Zerodha's 2FA page reuses id="userid" for its TOTP/PIN input
        # (distinguishable only by label="External TOTP" and type="number").
        twofa_field = driver.find_element(By.ID, "userid")
        if self._config.totp_secret_key:
            twofa_field.send_keys(pyotp.TOTP(self._config.totp_secret_key).now())
            self._logger.info('==> TOTP entered')
        else:
            twofa_field.send_keys(self._config.pin)
            self._logger.info('==> PIN entered')
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)

        # The first time an app is authorized, Kite Connect shows an
        # explicit consent screen (same submit button) before redirecting
        # with request_token; subsequent logins skip straight past it.
        if 'request_token=' not in driver.current_url:
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            self._logger.info('==> app authorization confirmed')
            time.sleep(5)

        url = driver.current_url
        initial_request_token = url.split('request_token=')[1]
        return initial_request_token.split('&')[0]

    def _exchange_code_for_token(self, code: str) -> str:
        api_key = self._config.client_id
        api_secret = self._config.client_secret
        checksum = hashlib.sha256(f'{api_key}{code}{api_secret}'.encode('utf-8')).hexdigest()

        data = {
            'api_key': api_key,
            'request_token': code,
            'checksum': checksum,
        }
        resp = requests.post(url=self._config.authz_url, data=data)
        assert resp.status_code == 200, f"Error exchanging request_token for access_token:\n {resp.json()}"

        access_token = resp.json()['data']['access_token']
        self._logger.debug(f'access_token: {access_token}')
        return access_token

    def _build_auth_header(self) -> dict:
        return {
            "Authorization": f"token {self._config.client_id}:{self._access_token}",
        }
