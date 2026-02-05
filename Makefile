# OpenGradient SDK Makefile

# Default model for testing (override with: make chat MODEL=openai/gpt-4o)
MODEL ?= anthropic/claude-3.7-sonnet

# ============================================================================
# Development
# ============================================================================

install:
	pip install -e .

build:
	python -m build

publish:
	@echo "Current version:" $$(grep 'version = ' pyproject.toml | cut -d'"' -f2)
	rm -rf dist/*
	python -m build
	twine upload dist/*

check:
	ruff format .
	mypy src
	mypy examples

docs:
	pdoc opengradient -o docs --template-dir ./templates --force

# ============================================================================
# Testing
# ============================================================================

test: utils_test integrationtest

utils_test:
	pytest tests/utils_test.py -v

integrationtest:
	python integrationtest/agent/test_agent.py
	python integrationtest/workflow_models/test_workflow_models.py

examples:
	@for f in $$(find examples -name '*.py' | sort); do \
		echo "Running $$f..."; \
		python "$$f" || exit 1; \
	done
	@echo "All examples passed."

# ============================================================================
# CLI Examples (use MODEL=provider/model to change model)
# ============================================================================

infer:
	python -m opengradient.cli infer \
		-m "hJD2Ja3akZFt1A2LT-D_1oxOCz_OtuGYw4V9eE1m39M" \
		--input '{"open_high_low_close": [[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4]]}'

completion:
	python -m opengradient.cli completion \
		--model $(MODEL) --mode TEE \
		--prompt "Hello, how are you?" \
		--max-tokens 50

chat:
	python -m opengradient.cli chat \
		--model $(MODEL) --mode TEE \
		--messages '[{"role":"user","content":"Tell me a fun fact"}]' \
		--max-tokens 150

chat-stream:
	python -m opengradient.cli chat \
		--model $(MODEL) --mode TEE \
		--messages '[{"role":"user","content":"Tell me a short story"}]' \
		--max-tokens 250 \
		--stream

chat-tool:
	python -m opengradient.cli chat \
		--model $(MODEL) --mode TEE \
		--messages '[{"role":"user","content":"What is the weather in Tokyo?"}]' \
		--tools '[{"type":"function","function":{"name":"get_weather","description":"Get weather for a location","parameters":{"type":"object","properties":{"location":{"type":"string"},"unit":{"type":"string","enum":["celsius","fahrenheit"]}},"required":["location"]}}}]' \
		--max-tokens 100 \
		--stream

.PHONY: install build publish check docs test utils_test integrationtest examples \
	infer completion chat chat-stream chat-tool
