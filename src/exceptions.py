class OpenGradientError(Exception):
    """Base exception for OpenGradient SDK"""
    def __init__(self, message, status_code=None, response=None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (Status code: {self.status_code})"

class FileNotFoundError(OpenGradientError):
    """Raised when a file is not found"""
    def __init__(self, file_path):
        super().__init__(f"File not found: {file_path}")
        self.file_path = file_path

class UploadError(OpenGradientError):
    """Raised when there's an error during file upload"""
    def __init__(self, message, file_path=None, **kwargs):
        super().__init__(message, **kwargs)
        self.file_path = file_path

class InferenceError(OpenGradientError):
    """Raised when there's an error during inference"""
    def __init__(self, message, model_cid=None, **kwargs):
        super().__init__(message, **kwargs)
        self.model_cid = model_cid

class ResultRetrievalError(OpenGradientError):
    """Raised when there's an error retrieving results"""
    def __init__(self, message, inference_cid=None, **kwargs):
        super().__init__(message, **kwargs)
        self.inference_cid = inference_cid

class AuthenticationError(OpenGradientError):
    """Raised when there's an authentication error"""
    def __init__(self, message="Authentication failed", **kwargs):
        super().__init__(message, **kwargs)

class RateLimitError(OpenGradientError):
    """Raised when API rate limit is exceeded"""
    def __init__(self, message="Rate limit exceeded", retry_after=None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after

class InvalidInputError(OpenGradientError):
    """Raised when invalid input is provided"""
    def __init__(self, message, invalid_fields=None, **kwargs):
        super().__init__(message, **kwargs)
        self.invalid_fields = invalid_fields or []

class ServerError(OpenGradientError):
    """Raised when a server error occurs"""
    pass

class TimeoutError(OpenGradientError):
    """Raised when a request times out"""
    def __init__(self, message="Request timed out", timeout=None, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout = timeout

class NetworkError(OpenGradientError):
    """Raised when a network error occurs"""
    pass

class UnsupportedModelError(OpenGradientError):
    """Raised when an unsupported model type is used"""
    def __init__(self, model_type):
        super().__init__(f"Unsupported model type: {model_type}")
        self.model_type = model_type

class InsufficientCreditsError(OpenGradientError):
    """Raised when the user has insufficient credits for the operation"""
    def __init__(self, message="Insufficient credits", required_credits=None, available_credits=None, **kwargs):
        super().__init__(message, **kwargs)
        self.required_credits = required_credits
        self.available_credits = available_credits

    def __str__(self):
        base_str = super().__str__()
        if self.required_credits is not None and self.available_credits is not None:
            return f"{base_str} (Required: {self.required_credits}, Available: {self.available_credits})"
        return base_str
