import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# .env 파일 로드
load_dotenv()


def _get_required_env(key: str) -> str:
    """
    필수 환경변수 조회
    값이 없으면 즉시 예외를 발생시켜 초기 설정 누락을 빠르게 확인할 수 있도록 한다.
    """
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Environment variable '{key}' is required.")
    return value


def get_database_url() -> str:
    """
    Azure SQL / MSSQL 공통 접속 URL 생성
    - 개발환경: .env 사용 가능
    - 운영환경: 시스템 환경변수 또는 secret manager 사용 가능
    """
    server = _get_required_env("DB_SERVER")
    port = os.getenv("DB_PORT", "1433")
    database = _get_required_env("DB_NAME")
    username = _get_required_env("DB_USER")
    password = _get_required_env("DB_PASSWORD")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")

    # Azure SQL 기준 권장 옵션
    odbc_connect = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server},{port};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )

    return f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc_connect)}"


DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)