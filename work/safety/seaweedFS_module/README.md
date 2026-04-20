# SeaweedFS Manager

SeaweedFS Filer를 데이터레이크로 활용하기 위한 파일 업로드/다운로드 도구.
Web UI와 CLI 스크립트 두 가지 방식을 제공한다.

## 주요 기능

- **Web UI** - 브라우저 기반 파일 탐색, 업로드, 다운로드 (드래그 앤 드롭 지원)
- **CLI 스크립트** - 커맨드라인 기반 대량 병렬 업로드/다운로드
- 멀티스레드 병렬 처리 및 실패 파일 자동 재시도
- 이어받기(resume) 지원

## 기술 스택

| 구성 요소 | 기술 |
|---|---|
| CLI 스크립트 | Python 3.10+, requests |
| Web Backend | FastAPI, uvicorn, httpx |
| Web Frontend | React, TypeScript, Vite |
| 스토리지 | SeaweedFS Filer |

## 프로젝트 구조

```
seaweedFS_module/
├── config.json.example                  # 설정 파일 예시
├── pyproject.toml                       # 프로젝트 메타데이터 및 의존성
├── requirements.txt                     # Python 의존성 (버전 범위)
├── requirements.lock                    # Python 의존성 (핀된 버전)
├── start.sh                             # Web UI 실행 스크립트
│
├── seaweed_upload_to_seaweedfs.py       # CLI: 로컬 -> SeaweedFS 업로드
├── seaweed_download_from_seaweedfs.py   # CLI: SeaweedFS -> 로컬 다운로드
├── organize_cases.py                    # 전처리: tar.gz 분류/압축해제
│
├── backend/                             # Web UI 백엔드 (FastAPI)
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── routers/                         # API 엔드포인트
│   │   ├── browse.py
│   │   ├── upload.py
│   │   ├── download.py
│   │   └── settings.py
│   └── services/                        # 비즈니스 로직
│       ├── seaweed_client.py
│       └── task_manager.py
│
└── frontend/                            # Web UI 프론트엔드 (React + Vite)
    ├── src/
    ├── package.json
    └── vite.config.ts
```

## 설치

### 사전 요구사항

- Python 3.10+
- Node.js (Web UI 사용 시)
- SeaweedFS Filer 접근 가능

### Python 의존성 설치 (uv 권장)

```bash
# uv 설치 (미설치 시)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 가상환경 생성 + 의존성 설치
uv sync
```

또는 pip으로 설치:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 프론트엔드 빌드 (Web UI 사용 시)

```bash
cd frontend && npm install && npm run build
```

> `frontend/dist/`가 존재하면 백엔드가 자동으로 정적 파일을 서빙한다.

### 설정 파일

```bash
cp config.json.example config.json
```

`config.json`에서 SeaweedFS Filer 주소를 설정한다:

```json
{
  "filer_url": "http://<FILER_HOST>:8888",
  "max_workers": 16,
  "retry_count": 3,
  "page_size": 100,
  "list_page_size": 1000,
  "timeout": 30
}
```

| 항목 | 설명 | 기본값 |
|---|---|---|
| `filer_url` | SeaweedFS Filer 주소 | - |
| `max_workers` | 동시 업로드/다운로드 스레드 수 | 16 |
| `retry_count` | 실패 시 재시도 횟수 | 3 |
| `page_size` | Web UI 파일 목록 페이지 크기 | 100 |
| `list_page_size` | CLI 파일 목록 조회 단위 | 1000 |
| `timeout` | HTTP 요청 타임아웃(초) | 30 |

## 사용법

### Web UI

```bash
# 개발 모드 (프론트/백엔드 동시 실행)
./start.sh

# 또는 uv로 백엔드만 실행 (프론트엔드 빌드 필요)
uv run seaweed-server
```

- Backend: http://localhost:8889
- Frontend (개발 모드): http://localhost:5173

### CLI - 업로드

```bash
python3 seaweed_upload_to_seaweedfs.py
```

스크립트 디렉토리 하위의 대상 폴더를 탐색하여 SeaweedFS Filer에 병렬 업로드한다.
실패 파일은 `upload_fail_{폴더명}.txt`에 기록된다.

### CLI - 다운로드

```bash
# 기본: ./download 폴더에 다운로드
python3 seaweed_download_from_seaweedfs.py

# 출력 경로 지정
python3 seaweed_download_from_seaweedfs.py -o /data/output

# 특정 원격 폴더만 다운로드
python3 seaweed_download_from_seaweedfs.py -f <folder_name>

# 동시 스레드 수 변경
python3 seaweed_download_from_seaweedfs.py -w 32
```

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `-o`, `--output` | `./download` | 다운로드 저장 경로 |
| `-f`, `--folder` | 전체 | 특정 원격 폴더만 다운로드 |
| `-w`, `--workers` | `16` | 동시 다운로드 스레드 수 |

### 전처리 - tar.gz 분류

```bash
python3 organize_cases.py
```

tar.gz 아카이브를 카테고리별로 분류/압축해제하여 SeaweedFS 업로드 전 데이터를 정리한다.

## 트러블슈팅

### Cannot assign requested address

대량 업로드/다운로드 시 로컬 포트가 고갈될 수 있다. `max_workers` 또는 `-w` 옵션으로 스레드 수를 줄여서 실행한다.

### SeaweedFS 연결 실패

```bash
curl -s http://<FILER_HOST>:8888/
```

### 실패 파일 재처리

실패한 파일은 `upload_fail_*.txt` / `download_fail_*.txt`에 기록되므로 해당 파일만 재처리하면 된다.
