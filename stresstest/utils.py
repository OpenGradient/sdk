import uuid
import time
import random
from typing import List, Callable, Tuple

def generate_unique_input(request_id: int) -> dict:
    """Generate a unique input for testing."""
    num_input1 = [random.uniform(0, 10) for _ in range(3)]
    num_input2 = random.randint(1, 20)
    str_input1 = [random.choice(["hello", "world", "ONNX", "test"]) for _ in range(2)]
    str_input2 = f"Request {request_id}: {str(uuid.uuid4())[:8]}"
    
    return {
        "num_input1": num_input1,
        "num_input2": num_input2,
        "str_input1": str_input1,
        "str_input2": str_input2
    }

def generate_unique_prompt(request_id: int) -> str:
    """Generate a unique prompt for testing."""
    topics = ["science", "history", "technology", "art", "sports", "music", "literature", "philosophy", "politics", "economics"]
    adjectives = ["interesting", "surprising", "little-known", "controversial", "inspiring", "thought-provoking"]
    
    topic = random.choice(topics)
    adjective = random.choice(adjectives)
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 characters of a UUID
    
    return f"Request {request_id}: Tell me a {adjective} fact about {topic}. Keep it short. Unique ID: {unique_id}"


def stress_test_wrapper(infer_function: Callable, num_requests: int, is_llm: bool = False) -> Tuple[List[float], int]:
    """
    Wrapper function to stress test the inference.
    
    Args:
    infer_function (Callable): The inference function to test.
    num_requests (int): Number of requests to send.
    is_llm (bool): Whether the test is for an LLM model. Default is False.
    
    Returns:
    Tuple[List[float], int]: List of latencies for each request and the number of failures.
    """
    latencies = []
    failures = 0
    
    for i in range(num_requests):
        if is_llm:
            input_data = generate_unique_prompt(i)
        else:
            input_data = generate_unique_input(i)
        
        start_time = time.time()
        
        try:
            _ = infer_function(input_data)
            end_time = time.time()
            latency = end_time - start_time
            latencies.append(latency)
            print(f"Request {i+1}/{num_requests} completed. Latency: {latency:.4f} seconds")
        except Exception as e:
            failures += 1
            print(f"Request {i+1}/{num_requests} failed. Error: {str(e)}")
    
    return latencies, failures
