"""업로드 라우터."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..config import load_config
from ..models import UploadRequest
from ..services.task_manager import task_manager

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/start")
async def start_upload(body: UploadRequest):
    cfg = load_config()
    task_id = task_manager.start_upload(cfg, body.local_dir, body.remote_dir, body.pattern)
    return {"task_id": task_id}


@router.get("/{task_id}/progress")
async def upload_progress(task_id: str):
    return StreamingResponse(
        task_manager.stream_progress(task_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/{task_id}/cancel")
async def cancel_upload(task_id: str):
    ok = task_manager.cancel(task_id)
    return {"cancelled": ok}
