import os
import opengradient as og

og_client = og.new_client(email=None, password=None, private_key=os.environ.get("OG_PRIVATE_KEY"))

og_client.create_model(
    model_name="example-model",
    model_desc="An example machine learning model for demonstration purposes",
    version="1.0.0"
)
