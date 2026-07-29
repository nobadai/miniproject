"""FastAPI ASGI 애플리케이션 진입점이다.

공통 fastset 기반으로 생성한 애플리케이션을 외부에 제공한다.
"""

from .core.fastset import run


app = run()
