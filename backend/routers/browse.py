"""파일 목록 조회 / 이미지 프록시 라우터."""

from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import Response

from ..config import load_config
from ..models import FileListResponse, StatsResponse
from ..services import seaweed_client

router = APIRouter(prefix="/api/browse", tags=["browse"])


@router.get("/{folder}", response_model=FileListResponse)
async def list_files(
    folder: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    cfg = load_config()
    files, total = await seaweed_client.list_files(cfg, folder, page, page_size, category, search)
    return FileListResponse(folder=folder, total=total, page=page, page_size=page_size, files=files)


@router.get("/{folder}/stats", response_model=StatsResponse)
async def get_stats(folder: str):
    cfg = load_config()
    total, categories = await seaweed_client.get_stats(cfg, folder)
    return StatsResponse(folder=folder, total=total, categories=categories)


@router.get("/{folder}/preview/{filename}")
async def preview_image(folder: str, filename: str):
    cfg = load_config()
    content = await seaweed_client.proxy_image(cfg, folder, filename)
    return Response(content=content, media_type="image/jpeg")
