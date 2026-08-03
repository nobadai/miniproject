// 목적: 홈 화면에서 주요 기능으로 이동하는 큰 카드 버튼을 제공한다.
// 주요 역할: 아이콘, 제목, 설명을 큰 터치 영역 하나로 묶어 표시한다.

import Link from "next/link";

interface ActionCardProps {
  href: string;
  icon: string;
  title: string;
  description: string;
}

export default function ActionCard({
  href,
  icon,
  title,
  description,
}: ActionCardProps) {
  return (
    <Link
      href={href}
      className="flex min-h-[112px] items-center gap-4 rounded-2xl border-2 border-line bg-surface px-5 py-5 active:border-brand active:bg-brand-soft"
    >
      <span
        aria-hidden="true"
        className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-brand-soft text-3xl"
      >
        {icon}
      </span>
      <span className="flex-1">
        <span className="block text-xl font-bold text-ink">{title}</span>
        <span className="mt-1 block text-sm text-ink-soft">{description}</span>
      </span>
      <span aria-hidden="true" className="text-xl font-bold text-brand">
        ›
      </span>
    </Link>
  );
}
