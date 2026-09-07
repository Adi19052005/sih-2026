import os
import tempfile

from backend.tools.sandbox import execute_python_code

from backend.tools.doc_generator import (
    generate_word_doc,
    generate_powerpoint,
    generate_csv
)


def test_valid_python_execution():
    """Test valid Python code execution."""

    print("\n[Test A] Testing valid Python execution...")

    result = execute_python_code(
        "print('Sandbox Active')"
    )

    assert result["success"] is True
    assert "Sandbox Active" in result["stdout"]

    print("PASS: Valid Python execution")
    print("Output:", result["stdout"].strip())


def test_broken_python_execution():
    """Test broken Python code execution."""

    print("\n[Test B] Testing broken Python execution...")

    result = execute_python_code(
        "1 / 0"
    )

    assert result["success"] is False
    assert result["stderr"]

    print("PASS: Broken Python error handling")

    print("Error captured:")
    print(result["stderr"].strip())


def test_document_generators():
    """Test DOCX, PPTX, and CSV generation."""

    print("\n[Test C] Testing document generators...")

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:

        # File paths
        docx_path = os.path.join(
            temp_dir,
            "test_document.docx"
        )

        pptx_path = os.path.join(
            temp_dir,
            "test_presentation.pptx"
        )

        csv_path = os.path.join(
            temp_dir,
            "test_data.csv"
        )

        # -------------------------
        # Generate Word Document
        # -------------------------
        generate_word_doc(
            title="Step 2 Test Document",
            content=(
                "This document was generated locally "
                "by the Sovereign AI Workbench."
            ),
            filepath=docx_path
        )

        assert os.path.exists(docx_path)

        print("PASS: Word document generation")

        # -------------------------
        # Generate PowerPoint
        # -------------------------
        generate_powerpoint(
            title="Step 2 Test Presentation",
            bullet_points=[
                "Local execution",
                "Air-gapped architecture",
                "No external API calls",
                "Deterministic tools"
            ],
            filepath=pptx_path
        )

        assert os.path.exists(pptx_path)

        print("PASS: PowerPoint generation")

        # -------------------------
        # Generate CSV
        # -------------------------
        generate_csv(
            headers=[
                "Component",
                "Status"
            ],
            rows=[
                ["Execution Sandbox", "Working"],
                ["Word Generator", "Working"],
                ["PowerPoint Generator", "Working"],
                ["CSV Generator", "Working"]
            ],
            filepath=csv_path
        )

        assert os.path.exists(csv_path)

        print("PASS: CSV generation")


def main():

    print("=" * 50)
    print("SOVEREIGN AI WORKBENCH")
    print("STEP 2 - CORE TOOLS TEST")
    print("=" * 50)

    test_valid_python_execution()

    test_broken_python_execution()

    test_document_generators()

    print("\n" + "=" * 50)
    print("ALL STEP 2 TESTS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    main()