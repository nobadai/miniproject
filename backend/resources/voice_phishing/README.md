# 보이스피싱 분석 데이터

금융감독원 `그놈 목소리` 공개 자료에서 수집한 텍스트와 보이스피싱 분석용 기준 데이터를 보관한다.

- `configs/`: 규칙 기반 판별 설정
- `evaluations/`: KoELECTRA 학습·평가용 JSONL
- `raw_texts/`: 선별한 원문을 분석 입력 형식으로 정리한 TXT
- `transcripts/`: 금융감독원 게시글에 공개된 녹취 TXT
- `metadata.csv`: 공개 자료의 게시글·파일·출처 연결 정보

현재 API 단계에서는 업로드한 오디오의 파일 식별자와 `transcripts/`의 같은 식별자를 연결한다. 실제 STT가 추가되면 이 연결 부분을 STT 결과로 교체한다.

`evaluations/eval_v1.jsonl`이 현재 학습과 평가의 기준 입력이다. 나머지 JSONL은 데이터 생성 과정의 스냅샷이므로 서로 무조건 병합하지 않는다.
