"""
Generates an access token for the broker(s) configured in
${HOME}/.dvarpal/dvarpal.yaml and prints the outcome.

Works regardless of whether `broker` in dvarpal.yaml is `upstox`, `zerodha`,
or `all` -- run as-is:

    python3 examples/generate_token.py
"""
import logging

from dvarpal import get_session_managers

logging.basicConfig(level=logging.INFO)

for broker_name, session_manager in get_session_managers().items():
    session_manager.generate_access_token()
    print(f"[{broker_name}] access_token: {session_manager.get_access_token()}")
    print(f"[{broker_name}] session valid: {session_manager.is_session_valid()}")
