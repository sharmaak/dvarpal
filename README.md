# Dvarpal
'Dvarpal' (Sanskrit: द्वारपाल) means 'door guard'. Davrpal aims to provide automated 
login mechanism for Indian stock brokers. 

<!-- TOC -->
* [Dvarpal](#dvarpal)
  * [Supported Brokers](#supported-brokers)
  * [Installation](#installation)
  * [Configuration](#configuration)
  * [Usage](#usage)
  * [Sample Code](#sample-code)
  * [Upgrading from 2.x](#upgrading-from-2x)
<!-- TOC -->

## Supported Brokers

1. Upstox
2. Zerodha

Dvarpal is designed so that support for more brokers can be added easily. 

## Installation
```commandline
pip install dvarpal
```

## Prerequisite
Dvarpal uses Selenium + Firefox ESR + Gecko Driver to perform automated logins. 
Firefox ESR and Gecko Driver have to be installed on operating system. For linux, 
this is automated in the script [install-firefox-esr-geckodriver.sh](etc/install-firefox-esr-geckodriver.sh)

For Windows and Mac, it is left upto the user to perform similar installations. 

## Configuration

Dvarpal picks up its configuration file from `${HOME}/.dvarpal/dvarpal.yaml`. Its structure is
uniform regardless of how many brokers you use: only `broker`, `browser_useragent`, and
`browser_headless` live at the top level since they're common to every broker; everything
else is broker-specific and goes under its own `upstox:` / `zerodha:` section. The top-level
`broker` field selects which section(s) are used: `upstox`, `zerodha`, or `all` (both).

Upstox:
```yaml
broker: upstox

browser_useragent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1
browser_headless: false

upstox:
  authn_url: https://api.upstox.com/v2/login/authorization/dialog
  authz_url: https://api.upstox.com/v2/login/authorization/token
  session_validation_url: https://api-v2.upstox.com/user/profile

  # The following properties are part of upstox app created for API access
  client_id: <your-client-id>
  client_secret: <your-client-secret>
  redirect_uri: <your-redirect-url>

  # TOTP secret key generated using https://help.upstox.com/support/solutions/articles/260343-what-is-totp-and-how-to-enable-totp-for-my-account-
  totp_secret_key: <your TOTP secret key>

  mobile: <your registered mobile number>
  pin: <your pin>
```

Zerodha:
```yaml
broker: zerodha

browser_useragent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1
browser_headless: false

zerodha:
  authn_url: https://kite.zerodha.com/connect/login
  authz_url: https://api.kite.trade/session/token
  session_validation_url: https://api.kite.trade/user/profile
  redirect_uri: <your-redirect-url>

  # The following properties are part of the Kite Connect app created for API access
  client_id: <your-api-key>
  client_secret: <your-api-secret>

  user_id: <your zerodha user id>
  password: <your zerodha password>

  # Set totp_secret_key if your account's second factor is TOTP, otherwise set pin.
  totp_secret_key: <your TOTP secret key>
  pin: <your pin>
```

`broker: all` follows the same shape with both `upstox:` and `zerodha:` sections present --
see [config_samples/all-brokers.dvarpal.yaml](config_samples/all-brokers.dvarpal.yaml).

For more samples, refer to the [config_samples](./config_samples) directory.

## Usage

Starting version 2.0.0, Dvarpal uses Firefox ESR + Gecko Driver for all brokers.

For a single broker (`broker: upstox` or `broker: zerodha`):
```python
from dvarpal import get_session_manager

session_manager = get_session_manager()  # picks the broker based on config.broker
session_manager.generate_access_token()  # to generate a new access token
session_manager.is_session_valid()  # to check if access token is valid
session_manager.get_access_token()  # get the actual access token string
```

For `broker: all`, use `get_session_managers()` instead, which returns one manager per
configured broker:
```python
from dvarpal import get_session_managers

for broker_name, session_manager in get_session_managers().items():
    session_manager.generate_access_token()
    print(broker_name, session_manager.get_access_token())
```

You can also instantiate a broker-specific manager directly, e.g. 
`from dvarpal.brokers.zerodha import ZerodhaSessionManager`.

Each broker's access_token is saved to its own file, `${HOME}/.dvarpal/dvarpal_session_<broker>` 
(e.g. `dvarpal_session_upstox`), so running multiple brokers never overwrites another's token. 
Before generating a new access token, dvarpal checks that file. If it exists, it loads the 
access token from file and uses it. If the token is expired or invalid, dvarpal generates a new one.

## Sample Code

A complete, runnable script is at [examples/generate_token.py](examples/generate_token.py). It 
works no matter how many brokers `broker` in `dvarpal.yaml` selects, since `get_session_managers()` 
always returns one manager per selected broker (a dict with a single entry when only one broker 
is configured):

```python
import logging

from dvarpal import get_session_managers

logging.basicConfig(level=logging.INFO)

for broker_name, session_manager in get_session_managers().items():
    session_manager.generate_access_token()
    print(f"[{broker_name}] access_token: {session_manager.get_access_token()}")
    print(f"[{broker_name}] session valid: {session_manager.is_session_valid()}")
```

Run it with:
```commandline
python3 examples/generate_token.py
```

The first run opens a browser and drives the login form; subsequent runs reuse the cached token 
from `${HOME}/.dvarpal/dvarpal_session_<broker>` as long as it's still valid, and skip the browser 
entirely.

## Upgrading from 2.x

3.0.0 is a deliberate breaking release -- multi-broker support couldn't be bolted onto the 2.x 
shape cleanly, so these changes are not backward compatible:

* **Import path**: `dvarpal.session` (Chrome) and `dvarpal.session_firefox` no longer exist. 
  Use `from dvarpal import get_session_manager` (or import a broker class from `dvarpal.brokers.*` 
  directly) instead of `from dvarpal.session_firefox import SessionManager`.
* **Config file shape**: `dvarpal.yaml` no longer accepts broker-specific fields 
  (`client_id`, `authn_url`, `mobile`, etc.) at the top level. They must be nested under an 
  `upstox:` or `zerodha:` section, as shown above -- only `broker`, `browser_useragent`, and 
  `browser_headless` stay at the top level.
* **Token cache filename**: the cached access token moved from `${HOME}/.dvarpal/dvarpal_session` 
  to `${HOME}/.dvarpal/dvarpal_session_<broker>`. A token cached by 2.x is not picked up after 
  upgrading; dvarpal just performs one fresh login and re-caches it at the new path.

The underlying login automation for Upstox itself (form fields, OTP/TOTP/PIN flow, token 
exchange) is unchanged from 2.x -- only how you reach it changed.
