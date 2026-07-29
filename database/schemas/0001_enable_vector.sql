-- 목적: 새 Database에서 pgvector Extension을 활성화한다.
-- 주요 역할: 실제 서비스 Table 없이 Vector Type 사용 기반만 제공한다.

CREATE EXTENSION IF NOT EXISTS vector;
