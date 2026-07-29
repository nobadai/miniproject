# 프로젝트 초기 구성 안내

## 1. 문서 목적

이 문서는 프로젝트의 초기 개발 환경과 공통 골격을 설명한다.

현재 프로젝트에는 투자 사기 분석, 보이스피싱 분석, 뉴스 분석 등의 실제 서비스 기능이 없다. 실제 API Endpoint, 화면, Database Table, Seed 데이터도 아직 정의하지 않았다. 팀원은 기능을 추가하기 전에 `PROJECT_RULES.md`와 이 문서를 함께 확인해야 한다.

## 2. 기술 구성

| 영역 | 기술 |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | Python 3.12, FastAPI, Uvicorn |
| Database | PostgreSQL 18, pgvector |
| Backend Database Driver | psycopg |
| Backend Package Manager | uv |
| Frontend Package Manager | npm |
| Container | Docker, Docker Compose |
| CI/CD | GitHub Actions 사용 예정 |

Redis와 Kafka는 사용하지 않는다.

## 3. 전체 디렉터리 구조

```text
project-root/
├── frontend/
│   ├── app/                 # Next.js App Router
│   ├── components/          # 재사용 가능한 UI Component
│   ├── services/            # Backend API 통신
│   ├── types/               # Frontend 공통 Type
│   ├── utils/               # Domain 비종속 Utility
│   ├── public/              # 정적 Resource
│   ├── .env                 # Frontend 실제 환경변수, Git 제외
│   ├── .env.example         # Frontend 환경변수 Template
│   ├── Dockerfile
│   ├── package.json
│   └── package-lock.json
├── backend/
│   ├── app/
│   │   ├── routers/         # HTTP Endpoint
│   │   ├── services/        # Business Logic
│   │   ├── repositories/    # Pure SQL 기반 Database 접근
│   │   ├── models/          # Database 단위 Model이 필요할 때 사용
│   │   ├── schemas/         # Pydantic Request/Response Schema
│   │   ├── clients/         # 외부 Service 연결
│   │   ├── core/            # Settings와 FastAPI 초기화
│   │   └── main.py          # ASGI Application 진입점
│   ├── .env                 # Backend 실제 환경변수, Git 제외
│   ├── .env.example         # Backend 환경변수 Template
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── uv.lock
├── database/
│   ├── schemas/             # 최초 Database 구조 SQL
│   ├── migrations/          # Database 변경 SQL
│   └── seeds/               # 개발 및 Test Seed SQL
├── docs/                    # 프로젝트 문서
├── .github/
│   ├── ISSUE_TEMPLATE/      # Issue Template
│   └── workflows/           # GitHub Actions Workflow 위치
├── compose.yml
├── PROJECT_RULES.md
└── README.md
```

## 4. 계층별 책임

Backend의 기본 호출 흐름은 다음과 같다.

```text
routers → services → repositories → PostgreSQL
                    └→ clients
```

- `routers`: HTTP 요청 수신, Pydantic 검증, Service 호출, 공통 응답 반환
- `services`: 핵심 Business Logic과 Repository/Client 조합
- `repositories`: Pure SQL 작성 및 Database 접근
- `schemas`: API Request/Response 계약
- `clients`: 외부 API, AI, OCR, STT 연결
- `core`: 환경설정, FastAPI 초기화, Router 자동 등록

Router에서 SQL을 직접 실행하거나 Service에서 psycopg를 직접 호출하지 않는다. Database 접근은 `repositories/`에 둔다.

## 5. 환경변수 구성

### 5.1 환경 파일 정책

Frontend와 Backend는 환경 파일을 분리한다.

```text
frontend/.env
frontend/.env.example
backend/.env
backend/.env.example
```

실제 `.env` 두 파일은 Git에서 제외한다. `.env.example`에는 변수 이름과 공개 가능한 기본값만 작성하며 실제 Password, Token, API Key를 작성하지 않는다.

새 환경을 준비할 때 다음 명령으로 Template을 복사한다.

```powershell
Copy-Item frontend/.env.example frontend/.env
Copy-Item backend/.env.example backend/.env
```

### 5.2 Frontend 환경변수

현재 Frontend가 사용하는 환경변수는 다음 하나뿐이다.

```dotenv
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

`NEXT_PUBLIC_` 변수는 Browser Bundle에 포함되는 공개값이다. API Key, Database Password, Token 등의 Secret에는 절대 사용하지 않는다.

### 5.3 Backend 환경변수

```dotenv
# 애플리케이션
APP_NAME=
APP_ENV=
APP_DEBUG=
CORS_ORIGINS=

# PostgreSQL
POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

# 외부 API
OPENAI_API_KEY=
```

`POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`는 Backend Settings가 읽고 psycopg 연결정보로 전달한다.

- Local Backend에서 Docker PostgreSQL에 접근: `POSTGRES_HOST=localhost`
- Docker Backend에서 Compose PostgreSQL에 접근: Compose가 `POSTGRES_HOST=database`로 Override

Container 사이의 통신에서 `localhost`를 사용하면 안 된다.

### 5.4 Settings 초기화

`backend/app/core/config.py`의 `Settings`가 `backend/.env`를 읽는다.

- Pydantic Settings가 환경변수 Type과 필수값을 검증한다.
- PostgreSQL 연결값이 비어 있으면 Application 초기화 단계에서 실패한다.
- Password와 API Key는 `SecretStr`로 관리한다.
- Module에서 생성한 `settings` 객체를 Backend 전체가 공유한다.
- Settings 전체 또는 Secret 값을 Log에 출력하지 않는다.

환경변수를 추가할 때는 `Settings`와 `backend/.env.example` 또는 `frontend/.env.example`을 함께 수정한다.

## 6. Frontend 구성

Frontend는 Next.js App Router를 사용한다.

- `app/layout.tsx`: 공통 HTML Layout과 Metadata
- `app/page.tsx`: Root Page 진입점
- `app/globals.css`: Tailwind CSS와 전역 Style
- `next.config.ts`: Docker용 Standalone Build 설정
- `services/`: Backend API 통신을 기능별로 분리
- `components/`: 재사용 가능한 UI만 배치

현재 Root Page는 실제 서비스 화면을 구현하지 않은 빈 진입점이다.

### Frontend Dependency

| Dependency | 용도 |
| --- | --- |
| `next` | App Router와 Frontend Build |
| `react`, `react-dom` | React Runtime |
| `typescript` | TypeScript 검사와 Build |
| `tailwindcss` | CSS Utility Framework |
| `@tailwindcss/postcss` | Tailwind PostCSS 처리 |
| `eslint`, `eslint-config-next` | Source 정적 검사 |
| `@types/*` | TypeScript Type 선언 |

## 7. Backend 구성

### 7.1 Application 시작 흐름

```text
app/main.py
  → core/fastset.py의 run()
  → Settings 적용
  → Router 탐색 및 등록
  → CORS Middleware 적용
  → FastAPI Application 반환
```

`main.py`에는 기능별 Router를 직접 등록하지 않는다.

### 7.2 Router 자동 등록

`fastset.py`는 `backend/app/routers/`의 Python 파일을 자동으로 탐색한다. 파일에 `APIRouter` Type의 `router` 변수가 있으면 파일명으로 URL Prefix를 만들어 등록한다.

| Router 파일 | 자동 Prefix |
| --- | --- |
| `fraud_analysis.py` | `/fraud-analysis` |
| `voice_phishing.py` | `/voice-phishing` |
| `news_article.py` | `/news-article` |

Python 파일명은 `snake_case`, URL은 `kebab-case`를 사용한다. Router 파일에서 동일한 Prefix를 다시 선언하지 않는다.

새 Router를 추가할 때는 다음 순서를 따른다.

1. `backend/app/routers/`에 `snake_case` 파일을 만든다.
2. 파일에 `router = APIRouter()`를 정의한다.
3. 하위 Endpoint Path와 HTTP Method만 정의한다.
4. Request/Response는 `schemas/`의 Pydantic Schema를 사용한다.
5. Business Logic은 `services/`로 분리한다.
6. Database 접근은 `repositories/`로 분리한다.

### 7.3 공통 API 응답

`backend/app/schemas/api_response.py`의 `ApiResponse`를 사용한다.

```json
{
  "success": true,
  "data": {},
  "message": "요청이 정상적으로 처리되었습니다."
}
```

실패 응답도 동일한 구조를 사용한다.

```json
{
  "success": false,
  "data": null,
  "message": "요청을 처리할 수 없습니다."
}
```

Endpoint는 `response_model`을 명시한다. 정상 응답은 `200` 또는 `201`을 중심으로 사용하며 공통 응답 구조 때문에 `204`는 사용하지 않는다.

### 7.4 Backend Dependency

| Dependency | 용도 |
| --- | --- |
| `fastapi` | Backend API Framework |
| `uvicorn[standard]` | ASGI Server |
| `pydantic-settings` | 환경변수 로딩과 검증 |
| `psycopg[binary]` | PostgreSQL 연결과 Pure SQL 실행 |

Backend Dependency는 `uv`로만 관리한다. `requirements.txt`를 별도로 만들지 않는다.

## 8. Pure SQL Database 접근

ORM과 Query Builder를 사용하지 않는다. SQL은 Repository에서 직접 작성하고 `backend/app/repositories/db.py`의 공통 Helper로 실행한다.

### 8.1 공통 Helper

| 함수 | 역할 | 반환값 |
| --- | --- | --- |
| `get_connection()` | PostgreSQL 연결 생성 | Dictionary Row Connection |
| `find_one(sql, parameters)` | 단일 Row 조회 | `dict` 또는 `None` |
| `find_all(sql, parameters)` | 여러 Row 조회 | `list[dict]` |
| `save(sql, parameters)` | 단일 변경 SQL 실행 | 성공 시 `True` |

각 Helper는 Connection을 열고, SQL을 실행한 후 Commit한다. psycopg 오류가 발생하면 Rollback하고 오류를 Log에 남긴 뒤 예외를 다시 전달한다. 마지막에는 Connection을 닫는다.

### 8.2 SQL Parameter 규칙

psycopg Parameter Placeholder는 `%s`를 사용한다.

```python
sql = "SELECT id FROM users WHERE id = %s"
parameters = (user_id,)
result = find_one(sql, parameters)
```

사용자 입력을 f-string이나 문자열 연결로 SQL에 삽입하지 않는다.

```python
# 금지
sql = f"SELECT id FROM users WHERE id = {user_id}"
```

Table과 Column 이름은 개발자가 작성한 고정 SQL에서 관리한다. 실제 SQL은 해당 기능의 Repository 파일에 두며 Router 또는 Service에 작성하지 않는다.

## 9. Database SQL 관리

Application Python Code와 Database 구조 변경 SQL을 분리한다.

- `database/schemas/`: 최초 Schema, Table, Index, Extension 정의
- `database/migrations/`: 기존 구조를 변경하는 SQL
- `database/seeds/`: 개발/Test 초기 데이터

현재 `database/schemas/0001_enable_vector.sql`은 다음 Extension만 활성화한다.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

실제 서비스 Table은 아직 없다.

이미 적용된 Migration은 수정하지 않는다. Database 구조 변경이 필요하면 새 Migration SQL을 추가한다.

## 10. Local 실행

### 10.1 준비 항목

- Python 3.12
- uv
- Node.js
- npm
- Docker Desktop 또는 Docker Engine
- Docker Compose

### 10.2 PostgreSQL 실행

```powershell
docker compose --env-file frontend/.env up -d database
```

### 10.3 Backend 실행

```powershell
cd backend
uv sync --frozen --python 3.12
uv run uvicorn app.main:app --reload
```

- API Server: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### 10.4 Frontend 실행

```powershell
cd frontend
npm ci
npm run dev
```

- Frontend: `http://localhost:3000`

## 11. Docker 실행

전체 Service를 Build하고 실행한다.

```powershell
docker compose --env-file frontend/.env up --build
```

Service와 Port는 다음과 같다.

| Service | Container 역할 | Local Port |
| --- | --- | --- |
| `frontend` | Next.js | `3000` |
| `backend` | FastAPI/Uvicorn | `8000` |
| `database` | PostgreSQL/pgvector | `5432` |

Backend는 Database Health Check가 통과한 뒤 시작한다. Database 데이터는 `postgres_data` Volume에 보존된다.

Container를 중지한다.

```powershell
docker compose down
```

Database Volume까지 제거하면 저장된 Local 데이터가 삭제된다. 필요한 경우에만 실행한다.

```powershell
docker compose down --volumes
```

## 12. Git과 GitHub

다음 Local 파일과 생성물은 Git에 포함하지 않는다.

- `frontend/.env`, `backend/.env`
- `node_modules/`, `.next/`
- `.venv/`, `__pycache__/`
- Test/Type/Lint Cache
- IDE와 운영체제 임시 파일

다음 파일은 Git에 포함한다.

- `frontend/.env.example`, `backend/.env.example`
- `frontend/package-lock.json`
- `backend/uv.lock`
- SQL Schema/Migration/Seed
- GitHub 설정과 문서

`.github/ISSUE_TEMPLATE/`에는 기능, Bug, 문서, 장애, 성능, 보안, Trouble Shooting, Update 작업용 Template이 준비되어 있다. `.github/workflows/`는 GitHub Actions Workflow를 추가할 위치이며 실제 Workflow 정책은 아직 확정되지 않았다.

Commit, Push, Branch 삭제, Merge 등의 Git 작업은 명시적인 요청 없이 수행하지 않는다.

## 13. Naming과 Source 작성 규칙

### Frontend

- 변수/함수: `camelCase`
- React Component, Type/Interface: `PascalCase`
- 상수: `UPPER_SNAKE_CASE`

### Backend

- 변수/함수: `snake_case`
- Class: `PascalCase`
- 상수: `UPPER_SNAKE_CASE`
- Import: 상대경로

### Database

- Table: `snake_case` 복수형
- Column: `snake_case`
- Primary Key: `id`
- Foreign Key: `<entity>_id`

주요 Source 파일 최상단에는 파일 목적과 주요 역할을 설명하는 한국어 주석을 작성한다. `print()`와 `console.log()`는 Commit 전에 제거한다.

## 14. 기본 검증 명령

### Frontend

```powershell
cd frontend
npm ci
npm run lint
npm run build
```

### Backend

```powershell
cd backend
uv lock --check
uv sync --frozen --python 3.12
uv run python -m compileall app
uv run uvicorn app.main:app
```

### Docker Compose

```powershell
docker compose --env-file frontend/.env config --quiet
```

## 15. 주의사항과 미결정 사항

- 환경 파일은 팀 요청에 따라 Frontend와 Backend로 분리했다. 이는 루트 `.env`와 `.env.example`만 사용하도록 작성된 기존 `PROJECT_RULES.md` 내용과 다르므로 팀 공통 규칙 문서의 별도 합의 및 정리가 필요하다.
- PostgreSQL은 현재 18, pgvector는 0.8.5 Image를 사용한다. 팀 고정 Version 여부는 별도로 결정해야 한다.
- Node.js Major Version을 팀 규칙으로 아직 고정하지 않았다.
- GitHub Actions Workflow의 Trigger와 검사 항목은 아직 결정하지 않았다.
- 운영 CORS Origin은 배포 주소가 결정된 뒤 `CORS_ORIGINS`에 추가해야 한다.
- `NEXT_PUBLIC_` 값은 Next.js Build 시 Browser Bundle에 포함될 수 있다.
- npm 보안 점검에서 Next.js 전이 Dependency 관련 취약점이 확인된 적이 있다. Breaking Change를 동반하는 자동 수정은 적용하지 말고 안정 Version 제공 여부를 확인한 뒤 팀 합의로 갱신한다.
- pgvector 초기화 SQL은 PostgreSQL Volume이 처음 생성될 때 실행된다. 이미 생성된 Volume에는 초기화 SQL이 다시 실행되지 않는다.

## 16. 작업 시작 전 Check List

1. `PROJECT_RULES.md`와 이 문서를 확인했는가?
2. 기능에 맞는 기존 Folder/Layer를 선택했는가?
3. 새 환경변수를 올바른 `.env.example`에도 추가했는가?
4. Secret이 Frontend 또는 Git 관리 파일에 포함되지 않았는가?
5. Router Prefix를 파일 안에서 중복 선언하지 않았는가?
6. SQL을 Repository에 작성하고 Parameter Binding을 사용했는가?
7. API Request/Response에 Pydantic Schema와 공통 응답을 사용했는가?
8. 임시 Log와 Debug Code를 제거했는가?
9. Frontend Lint/Build와 Backend 초기화를 검증했는가?
10. Database 구조 변경이 있다면 새 SQL Migration으로 작성했는가?
