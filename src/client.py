import requests
import os
import time
from .exceptions import FileNotFoundError, UploadError, OpenGradientError, InferenceError, ResultRetrievalError

class Client:
    def __init__(self, api_key, base_url="http://localhost:5002", max_retries=3, retry_delay=1):
        self.api_key = api_key
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _make_request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers

        for attempt in range(self.max_retries):
            try:
                response = requests.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise OpenGradientError(f"Request failed after {self.max_retries} attempts: {str(e)}")
                time.sleep(self.retry_delay)

    def upload(self, model_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"File not found: {model_path}")

        try:
            with open(model_path, "rb") as file:
                files = {"file": (os.path.basename(model_path), file)}
                return self._make_request("POST", "upload", params={"stream": "true"}, files=files)
        except OpenGradientError as e:
            raise UploadError(f"Upload failed: {str(e)}")

    # def infer(self, model_cid, model_inputs, inference_type="vanilla"):
    #     try:
    #         data = {
    #             "model_cid": model_cid,
    #             "model_inputs": model_inputs,
    #             "inference_type": inference_type
    #         }
    #         return self._make_request("POST", "infer", json=data)
    #     except OpenGradientError as e:
    #         raise InferenceError(f"Inference failed: {str(e)}")

    # def get_results(self, inference_cid):
    #     response = self._make_request("GET", f"results/{inference_cid}")
    #     result = response.json()
    #     if result["status"] == "completed":
    #         return result["data"], result["proof"]
    #     elif result["status"] == "failed":
    #         raise InferenceError(f"Inference failed: {result.get('error', 'Unknown error')}")
    #     else:
    #         return None, None  # Indicating that the result is not ready yet
