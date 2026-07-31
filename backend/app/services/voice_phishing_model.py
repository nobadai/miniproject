"""KoELECTRA 보이스피싱 모델의 CUDA 추론 기반을 제공한다.

통화 텍스트를 겹치는 토큰 청크로 나누고 위험도가 높은 청크를 결합해
저장된 분류 모델의 통화 단위 점수를 계산한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = BACKEND_ROOT / "artifacts" / "voice_phishing" / "koelectra"
DEFAULT_BASE_MODEL = "monologg/koelectra-base-v3-discriminator"
LABEL_TO_ID = {"normal": 0, "suspicious": 1}


@dataclass(frozen=True)
class KoElectraScore:
    """KoELECTRA가 계산한 통화 단위 위험 점수이다."""

    score: float
    chunks_analyzed: int
    top_chunks: int


def require_cuda() -> torch.device:
    """CUDA가 없을 때 CPU로 우회하지 않고 명확한 오류를 반환한다."""
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA GPU를 사용할 수 없습니다. CUDA PyTorch 설치를 확인하세요."
        )
    return torch.device("cuda")


def format_call_text(turns: list[dict]) -> str:
    """화자 정보가 보존된 KoELECTRA 입력 문자열을 만든다."""
    speaker_names = {"other": "상대", "self": "본인"}
    return "\n".join(
        f"[{speaker_names.get(turn.get('speaker'), '기타')}] {turn['text']}"
        for turn in turns
    )


def choose_chunks(chunks: list[list[int]], limit: int) -> list[list[int]]:
    """긴 통화의 시작과 끝을 포함해 청크를 고르게 선택한다."""
    if limit < 1:
        raise ValueError("max_chunks는 1 이상이어야 합니다.")
    if len(chunks) <= limit:
        return chunks
    if limit == 1:
        return [chunks[0]]
    indexes = [
        round(index * (len(chunks) - 1) / (limit - 1))
        for index in range(limit)
    ]
    return [chunks[index] for index in indexes]


def encode_turns(
    turns: list[dict],
    tokenizer,
    max_length: int = 512,
    stride: int = 128,
    max_chunks: int = 8,
) -> list[dict]:
    """통화 발화를 모델 입력용 겹침 청크로 변환한다."""
    if not turns:
        raise ValueError("분석할 발화가 없습니다.")
    encoded = tokenizer(
        format_call_text(turns),
        truncation=True,
        max_length=max_length,
        stride=stride,
        return_overflowing_tokens=True,
    )
    input_ids = choose_chunks(encoded["input_ids"], max_chunks)
    return [
        {"input_ids": token_ids, "attention_mask": [1] * len(token_ids)}
        for token_ids in input_ids
    ]


def forward_chunks(
    model,
    chunks: list[dict],
    tokenizer,
    batch_size: int,
    device: torch.device,
) -> torch.Tensor:
    """청크를 작은 CUDA 배치로 실행하고 연결된 logits를 반환한다."""
    outputs = []
    for start in range(0, len(chunks), batch_size):
        batch = tokenizer.pad(
            chunks[start : start + batch_size], padding=True, return_tensors="pt"
        )
        batch = {
            key: value.to(device, non_blocking=True) for key, value in batch.items()
        }
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            outputs.append(model(**batch).logits)
    return torch.cat(outputs)


class KoElectraAnalyzer:
    """저장된 KoELECTRA 모델을 한 번 로드해 CUDA에서 재사용한다."""

    def __init__(self, model_path: Path | str = DEFAULT_MODEL_PATH):
        resolved_path = Path(model_path)
        if not resolved_path.is_dir():
            raise FileNotFoundError(
                f"KoELECTRA 모델 디렉터리를 찾을 수 없습니다: {resolved_path}"
            )
        self.device = require_cuda()
        self.tokenizer = AutoTokenizer.from_pretrained(resolved_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            resolved_path
        ).to(self.device)
        self.model.eval()

    @torch.no_grad()
    def score(
        self,
        turns: list[dict],
        batch_size: int = 2,
        top_k: int = 3,
        max_length: int = 512,
        stride: int = 128,
        max_chunks: int = 8,
    ) -> KoElectraScore:
        """상위 위험 청크 logits 평균으로 통화 점수를 계산한다."""
        chunks = encode_turns(
            turns,
            self.tokenizer,
            max_length=max_length,
            stride=stride,
            max_chunks=max_chunks,
        )
        logits = forward_chunks(
            self.model, chunks, self.tokenizer, batch_size, self.device
        )
        probabilities = torch.softmax(logits.float(), dim=-1)[:, 1]
        selected_count = min(top_k, len(probabilities))
        indexes = torch.topk(probabilities, selected_count).indices
        call_logits = logits[indexes].mean(dim=0)
        score = torch.softmax(call_logits.float(), dim=-1)[1].item()
        return KoElectraScore(
            score=score,
            chunks_analyzed=len(chunks),
            top_chunks=selected_count,
        )
