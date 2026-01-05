# Variables for file names
MESSAGES_FILE := messages.json
TOOLS_FILE := tools.json
LLAMA_3B_MODEL := meta-llama/Meta-Llama-3-8B-Instruct
LLAMA_70B_MODEL := meta-llama/Llama-3.1-70B-Instruct
QWEN_2_5_72B_INSTRUCT := Qwen/Qwen2.5-72B-Instruct
DOBBY_UNHINGED_3_1_8B := SentientAGI/Dobby-Mini-Unhinged-Llama-3.1-8B
DOBBY_LEASHED_3_1_8B := SentientAGI/Dobby-Mini-Leashed-Llama-3.1-8B

infer:
	pip install -e .
	python -m opengradient.cli infer -m "hJD2Ja3akZFt1A2LT-D_1oxOCz_OtuGYw4V9eE1m39M" --input '{"open_high_low_close": [[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4]]}'

completion:
	pip install -e .
	python -m opengradient.cli completion --model $(DOBBY_UNHINGED_3_1_8B) \
		--prompt "hello doctor?!??!! $(shell echo $$RANDOM)" \
		--max-tokens 50

chat:
	pip install -e .
	python -m opengradient.cli chat --model $(DOBBY_LEASHED_3_1_8B) \
		--messages '[{"role":"user","content":"hellooooo $(shell echo $$RANDOM)"}]' \
		--max-tokens 50

tool:
	pip install -e .
	python -m opengradient.cli chat --model $(LLAMA_70B_MODEL) --messages '[{"role": "system", "content": "You are a AI assistant that helps the user with tasks. Use tools if necessary."}, {"role": "user", "content": "Hi! How are you doing today?"}, {"role": "assistant", "content": "I'\''m doing well! How can I help you?", "name": "HAL"}, {"role": "user", "content": "Can you tell me what the temperate will be in Dallas, in fahrenheit?"}]' --tools '[{"type": "function", "function": {"name": "get_current_weather", "description": "Get the current weather in a given location", "parameters": {"type": "object", "properties": {"city": {"type": "string", "description": "The city to find the weather for, e.g. '\''San Francisco'\''"}, "state": {"type": "string", "description": "the two-letter abbreviation for the state that the city is in, e.g. '\''CA'\'' which would mean '\''California'\''"}, "unit": {"type": "string", "description": "The unit to fetch the temperature in", "enum": ["celsius", "fahrenheit"]}}, "required": ["city", "state", "unit"]}}}]' --max-tokens 200

# Create the messages JSON file
messages:
	@echo '[{"role":"system","content":"You are a AI assistant that helps the user with tasks. Use tools if necessary."},{"role":"user","content":"Hi! How are you doing today?"},{"role":"assistant","content":"I'\''m doing well! How can I help you?","name":"HAL"},{"role":"user","content":"Can you tell me what the temperate will be in Dallas, in fahrenheit?"}]' > $(MESSAGES_FILE)

# Create the tools JSON file
tools:
	@echo '[{"type":"function","function":{"name":"get_current_weather","description":"Get the current weather in a given location","parameters":{"type":"object","properties":{"city":{"type":"string","description":"The city to find the weather for, e.g. '\''San Francisco'\''"},"state":{"type":"string","description":"the two-letter abbreviation for the state that the city is in, e.g. '\''CA'\'' which would mean '\''California'\''"},"unit":{"type":"string","description":"The unit to fetch the temperature in","enum":["celsius","fahrenheit"]}},"required":["city","state","unit"]}}}]' > $(TOOLS_FILE)

generate: messages tools

chat_files: generate
	pip install -e .
	python -m opengradient.cli chat \
		--model $(QWEN_2_5_72B_INSTRUCT) \
		--messages-file $(MESSAGES_FILE) \
		--tools-file $(TOOLS_FILE) \
		--max-tokens 200

tee_completion:
	pip install -e .
	python -m opengradient.cli completion --model $(LLAMA_70B_MODEL) --mode TEE --prompt "hello doctor" --max-tokens 150

tee_chat:
	pip install -e .
	python -m opengradient.cli chat --model $(LLAMA_70B_MODEL) --mode TEE --messages '[{"role":"user","content":"hello"}]' --max-tokens 150

route_chat:
	pip install -e .
	python -m opengradient.cli chat --model gpt-4.1-2025-04-14 --mode TEE --messages '[{"role":"user", "content":"Name me three random numbers"}]' --max-tokens 50

batch_route_chat:
	pip install -e .
	@for i in $$(seq 1 50); do \
		python -m opengradient.cli chat --model gpt-4.1-2025-04-14 --messages '[{"role":"user", "content":"Who are you?"}]' --max-tokens 50 & \
	done; \
	wait

docs:
	pdoc opengradient -o docs --template-dir ./templates --force

build:
	python -m build 

publish:
	@echo "📋 Current version:" $$(grep 'version = ' pyproject.toml | cut -d'"' -f2)
	@echo "🧹 Cleaning dist directory..."
	rm -rf dist/*
	@echo "🏗️  Building distributions..."
	python -m build
	@echo "📦 Generated files in dist/:"
	ls -l dist/
	@echo "🚀 Uploading to PyPI..."
	twine upload dist/*
	@echo "✨ Done! Published to PyPI"

check:
	ruff format .
	mypy src
	mypy examples

test: integrationtest utils_test infer completion chat tool tee_completion tee_chat

integrationtest:
	python integrationtest/agent/test_agent.py
	python integrationtest/workflow_models/test_workflow_models.py

utils_test:
	pytest tests/utils_test.py -v

.PHONY: docs ruff integrationtest
