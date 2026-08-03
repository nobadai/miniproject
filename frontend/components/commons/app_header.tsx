// 목적: 모든 화면 상단에 고정으로 노출되는 서비스 헤더를 제공한다.
// 주요 역할: 서비스 이름을 알리고 글자 크기 조절 기능을 제공한다.

"use client";

import { useSyncExternalStore } from "react";

const LARGE_TEXT_STORAGE_KEY = "safeKeeperLargeText";
const LARGE_TEXT_CLASS_NAME = "large-text";

// 글자 크기는 html 태그의 class로 관리한다. 화면이 그려지기 전에 layout의
// Script가 저장값을 먼저 적용하므로, React는 그 결과를 읽어 버튼 문구만 맞춘다.
const storeListeners = new Set<() => void>();

function subscribeLargeText(onStoreChange: () => void) {
  storeListeners.add(onStoreChange);
  return () => {
    storeListeners.delete(onStoreChange);
  };
}

function getLargeTextSnapshot(): boolean {
  return document.documentElement.classList.contains(LARGE_TEXT_CLASS_NAME);
}

function getLargeTextServerSnapshot(): boolean {
  return false;
}

function applyLargeText(nextValue: boolean) {
  document.documentElement.classList.toggle(LARGE_TEXT_CLASS_NAME, nextValue);
  window.localStorage.setItem(LARGE_TEXT_STORAGE_KEY, String(nextValue));
  storeListeners.forEach((storeListener) => storeListener());
}

export default function AppHeader() {
  const isLargeText = useSyncExternalStore(
    subscribeLargeText,
    getLargeTextSnapshot,
    getLargeTextServerSnapshot
  );

  return (
    <header className="sticky top-0 z-10 bg-brand px-5 py-4 text-white">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xl font-bold">안심지킴이</p>
          <p className="text-sm text-white/85">보이스피싱·금융사기 확인 도우미</p>
        </div>
        <button
          type="button"
          onClick={() => applyLargeText(!isLargeText)}
          aria-pressed={isLargeText}
          className="min-h-[48px] shrink-0 rounded-xl border-2 border-white/70 px-4 text-sm font-bold text-white"
        >
          {isLargeText ? "글자 작게" : "글자 크게"}
        </button>
      </div>
    </header>
  );
}
