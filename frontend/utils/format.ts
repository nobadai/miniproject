// 목적: 화면 곳곳에서 반복되는 값 표시 형식을 공통 함수로 제공한다.
// 주요 역할: 비율, 파일 크기, 날짜를 중장년 사용자가 읽기 쉬운 형태로 변환한다.

export function formatPercent(ratio: number): string {
  return `${Math.round(ratio * 100)}%`;
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(bytes / 1024))}KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

export function formatSignedPercent(ratio: number): string {
  const sign = ratio > 0 ? "+" : "";
  return `${sign}${ratio.toFixed(1)}%`;
}

/** ISO 날짜 문자열을 "8월 3일 오후 2시" 형태로 바꾼다. */
export function formatPublishedAt(publishedAt: string): string {
  const publishedDate = new Date(publishedAt);
  if (Number.isNaN(publishedDate.getTime())) {
    return publishedAt;
  }

  const month = publishedDate.getMonth() + 1;
  const day = publishedDate.getDate();
  const hour = publishedDate.getHours();
  const meridiem = hour < 12 ? "오전" : "오후";
  const displayHour = hour % 12 === 0 ? 12 : hour % 12;

  return `${month}월 ${day}일 ${meridiem} ${displayHour}시`;
}
