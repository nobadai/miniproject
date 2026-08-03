"""시황 기사에 대한 Gemma 감성 판정과 근거 검증 흐름을 제공한다.

모델이 고른 근거 문장이 본문에 실재하는지 코드로 검증해 환각과 부분 발췌를
가려내고, 저장용 Record를 조립한다. 검증 결과는 기록용이 아니라 화면 필터이며
verify_status가 ok가 아닌 근거는 조회 단계에서 제외한다.
"""

from __future__ import annotations

import logging
import re


logger = logging.getLogger(__name__)

# "다." 뒤 공백과 일반 문장부호 뒤 공백을 문장 경계로 본다.
SENTENCE_BOUNDARY = re.compile(r"(?<=다\.)\s+|(?<=[.!?])\s+")

# 전문가 인용으로 판단되는 근거는 화면에 출처를 병기해야 한다.
QUOTE_PATTERN = re.compile(r'"[^"]{5,}"|고\s*(설명|밝혔|말했|전했|덧붙였)|라고\s')

BANNED_TERMS = [
    "매수", "매도", "사야", "팔아야", "살 때", "지금이", "기회", "추천", "유망",
    "목표가", "오를 것", "내릴 것", "전망된다", "시그널", "신호", "저점 매수",
    "Bullish", "Bearish", "Buy", "Sell", "Valuation", "Insight",
]

# 수급 용어는 정상 표현이므로 금지어 검사 전에 가린다.
#
# 단독 "매수"·"매도"까지 가리는 이유는 시황 서술이 "기관·외국인 매수와 개인
# 순매도가 충돌"처럼 수급 주체를 그대로 쓰기 때문이다. 이 둘을 가리면
# BANNED_TERMS 의 "매수"·"매도" 항목은 사실상 발동하지 않는다. 대신 실제 투자
# 권유는 "추천", "유망", "기회", "지금이", "목표가" 등 나머지 항목이 잡는다.
# 길이가 긴 표현을 먼저 두어 가리는 순서를 안정적으로 유지한다.
MASKED_TERMS = [
    "순매수", "순매도", "매수세", "매도세", "매수 주체", "매도 물량",
    "매수", "매도",
]


def normalize_for_match(text: str) -> str:
    """공백을 모두 제거해 문자열 대조 기준을 만든다."""

    return re.sub(r"\s+", "", text)


def split_sentences(text: str) -> list[str]:
    """본문을 완결 문장 단위로 나눈다."""

    return [
        sentence.strip()
        for sentence in SENTENCE_BOUNDARY.split(text)
        if sentence and sentence.strip()
    ]


def detect_quotes(evidence: list[str]) -> list[bool]:
    """근거 문장이 전문가 인용인지 판단한다."""

    return [bool(QUOTE_PATTERN.search(sentence)) for sentence in evidence]


def check_banned_terms(text: str) -> list[str]:
    """투자 권유 표현을 검출한다. 수급 용어는 가린 뒤 검사한다."""

    if not text:
        return []

    masked = text
    for term in MASKED_TERMS:
        masked = masked.replace(term, "○")
    return [term for term in BANNED_TERMS if term in masked]


def _resolve_verify_status(
    normalized: str,
    normalized_body: str,
    normalized_sentences: list[str],
) -> str:
    """근거 한 건의 검증 상태를 정한다.

    판정 순서를 바꾸면 환각과 부분 발췌가 구분되지 않는다.
    1. 공백을 지운 근거가 공백을 지운 본문에 없으면 환각이다.
    2. 본문 문장과 통째로 일치하면 정상이다.
    3. 본문 문장의 끝부분과 일치하면 앞의 수식어만 잘린 것이므로 정상으로 본다.
       모델이 "15일 한국거래소에 따르면" 같은 시각·출처 수식어를 자주 떼는데,
       이는 문장의 사실관계를 바꾸지 않는다.
    4. 그 밖에는 문장 뒤가 잘린 것이다. "~했지만 개인은 순매도했다"처럼 뒤에
       붙는 상반 요인이 사라지면 의미가 뒤집히므로 부분 발췌로 남긴다.
    """

    if normalized not in normalized_body:
        return "missing"
    if normalized in normalized_sentences:
        return "ok"
    if any(sentence.endswith(normalized) for sentence in normalized_sentences):
        return "ok"
    return "partial"


def verify_evidence(body: str, evidence: list[str]) -> dict:
    """근거 문장이 본문에 그대로 있는지 확인해 환각과 부분 발췌를 가른다."""

    normalized_body = normalize_for_match(body)
    normalized_sentences = [
        normalize_for_match(item) for item in split_sentences(body)
    ]
    quotes = detect_quotes(evidence)

    evidences: list[dict] = []
    for index, sentence in enumerate(evidence):
        normalized = normalize_for_match(sentence)
        verify_status = _resolve_verify_status(
            normalized, normalized_body, normalized_sentences
        )
        if verify_status == "ok" and normalized not in normalized_sentences:
            logger.info("근거 앞부분이 잘렸으나 사실관계는 유지됩니다: %s", sentence)
        evidences.append(
            {
                "seq": index + 1,
                "sentence": sentence,
                "verify_status": verify_status,
                "is_quote": quotes[index],
            }
        )

    verified = all(item["verify_status"] == "ok" for item in evidences)
    return {"evidence_verified": verified, "evidences": evidences}


def build_sentiment_record(classification: dict, body: str) -> dict:
    """모델 출력에 검증 결과를 덧붙여 저장용 Record를 조립한다."""

    verification = verify_evidence(body, classification["evidence"])
    metadata = classification.get("llm_metadata", {})
    banned_hits = check_banned_terms(classification.get("note", ""))

    if banned_hits:
        logger.warning("판정 note에서 금지 표현 검출: %s", ", ".join(banned_hits))
    for evidence in verification["evidences"]:
        if evidence["verify_status"] != "ok":
            logger.warning(
                "근거 검증 실패(%s): %s",
                evidence["verify_status"],
                evidence["sentence"],
            )

    return {
        "label": classification["label"],
        "confidence": classification["confidence"],
        "rule": classification["rule"],
        "note": classification.get("note", ""),
        "evidence_verified": verification["evidence_verified"],
        "banned_hits": banned_hits,
        "evidences": verification["evidences"],
        "llm_model": metadata.get("llm_model"),
        "llm_prompt_version": metadata.get("llm_prompt_version"),
        "llm_done_reason": metadata.get("llm_done_reason"),
    }
