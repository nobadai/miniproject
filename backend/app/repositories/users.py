"""사용자 인증과 회원 관리에 필요한 PostgreSQL Query를 제공한다."""

from typing import Any

import psycopg

from .db import get_connection


class UserNotFoundError(LookupError):
    """활성 사용자를 찾을 수 없을 때 발생한다."""


class InvalidCurrentPasswordError(ValueError):
    """현재 비밀번호가 일치하지 않을 때 발생한다."""


def find_user_id_by_email(email: str) -> int | None:
    """활성 상태와 관계없이 이메일에 대응하는 사용자 ID를 조회한다."""

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()
        return None if row is None else int(row["id"])
    finally:
        connection.close()


def create_user(email: str, password: str, name: str) -> dict[str, Any]:
    """새 사용자를 생성하고 공개 가능한 사용자 정보를 반환한다."""

    # TODO(security): 프로토타입 종료 전 password_hash 기반 저장으로 전환한다.
    sql = """
        INSERT INTO users (email, password, name)
        VALUES (%s, %s, %s)
        RETURNING id, email, name, is_active, created_at, updated_at
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, (email, password, name))
            user = cursor.fetchone()
        connection.commit()
    except psycopg.Error:
        connection.rollback()
        raise
    finally:
        connection.close()

    if user is None:
        raise UserNotFoundError
    return user


def find_active_user_by_email(email: str) -> dict[str, Any] | None:
    """로그인 검증에 필요한 활성 사용자와 비밀번호를 조회한다."""

    sql = """
        SELECT id, email, password, name, is_active, created_at, updated_at
        FROM users
        WHERE email = %s
          AND is_active = TRUE
          AND deleted_at IS NULL
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, (email,))
            return cursor.fetchone()
    finally:
        connection.close()


def find_active_user_by_id(user_id: int) -> dict[str, Any] | None:
    """비밀번호를 제외한 활성 사용자 정보를 조회한다."""

    sql = """
        SELECT id, email, name, is_active, created_at, updated_at
        FROM users
        WHERE id = %s
          AND is_active = TRUE
          AND deleted_at IS NULL
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            return cursor.fetchone()
    finally:
        connection.close()


def update_user(
    user_id: int,
    *,
    name: str | None,
    current_password: str | None,
    new_password: str | None,
) -> dict[str, Any]:
    """이름이나 비밀번호를 하나의 트랜잭션에서 수정한다."""

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            if new_password is not None:
                cursor.execute(
                    """
                    SELECT password
                    FROM users
                    WHERE id = %s
                      AND is_active = TRUE
                      AND deleted_at IS NULL
                    FOR UPDATE
                    """,
                    (user_id,),
                )
                password_row = cursor.fetchone()
                if password_row is None:
                    raise UserNotFoundError
                # TODO(security): 프로토타입 종료 전 안전한 해시 검증으로 전환한다.
                if password_row["password"] != current_password:
                    raise InvalidCurrentPasswordError

            if name is not None and new_password is not None:
                sql = """
                    UPDATE users
                    SET name = %s,
                        password = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                      AND is_active = TRUE
                      AND deleted_at IS NULL
                    RETURNING id, email, name, is_active, created_at, updated_at
                """
                parameters = (name, new_password, user_id)
            elif name is not None:
                sql = """
                    UPDATE users
                    SET name = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                      AND is_active = TRUE
                      AND deleted_at IS NULL
                    RETURNING id, email, name, is_active, created_at, updated_at
                """
                parameters = (name, user_id)
            else:
                sql = """
                    UPDATE users
                    SET password = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                      AND is_active = TRUE
                      AND deleted_at IS NULL
                    RETURNING id, email, name, is_active, created_at, updated_at
                """
                parameters = (new_password, user_id)

            cursor.execute(sql, parameters)
            user = cursor.fetchone()
            if user is None:
                raise UserNotFoundError
        connection.commit()
        return user
    except (psycopg.Error, UserNotFoundError, InvalidCurrentPasswordError):
        connection.rollback()
        raise
    finally:
        connection.close()


def soft_delete_user(user_id: int, password: str) -> None:
    """비밀번호를 확인하고 사용자를 소프트 삭제한다."""

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT password
                FROM users
                WHERE id = %s
                  AND is_active = TRUE
                  AND deleted_at IS NULL
                FOR UPDATE
                """,
                (user_id,),
            )
            user = cursor.fetchone()
            if user is None:
                raise UserNotFoundError
            # TODO(security): 프로토타입 종료 전 안전한 해시 검증으로 전환한다.
            if user["password"] != password:
                raise InvalidCurrentPasswordError

            cursor.execute(
                """
                UPDATE users
                SET is_active = FALSE,
                    deleted_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                  AND is_active = TRUE
                  AND deleted_at IS NULL
                RETURNING id
                """,
                (user_id,),
            )
            if cursor.fetchone() is None:
                raise UserNotFoundError
        connection.commit()
    except (psycopg.Error, UserNotFoundError, InvalidCurrentPasswordError):
        connection.rollback()
        raise
    finally:
        connection.close()
