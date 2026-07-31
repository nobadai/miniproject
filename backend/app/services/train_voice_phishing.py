"""기준 JSONL로 배포용 KoELECTRA 모델을 CUDA에서 학습한다.

기존 통화 단위 상위 청크 학습 방식을 사용하고, 학습 완료 모델과
토크나이저를 이후 파일 분석에서 다시 불러올 수 있도록 저장한다.
"""

from __future__ import annotations

import argparse
import json
import logging
import random
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import logging as transformers_logging

from .voice_phishing_model import (
    BACKEND_ROOT,
    DEFAULT_BASE_MODEL,
    DEFAULT_MODEL_PATH,
    LABEL_TO_ID,
    encode_turns,
    forward_chunks,
    require_cuda,
)


DEFAULT_INPUT_PATH = (
    BACKEND_ROOT
    / "resources"
    / "voice_phishing"
    / "evaluations"
    / "eval_v1.jsonl"
)
logger = logging.getLogger(__name__)


def load_training_rows(path: Path) -> list[dict]:
    """JSONL을 읽고 학습에 필요한 라벨과 발화를 검증한다."""
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not rows:
        raise ValueError("학습 데이터가 비어 있습니다.")
    for row in rows:
        if row.get("label") not in LABEL_TO_ID:
            raise ValueError(f"지원하지 않는 학습 라벨입니다: {row.get('label')}")
        if not row.get("turns"):
            raise ValueError(f"발화가 없는 학습 데이터입니다: {row.get('call_id')}")
    return rows


@torch.no_grad()
def select_top_chunks(
    model,
    chunks: list[dict],
    tokenizer,
    batch_size: int,
    device: torch.device,
    top_k: int,
) -> list[int]:
    """현재 모델에서 피싱 점수가 높은 청크 인덱스를 선택한다."""
    model.eval()
    logits = forward_chunks(model, chunks, tokenizer, batch_size, device)
    probabilities = torch.softmax(logits.float(), dim=-1)[:, 1]
    selected_count = min(top_k, len(chunks))
    return torch.topk(probabilities, selected_count).indices.cpu().tolist()


def train_model(
    rows: list[dict],
    output_path: Path,
    base_model: str = DEFAULT_BASE_MODEL,
    epochs: int = 2,
    learning_rate: float = 2e-5,
    batch_size: int = 2,
    top_k: int = 3,
    max_length: int = 512,
    stride: int = 128,
    max_chunks: int = 8,
    seed: int = 42,
) -> None:
    """전체 기준 데이터로 최종 모델을 학습하고 저장한다."""
    device = require_cuda()
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True

    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model = AutoModelForSequenceClassification.from_pretrained(
        base_model, num_labels=2
    ).to(device)
    encoded_calls = [
        {
            "call_id": row["call_id"],
            "label": LABEL_TO_ID[row["label"]],
            "chunks": encode_turns(
                row["turns"],
                tokenizer,
                max_length=max_length,
                stride=stride,
                max_chunks=max_chunks,
            ),
        }
        for row in rows
    ]

    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    scaler = torch.amp.GradScaler("cuda")
    random_generator = random.Random(seed)
    for epoch in range(1, epochs + 1):
        random_generator.shuffle(encoded_calls)
        total_loss = 0.0
        for call in encoded_calls:
            selected_indexes = select_top_chunks(
                model,
                call["chunks"],
                tokenizer,
                batch_size,
                device,
                top_k,
            )
            selected_chunks = [
                call["chunks"][index] for index in selected_indexes
            ]
            model.train()
            optimizer.zero_grad()
            logits = forward_chunks(
                model, selected_chunks, tokenizer, batch_size, device
            )
            call_logits = logits.mean(dim=0, keepdim=True)
            label = torch.tensor([call["label"]], device=device)
            loss = torch.nn.functional.cross_entropy(call_logits.float(), label)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            total_loss += loss.item()
        logger.info(
            "KoELECTRA 학습 epoch=%s loss=%.4f",
            epoch,
            total_loss / len(encoded_calls),
        )

    output_path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)
    logger.info("KoELECTRA 모델 저장 완료: %s", output_path)


def main() -> None:
    """Python 모듈 실행 인자를 받아 배포용 모델 학습을 시작한다."""
    parser = argparse.ArgumentParser(description="보이스피싱 KoELECTRA 학습")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--base-model", default=DEFAULT_BASE_MODEL)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--stride", type=int, default=128)
    parser.add_argument("--max-chunks", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    arguments = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    transformers_logging.set_verbosity_error()
    rows = load_training_rows(arguments.input)
    train_model(
        rows=rows,
        output_path=arguments.output,
        base_model=arguments.base_model,
        epochs=arguments.epochs,
        learning_rate=arguments.learning_rate,
        batch_size=arguments.batch_size,
        top_k=arguments.top_k,
        max_length=arguments.max_length,
        stride=arguments.stride,
        max_chunks=arguments.max_chunks,
        seed=arguments.seed,
    )


if __name__ == "__main__":
    main()
