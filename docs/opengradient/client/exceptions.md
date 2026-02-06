---
outline: [2,3]
---

  

# Package opengradient.client.exceptions

Exception types for OpenGradient SDK errors.

## Classes
    

### AuthenticationError

```python
class AuthenticationError
```

  

  
Raised when there's an authentication error
  

#### Constructor

```python
def __init__(message='Authentication failed', **kwargs)
```
      
    

### FileNotFoundError

```python
class FileNotFoundError
```

  

  
Raised when a file is not found
  

#### Constructor

```python
def __init__(file_path)
```
      
    

### InferenceError

```python
class InferenceError
```

  

  
Raised when there's an error during inference
  

#### Constructor

```python
def __init__(message, model_cid=None, **kwargs)
```
      
    

### InsufficientCreditsError

```python
class InsufficientCreditsError
```

  

  
Raised when the user has insufficient credits for the operation
  

#### Constructor

```python
def __init__(message='Insufficient credits', required_credits=None, available_credits=None, **kwargs)
```
      
    

### InvalidInputError

```python
class InvalidInputError
```

  

  
Raised when invalid input is provided
  

#### Constructor

```python
def __init__(message, invalid_fields=None, **kwargs)
```
      
    

### NetworkError

```python
class NetworkError
```

  

  
Raised when a network error occurs
  

#### Constructor

```python
def __init__(message, status_code=None, response=None)
```
      
    

### OpenGradientError

```python
class OpenGradientError
```

  

  
Base exception for OpenGradient SDK
  

#### Constructor

```python
def __init__(message, status_code=None, response=None)
```

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
      
    

### RateLimitError

```python
class RateLimitError
```

  

  
Raised when API rate limit is exceeded
  

#### Constructor

```python
def __init__(message='Rate limit exceeded', retry_after=None, **kwargs)
```
      
    

### ResultRetrievalError

```python
class ResultRetrievalError
```

  

  
Raised when there's an error retrieving results
  

#### Constructor

```python
def __init__(message, inference_cid=None, **kwargs)
```
      
    

### ServerError

```python
class ServerError
```

  

  
Raised when a server error occurs
  

#### Constructor

```python
def __init__(message, status_code=None, response=None)
```
      
    

### TimeoutError

```python
class TimeoutError
```

  

  
Raised when a request times out
  

#### Constructor

```python
def __init__(message='Request timed out', timeout=None, **kwargs)
```
      
    

### UnsupportedModelError

```python
class UnsupportedModelError
```

  

  
Raised when an unsupported model type is used
  

#### Constructor

```python
def __init__(model_type)
```
      
    

### UploadError

```python
class UploadError
```

  

  
Raised when there's an error during file upload
  

#### Constructor

```python
def __init__(message, file_path=None, **kwargs)
```