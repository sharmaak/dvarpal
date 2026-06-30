import os

import yaml

ALL_BROKERS = ('upstox', 'zerodha')
DEFAULT_USERAGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'

# Top-level yaml keys that are structural (broker selector + per-broker
# sections) rather than fields shared across brokers.
_STRUCTURAL_KEYS = {'broker', *ALL_BROKERS}


class SessionConfig:

    def __init__(self, broker: str = None):
        full_cfg = SessionConfig._load_config_from_file()
        broker = broker or full_cfg.get('broker', 'upstox')
        if broker == 'all':
            raise ValueError(
                "broker 'all' selects multiple brokers; use dvarpal.get_session_managers() "
                "instead of constructing a single SessionConfig()")
        if broker not in ALL_BROKERS:
            raise ValueError(f"Unsupported broker '{broker}'. Supported brokers: {list(ALL_BROKERS)}")

        cfg = SessionConfig._resolve_broker_section(full_cfg, broker)
        self.broker = broker
        self.access_token_file = cfg.get('access_token_file') or SessionConfig._default_access_token_file(broker)

        self.authn_url: str = cfg['authn_url']
        self.authz_url: str = cfg['authz_url']
        self.redirect_uri: str = cfg['redirect_uri']
        self.session_validation_url: str = cfg['session_validation_url']
        self.browser_useragent = cfg.get('browser_useragent', DEFAULT_USERAGENT)
        self.browser_headless = cfg.get('browser_headless', False)

        self.client_id: str = cfg['client_id']
        self.client_secret: str = cfg['client_secret']

        # Upstox: mobile + totp_secret_key + pin.
        # Zerodha: user_id + password, then totp_secret_key or pin for 2FA.
        self.mobile = cfg.get('mobile')
        self.user_id = cfg.get('user_id')
        self.password = cfg.get('password')
        self.totp_secret_key = cfg.get('totp_secret_key')
        self.pin = cfg.get('pin')

    @staticmethod
    def selected_brokers() -> list:
        """Brokers selected by the top-level `broker` field: a single name,
        or both, when it is set to `all`."""
        full_cfg = SessionConfig._load_config_from_file()
        broker = full_cfg.get('broker', 'upstox')
        return list(ALL_BROKERS) if broker == 'all' else [broker]

    @staticmethod
    def _resolve_broker_section(full_cfg: dict, broker: str) -> dict:
        # Fields outside the broker sections (e.g. browser_headless) are
        # shared defaults; a broker's own section overrides them.
        shared = {k: v for k, v in full_cfg.items() if k not in _STRUCTURAL_KEYS}
        section = full_cfg.get(broker) or {}
        return {**shared, **section}

    @staticmethod
    def _load_config_from_file():
        # Choose home directory env variable based on OS. os.name = 'nt' for windows.
        config_file = os.path.join(SessionConfig.get_home_dir(), ".dvarpal", 'dvarpal.yaml')
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        return config_data

    @staticmethod
    def _default_access_token_file(broker: str):
        return os.path.join(SessionConfig.get_home_dir(), ".dvarpal", f"dvarpal_session_{broker}")

    @staticmethod
    def get_home_dir():
        return os.getenv('USERPROFILE') if os.name == 'nt' else os.getenv('HOME')
