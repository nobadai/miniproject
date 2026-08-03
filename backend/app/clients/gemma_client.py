"""gemma_client.py
레이어: Clients
역할: 로컬 Ollama의 Gemma 모델에 시황 기사를 보내 감성 판정 JSON을 받아오며,
      규칙 전문과 Few-shot Message를 조립한다.

규칙 전문과 Few-shot은 Runtime에 바뀌지 않으므로 Resource 파일이 아니라
Module 상수로 둔다. Prompt와 이를 조립하는 Code가 한 곳에 있어야 Few-shot
형식과 실제 입력 형식이 어긋나지 않는다.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from datetime import date


logger = logging.getLogger(__name__)

PROMPT_VERSION = "v2.0"
REQUEST_TIMEOUT_SECONDS = 120

RULE_CODES = [
    "R1", "R2", "R3", "R4", "R5",
    "B01", "B02", "B03", "B04", "B05", "B06", "B07",
    "B08", "B09", "B10", "B11", "B12", "B13", "B14",
]

# 모델이 만드는 값은 이 5개가 전부다. 검증 결과는 Service 계층이 계산해 덧붙인다.
SENTIMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "label": {"type": "string", "enum": ["POS", "NEU", "NEG"]},
        "confidence": {"type": "string", "enum": ["H", "L"]},
        "evidence": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 3,
        },
        "rule": {"type": "string", "enum": RULE_CODES},
        "note": {"type": "string"},
    },
    "required": ["label", "confidence", "evidence", "rule", "note"],
    "additionalProperties": False,
}

# gemma_labeling_spec_v2.0.md A절 규칙 전문이다. 마지막 줄 뒤에 기사 Block이 붙는다.
RULES = """너는 한국 증시 시황뉴스의 감성을 판정하는 분류기다.
설명하지 말고 JSON 하나만 출력한다.

# 판정 질문
"이 기사가 서술하는 시장 상황이 우호적인가, 비우호적인가?"
- 문체가 밝은지 어두운지를 묻는 것이 아니다.
- 앞으로 주가가 오를지 내릴지를 묻는 것이 아니다.

# 판정 대상
개별 기업이 아니라 기사가 다루는 시장 전체(지수·수급·투자심리)다.
특정 종목이 나와도 시장 상황을 설명하는 예시라면 시장 기준으로 판정한다.
기사가 개별 기업·산업만 다루어 시장 전체 함의를 알 수 없으면 R4를 적용한다.

# 라벨 (반드시 이 셋 중 하나)
POS = 시장에 우호적
NEU = 방향이 불분명하거나 상쇄됨
NEG = 시장에 비우호적

점수, 백분율, "Bullish" 같은 다른 척도를 만들지 않는다.

# 규칙 (정해지면 멈춘다. 하나만 적용한다)
R1. 판정 대상인 한국 시장·지수에 대해 시장 기대치와 비교하는 표현이 있으면
    그 방향을 최우선으로 따른다.
    개별 기업 실적이 원인으로 언급된 기대치 비교는 여기 해당하지 않는다.
R2. 절대 수준이 아니라 변화의 방향을 본다.
    "낙폭 축소", "감소세 진정" -> POS
    "상승폭 축소", "증가세 둔화" -> NEG
R3. 우호·비우호 요인이 함께 있으면 제목 뒷부분(주절)의 방향을 따른다.
    근거는 그 방향을 뒷받침하는 본문 문장에서 고른다.
R4. 시장에 대한 함의를 한 문장으로 말할 수 없으면 NEU.
    개별 기업·산업 뉴스로 시장 전체와의 연결이 불분명한 경우가 여기 해당한다.
R5. 그래도 갈리면 NEU. NEU가 기본값이다.

# 경계 사례
B01 혼조세, 보합권, 관망세, 눈치보기 -> NEU
B02 외국인·기관 순매수(전환) -> POS
B03 외국인·기관 순매도(전환) -> NEG
B04 낙폭 과대 반등, 기술적 반등 -> POS
B05 차익실현 매물, 숨고르기 -> NEG
B06 거래대금 감소, 거래 부진 -> NEG
B07 변동성 확대, 불확실성 고조 -> NEG
B08 환율 급등 -> NEG / 환율 안정 -> POS
B09 금리 인하 기대 -> POS / 금리 인상 우려 -> NEG
B10 의문형 제목("반등할까", "바닥인가") -> NEU
B11 장 시작 전 예고, 일정 안내, 지표 발표 예정 -> NEU
B12 특정 업종만 상승하고 지수는 하락 -> NEG
B13 여러 요인이 겹쳐 원인 하나로 좁혀지지 않는 하락 -> NEG
B14 여러 요인이 겹쳐 원인 하나로 좁혀지지 않는 상승 -> POS

경계 사례가 둘 이상 성립하면, 기사가 원인으로 밝힌 것에 가장 가까운 코드를 고른다.

2차 추론은 하지 않는다.
예: 환율 급등이 수출주에 좋다는 식으로 넘겨짚지 않는다.

# 확신도(confidence)
객관적 조건으로만 판단한다. "망설여진다"는 느낌으로 판단하지 않는다.

L = 우호 요인과 비우호 요인이 본문에 함께 있다.
    R3를 적용했으면 항상 L.
H = 방향이 한쪽으로만 분명하다.

L이면 note에 무엇과 무엇이 충돌하는지 한 문장으로 적는다.
H이면 note는 빈 문자열이다.

# 근거(evidence) 선택 규칙
1. 완결된 한 문장을 처음부터 끝까지 통째로 옮긴다.
   문장 중간부터 자르거나 뒷부분을 버리지 않는다.
2. 다음 순서로 고른다.
   (1) 수치가 들어간 사실 서술
   (2) 수치 없는 사실 서술
   (3) 기자의 해석 ("~로 풀이된다", "~한 것이다")
   (4) 전문가 인용 ("~고 설명했다", "~고 밝혔다")
   (3)과 (4)는 (1)(2)로 채울 수 없을 때만 쓴다.
3. 1~3개. 서로 다른 사실을 담은 문장을 고른다.
4. 제목에서 가져오지 않는다. 반드시 본문 문장이어야 한다.
5. 본문에 수급(외국인·기관·개인의 순매수/순매도)이 나오면
   근거에 수급 문장을 반드시 1개 포함한다.

# 금지
- 기사에 없는 수치, 사건, 기업명을 만들지 않는다.
- 이전 대화나 사전 지식을 언급하지 않는다. 매 요청은 독립이다.
- 기사 이후에 벌어진 일을 사용하지 않는다.
- 투자 권유·예측 표현을 쓰지 않는다.
  금지어: 매수, 매도, 사야, 팔아야, 살 때, 지금이, 기회, 시그널,
         유망, 추천, 목표가, 오를 것, 내릴 것, 전망된다
- 영어 금융용어(Bullish, Bearish 등)를 쓰지 않는다.
- 판단 과정을 서술하지 않는다. 라벨부터 확정한다.
- 마크다운, 이모지, 코드블록 표시, 인사말을 쓰지 않는다.

# 출력 (이 JSON만)
{"label":"POS|NEU|NEG","confidence":"H|L","evidence":["본문 문장 전체"],"rule":"코드 하나","note":""}

이제 아래 기사를 판정한다."""


def format_article(title: str, market_date: date | str, body: str) -> str:
    """Prompt 말미에 붙일 기사 Block을 만든다.

    Label 이름은 바꾸지 않는다. Few-shot 10건이 이 표기를 쓰고 있어
    바꾸면 Few-shot을 전부 다시 써야 한다.
    """

    return f"\n\n[제목] {title}\n[발행일] {market_date}\n[본문] {body}"


# gemma_labeling_spec_v2.0.md C절 Few-shot 10건이다.
# 응답은 문자열 그대로 적는다. json.dumps로 만들면 Key 순서와 공백이 문서와
# 달라질 수 있고, 모델이 그 형식을 따라 해 출력이 흔들린다.
FEWSHOT_EXAMPLES: list[tuple[str, str, str, str]] = [
    (
        "외국인, 8거래일 만에 순매수 전환… 코스피 2,660 회복",
        "2026-07-21",
        "외국인이 8거래일 만에 순매수로 돌아섰다. 외국인은 이날 4820억원을 순매수했다. "
        "코스피는 전 거래일 대비 18.4포인트 오른 2,663.4에 마감했다.",
        '{"label":"POS","confidence":"H",'
        '"evidence":["외국인은 이날 4820억원을 순매수했다."],'
        '"rule":"B02","note":""}',
    ),
    (
        "코스피 사흘째 약세… 낙폭은 크게 줄어",
        "2026-07-22",
        "코스피 낙폭이 사흘 만에 크게 줄었다. 전날 42.7포인트 내렸던 지수는 이날 "
        "2.1포인트 하락한 2,661.3에 마감했다. 장 후반 들어 하락 폭을 좁히며 "
        "2,660선을 지켜냈다.",
        '{"label":"POS","confidence":"H",'
        '"evidence":["전날 42.7포인트 내렸던 지수는 이날 2.1포인트 하락한 2,661.3에 마감했다.",'
        '"장 후반 들어 하락 폭을 좁히며 2,660선을 지켜냈다."],'
        '"rule":"R2","note":""}',
    ),
    (
        "7월 수출 시장 예상치 웃돌아… 코스피 2,670선 회복",
        "2026-07-24",
        "7월 수출이 시장 예상치를 웃돌았다. 7월 수출액은 587억달러로 시장 컨센서스 "
        "561억달러를 4.6% 상회했다. 코스피는 12.8포인트 오른 2,672.9에 마감했다.",
        '{"label":"POS","confidence":"H",'
        '"evidence":["7월 수출액은 587억달러로 시장 컨센서스 561억달러를 4.6% 상회했다.",'
        '"코스피는 12.8포인트 오른 2,672.9에 마감했다."],'
        '"rule":"R1","note":""}',
    ),
    (
        "코스피 보합 마감… 방향성 없는 하루",
        "2026-07-27",
        "코스피가 방향을 잡지 못한 채 보합권에서 마감했다. 지수는 전 거래일보다 "
        "0.8포인트 오른 2,661.7에 거래를 마쳤다. 장중 고점과 저점의 차이는 "
        "9.2포인트로 최근 한 달 사이 가장 좁았다.",
        '{"label":"NEU","confidence":"H",'
        '"evidence":["지수는 전 거래일보다 0.8포인트 오른 2,661.7에 거래를 마쳤다.",'
        '"장중 고점과 저점의 차이는 9.2포인트로 최근 한 달 사이 가장 좁았다."],'
        '"rule":"B01","note":""}',
    ),
    (
        "이번 주 미 고용지표 발표… 국내 증시 일정은",
        "2026-07-28",
        "이번 주 국내 증시는 주요 경제지표 발표 일정을 앞두고 있다. 미국 7월 고용지표는 "
        "오는 8월 1일 발표될 예정이다. 국내에서는 같은 날 7월 수출입 동향이 공개된다.",
        '{"label":"NEU","confidence":"H",'
        '"evidence":["미국 7월 고용지표는 오는 8월 1일 발표될 예정이다.",'
        '"국내에서는 같은 날 7월 수출입 동향이 공개된다."],'
        '"rule":"B11","note":""}',
    ),
    (
        "OO바이오, 신약 임상 3상 진입… 주가 12% 급등",
        "2026-07-29",
        "OO바이오가 개발 중인 항암 신약이 임상 3상에 진입했다. 회사는 이날 "
        "식품의약품안전처로부터 3상 시험계획을 승인받았다. OO바이오 주가는 전 거래일보다 "
        "12.4% 오른 8만7400원에 마감했다.",
        '{"label":"NEU","confidence":"H",'
        '"evidence":["OO바이오 주가는 전 거래일보다 12.4% 오른 8만7400원에 마감했다.",'
        '"회사는 이날 식품의약품안전처로부터 3상 시험계획을 승인받았다."],'
        '"rule":"R4","note":""}',
    ),
    (
        "엇갈린 코스피… 지수 상승·외국인 순매도 동시에",
        "2026-07-31",
        "코스피가 사흘 만에 상승했다. 지수는 전 거래일보다 14.2포인트 오른 2,675.5에 "
        "마감했다. 다만 외국인은 이날 3120억원을 순매도해 닷새 연속 순매도를 기록했다.",
        '{"label":"NEU","confidence":"L",'
        '"evidence":["지수는 전 거래일보다 14.2포인트 오른 2,675.5에 마감했다.",'
        '"다만 외국인은 이날 3120억원을 순매도해 닷새 연속 순매도를 기록했다."],'
        '"rule":"R5","note":"지수 상승과 외국인 순매도가 충돌해 방향이 정해지지 않음"}',
    ),
    (
        "원·달러 환율 1,420원 돌파… 8개월 만에 최고",
        "2026-08-01",
        "원·달러 환율이 8개월 만에 1,420원을 넘어섰다. 서울 외환시장에서 원·달러 "
        "환율은 전 거래일보다 18.4원 오른 1,423.6원에 거래를 마쳤다. 코스피는 환율 "
        "부담에 9.6포인트 내린 2,662.3에 마감했다.",
        '{"label":"NEG","confidence":"H",'
        '"evidence":["서울 외환시장에서 원·달러 환율은 전 거래일보다 18.4원 오른 1,423.6원에 거래를 마쳤다.",'
        '"코스피는 환율 부담에 9.6포인트 내린 2,662.3에 마감했다."],'
        '"rule":"B08","note":""}',
    ),
    (
        "지수는 올랐지만… 거래대금 6개월래 최저",
        "2026-07-23",
        "코스피가 3.2포인트 오른 2,655.1에 마감했다. 다만 거래대금은 6조4000억원으로 "
        "6개월 만에 가장 낮은 수준으로 줄었다. 외국인은 1200억원을 순매수했다.",
        '{"label":"NEG","confidence":"L",'
        '"evidence":["다만 거래대금은 6조4000억원으로 6개월 만에 가장 낮은 수준으로 줄었다.",'
        '"외국인은 1200억원을 순매수했다."],'
        '"rule":"R3","note":"지수 상승·외국인 순매수와 거래 부진이 충돌"}',
    ),
    (
        "외국인 1조 넘게 순매도… 코스피 2% 급락",
        "2026-07-25",
        "외국인이 하루에 1조원 넘게 순매도했다. 외국인은 유가증권시장에서 1조2740억원을 "
        "순매도했다. 코스피는 전 거래일보다 54.3포인트(2.01%) 내린 2,646.8에 마감했다.",
        '{"label":"NEG","confidence":"H",'
        '"evidence":["외국인은 유가증권시장에서 1조2740억원을 순매도했다.",'
        '"코스피는 전 거래일보다 54.3포인트(2.01%) 내린 2,646.8에 마감했다."],'
        '"rule":"B03","note":""}',
    ),
]


def _build_fewshot_messages() -> list[dict[str, str]]:
    """첫 user 턴에만 규칙 전문을 붙여 Few-shot Message를 조립한다."""

    messages: list[dict[str, str]] = []
    for index, (title, market_date, body, response) in enumerate(FEWSHOT_EXAMPLES):
        article = format_article(title, market_date, body)
        content = RULES + article if index == 0 else article.lstrip("\n")
        messages.append({"role": "user", "content": content})
        # Gemma Template이 assistant 턴을 model 턴으로 변환한다.
        messages.append({"role": "assistant", "content": response})
    return messages


# 매 요청마다 다시 만들 이유가 없어 Module Level에서 한 번만 조립한다.
FEWSHOT_MESSAGES = _build_fewshot_messages()


class GemmaSentimentError(RuntimeError):
    """Gemma 감성 판정 요청 또는 응답 처리 실패를 나타낸다."""


class GemmaUnavailableError(GemmaSentimentError):
    """Ollama 연결 실패 또는 Timeout을 나타낸다."""


class GemmaEmptyResponseError(GemmaSentimentError):
    """응답 본문이 비어 있음을 나타낸다. think를 끄지 않으면 여기에 해당한다."""


class GemmaSchemaError(ValueError):
    """응답 JSON Parsing 실패 또는 필드 누락을 나타낸다."""


class GemmaSentimentClient:
    """Ollama 호출 설정과 감성 판정 요청을 관리한다."""

    def __init__(
        self,
        *,
        host: str,
        model: str,
        num_ctx: int,
        num_gpu: int,
        timeout: int = REQUEST_TIMEOUT_SECONDS,
    ) -> None:
        if not host.strip():
            raise ValueError("Ollama 주소가 비어 있습니다.")
        if not model.strip():
            raise ValueError("Ollama 모델명이 비어 있습니다.")
        self.host = host.rstrip("/")
        self.model = model
        self.num_ctx = num_ctx
        self.num_gpu = num_gpu
        self.timeout = timeout

    def _build_payload(self, prompt: str) -> dict:
        """Ollama /api/chat 요청 본문을 만든다.

        think 는 options 안이 아니라 최상위에 둔다. options 안에 넣으면 무시되어
        사고과정이 토큰을 모두 소비하고 응답이 빈 문자열이 된다.
        num_gpu 를 고정하지 않으면 재실행마다 판정이 뒤집힌다.
        """

        return {
            "model": self.model,
            "messages": [*FEWSHOT_MESSAGES, {"role": "user", "content": prompt}],
            "format": SENTIMENT_SCHEMA,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0,
                "seed": 0,
                "num_predict": 400,
                "num_ctx": self.num_ctx,
                "num_gpu": self.num_gpu,
            },
        }

    def _request_chat(self, prompt: str) -> dict:
        """Ollama /api/chat을 호출하고 응답 전체를 반환한다."""

        request = urllib.request.Request(
            f"{self.host}/api/chat",
            data=json.dumps(self._build_payload(prompt)).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            logger.exception("Ollama 감성 판정 요청 실패")
            raise GemmaUnavailableError(
                f"Ollama에 연결하지 못했습니다: {self.host}"
            ) from error

        try:
            return json.loads(body)
        except json.JSONDecodeError as error:
            raise GemmaSchemaError("Ollama 응답이 올바른 JSON이 아닙니다.") from error

    def classify(self, *, title: str, market_date: date | str, body: str) -> dict:
        """기사 한 건의 감성을 판정하고 모델 출력 5필드와 실행 정보를 반환한다."""

        prompt = RULES + format_article(title, market_date, body)
        response = self._request_chat(prompt)

        content = (response.get("message") or {}).get("content", "")
        if not content.strip():
            raise GemmaEmptyResponseError(
                "Gemma 응답이 비어 있습니다. think 설정을 확인하세요."
            )

        try:
            data = json.loads(content)
        except json.JSONDecodeError as error:
            raise GemmaSchemaError("Gemma 응답이 올바른 JSON이 아닙니다.") from error

        missing = [
            name
            for name in ("label", "confidence", "evidence", "rule", "note")
            if name not in data
        ]
        if missing:
            raise GemmaSchemaError(
                f"Gemma 응답에 필드가 없습니다: {', '.join(missing)}"
            )
        if not isinstance(data["evidence"], list) or not data["evidence"]:
            raise GemmaSchemaError("Gemma 응답의 근거가 비어 있습니다.")

        return {
            "label": data["label"],
            "confidence": data["confidence"],
            "evidence": [str(sentence) for sentence in data["evidence"]],
            "rule": data["rule"],
            "note": data["note"],
            "llm_metadata": {
                "llm_model": self.model,
                "llm_prompt_version": PROMPT_VERSION,
                "llm_done_reason": response.get("done_reason"),
            },
        }
