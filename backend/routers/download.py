"""다운로드 라우터."""

import io
import zipfile
from typing import List

import httpx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..config import load_config
from ..models import DownloadRequest
from ..services import seaweed_client
from ..services.task_manager import task_manager

router = APIRouter(prefix="/api/download", tags=["download"])


@router.post("/start")
async def start_download(body: DownloadRequest):
    cfg = load_config()

    # 파일 목록 가져오기 (카테고리 필터 적용)
    idx = await seaweed_client.get_file_index(cfg, body.remote_dir)
    if body.category:
        indices = idx.by_category.get(body.category, [])
        filenames = [idx.entries[i].name for i in indices]
    else:
        filenames = [e.name for e in idx.entries]

    task_id = task_manager.start_download(
        cfg, body.remote_dir, body.local_dir,
        body.category, body.skip_existing, filenames,
    )
    return {"task_id": task_id, "file_count": len(filenames)}


@router.get("/{task_id}/progress")
async def download_progress(task_id: str):
    return StreamingResponse(
        task_manager.stream_progress(task_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/{task_id}/cancel")
async def cancel_download(task_id: str):
    ok = task_manager.cancel(task_id)
    return {"cancelled": ok}
