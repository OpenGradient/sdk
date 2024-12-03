unittest:
	python -m unittest discover

infer:
	pip install -e .
	python -m opengradient.cli infer -m QmbUqS93oc4JTLMHwpVxsE39mhNxy6hpf6Py3r9oANr8aZ --input '{"num_input1":[1.0, 2.0, 3.0], "num_input2":10, "str_input1":["hello", "ONNX"], "str_input2":" world"}'

llm:
	pip install -e .
	python -m opengradient.cli completion --model meta-llama/Meta-Llama-3-8B-Instruct --prompt "hello doctor" --max-tokens 50

chat:
	pip install -e .
	python -m opengradient.cli chat --model meta-llama/Meta-Llama-3-8B-Instruct --messages '[{"role":"user","content":"hello"}]' --max-tokens 50

tool:
	pip install -e .
	python -m opengradient.cli chat --model NousResearch/Hermes-3-Llama-3.1-70B --messages '[{"role": "system", "content": "You are a AI assistant that helps the user with tasks. Use tools if necessary."}, {"role": "user", "content": "Hi! How are you doing today?"}, {"role": "assistant", "content": "I'\''m doing well! How can I help you?", "name": "HAL"}, {"role": "user", "content": "Can you tell me what the temperate will be in Dallas, in fahrenheit?"}]' --tools '[{"type": "function", "function": {"name": "get_current_weather", "description": "Get the current weather in a given location", "parameters": {"type": "object", "properties": {"city": {"type": "string", "description": "The city to find the weather for, e.g. '\''San Francisco'\''"}, "state": {"type": "string", "description": "the two-letter abbreviation for the state that the city is in, e.g. '\''CA'\'' which would mean '\''California'\''"}, "unit": {"type": "string", "description": "The unit to fetch the temperature in", "enum": ["celsius", "fahrenheit"]}}, "required": ["city", "state", "unit"]}}}]' --max-tokens 200
