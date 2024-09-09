import pytest
from src.client import Client
import os

@pytest.mark.integration
def test_upload_integration():
    client = Client(api_key="test_api_key", base_url="http://localhost:5002")
    
    # Create a temporary test file
    test_file_path = "test_model.onnx"
    with open(test_file_path, "wb") as f:
        f.write(b"fake model content")
    
    try:
        result = client.upload(test_file_path)
        assert "model_cid" in result
        print(f"Upload successful. Model CID: {result['model_cid']}")
    finally:
        # Clean up the test file
        os.remove(test_file_path)