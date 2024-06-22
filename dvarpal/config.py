import logging
import os

import yaml


class SessionConfig:

    def __init__(self):
        cfg = SessionConfig._load_config_from_file()
        self.access_token_file = cfg.get('access_token_file') if cfg.get('access_token_file') else os.path.join(os.getenv('HOME'), 'dvarpal_session')

        self.authn_url: str = cfg['authn_url']
        self.authz_url: str = cfg['authz_url']
        self.redirect_uri: str = cfg['redirect_uri']
        self.session_validation_url: str = cfg['session_validation_url']
        self.user_agent = cfg['user_agent']

        self.client_id: str = cfg['client_id']
        self.client_secret: str = cfg['client_secret']
        self.mobile: str = cfg['mobile']
        self.totp_secret_key: str = cfg['totp_secret_key']
        self.pin: str = cfg['pin']

    @staticmethod
    def _load_config_from_file():
        config_file = os.path.join(os.getenv('HOME'), 'dvarpal.yaml')
        if not os.path.exists(config_file):
            pass

        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        # logging.info(f'Loaded dvarpal config from file {config_file}')
        return config_data

