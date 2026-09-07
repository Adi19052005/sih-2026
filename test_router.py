
from backend.router import TaskRouter


def main():
    router = TaskRouter()

    print("=" * 45)
    print("TASK ROUTER TEST")
    print("=" * 45)

    # Test 1: Coding prompt
    result = router.route("Write a Python script")

    print("\nTest 1: Coding Prompt")
    print("Selected model:", result)

    assert result == "qwen2.5-coder:3b"

    print("PASS")

    # Test 2: General prompt
    result = router.route("Explain artificial intelligence")

    print("\nTest 2: General Prompt")
    print("Selected model:", result)

    assert result == "qwen2.5:3b"

    print("PASS")

    # Test 3: File / Vision prompt
    result = router.route(
        "Analyze this uploaded file",
        has_file=True
    )

    print("\nTest 3: File Prompt")
    print("Selected model:", result)

    assert result == "qwen2.5vl:7b"

    print("PASS")

    print("\n" + "=" * 45)
    print("ALL ROUTER TESTS PASSED")
    print("=" * 45)


if __name__ == "__main__":
    main()
