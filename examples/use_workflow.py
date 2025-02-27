import os
import opengradient as og

og_client = og.new_client(email=None, password=None, private_key=os.environ.get("OG_PRIVATE_KEY"))

model_output = og_client.read_workflow_result(
    # This is the workflow contract address that you previously deployed
    contract_address="0x58Dd93E1aE6B6f21b479b3B2913B055eFD2E74Ee"
)

print(f"Latest model prediction: {model_output.numbers}")

model_output_history = og_client.read_workflow_history(
    # This is the workflow contract address that you previously deployed
    contract_address="0x58Dd93E1aE6B6f21b479b3B2913B055eFD2E74Ee",
    num_results=5,
)

print(f"Model prediction history: {model_output_history}")
