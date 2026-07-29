"""db.py
레이어: Repositories
역할: PostgreSQL 연결 및 공통 DB 조회·저장 Helper 함수 모음.
"""

import logging
from typing import Any

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

from ..core.config import settings


logger = logging.getLogger(__name__)
connection_parameters = {
    "host": settings.postgres_host,
    "port": settings.postgres_port,
    "dbname": settings.postgres_db,
    "user": settings.postgres_user,
    "password": settings.postgres_password.get_secret_value(),
    "row_factory": dict_row,
}


def get_connection() -> Connection[dict[str, Any]]:
    """PostgreSQL에 연결한다."""

    try:
        return psycopg.connect(**connection_parameters)
    except psycopg.Error:
        logger.exception("PostgreSQL 연결 실패")
        raise


def find_one(sql: str, parameters=None) -> dict[str, Any] | None:
    """DB에서 단일 Row를 조회한다."""

    result = None
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, parameters)
            result = cursor.fetchone()
        connection.commit()
    except psycopg.Error:
        connection.rollback()
        logger.exception("PostgreSQL 단일 Row 조회 실패")
        raise
    finally:
        connection.close()

    return result


def find_all(sql: str, parameters=None) -> list[dict[str, Any]]:
    """DB에서 여러 Row를 조회한다."""

    result = []
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, parameters)
            result = cursor.fetchall()
        connection.commit()
    except psycopg.Error:
        connection.rollback()
        logger.exception("PostgreSQL 다중 Row 조회 실패")
        raise
    finally:
        connection.close()

    return result


def save(sql: str, parameters=None) -> bool:
    """DB에 단일 변경 Query를 반영한다."""

    result = False
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, parameters)
        connection.commit()
        result = True
    except psycopg.Error:
        connection.rollback()
        logger.exception("PostgreSQL 저장 실패")
        raise
    finally:
        connection.close()

    return result
