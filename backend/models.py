"""Pydantic 스키마 정의."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# ── Config ──────────────────────────────────────────────────────────────────

class AppConfig(BaseModel):
    filer_url: str = ""
    max_workers: int = 16
    retry_count: int = 3
    page_size: int = 100
    list_page_size: int = 1000
    timeout: int = 30


class AppConfigUpdate(BaseModel):
    filer_url: Optional[str] = None
    max_workers: Optional[int] = None
    retry_count: Optional[int] = None
    page_size: Optional[int] = None
    list_page_size: Optional[int] = None
    timeout: Optional[int] = None


# ── File ────────────────────────────────────────────────────────────────────

class FileEntry(BaseModel):
    name: str
    size: int
    category: str


class FileListResponse(BaseModel):
    folder: str
    total: int
    page: int
    page_size: int
    files: List[FileEntry]


class CategoryStat(BaseModel):
    category: str
    count: int


class StatsResponse(BaseModel):
    folder: str
    total: int
    categories: List[CategoryStat]


# ── Task ────────────────────────────────────────────────────────────────────

class TaskState(BaseModel):
    task_id: str
    task_type: Literal["upload", "download"]
    status: Literal["pending", "running", "completed", "cancelled", "failed"] = "pending"
    total: int = 0
    completed: int = 0
    failed: int = 0
    skipped: int = 0
    rate: float = 0.0
    elapsed: float = 0.0
    errors: List[str] = Field(default_factory=list)


class UploadRequest(BaseModel):
    local_dir: str
    remote_dir: str = "accept"
    pattern: str = "*.jpg"


class DownloadRequest(BaseModel):
    remote_dir: str = "accept"
    local_dir: str
    category: Optional[str] = None
    skip_existing: bool = True


class ConnectionTestResult(BaseModel):
    ok: bool
    version: str = ""
    error: str = ""
