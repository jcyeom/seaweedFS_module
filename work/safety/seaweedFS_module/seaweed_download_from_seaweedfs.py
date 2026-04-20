#!/usr/bin/env python3
"""SeaweedFS Filer에서 accept / non_accept 폴더의 파일을 다운로드하는 스크립트.

사용법:
    python3 download_from_seaweedfs.py                      # 기본 경로(./download)에 다운로드
    python3 download_from_seaweedfs.py -o /path/to/output   # 출력 경로 지정
    python3 download_from_seaweedfs.py -f accept             # accept만 다운로드
    python3 download_from_seaweedfs.py -f non_accept         # non_accept만 다운로드
"""

import argparse
import json
import os
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
REMOTE_FOLDERS = ["accept", "non_accept"]
LIST_PAGE_SIZE = _cfg.get("list_page_size", 1000)
MAX_WORKERS = _cfg.get("max_workers", 16)
RETRY_COUNT = _cfg.get("retry_count", 3)


def list_files(remote_dir):
    """SeaweedFS Filer에서 디렉토리 내 모든 파일 목록을 가져온다."""
    files = []
    last_filename = ""

    while True:
        url = f"{SEAWEED_FILER_URL}/{remote_dir}/"
        params = {"limit": LIST_PAGE_SIZE, "lastFileName": last_filename}
        resp = requests.get(url, params=params, headers={"Accept": "application/json"}, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        entries = data.get("Entries") or []
        for entry in entries:
            full_path = entry["FullPath"]
            filename = os.path.basename(full_path)
            file_size = entry.get("FileSize", 0)
            files.append({"name": filename, "size": file_size})

        if not data.get("ShouldDisplayLoadMore") or not entries:
            break

        last_filename = data.get("LastFileName", "")
        if not last_filename:
            break

    return files


def download_file(remote_dir, filename, local_dir):
    """단일 파일을 SeaweedFS에서 다운로드한다."""
    url = f"{SEAWEED_FILER_URL}/{remote_dir}/{filename}"
    local_path = os.path.join(local_dir, filename)

    # 이미 존재하면 스킵
    if os.path.exists(local_path):
        return True, filename, "skipped"

    for attempt in range(1, RETRY_COUNT + 1):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                return True, filename, None
            else:
                err = f"HTTP {resp.status_code}"
        except requests.RequestException as e:
            err = str(e)

        if attempt < RETRY_COUNT:
            time.sleep(1)

    return False, filename, err


def download_folder(remote_dir, output_root, max_workers=MAX_WORKERS):
    """원격 폴더의 모든 파일을 다운로드한다."""
    print(f"[{remote_dir}] 파일 목록 조회 중...")
    files = list_files(remote_dir)
    total = len(files)

    if total == 0:
        print(f"[{remote_dir}] 파일 없음")
        return

    total_size_mb = sum(f["size"] for f in files) / (1024 * 1024)
    print(f"[{remote_dir}] {total}개 파일 ({total_size_mb:.1f} MB) 다운로드 시작")

    local_dir = os.path.join(output_root, remote_dir)
    os.makedirs(local_dir, exist_ok=True)

    success_count = 0
    skip_count = 0
    fail_count = 0
    failed_files = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(download_file, remote_dir, f["name"], local_dir): f
            for f in files
        }

        for i, future in enumerate(as_completed(futures), 1):
            ok, filename, err = future.result()
            if ok:
                if err == "skipped":
                    skip_count += 1
                else:
                    success_count += 1
            else:
                fail_count += 1
                failed_files.append((filename, err))

            if i % 500 == 0 or i == total:
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                print(
                    f"  [{remote_dir}] {i}/{total} "
                    f"({success_count} new, {skip_count} skip, {fail_count} fail) "
                    f"{rate:.1f} files/s"
                )

    elapsed = time.time() - start_time
    print(
        f"[{remote_dir}] 완료: {success_count} 다운로드, "
        f"{skip_count} 스킵, {fail_count} 실패 ({elapsed:.1f}s)"
    )

    if failed_files:
        fail_log = os.path.join(output_root, f"download_fail_{remote_dir}.txt")
        with open(fail_log, "w", encoding="utf-8") as f:
            for fname, err in failed_files:
                f.write(f"{fname}\t{err}\n")
        print(f"  실패 목록: {fail_log}")


def main():
    parser = argparse.ArgumentParser(description="SeaweedFS에서 accept/non_accept 다운로드")
    parser.add_argument(
        "-o", "--output", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "download"),
        help="다운로드 저장 경로 (기본: ./download)",
    )
    parser.add_argument(
        "-f", "--folder", choices=["accept", "non_accept"],
        help="특정 폴더만 다운로드 (미지정 시 둘 다)",
    )
    parser.add_argument(
        "-w", "--workers", type=int, default=MAX_WORKERS,
        help=f"동시 다운로드 스레드 수 (기본: {MAX_WORKERS})",
    )
    args = parser.parse_args()

    workers = args.workers
    folders = [args.folder] if args.folder else REMOTE_FOLDERS
    output_root = args.output
    os.makedirs(output_root, exist_ok=True)

    print(f"SeaweedFS Filer: {SEAWEED_FILER_URL}")
    print(f"저장 경로: {output_root}")
    print(f"동시 스레드: {workers}\n")

    for folder in folders:
        download_folder(folder, output_root, workers)
        print()


if __name__ == "__main__":
    main()
