---
outline: [2,3]
---

  

# Package opengradient.client.model_hub

Model Hub for creating, versioning, and uploading ML models.

## Classes
    

###  ModelHub

<code>class <b>ModelHub</b>(hub_user: Optional[Dict] = None)</code>

  

  
Model Hub namespace.

Provides access to the OpenGradient Model Hub for creating, versioning,
and uploading ML models. Requires email/password authentication.
  

  

### Create model 

```python
def create_model(self, model_name: str, model_desc: str, version: str = '1.00') ‑> opengradient.types.ModelRepository
```

  

  
Create a new model with the given model_name and model_desc, and a specified version.
  

**Returns**

dict: The server response containing model details.

**Raises**

* **`CreateModelError`**: If the model creation fails.
  

  

### Create version 

```python
def create_version(self, model_name: str, notes: str = '', is_major: bool = False) ‑> dict
```

  

  
Create a new version for the specified model.
  

**Returns**

dict: The server response containing version details.

**Raises**

* **`Exception`**: If the version creation fails.
  

  

### List files 

```python
def list_files(self, model_name: str, version: str) ‑> List[Dict]
```

  

  
List files for a specific version of a model.
  

**Returns**

List[Dict]: A list of dictionaries containing file information.

**Raises**

* **`OpenGradientError`**: If the file listing fails.
  

  

### Upload 

```python
def upload(self, model_path: str, model_name: str, version: str) ‑> opengradient.types.FileUploadResult
```

  

  
Upload a model file to the server.
  

**Returns**

dict: The processed result.

**Raises**

* **`OpenGradientError`**: If the upload fails.