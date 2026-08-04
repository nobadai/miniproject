# Frontend API 연동 명세서

`frontend/services/` 안의 함수를 실제 Backend API 호출로 교체하기 위한 안내 문서다.
2026-08-03에 `backend/app/routers/`, `backend/app/schemas/`를 직접 읽어 아래 10개
함수의 Endpoint·요청·응답 전부를 실제 코드 기준으로 확정했다("추정" 표시는 더 이상
없다). Backend 코드는 이 문서 갱신 과정에서 읽기만 했고 수정하지 않았다.

## 전체 요약

| 함수 | 파일 | 실제 Endpoint(확정) | 인증 필요 | 연결 위치 |
| --- | --- | --- | --- | --- |
| `analyzeFraudScreen` | `services/fraud_analysis.ts` | `POST /fraud-analysis` | 필요(쿠키) | `app/fraud-check/FraudCheckView.tsx` (`ScreenCheckPanel`) |
| `analyzeVoicePhishing` | `services/voice_phishing.ts` | `POST /voice-phishing/analysis` | 필요(쿠키) | `app/fraud-check/FraudCheckView.tsx` (`VoiceCheckPanel`) |
| `getNewsArticles` | `services/news.ts` | `GET /news` | 불필요 | `app/news/page.tsx`, `components/news/NewsBanner.tsx` |
| `getNewsArticleById` | `services/news.ts` | 없음(목록을 받아 `url`로 필터링) | 불필요 | `app/news/[url]/page.tsx` |
| `login` | `services/auth.ts` | `POST /auth/login` | 불필요 | `app/login/page.tsx` |
| `signup` | `services/auth.ts` | `POST /auth/signup` | 불필요 | `app/signup/page.tsx` |
| `logout` | `services/auth.ts` | `POST /auth/logout` | 필요(쿠키) | `components/commons/LogoutButton.tsx` → `app/mypage/page.tsx` |
| `getMyProfile` / `getMyProfileForServerComponent` | `services/user.ts` / `services/user_server.ts` | `GET /users/me` | 필요(쿠키) | `components/commons/Header.tsx`(Client), `app/mypage/page.tsx`·`app/mypage/edit/page.tsx`(Server) |
| `updateMyProfile` | `services/user.ts` | `PATCH /users/me` | 필요(쿠키) | `app/mypage/edit/EditProfileForm.tsx` |
| `withdrawMyAccount` | `services/user.ts` | `DELETE /users/me` | 필요(쿠키) | `app/mypage/withdraw/page.tsx` |

**10개 전부 실제 Endpoint를 확정하고 fetch 구현까지 완료**했다. `analyzeFraudScreen`/
`analyzeVoicePhishing`은 이전에도 확정이었고, 나머지 8개(뉴스/인증/마이페이지)는
이번에 `backend/app/routers/`, `backend/app/schemas/` 실제 코드로 처음 확정했다.

---

## 인증 공통 사항

Backend는 JWT를 `access_token`이라는 이름의 **HttpOnly 쿠키**에 담아 발급한다
(`backend/app/core/security.py`). 로그인 성공 시 Backend가 `Set-Cookie`로 발급하고,
로그아웃 시 같은 속성으로 삭제한다. `access_token` 쿠키가 필요한 Endpoint는 모두
`fetch` 옵션에 `credentials: "include"`가 있어야 브라우저가 쿠키를 저장·전송한다.

인증이 필요한 Endpoint에 쿠키 없이(비로그인 상태로) 요청하면 `backend/app/core/dependencies.py`의
`get_current_user`가 **401**과 함께 FastAPI 기본 오류 형식 `{"detail": "인증이 필요합니다."}`을
반환한다(공통 `ApiResponse` 포맷이 아님). `frontend/utils/api_client.ts`의
`unwrapApiResponse`는 `message`가 없으면 `detail`을 보조로 읽으므로, 이 경우 화면에는
그대로 **"인증이 필요합니다."** 에러가 표시된다 — 비로그인 상태로 사기화면/보이스피싱
판별을 시도하면 이 메시지가 뜨는 것이 정상 동작이다.

로그아웃(`POST /auth/logout`)과 회원탈퇴(`DELETE /users/me`)는 **204 No Content**로
Body가 없다. `unwrapApiResponse`는 `response.status === 204`를 성공으로 간주해 바로
반환한다(JSON 파싱을 시도하지 않는다).

---

## 1. `analyzeFraudScreen`

- **파일**: `frontend/services/fraud_analysis.ts`
- **시그니처**: `analyzeFraudScreen(file: File): Promise<FraudAnalysisResult>`
- **Endpoint**: `POST /fraud-analysis` (`multipart/form-data`, 필드명 `file`) — **인증 필요**
  (`backend/app/routers/fraud_analysis.py`의 `current_user: CurrentUser` 의존성).
- **요청/응답 타입 대조**: 일치. `backend/app/schemas/fraud_analysis.py`의
  `FraudAnalysisResult`(`verdict`, `tamper_types`, `reasoning`, `confidence`,
  `undetermined_reason`)와 `frontend/types/fraud_analysis.ts`가 동일하다.
- **호출 위치**: `app/fraud-check/FraudCheckView.tsx`의 `ScreenCheckPanel`.
- **상태**: 완료. 비로그인 상태로 호출하면 401 → "인증이 필요합니다." 에러 배너가 뜬다.

## 2. `analyzeVoicePhishing`

- **파일**: `frontend/services/voice_phishing.ts`
- **시그니처**: `analyzeVoicePhishing(file: File): Promise<VoicePhishingAnalysis>`
- **Endpoint**: `POST /voice-phishing/analysis` (`multipart/form-data`, 필드명 `file`) —
  **인증 필요**(`backend/app/routers/voice_phishing.py`의 `current_user: CurrentUser`).
- **요청/응답 타입 대조**: 일치.
- **호출 위치**: `app/fraud-check/FraudCheckView.tsx`의 `VoiceCheckPanel`.
- **상태**: 완료. Backend 라우터가 실패 시(파일명 없음, 200MB 초과, 빈 파일, 지원하지
  않는 형식, 서버 오류)에도 `HTTPException`을 던지지 않고 `response.status_code`를
  직접 바꾸며 `ApiResponse{success:false, message}`를 반환한다 — `unwrapApiResponse`가
  HTTP 상태와 무관하게 `success` 필드로 판단하므로 정상 처리된다. 단, **인증 실패
  (401)만은 `CurrentUser` 의존성이 Handler 진입 전에 걸어서 여전히 FastAPI
  `HTTPException` 형태(`{"detail": "..."}）**로 온다.

## 3. `getNewsArticles`

- **파일**: `frontend/services/news.ts`
- **시그니처**: `getNewsArticles(): Promise<NewsArticle[]>`
- **Endpoint**: `GET /news` (확정 — 이전에는 `/news-article`로 잘못 추정했었다.
  `backend/app/routers/news.py`가 파일명 `news.py` 기준 `/news` Prefix로 자동 등록됨).
- **응답 구조(확정)**: `backend/app/schemas/news.py`의 `News` 그대로.
  - `market_date`(date), `brief_type`("morning" | "closing"), `title`, `published_at`(datetime),
    `url`, `source`, `body`
  - `summary: string | null` — 요약 배치가 아직 처리하지 않은 기사는 `null`
  - `label: "POS" | "NEU" | "NEG" | null` — 감성 판정 배치가 아직 처리하지 않은 기사는 `null`
    (`backend/app/clients/gemma_client.py`의 `SENTIMENT_SCHEMA`가 정한 값)
  - `evidence: {sentence: string, is_quote: boolean}[]` — 판정 근거 문장 배열(0개 이상)
  - **`id` 필드가 없다.** `News` Response Schema는 의도적으로 id를 빼서 화면에 내부
    식별자가 노출되지 않게 막아뒀다(`backend/app/schemas/news.py` 주석 참고).
- **Frontend 대응**: `frontend/types/news.ts`를 위 구조 그대로 재정의했다. 이전에 있던
  `id`(number), `session`("morning"|"close"), `sentiment`("pos"|"neg"|"neu"),
  `sessionLabel`, `time`, `reason` 필드는 전부 삭제했다(더미 데이터 전용 필드였음).
- **호출 위치**: `app/news/page.tsx`(Server), `components/news/NewsBanner.tsx`(Client).
- **상태**: 완료. `components/news/news_data.ts`(더미 배열)는 삭제했고, 감성/시황 표시용
  상수는 `components/news/news_labels.ts`로 새로 뺐다.

## 4. `getNewsArticleById`

- **파일**: `frontend/services/news.ts`
- **시그니처**: `getNewsArticleById(articleUrl: string): Promise<NewsArticle | null>`
- **Endpoint**: 없음(단건 조회 API 미제공, 확정). `getNewsArticles()`로 전체 목록을 받아
  `article.url === articleUrl`로 필터링한다.
- **식별자 변경**: Backend에 `id`가 없어 원문 URL(`url`)을 고유 키로 쓴다. 라우트 폴더를
  `app/news/[id]/` → `app/news/[url]/`로 이름을 바꿨고, 링크는
  `/news/${encodeURIComponent(article.url)}`로 생성한다. 상세 페이지에서는
  `decodeURIComponent`로 되돌려 조회한다.
- **호출 위치**: `app/news/[url]/page.tsx`.
- **상태**: 완료.

## 5. `login`

- **파일**: `frontend/services/auth.ts`
- **시그니처**: `login(payload: LoginPayload): Promise<UserProfile>` — `LoginPayload{email, password}`
- **Endpoint**: `POST /auth/login` (확정 — `backend/app/routers/auth.py`). 성공 시 200 +
  `ApiResponse<UserResponse>`, 응답 Header에 `Set-Cookie: access_token=...`(HttpOnly).
  실패(이메일/비밀번호 불일치) 시 401 + `{"detail": "이메일 또는 비밀번호가 올바르지
  않습니다."}`.
- **요청/응답 타입 대조**: 일치(아래 `UserResponse` 참고).
- **호출 위치**: `app/login/page.tsx`.
- **상태**: 완료.

## 6. `signup`

- **파일**: `frontend/services/auth.ts`
- **시그니처**: `signup(payload: SignupPayload): Promise<UserProfile>` — `SignupPayload{name, email, password}`
- **Endpoint**: `POST /auth/signup` (확정). 성공 시 201 + `ApiResponse<UserResponse>`.
  이메일 중복 시 409 + `{"detail": "이미 가입된 이메일입니다."}`.
- **요청 타입 변경**: Backend `SignupRequest`(`backend/app/schemas/auth.py`)는
  `email`/`password`/`name`만 받고 `model_config = ConfigDict(extra="forbid")`라서
  다른 필드(`phone` 등)를 보내면 422가 난다. 기존 `SignupPayload`에 있던 `phone`
  필드를 제거했고, 회원가입 화면의 휴대폰 번호 입력란도 함께 지웠다.
- **호출 위치**: `app/signup/page.tsx`.
- **상태**: 완료.

## 7. `logout`

- **파일**: `frontend/services/auth.ts`
- **시그니처**: `logout(): Promise<void>`
- **Endpoint**: `POST /auth/logout` (확정). 성공 시 **204 No Content**(Body 없음), 인증
  쿠키를 삭제한다.
- **호출 위치**: `app/mypage/page.tsx`의 "로그아웃" — 쿠키 삭제 요청이 필요해 Client
  Component `components/commons/LogoutButton.tsx`로 분리했다. 클릭하면 `logout()`을
  호출한 뒤(실패해도) `/login`으로 이동한다.
- **상태**: 완료(이번 작업에서 새로 연결).

## 8. `getMyProfile` / `getMyProfileForServerComponent`

- **파일**: `frontend/services/user.ts`(Client 전용) / `frontend/services/user_server.ts`(Server 전용)
- **시그니처**: `(): Promise<UserProfile>`
- **Endpoint**: `GET /users/me` (확정 — `backend/app/routers/users.py`). 200 +
  `ApiResponse<UserResponse>`. 비로그인 시 401.
- **응답 타입(확정) — `UserResponse`**(`backend/app/schemas/user.py`):
  ```
  { id: number, email: string, name: string, is_active: boolean,
    created_at: string, updated_at: string }
  ```
  이전에 Frontend가 추정으로 넣어뒀던 `phone`, `joinedAt` 필드는 실제 Backend에
  없어 `frontend/types/user.ts`에서 제거했다. 가입일이 필요하면 `created_at`을
  그대로 쓰거나 화면에서 포맷한다(`app/mypage/page.tsx`의 `formatJoinedDate` 참고).
- **Server Component 호출 이슈**: `credentials: "include"`는 Browser fetch에서만
  로그인 쿠키를 자동으로 실어준다. `app/mypage/page.tsx`, `app/mypage/edit/page.tsx`는
  Server Component라 그냥 `getMyProfile()`을 쓰면 방문자의 쿠키가 전달되지 않아 항상
  미인증 상태로 응답받는다. 그래서 `next/headers`의 `cookies()`로 들어온 요청의
  쿠키를 그대로 실어 보내는 `getMyProfileForServerComponent`를
  `services/user_server.ts`에 별도로 뒀다(`next/headers`는 Server 전용 API라
  Client Component인 `Header.tsx`가 import하는 `user.ts`와 파일을 분리해야 함).
- **호출 위치**: `components/commons/Header.tsx`(Client → `user.ts`),
  `app/mypage/page.tsx`, `app/mypage/edit/page.tsx`(Server → `user_server.ts`).
- **상태**: 완료.

## 9. `updateMyProfile`

- **파일**: `frontend/services/user.ts`
- **시그니처**: `updateMyProfile(payload: UpdateProfilePayload): Promise<UserProfile>`
- **Endpoint**: `PATCH /users/me` (확정). 200 + `ApiResponse<UserResponse>`.
- **요청 타입(확정) — `UserUpdateRequest`**(`backend/app/schemas/user.py`,
  `extra="forbid"`):
  ```
  { name?: string, current_password?: string, new_password?: string }
  ```
  `phone` 필드는 없어 제거했다. **검증 규칙**(`validate_update_fields`):
  - `name`과 `new_password`가 둘 다 없으면 실패("이름 또는 새 비밀번호 중 하나
    이상이 필요합니다.")
  - `new_password`를 보내려면 `current_password`도 함께 보내야 하고 그 반대도 마찬가지
  - `new_password`는 `current_password`와 달라야 한다
  - 위반 시 422, 현재 비밀번호가 틀리면 401(`{"detail": "현재 비밀번호가 올바르지
    않습니다."}`)
- **호출 위치**: `app/mypage/edit/EditProfileForm.tsx`(신규 Client Component, "저장하기"
  버튼) — 이름/비밀번호 폼 값을 위 검증 규칙에 맞게 조립해 호출한다. `app/mypage/edit/page.tsx`는
  Server Component로 남기고 프로필 조회(`getMyProfileForServerComponent`)만 담당한다.
- **상태**: 완료(이번 작업에서 새로 연결).

## 10. `withdrawMyAccount`

- **파일**: `frontend/services/user.ts`
- **시그니처**: `withdrawMyAccount(password: string): Promise<void>`
- **Endpoint**: `DELETE /users/me` (확정). 성공 시 **204 No Content**, 소프트 삭제 후
  인증 쿠키를 삭제한다. 현재 비밀번호가 틀리면 401.
- **요청 타입**: `UserDeleteRequest{password}` — 기존 구현과 이미 일치했다.
- **호출 위치**: `app/mypage/withdraw/page.tsx` — 정적 안내 화면이었던 것을 Client
  Component로 바꿔 비밀번호 입력 + 동의 체크박스 + "탈퇴하기" 버튼에 연결했다. 성공
  시 `/`로 이동한다.
- **상태**: 완료(이번 작업에서 새로 연결).

---

## 참고 — 남은 것 / 검증 안 된 것

- **인증 상태 전역 관리 없음.** 로그인 성공 후 "로그인했다"는 사실을 Header 등
  다른 화면이 아는 방법이 없다(항상 `getMyProfile()`을 시도해 성공하면 로그인된
  것으로 간주하는 구조). 전역 상태(Context 등)는 여전히 범위 밖이다.
- **실제 Backend 서버 대상 검증 여부는 작업 시점의 최종 보고를 확인할 것.** 이
  문서는 코드 대조 결과만 다루며, 브라우저로 직접 눌러본 결과는 다루지 않는다.
