"""백그라운드 업로드/다운로드 작업 관리."""

import asyncio
import glob
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from uuid import uuid4

from ..models import AppConfig, TaskState
from . import seaweed_client


class TaskManager:
    def __init__(self) -> None:
        self._tasks: Dict[str, TaskState] = {}
        self._cancel_flags: Dict[str, threading.Event] = {}
        self._lock = threading.Lock()

    def get(self, task_id: str) -> Optional[TaskState]:
        return self._tasks.get(task_id)

    def _update(self, task_id: str, **kwargs) -> None:
        with self._lock:
            state = self._tasks[task_id]
            for k, v in kwargs.items():
                setattr(state, k, v)

    # ── Upload ──────────────────────────────────────────────────────────────

    def start_upload(self, cfg: AppConfig, local_dir: str, remote_dir: str, pattern: str) -> str:
        task_id = uuid4().hex[:8]
        self._tasks[task_id] = TaskState(task_id=task_id, task_type="upload")
        self._cancel_flags[task_id] = threading.Event()
        t = threading.Thread(target=self._run_upload, args=(task_id, cfg, local_dir, remote_dir, pattern), daemon=True)
        t.start()
        return task_id

    def _run_upload(self, task_id: str, cfg: AppConfig, local_dir: str, remote_dir: str, pattern: str) -> None:
        files = sorted(glob.glob(os.path.join(local_dir, pattern)))
        total = len(files)
        self._update(task_id, status="running", total=total)

        if total == 0:
            self._update(task_id, status="completed")
            return

        cancel = self._cancel_flags[task_id]
        completed = 0
        failed = 0
        errors: List[str] = []
        start = time.time()

        with ThreadPoolExecutor(max_workers=cfg.max_workers) as pool:
            futures = {pool.submit(seaweed_client.upload_single_file, cfg, fp, remote_dir): fp for fp in files}
            for future in as_completed(futures):
                if cancel.is_set():
                    pool.shutdown(wait=False, cancel_futures=True)
                    self._update(task_id, status="cancelled")
                    return

                ok, err = future.result()
                if ok:
                    completed += 1
                else:
                    failed += 1
                    if len(errors) < 50:
                        errors.append("{}: {}".format(os.path.basename(futures[future]), err))

                elapsed = time.time() - start
                rate = (completed + failed) / elapsed if elapsed > 0 else 0
                self._update(task_id, completed=completed, failed=failed, rate=round(rate, 1), elapsed=round(elapsed, 1), errors=errors)

        seaweed_client.invalidate_cache(remote_dir)
        self._update(task_id, status="completed")

    # ── Download ────────────────────────────────────────────────────────────

    def start_download(
        self, cfg: AppConfig, remote_dir: str, local_dir: str,
        category: Optional[str], skip_existing: bool, filenames: List[str],
    ) -> str:
        task_id = uuid4().hex[:8]
        self._tasks[task_id] = TaskState(task_id=task_id, task_type="download")
        self._cancel_flags[task_id] = threading.Event()
        t = threading.Thread(
            target=self._run_download,
            args=(task_id, cfg, remote_dir, local_dir, skip_existing, filenames),
            daemon=True,
        )
        t.start()
        return task_id

    def _run_download(
        self, task_id: str, cfg: AppConfig, remote_dir: str, local_dir: str,
        skip_existing: bool, filenames: List[str],
    ) -> None:
        os.makedirs(local_dir, exist_ok=True)
        total = len(filenames)
        self._update(task_id, status="running", total=total)

        if total == 0:
            self._update(task_id, status="completed")
            return

        cancel = self._cancel_flags[task_id]
        completed = 0
        failed = 0
        skipped = 0
        errors: List[str] = []
        start = time.time()

        with ThreadPoolExecutor(max_workers=cfg.max_workers) as pool:
            futures = {
                pool.submit(seaweed_client.download_single_file, cfg, remote_dir, fn, local_dir, skip_existing): fn
                for fn in filenames
            }
            for future in as_completed(futures):
                if cancel.is_set():
                    pool.shutdown(wait=False, cancel_futures=True)
                    self._update(task_id, status="cancelled")
                    return

                ok, err, was_skipped = future.result()
                if ok:
                    if was_skipped:
                        skipped += 1
                    else:
                        completed += 1
                else:
                    failed += 1
                    if len(errors) < 50:
                        errors.append("{}: {}".format(futures[future], err))

                elapsed = time.time() - start
                rate = (completed + failed + skipped) / elapsed if elapsed > 0 else 0
                self._update(
                    task_id, completed=completed, failed=failed, skipped=skipped,
                    rate=round(rate, 1), elapsed=round(elapsed, 1), errors=errors,
                )

        self._update(task_id, status="completed")

    # ── Cancel ──────────────────────────────────────────────────────────────

    def cancel(self, task_id: str) -> bool:
        flag = self._cancel_flags.get(task_id)
        if flag:
            flag.set()
            return True
        return False

    # ── SSE ─────────────────────────────────────────────────────────────────

    async def stream_progress(self, task_id: str):
        while True:
            state = self._tasks.get(task_id)
            if state is None:
                yield 'data: {"error": "task not found"}\n\n'
                return
            yield "data: {}\n\n".format(state.model_dump_json())
            if state.status in ("completed", "cancelled", "failed"):
                return
            await asyncio.sleep(0.5)


task_manager = TaskManager()
