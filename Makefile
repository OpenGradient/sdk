# Variables for file names
MESSAGES_FILE := messages.json
TOOLS_FILE := tools.json

# TEE models - One from each provider
GPT_4O := openai/gpt-4o
CLAUDE_3_7_SONNET := anthropic/claude-3.7-sonnet
GEMINI_2_5_FLASH := google/gemini-2.5-flash
GROK_3_MINI_BETA := x-ai/grok-3-mini-beta

infer:
	pip install -e .
	python -m opengradient.cli infer -m "hJD2Ja3akZFt1A2LT-D_1oxOCz_OtuGYw4V9eE1m39M" --input '{"open_high_low_close": [[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4]]}'

completion:
	pip install -e .
	python -m opengradient.cli completion --model $(CLAUDE_3_7_SONNET) --mode TEE \
		--prompt "hello doctor?!??!! $(shell echo $$RANDOM)" \
		--max-tokens 50

# Create the messages JSON file
messages:
	@echo '[{"role":"system","content":"You are a AI assistant that helps the user with tasks. Use tools if necessary."},{"role":"user","content":"Hi! How are you doing today?"},{"role":"assistant","content":"I'\''m doing well! How can I help you?","name":"HAL"},{"role":"user","content":"Can you tell me what the temperate will be in Dallas, in fahrenheit?"}]' > $(MESSAGES_FILE)

# Create the tools JSON file
tools:
	@echo '[{"type":"function","function":{"name":"get_current_weather","description":"Get the current weather in a given location","parameters":{"type":"object","properties":{"city":{"type":"string","description":"The city to find the weather for, e.g. '\''San Francisco'\''"},"state":{"type":"string","description":"the two-letter abbreviation for the state that the city is in, e.g. '\''CA'\'' which would mean '\''California'\''"},"unit":{"type":"string","description":"The unit to fetch the temperature in","enum":["celsius","fahrenheit"]}},"required":["city","state","unit"]}}}]' > $(TOOLS_FILE)

generate: messages tools

# ============================================================================
# OpenAI (GPT-4o) Tests
# ============================================================================

openai_chat:
	pip install -e .
	python -m opengradient.cli chat --model $(GPT_4O) --mode TEE \
		--messages '[{"role":"user","content":"Tell me a fun fact about space"}]' \
		--max-tokens 150

openai_stream:
	pip install -e .
	python -m opengradient.cli chat --model $(GPT_4O) --mode TEE \
		--messages '[{"role":"user","content":"Describe the plot of The Matrix"}]' \
		--max-tokens 250 \
		--stream

openai_tool_stream:
	pip install -e .
	python -m opengradient.cli chat --model $(GPT_4O) --mode TEE \
		--messages '[{"role":"user","content":"What is the weather in Tokyo?"}]' \
		--tools '[{"type":"function","function":{"name":"get_weather","description":"Get weather for a location","parameters":{"type":"object","properties":{"location":{"type":"string"},"unit":{"type":"string","enum":["celsius","fahrenheit"]}},"required":["location"]}}}]' \
		--max-tokens 100 \
		--stream

# ============================================================================
# Anthropic (Claude) Tests
# ============================================================================

anthropic_chat:
	pip install -e .
	python -m opengradient.cli chat --model $(CLAUDE_3_7_SONNET) --mode TEE \
		--messages '[{"role":"user","content":"Write a short poem about AI"}]' \
		--max-tokens 150

anthropic_stream:
	pip install -e .
	python -m opengradient.cli chat --model $(CLAUDE_3_7_SONNET) --mode TEE \
		--messages '[{"role":"user","content":"Write a haiku about streaming"}]' \
		--max-tokens 100 \
		--stream

anthropic_tool_stream:
	pip install -e .
	python -m opengradient.cli chat --model $(CLAUDE_3_7_SONNET) --mode TEE \
		--messages '[{"role":"user","content":"Can you check the weather in Paris and tell me if I need an umbrella?"}]' \
		--tools '[{"type":"function","function":{"name":"get_weather","description":"Get current weather","parameters":{"type":"object","properties":{"location":{"type":"string"},"unit":{"type":"string","enum":["celsius","fahrenheit"]}},"required":["location"]}}}]' \
		--max-tokens 150 \
		--stream

# ============================================================================
# Google (Gemini) Tests
# ============================================================================

google_chat:
	pip install -e .
	python -m opengradient.cli chat --model $(GEMINI_2_5_FLASH) --mode TEE \
		--messages '[{"role":"user","content":"Explain quantum computing in simple terms"}]' \
		--max-tokens 200

google_stream:
	pip install -e .
	python -m opengradient.cli chat --model $(GEMINI_2_5_FLASH) --mode TEE \
		--messages '[{"role":"user","content":"Tell me a short story"}]' \
		--max-tokens 250 \
		--stream

google_tool_stream:
	pip install -e .
	python -m opengradient.cli chat --model $(GEMINI_2_5_FLASH) --mode TEE \
		--messages '[{"role":"user","content":"What'\''s the temperature in London right now?"}]' \
		--tools '[{"type":"function","function":{"name":"get_temperature","description":"Get current temperature","parameters":{"type":"object","properties":{"city":{"type":"string"},"unit":{"type":"string","enum":["celsius","fahrenheit"]}},"required":["city"]}}}]' \
		--max-tokens 100 \
		--stream

# ============================================================================
# xAI (Grok) Tests
# ============================================================================

xai_chat:
	pip install -e .
	python -m opengradient.cli chat --model $(GROK_3_MINI_BETA) --mode TEE \
		--messages '[{"role":"user","content":"What is the meaning of life?"}]' \
		--max-tokens 150

xai_stream:
	pip install -e .
	python -m opengradient.cli chat --model $(GROK_3_MINI_BETA) --mode TEE \
		--messages '[{"role":"user","content":"Tell me about the history of SpaceX"}]' \
		--max-tokens 200 \
		--stream

xai_tool_stream:
	pip install -e .
	python -m opengradient.cli chat --model $(GROK_3_MINI_BETA) --mode TEE \
		--messages '[{"role":"user","content":"Find the current temperature in New York"}]' \
		--tools '[{"type":"function","function":{"name":"get_temp","description":"Get temperature","parameters":{"type":"object","properties":{"location":{"type":"string"}},"required":["location"]}}}]' \
		--max-tokens 100 \
		--stream

# ============================================================================
# Test All Providers
# ============================================================================

test_all_chat:
	@echo "🤖 Testing normal chat for all providers..."
	@echo "\n📍 OpenAI GPT-4o:"
	$(MAKE) openai_chat
	@echo "\n📍 Anthropic Claude:"
	$(MAKE) anthropic_chat
	@echo "\n📍 Google Gemini:"
	$(MAKE) google_chat
	@echo "\n📍 xAI Grok:"
	$(MAKE) xai_chat

test_all_stream:
	@echo "🌊 Testing streaming for all providers..."
	@echo "\n📍 OpenAI GPT-4o:"
	$(MAKE) openai_stream
	@echo "\n📍 Anthropic Claude:"
	$(MAKE) anthropic_stream
	@echo "\n📍 Google Gemini:"
	$(MAKE) google_stream
	@echo "\n📍 xAI Grok:"
	$(MAKE) xai_stream

test_all_tool_stream:
	@echo "🔧 Testing tool streaming for all providers..."
	@echo "\n📍 OpenAI GPT-4o:"
	$(MAKE) openai_tool_stream
	@echo "\n📍 Anthropic Claude:"
	$(MAKE) anthropic_tool_stream
	@echo "\n📍 Google Gemini:"
	$(MAKE) google_tool_stream
	@echo "\n📍 xAI Grok:"
	$(MAKE) xai_tool_stream

test_all: test_all_chat test_all_stream test_all_tool_stream

# ============================================================================
# Batch Tests
# ============================================================================

batch_route_chat:
	pip install -e .
	@for i in $$(seq 1 50); do \
		python -m opengradient.cli chat --model $(GPT_4O) --mode TEE --messages '[{"role":"user", "content":"Who are you?"}]' --max-tokens 50 & \
	done; \
	wait

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

# ============================================================================
# Utility
# ============================================================================

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

test: integrationtest utils_test infer completion

integrationtest:
	python integrationtest/agent/test_agent.py
	python integrationtest/workflow_models/test_workflow_models.py

utils_test:
	pytest tests/utils_test.py -v

.PHONY: docs ruff integrationtest openai_chat openai_stream openai_tool_stream \
	anthropic_chat anthropic_stream anthropic_tool_stream \
	google_chat google_stream google_tool_stream \
	xai_chat xai_stream xai_tool_stream \
	test_all_chat test_all_stream test_all_tool_stream test_all \
	batch_route_chat batch_stream
