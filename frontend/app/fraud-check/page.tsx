// 목적: 사기화면 판별 / 보이스피싱 판별 페이지의 진입점을 정의한다.
// 주요 역할: 탭 상태를 읽는 Client Component(FraudCheckView)를 Suspense로 감싸 제공한다.

import { Suspense } from "react";
import FraudCheckView from "./FraudCheckView";

export default function FraudCheckPage() {
  return (
    <Suspense fallback={null}>
      <FraudCheckView />
    </Suspense>
  );
}
