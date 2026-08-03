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
PostgreSQL `news_articles`에 적재합니다. `database/schemas/0004_create_news_tables.sql`을
먼저 적용해야 합니다.

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

이미 적재된 기사는 상세 페이지를 열지 않고 건너뛰므로 같은 기간을 다시
수집해도 새 기사만 처리합니다. `url`에 `UNIQUE`가 걸려 있어 중복 적재도
발생하지 않습니다.

수집 중 일부 기사에 실패하면 성공한 기사를 적재한 뒤 종료 코드 `1`을
반환합니다. 자동화에서는 이 종료 코드를 실패로 처리하고 실패 기사 Log를
확인합니다. 검색 페이지 접근에 실패한 경우의 화면은 `--screenshot-directory`
위치(기본 `backend/cache/news/`)에 저장되며 Git에 포함되지 않습니다.

적재된 기사를 Gemini로 한 줄 요약할 때는 `GEMINI_API_KEY`를 설정한 뒤 다음
명령을 실행합니다. 기본 모델은 `gemini-3.1-flash-lite`입니다.

```text
cd backend
uv run python -m app.services.news_summary_batch
```

요약 배치는 `news_summaries`에 결과가 없거나 `status`가 `failed`인 기사만
조회하므로, 이미 요약된 기사는 처리 대상에 들어오지 않고 실패한 기사는 다음
실행에서 자동으로 재시도됩니다. 무료 티어의 요청 한도를 고려해 기본 요청
간격은 5초이며, 429 응답은 서버가 안내한 시간만큼 기다린 뒤 자동 재시도합니다.
소량만 점검하려면 `--limit 1`처럼 처리 건수를 지정합니다.

적재된 기사에 로컬 Gemma로 감성 판정을 붙일 때는 Ollama를 실행하고 다음 명령을
사용합니다. 판정과 근거는 `news_sentiments`, `news_sentiment_evidences`에 저장되며
판정이 없거나 실패한 기사만 처리합니다.

```text
cd backend
uv run python -m app.services.news_sentiment_batch
```

판정 결과를 Seed SQL로 내보내려면 다음을 실행합니다. Prompt를 고쳐 다시 판정한
뒤에도 같은 명령으로 `database/seeds/0003_news_sentiments.sql`을 재생성합니다.

```text
uv run python -m app.services.news_sentiment_seed
```

## 전체 파이프라인

수집, 한 줄 요약, 감성 판정을 순서대로 실행합니다.

```text
cd backend
uv run python -m app.services.news_pipeline --start 2026-08-03 --end 2026-08-03
```

각 단계가 이미 처리한 기사를 건너뛰므로 몇 번을 실행해도 결과가 같습니다. 한
단계가 실패해도 다음 단계를 계속 진행하는데, 앞선 실행에서 남은 미처리 기사는
수집 실패와 무관하게 분석할 수 있기 때문입니다. 한 단계라도 실패하면 종료 코드
`1`을 반환합니다.

| Option | 설명 |
| --- | --- |
| `--skip-collect` | 크롤링을 건너뜁니다. Chrome이 없는 환경에서 분석만 돌릴 때 사용합니다 |
| `--skip-summary` / `--skip-sentiment` | 해당 단계를 건너뜁니다 |
| `--limit` | 요약·판정 단계에서 각각 처리할 최대 기사 수 |

수집한 기사 원문은 Database에만 보관하며 Git에 추가하지 않습니다. 팀원이
데이터셋을 공유해야 할 때는 `database/seeds/`의 Seed SQL로 전달합니다.

## Docker 실행

Docker 실행 시 Compose가 Backend의 `POSTGRES_HOST`를 Service 이름인 `database`로 Override합니다.

```powershell
docker compose --env-file frontend/.env up --build
```
