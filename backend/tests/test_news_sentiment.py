"""감성 판정의 근거 검증과 저장용 Record 조립을 검증한다."""

import unittest

from app.services.news_sentiment import (
    build_sentiment_record,
    check_banned_terms,
    detect_quotes,
    normalize_for_match,
    split_sentences,
    verify_evidence,
)


BODY = (
    "13일 한국거래소에 따르면 이날 오전 10시 23분 현재 코스피는 전 거래일 대비 "
    "267.75p(-3.58%) 내린 7208.19에 거래 중이다.\n\n"
    "유가증권시장에서는 개인이 7668억원을 순매수 중이고 외국인과 기관이 각각 "
    "3221억원, 4137억원을 순매도했다.\n\n"
    '강진혁 신한투자증권 연구원은 "전날 급등에 따른 매물 출회가 이어지고 있다"고 설명했다.'
)

FULL_SENTENCE = (
    "13일 한국거래소에 따르면 이날 오전 10시 23분 현재 코스피는 전 거래일 대비 "
    "267.75p(-3.58%) 내린 7208.19에 거래 중이다."
)
SUPPLY_SENTENCE = (
    "유가증권시장에서는 개인이 7668억원을 순매수 중이고 외국인과 기관이 각각 "
    "3221억원, 4137억원을 순매도했다."
)


def make_classification(evidence: list[str], *, note: str = "") -> dict:
    return {
        "label": "NEG",
        "confidence": "L" if note else "H",
        "evidence": evidence,
        "rule": "R3",
        "note": note,
        "llm_metadata": {
            "llm_model": "gemma4:12b-it-qat",
            "llm_prompt_version": "v2.0",
            "llm_done_reason": "stop",
        },
    }


class EvidenceVerificationTests(unittest.TestCase):
    def test_sentence_is_split_on_korean_and_common_endings(self) -> None:
        sentences = split_sentences(BODY)

        self.assertEqual(len(sentences), 3)
        self.assertTrue(sentences[0].endswith("거래 중이다."))

    def test_whitespace_is_ignored_when_matching(self) -> None:
        self.assertEqual(normalize_for_match(" 코스피 는  올랐다. "), "코스피는올랐다.")

    def test_exact_sentence_is_marked_ok(self) -> None:
        result = verify_evidence(BODY, [FULL_SENTENCE])

        self.assertTrue(result["evidence_verified"])
        self.assertEqual(result["evidences"][0]["verify_status"], "ok")
        self.assertEqual(result["evidences"][0]["seq"], 1)

    def test_sentence_absent_from_body_is_marked_missing(self) -> None:
        evidence = ["코스닥은 전 거래일보다 15.38p 오른 800.00에 마감했다."]

        result = verify_evidence(BODY, evidence)

        self.assertEqual(result["evidences"][0]["verify_status"], "missing")
        self.assertFalse(result["evidence_verified"])

    def test_leading_attribution_trimmed_is_accepted(self) -> None:
        """앞의 시각·출처 수식어만 잘린 근거는 사실관계가 그대로라 통과시킨다."""

        evidence = ["코스피는 전 거래일 대비 267.75p(-3.58%) 내린 7208.19에 거래 중이다."]

        result = verify_evidence(BODY, evidence)

        self.assertEqual(result["evidences"][0]["verify_status"], "ok")
        self.assertTrue(result["evidence_verified"])

    def test_sentence_cut_at_the_tail_is_marked_partial(self) -> None:
        """뒤가 잘리면 상반 요인이 사라져 의미가 뒤집힐 수 있으므로 남긴다."""

        evidence = ["유가증권시장에서는 개인이 7668억원을 순매수 중이고"]

        result = verify_evidence(BODY, evidence)

        self.assertEqual(result["evidences"][0]["verify_status"], "partial")
        self.assertFalse(result["evidence_verified"])

    def test_fragment_cut_on_both_sides_is_marked_partial(self) -> None:
        evidence = ["코스피는 전 거래일 대비 267.75p(-3.58%) 내린"]

        result = verify_evidence(BODY, evidence)

        self.assertEqual(result["evidences"][0]["verify_status"], "partial")

    def test_quotation_is_detected_for_source_attribution(self) -> None:
        quoted = '강진혁 신한투자증권 연구원은 "전날 급등에 따른 매물 출회가 이어지고 있다"고 설명했다.'

        self.assertEqual(detect_quotes([quoted, FULL_SENTENCE]), [True, False])


class BannedTermTests(unittest.TestCase):
    def test_supply_and_demand_terms_are_not_treated_as_banned(self) -> None:
        text = "외국인이 순매수했고 기관은 순매도했다."

        self.assertEqual(check_banned_terms(text), [])

    def test_bare_supply_terms_in_note_are_not_treated_as_banned(self) -> None:
        """시황 note는 수급 주체를 '기관·외국인 매수'처럼 그대로 쓴다."""

        text = "지수 상승 및 기관·외국인 매수와 개인 순매도 요인이 충돌"

        self.assertEqual(check_banned_terms(text), [])

    def test_recommendation_with_supply_term_is_still_detected(self) -> None:
        text = "지금이 매수 추천 구간이다."

        hits = check_banned_terms(text)

        self.assertIn("추천", hits)
        self.assertIn("지금이", hits)

    def test_investment_recommendation_is_detected(self) -> None:
        text = "지금이 저점 매수 기회다."

        hits = check_banned_terms(text)

        self.assertIn("지금이", hits)
        self.assertIn("기회", hits)

    def test_empty_text_has_no_hits(self) -> None:
        self.assertEqual(check_banned_terms(""), [])


class SentimentRecordTests(unittest.TestCase):
    def test_record_carries_model_output_and_verification(self) -> None:
        record = build_sentiment_record(
            make_classification([FULL_SENTENCE, SUPPLY_SENTENCE]),
            BODY,
        )

        self.assertEqual(record["label"], "NEG")
        self.assertEqual(record["rule"], "R3")
        self.assertTrue(record["evidence_verified"])
        self.assertEqual(len(record["evidences"]), 2)
        self.assertEqual(record["evidences"][1]["seq"], 2)
        self.assertEqual(record["llm_model"], "gemma4:12b-it-qat")
        self.assertEqual(record["llm_prompt_version"], "v2.0")
        self.assertEqual(record["llm_done_reason"], "stop")
        self.assertEqual(record["banned_hits"], [])

    def test_banned_term_in_note_is_recorded(self) -> None:
        record = build_sentiment_record(
            make_classification([FULL_SENTENCE], note="지금이 기회로 보인다"),
            BODY,
        )

        self.assertIn("기회", record["banned_hits"])
        self.assertEqual(record["confidence"], "L")


if __name__ == "__main__":
    unittest.main()
