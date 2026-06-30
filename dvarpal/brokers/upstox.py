import time
from urllib.parse import quote

import pyotp
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

from dvarpal.brokers.base import BaseSessionManager


class UpstoxSessionManager(BaseSessionManager):

    def _build_authn_url(self) -> str:
        return (f'{self._config.authn_url}?'
                f'response_type=code&'
                f'client_id={self._config.client_id}&'
                f'redirect_uri={quote(self._config.redirect_uri)}')

    def _perform_browser_login(self, driver: webdriver.Firefox) -> str:
        phone_no = driver.find_element(By.ID, "mobileNum")
        phone_no.send_keys(self._config.mobile)
        self._logger.info('==> mobile number entered')

        get_otp_btn = driver.find_element(By.ID, "getOtp")
        get_otp_btn.submit()
        self._logger.info('==> OTP requested')
        time.sleep(5)

        otp = driver.find_element(By.ID, "otpNum")
        totp = pyotp.TOTP(self._config.totp_secret_key).now()
        otp.send_keys(totp)
        self._logger.info('==> TOTP entered')
        continue_btn = driver.find_element(By.ID, "continueBtn")
        continue_btn.submit()
        self._logger.info('==> TOTP submitted')
        time.sleep(5)

        pin = driver.find_element(By.ID, "pinCode")
        pin.send_keys(self._config.pin)
        self._logger.info('==> PIN entered')
        submit = driver.find_element(By.ID, "pinContinueBtn")
        submit.click()
        self._logger.info('==> PIN submitted')
        time.sleep(5)

        url = driver.current_url
        initial_access_code = url.split('code=')[1]
        return initial_access_code.split('&')[0]

    def _exchange_code_for_token(self, code: str) -> str:
        s = requests.Session()
        headers = {"accept": "application/json", "Api-Version": "2.0",
                   "content-type": "application/x-www-form-urlencoded"}
        data = {'code': code,
                'client_id': self._config.client_id,
                'client_secret': self._config.client_secret,
                'redirect_uri': self._config.redirect_uri,
                'grant_type': 'authorization_code'
                }
        resp = s.post(url=self._config.authz_url, headers=headers, data=data)
        assert resp.status_code == 200, f"Error in r3:\n {resp.json()}"

        json_response = resp.json()
        access_token = json_response['access_token']
        self._logger.debug(f'access_token: {access_token}')
        return access_token

    def _build_auth_header(self) -> dict:
        return {
            "Api-Version": "2.0",
            "Authorization": f"Bearer {self._access_token}",
        }
