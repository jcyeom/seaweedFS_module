# SeaweedFS 데이터레이크 모듈 요약

## 개요

SeaweedFS Filer를 데이터레이크로 활용하기 위한 파일 업로드/다운로드 도구.
대량 파일을 SeaweedFS에 적재하고 필요 시 내려받을 수 있다.

## 제공 방식

| 방식 | 설명 |
|---|---|
| **Web UI** | 브라우저 기반 파일 탐색, 업로드, 다운로드 |
| **CLI 스크립트** | 커맨드라인 기반 대량 병렬 업로드/다운로드 |

## 주요 기능

- SeaweedFS Filer에 파일 업로드 (멀티스레드 병렬 처리)
- SeaweedFS Filer에서 파일 다운로드 (이어받기 지원)
- Web UI를 통한 디렉토리 탐색 및 파일 관리
- 실패 파일 자동 재시도 및 로그 기록

## 기술 스택

| 구성 요소 | 기술 |
|---|---|
| CLI 스크립트 | Python 3.10+, requests |
| Web Backend | FastAPI, uvicorn, httpx |
| Web Frontend | React, TypeScript, Vite |
| 스토리지 | SeaweedFS Filer |

## 파일 구성

```
seaweedFS_module/
├── config.json                          # SeaweedFS 접속 설정
├── seaweed_upload_to_seaweedfs.py       # CLI 업로드
├── seaweed_download_from_seaweedfs.py   # CLI 다운로드
├── start.sh                             # Web UI 실행
├── backend/                             # FastAPI 백엔드
└── frontend/                            # React 프론트엔드
```

## 실행 방법

### Web UI

```bash
./start.sh
# Backend:  http://localhost:8889
# Frontend: http://localhost:5173
```

### CLI

```bash
# 업로드
python3 seaweed_upload_to_seaweedfs.py

# 다운로드
python3 seaweed_download_from_seaweedfs.py -o ./download -w 16
```

## 설정

`config.json`에서 SeaweedFS Filer 주소, 스레드 수, 재시도 횟수 등을 설정한다.
상세 설정 항목은 `seaweed_README.md`를 참고.
