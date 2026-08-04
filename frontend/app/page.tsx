// 목적: Frontend 홈 화면을 정의한다.
// 주요 역할: 서비스 소개(Hero), 금융 뉴스 배너, 기능 카드, 이용 통계를 보여준다.

import Link from "next/link";
import NewsBanner from "../components/news/NewsBanner";

const FEATURE_CARDS = [
  {
    href: "/fraud-check",
    title: "사기화면 판별",
    description:
      "은행·카드 앱 캡처 화면을 올리면 정상 · 사기의심 · 판단불가 3단계로 분석해요.",
    icon: (
      <path d="M3 15l5-5 4 4 5-6 4 5" />
    ),
  },
  {
    href: "/fraud-check?tab=voice",
    title: "보이스피싱 판별",
    badge: "구현 예정",
    description:
      "통화 녹음 파일을 올리면 대화 내용을 분석해 보이스피싱 의심도와 대응 방법을 안내해요.",
    icon: (
      <>
        <path d="M6 11a6 6 0 0 0 12 0" />
        <path d="M12 17v4" />
        <path d="M9 21h6" />
      </>
    ),
  },
  {
    href: "/news",
    title: "금융 뉴스 감성 분석",
    description: "최신 금융 뉴스를 긍정·부정·중립으로 분류해 흐름을 한눈에 볼 수 있어요.",
    icon: <path d="M8 10h8M8 14h5" />,
  },
];

const STATS = [
  { num: "1,204건", label: "누적 사기화면 판별" },
  { num: "386건", label: "누적 보이스피싱 판별" },
  { num: "97.2%", label: "서비스 가동률" },
];

export default function HomePage() {
  return (
    <main>
      <div className="mb-5 bg-navy px-10 py-[52px] text-white">
        <div className="mb-2.5 text-xs font-semibold tracking-[0.3px] text-[#9fb0c6]">
          금융 사기 탐지 서비스
        </div>
        <h1 className="mb-3 text-[26px] font-bold leading-[1.4] tracking-tight">
          화면 한 장으로
          <br />
          사기 여부를 확인하세요
        </h1>
        <p className="mb-6 text-sm leading-[1.6] text-[#c3ccd8]">
          의심되는 화면을 올리면 사기 여부와 근거를 알려드립니다.
        </p>
        <div className="flex gap-2.5">
          <Link
            href="/fraud-check"
            className="rounded-md bg-white px-[22px] py-3 text-[13.5px] font-semibold text-navy"
          >
            사기화면 판별 시작하기
          </Link>
          <Link
            href="/news"
            className="rounded-md border border-[#3a5578] px-[22px] py-3 text-[13.5px] font-semibold text-[#dfe6ee]"
          >
            금융 뉴스 감성 분석 보기
          </Link>
        </div>
      </div>

      <NewsBanner />

      <div className="mb-6 grid grid-cols-1 gap-px border border-line bg-line sm:grid-cols-3">
        {FEATURE_CARDS.map((card) => (
          <Link key={card.href} href={card.href} className="bg-white p-6">
            <div className="mb-3.5 flex h-[38px] w-[38px] items-center justify-center rounded-[7px] bg-line-soft text-navy">
              <svg
                className="h-[18px] w-[18px]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth={1.6}
              >
                {card.icon}
              </svg>
            </div>
            <h3 className="mb-1.5 text-[14.5px] font-bold text-ink">
              {card.title}
              {card.badge ? (
                <span className="ml-1.5 rounded-[3px] border border-caution-border bg-caution-bg px-1.5 py-0.5 text-[10px] font-bold text-caution">
                  {card.badge}
                </span>
              ) : null}
            </h3>
            <p className="text-[12.5px] leading-[1.6] text-ink-sub">
              {card.description}
            </p>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-px border border-line bg-line sm:grid-cols-3">
        {STATS.map((stat) => (
          <div key={stat.label} className="bg-white p-5 text-center">
            <div className="text-xl font-bold text-navy">{stat.num}</div>
            <div className="mt-1 text-xs text-ink-sub">{stat.label}</div>
          </div>
        ))}
      </div>
    </main>
  );
}
