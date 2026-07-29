# PROJECT_RULES.md

> 팀 노션에서 확정한 규칙과 이후 협의하여 확정한 공통 개발 규칙을
> 정리한다. Codex, Claude, Antigravity 등 AI Coding Agent를 포함한 모든
> 개발 작업은 본 규칙을 우선 따른다.

## 1. 기술 스택

  구분                       확정 규칙
  -------------------------- -----------------------
  Python                     3.12
  Frontend                   Next.js + TypeScript
  Backend                    Python + FastAPI
  Database                   PostgreSQL + pgvector
  Cache / Message Queue      Redis, Kafka 제외
  Frontend CSS               Tailwind CSS
  CI/CD                      GitHub Actions
  Backend Package Manager    uv
  Frontend Package Manager   npm

## 2. 기본 개발 원칙

-   기존 프로젝트 구조와 규칙을 우선한다.
-   불필요하게 복잡한 구조, 계층, 디자인 패턴을 도입하지 않는다.
-   Class가 필요한 구조는 Class 기반으로 작성한다.
-   Alias는 사용하지 않는다.
-   Import는 상대경로를 사용한다.
-   DB 적재 및 변경은 SQL 작성 후 수행하는 방식을 기본으로 한다.
-   프레임워크가 특정 파일명/디렉터리 구조를 강제하는 경우 프레임워크
    규칙을 우선한다.

## 3. Naming Convention

### Frontend

-   변수/함수: `camelCase`
-   React Component: `PascalCase`
-   TypeScript Type/Interface: `PascalCase`
-   상수: `UPPER_SNAKE_CASE`
-   축약어 사용 가능

### Backend

-   변수/함수: `snake_case`
-   Class: `PascalCase`
-   상수: `UPPER_SNAKE_CASE`
-   Enum Class: `PascalCase`
-   Enum Value: `UPPER_SNAKE_CASE`
-   가능한 한 풀네임 사용

### Database

-   Table: `snake_case` + 복수형
-   Column: `snake_case`
-   Primary Key: `id`
-   Foreign Key: `<entity>_id`
-   축약어 사용 가능하나 의미를 Comment로 명시

### Folder / File

-   폴더: 소문자 + 복수형 + 풀네임
-   파일: 소문자 + 단수형 + 풀네임
-   여러 단어 파일명: `snake_case`
-   프레임워크 예약 파일은 예외

예: `fraud_analysis.py`, `voice_phishing.py`, `news_article.py`,
`fraud_result.tsx`

예약 파일 예: `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`,
`route.ts`, `__init__.py`

## 4. 프로젝트 구조

프로젝트는 역할이 명확하게 드러나는 계층 구조를 유지한다.
새로운 파일을 생성할 때는 먼저 기존 폴더 중 해당 역할을 담당하는 위치가 있는지 확인한다.

```text
project-root/
├── frontend/               # Next.js 기반 사용자 화면 및 Frontend 로직
│   ├── app/                # App Router 기반 Page, Layout, Route 구성
│   ├── components/         # 재사용 가능한 UI Component
│   ├── services/           # Backend API 호출 및 통신 로직
│   ├── types/              # Frontend 공통 TypeScript Type
│   ├── utils/              # 특정 Domain에 종속되지 않는 공통 Utility
│   └── public/             # 이미지, 아이콘 등 정적 리소스
│
├── backend/                # FastAPI 기반 API 및 Backend 애플리케이션
│   └── app/
│       ├── routers/        # Endpoint 및 HTTP Request/Response 처리
│       ├── services/       # 핵심 비즈니스 로직
│       ├── repositories/   # PostgreSQL 등 Database 접근
│       ├── models/         # Database ORM/Model 정의
│       ├── schemas/        # Pydantic Request/Response Schema
│       ├── clients/        # 외부 API, AI, OCR, STT 서비스 연동
│       ├── core/           # 환경설정 및 애플리케이션 공통 기반 설정
│       │   └── fastset.py  # FastAPI 초기화 및 Router 자동 등록 기반 설정
│       └── main.py         # FastAPI Application 진입점
│
├── database/               # SQL 기반 Database 정의 및 변경 이력
│   ├── schemas/            # 최초 Schema/Table 정의 SQL
│   ├── migrations/         # Schema 변경 SQL
│   └── seeds/              # 초기/샘플 데이터 SQL
│
├── docs/                   # 개발 및 프로젝트 관련 문서
├── .github/                # GitHub Actions, Issue/PR Template 등 GitHub 설정
├── compose.yml             # 전체 서비스 Docker Compose 정의
└── PROJECT_RULES.md        # 프로젝트 공통 개발 규칙
```

### 4.1 Root

#### `frontend/`

Next.js 기반 Frontend 애플리케이션 전체를 관리한다.

포함:
- 화면
- Component
- 사용자 Interaction
- Backend API 호출
- Frontend Type
- Browser에서 필요한 상태 및 표현 로직

포함하지 않음:
- Database 직접 접근
- OpenAI 등 Secret이 필요한 외부 API 직접 호출
- Backend 비즈니스 로직

#### `backend/`

FastAPI 기반 Backend 애플리케이션 전체를 관리한다.

포함:
- API Endpoint
- 비즈니스 로직
- AI/OCR/STT 처리
- 외부 서비스 연결
- Database 접근
- Request/Response 검증
- 환경설정

#### `database/`

Database 자체를 정의하거나 변경하기 위한 SQL 파일을 관리한다.

Application Python Code를 저장하지 않는다.

#### `docs/`

프로젝트 구현과 협업에 필요한 문서를 관리한다.

예:
- API 명세
- 구조 설명
- 개발 참고 문서
- 설계 문서

실제 Application Source Code는 저장하지 않는다.

#### `.github/`

GitHub에서 사용하는 설정 파일을 관리한다.

예:
- GitHub Actions Workflow
- Issue Template
- Pull Request Template

#### `compose.yml`

Frontend, Backend, Database 등 프로젝트 실행에 필요한 Docker Service를 정의한다.

환경별 Compose 파일을 필요 이상으로 분리하지 않는다.

#### `PROJECT_RULES.md`

팀 공통 개발 규칙의 기준 문서이다.

AI Coding Agent와 팀원 모두 이 문서를 우선 참고한다.

작업 편의를 위해 임의로 변경하지 않는다.

### 4.2 Frontend Structure

#### `frontend/app/`

Next.js App Router 기반 Routing 영역이다.

주요 역할:
- Page 정의
- Layout 정의
- Route Segment 구성
- Loading/Error UI
- Next.js Route Handler가 필요한 경우 해당 Route 정의

예:

```text
app/
├── fraud/
│   └── page.tsx
├── voice-phishing/
│   └── page.tsx
├── news/
│   └── page.tsx
├── layout.tsx
└── page.tsx
```

규칙:
- 페이지 전용 화면 구성과 Routing을 담당한다.
- 재사용 가능한 UI는 `components/`로 분리한다.
- 복잡한 API 통신 로직을 Page에 직접 작성하지 않는다.
- Backend 비즈니스 로직을 구현하지 않는다.

#### `frontend/components/`

재사용 가능한 UI Component를 관리한다.

주요 역할:
- 공통 Button, Modal, Card 등 UI
- 기능별 재사용 Component
- 화면을 구성하는 표현 단위

예:

```text
components/
├── commons/
├── frauds/
├── voice-phishings/
└── news/
```

규칙:
- API 호출 자체를 Component 곳곳에 중복 작성하지 않는다.
- Backend 통신이 필요하면 `services/`를 사용한다.
- 하나의 Page에서만 사용되더라도 충분히 복잡하고 독립적인 UI라면 Component로 분리할 수 있다.
- 지나치게 작은 단위까지 기계적으로 Component로 분리하지 않는다.

#### `frontend/services/`

Backend API 통신 로직을 관리한다.

주요 역할:
- HTTP Request
- Request Parameter 구성
- Response 전달
- 공통 API Base URL 사용

예:

```text
services/
├── fraud_analysis.ts
├── voice_phishing.ts
└── news_article.ts
```

규칙:
- Page/Component마다 동일한 `fetch` 또는 HTTP 호출을 반복 작성하지 않는다.
- UI 표시 로직을 포함하지 않는다.
- Backend의 비즈니스 판단을 Frontend Service에 복제하지 않는다.
- API Endpoint와 Request/Response 계약을 기존 Backend 규칙에 맞춘다.

#### `frontend/types/`

Frontend에서 공유하는 TypeScript Type을 관리한다.

주요 역할:
- API Request/Response Type
- Component 간 공유 Type
- 여러 파일에서 재사용하는 Domain Type

규칙:
- 한 파일에서만 사용하는 단순 Type까지 무조건 이동시키지 않는다.
- Backend Pydantic Schema와 의미가 같은 API Type은 필드명을 임의로 다르게 정의하지 않는다.
- API JSON Field는 `snake_case` 규칙을 유지한다.

#### `frontend/utils/`

특정 UI나 Domain에 직접 종속되지 않는 공통 Utility 함수를 관리한다.

예:
- 날짜 Formatting
- 문자열 Formatting
- 공통 값 변환

규칙:
- 무엇이든 넣는 잡동사니 폴더로 사용하지 않는다.
- 비즈니스 로직을 `utils/`로 이동하지 않는다.
- API 호출은 `services/`에 둔다.
- 특정 Component에만 필요한 작은 함수는 해당 Component 가까이에 둘 수 있다.

#### `frontend/public/`

정적 리소스를 관리한다.

예:
- Image
- Icon
- 정적 JSON 등 실제로 Public Resource로 제공할 파일

Secret 또는 환경설정 파일을 저장하지 않는다.

### 4.3 Backend Structure

Backend 기본 흐름:

```text
routers
  ↓
services
  ↓
repositories
  ↓
models
```

외부 서비스가 필요한 경우:

```text
routers
  ↓
services
  ├── repositories
  └── clients
```

`schemas`는 계층 흐름이 아니라 API 계약 정의에 사용한다.

#### `backend/app/routers/`

FastAPI Endpoint를 정의한다.

주요 역할:
- Route URL
- HTTP Method
- Request 수신
- Pydantic Schema 연결
- Service 호출
- HTTP Response 반환

규칙:
- 핵심 비즈니스 로직을 Router에 직접 작성하지 않는다.
- Database Query를 직접 작성하지 않는다.
- 외부 AI/OCR/STT API를 Router에서 직접 호출하지 않는다.
- Router는 가능한 한 요청과 응답 흐름을 조정하는 역할에 집중한다.

#### `backend/app/services/`

프로젝트 핵심 비즈니스 로직을 관리한다.

주요 역할:
- 투자 사기 판별 흐름
- 보이스피싱 분석 흐름
- 금융 뉴스 분석 흐름
- Repository와 Client 호출 조합
- 결과 가공 및 판단

규칙:
- HTTP Endpoint 세부사항에 과도하게 의존하지 않는다.
- 직접 SQL을 실행하지 않고 `repositories/`를 통해 접근한다.
- 외부 API 구현 세부사항은 `clients/`로 분리한다.
- 단순 전달만 하는 의미 없는 Service 계층을 만들지 않는다.

#### `backend/app/repositories/`

Database 접근 로직을 관리한다.

주요 역할:
- 조회
- 저장
- 수정
- 삭제
- SQL 실행
- pgvector 관련 Database Query

규칙:
- 비즈니스 판단 로직을 작성하지 않는다.
- HTTP Request/Response를 다루지 않는다.
- 외부 API를 호출하지 않는다.
- Database 접근 방식은 가능한 한 이 폴더로 통일한다.

#### `backend/app/models/`

Database Model을 정의한다.

주요 역할:
- Table과 연결되는 Model
- Column
- 관계
- Database 단위 구조

규칙:
- API Response 표현을 위한 Schema 역할과 혼합하지 않는다.
- API Request/Response는 `schemas/`를 사용한다.

#### `backend/app/schemas/`

Pydantic 기반 데이터 Schema를 관리한다.

주요 역할:
- API Request Schema
- API Response Schema
- 공통 `ApiResponse`
- Service 간 명확한 데이터 구조가 필요한 경우 관련 Schema

규칙:
- Database Model과 API Schema를 동일한 개념으로 취급하지 않는다.
- API JSON Naming 규칙인 `snake_case`를 유지한다.
- 기존 API 계약을 임의로 변경하지 않는다.

#### `backend/app/clients/`

프로젝트 외부 시스템 또는 외부 서비스 연결을 관리한다.

예:
- Whisper
- OCR
- LLM
- 뉴스 API
- 기타 외부 HTTP API

주요 역할:
- 외부 서비스 요청
- 인증 Header 구성
- Timeout
- 외부 응답 처리
- 외부 서비스 오류 전달

규칙:
- 외부 API 호출 코드를 Service 여러 곳에 반복 작성하지 않는다.
- API Key를 코드에 직접 작성하지 않는다.
- 환경변수/Settings를 통해 Credential을 전달받는다.
- 프로젝트의 최종 비즈니스 판단은 Client가 아니라 `services/`에서 수행한다.

#### `backend/app/core/`

애플리케이션 전반에서 사용하는 기반 설정을 관리한다.

예:
- `config.py`
- `fastset.py`
- 공통 환경설정
- 공통 Logger 설정
- FastAPI Application 초기화 설정

`fastset.py`는 초기 프로젝트 템플릿에 미리 제공되는 기반 파일로 사용한다.

주요 역할:
- FastAPI Application 초기화
- API Router 자동 탐색 및 등록
- Router 파일명을 기준으로 Prefix 자동 적용
- CORS 등 Application 공통 설정 연결

규칙:
- Router 자동 등록 기능은 초기 프로젝트 구조에 이미 구현되어 있다고 가정한다.
- 기능 개발자가 Router를 추가할 때 `main.py` 또는 `fastset.py`에 등록 코드를 반복해서 추가하지 않는다.
- Router Prefix를 각 API 파일에서 중복으로 직접 관리하지 않는다.
- 기본 자동 등록 구조를 기능 구현 편의를 위해 임의로 변경하지 않는다.
- 특정 기능의 비즈니스 로직을 넣지 않는다.
- `utils/`처럼 임의의 코드를 모으는 공간으로 사용하지 않는다.
- 프로젝트 전체에서 공통으로 사용하는 기반 코드만 둔다.

#### `backend/app/main.py`

FastAPI Application의 진입점이다.

초기 프로젝트 템플릿에서 제공되는 FastAPI 초기화 구조를 사용하며,
Router 등록과 공통 설정의 세부 구현은 `fastset.py` 등 기반 설정 파일에 위임할 수 있다.

규칙:
- 기능별 Router를 `main.py`에 하나씩 수동 등록하는 방식을 기본으로 사용하지 않는다.
- 기능별 비즈니스 로직을 직접 구현하지 않는다.
- 거대한 설정 파일로 만들지 않는다.

### 4.4 Database Structure

#### `database/schemas/`

최초 Database 구조를 정의하는 SQL을 관리한다.

예:
- Table 생성
- Index 생성
- pgvector Extension/Column 초기 정의

#### `database/migrations/`

기존 Database 구조 변경 이력을 SQL로 관리한다.

예:
- Column 추가
- Index 변경
- Table 구조 변경

규칙:
- 이미 적용된 Migration을 이유 없이 수정하지 않는다.
- 변경이 필요하면 새로운 Migration SQL을 추가하는 방식을 우선한다.

#### `database/seeds/`

개발 및 테스트에 필요한 초기/샘플 데이터를 관리한다.

실제 운영 Secret이나 민감정보를 Seed 데이터에 포함하지 않는다.

### 4.5 Folder Boundary Rules

파일을 생성하기 전에 해당 역할에 맞는 기존 폴더가 있는지 먼저 확인한다.

잘못된 예:

```text
routers/ 안에서 SQL 직접 실행
components/ 안에서 OpenAI API 직접 호출
utils/ 안에 핵심 투자 사기 판별 로직 작성
clients/ 안에서 최종 사기 위험도 판단
models/ 안에 API Response 전용 구조 정의
```

새로운 Layer를 추가하기 전에 기존 구조로 해결 가능한지 먼저 확인한다.

다음과 같은 Layer는 임의로 추가하지 않는다.

```text
controllers
handlers
managers
usecases
```

기존 구조로 처리하기 어려운 명확한 이유가 있을 때만 새로운 구조를 제안한다.

## 5. 파일 설명 주석

직접 작성하는 주요 소스 파일 최상단에는 다음을 설명하는 주석을 작성한다.

1.  파일의 목적
2.  파일의 주요 역할

파일 책임이 변경되면 최상단 설명도 함께 수정한다.

-   코드 자체를 그대로 번역하는 불필요한 주석은 남발하지 않는다.
-   복잡한 로직은 무엇보다 "왜 이렇게 구현했는지"를 설명한다.
-   함수/Class가 복잡하거나 역할이 불명확할 때 Docstring/JSDoc을
    작성한다.
-   모든 함수에 Docstring/JSDoc을 기계적으로 강제하지 않는다.
-   자동 생성 파일, lock 파일, `package.json`, 내용이 없는 `__init__.py`
    등은 예외로 할 수 있다.

## 6. API Rules

### 6.1 Router / Prefix

Backend 초기 프로젝트 템플릿에는 FastAPI Router 자동 등록 구조가 미리 구성되어 있다고 가정한다.

기본 원칙:

- API Router 파일을 정해진 Router/API 디렉터리에 추가하면 자동 등록된다.
- Router Prefix는 Router 파일명을 기준으로 자동 생성된다.
- Python 파일명은 기존 규칙대로 `snake_case`를 사용한다.
- URL Prefix에서는 파일명의 `_`를 `-`로 변환하여 사용한다.
- 기능 개발자가 동일한 Prefix를 Router 파일마다 반복해서 직접 선언하지 않는다.
- 기능 추가를 위해 `main.py` 또는 초기 Router 등록 코드를 매번 수정하지 않는다.
- 자동 Router 등록 구조 자체를 임의로 변경하지 않는다.

예:

```text
fraud_analysis.py
→ /fraud-analysis

voice_phishing.py
→ /voice-phishing

news_article.py
→ /news-article
```

이 규칙은 **초기 프로젝트 템플릿에 해당 기능이 이미 구현되어 있다는 전제**이며,
`PROJECT_RULES.md`에 Router 자동 등록 구현 코드를 복제하지 않는다.

### 6.2 URL Naming

자동 생성되는 Prefix 외의 하위 Endpoint Path에도 다음 규칙을 적용한다.

- lowercase 사용
- 여러 단어는 `kebab-case`
- 의미를 명확하게 표현한다.
- 불필요한 동사를 URL에 넣지 않고 가능한 경우 HTTP Method로 동작을 표현한다.

### 6.3 HTTP Method

- `GET`: 조회
- `POST`: 생성 또는 분석 요청
- `PATCH`: 일부 수정
- `DELETE`: 삭제
- `PUT`: 전체 교체가 명확하게 필요한 경우에만 사용

### 6.4 JSON Naming

API Request / Response JSON Field는 `snake_case`를 사용한다.

Frontend 내부 변수의 `camelCase` 규칙과 API JSON 규칙은 분리한다.

### 6.5 Request / Response Schema

- Request / Response는 Pydantic Schema로 정의한다.
- FastAPI `response_model`을 사용한다.
- 공통 Response 구조를 사용한다.

기본 구조:

```json
{
  "success": true,
  "data": {},
  "message": "요청이 정상적으로 처리되었습니다."
}
```

실패 예:

```json
{
  "success": false,
  "data": null,
  "message": "지원하지 않는 파일 형식입니다."
}
```

개념적 Schema:

```python
class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    message: str | None = None
```

### 6.6 HTTP Status

응답 구조를 단순화하기 위해 정상 응답은 `200` 또는 `201`을 중심으로 사용한다.

- `200`: 조회 및 일반 성공
- `201`: 생성 및 분석 요청 성공
- `400`: 잘못된 요청
- `404`: 리소스를 찾을 수 없음
- `422`: FastAPI / Pydantic Validation
- `500`: 서버 내부 오류

`204 No Content`는 공통 Response 구조와의 일관성을 위해 사용하지 않는다.

### 6.7 File Upload

- 파일 업로드는 `multipart/form-data`를 사용한다.
- JSON 입력과 파일 입력의 성격이 크게 다른 경우 Endpoint를 분리한다.

## 7. Git / GitHub Rules

작업 흐름:
`Issue → Branch → Commit → Push → Pull Request → Review → Squash Merge → Issue Close → Branch Delete`

### Issue

-   작업별 GitHub Issue 생성
-   Issue 1개 = 하나의 명확한 작업 단위

### Branch

형식: `<type>/<description>_<name>`

-   전체 소문자
-   description은 영문
-   여러 단어는 `-`로 구분
-   마지막에 `_` + 작업자 이름 철자

Type: `feature`, `fix`, `refactor`, `docs`, `chore`

예: `feature/news-analysis_lch`, `fix/ocr-upload_lch`

### Commit

형식: `<한글 작업 내용> #<issue-number>`

예: `금융 뉴스 조회 API 구현 #12`

-   별도 Commit Type Prefix 사용 안 함
-   한글로 명확하게 작성
-   Issue 번호는 마지막
-   하나의 논리적 변경 단위로 Commit
-   `수정`, `작업`, `업데이트`, `최종`, `코드 수정` 같은 의미 없는
    메시지 금지

### Pull Request

제목: `<한글 작업 내용> #<issue-number>`

본문: - 작업 내용 - 확인 사항 - 관련 이슈 - `Closes #<issue-number>`로
Issue 연결

원칙: `Issue 1개 ≈ Branch 1개 ≈ PR 1개`

### Review / Merge

-   최소 팀원 1명 확인 후 Merge
-   작성자가 리뷰 없이 바로 Merge하는 것은 원칙적으로 금지
-   `Squash and merge` 사용
-   `main` 직접 Commit/Push 금지
-   Merge 후 작업 Branch 삭제

## 8. Package Management

Backend: - Python 3.12 - `uv` - `pyproject.toml` - `uv.lock` Git 포함 -
Dependency 추가/삭제는 uv 사용 - `requirements.txt` 병행 관리하지 않음

Frontend: - `npm` - `package.json` - `package-lock.json` Git 포함 -
yarn/pnpm 혼용 금지

## 9. Environment & Configuration Rules

환경변수는 Local, Docker, Frontend, Backend에서 동일한 이름 체계를 유지하고,
실제 Secret 값과 공개 가능한 설정값을 명확히 구분한다.

### 9.1 Environment Variable Naming

모든 환경변수 이름은 `UPPER_SNAKE_CASE`를 사용한다.

예:

```text
DATABASE_URL
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
OPENAI_API_KEY
NEXT_PUBLIC_API_BASE_URL
```

규칙:

- 환경변수 이름만 보고 역할을 파악할 수 있도록 작성한다.
- 의미가 불분명한 한 글자 또는 과도한 축약어를 사용하지 않는다.
- 동일한 의미의 환경변수를 여러 이름으로 만들지 않는다.
- 기존 환경변수 이름을 임의로 변경하지 않는다.
- 새로운 환경변수를 추가하면 `.env.example`도 반드시 함께 수정한다.
- 사용하지 않게 된 환경변수를 삭제할 때는 Backend, Frontend, Docker Compose의 참조 여부를 먼저 확인한다.

### 9.2 Environment Files

기본적으로 다음 두 파일만 사용한다.

```text
.env
.env.example
```

`.env`:

- 실제 Local 개발 환경값을 저장한다.
- API Key, DB Password 등 실제 Secret을 포함할 수 있다.
- Git에 Commit하지 않는다.
- `.gitignore`에 반드시 포함한다.
- 파일 전체 내용을 로그, 응답, 문서에 출력하지 않는다.

`.env.example`:

- Git에 포함한다.
- 프로젝트 실행에 필요한 환경변수의 이름을 공유한다.
- 실제 Secret 값은 절대 작성하지 않는다.
- 팀원이 어떤 값을 준비해야 하는지 알 수 있도록 용도별로 구분한다.

예:

```dotenv
# Application
APP_ENV=
APP_DEBUG=

# Database
DATABASE_URL=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

# External API
OPENAI_API_KEY=

# Frontend
NEXT_PUBLIC_API_BASE_URL=
```

현재 프로젝트에서는 필요성이 확인되기 전까지 다음과 같이 환경 파일을 과도하게 분리하지 않는다.

```text
.env.local
.env.development
.env.production
.env.docker
.env.test
```

추가 환경 파일이 필요하면 팀 합의 후 추가한다.

### 9.3 Required / Optional Values

환경변수는 필수값과 선택값을 명확히 구분한다.

Secret이나 외부 연결에 필요한 중요한 값은 의미 없는 기본값으로 숨기지 않는다.

허용 예:

```python
app_name: str = "finance-ai"
debug: bool = False
```

지양:

```python
database_url: str = "postgresql://admin:password@localhost/database"
```

금지:

```python
openai_api_key: str = "actual-secret-key"
```

원칙:

- 일반 애플리케이션 설정은 안전한 기본값을 사용할 수 있다.
- API Key, Password, Token은 기본값으로 실제 값을 작성하지 않는다.
- 필수 연결정보가 없으면 초기화 단계에서 명확하게 실패하도록 한다.
- 환경변수 누락을 임의의 fallback 값으로 숨기지 않는다.

### 9.4 Backend Configuration

Backend 환경설정은 `pydantic-settings`를 사용한다.

설정 파일 위치:

```text
backend/app/core/config.py
```

환경설정 접근의 단일 진입점은 Settings 객체로 통일한다.

예:

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    openai_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

규칙:

- 환경변수가 필요하면 먼저 `Settings`에 정의한다.
- Service, Repository, Client 등에서 `os.getenv()` 또는 `os.environ[]`을 직접 반복 사용하지 않는다.
- 환경설정 타입 검증은 `pydantic-settings`에 맡긴다.
- Settings는 애플리케이션 전체에서 동일한 방식으로 접근한다.
- Secret 값을 Log에 출력하지 않는다.
- Settings 객체 전체를 Debug 용도로 그대로 출력하지 않는다.

### 9.5 Secret Rules

다음 값은 Secret으로 취급한다.

- API Key
- Password
- Token
- Database 인증정보
- 외부 서비스 Credential
- Private Key
- 기타 인증용 값

Secret은 다음 위치에 직접 작성하지 않는다.

- Source Code
- Dockerfile
- Git 관리 파일
- `.env.example`
- README
- Log
- Error Response
- Test Fixture에 실제 운영 Secret

Secret이 필요하면 환경변수를 통해 전달한다.

## 10. Next.js Environment Rules

Next.js 환경변수는 **Server 전용 변수**와 **Browser에 공개되는 변수**를 명확히 구분한다.

### 10.1 Server-only Environment Variables

`NEXT_PUBLIC_` Prefix가 없는 환경변수는 기본적으로 Server 측 코드에서 사용하는 값으로 취급한다.

예:

```dotenv
BACKEND_INTERNAL_URL=http://backend:8000
INTERNAL_SERVICE_TOKEN=
```

다음 정보는 Server 전용으로 유지한다.

- API Key
- Password
- Token
- Database 접속정보
- 외부 서비스 Secret
- 내부 Container 주소 중 Browser에서 알 필요가 없는 값

Client Component에서 Secret 환경변수를 직접 읽으려고 하지 않는다.

### 10.2 Public Environment Variables

Browser에서 직접 사용해야 하는 값만 `NEXT_PUBLIC_` Prefix를 사용한다.

예:

```dotenv
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

`NEXT_PUBLIC_`이 붙은 값은 Browser에서 접근 가능한 공개값으로 간주한다.

따라서 다음과 같은 변수는 절대 만들지 않는다.

```text
NEXT_PUBLIC_OPENAI_API_KEY
NEXT_PUBLIC_POSTGRES_PASSWORD
NEXT_PUBLIC_DATABASE_URL
NEXT_PUBLIC_SECRET_KEY
NEXT_PUBLIC_ACCESS_TOKEN
```

판단 기준:

> 사용자가 Browser Developer Tools에서 값을 확인해도 문제가 없는가?

문제가 있다면 `NEXT_PUBLIC_`을 사용하지 않는다.

### 10.3 Server Component / Client Component

Next.js App Router에서는 Server와 Client 실행 위치를 구분한다.

Server Component 또는 Server 측 코드:

```typescript
const internalUrl = process.env.BACKEND_INTERNAL_URL;
```

Client Component에서 Browser에 필요한 값:

```typescript
const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
```

규칙:

- Client에서 Secret이 필요한 구조를 만들지 않는다.
- Secret이 필요한 외부 API 호출은 Browser에서 직접 수행하지 않고 Backend 또는 Server 측을 통해 처리한다.
- 단순히 접근이 편하다는 이유로 `NEXT_PUBLIC_`을 붙이지 않는다.

### 10.4 Build-time Public Variables

`NEXT_PUBLIC_` 환경변수는 Frontend Browser Bundle에 포함되는 공개 설정값으로 취급한다.

따라서 Docker Image를 Build한 이후 다른 환경에서 같은 Image를 재사용할 경우,
`NEXT_PUBLIC_` 값이 예상대로 Runtime에 변경되지 않을 수 있음을 고려한다.

예를 들어 다음 방식은 주의한다.

```text
Build
NEXT_PUBLIC_API_BASE_URL=https://dev-api.example.com

↓

동일 Image를 Production으로 이동

↓

Runtime에서
NEXT_PUBLIC_API_BASE_URL=https://prod-api.example.com
으로 바꿨다고 가정
```

Browser Bundle에 이미 값이 포함된 경우 Build 당시 값을 계속 사용할 수 있다.

따라서:

- `NEXT_PUBLIC_` 값은 Build 시점 설정값이라는 점을 고려한다.
- Docker Build 시 필요한 공개 환경변수가 있다면 Build 환경에서 명확히 주입한다.
- 배포 후 자주 변경되어야 하는 값을 무조건 `NEXT_PUBLIC_`로 만들지 않는다.
- 하나의 Docker Image를 여러 환경에 승격하여 사용할 계획이라면 Runtime 설정이 필요한지 별도로 설계한다.
- 미니프로젝트에서는 구조를 복잡하게 만들지 않고, Frontend API Base URL 정도의 공개값만 최소한으로 사용한다.

### 10.5 Frontend `.env` Usage

Frontend가 환경변수를 사용할 때도 실제 Secret을 별도 Frontend 파일에 복사하지 않는다.

금지 예:

```text
frontend/.env에 OPENAI_API_KEY 복사
frontend/.env.local에 DB_PASSWORD 복사
```

외부 AI API Key 및 DB 인증정보는 Backend에서 관리한다.

Frontend가 알아야 하는 것은 가능한 한 다음과 같은 공개 설정으로 제한한다.

```text
NEXT_PUBLIC_API_BASE_URL
```

### 10.6 Next.js Environment Checklist

새로운 Frontend 환경변수를 추가할 때 확인한다.

1. Browser에서 필요한 값인가?
2. 공개되어도 안전한 값인가?
3. Server에서만 사용할 수는 없는가?
4. `NEXT_PUBLIC_`이 정말 필요한가?
5. Docker Build 시점과 Runtime 중 언제 값이 결정되어야 하는가?
6. `.env.example`에 변수 이름이 추가되었는가?

## 11. Docker Configuration Rules

기본 구조:

```text
project-root/
├── .env
├── .env.example
├── compose.yml
├── frontend/
│   ├── Dockerfile
│   └── .dockerignore
└── backend/
    ├── Dockerfile
    └── .dockerignore
```

Compose는 루트의 `compose.yml` 하나를 기본으로 사용한다.

기본 Service:

```text
frontend
backend
database
```

Redis와 Kafka는 사용하지 않는다.

### 11.1 Compose Environment

환경변수 전달은 `env_file` 사용을 기본으로 한다.

예:

```yaml
services:
  backend:
    env_file:
      - .env
```

같은 환경변수를 `.env`, `env_file`, `environment`에 불필요하게 중복 선언하지 않는다.

명시적인 Override가 필요한 경우에만 `environment` 사용을 고려한다.

### 11.2 Local / Container Host Rules

실행 위치에 따라 Host의 의미가 다름을 반드시 구분한다.

Local Process에서 Docker Container로 접근:

```text
localhost:<published-port>
```

Docker Container에서 다른 Compose Service로 접근:

```text
<service-name>:<container-port>
```

예:

```text
Local FastAPI → Docker PostgreSQL
localhost:5432

Docker Backend → Docker PostgreSQL
database:5432
```

Container 내부에서 다른 Container를 가리키기 위해 `localhost`를 사용하지 않는다.

### 11.3 Docker Secret Rules

Dockerfile에 실제 Secret을 작성하지 않는다.

금지:

```dockerfile
ENV OPENAI_API_KEY=actual-key
ENV POSTGRES_PASSWORD=actual-password
```

Docker Image에 Secret 파일을 `COPY`하지 않는다.

`.dockerignore`에서 최소한 다음과 같은 민감 파일이 Build Context에 불필요하게 포함되지 않도록 관리한다.

```text
.env
.git
node_modules
.venv
```

프로젝트 규모상 별도의 Docker Secret 관리 시스템은 기본 요구사항으로 강제하지 않는다.
현재 개발/데모 환경에서는 `.env`와 Compose를 중심으로 관리한다.

### 11.4 AI Environment Rules

AI Coding Agent는 환경설정 작업에서 다음을 지킨다.

- `.env` 실제 값을 출력하지 않는다.
- `.env` 전체 내용을 응답이나 Log에 출력하지 않는다.
- Secret 값을 임의로 생성하여 코드에 넣지 않는다.
- Secret을 Source Code나 Dockerfile로 이동하지 않는다.
- 새로운 환경변수를 추가하면 `.env.example`도 함께 수정한다.
- 기존 환경변수 이름을 임의로 Rename하지 않는다.
- 기존 환경변수를 영향 범위 확인 없이 삭제하지 않는다.
- `NEXT_PUBLIC_`에 Secret을 넣지 않는다.
- Browser에서 필요하지 않은 값을 `NEXT_PUBLIC_`으로 만들지 않는다.
- Docker Container 간 주소에 `localhost`를 잘못 사용하지 않는다.
- 환경변수 변경으로 Backend, Frontend, Docker Compose 중 다른 영역이 영향을 받으면 변경 범위를 함께 확인한다.

## 12. Logging / Debugging

### print / console

-   `print()` / `console.log()`는 개발·디버깅 중 임시 사용 가능
-   Commit 전에 모두 제거
-   디버깅 출력이 남은 상태로 Commit 금지

### Logger

필요한 위치에만 사용한다.

권장: - 중요한 작업 시작/완료 - 외부 API 호출 실패 - DB 처리 실패 -
AI/OCR/STT 처리 실패 - 복구 가능한 비정상 상황 - 원인 추적이 필요한 예외

지양: - 단순 변수 확인 - 모든 함수 진입/종료 - 반복문마다 출력 - 추적
가치 없는 정상 처리

Level: - DEBUG: 개발 중 상세 추적 - INFO: 중요한 정상 처리 - WARNING:
비정상이나 처리 가능 - ERROR: 작업 실패

Traceback이 필요한 예외는 `logger.exception()`을 고려한다.

로그 금지 정보: - API Key, Password, Token, Secret - `.env` 전체 - DB
인증정보 - 불필요한 개인정보 - 필요하지 않은 사용자 입력 원문 전체

Debugging: - 오류 메시지와 Stack Trace를 먼저 확인 - 원인 확인 없이
`try/except`로 숨기지 않음 - 임시 Debug 출력은 Commit 전 제거 - 오류
수정 시 관련 없는 코드 변경 금지 - fallback/hard coding으로 문제를
숨기거나 테스트 통과 금지 - 수정 후 기존 기능 정상 동작 재확인 -
`except Exception: pass` 금지

## 13. AI Coding Agent Rules

Codex, Claude, Antigravity 등 모든 AI Coding Agent에 적용한다.

### 작업 전

-   관련 파일과 기존 구조를 먼저 확인
-   `PROJECT_RULES.md` 우선 확인
-   기존 Naming/구현 방식 확인

### 요청 범위

-   요청 범위 안에서만 작업
-   요청하지 않은 기능 추가 금지
-   관련 없는 파일 수정 금지
-   더 좋아 보인다는 이유만으로 대규모 Refactor 금지

### 구조

-   정해진 Folder/Layer 임의 변경 금지
-   새 최상위 Layer 임의 추가 금지
-   기존 파일/디렉터리의 불필요한 이동/Rename 금지

### API

다음을 임의 변경하지 않는다. - Endpoint URL - HTTP Method -
Request/Response Schema - 공통 Response 구조

변경 필요 시 사용자에게 먼저 알린다.

### Database

Table, Column, Data Type, PK/FK, Schema를 임의 변경하지 않는다. 변경
필요 시 SQL 변경사항과 영향 범위를 먼저 제시한다.

### Dependency

-   기존 Dependency로 해결 가능하면 새 Package 추가 금지
-   Python은 uv, Frontend는 npm 사용
-   요청과 관계없는 Dependency Upgrade 금지
-   lock 파일을 이유 없이 삭제/재생성하지 않음

### 오류 은폐

-   임의 fallback으로 오류 숨기기 금지
-   테스트 통과 목적 Hard Coding 금지
-   원인 확인 없는 광범위 `try/except` 금지
-   `except Exception: pass` 금지

### 임시 코드

Commit 전 제거: - `print()` - `console.log()` - 임시 Debug Code -
불필요한 임시 변수 - 사용하지 않는 코드 - 불필요하게 주석 처리된 기존
코드

### Git

사용자의 명시적 요청 없이 금지: - commit - push - merge - rebase -
reset - branch 삭제 - force push

### 기존 작업 보호

-   다른 팀원 코드 임의 덮어쓰기 금지
-   기존 변경사항 임의 Revert 금지
-   자신이 만들지 않은 수정사항 임의 삭제 금지
-   Conflict에서 임의로 한쪽 변경만 선택 금지

### 규칙 보호

-   작업 편의를 위한 `PROJECT_RULES.md` 임의 변경 금지
-   AI 자신의 일반 스타일보다 프로젝트 규칙 우선
-   요청과 규칙이 충돌하면 임의로 규칙을 깨지 말고 사용자에게 알림

### 자율 처리 가능 범위

기존 계약/구조를 바꾸지 않는 범위에서 다음은 자율 처리 가능: - 필요한
함수 분리 - 변수명 개선 - 필요한 Import - Type 지정 - 명백한 문법 오류
수정 - 요청 구현에 필요한 작은 내부 변경

핵심 기준: \> 기존 계약, 구조, 데이터, Dependency, Git 상태에 영향을
주는 변경은 보수적으로 처리하고, 정해진 구조 안에서의 구현은 자율적으로
처리한다.

### 작업 완료 보고

최소한 다음을 보고한다. - 변경 파일 - 주요 변경사항 - 실행/검증 내용 -
남은 문제 또는 확인 필요 사항
