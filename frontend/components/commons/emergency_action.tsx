// 목적: 위험 판정 이후 바로 이어갈 수 있는 대응 행동을 안내한다.
// 주요 역할: 신고 전화 연결과 가족 알림 문자를 큰 버튼으로 제공한다.

interface EmergencyActionProps {
  shareMessage: string;
}

export default function EmergencyAction({ shareMessage }: EmergencyActionProps) {
  return (
    <section className="rounded-2xl border-2 border-line bg-surface px-5 py-5">
      <h3 className="text-lg font-bold text-ink">이렇게 하세요</h3>
      <p className="mt-2 text-sm text-ink-soft">
        이미 송금했다면 즉시 은행 콜센터에 지급정지를 요청하세요.
      </p>

      <div className="mt-4 flex flex-col gap-3">
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
        <a
          href={`sms:?body=${encodeURIComponent(shareMessage)}`}
          className="flex min-h-[64px] items-center justify-center rounded-xl border-2 border-line px-4 text-lg font-bold text-ink"
        >
          👨‍👩‍👧 가족에게 문자로 알리기
        </a>
      </div>
    </section>
  );
}
