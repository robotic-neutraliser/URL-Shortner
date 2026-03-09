"""
Load Test for URL Shortener
-----------------------------
Make sure the server is running first:
  uvicorn main:app --reload

Then run:
  python load_test.py
"""

import time
import json
import threading
import urllib.request
import urllib.error

BASE_URL    = "http://localhost:8000"
TOTAL_REQS  = 100   # total URLs to shorten
THREADS     = 20    # concurrent threads

SAMPLE_URLS = [
    "https://www.google.com",
    "https://www.github.com",
    "https://www.youtube.com",
    "https://www.stackoverflow.com",
    "https://www.wikipedia.org",
]

results   = {"success": 0, "errors": 0}
latencies = []
lock      = threading.Lock()


def shorten_url(url: str):
    start = time.time()
    try:
        data = json.dumps({"long_url": url}).encode("utf-8")
        req  = urllib.request.Request(
            f"{BASE_URL}/shorten",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as response:
            latency = (time.time() - start) * 1000
            with lock:
                results["success"] += 1
                latencies.append(latency)
    except Exception:
        with lock:
            results["errors"] += 1


print(f"Sending {TOTAL_REQS} requests across {THREADS} threads...\n")
start_time = time.time()

threads = []
for i in range(TOTAL_REQS):
    url = SAMPLE_URLS[i % len(SAMPLE_URLS)]
    t   = threading.Thread(target=shorten_url, args=(url,))
    threads.append(t)

for i in range(0, TOTAL_REQS, THREADS):
    batch = threads[i:i + THREADS]
    for t in batch:
        t.start()
    for t in batch:
        t.join()

total_time  = time.time() - start_time
avg_latency = sum(latencies) / len(latencies) if latencies else 0
max_latency = max(latencies) if latencies else 0
rps         = TOTAL_REQS / total_time

print("=" * 40)
print(f"  Total requests  : {TOTAL_REQS}")
print(f"  Successful      : {results['success']}")
print(f"  Errors          : {results['errors']}")
print(f"  Total time      : {total_time:.2f}s")
print(f"  Requests/sec    : {rps:.1f}")
print(f"  Avg latency     : {avg_latency:.1f}ms")
print(f"  Max latency     : {max_latency:.1f}ms")
print("=" * 40)
