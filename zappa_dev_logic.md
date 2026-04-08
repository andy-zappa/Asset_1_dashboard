🚀 ZAPPA Project Architecture & AI Harness (v1.1)
[AI 모델 및 관리자를 위한 필수 지침]
이 문서는 ZAPPA 금융 대시보드 프로젝트의 전체 아키텍처와 파일별 역할을 정의한 명세서입니다. AI는 본 프로젝트의 코드를 수정하거나 디버깅할 때 반드시 아래의 시스템 구조와 'AI 코딩 규칙'을 엄격하게 준수하여 답변해야 합니다.

🏗️ 1단계: 시스템 인프라 및 핵심 파이프라인
운영 환경: Oracle Cloud (Always Free ARM, 4 OCPU, 24GB RAM, LINUX 9.7)

핵심 스택: Python 3, FastAPI (API 서버), Streamlit (프론트엔드 UI), Bash (프로세스 감시)

전체 흐름:

collector.py가 주기적으로 각 거래소 API를 찔러 데이터를 수집하고 .json 파일로 저장.

api_server.py가 이 .json 파일들을 서빙.

프론트엔드(andy_zappa.py)가 API 서버를 호출하여 사용자에게 시각화.

watchdog.sh가 백그라운드에서 죽은 프로세스를 살려내는 무중단 아키텍처.

🤖 2단계: 파일별 역할 명세 (백엔드 / 일꾼 로봇)
1. watchdog.sh (감시자)
역할: 백그라운드 프로세스가 죽었는지 1분(또는 크론탭 주기)마다 감시하고 부활시키는 쉘 스크립트.

감시 대상: api_server.py, collector.py, andy_arbi_v1.py (차익거래 봇).

특징: ps -ef | grep으로 프로세스를 찾고, 죽어있으면 nohup으로 재실행하며 /home/opc/watchdog.log에 기록함.

2. api_server.py (API 게이트웨이 & 컨트롤 타워)
역할: FastAPI 기반(포트 8000). 생성된 JSON 데이터를 프론트엔드로 전달하고, 프론트엔드의 관리자(Admin) 설정 변경 명령을 수신함.

엔드포인트: /taxable, /tax_advantaged, /crypto, /get_config, /update_config.

특징: 프론트엔드에서 /update_config로 설정값을 저장하면, 즉시 데이터 동기화를 위해 개별 일꾼(andy_taxable_v1 등)의 함수를 강제 호출하여 데이터를 갱신함.

3. collector.py (무한 루프 데이터 수집기)
역할: 10초 단위로 무한 루프를 돌며 개별 수집 스크립트의 함수(generate_*_data())를 실행.

특징: try-except로 철저히 감싸져 있어, 주식 API가 에러가 나도 코인 API 수집은 정상 작동하도록 설계됨(Hanging 방지). 하루 1회 save_daily_history()를 통해 자산의 일일 평가액을 history_db.json에 기록함.

4. 수집 로봇 삼총사
andy_tax_advantaged_v1.py (절세계좌 수집):

한국투자증권(KIS) API 사용. (OAuth2 토큰 관리: kis_token.json).

DC, IRP, PENSION, ISA 계좌의 국내 자산 및 안전자산(예금 등) 평가 로직 포함.

andy_taxable_v1.py (일반계좌 수집):

KIS API 및 Yahoo Finance API 병행 사용.

미국 정규장 시간(is_us_regular_market)을 판단하여 정규장엔 KIS 실시간 시세를, 그 외 시간엔 Yahoo Finance 시세를 가져오는 정합성 로직 포함. 야후에서 실시간 환율(USDKRW)을 가져옴.

andy_crypto_v1.py (암호화폐 수집):

업비트(Upbit) API 사용.

[보안주의] API 키를 평문으로 저장하지 않고, cryptography.fernet 라이브러리를 사용해 /home/opc/zappa.key와 encrypted_keys.json을 복호화하여 사용함.

🎨 3단계: 프론트엔드 구조 (andy_zappa.py)
프레임워크: Streamlit (Layout: wide).

UI/UX 특징: Streamlit의 기본 한계를 넘기 위해 대량의 HTML/CSS, Javascript(components.html)가 주입되어 있음. Zappa 로고, 프로필 등은 Base64로 인코딩된 이미지를 사용. Plotly(Treemap, Equity Curve) 및 Echarts(도넛 차트) 활용.

인증 로직: bcrypt를 사용한 단방향 해시 암호화 적용. Oracle API 서버에서 해시값을 가져오며 통신 실패 시 st.secrets 참조. 모바일 자동 로그인을 위한 URL Token(?token=andy_zappa_pass) 적용.

주요 뷰 (메뉴):

대시보드 (Treemap, Pie Chart)

절세계좌, 일반계좌, 암호화폐 상세 뷰 (Expander 기반 리스트)

알고리즘 (Zappa Alpha) / 차익거래 (Zappa Arbi) : 현재 프론트엔드 UI 목업 및 컨트롤 패널 위주로 구현되어 있음.

Admin 패널 : 비밀번호 변경 및 각 계좌의 원금, 현금, 보유 종목(master_config.json 매핑)을 편집하고 오라클 서버로 배포(Deploy).

💾 4단계: 데이터베이스 (Data & State)
master_config.json: 사용자가 Admin 패널에서 입력한 계좌별 원금, 현금 잔고, 보유 종목의 매수단가 및 수량 등 '기준 데이터'가 저장됨.

data_taxable.json, data_tax_advantaged.json, data_crypto.json: 봇들이 실시간 시세를 반영하여 계산해 낸 '결과 데이터'.

history_db.json: 과거 수익률(1일/7일/15일/30일 전) 비교를 위해 매일의 자산 총액을 기록하는 장부.

🚨 5단계: AI 코딩 및 수정 가이드라인 (Harness Rules)
AI는 이 프로젝트와 관련된 요청을 수행할 때 다음을 반드시 지켜야 합니다.

Strict Modification (명령 수행 원칙): 기존 코드를 임의로 리팩토링하거나 구조를 뜯어고치지 마십시오. 사용자가 지시한 부분, 추가 기능, 혹은 발생한 에러의 원인 부분만 핀포인트로 정확히 수정하여 제공하십시오.

No Hallucination (추측 배제): 제공된 파일의 로직에 없는 기능(예: 아직 연동되지 않은 바이낸스 API 로직 등)을 이미 존재하는 것처럼 가정하여 코드를 짜지 마십시오. 모르는 것은 사용자에게 질문하십시오.

HTML/CSS Formatting (프론트엔드 규칙): 프론트엔드(andy_zappa.py)에 주입되는 st.markdown() 내부의 HTML/CSS 코드를 출력할 때는 무조건 좌측 탭 여백 없이 화면 좌측 끝에 딱 붙여서(들여쓰기 없이) 출력하십시오. (파이썬 문자열 인식 오류 방지용)

Code Segmentation (출력 규칙): 제공해야 할 파이썬 코드가 500줄을 넘어갈 경우, 데이터 유실 방지를 위해 무조건 500줄 단위로 끊어서 출력하고 "다음 출력을 위해 '다음'이라고 입력해 주세요"라고 대기하십시오.

Fact-Based Output (응답 태도): 단계별로 끊어서, 팩트 중심의 짧고 명확한 보고 형태로 답변을 생성하십시오.
