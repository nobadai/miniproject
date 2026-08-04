// 목적: 사기화면 판별 / 보이스피싱 판별 탭 전환 화면을 정의한다.
// 주요 역할: 파일 선택 → services 호출 → 로딩/에러/결과 상태를 관리한다.
//           services 함수는 아직 throw new Error("not implemented") 상태이므로,
//           지금 "판별하기"를 누르면 에러 상태 UI가 뜨는 것이 정상 동작이다.
//           API 연동 담당자는 services/fraud_analysis.ts, services/voice_phishing.ts
//           내부 구현만 채우면 이 화면은 별도 수정 없이 그대로 동작한다.

"use client";

import { useSearchParams } from "next/navigation";
import { useRef, useState } from "react";
import FraudResultCard from "../../components/frauds/FraudResultCard";
import VoicePhishingResultCard from "../../components/voice_phishings/VoicePhishingResultCard";
import { analyzeFraudScreen } from "../../services/fraud_analysis";
import { analyzeVoicePhishing } from "../../services/voice_phishing";
import type { FraudAnalysisResult } from "../../types/fraud_analysis";
import type { VoicePhishingAnalysis } from "../../types/voice_phishing";

type FraudCheckTab = "screen" | "voice";

const SCREEN_HISTORY = [
  { tag: "화면", text: "가짜 은행 앱", result: "사기 의심", className: "text-alert" },
  { tag: "화면", text: "문자 속 링크 화면", result: "판단 불가", className: "text-ink" },
  { tag: "화면", text: "카카오뱅크 송금 완료 화면", result: "정상", className: "text-safe" },
];

const VOICE_HISTORY = [
  { tag: "음성", text: "03:54", result: "87% 의심", className: "text-alert" },
  { tag: "화면", text: "가짜 은행 앱", result: "사기 의심", className: "text-alert" },
  { tag: "음성", text: "01:12", result: "22% 낮음", className: "text-safe" },
];

export default function FraudCheckView() {
  const searchParams = useSearchParams();
  const initialTab: FraudCheckTab =
    searchParams.get("tab") === "voice" ? "voice" : "screen";
  const [tab, setTab] = useState<FraudCheckTab>(initialTab);

  return (
    <div>
      <div className="flex border border-line bg-white px-1">
        <button
          type="button"
          onClick={() => setTab("screen")}
          className={`flex items-center gap-[7px] px-5 pb-[13px] pt-[15px] text-sm font-medium ${
            tab === "screen"
              ? "border-b-2 border-navy font-semibold text-navy"
              : "border-b-2 border-transparent text-ink-sub"
          }`}
        >
          <svg
            className="h-4 w-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.6}
          >
            <rect x="3" y="4" width="18" height="14" rx="1.5" />
            <path d="M3 15l5-5 4 4 5-6 4 5" />
          </svg>
          사기화면 판별
        </button>
        <button
          type="button"
          onClick={() => setTab("voice")}
          className={`flex items-center gap-[7px] px-5 pb-[13px] pt-[15px] text-sm font-medium ${
            tab === "voice"
              ? "border-b-2 border-navy font-semibold text-navy"
              : "border-b-2 border-transparent text-ink-sub"
          }`}
        >
          <svg
            className="h-4 w-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.6}
          >
            <rect x="9" y="3" width="6" height="11" rx="3" />
            <path d="M6 11a6 6 0 0 0 12 0" />
            <path d="M12 17v4" />
            <path d="M9 21h6" />
          </svg>
          보이스피싱 판별
        </button>
      </div>

      <div className="border border-t-line-soft border-line bg-white p-8">
        {tab === "screen" ? (
          <ScreenCheckPanel />
        ) : (
          <VoiceCheckPanel />
        )}
      </div>
    </div>
  );
}

function ScreenCheckPanel() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FraudAnalysisResult | null>(null);

  const handleAnalyze = async () => {
    if (!file) {
      setError("먼저 사기가 의심되는 화면 사진을 선택해주세요.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const analysis = await analyzeFraudScreen(file);
      setResult(analysis);
    } catch (cause) {
      setResult(null);
      setError(
        cause instanceof Error ? cause.message : "사기화면 판별에 실패했습니다."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 gap-7 lg:grid-cols-[1fr_300px]">
      <div>
        <div className="rounded-md border border-line bg-[#fafbfc] px-5 py-[46px] text-center text-ink-sub">
          <svg
            className="mx-auto mb-3 h-7 w-7 text-[#97a1ad]"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.4}
          >
            <rect x="3" y="4" width="18" height="14" rx="1.5" />
            <path d="M3 15l5-5 4 4 5-6 4 5" />
          </svg>
          <div className="mb-1 text-[15px] font-semibold text-ink">
            사기가 의심되는 화면 사진을 올려주세요
          </div>
          <div className="mb-[18px] text-[12.5px] text-ink-sub">
            {file ? `선택된 파일: ${file.name}` : "휴대폰 캡처 화면도 괜찮아요 (JPG, PNG)"}
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="rounded-md border border-[#c9ced6] bg-white px-[18px] py-2.5 text-[13.5px] font-semibold text-ink"
          >
            사진 선택하기
          </button>
        </div>
        <button
          type="button"
          onClick={handleAnalyze}
          disabled={loading}
          className="my-5 w-full rounded-md bg-navy py-3.5 text-[14.5px] font-semibold text-white disabled:opacity-60"
        >
          {loading ? "판별하는 중..." : "판별하기"}
        </button>

        {error && (
          <div className="mb-5 rounded-md border border-alert-border bg-alert-bg px-4 py-3 text-[13px] text-alert">
            {error}
          </div>
        )}

        {result ? (
          <FraudResultCard result={result} />
        ) : (
          !error && (
            <div className="rounded-md border border-line px-5 py-8 text-center text-[13px] text-ink-sub">
              아직 판별한 화면이 없어요. 사진을 선택하고 판별하기를 눌러주세요.
            </div>
          )
        )}
      </div>

      <HistorySidebar items={SCREEN_HISTORY} />
    </div>
  );
}

function VoiceCheckPanel() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<VoicePhishingAnalysis | null>(null);

  const handleAnalyze = async () => {
    if (!file) {
      setError("먼저 분석할 통화 녹음 파일을 선택해주세요.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const analysis = await analyzeVoicePhishing(file);
      setResult(analysis);
    } catch (cause) {
      setResult(null);
      setError(
        cause instanceof Error ? cause.message : "보이스피싱 판별에 실패했습니다."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 gap-7 lg:grid-cols-[1fr_300px]">
      <div>
        <div className="mb-5 flex items-center gap-3 rounded-md border border-line px-[18px] py-4 text-[13px] text-ink-sub">
          <svg
            className="h-[18px] w-[18px] shrink-0 text-[#97a1ad]"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.6}
          >
            <rect x="9" y="3" width="6" height="11" rx="3" />
            <path d="M6 11a6 6 0 0 0 12 0" />
          </svg>
          {file
            ? `선택된 파일: ${file.name}`
            : "통화 녹음 파일을 올리면 대화 내용을 분석해요 (MP3, M4A, WAV)"}
          <input
            ref={fileInputRef}
            type="file"
            accept="audio/*"
            className="hidden"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="ml-auto rounded-md border border-[#c9ced6] bg-white px-[18px] py-2.5 text-[13.5px] font-semibold text-ink"
          >
            파일 선택
          </button>
        </div>
        <button
          type="button"
          onClick={handleAnalyze}
          disabled={loading}
          className="mb-5 w-full rounded-md bg-navy py-3.5 text-[14.5px] font-semibold text-white disabled:opacity-60"
        >
          {loading ? "판별하는 중..." : "판별하기"}
        </button>

        {error && (
          <div className="mb-5 rounded-md border border-alert-border bg-alert-bg px-4 py-3 text-[13px] text-alert">
            {error}
          </div>
        )}

        {result ? (
          <VoicePhishingResultCard result={result} />
        ) : (
          !error && (
            <div className="rounded-md border border-line px-5 py-8 text-center text-[13px] text-ink-sub">
              아직 판별한 통화가 없어요. 파일을 선택하고 판별하기를 눌러주세요.
            </div>
          )
        )}
      </div>

      <HistorySidebar items={VOICE_HISTORY} />
    </div>
  );
}

function HistorySidebar({
  items,
}: {
  items: { tag: string; text: string; result: string; className: string }[];
}) {
  return (
    <div>
      <div className="mb-3.5 text-[12.5px] font-bold uppercase tracking-[0.3px] text-ink-sub">
        최근 확인 기록
      </div>
      {items.map((item, index) => (
        <div
          key={index}
          className="flex items-start gap-2.5 border-b border-line-soft py-3 text-[13px] last:border-b-0"
        >
          <span className="mt-px shrink-0 rounded-[3px] border border-line px-[7px] py-[3px] text-[10.5px] font-bold text-ink-sub">
            {item.tag}
          </span>
          <div className="text-ink-body">
            {item.text} · <b className={item.className}>{item.result}</b>
          </div>
        </div>
      ))}
    </div>
  );
}
