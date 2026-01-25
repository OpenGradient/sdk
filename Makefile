# Variables for file names
MESSAGES_FILE := messages.json
TOOLS_FILE := tools.json
# TEE models (deprecated models: meta-llama, Qwen, Dobby)
GPT_4O := openai/gpt-4o
CLAUDE_3_5_HAIKU := anthropic/claude-3.5-haiku
CLAUDE_3_7_SONNET := anthropic/claude-3.7-sonnet
GPT_4_1_2025_04_14 := openai/gpt-4.1-2025-04-14
GEMINI_2_5_FLASH := google/gemini-2.5-flash

infer:
	pip install -e .
	python -m opengradient.cli infer -m "hJD2Ja3akZFt1A2LT-D_1oxOCz_OtuGYw4V9eE1m39M" --input '{"open_high_low_close": [[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4]]}'

completion:
	pip install -e .
	python -m opengradient.cli completion --model $(CLAUDE_3_5_HAIKU) \
		--prompt "hello doctor?!??!! $(shell echo $$RANDOM)" \
		--max-tokens 50

chat:
	pip install -e .
	python -m opengradient.cli chat --model $(CLAUDE_3_5_HAIKU) \
		--messages '[{"role":"user","content":"hellooooo $(shell echo $$RANDOM)"}]' \
		--max-tokens 50

tool:
	pip install -e .
	python -m opengradient.cli chat --model $(CLAUDE_3_7_SONNET) --messages '[{"role": "system", "content": "You are a AI assistant that helps the user with tasks. Use tools if necessary."}, {"role": "user", "content": "Hi! How are you doing today?"}, {"role": "assistant", "content": "I'\''m doing well! How can I help you?", "name": "HAL"}, {"role": "user", "content": "Can you tell me what the temperate will be in Dallas, in fahrenheit?"}]' --tools '[{"type": "function", "function": {"name": "get_current_weather", "description": "Get the current weather in a given location", "parameters": {"type": "object", "properties": {"city": {"type": "string", "description": "The city to find the weather for, e.g. '\''San Francisco'\''"}, "state": {"type": "string", "description": "the two-letter abbreviation for the state that the city is in, e.g. '\''CA'\'' which would mean '\''California'\''"}, "unit": {"type": "string", "description": "The unit to fetch the temperature in", "enum": ["celsius", "fahrenheit"]}}, "required": ["city", "state", "unit"]}}}]' --max-tokens 200

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
		--model $(CLAUDE_3_7_SONNET) \
		--messages-file $(MESSAGES_FILE) \
		--tools-file $(TOOLS_FILE) \
		--max-tokens 200

tee_completion:
	pip install -e .
	python -m opengradient.cli completion --model $(GPT_4_1_2025_04_14) --mode TEE --prompt "hello doctor" --max-tokens 150

tee_chat:
	pip install -e .
	python -m opengradient.cli chat --model $(GPT_4_1_2025_04_14) --mode TEE --messages '[{"role":"user","content":"hello"}]' --max-tokens 150

# Streaming tests
stream_chat:
	pip install -e .
	python -m opengradient.cli chat --model $(GPT_4O) --mode TEE \
		--messages '[{"role":"user","content":"Describe to me the plot of The Matrix"}]' \
		--max-tokens 250 \
		--stream

stream_chat_claude:
	pip install -e .
	python -m opengradient.cli chat --model $(CLAUDE_3_7_SONNET) --mode TEE \
		--messages '[{"role":"user","content":"Write a haiku about streaming"}]' \
		--max-tokens 100 \
		--stream

stream_chat_gemini:
	pip install -e .
	python -m opengradient.cli chat --model $(GEMINI_2_5_FLASH) --mode TEE \
		--messages '[{"role":"user","content":"Tell me a short joke"}]' \
		--max-tokens 50 \
		--stream

stream_tool:
	pip install -e .
	python -m opengradient.cli chat --model $(GPT_4O) --mode TEE \
		--messages '[{"role":"user","content":"What is the weather in Tokyo?"}]' \
		--tools '[{"type":"function","function":{"name":"get_weather","description":"Get weather for a location","parameters":{"type":"object","properties":{"location":{"type":"string"},"unit":{"type":"string","enum":["celsius","fahrenheit"]}},"required":["location"]}}}]' \
		--max-tokens 100 \
		--stream

# Test all streaming models
stream_all:
	@echo "🌊 Testing streaming with GPT-4o..."
	$(MAKE) stream_chat
	@echo "\n🌊 Testing streaming with Claude..."
	$(MAKE) stream_chat_claude
	@echo "\n🌊 Testing streaming with Gemini..."
	$(MAKE) stream_chat_gemini

route_chat:
	pip install -e .
	python -m opengradient.cli chat --model $(GPT_4_1_2025_04_14) --mode TEE --messages '[{"role":"user", "content":"Name me three random numbers"}]' --max-tokens 50

batch_route_chat:
	pip install -e .
	@for i in $$(seq 1 50); do \
		python -m opengradient.cli chat --model $(GPT_4_1_2025_04_14) --messages '[{"role":"user", "content":"Who are you?"}]' --max-tokens 50 & \
	done; \
	wait

# Batch streaming test (concurrent streams)
batch_stream:
	pip install -e .
	@echo "🌊 Testing concurrent streaming (10 requests)..."
	@for i in $$(seq 1 10); do \
		python -m opengradient.cli chat --model $(GPT_4O) --mode TEE \
			--messages '[{"role":"user","content":"Say hi and tell me a number: '$$i'"}]' \
			--max-tokens 30 \
			--stream & \
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

test: integrationtest utils_test infer completion chat tool tee_completion tee_chat stream_chat

integrationtest:
	python integrationtest/agent/test_agent.py
	python integrationtest/workflow_models/test_workflow_models.py

utils_test:
	pytest tests/utils_test.py -v

.PHONY: docs ruff integrationtest stream_chat stream_chat_claude stream_chat_gemini stream_tool stream_all batch_stream