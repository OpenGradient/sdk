import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.client import Client
from src.exceptions import FileNotFoundError, UploadError, InferenceError, ResultRetrievalError, AuthenticationError, RateLimitError, InvalidInputError

import pytest
from unittest.mock import patch, Mock, mock_open
import requests
import time

@pytest.fixture
def client():
    return Client(api_key="test_api_key")

def test_upload_success(client):
    with patch('src.client.requests.request') as mock_request, \
         patch('src.client.os.path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data=b'fake_file_content')):
        mock_response = Mock()
        mock_response.json.return_value = {"model_cid": "test_cid"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = client.upload("test_model.onnx")
        assert result == {"model_cid": "test_cid"}

def test_upload_file_not_found(client):
    with pytest.raises(FileNotFoundError):
        client.upload("non_existent_file.onnx")

def test_upload_authentication_error(client):
    with patch('src.client.requests.request') as mock_request, \
         patch('src.client.os.path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data=b'fake_file_content')):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=Mock(status_code=401))
        mock_request.return_value = mock_response

        with pytest.raises(UploadError):
            client.upload("test_model.onnx")

# def test_infer_success(client):
#     with patch('src.client.requests.request') as mock_request:
#         mock_response = Mock()
#         mock_response.json.return_value = {"inference_cid": "test_inference_cid"}
#         mock_response.raise_for_status.return_value = None
#         mock_request.return_value = mock_response

#         result = client.infer("test_model_cid", {"input": [1, 2, 3]})
#         assert result == {"inference_cid": "test_inference_cid"}

# def test_get_results_not_ready(client):
#     with patch('src.client.requests.request') as mock_request:
#         mock_response = Mock()
#         mock_response.json.return_value = {"status": "processing"}
#         mock_response.raise_for_status.return_value = None
#         mock_request.return_value = mock_response

#         result, proof = client.get_results("test_inference_cid")
#         assert result is None
#         assert proof is None

# def test_get_results_success(client):
#     with patch('src.client.requests.request') as mock_request:
#         mock_response = Mock()
#         mock_response.json.return_value = {"status": "completed", "data": "test_result", "proof": "test_proof"}
#         mock_response.raise_for_status.return_value = None
#         mock_request.return_value = mock_response

#         result, proof = client.get_results("test_inference_cid")
#         assert result == "test_result"
#         assert proof == "test_proof"

# def test_get_results_failed(client):
#     with patch('src.client.requests.request') as mock_request:
#         mock_response = Mock()
#         mock_response.json.return_value = {"status": "failed", "error": "Test error"}
#         mock_response.raise_for_status.return_value = None
#         mock_request.return_value = mock_response

#         with pytest.raises(InferenceError, match="Inference failed: Test error"):
#             client.get_results("test_inference_cid")

def test_infer_success(client):
    with patch('src.client.requests.request') as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {"inference_cid": "test_inference_cid"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = client.infer("test_model_cid", {"input": [1, 2, 3]})
        assert result == {"inference_cid": "test_inference_cid"}

        mock_request.assert_called_once_with(
            "POST",
            "http://localhost:5002/infer",
            json={
                "model_cid": "test_model_cid",
                "model_inputs": {"input": [1, 2, 3]},
                "contract_address": "0x1234567890123456789012345678901234567890"
            },
            headers={"Authorization": "Bearer test_api_key"}
        )

def test_infer_invalid_input(client):
    with pytest.raises(InvalidInputError):
        client.infer("test_model_cid", {"invalid_input": "value"})