import argparse
import os
from typing import Optional

import opengradient as og
from x402v2.mechanisms.evm.constants import PERMIT2_ADDRESS
from web3 import Web3

BASE_OPG_ADDRESS = "0x240b09731D96979f50B2C649C9CE10FcF9C7987F"
BASE_SEPOLIA_RPC = "https://sepolia.base.org"
MAX_UINT256 = (1 << 256) - 1

ERC20_ABI = [
    {
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]


def _get_base_sepolia_web3() -> Web3:
    return Web3(Web3.HTTPProvider(BASE_SEPOLIA_RPC))


def get_permit2_allowance(client_address: str) -> int:
    w3 = _get_base_sepolia_web3()
    token = w3.eth.contract(address=Web3.to_checksum_address(BASE_OPG_ADDRESS), abi=ERC20_ABI)
    return token.functions.allowance(
        Web3.to_checksum_address(client_address),
        Web3.to_checksum_address(PERMIT2_ADDRESS),
    ).call()


def check_permit2_approval(client_address: str) -> None:
    """Raise an error if Permit2 approval is missing for base-testnet."""
    allowance = get_permit2_allowance(client_address)
    print(f"Current OPG Permit2 allowance: {allowance}")

    if allowance == 0:
        raise RuntimeError(
            f"ERROR: No Permit2 approval found for address {client_address}. "
            f"Approve Permit2 ({PERMIT2_ADDRESS}) to spend OPG ({BASE_OPG_ADDRESS}) "
            "on Base Sepolia before using x402 payments."
        )


def grant_permit2_approval(
    private_key: str,
    amount: int = MAX_UINT256,
    gas_multiplier: float = 1.2,
    nonce: Optional[int] = None,
) -> str:
    """Send ERC-20 approve(spender=Permit2, amount=amount) for OPG on Base Sepolia."""
    w3 = _get_base_sepolia_web3()

    account = w3.eth.account.from_key(private_key)
    token = w3.eth.contract(address=Web3.to_checksum_address(BASE_OPG_ADDRESS), abi=ERC20_ABI)

    tx_nonce = nonce
    if tx_nonce is None:
        tx_nonce = w3.eth.get_transaction_count(account.address, "pending")

    approve_fn = token.functions.approve(Web3.to_checksum_address(PERMIT2_ADDRESS), amount)
    estimated_gas = approve_fn.estimate_gas({"from": account.address})

    tx = approve_fn.build_transaction(
        {
            "from": account.address,
            "nonce": tx_nonce,
            "gas": int(estimated_gas * gas_multiplier),
            "gasPrice": w3.eth.gas_price,
            "chainId": w3.eth.chain_id,
        }
    )

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt.status != 1:
        raise RuntimeError(f"Permit2 approval transaction failed: {tx_hash.hex()}")

    return tx_hash.hex()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Grant Permit2 approval to spend OPG on Base Sepolia.")
    parser.add_argument(
        "--amount",
        type=int,
        default=MAX_UINT256,
        help="Approval amount in base units (default: max uint256).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    private_key = os.environ.get("OG_PRIVATE_KEY")
    if not private_key:
        raise RuntimeError("OG_PRIVATE_KEY is not set.")

    client = og.Client(private_key=private_key)
    wallet_address = client.wallet_address

    before = get_permit2_allowance(wallet_address)
    print(f"Wallet: {wallet_address}")
    print(f"Permit2: {PERMIT2_ADDRESS}")
    print(f"OPG Token: {BASE_OPG_ADDRESS}")
    print(f"Allowance before: {before}")

    tx_hash = grant_permit2_approval(private_key=private_key, amount=args.amount)
    after = get_permit2_allowance(wallet_address)

    print(f"Approval transaction hash: {tx_hash}")
    print(f"Allowance after: {after}")


if __name__ == "__main__":
    main()
