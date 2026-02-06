import os

import opengradient as og

og_client = og.Client(
    private_key=os.environ.get("OG_PRIVATE_KEY"),
    email=os.environ.get("OG_MODEL_HUB_EMAIL"),
    password=os.environ.get("OG_MODEL_HUB_PASSWORD"),
)

model_repo = og_client.model_hub.create_model(model_name="Demo_Custom_Model_Adam", model_desc="My custom model for demoing Model Hub")
upload_result = og_client.model_hub.upload(model_name=model_repo.name, version=model_repo.initialVersion, model_path="./path/to/model.onnx")

print(f"Uploaded model, use following CID to access: {upload_result.modelCid}")
