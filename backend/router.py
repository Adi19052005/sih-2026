import os
import re


class TaskRouter:
    """
    Smart model router for the Sovereign AI Workbench.

    Models:
    - qwen2.5:3b       -> General conversation and knowledge tasks
    - qwen2.5-coder:3b -> Programming/code tasks
    - qwen2.5vl:7b     -> Images, PDFs, OCR, vision tasks
    """

    VISION_MODEL = "qwen2.5vl:7b"
    CODER_MODEL = "qwen2.5-coder:3b"
    GENERAL_MODEL = "qwen2.5:3b"

    # ==========================================================
    # FILE EXTENSIONS
    # ==========================================================

    IMAGE_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
        ".gif"
    }

    PDF_EXTENSIONS = {
        ".pdf"
    }

    CODE_EXTENSIONS = {
        ".py",
        ".java",
        ".js",
        ".mjs",
        ".cjs",
        ".ts",
        ".tsx",
        ".jsx",
        ".cpp",
        ".cc",
        ".cxx",
        ".c",
        ".h",
        ".hpp",
        ".cs",
        ".go",
        ".rs",
        ".php",
        ".rb",
        ".html",
        ".css",
        ".sql"
    }

    TEXT_EXTENSIONS = {
        ".txt",
        ".md",
        ".json",
        ".csv",
        ".xml",
        ".yaml",
        ".yml"
    }

    # ==========================================================
    # VISION KEYWORDS
    # ==========================================================

    VISION_KEYWORDS = [
        "analyze this image",
        "analyse this image",
        "describe this image",
        "read this image",
        "what is in this image",
        "what is shown in this image",
        "what does this image contain",
        "what does this image consist of",
        "extract text from image",
        "ocr this image",
        "analyze screenshot",
        "analyse screenshot",
        "describe the screenshot",

        "analyze this pdf",
        "analyse this pdf",
        "read this pdf",
        "extract text from pdf",
        "ocr this document",
        "scanned document"
    ]

    # ==========================================================
    # CODING PATTERNS
    # ==========================================================

    CODING_PATTERNS = [

        # General code requests
        r"\bwrite code\b",
        r"\bcreate code\b",
        r"\bgenerate code\b",
        r"\bgive me code\b",
        r"\bprovide code\b",

        # Explicit language requests
        r"\bwrite (?:a )?(?:python|java|javascript|js|c\+\+|cpp|c) (?:program|code|script)\b",
        r"\bcreate (?:a )?(?:python|java|javascript|js|c\+\+|cpp|c) (?:program|code|script)\b",
        r"\bgenerate (?:a )?(?:python|java|javascript|js|c\+\+|cpp|c) (?:program|code|script)\b",

        # "Program in Java/Python"
        r"\bwrite (?:a )?program in (?:python|java|javascript|js|c\+\+|cpp|c)\b",
        r"\bcreate (?:a )?program in (?:python|java|javascript|js|c\+\+|cpp|c)\b",

        # Problem solving
        r"\bsolve .* in (?:python|java|javascript|js|c\+\+|cpp|c)\b",
        r"\bimplement .* in (?:python|java|javascript|js|c\+\+|cpp|c)\b",

        # Debugging
        r"\bdebug (?:this )?code\b",
        r"\bfix (?:this )?code\b",
        r"\brefactor (?:this )?code\b",
        r"\bdebug my code\b",
        r"\bfix my code\b",

        # Existing code
        r"\bexplain this code\b",
        r"\bexplain my code\b",
        r"\breview this code\b",
        r"\banalyze this code\b",

        # Execution
        r"\brun (?:this )?(?:code|program|script)\b",
        r"\bexecute (?:this )?(?:code|program|script)\b",
        r"\bcompile (?:this )?(?:code|program)\b",

        # Errors
        r"\bsyntax error\b",
        r"\bsegmentation fault\b",
        r"\bcompiler error\b",
        r"\bruntime error\b",

        # Competitive programming
        r"\bsolve this problem\b.*\b(?:code|solution|implement)\b",
        r"\bleetcode\b.*\b(?:code|solution|implement)\b"
    ]

    # ==========================================================
    # ROUTER
    # ==========================================================

    def route(
        self,
        prompt: str,
        file_path: str = None,
        has_file: bool = False
    ) -> str:

        prompt_lower = (
            prompt.lower().strip()
            if prompt
            else ""
        )

        # ======================================================
        # PRIORITY 1: ACTUAL FILE TYPE
        # ======================================================

        if file_path:

            extension = os.path.splitext(
                file_path
            )[1].lower()

            # Images always go to Vision model
            if extension in self.IMAGE_EXTENSIONS:
                return self.VISION_MODEL

            # PDFs go to Vision model
            if extension in self.PDF_EXTENSIONS:
                return self.VISION_MODEL

            # Source code files go to Coder
            if extension in self.CODE_EXTENSIONS:
                return self.CODER_MODEL

            # Text/data files go to General
            if extension in self.TEXT_EXTENSIONS:
                return self.GENERAL_MODEL

            # Unknown files
            return self.GENERAL_MODEL

        # ======================================================
        # PRIORITY 2: VISION REQUEST
        # ======================================================

        if any(
            keyword in prompt_lower
            for keyword in self.VISION_KEYWORDS
        ):
            return self.VISION_MODEL

        # ======================================================
        # PRIORITY 3: EXPLICIT CODING REQUEST
        # ======================================================

        for pattern in self.CODING_PATTERNS:

            if re.search(
                pattern,
                prompt_lower,
                re.IGNORECASE | re.DOTALL
            ):
                return self.CODER_MODEL

        # ======================================================
        # PRIORITY 4: BACKWARD COMPATIBILITY
        # ======================================================

        if has_file:
            return self.GENERAL_MODEL

        # ======================================================
        # PRIORITY 5: GENERAL MODEL
        # ======================================================

        return self.GENERAL_MODEL