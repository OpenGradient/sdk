import os

import opengradient as og

og_client = og.Client(
    private_key=os.environ.get("OG_PRIVATE_KEY"),
    email=os.environ.get("OG_MODEL_HUB_EMAIL"),
    password=os.environ.get("OG_MODEL_HUB_PASSWORD"),
)

og_client.model_hub.create_model(
    model_name="example-model", model_desc="An example machine learning model for demonstration purposes", version="1.0.0"
)
