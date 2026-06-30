from dvarpal.brokers.base import BaseSessionManager
from dvarpal.brokers.upstox import UpstoxSessionManager
from dvarpal.brokers.zerodha import ZerodhaSessionManager
from dvarpal.config import SessionConfig

_BROKERS = {
    'upstox': UpstoxSessionManager,
    'zerodha': ZerodhaSessionManager,
}


def get_session_manager(config: SessionConfig = None) -> BaseSessionManager:
    config = config if config is not None else SessionConfig()
    try:
        manager_cls = _BROKERS[config.broker]
    except KeyError:
        raise ValueError(f"Unsupported broker '{config.broker}'. Supported brokers: {list(_BROKERS)}")
    return manager_cls(config)
