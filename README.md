# ILHOS_Project_DLab

내부 업무용 ERP 스타일 시스템 및 분석 도구 개발 프로젝트

## 프로젝트 목적
- 로그인 기반 업무 시스템 구축
- 권한별 메뉴 제어
- ERP 스타일 좌측 메뉴 + 우측 화면 구조 구현
- 기준정보 / 구매 / 생산 / 분석 기능 확장
- MSSQL 기반 데이터 관리
- 해외 사용자를 고려하여 화면 문구는 영어로 구성

## 1차 개발 범위
- 로그인
- 대시보드
- 메뉴 구조
- 사용자/권한 구조
- 거래처관리
- 품목관리

## 기술 스택
- Python
- Streamlit
- MSSQL
- SQLAlchemy
- pyodbc
- Pandas


## 🚀 주요 기능 (2Days)
- 업체 관리 (CRUD)
- Grid 기반 데이터 조회 (st-aggrid)
- 상태 기반 화면 제어 (session_state)
- 팝업 확인창 (st.dialog)

---

## ⚙️ 실행 방법

```bash
streamlit run app.py