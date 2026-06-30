# v3.0.0-beta: Zerodha broker support

## Why

Dvarpal currently only automates login for Upstox. The login flow, token
exchange, and validation logic are hardcoded to Upstox's specifics inside
`SessionManager`, so adding a second broker requires pulling those pieces
apart into broker-specific implementations behind a common interface.

## Key differences: Upstox vs Zerodha (Kite Connect)

| | Upstox | Zerodha |
|---|---|---|
| Login form | mobile -> OTP -> PIN | user_id + password -> TOTP/PIN (2FA) |
| Redirect param | `code` | `request_token` |
| Token exchange | POST `code` + `client_secret` directly | POST `request_token` + SHA-256 checksum of `api_key+request_token+api_secret` |
| Token response shape | `{access_token: ...}` | `{data: {access_token: ...}}` |
| Validation auth header | `Bearer <token>` | `token <api_key>:<access_token>` |

## Architecture

- `dvarpal/brokers/base.py` -- `BaseSessionManager`: shared Firefox-ESR
  driver setup, access-token file caching, `generate_access_token()` /
  `is_session_valid()` skeleton. Abstract hooks:
  - `_perform_browser_login(driver) -> code_or_token`
  - `_exchange_code_for_token(code_or_token) -> access_token`
  - `_build_auth_header(access_token) -> dict`
- `dvarpal/brokers/upstox.py` -- `UpstoxSessionManager`, current
  `session_firefox.py` logic moved in unchanged.
- `dvarpal/brokers/zerodha.py` -- `ZerodhaSessionManager`, new.
- `dvarpal/session.py` (Chrome/undetected-chromedriver path) is deleted;
  README already marks it deprecated. `undetected_chromedriver` dependency
  dropped from `setup.py`.
- `dvarpal.get_session_manager(config)` factory picks the subclass based on
  `config.broker`.

## Config changes

- `SessionConfig` gains `broker: upstox|zerodha`.
- New optional fields for Zerodha: `user_id`, `password`.
- Reused as-is for Zerodha: `client_id`/`client_secret` (-> api_key/api_secret),
  `totp_secret_key`, `pin`, `redirect_uri`, `session_validation_url`.
- New sample: `config_samples/zerodha.dvarpal.yaml`.

## Tests / docs

- `test/test_zerodha_session_manager.py` mirrors the existing Upstox test.
- README: add Zerodha to supported brokers, update usage snippet to use the
  factory.

## Open risk

Zerodha's login-page DOM selectors (user_id/password/TOTP fields) are
implemented from the commonly known Kite Connect login flow structure but
have not been verified against the live page. Amit will do one live login
run on `feature/v3` and report back any selector mismatches to patch.

## Branch / versioning

All work happens on `feature/v3` (never `main`). Target version
`3.0.0-beta` in `setup.py`.
