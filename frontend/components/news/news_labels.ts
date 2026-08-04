// 목적: 금융 뉴스 감성 판정(label)·시황 구분(brief_type) 값을 화면 표시용
//      문구·스타일로 매핑한다.
// 주요 역할: Backend가 내려주는 원시 값(POS/NEU/NEG, morning/closing)을
//           뉴스 카드·배너·상세 화면이 공통으로 쓰는 배지 문구/색상으로 변환한다.

import type { NewsBriefType, NewsLabel } from "../../types/news";

export const NEWS_LABEL_TEXT: Record<NewsLabel, string> = {
  POS: "긍정",
  NEU: "중립",
  NEG: "부정",
};

export const NEWS_LABEL_CLASS: Record<NewsLabel, string> = {
  POS: "bg-safe-bg text-safe",
  NEU: "bg-line-soft text-ink-sub",
  NEG: "bg-alert-bg text-alert",
};

// summary/label은 요약·판정 배치가 아직 처리하지 않은 기사에서 null로 내려온다.
export const NEWS_LABEL_UNRESOLVED_TEXT = "판정 대기";
export const NEWS_LABEL_UNRESOLVED_CLASS = "bg-line-soft text-ink-sub";

export const NEWS_BRIEF_TYPE_LABEL: Record<NewsBriefType, string> = {
  morning: "오전시황",
  closing: "마감시황",
};

// 뉴스 카드/배너가 공통으로 쓰는 짧은 날짜 표시("2026.07.31").
export function formatNewsListDate(publishedAt: string): string {
  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  })
    .format(new Date(publishedAt))
    .replace(/\. /g, ".")
    .replace(/\.$/, "");
}
