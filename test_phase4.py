from fastapi.testclient import TestClient

from backend.api import app
from backend.router import TaskRouter
from backend.network_sentry import check_airgap_status


client = TestClient(app)


def print_header(title):

    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_network_sentry():

    print_header(
        "TEST A: NETWORK SENTRY"
    )

    result = check_airgap_status()

    print("\nWorkbench Status:")
    print(result["status"])

    print("\nWorkbench Air-Gapped:")
    print(result["airgapped"])

    print("\nExternal Connections:")
    print(result["external_socket_count"])

    assert "airgapped" in result
    assert "status" in result
    assert "active_external_sockets" in result

    print("\nPASS: Network Sentry is working")


def test_sentry_api():

    print_header(
        "TEST B: SENTRY API ENDPOINT"
    )

    response = client.get(
        "/sentry/status"
    )

    print("\nHTTP Status:")
    print(response.status_code)

    print("\nResponse:")

    data = response.json()

    print(data)

    assert response.status_code == 200

    assert "airgapped" in data
    assert "status" in data

    print("\nPASS: /sentry/status API")


def test_router():

    print_header(
        "TEST C: SMART MODEL ROUTER"
    )

    router = TaskRouter()

    # Image routing

    result = router.route(
        "Analyze this image",
        file_path="workspace/test.png"
    )

    print(
        "\nImage File →",
        result
    )

    assert result == "qwen2.5vl:7b"

    # PDF routing

    result = router.route(
        "Read this scanned document",
        file_path="workspace/document.pdf"
    )

    print(
        "Scanned PDF →",
        result
    )

    assert result == "qwen2.5vl:7b"

    # Coding routing

    result = router.route(
        "Write a Python script"
    )

    print(
        "Python Task →",
        result
    )

    assert result == "qwen2.5-coder:3b"

    # General routing

    result = router.route(
        "Explain artificial intelligence"
    )

    print(
        "General Task →",
        result
    )

    assert result == "qwen2.5:3b"

    print("\nPASS: Smart Model Router")


def test_chat_api():

    print_header(
        "TEST D: CHAT API"
    )

    response = client.post(
        "/chat",
        data={
            "prompt":
            "Write a python script that prints numbers from 1 to 5"
        }
    )

    print("\nHTTP Status:")
    print(response.status_code)

    assert response.status_code == 200

    data = response.json()

    print("\nSession ID:")
    print(data["session_id"])

    print("\nSelected Model:")
    print(data["selected_model"])

    print("\nGenerated Code:")
    print(data["generated_code"])

    print("\nFinal Output:")
    print(data["final_output"])

    assert data["success"] is True

    assert data["session_id"] is not None

    assert data["selected_model"] == (
        "qwen2.5-coder:3b"
    )

    assert data["tool_result"] is not None

    return data["session_id"]


def test_history_api(session_id):

    print_header(
        "TEST E: SQLITE HISTORY API"
    )

    response = client.get(
        f"/history/{session_id}"
    )

    print("\nHTTP Status:")
    print(response.status_code)

    assert response.status_code == 200

    data = response.json()

    print("\nSession ID:")
    print(data["session_id"])

    print("\nMessage Count:")
    print(data["message_count"])

    print("\nHistory:")

    for message in data["history"]:

        print(
            f"[{message['role']}] "
            f"{message['content']}"
        )

    assert data["session_id"] == session_id

    assert data["message_count"] >= 1

    print("\nPASS: SQLite History API")


def test_artifacts_api(session_id):

    print_header(
        "TEST F: ARTIFACTS API"
    )

    response = client.get(
        f"/artifacts/{session_id}"
    )

    print("\nHTTP Status:")
    print(response.status_code)

    assert response.status_code == 200

    data = response.json()

    print("\nSession ID:")
    print(data["session_id"])

    print("\nArtifact Count:")
    print(data["artifact_count"])

    print("\nArtifacts:")

    for artifact in data["artifacts"]:

        print(artifact)

    assert data["session_id"] == session_id

    assert "artifacts" in data

    print("\nPASS: Artifacts API")


def main():

    print("\n")

    print("#" * 65)
    print("SOVEREIGN AI WORKBENCH")
    print("PHASE 4 - COMPLETE VERIFICATION SUITE")
    print("#" * 65)

    # ----------------------------------------------
    # TEST A
    # ----------------------------------------------

    test_network_sentry()

    # ----------------------------------------------
    # TEST B
    # ----------------------------------------------

    test_sentry_api()

    # ----------------------------------------------
    # TEST C
    # ----------------------------------------------

    test_router()

    # ----------------------------------------------
    # TEST D
    # ----------------------------------------------

    session_id = test_chat_api()

    # ----------------------------------------------
    # TEST E
    # ----------------------------------------------

    test_history_api(
        session_id
    )

    # ----------------------------------------------
    # TEST F
    # ----------------------------------------------

    test_artifacts_api(
        session_id
    )

    print("\n")

    print("=" * 65)
    print("ALL PHASE 4 TESTS PASSED")
    print("=" * 65)

    print("\nVerified Components:")

    print("✓ Network Sentry")
    print("✓ Workbench Air-Gap Monitoring")
    print("✓ FastAPI Server")
    print("✓ Sentry Status Endpoint")
    print("✓ Smart Model Router")
    print("✓ Chat API")
    print("✓ LangGraph Agent Integration")
    print("✓ SQLite Chat History API")
    print("✓ Artifact API")

    print("\nPHASE 4 COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()