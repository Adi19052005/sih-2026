import os
import shutil
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from backend.agent import SovereignAgent
from backend.db import db
from backend.network_sentry import check_airgap_status


# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

WORKSPACE_DIR = os.path.join(
    PROJECT_ROOT,
    "workspace"
)

os.makedirs(
    WORKSPACE_DIR,
    exist_ok=True
)


# ==========================================================
# FASTAPI APPLICATION
# ==========================================================

app = FastAPI(
    title="Sovereign AI Workbench API",
    description="Fully Local Air-Gapped AI Workbench API",
    version="1.2.0"
)


# ==========================================================
# AGENT
# ==========================================================

agent = SovereignAgent()


# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
def root():

    return {
        "service": "Sovereign AI Workbench",
        "status": "RUNNING",
        "mode": "LOCAL_AIR_GAPPED"
    }


# ==========================================================
# SESSION LIST
# Used by Streamlit Session Selector
# ==========================================================

@app.get("/sessions")
def get_sessions():

    try:

        sessions = db.get_all_sessions()

        return {
            "session_count": len(sessions),
            "sessions": sessions
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================================
# CREATE NEW SESSION
# Used by Streamlit "New Session" button
# ==========================================================

@app.post("/sessions/new")
def create_new_session():

    try:

        session_id = db.create_session()

        session_workspace = os.path.join(
            WORKSPACE_DIR,
            f"session_{session_id}"
        )

        os.makedirs(
            session_workspace,
            exist_ok=True
        )

        return {
            "success": True,
            "session_id": session_id,
            "workspace": session_workspace
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================================
# CHAT
# ==========================================================

@app.post("/chat")
async def chat(
    prompt: str = Form(...),
    session_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):

    try:

        # --------------------------------------------------
        # CREATE / VERIFY SESSION
        # --------------------------------------------------

        if not session_id:

            session_id = db.create_session()

        elif not db.session_exists(session_id):

            db.create_session_with_id(session_id)

        # --------------------------------------------------
        # CREATE SESSION WORKSPACE
        # --------------------------------------------------

        session_workspace = os.path.abspath(
            os.path.join(
                WORKSPACE_DIR,
                f"session_{session_id}"
            )
        )

        os.makedirs(
            session_workspace,
            exist_ok=True
        )

        # --------------------------------------------------
        # HANDLE FILE UPLOAD
        # --------------------------------------------------

        file_path = None
        uploaded_file_name = None

        if file and file.filename:

            uploaded_file_name = os.path.basename(
                file.filename
            )

            file_path = os.path.abspath(
                os.path.join(
                    session_workspace,
                    uploaded_file_name
                )
            )

            # Security check
            if os.path.commonpath(
                [session_workspace, file_path]
            ) != session_workspace:

                raise HTTPException(
                    status_code=403,
                    detail="Invalid file path"
                )

            with open(
                file_path,
                "wb"
            ) as output_file:

                shutil.copyfileobj(
                    file.file,
                    output_file
                )

        # --------------------------------------------------
        # RUN LOCAL AGENT
        # --------------------------------------------------

        result = agent.run(
            prompt=prompt,
            session_id=session_id,
            file_path=file_path
        )

        # --------------------------------------------------
        # FETCH SESSION ARTIFACTS
        # --------------------------------------------------

        artifacts = db.get_session_artifacts(
            session_id
        )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return {
            "success": True,

            "session_id": session_id,

            "selected_model": result.get(
                "selected_model"
            ),

            "generated_code": result.get(
                "generated_code"
            ),

            "final_output": result.get(
                "final_output"
            ),

            "tool_result": result.get(
                "tool_result"
            ),

            "error_count": result.get(
                "error_count"
            ),

            "uploaded_file": uploaded_file_name,

            "uploaded_file_path": file_path,

            "artifacts": artifacts,

            "artifact_count": len(artifacts)
        }

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================================
# NETWORK SENTRY STATUS
# ==========================================================

@app.get("/sentry/status")
def sentry_status():

    try:

        return check_airgap_status()

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================================
# SESSION CHAT HISTORY
# ==========================================================

@app.get("/history/{session_id}")
def get_history(session_id: str):

    try:

        if not db.session_exists(session_id):

            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        history = db.get_session_history(
            session_id
        )

        return {
            "session_id": session_id,
            "message_count": len(history),
            "history": history
        }

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================================
# SESSION ARTIFACTS
# ==========================================================

@app.get("/artifacts/{session_id}")
def get_artifacts(session_id: str):

    try:

        if not db.session_exists(session_id):

            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        artifacts = db.get_session_artifacts(
            session_id
        )

        return {
            "session_id": session_id,
            "artifact_count": len(artifacts),
            "artifacts": artifacts
        }

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================================
# DOWNLOAD ARTIFACT
# ==========================================================

@app.get("/download/{session_id}/{file_name}")
def download_file(
    session_id: str,
    file_name: str
):

    try:

        # --------------------------------------------------
        # SANITIZE FILE NAME
        # --------------------------------------------------

        safe_file_name = os.path.basename(
            file_name
        )

        # --------------------------------------------------
        # SESSION WORKSPACE
        # --------------------------------------------------

        session_workspace = os.path.abspath(
            os.path.join(
                WORKSPACE_DIR,
                f"session_{session_id}"
            )
        )

        requested_file = os.path.abspath(
            os.path.join(
                session_workspace,
                safe_file_name
            )
        )

        # --------------------------------------------------
        # PREVENT PATH TRAVERSAL
        # --------------------------------------------------

        if os.path.commonpath(
            [session_workspace, requested_file]
        ) != session_workspace:

            raise HTTPException(
                status_code=403,
                detail="Invalid file path"
            )

        # --------------------------------------------------
        # VERIFY ARTIFACT IS REGISTERED
        # --------------------------------------------------

        artifacts = db.get_session_artifacts(
            session_id
        )

        artifact = next(
            (
                item
                for item in artifacts
                if item["file_name"] == safe_file_name
            ),
            None
        )

        if not artifact:

            raise HTTPException(
                status_code=404,
                detail="Artifact not registered"
            )

        # --------------------------------------------------
        # USE DATABASE FILE PATH
        # --------------------------------------------------

        database_file_path = os.path.abspath(
            artifact["file_path"]
        )

        if not os.path.exists(
            database_file_path
        ):

            raise HTTPException(
                status_code=404,
                detail="Artifact file does not exist"
            )

        # --------------------------------------------------
        # FINAL SECURITY CHECK
        # --------------------------------------------------

        if os.path.commonpath(
            [session_workspace, database_file_path]
        ) != session_workspace:

            raise HTTPException(
                status_code=403,
                detail="Invalid artifact location"
            )

        # --------------------------------------------------
        # RETURN FILE
        # --------------------------------------------------

        return FileResponse(
            path=database_file_path,
            filename=safe_file_name,
            media_type="application/octet-stream"
        )

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )