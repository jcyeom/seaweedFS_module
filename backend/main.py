"""FastAPI 앱 엔트리포인트."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.staticfiles import StaticFiles

from .routers import browse, download, settings, upload

_static_dir = Path(__file__).resolve().parent / "static"

app = FastAPI(title="SeaweedFS Manager", version="0.1.0", redoc_url=None)

# 로컬 정적 파일 서빙 (ReDoc JS 번들 등)
app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


@app.get("/redoc", include_in_schema=False)
async def custom_redoc():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(settings.router)
app.include_router(browse.router)
app.include_router(upload.router)
app.include_router(download.router)

# 프론트엔드 빌드 결과물 서빙 (존재할 경우)
_frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="spa")


def run():
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8889, reload=True)


if __name__ == "__main__":
    run()
