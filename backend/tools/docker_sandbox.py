import os
import shutil
import tempfile
import subprocess
from pathlib import Path


# ==========================================================
# SANDBOX CONFIGURATION
# ==========================================================

TIMEOUT_SECONDS = 10

MEMORY_LIMIT = "256m"

CPU_LIMIT = "1"

PID_LIMIT = "64"


# ==========================================================
# LANGUAGE CONFIGURATION
# ==========================================================

LANGUAGE_CONFIG = {

    # ------------------------------------------------------
    # PYTHON
    # ------------------------------------------------------

    "python": {
        "image": "python:3.12-alpine",
        "filename": "main.py",
        "command": [
            "python",
            "/workspace/main.py"
        ]
    },

    # ------------------------------------------------------
    # JAVASCRIPT
    # ------------------------------------------------------

    "javascript": {
        "image": "node:22-alpine",
        "filename": "main.js",
        "command": [
            "node",
            "/workspace/main.js"
        ]
    },

    "js": {
        "image": "node:22-alpine",
        "filename": "main.js",
        "command": [
            "node",
            "/workspace/main.js"
        ]
    },

    # ------------------------------------------------------
    # JAVA
    # ------------------------------------------------------

    "java": {
        "image": "eclipse-temurin:21-jdk-alpine",
        "filename": "Main.java",
        "command": [
            "sh",
            "-c",
            "javac /workspace/Main.java "
            "&& java -cp /workspace Main"
        ]
    },

    # ------------------------------------------------------
    # C++
    # ------------------------------------------------------

    "cpp": {
        "image": "gcc:14",
        "filename": "main.cpp",
        "command": [
            "sh",
            "-c",
            "g++ /workspace/main.cpp "
            "-o /workspace/program "
            "&& /workspace/program"
        ]
    },

    "c++": {
        "image": "gcc:14",
        "filename": "main.cpp",
        "command": [
            "sh",
            "-c",
            "g++ /workspace/main.cpp "
            "-o /workspace/program "
            "&& /workspace/program"
        ]
    },

    # ------------------------------------------------------
    # C
    # ------------------------------------------------------

    "c": {
        "image": "gcc:14",
        "filename": "main.c",
        "command": [
            "sh",
            "-c",
            "gcc /workspace/main.c "
            "-o /workspace/program "
            "&& /workspace/program"
        ]
    }
}


# ==========================================================
# CHECK DOCKER
# ==========================================================

def is_docker_available() -> bool:

    try:

        result = subprocess.run(
            [
                "docker",
                "--version"
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        return result.returncode == 0

    except Exception:

        return False


# ==========================================================
# NORMALIZE LANGUAGE
# ==========================================================

def normalize_language(
    language: str
) -> str:

    if not language:

        return "python"

    language = language.lower().strip()

    aliases = {

        "py": "python",
        "python3": "python",

        "node": "javascript",
        "nodejs": "javascript",

        "cxx": "cpp",

        "c plus plus": "cpp"
    }

    return aliases.get(
        language,
        language
    )


# ==========================================================
# EXECUTE CODE IN DOCKER
# ==========================================================

def execute_code(
    code: str,
    language: str = "python",
    timeout_seconds: int = TIMEOUT_SECONDS,
    working_directory: str = None
) -> dict:
    """
    Execute source code inside an isolated Docker container.

    Supported languages:

    - Python
    - JavaScript
    - Java
    - C
    - C++

    Security:

    - No network access
    - Memory limited
    - CPU limited
    - PID limited
    - Temporary isolated workspace
    - Automatic cleanup

    Returns:

    {
        "success": bool,
        "stdout": str,
        "stderr": str,
        "language": str
    }
    """

    temp_directory = None

    try:

        # --------------------------------------------------
        # NORMALIZE LANGUAGE
        # --------------------------------------------------

        language = normalize_language(
            language
        )

        if language not in LANGUAGE_CONFIG:

            return {
                "success": False,
                "stdout": "",
                "stderr": (
                    f"Unsupported language: {language}. "
                    "Supported languages: "
                    "python, java, javascript, c, cpp"
                ),
                "language": language
            }

        # --------------------------------------------------
        # CHECK DOCKER
        # --------------------------------------------------

        if not is_docker_available():

            return {
                "success": False,
                "stdout": "",
                "stderr": (
                    "Docker is not available. "
                    "Please install Docker Desktop and "
                    "make sure it is running."
                ),
                "language": language
            }

        # --------------------------------------------------
        # GET LANGUAGE CONFIG
        # --------------------------------------------------

        config = LANGUAGE_CONFIG[
            language
        ]

        image = config["image"]

        filename = config["filename"]

        command = config["command"]

        # --------------------------------------------------
        # CREATE TEMPORARY ISOLATED DIRECTORY
        # --------------------------------------------------

        temp_directory = tempfile.mkdtemp(
            prefix="sovereign_sandbox_"
        )

        source_file = os.path.join(
            temp_directory,
            filename
        )

        # --------------------------------------------------
        # WRITE SOURCE CODE
        # --------------------------------------------------

        with open(
            source_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(code)

        # --------------------------------------------------
        # WINDOWS PATH FIX
        # --------------------------------------------------

        docker_workspace = os.path.abspath(
            temp_directory
        )

        # --------------------------------------------------
        # BUILD DOCKER COMMAND
        # --------------------------------------------------

        docker_command = [

            "docker",
            "run",

            "--rm",

            # ------------------------------------------
            # SECURITY
            # ------------------------------------------

            "--network",
            "none",

            "--memory",
            MEMORY_LIMIT,

            "--cpus",
            CPU_LIMIT,

            "--pids-limit",
            PID_LIMIT,

            # Prevent privilege escalation

            "--security-opt",
            "no-new-privileges",

            # ------------------------------------------
            # CONTAINER NAME
            # ------------------------------------------

            "--name",
            (
                f"sovereign-sandbox-"
                f"{os.getpid()}"
            ),

            # ------------------------------------------
            # MOUNT TEMP DIRECTORY
            # ------------------------------------------

            "-v",
            (
                f"{docker_workspace}:"
                f"/workspace"
            ),

            # ------------------------------------------
            # WORKING DIRECTORY
            # ------------------------------------------

            "-w",
            "/workspace",

            # ------------------------------------------
            # IMAGE
            # ------------------------------------------

            image
        ]

        # Add execution command

        docker_command.extend(
            command
        )

        # --------------------------------------------------
        # RUN CONTAINER
        # --------------------------------------------------

        result = subprocess.run(
            docker_command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )

        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        if result.returncode == 0:

            return {

                "success": True,

                "stdout": result.stdout,

                "stderr": result.stderr,

                "language": language,

                "sandbox": "docker"
            }

        # --------------------------------------------------
        # EXECUTION FAILURE
        # --------------------------------------------------

        return {

            "success": False,

            "stdout": result.stdout,

            "stderr": result.stderr,

            "language": language,

            "sandbox": "docker"
        }


    # ======================================================
    # TIMEOUT
    # ======================================================

    except subprocess.TimeoutExpired as error:

        stdout = error.stdout or ""

        stderr = error.stderr or ""

        if isinstance(
            stdout,
            bytes
        ):

            stdout = stdout.decode(
                "utf-8",
                errors="replace"
            )

        if isinstance(
            stderr,
            bytes
        ):

            stderr = stderr.decode(
                "utf-8",
                errors="replace"
            )

        return {

            "success": False,

            "stdout": stdout,

            "stderr": (
                f"Execution timed out after "
                f"{timeout_seconds} seconds.\n"
                f"{stderr}"
            ),

            "language": language,

            "sandbox": "docker"
        }


    # ======================================================
    # GENERAL ERROR
    # ======================================================

    except Exception as error:

        return {

            "success": False,

            "stdout": "",

            "stderr": str(error),

            "language": language,

            "sandbox": "docker"
        }


    # ======================================================
    # CLEANUP
    # ======================================================

    finally:

        if temp_directory:

            try:

                shutil.rmtree(
                    temp_directory,
                    ignore_errors=True
                )

            except Exception:

                pass


# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================

def execute_python_code(
    code_string: str,
    timeout_seconds: int = 10,
    working_directory: str = None
) -> dict:
    """
    Backward-compatible Python execution function.

    Existing code using execute_python_code()
    will continue to work.
    """

    return execute_code(
        code=code_string,
        language="python",
        timeout_seconds=timeout_seconds,
        working_directory=working_directory
    )