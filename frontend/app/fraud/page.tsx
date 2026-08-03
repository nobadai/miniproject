// 목적: 문자나 앱 화면 캡처로 금융사기 여부를 검사하는 화면을 정의한다.
// 주요 역할: 이미지 선택과 미리보기, 분석 요청, 결과 표시를 담당한다.

"use client";

import { useEffect, useRef, useState } from "react";
import FileUploadBox from "../../components/commons/file_upload_box";
import PageHeading from "../../components/commons/page_heading";
import FraudResult from "../../components/frauds/fraud_result";
import { analyzeFraudImage } from "../../services/fraud_analysis";
import type { FraudAnalysisResult } from "../../types/fraud_analysis";

export default function FraudPage() {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<FraudAnalysisResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const previewUrlRef = useRef<string | null>(null);

  // 화면을 벗어날 때 남아 있는 임시 주소를 해제해 메모리를 정리한다.
  useEffect(() => {
    return () => {
      if (previewUrlRef.current !== null) {
        URL.revokeObjectURL(previewUrlRef.current);
      }
    };
  }, []);

  const selectImageFile = (selectedFile: File | null) => {
    // 미리보기용 임시 주소는 파일이 바뀔 때마다 이전 것을 반드시 해제해야 한다.
    if (previewUrlRef.current !== null) {
      URL.revokeObjectURL(previewUrlRef.current);
    }
    previewUrlRef.current =
      selectedFile === null ? null : URL.createObjectURL(selectedFile);

    setImageFile(selectedFile);
    setPreviewUrl(previewUrlRef.current);
    setResult(null);
    setErrorMessage(null);
  };

  const requestAnalysis = async () => {
    if (imageFile === null) {
      return;
    }

    setIsAnalyzing(true);
    setResult(null);
    setErrorMessage(null);

    try {
      const response = await analyzeFraudImage(imageFile);
      if (response.success && response.data) {
        setResult(response.data);
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
        title="문자·화면 검사"
        description="받은 문자나 이체 완료 화면을 캡처해서 올리면 조작된 흔적이 있는지 확인해 드려요."
      />

      <FileUploadBox
        accept="image/png,image/jpeg,image/webp,image/gif"
        icon="📷"
        emptyTitle="검사할 화면 캡처를 선택하세요"
        emptyDescription="PNG, JPG, WEBP, GIF 이미지를 올릴 수 있어요"
        selectButtonLabel="사진 선택하기"
        selectedFile={imageFile}
        previewUrl={previewUrl}
        onSelectFile={selectImageFile}
      />

      <button
        type="button"
        onClick={requestAnalysis}
        disabled={imageFile === null || isAnalyzing}
        className="min-h-[72px] w-full rounded-2xl bg-brand text-xl font-bold text-white disabled:bg-line disabled:text-ink-soft"
      >
        {isAnalyzing ? "검사하는 중이에요..." : "사기 화면인지 검사하기"}
      </button>

      {isAnalyzing && (
        <p className="rounded-2xl border-2 border-brand bg-brand-soft px-5 py-5 text-base text-ink">
          올려주신 화면을 살펴보고 있어요. 잠시만 기다려 주세요.
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

      {result && <FraudResult result={result} />}
    </div>
  );
}
