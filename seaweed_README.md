# SeaweedFS 데이터레이크 업로드/다운로드 도구

SeaweedFS Filer를 데이터레이크로 활용하기 위한 파일 업로드/다운로드 도구.
Web UI와 CLI 스크립트 두 가지 방식을 제공한다.

## 프로젝트 구성

```
seaweedFS_module/
├── seaweed_README.md                    # 본 문서
├── config.json                          # SeaweedFS 접속 설정 (.gitignore)
├── config.json.example                  # 설정 파일 예시
├── pyproject.toml                       # 프로젝트 메타데이터 및 의존성
├── requirements.txt                     # Python 의존성 (버전 범위)
├── requirements.lock                    # Python 의존성 (핀된 버전)
├── start.sh                             # Web UI 실행 스크립트
│
├── seaweed_upload_to_seaweedfs.py       # CLI: 로컬 -> SeaweedFS 업로드
├── seaweed_download_from_seaweedfs.py   # CLI: SeaweedFS -> 로컬 다운로드
├── upload_to_seaweedfs.py               # CLI: 업로드 (260410 원본)
├── organize_cases.py                    # 전처리: tar.gz 분류/압축해제
├── organize_cases.md                    # 전처리 스크립트 설명
├── summary.md                           # 프로젝트 요약
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
└── frontend/                            # Web UI 프론트엔드 (React + Vite)
```

## 사전 준비

### 의존성 설치 (uv 권장)

```bash
# uv 설치 (미설치 시)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 가상환경 생성 + 의존성 설치
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

또는 pip으로 설치:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 프론트엔드 (Web UI 사용 시)

```bash
cd frontend && npm install && npm run build
```

> `frontend/dist/`가 존재하면 백엔드가 자동으로 정적 파일을 서빙한다.
> 개발 모드에서는 `start.sh`로 프론트/백엔드를 동시에 실행할 수 있다.

### 설정 파일

`config.json.example`을 복사하여 `config.json`을 생성하고, SeaweedFS Filer 주소를 입력한다.

```bash
cp config.json.example config.json
```

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

---

## 1. Web UI

브라우저에서 SeaweedFS의 파일을 탐색, 업로드, 다운로드할 수 있는 웹 인터페이스.

### 실행

```bash
./start.sh
```

- Backend: http://localhost:8889
- Frontend: http://localhost:5173

### 주요 기능

- 디렉토리 탐색 및 파일 목록 조회
- 파일 업로드 (드래그 앤 드롭 지원)
- 파일 다운로드
- SeaweedFS 접속 설정 변경

---

## 2. CLI 스크립트

### 업로드 (seaweed_upload_to_seaweedfs.py)

로컬 디렉토리의 파일을 SeaweedFS Filer에 병렬 업로드한다.

```bash
python3 seaweed_upload_to_seaweedfs.py
```

#### 동작 방식

1. 스크립트 디렉토리 하위의 대상 폴더를 탐색
2. 각 파일을 SeaweedFS Filer에 POST (multipart/form-data)
3. 멀티스레드 병렬 업로드
4. 실패 시 설정된 횟수만큼 재시도
5. 최종 실패 파일은 `upload_fail_{폴더명}.txt`에 기록

#### 출력 예시

```
SeaweedFS Filer: http://10.252.219.219:8888
동시 스레드: 16

[my_data] 10000개 파일 업로드 시작 (스레드: 16)
  [my_data] 500/10000 (500 ok, 0 fail) 450.0 files/s
  ...
[my_data] 완료: 10000 성공, 0 실패 (22.3s)
```

### 다운로드 (seaweed_download_from_seaweedfs.py)

SeaweedFS Filer에 저장된 파일을 로컬로 병렬 다운로드한다.

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

#### 명령줄 옵션

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `-o`, `--output` | `./download` | 다운로드 저장 경로 |
| `-f`, `--folder` | 전체 | 특정 원격 폴더만 다운로드 |
| `-w`, `--workers` | `16` | 동시 다운로드 스레드 수 |

#### 동작 방식

1. SeaweedFS Filer API로 파일 목록 조회 (페이지네이션)
2. 로컬에 이미 존재하는 파일은 스킵 (이어받기 지원)
3. 멀티스레드 병렬 다운로드
4. 실패 시 설정된 횟수만큼 재시도
5. 최종 실패 파일은 `download_fail_{폴더명}.txt`에 기록

---

## SeaweedFS Filer API 참고

### 파일 업로드

```
POST http://<FILER_HOST>:8888/{remote_dir}/{filename}
Content-Type: multipart/form-data

file=@local_file
```

- 성공 응답: `201 Created`
- 응답 본문: `{"name": "filename.ext", "size": 186618}`

### 파일 목록 조회

```
GET http://<FILER_HOST>:8888/{remote_dir}/?limit=1000&lastFileName=
Accept: application/json
```

응답 구조:

```json
{
  "Path": "/my_data",
  "Entries": [
    {
      "FullPath": "/my_data/sample_file.jpg",
      "FileSize": 350887
    }
  ],
  "ShouldDisplayLoadMore": true,
  "LastFileName": "sample_file.jpg"
}
```

### 파일 다운로드

```
GET http://<FILER_HOST>:8888/{remote_dir}/{filename}
```

---

## 트러블슈팅

### Cannot assign requested address

대량 업로드/다운로드 시 로컬 포트가 고갈될 수 있다. 스레드 수를 줄여서 실행한다.

```bash
python3 seaweed_upload_to_seaweedfs.py      # config.json의 max_workers를 줄임
python3 seaweed_download_from_seaweedfs.py -w 8
```

실패한 파일은 `upload_fail_*.txt` / `download_fail_*.txt`에 기록되므로 해당 파일만 재처리하면 된다.

### SeaweedFS 연결 실패

```bash
# Filer 상태 확인
curl -s http://<FILER_HOST>:8888/
```

### 파일 존재 여부 확인

```bash
# 특정 파일 확인
curl -I http://<FILER_HOST>:8888/<remote_dir>/<filename>

# 폴더 파일 수 확인
curl -s "http://<FILER_HOST>:8888/<remote_dir>/?limit=1" \
  -H "Accept: application/json" | python3 -m json.tool
```

---

## 의존성 관리

### 파일 구성

| 파일 | 용도 |
|---|---|
| `pyproject.toml` | 프로젝트 메타데이터 및 의존성 선언 (uv/pip 공용) |
| `requirements.txt` | 최소 의존성 목록 (버전 범위) |
| `requirements.lock` | 핀된 전체 의존성 (재현 가능한 배포용) |

### 의존성 추가/변경 시

```bash
# 1. pyproject.toml의 dependencies에 패키지 추가
# 2. requirements.txt에도 동일하게 반영
# 3. 설치 후 lock 파일 갱신
uv pip install -r requirements.txt
uv pip freeze > requirements.lock
```

### 배포 환경에서 설치

```bash
# 정확히 동일한 버전으로 설치 (권장)
uv pip install -r requirements.lock

# 또는 최신 호환 버전으로 설치
uv pip install -r requirements.txt
```
