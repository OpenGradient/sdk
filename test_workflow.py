from web3 import AsyncWeb3
from web3.providers import WebSocketProvider
from eth_account import Account
import json
from pathlib import Path
import asyncio
import time

# Constants
RPC_URL = "ws://18.218.115.248:8546"
HISTORICAL_CONTRACT_ADDRESS = "0x00000000000000000000000000000000000000F5"
MODEL_CID = "QmRhcpDXfYCKsimTmJYrAVM4Bbvck59Zb2onj3MHv9Kw5N"

async def deploy_and_run_contract(w3, private_key):
    account = Account.from_key(private_key)
    
    # Load pre-compiled contract artifacts from build directory
    build_dir = Path.cwd() / 'build'
    abi_path = Path(__file__).parent / 'src' / 'opengradient' / 'abi' / 'ModelExecutorHistorical.abi'
    with open(abi_path, 'r') as f:
        abi = json.load(f)
    with open(build_dir / 'ModelExecutorHistorical.bin', 'r') as f:
        bytecode = f.read().strip()
    
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Create historical input query matching the HistoricalInputQuery struct
    historical_input = (
        "ETH/USD",                    # currency_pair (string)
        10,                          # total_candles (uint32)
        30,                          # candle_duration_in_mins (uint32)
        0,                           # order (uint8 - CandleOrder.Ascending)
        [0, 1, 3, 2]                 # candle_types array (uint8[] - [Open, High, Close, Low])
    )
    
    # Deploy contract
    print("\nDeploying contract...")
    nonce = await w3.eth.get_transaction_count(account.address, 'pending')
    
    transaction = await Contract.constructor(
        MODEL_CID,
        historical_input,
        HISTORICAL_CONTRACT_ADDRESS
    ).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 15000000,
        'gasPrice': await w3.eth.gas_price,
        'chainId': await w3.eth.chain_id
    })
    
    signed_txn = account.sign_transaction(transaction)
    tx_hash = await w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    tx_receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)
    
    contract_address = tx_receipt.contractAddress
    print(f"Contract deployed at: {contract_address}")
    
    # Create contract instance for interaction
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    # Call run() function
    print("\nCalling run()...")
    nonce = await w3.eth.get_transaction_count(account.address, 'pending')
    
    run_tx = await contract.functions.run().build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 30000000,
        'gasPrice': await w3.eth.gas_price,
        'chainId': await w3.eth.chain_id
    })
    
    signed_run_tx = account.sign_transaction(run_tx)
    run_tx_hash = await w3.eth.send_raw_transaction(signed_run_tx.raw_transaction)
    run_receipt = await w3.eth.wait_for_transaction_receipt(run_tx_hash)
    
    if run_receipt.status == 0:
        raise Exception(f"Run transaction failed: {run_receipt}")
    
    print(f"Run transaction completed: {run_tx_hash.hex()}")
    
    # Wait longer for result and add retries
    max_retries = 5
    for i in range(max_retries):
        try:
            await asyncio.sleep(5)  # Wait 5 seconds between attempts
            print(f"\nAttempt {i+1} to get inference result...")
            result = await contract.functions.getInferenceResult().call()
            print(f"Result: {result}")
            return contract_address
        except Exception as e:
            if i == max_retries - 1:
                print(f"Failed to get result after {max_retries} attempts: {str(e)}")
                raise
            print(f"Attempt {i+1} failed, retrying...")
            continue

async def main():
    provider = WebSocketProvider(RPC_URL)
    w3 = AsyncWeb3(provider)
    
    try:
        await provider.connect()
        private_key = "1404c83e29d18180d33dac46848939a38ed9fc3c0c869f7623f0eb3a05504055"
        
        contract_address = await deploy_and_run_contract(w3, private_key)
        
        # Save contract address
        with open('contract_address.txt', 'w') as f:
            f.write(contract_address)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        await provider.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 