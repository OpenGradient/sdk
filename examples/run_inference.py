import os
import opengradient as og

og_client = og.new_client(email=None, password=None, private_key=os.environ.get("OG_PRIVATE_KEY"))

inference_result = og_client.infer(
    model_cid="QmbUqS93oc4JTLMHwpVxsE39mhNxy6hpf6Py3r9oANr8aZ",
    model_input={"num_input1": [1.0, 2.0, 3.0], "num_input2": 10, "str_input1": ["hello", "ONNX"], "str_input2": " world"},
    inference_mode=og.InferenceMode.VANILLA,
)

print(f"Output: {inference_result.model_output}")
print(f"Tx hash: {inference_result.transaction_hash}")
