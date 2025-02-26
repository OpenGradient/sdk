import os
import opengradient as og

og_client = og.new_client(email=None, password=None, private_key=os.environ.get("OG_PRIVATE_KEY"))

model_output = og_client.read_workflow_result(
    # This is the workflow contract address that you previously deployed
    contract_address='0x96FC3dB570ddb133dBfe3ccd5EafB23a6c61e222'
)

print(f"Model prediction: {model_output.numbers}")