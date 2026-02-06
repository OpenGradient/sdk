---
outline: [2,3]
---

  

# Package opengradient.client.exceptions

## Classes
    

###  AuthenticationError

<code>class <b>AuthenticationError</b>(message='Authentication failed', **kwargs)</code>

  

  
Raised when there's an authentication error
  

      
    

###  FileNotFoundError

<code>class <b>FileNotFoundError</b>(file_path)</code>

  

  
Raised when a file is not found
  

      
    

###  InferenceError

<code>class <b>InferenceError</b>(message, model_cid=None, **kwargs)</code>

  

  
Raised when there's an error during inference
  

      
    

###  InsufficientCreditsError

<code>class <b>InsufficientCreditsError</b>(message='Insufficient credits', required_credits=None, available_credits=None, **kwargs)</code>

  

  
Raised when the user has insufficient credits for the operation
  

      
    

###  InvalidInputError

<code>class <b>InvalidInputError</b>(message, invalid_fields=None, **kwargs)</code>

  

  
Raised when invalid input is provided
  

      
    

###  NetworkError

<code>class <b>NetworkError</b>(message, status_code=None, response=None)</code>

  

  
Raised when a network error occurs
  

      
    

###  OpenGradientError

<code>class <b>OpenGradientError</b>(message, status_code=None, response=None)</code>

  

  
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

<code>class <b>RateLimitError</b>(message='Rate limit exceeded', retry_after=None, **kwargs)</code>

  

  
Raised when API rate limit is exceeded
  

      
    

###  ResultRetrievalError

<code>class <b>ResultRetrievalError</b>(message, inference_cid=None, **kwargs)</code>

  

  
Raised when there's an error retrieving results
  

      
    

###  ServerError

<code>class <b>ServerError</b>(message, status_code=None, response=None)</code>

  

  
Raised when a server error occurs
  

      
    

###  TimeoutError

<code>class <b>TimeoutError</b>(message='Request timed out', timeout=None, **kwargs)</code>

  

  
Raised when a request times out
  

      
    

###  UnsupportedModelError

<code>class <b>UnsupportedModelError</b>(model_type)</code>

  

  
Raised when an unsupported model type is used
  

      
    

###  UploadError

<code>class <b>UploadError</b>(message, file_path=None, **kwargs)</code>

  

  
Raised when there's an error during file upload