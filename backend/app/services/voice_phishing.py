"""보이스피싱 통화의 규칙 점수와 발화 시퀀스를 분석한다.

업로드 오디오를 STT로 전사하거나 준비된 녹취를 읽어 turns를 만들고,
YAML 규칙 기반의 설명 가능한 점수와 상대방 발화의 위험 행동 전이,
KoELECTRA 점수를 융합해 최종 판정을 계산한다. 업로드 원본은 파일로
보관하고 메타데이터와 분석 결과는 Database에 남긴다.
"""

from __future__ import annotations

import hashlib
import logging
import re
import string
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import yaml

from ..clients.whisper_client import WhisperTranscriptionClient
from ..core.config import settings
from ..models.voice_phishing import VoicePhishingAnalysisRecord
from ..repositories import voice_phishing as voice_phishing_repository
from .voice_phishing_model import KoElectraAnalyzer


logger = logging.getLogger(__name__)


BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = (
    BACKEND_ROOT / "resources" / "voice_phishing" / "configs" / "keywords.yaml"
)
TRANSCRIPT_DIRECTORY = (
    BACKEND_ROOT / "resources" / "voice_phishing" / "transcripts"
)
# 영상 컨테이너를 함께 받는다. 전사 전에 ffmpeg 가 오디오 트랙만 뽑아
# 표준 WAV 로 정규화하므로, 분석 계층은 원본 컨테이너를 구분할 필요가 없다.
SUPPORTED_AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".m4a",
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".webm",
}
# 업로드 보관 Root 아래에서 기능별로 나누는 하위 경로이다.
UPLOAD_SUBDIRECTORY = "voice-phishing"
RULE_SCORE_WEIGHT = 0.33
KOELECTRA_SCORE_WEIGHT = 0.34
SEQUENCE_SCORE_WEIGHT = 0.33
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


class UnsupportedAudioFormatError(ValueError):
    """지원하지 않는 오디오 확장자가 입력됐음을 나타낸다."""


class PreparedTranscriptNotFoundError(FileNotFoundError):
    """현재 단계에서 연결할 준비된 녹취가 없음을 나타낸다."""


def analyze_uploaded_audio(audio_bytes: bytes, audio_filename: str) -> dict:
    """업로드 파일을 보관하고 전사·분석한 뒤 결과를 Database에 남긴다.

    같은 내용을 다시 올리면 저장된 직전 분석을 그대로 돌려준다. 전사와 모델
    추론은 통화 길이에 비례해 오래 걸리는 작업인데, 파일 내용이 같으면 결과도
    같기 때문이다.
    """
    transcript_id = validate_audio_filename(audio_filename)
    content_hash = hashlib.sha256(audio_bytes).hexdigest()
    upload = voice_phishing_repository.find_upload_by_content_hash(content_hash)

    if upload is None:
        # 파일을 먼저 쓰고 Row 를 남긴다. 순서를 뒤집으면 저장에 실패했을 때
        # 존재하지 않는 경로를 가리키는 Row 가 생긴다.
        stored_path = store_media_file(audio_bytes, audio_filename, content_hash)
        upload_id = voice_phishing_repository.save_upload(
            original_filename=Path(audio_filename).name,
            stored_path=stored_path,
            content_hash=content_hash,
            media_extension=Path(audio_filename).suffix.lower(),
            byte_size=len(audio_bytes),
        )
    else:
        upload_id = upload.id
        stored_analysis = voice_phishing_repository.find_latest_analysis(upload_id)
        if stored_analysis is not None:
            logger.info("저장된 분석 결과 사용: upload_id=%d", upload_id)
            return build_stored_analysis(
                stored_analysis, audio_filename, transcript_id
            )

    turns = _get_transcription_client().transcribe(audio_bytes, audio_filename)
    analysis = build_analysis(audio_filename, transcript_id, turns)
    voice_phishing_repository.save_analysis(upload_id, analysis)
    return analysis


def store_media_file(
    audio_bytes: bytes, audio_filename: str, content_hash: str
) -> str:
    """업로드 원본을 보관하고 저장 Root 기준 상대 경로를 반환한다.

    파일명이 아니라 내용 해시를 이름으로 쓴다. 같은 통화를 다른 이름으로 올려도
    사본이 늘지 않고, 이름만 같고 내용이 다른 파일이 서로를 덮어쓰지 않는다.
    Database 에는 상대 경로만 남겨 보관 위치를 옮겨도 기존 Row 를 고칠 필요가
    없게 한다.
    """
    relative_path = (
        Path(UPLOAD_SUBDIRECTORY)
        / f"{content_hash}{Path(audio_filename).suffix.lower()}"
    )
    target_path = settings.upload_directory / relative_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(audio_bytes)
    return relative_path.as_posix()


def build_stored_analysis(
    stored_analysis: VoicePhishingAnalysisRecord,
    audio_filename: str,
    transcript_id: str,
) -> dict:
    """저장된 분석 이력을 API 응답 구조로 되돌린다.

    파일명과 식별자는 저장된 값이 아니라 이번 요청 값을 쓴다. 점수는 파일
    내용에서 나오므로 재사용해도 같지만, 화면에는 사용자가 방금 올린 이름이
    보여야 한다.
    """
    return {
        "audio_filename": Path(audio_filename).name,
        "transcript_id": transcript_id,
        "prediction": stored_analysis.prediction,
        "fusion_raw_score": stored_analysis.fusion_raw_score,
        "fusion_score": stored_analysis.fusion_score,
        "rule_score": stored_analysis.rule_score,
        "rule_categories": stored_analysis.rule_categories,
        "sequence_score": stored_analysis.sequence_score,
        "transitions": stored_analysis.transitions,
        "koelectra_score": stored_analysis.koelectra_score,
        "decision_reason": stored_analysis.decision_reason,
        "turns": stored_analysis.turns,
    }


def analyze_prepared_audio(audio_filename: str) -> dict:
    """업로드 오디오 식별자에 대응하는 준비된 TXT를 전체 분석한다."""
    transcript_id, turns = load_prepared_transcript(audio_filename)
    return build_analysis(audio_filename, transcript_id, turns)


def build_analysis(
    audio_filename: str, transcript_id: str, turns: list[dict]
) -> dict:
    """규칙·KoELECTRA·시퀀스 점수를 융합해 API 응답 구조를 만든다."""
    rule_result = RuleScorer().score_call(turns)
    sequence_result = score_sequence(turns)
    model_result = _get_koelectra_analyzer().score(turns)
    prediction, reason = decide_prediction(
        rule_result.score, model_result.score, sequence_result.score
    )
    raw_score = min(
        RULE_SCORE_WEIGHT * rule_result.score
        + KOELECTRA_SCORE_WEIGHT * model_result.score
        + SEQUENCE_SCORE_WEIGHT * sequence_result.score,
        1.0,
    )
    if prediction == "suspicious":
        fusion_score = max(raw_score, 0.75)
    elif prediction == "normal":
        fusion_score = min(raw_score, 0.449999)
    else:
        fusion_score = min(max(raw_score, 0.45), 0.749999)

    return {
        "audio_filename": Path(audio_filename).name,
        "transcript_id": transcript_id,
        "prediction": prediction,
        "fusion_raw_score": round(raw_score, 6),
        "fusion_score": round(fusion_score, 6),
        "rule_score": round(rule_result.score, 6),
        "rule_categories": rule_result.categories_hit,
        "sequence_score": round(sequence_result.score, 6),
        "transitions": sequence_result.transitions,
        "koelectra_score": round(model_result.score, 6),
        "decision_reason": reason,
        "turns": turns,
    }


def validate_audio_filename(audio_filename: str) -> str:
    """업로드 파일명을 검증하고 분석 식별자를 반환한다.

    경로 구분자가 섞인 이름을 그대로 쓰면 의도하지 않은 위치를 가리킬 수
    있어, 파일명 부분만 남는지 먼저 확인한다.
    """
    safe_filename = Path(audio_filename).name
    if safe_filename != audio_filename or not safe_filename:
        raise UnsupportedAudioFormatError("유효하지 않은 오디오 파일명입니다.")
    suffix = Path(safe_filename).suffix.lower()
    if suffix not in SUPPORTED_AUDIO_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_AUDIO_EXTENSIONS))
        raise UnsupportedAudioFormatError(
            f"지원하지 않는 파일 형식입니다. 지원 형식: {supported}"
        )
    return Path(safe_filename).stem


def load_prepared_transcript(audio_filename: str) -> tuple[str, list[dict]]:
    """오디오 파일명과 같은 식별자의 사전 변환 TXT를 읽는다."""
    transcript_id = validate_audio_filename(audio_filename)
    transcript_path = TRANSCRIPT_DIRECTORY / f"{transcript_id}.txt"
    if not transcript_path.is_file():
        raise PreparedTranscriptNotFoundError(
            "준비된 텍스트가 없는 음성입니다. 현재 단계에서는 STT를 사용할 수 없습니다."
        )
    return transcript_id, parse_transcript(
        transcript_path.read_text(encoding="utf-8")
    )


def parse_transcript(text: str) -> list[dict]:
    """금융감독원 녹취의 사기범·피해자 발화를 표준 turns로 변환한다."""
    speaker_mapping = {"사기범": "other", "피해자": "self"}
    turns = []
    for line in text.splitlines():
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#"):
            continue
        speaker, separator, utterance = stripped_line.partition(":")
        if not separator or speaker.strip() not in speaker_mapping:
            continue
        normalized_utterance = utterance.strip()
        if normalized_utterance:
            turns.append(
                {
                    "idx": len(turns),
                    "speaker": speaker_mapping[speaker.strip()],
                    "text": normalized_utterance,
                }
            )
    if not turns:
        raise ValueError("준비된 텍스트에 분석 가능한 발화가 없습니다.")
    return turns


def decide_prediction(
    rule_score: float, model_score: float, sequence_score: float
) -> tuple[str, str]:
    """배포 모델 점수와 규칙·시퀀스 근거를 이용해 최종 판정한다."""
    if rule_score >= 0.75 and sequence_score >= 0.80:
        return "suspicious", "strong_rule_and_sequence"
    if model_score >= 0.80:
        return "suspicious", "model_high"
    if model_score >= 0.70 and sequence_score >= 0.75:
        return "suspicious", "model_and_sequence"
    if model_score <= 0.30 and rule_score < 0.45 and sequence_score < 0.45:
        return "normal", "all_signals_low"
    return "unknown", "signals_conflict_or_uncertain"


@lru_cache(maxsize=1)
def _get_koelectra_analyzer() -> KoElectraAnalyzer:
    """요청마다 GPU 모델을 다시 적재하지 않도록 한 인스턴스를 공유한다."""
    return KoElectraAnalyzer()


@lru_cache(maxsize=1)
def _get_transcription_client() -> WhisperTranscriptionClient:
    """요청마다 STT 모델을 다시 적재하지 않도록 한 인스턴스를 공유한다."""
    return WhisperTranscriptionClient()


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
