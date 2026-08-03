# Finance AI Mini Project

팀 공통 개발 환경과 애플리케이션 골격입니다. 실제 서비스 기능은 포함하지 않습니다.

## 준비 사항

- Python 3.12
- uv
- Node.js 24
- npm
- Docker 및 Docker Compose

Frontend와 Backend의 `.env.example`을 각각 `.env`로 복사한 뒤 필수 값을 입력합니다.

macOS/Linux:

```bash
cp frontend/.env.example frontend/.env
cp backend/.env.example backend/.env
```

Windows PowerShell:

```powershell
Copy-Item frontend/.env.example frontend/.env
Copy-Item backend/.env.example backend/.env
```

## 로컬 실행

```text
docker compose up -d database

cd backend
uv sync --frozen
uv run uvicorn app.main:app --reload
```

Frontend는 별도 Terminal에서 실행합니다.

macOS/Linux:

```bash
cd frontend
npm ci
npm run dev
```

Windows PowerShell:

```powershell
cd frontend
npm ci
npm run dev
```

로컬 Backend는 `backend/.env`의 `localhost` Database 주소를 사용합니다.

## 금융 뉴스 수집

파이낸셜뉴스의 `[fn오전시황]`, `[fn마감시황]` 기사를 Selenium으로 수집해
내부 검수용 JSONL과 CSV로 저장합니다. 기본 저장 위치인
`backend/cache/news/`는 Git에 포함되지 않습니다.

```text
cd backend
uv run python -m app.services.news_collector --start 2026-07-13 --end 2026-07-31
```

크롤러는 Chrome이 설치된 macOS 또는 Windows 호스트에서 실행합니다. Selenium
Manager가 운영체제에 맞는 Driver를 관리하므로 별도 Driver 경로는 지정하지
않지만, 첫 실행 시 다운로드를 위한 인터넷 연결이 필요할 수 있습니다. 현재
Backend Docker Image에는 브라우저 실행 환경이 없으므로 Container 안에서는
크롤러를 실행하지 않습니다. 실행 날짜만 수집할 때는 날짜 인수를 생략할 수
있습니다.

수집 중 일부 기사에 실패하면 정상 기사와 오류 파일을 모두 저장한 뒤 종료 코드
`1`을 반환합니다. 자동화에서는 이 종료 코드를 실패로 처리하고
`fn_market_errors.jsonl`을 확인합니다.

수집 결과 전체를 Gemini로 한 줄 요약할 때는 `GEMINI_API_KEY`를 설정한 뒤
다음 명령을 실행합니다. 기본 모델은 `gemini-3.1-flash-lite`이며, 완료된 원문
URL은 다음 실행에서 자동으로 건너뜁니다.

```text
cd backend
uv run python -m app.services.news_summary_batch
```

요약과 오류 결과는 기본적으로 `backend/cache/news/`에 즉시 저장되며 Git에
포함되지 않습니다. 무료 티어의 요청 한도를 고려해 기본 요청 간격은 5초이며,
429 응답은 서버가 안내한 시간만큼 기다린 뒤 자동 재시도합니다. 소량만
점검하려면 `--limit 1`처럼 처리 건수를 지정합니다.

원문·요약 결과가 저장되는 `backend/cache/`는 Git에 포함되지 않습니다. 팀원이
데이터셋을 사용해야 할 때는 승인된 공유 저장소로 별도 전달하거나 PostgreSQL
적재 후 공유하며, 원문 전체를 임의로 Git에 추가하지 않습니다.

## Docker 실행

Docker 실행 시 Compose가 Backend의 `POSTGRES_HOST`를 Service 이름인 `database`로 Override합니다.

```powershell
docker compose --env-file frontend/.env up --build
```
