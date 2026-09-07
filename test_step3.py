import os
import tempfile

from backend.db import db
from backend.rag_engine import ingest_document, query_rag
from backend.router import TaskRouter
from backend.agent import SovereignAgent


def test_database():
    """
    TEST A:
    Verify SQLite session creation and chat history.
    """

    print("\n" + "=" * 60)
    print("TEST A: SQLITE SESSION ENGINE")
    print("=" * 60)

    session_id = db.create_session()

    print("\nCreated Session ID:")
    print(session_id)

    db.save_message(
        session_id=session_id,
        role="user",
        content="Hello Sovereign Workbench",
        model_used=None
    )

    db.save_message(
        session_id=session_id,
        role="assistant",
        content="Local SQLite persistence is active.",
        model_used="qwen2.5:3b"
    )

    history = db.get_session_history(
        session_id
    )

    print("\nSession History:")

    for message in history:
        print(
            f"{message['role']}: "
            f"{message['content']}"
        )

    assert len(history) >= 2

    assert history[0]["role"] == "user"

    assert history[1]["role"] == "assistant"

    print("\nPASS: SQLite session and history persistence")


def test_rag_engine():
    """
    TEST B:
    Create a local text document,
    ingest it into ChromaDB,
    and retrieve context.
    """

    print("\n" + "=" * 60)
    print("TEST B: LOCAL CHROMADB RAG ENGINE")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:

        sample_file = os.path.join(
            temp_dir,
            "sovereign_ai_test.txt"
        )

        sample_content = """
Sovereign AI Workbench is a fully local and air-gapped
artificial intelligence platform.

The system uses Ollama models locally and does not require
external cloud APIs.

Sensitive government and enterprise documents remain inside
the local infrastructure.

The project includes SQLite session storage, ChromaDB local
RAG, a Python execution sandbox, and document generators.
"""

        with open(
            sample_file,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(sample_content)

        print("\nSample document created:")
        print(sample_file)

        chunk_count = ingest_document(
            sample_file
        )

        print("\nChunks stored in ChromaDB:")
        print(chunk_count)

        assert chunk_count > 0

        context = query_rag(
            "What is Sovereign AI Workbench?"
        )

        print("\nRetrieved RAG Context:")
        print(context)

        assert context.strip() != ""

        assert (
            "Sovereign AI Workbench"
            in context
        )

    print("\nPASS: Local document ingestion and retrieval")


def test_router():
    """
    TEST C:
    Verify TaskRouter selects the correct model.
    """

    print("\n" + "=" * 60)
    print("TEST C: SMART MODEL ROUTER")
    print("=" * 60)

    router = TaskRouter()

    # -----------------------------------------
    # CODING TASK
    # -----------------------------------------

    coding_result = router.route(
        "Write a Python script to calculate factorial"
    )

    print(
        "\nCoding prompt →",
        coding_result
    )

    assert (
        coding_result
        == "qwen2.5-coder:3b"
    )

    # -----------------------------------------
    # GENERAL TASK
    # -----------------------------------------

    general_result = router.route(
        "Explain what artificial intelligence is"
    )

    print(
        "General prompt →",
        general_result
    )

    assert (
        general_result
        == "qwen2.5:3b"
    )

    # -----------------------------------------
    # VISION / FILE TASK
    # -----------------------------------------

    vision_result = router.route(
        prompt="Analyze this uploaded document",
        file_path="workspace/sample.pdf"
    )

    print(
        "File prompt →",
        vision_result
    )

    assert (
        vision_result
        == "qwen2.5vl:7b"
    )

    # -----------------------------------------
    # OCR TASK
    # -----------------------------------------

    ocr_result = router.route(
        "Perform OCR on this image"
    )

    print(
        "OCR prompt →",
        ocr_result
    )

    assert (
        ocr_result
        == "qwen2.5vl:7b"
    )

    print("\nPASS: Smart model routing")


def test_agent_full_pipeline():
    """
    TEST D:

    Test the complete pipeline:

    Prompt
        ↓
    RAG
        ↓
    Router
        ↓
    Ollama
        ↓
    Python Sandbox
        ↓
    Session Workspace
        ↓
    SQLite Persistence
    """

    print("\n" + "=" * 60)
    print("TEST D: FULL AGENT PIPELINE")
    print("=" * 60)

    agent = SovereignAgent()

    session_id = db.create_session()

    print("\nSession ID:")
    print(session_id)

    result = agent.run(
        prompt=(
            "Write a Python script that prints the "
            "squares of numbers from 1 to 5"
        ),
        session_id=session_id
    )

    print("\nSelected Model:")
    print(
        result["selected_model"]
    )

    print("\nRAG Context:")
    print(
        result["rag_context"]
    )

    print("\nGenerated Code:")
    print(
        result["generated_code"]
    )

    print("\nSandbox Result:")
    print(
        result["tool_result"]
    )

    print("\nFinal Output:")
    print(
        result["final_output"]
    )

    # -----------------------------------------
    # VERIFY ROUTING
    # -----------------------------------------

    assert (
        result["selected_model"]
        == "qwen2.5-coder:3b"
    )

    # -----------------------------------------
    # VERIFY SANDBOX SUCCESS
    # -----------------------------------------

    assert (
        result["tool_result"]["success"]
        is True
    )

    # -----------------------------------------
    # VERIFY SESSION WORKSPACE
    # -----------------------------------------

    workspace_path = os.path.join(
        "workspace",
        f"session_{session_id}"
    )

    print("\nWorkspace Path:")
    print(
        os.path.abspath(workspace_path)
    )

    assert os.path.exists(
        workspace_path
    )

    # -----------------------------------------
    # VERIFY SQLITE PERSISTENCE
    # -----------------------------------------

    history = db.get_session_history(
        session_id
    )

    print("\nMessages Stored in SQLite:")

    for message in history:
        print(
            f"[{message['role']}] "
            f"{message['content'][:100]}"
        )

    assert len(history) >= 2

    print("\nPASS: Full Agent Pipeline")


def test_self_correction():
    """
    TEST E:

    Verify the actual LangGraph self-correction loop.

    Broken Code
        ↓
    Sandbox Failure
        ↓
    qwen2.5-coder:3b Correction
        ↓
    Sandbox Retry
        ↓
    SQLite Persistence
    """

    print("\n" + "=" * 60)
    print("TEST E: LANGGRAPH SELF-CORRECTION LOOP")
    print("=" * 60)

    agent = SovereignAgent()

    session_id = db.create_session()

    # Intentionally broken Python code
    broken_code = """
for i in range(5)
    print(i)
"""

    print("\nInitial Broken Code:")
    print(broken_code)

    result = agent.run_with_code(
        code=broken_code,
        session_id=session_id,
        prompt=(
            "Fix this Python syntax error and make "
            "the code execute successfully."
        )
    )

    print("\nCorrected Code:")
    print(
        result["generated_code"]
    )

    print("\nFinal Sandbox Result:")
    print(
        result["tool_result"]
    )

    print("\nCorrection Attempts:")
    print(
        result["error_count"]
    )

    print("\nFinal Output:")
    print(
        result["final_output"]
    )

    # -----------------------------------------
    # VERIFY SELF-CORRECTION OCCURRED
    # -----------------------------------------

    assert (
        result["error_count"] >= 1
    )

    assert (
        result["error_count"] <= 3
    )

    # -----------------------------------------
    # VERIFY FINAL EXECUTION
    # -----------------------------------------

    assert (
        result["tool_result"]["success"]
        is True
    )

    # -----------------------------------------
    # VERIFY SQLITE PERSISTENCE
    # -----------------------------------------

    history = db.get_session_history(
        session_id
    )

    print("\nStored Messages:")

    for message in history:
        print(
            f"[{message['role']}] "
            f"{message['content'][:100]}"
        )

    assert len(history) >= 2

    print(
        "\nPASS: Self-correction loop executed successfully"
    )


def main():

    print("\n" + "#" * 65)
    print("SOVEREIGN AI WORKBENCH")
    print("STEP 3 - SQLITE + RAG + ROUTER + LANGGRAPH AGENT")
    print("#" * 65)

    # -----------------------------------------
    # TEST A
    # -----------------------------------------

    test_database()

    # -----------------------------------------
    # TEST B
    # -----------------------------------------

    test_rag_engine()

    # -----------------------------------------
    # TEST C
    # -----------------------------------------

    test_router()

    # -----------------------------------------
    # TEST D
    # -----------------------------------------

    test_agent_full_pipeline()

    # -----------------------------------------
    # TEST E
    # -----------------------------------------

    test_self_correction()

    print("\n" + "=" * 65)
    print("ALL STEP 3 UPDATED TESTS PASSED")
    print("=" * 65)

    print("\nVerified Components:")

    print("✓ SQLite Session Engine")
    print("✓ SQLite Chat History")
    print("✓ Local ChromaDB RAG")
    print("✓ Local Embeddings")
    print("✓ Smart Model Router")
    print("✓ Ollama Agent")
    print("✓ Session-Isolated Sandbox")
    print("✓ LangGraph Self-Correction")
    print("✓ SQLite Agent Persistence")


if __name__ == "__main__":
    main()