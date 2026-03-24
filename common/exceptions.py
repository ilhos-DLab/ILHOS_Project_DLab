class AppError(Exception):
    """애플리케이션 공통 예외의 최상위 클래스"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    """입력값 검증 오류"""
    pass


class NotFoundError(AppError):
    """대상 데이터 없음"""
    pass


class BusinessError(AppError):
    """업무 규칙 위반"""
    pass


class DuplicateError(AppError):
    """중복 데이터 오류"""
    pass


class AuthenticationError(AppError):
    """로그인/인증 실패"""
    pass


class AuthorizationError(AppError):
    """권한 없음"""
    pass


class DatabaseError(AppError):
    """DB 처리 오류"""
    pass