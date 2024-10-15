import opengradient as og
import time
import random
import statistics
from typing import List, Callable, Tuple
import uuid
import argparse

# Number of requests to run serially
NUM_REQUESTS = 100
MODEL = "QmbUqS93oc4JTLMHwpVxsE39mhNxy6hpf6Py3r9oANr8aZ"

def run_inference(input_data: dict):
    og.infer(
        MODEL,
        og.InferenceMode.VANILLA,
        input_data
    )

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

def stress_test_wrapper(infer_function: Callable, num_requests: int) -> Tuple[List[float], int]:
    """
    Wrapper function to stress test the inference.
    
    Args:
    infer_function (Callable): The inference function to test.
    num_requests (int): Number of requests to send.
    
    Returns:
    Tuple[List[float], int]: List of latencies for each request and the number of failures.
    """
    latencies = []
    failures = 0
    
    for i in range(num_requests):
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

def main(private_key: str):
    # init with private key only
    og.init(private_key=private_key, email=None, password=None)

    latencies, failures = stress_test_wrapper(run_inference, num_requests=NUM_REQUESTS)
    
    # Calculate and print statistics
    total_requests = NUM_REQUESTS
    success_rate = (len(latencies) / total_requests) * 100 if total_requests > 0 else 0
    
    if latencies:
        avg_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
    else:
        avg_latency = median_latency = min_latency = max_latency = p95_latency = 0
    
    print("\nOpenGradient Inference Stress Test Results:")
    print(f"Using model '{MODEL}'")
    print("=" * 20 + "\n")
    print(f"Total Requests: {total_requests}")
    print(f"Successful Requests: {len(latencies)}")
    print(f"Failed Requests: {failures}")
    print(f"Success Rate: {success_rate:.2f}%\n")
    print(f"Average Latency: {avg_latency:.4f} seconds")
    print(f"Median Latency: {median_latency:.4f} seconds")
    print(f"Min Latency: {min_latency:.4f} seconds")
    print(f"Max Latency: {max_latency:.4f} seconds")
    print(f"95th Percentile Latency: {p95_latency:.4f} seconds")

    if failures > 0:
        print("\n🛑 WARNING: TEST FAILED")
    else:
        print("\n✅ NO FAILURES")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run inference stress test")
    parser.add_argument("private_key", help="Private key for inference")
    args = parser.parse_args()
    
    main(args.private_key)
