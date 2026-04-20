#!/usr/bin/env python3
"""수용/불수용 tar.gz 파일에서 엔드포인트 파일을 추출하여
accept / non_accept 폴더에 플랫하게 저장하는 스크립트.

저장 형식: {카테고리}_{원본파일명}  (예: EP_01_장애인전용구역_20250801_1_abc123.jpg)
파일명 충돌 시: 1_{카테고리}_{원본파일명}, 2_{카테고리}_{원본파일명} ...
"""

import os
import shutil
import tarfile
import tempfile
import re
import glob
from collections import defaultdict

# 경로 설정
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "260410")
ACCEPT_DIR = os.path.join(SCRIPT_DIR, "accept")
NON_ACCEPT_DIR = os.path.join(SCRIPT_DIR, "non_accept")

# 파일명 패턴: EP_01_장애인전용구역_수용_250801-250805.tar.gz
PATTERN = re.compile(r"^(.+?)_(수용|불수용)_(\d{6}-\d{6})\.tar\.gz$")


def classify_and_extract():
    """tar.gz 파일을 수용/불수용으로 분류, 엔드포인트 파일만 플랫하게 저장한다."""
    tar_files = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.tar.gz")))

    if not tar_files:
        print(f"[ERROR] tar.gz 파일을 찾을 수 없습니다: {SOURCE_DIR}")
        return

    # 각 그룹별로 파일명 -> [(카테고리, 원본경로)] 매핑을 먼저 수집
    accept_files = {}   # dest_name -> src_path
    non_accept_files = {}
    accept_results = {}
    non_accept_results = {}

    # 파일명 충돌 카운터
    accept_name_count = defaultdict(int)
    non_accept_name_count = defaultdict(int)

    for tar_path in tar_files:
        filename = os.path.basename(tar_path)
        match = PATTERN.match(filename)
        if not match:
            print(f"[SKIP] 패턴 불일치: {filename}")
            continue

        category = match.group(1)       # e.g. EP_01_장애인전용구역
        accept_type = match.group(2)    # 수용 or 불수용
        date_range = match.group(3)

        if accept_type == "수용":
            dest_dir = ACCEPT_DIR
            name_count = accept_name_count
            results = accept_results
        else:
            dest_dir = NON_ACCEPT_DIR
            name_count = non_accept_name_count
            results = non_accept_results

        os.makedirs(dest_dir, exist_ok=True)

        print(f"[EXTRACT] {filename} -> {os.path.relpath(dest_dir, SCRIPT_DIR)}/")

        saved_files = []
        with tarfile.open(tar_path, "r:gz") as tar:
            members = [m for m in tar.getmembers() if m.isfile()]

            for member in members:
                original_name = os.path.basename(member.name)
                # 목적 파일명: 카테고리_원본파일명
                dest_name = f"{category}_{original_name}"

                # 파일명 충돌 처리
                if dest_name in name_count:
                    name_count[dest_name] += 1
                    dup_idx = name_count[dest_name]
                    dest_name = f"{dup_idx}_{dest_name}"
                else:
                    name_count[dest_name] = 0

                dest_path = os.path.join(dest_dir, dest_name)

                # 멤버를 임시로 추출 후 이동
                f = tar.extractfile(member)
                if f is not None:
                    with open(dest_path, "wb") as out:
                        shutil.copyfileobj(f, out)
                    saved_files.append(dest_name)

        results[category] = {
            "source": filename,
            "date_range": date_range,
            "file_count": len(saved_files),
            "files": saved_files,
        }

    # 리스트 파일 생성
    write_list_file(os.path.join(ACCEPT_DIR, "file_list.txt"), accept_results, "수용")
    write_list_file(
        os.path.join(NON_ACCEPT_DIR, "file_list.txt"), non_accept_results, "불수용"
    )

    total_accept = sum(r["file_count"] for r in accept_results.values())
    total_non_accept = sum(r["file_count"] for r in non_accept_results.values())
    print(f"\n[DONE] accept: {total_accept} files")
    print(f"[DONE] non_accept: {total_non_accept} files")


def write_list_file(path, results, label):
    """카테고리별 파일 목록을 텍스트 파일로 저장한다."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"=== {label} 파일 목록 ===\n")
        f.write(f"=== 총 카테고리 수: {len(results)} ===\n")
        f.write(
            f"=== 총 파일 수: {sum(r['file_count'] for r in results.values())} ===\n\n"
        )

        for category in sorted(results):
            info = results[category]
            f.write(f"{'='*70}\n")
            f.write(f"[{category}]\n")
            f.write(f"  원본 tar: {info['source']}\n")
            f.write(f"  기간: {info['date_range']}\n")
            f.write(f"  파일 수: {info['file_count']}\n")
            f.write(f"{'='*70}\n")
            for fname in sorted(info["files"]):
                f.write(f"  {fname}\n")
            f.write("\n")
    print(f"[LIST] {os.path.relpath(path, SCRIPT_DIR)} 생성 완료")


if __name__ == "__main__":
    classify_and_extract()
