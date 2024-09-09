import pytest
from src.exceptions import (
    OpenGradientError, FileNotFoundError, UploadError, InferenceError,
    ResultRetrievalError, AuthenticationError, RateLimitError, InvalidInputError,
    ServerError, TimeoutError, NetworkError, UnsupportedModelError, InsufficientCreditsError
)

def test_open_gradient_error():
    error = OpenGradientError("Test error", status_code=400)
    assert str(error) == "Test error (Status code: 400)"

def test_file_not_found_error():
    error = FileNotFoundError("test_file.onnx")
    assert str(error) == "File not found: test_file.onnx"

def test_upload_error():
    error = UploadError("Upload failed", file_path="test_file.onnx")
    assert str(error) == "Upload failed (Status code: None)"
    assert error.file_path == "test_file.onnx"

def test_insufficient_credits_error():
    error = InsufficientCreditsError(required_credits=100, available_credits=50)
    assert str(error) == "Insufficient credits (Status code: None) (Required: 100, Available: 50)"

# Add more tests for other exception classes