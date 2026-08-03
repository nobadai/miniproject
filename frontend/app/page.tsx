// 목적: Frontend 루트 경로인 홈 화면을 정의한다.
// 주요 역할: 세 가지 주요 기능으로 이동하는 큰 카드와 기본 안전 수칙을 제공한다.

import ActionCard from "../components/commons/action_card";

const SAFETY_TIPS = [
  "전화로 계좌번호나 비밀번호를 묻는 곳은 모두 사기입니다.",
  "검찰, 경찰, 금융감독원은 절대 돈을 보내라고 하지 않습니다.",
  "문자로 온 링크는 누르지 말고 먼저 확인받으세요.",
];

export default function HomePage() {
  return (
    <div className="flex flex-col gap-6">
      <section>
        <h1 className="text-2xl font-bold text-ink">
          안녕하세요, 오늘도 안전하게 지켜드릴게요
        </h1>
        <p className="mt-2 text-base text-ink-soft">
          의심되는 통화나 문자가 있으면 아래에서 바로 확인해 보세요.
        </p>
      </section>

      <section className="flex flex-col gap-4">
        <ActionCard
          href="/voice-phishing"
          icon="📞"
          title="통화 녹음 검사"
          description="녹음 파일을 올리면 보이스피싱인지 확인해 드려요"
        />
        <ActionCard
          href="/fraud"
          icon="🖼️"
          title="문자·화면 검사"
          description="이체 내역이나 문자 캡처가 조작됐는지 확인해 드려요"
        />
        <ActionCard
          href="/news"
          icon="📰"
          title="내 맞춤 뉴스"
          description="가입한 금융상품과 관련된 소식만 모아 드려요"
        />
      </section>

      <section className="rounded-2xl border-2 border-caution bg-caution-soft px-5 py-5">
        <h2 className="text-lg font-bold text-caution">꼭 기억하세요</h2>
        <ul className="mt-3 flex flex-col gap-3">
          {SAFETY_TIPS.map((safetyTip) => (
            <li key={safetyTip} className="flex gap-2 text-base text-ink">
              <span aria-hidden="true" className="font-bold text-caution">
                ·
              </span>
              {safetyTip}
            </li>
          ))}
        </ul>
      </section>

      <section className="rounded-2xl border-2 border-line bg-surface px-5 py-5">
        <h2 className="text-lg font-bold text-ink">급할 때 연락하세요</h2>
        <div className="mt-3 flex flex-col gap-3">
          <a
            href="tel:112"
            className="flex min-h-[64px] items-center justify-center rounded-xl bg-danger px-4 text-lg font-bold text-white"
          >
            📞 경찰 112 신고하기
          </a>
          <a
            href="tel:1332"
            className="flex min-h-[64px] items-center justify-center rounded-xl border-2 border-brand px-4 text-lg font-bold text-brand"
          >
            🏛️ 금융감독원 1332 상담
          </a>
        </div>
      </section>
    </div>
  );
}
