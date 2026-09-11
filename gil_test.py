import time
import threading
import multiprocessing
import sys


"""
Output of Program


Python Version: 3.13.7
GIL Status: Enabled

--- 1. SEQUENTIAL (BASELINE) ---
[Task A] Starting calculation...
[Task A] Finished!
[Task B] Starting calculation...
[Task B] Finished!
Sequential Time: 15.41 seconds

--- 2. THREADING (GIL ENABLED) ---
[Thread A] Starting calculation...
[Thread B] Starting calculation...
[Thread B] Finished!
[Thread A] Finished!
Threading Time: 15.43 seconds                          ## IMPORTANT -> Because of GIL, the time has slightly increased
                                                                       because python keeps switching between threads

--- 3. MULTIPROCESSING (GIL BYPASSED) ---
[Process A] Starting calculation...
[Process B] Starting calculation...
[Process B] Finished!
[Process A] Finished!
Multiprocessing Time: 8.26 seconds


"""




# A heavy CPU-bound task
def heavy_computation(name, target):
    print(f"[{name}] Starting calculation...")
    while target > 0:
        target -= 1
    print(f"[{name}] Finished!")


# 1. Baseline: Running sequentially (One after the other)
def run_sequential(target):
    print("\n--- 1. SEQUENTIAL (BASELINE) ---")
    start = time.time()
    heavy_computation("Task A", target)
    heavy_computation("Task B", target)
    print(f"Sequential Time: {time.time() - start:.2f} seconds")


# 2. Threading: The GIL Bottleneck
def run_with_threads(target):
    print("\n--- 2. THREADING (GIL ENABLED) ---")
    start = time.time()

    thread1 = threading.Thread(target=heavy_computation, args=("Thread A", target))
    thread2 = threading.Thread(target=heavy_computation, args=("Thread B", target))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    print(f"Threading Time: {time.time() - start:.2f} seconds")


# 3. Multiprocessing: Bypassing the GIL
def run_with_multiprocessing(target):
    print("\n--- 3. MULTIPROCESSING (GIL BYPASSED) ---")
    start = time.time()

    process1 = multiprocessing.Process(target=heavy_computation, args=("Process A", target))
    process2 = multiprocessing.Process(target=heavy_computation, args=("Process B", target))

    process1.start()
    process2.start()

    process1.join()
    process2.join()

    print(f"Multiprocessing Time: {time.time() - start:.2f} seconds")


if __name__ == "__main__":
    # 50 million countdown - adjust this if your computer is very fast/slow
    # You want the sequential time to take roughly 2 to 5 seconds.
    TARGET_COUNT = 500_000_000

    # Check if we are running the new GIL-less Python 3.13+ mode
    gil_status = "Unknown"
    if hasattr(sys, "_is_gil_enabled"):
        gil_status = "Enabled" if sys._is_gil_enabled() else "DISABLED"
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"GIL Status: {gil_status}")

    run_sequential(TARGET_COUNT)
    run_with_threads(TARGET_COUNT)
    run_with_multiprocessing(TARGET_COUNT)