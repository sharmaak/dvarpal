# Dvarpal
'Dvarpal' (Sanskrit: द्वारपाल) means 'door guard'. Davrpal aims to provide automated 
login mechanism for Indian stock brokers. 

<!-- TOC -->
* [Dvarpal](#dvarpal)
  * [Supported Brokers](#supported-brokers)
  * [Installation](#installation)
  * [Configuration](#configuration)
  * [Usage](#usage)
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

Dvarpal picks up its configuration file from `${HOME}/.dvarpal/dvarpal.yaml`. The top-level 
`broker` field selects which broker(s) to log into: `upstox`, `zerodha`, or `all` (both).

When a single broker is selected, its fields can be written flat at the top level, as shown
below. When `broker: all` is selected, each broker needs its own `upstox:`/`zerodha:` section,
since each has a distinct client_id/secret and credentials that can't share a flat namespace --
see [config_samples/all-brokers.dvarpal.yaml](config_samples/all-brokers.dvarpal.yaml). Fields
left at the top level outside those sections (e.g. `browser_headless`) are shared defaults that
any broker section can still override.

Upstox:
```yaml
broker: upstox

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
