from dvarpal.brokers.base import BaseSessionManager
from dvarpal.brokers.upstox import UpstoxSessionManager
from dvarpal.brokers.zerodha import ZerodhaSessionManager
from dvarpal.config import SessionConfig

_BROKERS = {
    'upstox': UpstoxSessionManager,
    'zerodha': ZerodhaSessionManager,
}


def get_session_manager(config: SessionConfig = None) -> BaseSessionManager:
    """Returns the SessionManager for a single broker. config.broker must
    name one broker (not 'all') -- SessionConfig() already rejects 'all'."""
    config = config if config is not None else SessionConfig()
    return _BROKERS[config.broker](config)


def get_session_managers() -> dict:
    """Returns {broker_name: SessionManager} for every broker selected by
    the top-level `broker` field in dvarpal.yaml -- both, when it is 'all'."""
    return {broker: get_session_manager(SessionConfig(broker)) for broker in SessionConfig.selected_brokers()}
