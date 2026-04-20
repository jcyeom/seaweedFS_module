"""설정 조회/수정 라우터."""

from fastapi import APIRouter

from ..config import load_config, update_config
from ..models import AppConfig, AppConfigUpdate, ConnectionTestResult
from ..services import seaweed_client

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=AppConfig)
async def get_settings():
    return load_config()


@router.put("", response_model=AppConfig)
async def put_settings(body: AppConfigUpdate):
    return update_config(body)


@router.get("/test", response_model=ConnectionTestResult)
async def test_connection():
    cfg = load_config()
    ok, info = await seaweed_client.test_connection(cfg)
    if ok:
        return ConnectionTestResult(ok=True, version=info)
    return ConnectionTestResult(ok=False, error=info)
