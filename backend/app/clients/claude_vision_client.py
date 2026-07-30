"""claude_vision_client.py
레이어: Clients
역할: Anthropic Messages API(Vision)를 호출해 금융 사기 스크린샷을 분석하고,
      모델 응답에서 JSON 결과를 방어적으로 추출해 반환한다.
"""

import base64
import json
import logging
import re

import anthropic

from ..core.config import settings


logger = logging.getLogger(__name__)

MODEL_NAME = "claude-sonnet-5"

SYSTEM_PROMPT = """당신은 금융 사기 스크린샷을 탐지하는 보조 시스템입니다.
입력된 이미지는 은행/카드/간편결제 앱의 화면 캡처입니다. 아래 규칙에 따라
이미지를 분석하고, 반드시 JSON 하나만 출력하세요. 설명, 마크다운 코드블록,
그 외 텍스트는 절대 포함하지 마세요.

# 분류 기준 (3-class)
- "정상": 실제 은행/카드/간편결제 앱의 정상적인 이체·거래·조회 화면으로 보임. 금액, 문구, UI 요소에 조작 흔적이 없음.
- "사기의심": 아래 변조 유형 중 하나 이상이 관찰되어 조작/사기 의도가 의심됨.
- "판단불가": 해상도가 너무 낮거나, 화면이 잘려서 핵심 정보를 확인할 수 없거나, 블러 처리되어 판독이 불가능한 경우.

# 변조 유형 후보 (관찰되는 것만 배열로, 없으면 빈 배열)
금액위조, 과장문구삽입, 긴급성유도, 발신기관사칭, 출금지연_전산오류핑계, 본인인증_재인증유도_오버레이, UI위조, 계좌정보불일치, 기타

# 출력 JSON 스키마 (키 이름 정확히 지킬 것)
{
  "verdict": "정상" | "사기의심" | "판단불가",
  "tamper_types": [문자열, ...],
  "reasoning": "화면에서 실제로 관찰한 내용을 근거로 1~3문장, 한국어로",
  "confidence": 0.0에서 1.0 사이 숫자,
  "undetermined_reason": "verdict가 판단불가일 때만 채움, 아니면 null"
}
"""

_CODE_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _extract_json_text(raw_text: str) -> str:
    """모델이 지시를 어기고 코드블록으로 감싼 경우를 대비해 JSON 본문만 추출한다."""

    text = raw_text.strip()
    if text.startswith("```"):
        text = _CODE_FENCE_PATTERN.sub("", text).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("응답에서 JSON 객체를 찾을 수 없습니다")

    return text[start : end + 1]


def analyze_image(image_bytes: bytes, media_type: str) -> dict:
    """이미지를 Claude Vision에 전달해 사기 여부 분석 결과를 JSON dict로 반환한다."""

    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY가 설정되지 않았습니다")

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key.get_secret_value())
    image_data = base64.standard_b64encode(image_bytes).decode("utf-8")

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": "이 화면을 분석하고 지정된 JSON 스키마로만 응답하세요.",
                        },
                    ],
                }
            ],
        )
    except anthropic.APIError:
        logger.exception("Claude Vision API 호출 실패")
        raise

    text_blocks = [block.text for block in response.content if block.type == "text"]
    if not text_blocks:
        raise ValueError("Claude 응답에 텍스트 블록이 없습니다")

    raw_text = "".join(text_blocks)

    try:
        json_text = _extract_json_text(raw_text)
        return json.loads(json_text)
    except (ValueError, json.JSONDecodeError):
        logger.exception("Claude 응답 JSON 파싱 실패: %s", raw_text)
        raise
