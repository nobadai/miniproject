# Finance AI Mini Project

팀 공통 개발 환경과 애플리케이션 골격입니다. 실제 서비스 기능은 포함하지 않습니다.

## 준비 사항

- Python 3.12
- uv
- Node.js 24
- npm
- Docker 및 Docker Compose

Frontend와 Backend의 `.env.example`을 각각 `.env`로 복사한 뒤 필수 값을 입력합니다.

```powershell
Copy-Item frontend/.env.example frontend/.env
Copy-Item backend/.env.example backend/.env
```

## 로컬 실행

```powershell
docker compose up -d database

cd backend
uv sync --frozen
uv run uvicorn app.main:app --reload

cd ..\frontend
npm ci
npm run dev
```

로컬 Backend는 `backend/.env`의 `localhost` Database 주소를 사용합니다.

## Docker 실행

Docker 실행 시 Compose가 Backend의 `POSTGRES_HOST`를 Service 이름인 `database`로 Override합니다.

```powershell
docker compose --env-file frontend/.env up --build
```
