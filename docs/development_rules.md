# 개발 규칙

## 파일명 규칙
- 소문자 + 언더바 사용
- 예: user_management.py

## 함수명 규칙
- snake_case 사용
- 예: get_menu_list, validate_user

## 테이블명 규칙
- 복수형 사용
- 예: users, roles, menus

## 컬럼명 규칙
- snake_case 사용
- 예: user_id, user_name, parent_id

## DB 규칙
- 기본 DB는 MSSQL 사용
- PK / FK를 명확히 정의
- 공통 컬럼 use_yn, created_at 기본 포함 고려

## 화면 구성 규칙
- 상단 헤더
- 좌측 메뉴
- 우측 본문
- 본문은 조회조건 / 버튼 / 그리드 / 상세 영역 순으로 확장 가능하게 설계