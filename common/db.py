from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from config.database import SessionLocal


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    공통 DB 세션/트랜잭션 처리
    - 정상 처리 시 commit
    - 예외 발생 시 rollback
    - 마지막에 무조건 close
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()