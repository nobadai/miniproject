"""whisper_client.py
레이어: Clients
역할: 업로드된 통화 오디오를 ffmpeg로 정규화하고 faster-whisper로 전사해
      보이스피싱 분석 서비스가 사용하는 표준 turns 구조로 반환하며,
      같은 오디오를 다시 올렸을 때 전사 결과를 재사용한다.
"""

import hashlib
import json
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel

from ..core.config import settings


logger = logging.getLogger(__name__)

TARGET_SAMPLE_RATE = 16000
TELEPHONY_BAND_HZ = (300, 3400)
NORMALIZED_AUDIO_NAME = "normalized.wav"
BEAM_SIZE = 5
VAD_MIN_SILENCE_MS = 500
NO_SPEECH_THRESHOLD = 0.6
FFMPEG_ERROR_LOG_LIMIT = 300
CACHE_SCHEMA_VERSION = "stt-cache-v1"
CACHE_FINGERPRINT_LENGTH = 12


class AudioTranscriptionError(RuntimeError):
    """오디오 변환 또는 전사 처리가 실패했음을 나타낸다."""


class EmptyTranscriptionError(ValueError):
    """오디오에서 분석할 발화를 얻지 못했음을 나타낸다."""


def normalize_audio(source_path: Path) -> Path:
    """전사 입력으로 사용할 mono 16kHz PCM WAV를 생성한다.

    Whisper는 다양한 컨테이너를 직접 열 수 있지만, 통화 녹음은 코덱과 채널
    구성이 제각각이라 먼저 하나의 형식으로 맞춘다. 전화 대역 통과 필터는
    통화가 아닌 대역의 잡음이 전사 품질을 떨어뜨리는 것을 막는다.
    """
    if shutil.which("ffmpeg") is None:
        raise AudioTranscriptionError(
            "ffmpeg를 찾을 수 없습니다. 오디오 변환 도구를 설치해야 합니다."
        )

    target_path = source_path.parent / NORMALIZED_AUDIO_NAME
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(source_path),
    ]
    if settings.stt_telephony_band:
        low_hz, high_hz = TELEPHONY_BAND_HZ
        command += ["-af", f"highpass=f={low_hz},lowpass=f={high_hz}"]
    command += [
        "-ac",
        "1",
        "-ar",
        str(TARGET_SAMPLE_RATE),
        "-c:a",
        "pcm_s16le",
        str(target_path),
    ]

    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        logger.error(
            "오디오 정규화 실패: %s",
            completed.stderr.strip()[:FFMPEG_ERROR_LOG_LIMIT],
        )
        raise AudioTranscriptionError(
            "오디오를 변환할 수 없습니다. 손상되었거나 지원하지 않는 파일입니다."
        )
    return target_path


def build_turns(texts: list[str]) -> list[dict]:
    """전사 문장을 분석 계층이 읽는 turns 구조로 변환한다.

    화자 분리를 수행하지 않으므로 모든 발화를 상대방(other)으로 둔다.
    시퀀스 분석은 상대 발화만 태깅하기 때문에, 근거 없이 화자를 나누면
    위험 발화가 본인 쪽으로 잘못 배정되어 점수가 사라질 수 있다.
    """
    turns = []
    for text in texts:
        stripped_text = text.strip()
        if stripped_text:
            turns.append(
                {"idx": len(turns), "speaker": "other", "text": stripped_text}
            )
    return turns


def transcription_fingerprint() -> str:
    """전사 결과를 재사용해도 되는지 판별할 설정 지문을 만든다.

    모델이나 전처리가 바뀌면 같은 오디오라도 전사문이 달라진다. 설정을
    캐시 키에 포함하지 않으면 모델을 바꾼 뒤에도 옛 전사문이 반환된다.
    """
    payload = "|".join(
        [
            CACHE_SCHEMA_VERSION,
            settings.stt_model_size,
            settings.stt_compute_type,
            settings.stt_language,
            str(settings.stt_telephony_band),
        ]
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return digest[:CACHE_FINGERPRINT_LENGTH]


def cache_path(audio_bytes: bytes) -> Path:
    """오디오 내용 해시로 전사 캐시 경로를 만든다.

    파일명이 아니라 내용을 키로 쓴다. 같은 통화를 다른 이름으로 올려도
    재사용되고, 이름만 같고 내용이 다른 파일은 섞이지 않는다.
    """
    audio_digest = hashlib.sha256(audio_bytes).hexdigest()
    return settings.stt_cache_directory / transcription_fingerprint() / f"{audio_digest}.json"


def read_cached_turns(path: Path) -> list[dict] | None:
    """캐시된 전사 결과를 읽는다. 손상된 캐시는 없는 것으로 취급한다."""
    if not path.is_file():
        return None
    try:
        cached = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.warning("전사 캐시가 손상되어 다시 전사합니다: %s", path.name)
        return None
    turns = cached.get("turns")
    return turns or None


def write_cached_turns(path: Path, turns: list[dict]) -> None:
    """전사 결과를 원자적으로 기록한다.

    같은 오디오로 동시에 두 요청이 들어와도 반쪽 JSON이 남지 않도록
    임시 파일에 쓴 뒤 교체한다.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(".json.tmp")
    temporary_path.write_text(
        json.dumps({"turns": turns}, ensure_ascii=False), encoding="utf-8"
    )
    temporary_path.replace(path)


class WhisperTranscriptionClient:
    """faster-whisper 모델을 한 번 적재해 요청 간 재사용한다."""

    def __init__(self) -> None:
        self.model = WhisperModel(
            settings.stt_model_size,
            device=settings.stt_device,
            compute_type=settings.stt_compute_type,
        )

    def transcribe(self, audio_bytes: bytes, audio_filename: str) -> list[dict]:
        """업로드 오디오 바이트를 표준 turns로 전사한다.

        전사는 통화 길이에 비례해 오래 걸리므로, 같은 오디오와 같은 설정이면
        이전 결과를 그대로 쓴다.
        """
        cache_file = cache_path(audio_bytes)
        cached_turns = read_cached_turns(cache_file)
        if cached_turns is not None:
            logger.info("전사 캐시 사용: %s (발화 %d개)", cache_file.name, len(cached_turns))
            return cached_turns

        with tempfile.TemporaryDirectory() as work_directory:
            source_path = Path(work_directory) / Path(audio_filename).name
            source_path.write_bytes(audio_bytes)
            normalized_path = normalize_audio(source_path)
            texts = self._read_segment_texts(normalized_path)

        turns = build_turns(texts)
        if not turns:
            raise EmptyTranscriptionError(
                "오디오에서 발화를 찾지 못했습니다. 무음이거나 통화 내용이 없습니다."
            )
        write_cached_turns(cache_file, turns)
        logger.info("전사 완료: %s (발화 %d개)", cache_file.name, len(turns))
        return turns

    def _read_segment_texts(self, audio_path: Path) -> list[str]:
        """전사 세그먼트를 모두 소비해 문장 목록으로 만든다.

        faster-whisper는 세그먼트를 지연 생성하므로, 임시 디렉터리가
        지워지기 전에 여기서 전부 읽어 두어야 한다.
        """
        segments, _ = self.model.transcribe(
            str(audio_path),
            language=settings.stt_language,
            beam_size=BEAM_SIZE,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": VAD_MIN_SILENCE_MS},
            no_speech_threshold=NO_SPEECH_THRESHOLD,
            condition_on_previous_text=False,
        )
        return [segment.text for segment in segments]
