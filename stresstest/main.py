import opengradient as og
import time
import random
import statistics
from typing import List, Callable, Tuple
import uuid
import argparse

# Number of requests to run serially
NUM_REQUESTS = 1000

def run_prompt(prompt: str):
    og.infer_llm(
        "meta-llama/Meta-Llama-3-8B-Instruct",
        prompt,
        max_tokens=100
    )

def generate_unique_prompt(request_id: int) -> str:
    """Generate a unique prompt for testing."""
    topics = ["science", "history", "technology", "art", "sports", "music", "literature", "philosophy", "politics", "economics"]
    adjectives = ["interesting", "surprising", "little-known", "controversial", "inspiring", "thought-provoking"]
    
    topic = random.choice(topics)
    adjective = random.choice(adjectives)
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 characters of a UUID
    
    return f"Request {request_id}: Tell me a {adjective} fact about {topic}. Unique ID: {unique_id}"

def stress_test_wrapper(infer_function: Callable, num_requests: int) -> Tuple[List[float], int]:
    """
    Wrapper function to stress test the LLM inference.
    
    Args:
    infer_function (Callable): The LLM inference function to test.
    num_requests (int): Number of requests to send. Default is 1000.
    
    Returns:
    Tuple[List[float], int]: List of latencies for each request and the number of failures.
    """
    latencies = []
    failures = 0
    
    for i in range(num_requests):
        prompt = generate_unique_prompt(i)
        start_time = time.time()
        
        try:
            _ = infer_function(prompt)
            end_time = time.time()
            latency = end_time - start_time
            latencies.append(latency)
            print(f"Request {i+1}/{num_requests} completed. Latency: {latency:.4f} seconds")
        except Exception as e:
            failures += 1
            print(f"Request {i+1}/{num_requests} failed. Error: {str(e)}")
    
    return latencies, failures

def main(private_key: str):
    # init with private key only
    og.init(private_key=private_key, email=None, password=None)

    latencies, failures = stress_test_wrapper(run_prompt, num_requests=NUM_REQUESTS)
    
    # Calculate and print statistics
    total_requests = len(latencies) + failures
    success_rate = (len(latencies) / total_requests) * 100 if total_requests > 0 else 0
    
    if latencies:
        avg_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
    else:
        avg_latency = median_latency = min_latency = max_latency = p95_latency = 0
    
    print("\nTest Results:")
    print(f"Total Requests: {total_requests}")
    print(f"Successful Requests: {len(latencies)}")
    print(f"Failed Requests: {failures}")
    print(f"Success Rate: {success_rate:.2f}%")
    print(f"Average Latency: {avg_latency:.4f} seconds")
    print(f"Median Latency: {median_latency:.4f} seconds")
    print(f"Min Latency: {min_latency:.4f} seconds")
    print(f"Max Latency: {max_latency:.4f} seconds")
    print(f"95th Percentile Latency: {p95_latency:.4f} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LLM inference stress test")
    parser.add_argument("private_key", help="Private key for inference")
    args = parser.parse_args()
    
    main(args.private_key)