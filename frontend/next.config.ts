// 목적: Next.js 애플리케이션 Build를 설정한다.
// 주요 역할: Frontend Container용 독립 실행 결과물을 생성한다.

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
};

export default nextConfig;
