"""보이스피싱 텍스트의 규칙 점수와 발화 시퀀스를 분석한다.

YAML 규칙을 이용한 설명 가능한 점수와 상대방 발화의 위험 행동 전이를
계산하며, HTTP나 파일 업로드 방식에는 의존하지 않는다.
"""

from __future__ import annotations

import re
import string
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml


BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = (
    BACKEND_ROOT / "resources" / "voice_phishing" / "configs" / "keywords.yaml"
)
PUNCTUATION_TRANSLATION = str.maketrans(
    "", "", string.punctuation + "·…‥「」『』〈〉《》\"\"''"
)

ACT_PATTERNS = {
    "신원제시": r"수사관|담당검사|금융감독원|금감원|검찰청|중앙지검|경찰청|사이버수사대",
    "문제제기": r"명의.?도용|대포.?통장|사건.{0,8}(?:연루|접수|조사)|범죄|불법.?자금|계좌.{0,10}(?:개설|동결|정지)|피해자.?입증|구속|영장|고소|고발",
    "정보요구": r"(?:(?:생년월일|주민번호|계좌번호|비밀번호|인증번호|잔액|재산|자산|연소득).{0,15}(?:말씀|알려|불러|얼마|확인)|(?:말씀|알려|불러).{0,15}(?:생년월일|주민번호|계좌번호|비밀번호|인증번호|잔액|재산|자산|연소득)|은행.{0,10}(?:어디|몇))",
    "격리요구": r"(?:(?:가족|직원|주변.{0,3}사람|누구에게도|아무에게도|제.?3자|제.?삼자|타인).{0,18}(?:말하지|알리지|발설)|(?:말씀|발설).{0,8}(?:안.?됩니다|마세요)|(?:수사|조사).{0,6}(?:기밀|비밀)|(?:통화|전화).{0,10}(?:끊지|유지)|혼자.{0,8}(?:계시|있)|조용한.{0,5}(?:곳|장소)|자택으로.{0,8}(?:가|이동))",
    "행위지시": r"(?:(?:이체|송금|입금).{0,12}(?:해.?주|하셔|하세요|해야|하십시오|하십쇼|해라)|대출.{0,12}(?:받으|받아|진행하|신청하)|(?:앱|어플|프로그램).{0,10}(?:설치하|깔아|다운로드하)|링크.{0,10}(?:접속하|누르|클릭)|(?:은행|지점|창구).{0,12}(?:가시|가셔|방문하|이동하)|설정.{0,8}(?:들어가|여시)|(?:데이터|와이파이).{0,8}차단.{0,8}(?:해|하셔|하세요)|(?:전화|번호).{0,10}(?:걸어|누르|전화하)|(?:otp|인증번호|비밀번호).{0,10}(?:알려|불러))",
    "종료": r"(?:상담|통화|조사).{0,10}(?:종료|마치)|수고하셨습니다|좋은 하루|안녕히|끊겠습니다",
}
ACT_REGEX = {
    name: re.compile(pattern, re.IGNORECASE)
    for name, pattern in ACT_PATTERNS.items()
}
SAFE_CONTEXT = re.compile(
    r"(?:(?:비밀번호|보안카드|cvc|otp|인증번호).{0,25}(?:요구|여쭤|알려|보관).{0,10}(?:않|안|없)|"
    r"(?:링크|앱|어플).{0,25}(?:누르|설치|접속).{0,10}(?:마세요|않|안)|"
    r"(?:악성|보이스피싱|사기).{0,20}(?:주의|조심|예방|설치|링크)|"
    r"(?:비밀번호|보안카드|cvc|otp|인증번호).{0,20}(?:타인|누구).{0,15}(?:알려|공유)|"
    r"(?:대표번호|카드.?뒷면).{0,20}(?:다시|직접).{0,10}(?:확인|연락))",
    re.IGNORECASE,
)


def normalize(text: str, config: dict) -> str:
    """원문과 규칙 용어에 같은 정규화를 적용한다."""
    if config.get("lowercase", True):
        text = text.lower()
    if config.get("strip_punctuation", True):
        text = text.translate(PUNCTUATION_TRANSLATION)
    if config.get("strip_spaces", True):
        return re.sub(r"\s+", "", text)
    return re.sub(r"\s+", " ", text).strip()


@dataclass(frozen=True)
class Evidence:
    """규칙에 일치한 카테고리와 원문 근거이다."""

    category: str
    term: str
    snippet: str


@dataclass
class RuleScore:
    """규칙 스코어러가 반환하는 판정 결과이다."""

    score: float
    verdict: str
    confidence: str
    categories_hit: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    breakdown: dict = field(default_factory=dict)


@dataclass(frozen=True)
class SequenceScore:
    """위험 발화의 존재와 전이 분석 결과이다."""

    score: float
    transitions: list[str]
    evidence: list[dict]


class RuleScorer:
    """YAML 설정을 읽어 텍스트와 통화 단위 위험 점수를 계산한다."""

    def __init__(self, config_path: Path | str = DEFAULT_CONFIG_PATH):
        with Path(config_path).open(encoding="utf-8") as file:
            self.config = yaml.safe_load(file)

        self.normalize_config = self.config.get("normalize", {})
        self.categories = self.config["categories"]
        self.negative = self.config.get("negative", {})
        self.combination = self.config.get("combination", {})
        self.thresholds = self.config["thresholds"]
        self.score_cap = float(self.config.get("score_cap", 1.0))
        self.category_terms = {
            name: [(term, normalize(term, self.normalize_config)) for term in spec["terms"]]
            for name, spec in self.categories.items()
        }
        self.negative_terms = [
            (term, normalize(term, self.normalize_config))
            for term in self.negative.get("terms", [])
        ]

    def score_text(self, text: str) -> RuleScore:
        """단일 텍스트의 규칙 점수와 근거를 반환한다."""
        hits, negative_count = self._find_hits(text)
        base_score = sum(float(self.categories[category]["weight"]) for category in hits)
        category_count = len(hits)
        multipliers = {
            int(key): float(value)
            for key, value in self.combination.get("multipliers", {}).items()
        }
        if category_count == 0:
            multiplier = 1.0
        elif category_count in multipliers:
            multiplier = multipliers[category_count]
        else:
            multiplier = max(multipliers.values()) if multipliers else 1.0

        bonus = 0.0
        bonus_pairs = []
        for rule in self.combination.get("bonus_pairs", []):
            first_category, second_category = rule["pair"]
            if first_category in hits and second_category in hits:
                bonus += float(rule["bonus"])
                bonus_pairs.append(f"{first_category}+{second_category}")

        penalty = negative_count * float(self.negative.get("weight", 0.0))
        score = max(
            0.0,
            min(self.score_cap, base_score * multiplier + bonus + penalty),
        )
        verdict, confidence = self._verdict(score)
        evidence = [item for category_hits in hits.values() for item in category_hits]
        return RuleScore(
            score=score,
            verdict=verdict,
            confidence=confidence,
            categories_hit=sorted(hits),
            evidence=evidence,
            breakdown={
                "base": round(base_score, 4),
                "n_categories": category_count,
                "multiplier": multiplier,
                "bonus": round(bonus, 4),
                "bonus_pairs": bonus_pairs,
                "negative_hits": negative_count,
                "penalty": round(penalty, 4),
            },
        )

    def score_call(
        self, turns: Iterable[dict], window: int = 3, top_k: int = 3
    ) -> RuleScore:
        """상위 텍스트 윈도우를 이용해 통화 전체 점수를 계산한다."""
        texts = [turn["text"] for turn in turns]
        if not texts:
            return RuleScore(score=0.0, verdict="unknown", confidence="low")

        windows = [
            "\n".join(texts[index : index + window])
            for index in range(max(1, len(texts) - window + 1))
        ]
        results = sorted(
            (self.score_text(text) for text in windows),
            key=lambda result: result.score,
            reverse=True,
        )
        result_count = max(1, min(top_k, round(len(results) * 0.5)))
        selected_results = results[:result_count]
        score = sum(result.score for result in selected_results) / len(selected_results)
        verdict, confidence = self._verdict(score)
        merged_evidence = {
            (evidence.category, evidence.term): evidence
            for result in selected_results
            for evidence in result.evidence
        }
        return RuleScore(
            score=score,
            verdict=verdict,
            confidence=confidence,
            categories_hit=sorted(
                {
                    category
                    for result in selected_results
                    for category in result.categories_hit
                }
            ),
            evidence=list(merged_evidence.values()),
            breakdown={
                "n_windows": len(windows),
                "top_window_scores": [
                    round(result.score, 4) for result in selected_results
                ],
            },
        )

    def _find_hits(self, raw_text: str) -> tuple[dict[str, list[Evidence]], int]:
        normalized_text = normalize(raw_text, self.normalize_config)
        hits: dict[str, list[Evidence]] = {}
        for category, terms in self.category_terms.items():
            for original, normalized_term in terms:
                if normalized_term and normalized_term in normalized_text:
                    hits.setdefault(category, []).append(
                        Evidence(
                            category=category,
                            term=original,
                            snippet=_snippet(raw_text, original),
                        )
                    )
        negative_count = sum(
            1
            for _, normalized_term in self.negative_terms
            if normalized_term and normalized_term in normalized_text
        )
        return hits, negative_count

    def _verdict(self, score: float) -> tuple[str, str]:
        normal_max = float(self.thresholds["normal_max"])
        suspicious_min = float(self.thresholds["suspicious_min"])
        if score >= suspicious_min:
            confidence = "high" if score >= suspicious_min + 0.15 else "medium"
            return "suspicious", confidence
        if score < normal_max:
            confidence = "high" if score < normal_max - 0.20 else "medium"
            return "normal", confidence
        return "unknown", "low"


def score_sequence(turns: list[dict]) -> SequenceScore:
    """상대방 위험 발화의 존재와 순서를 점수화한다."""
    tagged_turns = _tag_turns(turns)
    present_tags = {tag for tags in tagged_turns for tag in tags}
    weights = {
        "신원제시": 0.10,
        "문제제기": 0.15,
        "정보요구": 0.10,
        "격리요구": 0.25,
        "행위지시": 0.20,
    }
    score = sum(weight for tag, weight in weights.items() if tag in present_tags)
    transitions = []
    for pattern, bonus in [
        (["신원제시", "문제제기"], 0.05),
        (["문제제기", "정보요구"], 0.05),
        (["문제제기", "격리요구"], 0.15),
        (["격리요구", "행위지시"], 0.20),
    ]:
        if _has_order(tagged_turns, pattern):
            score += bonus
            transitions.append("→".join(pattern))

    full_pattern = ["신원제시", "문제제기", "격리요구", "행위지시"]
    if _has_order(tagged_turns, full_pattern):
        score = 1.0
        transitions.append("→".join(full_pattern))

    evidence = []
    for index, tags in enumerate(tagged_turns):
        for tag in sorted(tags):
            if tag not in {item["act"] for item in evidence}:
                evidence.append(
                    {"act": tag, "turn": index, "text": turns[index]["text"][:100]}
                )
    return SequenceScore(
        score=min(score, 1.0), transitions=transitions, evidence=evidence
    )


def _tag_turns(turns: list[dict]) -> list[set[str]]:
    tagged_turns = []
    for turn in turns:
        if turn.get("speaker") != "other":
            tagged_turns.append(set())
            continue
        text = turn["text"]
        tags = {
            name for name, pattern in ACT_REGEX.items() if pattern.search(text)
        }
        if SAFE_CONTEXT.search(text):
            tags.difference_update({"격리요구", "행위지시"})
        tagged_turns.append(tags)
    return tagged_turns


def _has_order(tagged_turns: list[set[str]], pattern: list[str]) -> bool:
    position = -1
    for wanted_tag in pattern:
        position = next(
            (
                index
                for index in range(position + 1, len(tagged_turns))
                if wanted_tag in tagged_turns[index]
            ),
            -1,
        )
        if position < 0:
            return False
    return True


def _snippet(raw_text: str, term: str, padding: int = 20) -> str:
    loose_term = re.compile(
        r"\s*".join(map(re.escape, term.replace(" ", ""))), re.IGNORECASE
    )
    match = loose_term.search(raw_text)
    if not match:
        return term
    start = max(0, match.start() - padding)
    end = min(len(raw_text), match.end() + padding)
    return (
        ("…" if start > 0 else "")
        + raw_text[start:end].strip()
        + ("…" if end < len(raw_text) else "")
    )
