// 목적: 검사할 파일을 선택하는 공통 업로드 영역을 제공한다.
// 주요 역할: 큰 선택 버튼, 선택한 파일 정보, 미리보기를 함께 표시한다.

"use client";

import { useRef } from "react";
import { formatFileSize } from "../../utils/format";

interface FileUploadBoxProps {
  accept: string;
  icon: string;
  emptyTitle: string;
  emptyDescription: string;
  selectButtonLabel: string;
  selectedFile: File | null;
  previewUrl?: string | null;
  onSelectFile: (selectedFile: File | null) => void;
}

export default function FileUploadBox({
  accept,
  icon,
  emptyTitle,
  emptyDescription,
  selectButtonLabel,
  selectedFile,
  previewUrl,
  onSelectFile,
}: FileUploadBoxProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const openFilePicker = () => {
    fileInputRef.current?.click();
  };

  const clearSelectedFile = () => {
    onSelectFile(null);
    // 같은 파일을 다시 선택해도 change 이벤트가 발생하도록 입력값을 비운다.
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <section className="rounded-2xl border-2 border-dashed border-line bg-surface px-5 py-6">
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        className="sr-only"
        onChange={(changeEvent) =>
          onSelectFile(changeEvent.target.files?.[0] ?? null)
        }
      />

      {selectedFile === null ? (
        <div className="text-center">
          <p aria-hidden="true" className="text-3xl">
            {icon}
          </p>
          <p className="mt-3 text-lg font-bold text-ink">{emptyTitle}</p>
          <p className="mt-1 text-sm text-ink-soft">{emptyDescription}</p>
        </div>
      ) : (
        <div>
          {previewUrl && (
            // 업로드한 화면 캡처는 사용자가 맞는 이미지인지 눈으로 확인해야 해서 그대로 보여준다.
            // Browser 임시 주소(blob)라 next/image의 최적화 대상이 될 수 없어 img를 사용한다.
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={previewUrl}
              alt="선택한 이미지 미리보기"
              className="mb-4 max-h-72 w-full rounded-xl border-2 border-line object-contain"
            />
          )}
          <p className="text-sm text-ink-soft">선택한 파일</p>
          <p className="mt-1 break-all text-lg font-bold text-ink">
            {selectedFile.name}
          </p>
          <p className="mt-1 text-sm text-ink-soft">
            {formatFileSize(selectedFile.size)}
          </p>
        </div>
      )}

      <div className="mt-5 flex gap-3">
        <button
          type="button"
          onClick={openFilePicker}
          className="min-h-[64px] flex-1 rounded-xl bg-brand px-4 text-lg font-bold text-white active:bg-brand-dark"
        >
          {selectedFile === null ? selectButtonLabel : "다른 파일 선택"}
        </button>
        {selectedFile !== null && (
          <button
            type="button"
            onClick={clearSelectedFile}
            className="min-h-[64px] rounded-xl border-2 border-line px-5 text-lg font-bold text-ink-soft"
          >
            지우기
          </button>
        )}
      </div>
    </section>
  );
}
