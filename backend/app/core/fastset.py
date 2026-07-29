"""FastAPI 애플리케이션 초기화 기반을 정의한다.

애플리케이션을 생성하고 Router 자동 등록과 CORS 설정을 적용한다.
"""

import importlib
import pkgutil

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .. import routers
from .config import settings


def run() -> FastAPI:
    """FastAPI 애플리케이션을 구성하고 routers 폴더의 Router를 등록한다."""

    application = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        servers=[{"url": "/", "description": "API 기본 서버"}],
    )

    # Router 파일명은 snake_case에서 kebab-case로 변환해 URL Prefix로 사용한다.
    for module_info in sorted(
        pkgutil.iter_modules(routers.__path__), key=lambda item: item.name
    ):
        if module_info.name.startswith("_") or module_info.ispkg:
            continue

        module = importlib.import_module(
            f"..routers.{module_info.name}", package=__package__
        )
        router = getattr(module, "router", None)
        if isinstance(router, APIRouter):
            prefix = f"/{module_info.name.replace('_', '-')}"
            application.include_router(router, prefix=prefix)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return application
