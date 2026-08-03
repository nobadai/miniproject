// 목적: 통화 녹음 파일로 보이스피싱 여부를 검사하는 화면을 정의한다.
// 주요 역할: 오디오 선택, 분석 요청, 결과 표시까지의 화면 흐름을 담당한다.

"use client";

import { useState } from "react";
import FileUploadBox from "../../components/commons/file_upload_box";
import PageHeading from "../../components/commons/page_heading";
import VoicePhishingResult from "../../components/voice-phishings/voice_phishing_result";
import { analyzeVoicePhishingAudio } from "../../services/voice_phishing";
import type { VoicePhishingAnalysis } from "../../types/voice_phishing";

export default function VoicePhishingPage() {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<VoicePhishingAnalysis | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const selectAudioFile = (selectedFile: File | null) => {
    setAudioFile(selectedFile);
    setAnalysis(null);
    setErrorMessage(null);
  };

  const requestAnalysis = async () => {
    if (audioFile === null) {
      return;
    }

    setIsAnalyzing(true);
    setAnalysis(null);
    setErrorMessage(null);

    try {
      const response = await analyzeVoicePhishingAudio(audioFile);
      if (response.success && response.data) {
        setAnalysis(response.data);
      } else {
        setErrorMessage(response.message ?? "검사에 실패했습니다.");
      }
    } catch {
      setErrorMessage(
        "검사 서버에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요."
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <PageHeading
        title="통화 녹음 검사"
        description="통화 녹음 파일을 올리면 보이스피싱에서 자주 쓰이는 말과 대화 흐름을 확인해 드려요."
      />

      <FileUploadBox
        accept=".mp3,.wav,.m4a,.mp4,.mov,.avi,.mkv,.webm,audio/*,video/*"
        icon="🎧"
        emptyTitle="검사할 녹음 파일을 선택하세요"
        emptyDescription="MP3, WAV, M4A 녹음과 MP4 같은 영상 파일을 올릴 수 있어요"
        selectButtonLabel="녹음 파일 선택하기"
        selectedFile={audioFile}
        onSelectFile={selectAudioFile}
      />

      <button
        type="button"
        onClick={requestAnalysis}
        disabled={audioFile === null || isAnalyzing}
        className="min-h-[72px] w-full rounded-2xl bg-brand text-xl font-bold text-white disabled:bg-line disabled:text-ink-soft"
      >
        {isAnalyzing ? "검사하는 중이에요..." : "보이스피싱인지 검사하기"}
      </button>

      {isAnalyzing && (
        <p className="rounded-2xl border-2 border-brand bg-brand-soft px-5 py-5 text-base text-ink">
          녹음을 글로 바꾼 뒤 분석하고 있어요. 통화가 길면 1~2분 정도 걸릴 수
          있으니 잠시만 기다려 주세요.
        </p>
      )}

      {errorMessage && (
        <p
          role="alert"
          className="rounded-2xl border-2 border-danger bg-danger-soft px-5 py-5 text-base font-bold text-danger"
        >
          {errorMessage}
        </p>
      )}

      {analysis && <VoicePhishingResult analysis={analysis} />}
    </div>
  );
}
