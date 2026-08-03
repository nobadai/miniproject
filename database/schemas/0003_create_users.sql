-- 목적: 사용자 인증 및 회원 관리를 위한 users 테이블을 생성한다.
-- 주요 역할: 회원 정보, 계정 활성 상태 및 소프트 삭제 상태를 관리한다.
-- TODO(security): 운영 배포 전 password 컬럼을 password_hash로 변경하고
-- 안전한 비밀번호 해시 방식으로 전환해야 한다.

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ NULL,
    CONSTRAINT uq_users_email UNIQUE (email)
);

COMMENT ON TABLE users IS
    '사용자 인증과 회원 정보 관리를 위한 사용자 테이블';

COMMENT ON COLUMN users.id IS
    '사용자를 식별하는 자동 증가 고유 번호';

COMMENT ON COLUMN users.email IS
    '로그인과 사용자 식별에 사용하는 정규화된 고유 이메일 주소';

COMMENT ON COLUMN users.password IS
    '프로토타입 전용 평문 비밀번호. 운영 전 반드시 안전한 비밀번호 해시로 전환해야 함';

COMMENT ON COLUMN users.name IS
    '사용자가 입력한 이름';

COMMENT ON COLUMN users.is_active IS
    '계정 활성 여부. FALSE이면 로그인과 인증이 차단됨';

COMMENT ON COLUMN users.created_at IS
    '사용자 계정이 생성된 시각';

COMMENT ON COLUMN users.updated_at IS
    '사용자 정보가 마지막으로 수정된 시각';

COMMENT ON COLUMN users.deleted_at IS
    '회원탈퇴로 계정이 소프트 삭제된 시각. 탈퇴 전에는 NULL';

COMMENT ON CONSTRAINT users_pkey ON users IS
    '사용자를 식별하는 기본 키';

COMMENT ON CONSTRAINT uq_users_email ON users IS
    '동일한 이메일을 사용하는 사용자의 중복 가입을 방지하는 고유 제약조건';
