#!/usr/bin/env python3
"""accept / non_accept 폴더의 파일을 SeaweedFS Filer에 업로드하는 스크립트."""

import json
import os
import sys
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# 설정
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

def _load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

_cfg = _load_config()
SEAWEED_FILER_URL = _cfg["filer_url"]
FOLDERS = {
    "accept": os.path.join(SCRIPT_DIR, "accept"),
    "non_accept": os.path.join(SCRIPT_DIR, "non_accept"),
}
MAX_WORKERS = _cfg.get("max_workers", 16)
RETRY_COUNT = _cfg.get("retry_count", 3)


def upload_file(local_path, remote_dir):
    """단일 파일을 SeaweedFS Filer에 업로드한다."""
    filename = os.path.basename(local_path)
    url = f"{SEAWEED_FILER_URL}/{remote_dir}/{filename}"

    for attempt in range(1, RETRY_COUNT + 1):
        try:
            with open(local_path, "rb") as f:
                resp = requests.post(url, files={"file": (filename, f)}, timeout=30)
            if resp.status_code in (200, 201):
                return True, filename, None
            else:
                err = f"HTTP {resp.status_code}: {resp.text[:100]}"
        except requests.RequestException as e:
            err = str(e)

        if attempt < RETRY_COUNT:
            time.sleep(1)

    return False, filename, err


def upload_folder(folder_name, folder_path):
    """폴더 내 모든 파일을 병렬로 업로드한다."""
    files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(".jpg")
    ]

    total = len(files)
    if total == 0:
        print(f"[{folder_name}] 업로드할 파일 없음")
        return

    print(f"[{folder_name}] {total}개 파일 업로드 시작 (스레드: {MAX_WORKERS})")
    success_count = 0
    fail_count = 0
    failed_files = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(upload_file, fp, folder_name): fp for fp in files
        }

        for i, future in enumerate(as_completed(futures), 1):
            ok, filename, err = future.result()
            if ok:
                success_count += 1
            else:
                fail_count += 1
                failed_files.append((filename, err))

            if i % 500 == 0 or i == total:
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                print(
                    f"  [{folder_name}] {i}/{total} "
                    f"({success_count} ok, {fail_count} fail) "
                    f"{rate:.1f} files/s"
                )

    elapsed = time.time() - start_time
    print(
        f"[{folder_name}] 완료: {success_count} 성공, {fail_count} 실패 "
        f"({elapsed:.1f}s)"
    )

    if failed_files:
        fail_log = os.path.join(SCRIPT_DIR, f"upload_fail_{folder_name}.txt")
        with open(fail_log, "w", encoding="utf-8") as f:
            for fname, err in failed_files:
                f.write(f"{fname}\t{err}\n")
        print(f"  실패 목록: {fail_log}")


def main():
    print(f"SeaweedFS Filer: {SEAWEED_FILER_URL}")
    print(f"동시 스레드: {MAX_WORKERS}\n")

    for folder_name, folder_path in FOLDERS.items():
        if not os.path.isdir(folder_path):
            print(f"[ERROR] 폴더 없음: {folder_path}")
            continue
        upload_folder(folder_name, folder_path)
        print()


if __name__ == "__main__":
    main()
