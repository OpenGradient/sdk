sanity:
	pip install -e .
	python -m opengradient.cli infer QmbUqS93oc4JTLMHwpVxsE39mhNxy6hpf6Py3r9oANr8aZ VANILLA '{"num_input1":[1.0, 2.0, 3.0], "num_input2":10, "str_input1":["hello", "ONNX"], "str_input2":" world"}'