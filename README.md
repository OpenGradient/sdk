# OpenGradient Python SDK

Python SDK for OpenGradient inference services.

## Installation
```
pip install opengradient
```

## Quick Start
```
import opengradient
og = opengradient.Client(api_key="your_api_key")
```

### Upload a Model
```
model_cid = og.upload("path/to/model.onnx")
```

### Run Inference
```
inference_cid = og.infer(model_cid, model_inputs, inference_type="vanilla")
```
