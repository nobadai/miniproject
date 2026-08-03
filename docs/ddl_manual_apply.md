# DDL 수동 적용 안내

## 1. 문서 목적

이 문서는 `database/schemas/0002_create_voice_phishing_tables.sql`을 이미 사용 중인 Local Database에 적용하는 방법을 설명한다.

보이스피싱 업로드 파일과 분석 결과를 저장하는 Table 두 개가 이 SQL로 추가되었다. **이미 Database Volume을 만들어 둔 팀원은 이 문서의 명령을 한 번 실행해야 한다.**

## 2. 왜 수동 적용이 필요한가

`compose.yml`은 `database/schemas/`를 Container의 `/docker-entrypoint-initdb.d`에 연결한다. 이 디렉터리의 SQL은 **Database Volume이 비어 있을 때 최초 1회만** 실행된다.

| 상황 | 동작 |
| --- | --- |
| 처음 프로젝트를 받는 팀원 | `schemas/`의 모든 SQL이 자동 실행된다. **할 일 없음** |
| 이미 `docker compose up`을 한 적이 있는 팀원 | Volume에 데이터가 있어 SQL이 실행되지 않는다. **수동 적용 필요** |

Container를 재시작하거나 SQL 파일을 수정해도 다시 실행되지 않는다. 기존 Volume을 그대로 두면서 Table을 추가하려면 아래 명령으로 직접 적용해야 한다.

## 3. 적용이 필요한지 확인

프로젝트 Root에서 실행한다.

```bash
docker compose exec -T database psql -U finance_ai -d finance_ai -c "\dt"
```

`voice_phishing_uploads`와 `voice_phishing_analyses`가 보이면 이미 적용된 상태이므로 더 할 일이 없다.

## 4. 적용 명령

Database Container가 실행 중이어야 한다. 실행 중이 아니면 먼저 올린다.

```bash
docker compose up -d database
```

프로젝트 Root에서 다음을 실행한다.

```bash
docker compose exec -T database psql -U finance_ai -d finance_ai -v ON_ERROR_STOP=1 -f /docker-entrypoint-initdb.d/0002_create_voice_phishing_tables.sql
```

정상 결과는 다음과 같다.

```text
CREATE TABLE
CREATE TABLE
CREATE INDEX
```

이미 적용된 상태에서 다시 실행해도 안전하다. SQL이 `CREATE TABLE IF NOT EXISTS`로 작성되어 있어 `already exists, skipping` NOTICE만 출력되고 기존 데이터는 그대로 유지된다.

## 5. 적용 확인

```bash
docker compose exec -T database psql -U finance_ai -d finance_ai -c "\d voice_phishing_uploads"
docker compose exec -T database psql -U finance_ai -d finance_ai -c "\d voice_phishing_analyses"
```

`voice_phishing_uploads`는 7개, `voice_phishing_analyses`는 14개 Column이 나와야 한다. 특히 `voice_phishing_analyses`에 `prediction` Column이 있는지 확인한다.

Column 수만 빠르게 확인하려면 다음을 사용한다.

```bash
docker compose exec -T database psql -U finance_ai -d finance_ai -c "select table_name, count(*) as columns from information_schema.columns where table_name like 'voice_phishing%' group by table_name order by 1"
```

## 6. 주의: PowerShell에서 Pipe로 SQL을 넘기지 않는다

다음 방식은 사용하지 않는다.

```powershell
# 금지
Get-Content database/schemas/0002_create_voice_phishing_tables.sql -Raw | docker exec -i miniproject-database-1 psql -U finance_ai -d finance_ai
```

PowerShell Pipe를 통과하면서 SQL 일부가 유실될 수 있다. 실제로 이 방식으로 적용했을 때 `prediction` Column이 빠진 채 Table이 생성되었고, Insert 단계에서 `UndefinedColumn` 오류가 발생했다.

`4. 적용 명령`처럼 파일 경로를 `-f`로 지정하면 psql이 파일을 직접 읽으므로 이 문제가 없다.

## 7. Docker Compose를 쓰지 않는 경우

psql Client가 있다면 Container를 거치지 않고 Repository의 SQL 파일을 직접 지정해도 된다. 프로젝트 Root에서 실행한다.

```bash
psql -h localhost -p 5432 -U finance_ai -d finance_ai -v ON_ERROR_STOP=1 -f database/schemas/0002_create_voice_phishing_tables.sql
```

`psql`이 PATH에 없으면 전체 경로로 실행한다. pgAdmin이나 PostgreSQL을 설치한 적이 있다면 대부분 아래 위치에 함께 들어 있다.

```powershell
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -h localhost -U finance_ai -d finance_ai -v ON_ERROR_STOP=1 -f database\schemas\0002_create_voice_phishing_tables.sql
```

Client와 Server의 Major Version이 달라도 이 SQL을 적용하는 데는 문제가 없다. psql 16 Client로 PostgreSQL 18 Server에 적용해 동일한 결과를 확인했다.

한글 주석 때문에 Encoding이 걱정된다면 아래를 먼저 설정한다. 검증 환경에서는 설정하지 않아도 정상 적용되었으나, Console Codepage가 다른 환경을 위한 안전장치다.

```powershell
$env:PGCLIENTENCODING = "UTF8"
```

**Local에 직접 설치한 PostgreSQL Service를 함께 쓰고 있다면** 두 Server가 모두 5432를 사용하려 해 충돌한다. 어느 쪽에 접속했는지 헷갈리기도 쉬우므로, Docker Database를 쓰는 동안에는 Local Service를 정지해 둔다.

```powershell
Get-Service postgresql*
```

## 8. 참고: Volume을 지우고 다시 만드는 방법

Volume을 삭제하면 초기화 SQL이 다시 실행되어 수동 적용이 필요 없다.

```bash
docker compose down -v
docker compose up -d database
```

다만 `-v`는 **Database의 기존 데이터를 모두 삭제**하며 되돌릴 수 없다. 남겨야 할 데이터가 있는지 반드시 먼저 확인한다. 기본 선택지는 `4. 적용 명령`의 수동 적용이다.

## 9. 이 SQL이 추가하는 Table

| Table | 역할 |
| --- | --- |
| `voice_phishing_uploads` | 업로드한 오디오/영상의 원본 파일명, 저장 경로, 내용 해시, 크기 |
| `voice_phishing_analyses` | 업로드 건별 분석 결과. 판정, 각 점수, 근거, 발화 목록 |

원본 파일 자체는 Database가 아니라 `backend/uploads/`에 보관하고, Table에는 저장 경로만 남는다. 두 Table은 `upload_id`로 연결되며 업로드를 삭제하면 분석 이력도 함께 삭제된다.
