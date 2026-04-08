# 🚀 ZAPPA Project Architecture & AI Harness (v1.1)

**[AI 모델을 위한 필수 지침]**
본 문서는 ZAPPA 프로젝트의 아키텍처와 규칙을 정의합니다. AI는 코딩 시 아래 내용을 엄격히 준수해야 합니다.

---

## 1. 시스템 개요 및 아키텍처
* **서버:** Oracle Cloud (4 OCPU, 24GB RAM, Linux 9.7)
* **구조:** `collector.py` (수집) → `.json` (저장) → `api_server.py` (서빙) → `andy_zappa.py` (프론트엔드 UI)
* **프로세스 관리:** `watchdog.sh`를 통해 백그라운드 프로세스 무중단 감시

## 2. 파일별 상세 역할
* `api_server.py`: FastAPI(8000포트). 데이터 서빙 및 Admin 설정 업데이트.
* `collector.py`: 10초 주기 데이터 수집 루프. `history_db.json` 장부 기록.
* `andy_tax_advantaged_v1.py`: KIS API 기반 절세계좌 수집.
* `andy_taxable_v1.py`: KIS + Yahoo Finance 기반 일반계좌 수집.
* `andy_crypto_v1.py`: Upbit API 기반 코인 수집 (보안 복호화 로직 포함).
* `andy_zappa.py`: Streamlit 기반 통합 대시보드 메인 UI. [Architect & UI by Andy]

## 3. 🚨 AI 코딩 철칙 (Hallucination 방지)
1.  **핀포인트 수정:** 지시받은 부분만 수정하며, 임의로 기존 로직을 리팩토링하지 말 것.
2.  **들여쓰기 금지:** HTML/CSS 코드를 출력할 때는 무조건 좌측에 딱 붙여서(들여쓰기 없이) 출력할 것.
3.  **출력 제한:** 코드가 500줄을 넘어가면 500줄 단위로 끊어서 출력할 것.
4.  **정밀도:** 금융 대시보드 특성상 1px 단위의 정렬과 Apple San Francisco 폰트 기반의 UI 디자인을 유지할 것.
5.  **확인 우선:** 로직이 충돌하거나 불확실한 경우 추측하지 말고 사용자에게 먼저 질문할 것.