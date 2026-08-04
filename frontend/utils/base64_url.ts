// 목적: 슬래시(/)를 포함하는 문자열(원문 URL 등)을 Next.js 동적 라우트 세그먼트로
//      안전하게 쓰기 위한 Base64url 인코딩/디코딩 유틸리티를 제공한다.
// 주요 역할: encodeURIComponent로 만든 %2F(인코딩된 슬래시)는 Next.js 라우터가
//           경로 구분자로 다시 풀어버려 단일 동적 세그먼트([url] 등)에 매칭되지
//           않는 문제가 있다. 표준 Base64는 원래 슬래시(/)와 더하기(+)를 쓰므로,
//           경로 세그먼트에서 안전하도록 -, _로 치환하고 패딩(=)을 제거한다.
//           Server(Node.js)와 Client(Browser) 양쪽에서 호출되므로(뉴스 카드/배너는
//           Client Component, 상세 페이지는 Server Component) 두 환경 모두 지원한다.

export function encodeBase64Url(value: string): string {
  const base64 =
    typeof Buffer !== "undefined"
      ? Buffer.from(value, "utf-8").toString("base64")
      : btoa(String.fromCharCode(...new TextEncoder().encode(value)));
  return base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

export function decodeBase64Url(value: string): string {
  const padded = value.replace(/-/g, "+").replace(/_/g, "/");
  const base64 = padded + "=".repeat((4 - (padded.length % 4)) % 4);

  if (typeof Buffer !== "undefined") {
    return Buffer.from(base64, "base64").toString("utf-8");
  }
  const binary = atob(base64);
  return new TextDecoder().decode(Uint8Array.from(binary, (c) => c.charCodeAt(0)));
}
