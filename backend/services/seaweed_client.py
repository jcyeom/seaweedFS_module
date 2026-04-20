"""SeaweedFS Filer HTTP 클라이언트."""

import os
import re
import time
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import httpx

from ..models import AppConfig, FileEntry, CategoryStat

_CATEGORY_RE = re.compile(r"^([A-Z]+_\d+)")


def extract_category(filename: str) -> str:
    m = _CATEGORY_RE.match(filename)
    return m.group(1) if m else "unknown"


# ── 메모리 캐시 ──────────────────────────────────────────────────────────────

class _FolderCache:
    def __init__(self) -> None:
        self.entries: List[FileEntry] = []
        self.by_category: Dict[str, List[int]] = {}
        self.updated_at: float = 0.0


_cache: Dict[str, _FolderCache] = {}
_CACHE_TTL = 60.0


def invalidate_cache(folder: Optional[str] = None) -> None:
    if folder:
        _cache.pop(folder, None)
    else:
        _cache.clear()


# ── 파일 목록 ────────────────────────────────────────────────────────────────

async def _fetch_all_files(cfg: AppConfig, folder: str) -> List[FileEntry]:
    entries: List[FileEntry] = []
    last = ""
    async with httpx.AsyncClient(timeout=cfg.timeout) as client:
        while True:
            resp = await client.get(
                f"{cfg.filer_url}/{folder}/",
                params={"limit": cfg.list_page_size, "lastFileName": last},
                headers={"Accept": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
            for e in data.get("Entries") or []:
                name = os.path.basename(e["FullPath"])
                entries.append(FileEntry(
                    name=name,
                    size=e.get("FileSize", 0),
                    category=extract_category(name),
                ))
            if not data.get("ShouldDisplayLoadMore"):
                break
            last = data.get("LastFileName", "")
            if not last:
                break
    return entries


async def get_file_index(cfg: AppConfig, folder: str) -> _FolderCache:
    cached = _cache.get(folder)
    if cached and (time.time() - cached.updated_at) < _CACHE_TTL:
        return cached

    entries = await _fetch_all_files(cfg, folder)
    fc = _FolderCache()
    fc.entries = entries
    by_cat: Dict[str, List[int]] = defaultdict(list)
    for i, e in enumerate(entries):
        by_cat[e.category].append(i)
    fc.by_category = dict(by_cat)
    fc.updated_at = time.time()
    _cache[folder] = fc
    return fc


async def list_files(
    cfg: AppConfig,
    folder: str,
    page: int = 1,
    page_size: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> Tuple[List[FileEntry], int]:
    idx = await get_file_index(cfg, folder)

    if category:
        indices = idx.by_category.get(category, [])
        filtered = [idx.entries[i] for i in indices]
    else:
        filtered = idx.entries

    if search:
        search_lower = search.lower()
        filtered = [e for e in filtered if search_lower in e.name.lower()]

    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    return filtered[start:end], total


async def get_stats(cfg: AppConfig, folder: str) -> Tuple[int, List[CategoryStat]]:
    idx = await get_file_index(cfg, folder)
    stats = [
        CategoryStat(category=cat, count=len(indices))
        for cat, indices in sorted(idx.by_category.items())
    ]
    return len(idx.entries), stats


# ── 단일 파일 작업 ───────────────────────────────────────────────────────────

async def proxy_image(cfg: AppConfig, folder: str, filename: str) -> bytes:
    async with httpx.AsyncClient(timeout=cfg.timeout) as client:
        resp = await client.get(f"{cfg.filer_url}/{folder}/{filename}")
        resp.raise_for_status()
        return resp.content


async def test_connection(cfg: AppConfig) -> Tuple[bool, str]:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(cfg.filer_url)
            text = resp.text
            m = re.search(r"SeaweedFS Filer ([^<]+)", text)
            version = m.group(1).strip() if m else "unknown"
            return True, version
    except Exception as e:
        return False, str(e)


def upload_single_file(cfg: AppConfig, local_path: str, remote_dir: str) -> Tuple[bool, str]:
    """동기 업로드 (ThreadPoolExecutor용)."""
    filename = os.path.basename(local_path)
    url = f"{cfg.filer_url}/{remote_dir}/{filename}"
    for attempt in range(cfg.retry_count):
        try:
            with open(local_path, "rb") as f:
                resp = httpx.post(url, files={"file": (filename, f)}, timeout=cfg.timeout)
            if resp.status_code in (200, 201):
                return True, ""
            err = f"HTTP {resp.status_code}"
        except Exception as e:
            err = str(e)
        if attempt < cfg.retry_count - 1:
            time.sleep(1)
    return False, err


def download_single_file(
    cfg: AppConfig, remote_dir: str, filename: str, local_dir: str, skip_existing: bool
) -> Tuple[bool, str, bool]:
    """동기 다운로드 (ThreadPoolExecutor용). 반환: (성공, 에러, 스킵여부)"""
    local_path = os.path.join(local_dir, filename)
    if skip_existing and os.path.exists(local_path):
        return True, "", True

    url = f"{cfg.filer_url}/{remote_dir}/{filename}"
    for attempt in range(cfg.retry_count):
        try:
            resp = httpx.get(url, timeout=cfg.timeout)
            if resp.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                return True, "", False
            err = f"HTTP {resp.status_code}"
        except Exception as e:
            err = str(e)
        if attempt < cfg.retry_count - 1:
            time.sleep(1)
    return False, err, False
