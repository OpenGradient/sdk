infer:
	pip install -e .
	python -m opengradient.cli infer -m QmbUqS93oc4JTLMHwpVxsE39mhNxy6hpf6Py3r9oANr8aZ --input '{"num_input1":[1.0, 2.0, 3.0], "num_input2":10, "str_input1":["hello", "ONNX"], "str_input2":" world"}'

llm:
	pip install -e .
	python -m opengradient.cli llm --model meta-llama/Meta-Llama-3-8B-Instruct --prompt "hello doctor" --max-tokens 50
