# Frontend API 연동 명세서

`frontend/services/` 안의 함수를 실제 Backend API 호출로 교체하기 위한 안내 문서다.
"확정" 표시가 없는 기능(로그인/회원가입/마이페이지/뉴스)은 아직 Backend API 자체가
없어 Frontend에서 추정으로 만든 타입/함수이며, 실제 스펙이 나오면 필드명·엔드포인트가
달라질 수 있다.

## 전체 요약

| 함수 | 파일 | 엔드포인트 확정 여부 | 연결 위치 |
| --- | --- | --- | --- |
| `analyzeFraudScreen` | `services/fraud_analysis.ts` | **확정** — `POST /fraud-analysis` | `app/fraud-check/FraudCheckView.tsx` (`ScreenCheckPanel`) |
| `analyzeVoicePhishing` | `services/voice_phishing.ts` | **확정** — `POST /voice-phishing/analysis` | `app/fraud-check/FraudCheckView.tsx` (`VoiceCheckPanel`) |
| `getNewsArticles` | `services/news.ts` | 미확정 — 백엔드 미구현 (프론트 추정) | `app/news/page.tsx`, `components/news/NewsBanner.tsx` |
| `getNewsArticleById` | `services/news.ts` | 미확정 — 백엔드 미구현 (프론트 추정) | `app/news/[id]/page.tsx` |
| `login` | `services/auth.ts` | 미확정 — 백엔드 미구현 (프론트 추정) | `app/login/page.tsx` |
| `signup` | `services/auth.ts` | 미확정 — 백엔드 미구현 (프론트 추정) | `app/signup/page.tsx` |
| `logout` | `services/auth.ts` | 미확정 — 백엔드 미구현 (프론트 추정) | 없음 — 아직 어디서도 호출하지 않음 |
| `getMyProfile` | `services/user.ts` | 미확정 — 백엔드 미구현 (프론트 추정) | `components/commons/Header.tsx`, `app/mypage/page.tsx`, `app/mypage/edit/page.tsx` |
| `updateMyProfile` | `services/user.ts` | 미확정 — 백엔드 미구현 (프론트 추정) | 없음 — 아직 어디서도 호출하지 않음 |
| `withdrawMyAccount` | `services/user.ts` | 미확정 — 백엔드 미구현 (프론트 추정) | 없음 — 아직 어디서도 호출하지 않음 |

**확정 2개(사기화면/보이스피싱)** — 실제 Backend Pydantic Schema와 필드 단위로 대조 완료.
**미확정 8개(뉴스/인증/마이페이지)** — Backend API 자체가 없어 Frontend 추정치.

---

## 1. `analyzeFraudScreen`

- **파일**: `frontend/services/fraud_analysis.ts`
- **시그니처**: `analyzeFraudScreen(file: File): Promise<FraudAnalysisResult>`
- **엔드포인트**: **확정** — `POST /fraud-analysis` (`multipart/form-data`, 필드명 `file`)
- **요청/응답 타입 대조**: **일치**. `backend/app/schemas/fraud_analysis.py`의 `FraudAnalysisResult`(`verdict`, `tamper_types`, `reasoning`, `confidence`, `undetermined_reason`)와 `frontend/types/fraud_analysis.ts`의 `FraudAnalysisResult`가 필드명·타입·`verdict` 리터럴 3종까지 동일하다.
- **호출 위치**: `app/fraud-check/FraudCheckView.tsx`의 `ScreenCheckPanel` — "판별하기" 버튼 클릭 시 `handleAnalyze`에서 호출하고, 성공하면 `FraudResultCard`에 결과를 props로 전달한다.
- **끝나는지**: **거의 끝난다.** 함수 내부의 `throw new Error("not implemented")`를 실제 `fetch(NEXT_PUBLIC_API_BASE_URL + "/fraud-analysis", { method: "POST", body: formData })` 호출로 바꾸고, 응답 JSON에서 `ApiResponse<FraudAnalysisResult>`의 `data`를 꺼내 반환하도록만 고치면 된다. 호출부(`FraudCheckView.tsx`)는 이미 로딩/에러/결과 상태까지 연결되어 있어 추가로 손볼 필요가 없다.

## 2. `analyzeVoicePhishing`

- **파일**: `frontend/services/voice_phishing.ts`
- **시그니처**: `analyzeVoicePhishing(file: File): Promise<VoicePhishingAnalysis>`
- **엔드포인트**: **확정** — `POST /voice-phishing/analysis` (`multipart/form-data`, 필드명 `file`)
- **요청/응답 타입 대조**: **일치**. `backend/app/schemas/voice_phishing.py`의 `VoicePhishingAnalysis`(`audio_filename`, `transcript_id`, `prediction`, `fusion_raw_score`, `fusion_score`, `rule_score`, `rule_categories`, `sequence_score`, `transitions`, `koelectra_score`, `decision_reason`, `turns[].{idx,speaker,text}`)와 `frontend/types/voice_phishing.ts`가 필드 순서까지 동일하다.
- **호출 위치**: `app/fraud-check/FraudCheckView.tsx`의 `VoiceCheckPanel` — "판별하기" 버튼 클릭 시 `handleAnalyze`에서 호출하고, 성공하면 `VoicePhishingResultCard`에 결과를 props로 전달한다.
- **끝나는지**: **거의 끝난다.** `analyzeFraudScreen`과 동일한 패턴으로 `fetch` 호출만 채우면 된다. 다만 백엔드 라우터(`backend/app/routers/voice_phishing.py`)는 실패 시에도 `200`이 아니라 상태 코드를 `response.status_code`로 직접 바꿔 `ApiResponse{success:false}`를 반환하는 방식이라(HTTPException을 던지지 않음), 성공 실패를 `success` 필드로도 판단해야 하는지 확인이 필요하다. 이 부분만 유의하면 된다.

## 3. `getNewsArticles`

- **파일**: `frontend/services/news.ts`
- **시그니처**: `getNewsArticles(): Promise<NewsArticle[]>`
- **엔드포인트**: **미확정 — 백엔드 미구현.** `PROJECT_RULES.md`의 URL 네이밍 예시(`news_article.py` → `/news-article`)를 참고해 임시로 `GET /news-article`을 TODO 주석에 적어뒀을 뿐, 실제로 만들어진 라우터는 아니다.
- **요청/응답 타입 대조**: **백엔드 미확정 — 대조 불가.** `frontend/types/news.ts`의 `NewsArticle`(`sessionLabel` 등 camelCase)은 전부 Frontend 추정 타입이라 실제 백엔드 스키마와 비교할 대상 자체가 없다.
- **호출 위치**: `app/news/page.tsx`(Server Component, 페이지 진입 시 호출 후 `NewsListView`에 결과를 props로 전달), `components/news/NewsBanner.tsx`(Client Component, `useEffect`에서 호출).
- **끝나는지**: **아니다, 구조 정리가 더 필요하다.** 지금은 `components/news/news_data.ts`의 더미 배열을 그대로 반환하는 상태다(실제 fetch 아님). 실제 연동 시:
  1. 백엔드 응답이 snake_case라면, 이 함수 내부에서 fetch 응답을 받아 `NewsArticle`(camelCase)로 매핑하는 코드가 추가로 필요하다(현재는 그냥 그대로 반환만 함).
  2. 이 함수가 `components/news/news_data.ts`를 import하고 있는데, 실제 fetch로 바뀌면 이 import는 제거해야 한다.

## 4. `getNewsArticleById`

- **파일**: `frontend/services/news.ts`
- **시그니처**: `getNewsArticleById(id: number): Promise<NewsArticle | null>`
- **엔드포인트**: **미확정 — 백엔드 미구현.** TODO 주석에 `GET /news-article/{id}`로 적어뒀으나 실제 라우터는 없다.
- **요청/응답 타입 대조**: **백엔드 미확정 — 대조 불가.**
- **호출 위치**: `app/news/[id]/page.tsx`(Server Component) — `params`의 `id`를 숫자로 변환해 호출하고, 결과가 없으면 `notFound()`.
- **끝나는지**: `getNewsArticles`와 동일한 이유로 **아니다.** 다만 호출부는 이미 `notFound()` 처리까지 되어 있어 추가로 손볼 필요는 없다.

## 5. `login`

- **파일**: `frontend/services/auth.ts`
- **시그니처**: `login(payload: LoginPayload): Promise<UserProfile>` — `LoginPayload{email, password}`
- **엔드포인트**: **미확정 — 백엔드 미구현.**
- **요청/응답 타입 대조**: **백엔드 미확정 — 대조 불가.** `LoginPayload`/`UserProfile` 필드명은 전부 Frontend 추정.
- **호출 위치**: `app/login/page.tsx` — 로그인 폼 `onSubmit`에서 `FormData`로 `email`/`password`를 모아 호출하고, 성공하면 `/`로 이동, 실패하면 에러 배너를 보여준다.
- **끝나는지**: **아니다, 추가로 손볼 게 있다.**
  1. 실제 인증이 세션/쿠키 기반인지 토큰 기반인지에 따라 로그인 성공 후 토큰/세션을 어디에 저장할지(쿠키, localStorage 등) 정해야 하는데, 지금은 그 저장 로직이 전혀 없다.
  2. `Header.tsx`/`mypage`가 "로그인 상태"를 아는 방법이 지금은 없다(항상 `getMyProfile()`을 시도하는 구조). 로그인 여부에 따라 다르게 동작해야 한다면 별도 상태 관리(전역 상태, Context 등)가 필요하며, 이건 이번 작업 범위 밖이라 손대지 않았다.

## 6. `signup`

- **파일**: `frontend/services/auth.ts`
- **시그니처**: `signup(payload: SignupPayload): Promise<UserProfile>` — `SignupPayload{name, email, password, phone}`
- **엔드포인트**: **미확정 — 백엔드 미구현.**
- **요청/응답 타입 대조**: **백엔드 미확정 — 대조 불가.**
- **호출 위치**: `app/signup/page.tsx` — 가입 폼 `onSubmit`에서 `FormData`로 값을 모아 호출하고, 성공하면 `/login`으로 이동, 실패하면 에러 배너.
- **끝나는지**: 위 `login`과 동일한 이유(인증 상태 관리 미구현)로 **아니다.** 다만 화면의 폼 제출 흐름 자체는 fetch로 바꾸기만 하면 된다.

## 7. `logout`

- **파일**: `frontend/services/auth.ts`
- **시그니처**: `logout(): Promise<void>`
- **엔드포인트**: **미확정 — 백엔드 미구현.**
- **요청/응답 타입 대조**: 응답 타입 없음(`void`).
- **호출 위치**: **없음.** `app/mypage/page.tsx`의 "로그아웃" 메뉴는 지금 `logout()`을 호출하지 않고 그냥 `/login`으로 이동하는 `Link`다. 이번 요청 범위(로그인/회원가입 버튼만 연결)에 포함되지 않아 그대로 두었다.
- **끝나는지**: **아니다.** 함수 구현은 물론, `app/mypage/page.tsx`의 "로그아웃" `Link`를 `logout()`을 호출하는 버튼으로 바꾸는 작업이 추가로 필요하다.

## 8. `getMyProfile`

- **파일**: `frontend/services/user.ts`
- **시그니처**: `getMyProfile(): Promise<UserProfile>`
- **엔드포인트**: **미확정 — 백엔드 미구현.** TODO 주석엔 `GET /users/me`로 적어뒀으나 실제 라우터는 없다.
- **요청/응답 타입 대조**: **백엔드 미확정 — 대조 불가.**
- **호출 위치**: `components/commons/Header.tsx`(Client, `useEffect`에서 호출해 계정 영역에 표시), `app/mypage/page.tsx`(Server, 프로필 카드), `app/mypage/edit/page.tsx`(Server, 입력값 기본값). 세 곳 모두 실패 시 `DEFAULT_PROFILE`(이름 "게스트" 등)로 대체하도록 이미 처리돼 있다.
- **끝나는지**: **거의 끝난다.** fetch 호출만 채우면 세 화면 모두 자동으로 반영된다. 단, 인증이 필요한 API라면(로그인 안 한 상태에서 호출) 401 등 처리를 어떻게 할지는 `login` 항목의 "로그인 상태 관리 미구현" 문제와 연결되어 있다.

## 9. `updateMyProfile`

- **파일**: `frontend/services/user.ts`
- **시그니처**: `updateMyProfile(payload: UpdateProfilePayload): Promise<UserProfile>` — `UpdateProfilePayload{name, phone, currentPassword?, newPassword?}`
- **엔드포인트**: **미확정 — 백엔드 미구현.**
- **요청/응답 타입 대조**: **백엔드 미확정 — 대조 불가.**
- **호출 위치**: **없음.** `app/mypage/edit/page.tsx`의 "저장하기"는 지금도 `Link`이고 `updateMyProfile()`을 호출하지 않는다. 이번 요청 범위에 포함되지 않아 그대로 두었다.
- **끝나는지**: **아니다.** 함수 구현과 별개로, `app/mypage/edit/page.tsx`를 폼(`<form onSubmit>`)으로 바꾸고 `updateMyProfile()` 호출·로딩·에러 처리를 `login`/`signup`과 같은 패턴으로 추가해야 한다.

## 10. `withdrawMyAccount`

- **파일**: `frontend/services/user.ts`
- **시그니처**: `withdrawMyAccount(password: string): Promise<void>`
- **엔드포인트**: **미확정 — 백엔드 미구현.**
- **요청/응답 타입 대조**: 응답 타입 없음(`void`).
- **호출 위치**: **없음.** `app/mypage/withdraw/page.tsx`의 "탈퇴하기" 버튼은 지금도 아무 동작이 없는 `<button>`이다.
- **끝나는지**: **아니다.** `updateMyProfile`과 동일하게, 폼 제출 처리·확인 절차(비밀번호 입력값 전달)까지 추가로 구현해야 한다.

---

## 참고 — 이번 작업으로 바뀐 것 / 안 바뀐 것

- **바뀜**: 사기화면·보이스피싱·뉴스는 실제 화면에서 서비스 함수를 호출하는 구조로 연결됨. `FraudResultCard`/`VoicePhishingResultCard`는 props 기반으로 바뀌어 더미 상수를 갖지 않음.
- **안 바뀜**: `logout`, `updateMyProfile`, `withdrawMyAccount`는 여전히 호출 지점이 없음(요청 범위가 로그인/회원가입/프로필 조회까지였음). 로그인 성공 후 세션·토큰을 유지하는 전역 상태 관리도 아직 없음.
