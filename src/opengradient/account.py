import hashlib
import os
import secrets
from collections import namedtuple

from eth_account import Account

EthAccount = namedtuple("EthAccount", ["address", "private_key"])


def generate_eth_account() -> EthAccount:
    user_seed = _get_user_random_seed()
    private_key = _generate_secure_private_key(user_seed)

    # derive account
    account = Account.from_key(private_key)

    # get the public key (address)
    public_key = account.address

    return EthAccount(address=public_key, private_key=private_key)


def _get_user_random_seed():
    print("Please type a random string of characters (the longer and more random, the better):")
    print("> ", end="")  # Add a '>' prompt on a new line
    return input().encode()


def _generate_secure_private_key(user_input):
    # Combine multiple sources of entropy
    system_random = secrets.token_bytes(32)
    os_urandom = os.urandom(32)
    timestamp = str(secrets.randbits(256)).encode()

    # Add user input to the entropy sources
    combined = system_random + os_urandom + timestamp + user_input

    # Hash the combined entropy
    return hashlib.sha256(combined).hexdigest()
