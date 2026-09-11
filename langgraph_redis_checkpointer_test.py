import os
import operator
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.redis import RedisSaver


# ==========================================
# 1. DEFINE OUR STATE
# ==========================================
# We use operator.add for messages so they append instead of overwrite
class GraphState(TypedDict):
    messages: Annotated[list[str], operator.add]
    step_1_completed: bool


# ==========================================
# 2. DEFINE THE NODES
# ==========================================
def extraction_node(state: GraphState):
    print("\n[WORKER] --- NODE 1: EXTRACTION Executing... ---")
    print("[WORKER] (Pretending to do heavy PDF extraction for 10 seconds...)")

    return {
        "step_1_completed": True,
        "messages": ["Node 1: Extracted text from PDF"]
    }


# We use a global variable to simulate a transient crash on the first run
ATTEMPTS = 0

from memory_profiler import profile

@profile
def generation_node(state: GraphState):
    global ATTEMPTS
    ATTEMPTS += 1
    print("\n[WORKER] --- NODE 2: GENERATION Executing... ---")

    if ATTEMPTS == 1:
        print("[WORKER] 💥 CRASH! The worker ran out of memory (Simulated OOM).")
        # Raising an exception here simulates a Celery worker dying mid-task.
        # Note: Because Node 1 already finished, its state IS saved in Redis!
        raise RuntimeError("Worker Hard Crash")

    print("[WORKER] ✅ Worker survived! Generating final report...")
    return {"messages": ["Node 2: Final Report Generated!"]}


# ==========================================
# 3. BUILD AND COMPILE THE GRAPH
# ==========================================
workflow = StateGraph(GraphState)
workflow.add_node("extraction", extraction_node)
workflow.add_node("generation", generation_node)

workflow.add_edge(START, "extraction")
workflow.add_edge("extraction", "generation")
workflow.add_edge("generation", END)


# ==========================================
# 4. EXECUTION SIMULATION (THE "CELERY" RUNNER)
# ==========================================
def run_celery_task(thread_id: str):
    redis_uri = "redis://localhost:6379"

    with RedisSaver.from_conn_string(redis_uri) as checkpointer:
        checkpointer.setup()
        app = workflow.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": thread_id}}

        print(f"\n🚀 [SYSTEM] Starting Celery Task for thread_id: {thread_id}")

        # --- THE FIX IS HERE ---
        # Fetch the current state from Redis before invoking
        current_state = app.get_state(config)

        # If current_state.next has pending nodes, it means the graph crashed
        # midway and needs to be resumed.
        if current_state and current_state.next:
            print(f"[SYSTEM] 🔄 Existing state found! Pending nodes: {current_state.next}")
            print("[SYSTEM] Resuming from crash point...")
            # Passing None tells LangGraph to resume pending nodes using the checkpoint!
            input_data = None
        else:
            print("[SYSTEM] 🆕 No state found. Starting fresh...")
            input_data = {"messages": ["User Uploaded PDF."]}

        try:
            result = app.invoke(input_data, config=config)
            print("\n🎉 [SYSTEM] TASK COMPLETED SUCCESSFULLY!")
            print("Final State:", result)

        except RuntimeError as e:
            print(f"\n🚨 [SYSTEM] TASK FAILED WITH ERROR: {e}")
            print("[SYSTEM] (RabbitMQ will redeliver this task to a new worker...)")


if __name__ == "__main__":
    # In a real app, this job_id comes from FastAPI and is saved in your DB
    job_id = "pdf-job-999"

    print("==================================================")
    print(" SIMULATION: RUN 1 (Worker will crash)")
    print("==================================================")
    run_celery_task(thread_id=job_id)

    print("\n\n==================================================")
    print(" SIMULATION: RUN 2 (RabbitMQ Retries the Task)")
    print("==================================================")
    # Notice we pass the EXACT SAME thread_id.
    # Watch the console output carefully: Node 1 will NOT run this time.
    run_celery_task(thread_id=job_id)