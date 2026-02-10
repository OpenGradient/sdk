"""
Example: Structured outputs with OpenGradient TEE LLM inference

This example demonstrates how to use response_format to constrain LLM outputs
to valid JSON matching a specific schema. This is useful for reliable data extraction,
structured AI workflows, and programmatic consumption of LLM outputs.

Requirements:
- Set OG_PRIVATE_KEY environment variable with your wallet private key
- The model must support structured outputs (e.g., GPT-4o, GPT-4o-mini)

Usage:
    export OG_PRIVATE_KEY="0x..."
    python examples/run_x402_structured_output.py

Note:
    Structured output support depends on both the model and backend implementation.
    If you see markdown-formatted responses instead of pure JSON, the backend may
    not fully support response_format yet, or the model may need additional configuration.
"""

import json
import os
import re

import opengradient as og


def extract_json_from_response(content: str) -> str:
    """
    Extract JSON from response content.

    Handles cases where the backend returns markdown-formatted JSON
    instead of pure JSON.

    Args:
        content: The response content (may be JSON or markdown with JSON)

    Returns:
        Extracted JSON string
    """
    # Try to parse as-is first
    try:
        json.loads(content)
        return content
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', content, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()

    # Try to find JSON object in text
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        try:
            json.loads(json_match.group(0))
            return json_match.group(0)
        except json.JSONDecodeError:
            pass

    # If all else fails, return original content
    return content


def example_1_simple_json_mode():
    """Example 1: Simple JSON mode with chat"""
    print("\n=== Example 1: Simple JSON Mode ===")
    print("Using type='json_object' to return any valid JSON structure\n")

    private_key = os.environ.get("OG_PRIVATE_KEY")
    if not private_key:
        raise ValueError("Please set OG_PRIVATE_KEY environment variable")

    client = og.init(private_key=private_key)

    # Simple JSON mode - returns valid JSON, any structure
    result = client.llm.chat(
        model=og.TEE_LLM.GPT_4O,
        messages=[{"role": "user", "content": "List 3 colors as a JSON object with a 'colors' array"}],
        max_tokens=200,
        response_format={"type": "json_object"},
    )

    print(f"Raw response: {result.chat_output['content']}")
    data = json.loads(result.chat_output["content"])
    print(f"Parsed JSON: {data}")
    print(f"Payment hash: {result.payment_hash}")


def example_2_schema_validated_chat():
    """Example 2: Schema-validated output with chat"""
    print("\n=== Example 2: Schema-Validated Output ===")
    print("Using type='json_schema' to enforce a specific structure\n")

    private_key = os.environ.get("OG_PRIVATE_KEY")
    if not private_key:
        raise ValueError("Please set OG_PRIVATE_KEY environment variable")

    client = og.init(private_key=private_key)

    # Define a strict schema for the response
    color_schema = {
        "type": "object",
        "properties": {
            "colors": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of color names",
            },
            "count": {"type": "integer", "description": "Number of colors"},
        },
        "required": ["colors", "count"],
        "additionalProperties": False,
    }

    # Schema-validated mode - must match the schema exactly
    result = client.llm.chat(
        model=og.TEE_LLM.GPT_4O,
        messages=[{"role": "user", "content": "Give me 5 primary and secondary colors"}],
        max_tokens=300,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "color_list",
                "schema": color_schema,
                "strict": True,
            },
        },
    )

    print(f"Raw response: {result.chat_output['content']}")
    data = json.loads(result.chat_output["content"])
    print(f"\nColors returned: {data['colors']}")
    print(f"Count: {data['count']}")
    print(f"Payment hash: {result.payment_hash}")


def example_3_completion_structured():
    """Example 3: Structured output with completion"""
    print("\n=== Example 3: Structured Completion ===")
    print("Using response_format with the completion API\n")

    private_key = os.environ.get("OG_PRIVATE_KEY")
    if not private_key:
        raise ValueError("Please set OG_PRIVATE_KEY environment variable")

    client = og.init(private_key=private_key)

    # Schema for math problem response
    math_schema = {
        "type": "object",
        "properties": {
            "answer": {"type": "number", "description": "The numerical answer"},
            "explanation": {"type": "string", "description": "Step-by-step explanation"},
        },
        "required": ["answer", "explanation"],
    }

    result = client.llm.completion(
        model=og.TEE_LLM.GPT_4O,
        prompt="What is 15% of 240? Respond with JSON containing 'answer' and 'explanation' fields.",
        max_tokens=200,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "math_response",
                "schema": math_schema,
            },
        },
    )

    print(f"Raw response: {result.completion_output}")
    data = json.loads(result.completion_output)
    print(f"\nAnswer: {data['answer']}")
    print(f"Explanation: {data['explanation']}")


def example_4_streaming_structured():
    """Example 4: Streaming with structured output"""
    print("\n=== Example 4: Streaming Structured Output ===")
    print("Streaming JSON chunks (note: JSON is only valid when complete)\n")

    private_key = os.environ.get("OG_PRIVATE_KEY")
    if not private_key:
        raise ValueError("Please set OG_PRIVATE_KEY environment variable")

    client = og.init(private_key=private_key)

    # Define schema for a story response
    story_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "content": {"type": "string"},
            "word_count": {"type": "integer"},
        },
        "required": ["title", "content", "word_count"],
    }

    print("Streaming chunks:")
    chunks = []
    for chunk in client.llm.chat(
        model=og.TEE_LLM.GPT_4O,
        messages=[{"role": "user", "content": "Write a very short story (2 sentences) about a robot"}],
        max_tokens=300,
        stream=True,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "story_response",
                "schema": story_schema,
            },
        },
    ):
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            chunks.append(content)

    print("\n")
    full_response = "".join(chunks)
    data = json.loads(full_response)
    print(f"\nParsed structured response:")
    print(f"Title: {data['title']}")
    print(f"Content: {data['content']}")
    print(f"Word count: {data['word_count']}")


if __name__ == "__main__":
    try:
        example_1_simple_json_mode()
        example_2_schema_validated_chat()
        example_3_completion_structured()
        example_4_streaming_structured()
        print("\n✅ All examples completed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
