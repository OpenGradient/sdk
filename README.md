# OpenGradient Python SDK

Python SDK for OpenGradient inference services.

## Installation

- bash
```
pip install opengradient
```

## Quick Start
```
import opengradient as og
client = og.Client(api_key="your_api_key")
```

### Upload a Model
```
model_cid = client.upload("path/to/model.onnx")
```

### Run Inference
```
inference_cid = client.infer(model_cid, model_inputs, inference_type="vanilla")
```