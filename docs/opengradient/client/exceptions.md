---
outline: [2,3]
---

  

# Package opengradient.client.exceptions

Exception types for OpenGradient SDK errors.

## Classes
    

###  AuthenticationError

```python
class AuthenticationError(message='Authentication failed', **kwargs)
```

  

  
Raised when there's an authentication error
  

      
    

###  FileNotFoundError

```python
class FileNotFoundError(file_path)
```

  

  
Raised when a file is not found
  

      
    

###  InferenceError

```python
class InferenceError(message, model_cid=None, **kwargs)
```

  

  
Raised when there's an error during inference
  

      
    

###  InsufficientCreditsError

```python
class InsufficientCreditsError(message='Insufficient credits', required_credits=None, available_credits=None, **kwargs)
```

  

  
Raised when the user has insufficient credits for the operation
  

      
    

###  InvalidInputError

```python
class InvalidInputError(message, invalid_fields=None, **kwargs)
```

  

  
Raised when invalid input is provided
  

      
    

###  NetworkError

```python
class NetworkError(message, status_code=None, response=None)
```

  

  
Raised when a network error occurs
  

      
    

###  OpenGradientError

```python
class OpenGradientError(message, status_code=None, response=None)
```

  

  
Base exception for OpenGradient SDK
  

#### Subclasses
  * `AuthenticationError`
  * `FileNotFoundError`
  * `InferenceError`
  * `InsufficientCreditsError`
  * `InvalidInputError`
  * `NetworkError`
  * `RateLimitError`
  * `ResultRetrievalError`
  * `ServerError`
  * `TimeoutError`
  * `UnsupportedModelError`
  * `UploadError`
      
    

###  RateLimitError

```python
class RateLimitError(message='Rate limit exceeded', retry_after=None, **kwargs)
```

  

  
Raised when API rate limit is exceeded
  

      
    

###  ResultRetrievalError

```python
class ResultRetrievalError(message, inference_cid=None, **kwargs)
```

  

  
Raised when there's an error retrieving results
  

      
    

###  ServerError

```python
class ServerError(message, status_code=None, response=None)
```

  

  
Raised when a server error occurs
  

      
    

###  TimeoutError

```python
class TimeoutError(message='Request timed out', timeout=None, **kwargs)
```

  

  
Raised when a request times out
  

      
    

###  UnsupportedModelError

```python
class UnsupportedModelError(model_type)
```

  

  
Raised when an unsupported model type is used
  

      
    

###  UploadError

```python
class UploadError(message, file_path=None, **kwargs)
```

  

  
Raised when there's an error during file upload