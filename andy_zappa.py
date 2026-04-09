import streamlit as st
import streamlit.components.v1 as components
import json
import warnings
import os
import re
import time
import requests
from datetime import datetime
import urllib.parse
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit_authenticator as stauth

def get_live_data():
    url = "http://168.107.15.252:8888/data_arbi.json"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"데이터 수신 에러: {e}")
        return None
    return None

# 2. 대시보드 화면의 데이터를 실제 서버 데이터로 덮어쓰기 (JSON 구조 변경 반영)
live_data = get_live_data()
if live_data and 'items' in live_data:
    for item in live_data['items']:
        if item.get('ticker') == 'BTC':
            st.session_state.current_gap = item.get('gap')
            break

st.markdown("""
<style>
/* 모든 Primary 버튼(붉은색)을 딥파스텔 블루로 변경 */
div.stButton > button[kind="primary"] {
background-color: #7fb5e9 !important; /* 성공(Success) 메시지 톤의 연두색 */
color: white !important;
border: none;
width: 100%; /* 하단 큰 버튼처럼 가득 차게 유지 */
}
/* 마우스 올렸을 때 색상 */
div.stButton > button[kind="primary"]:hover {
background-color: #5a99d4 !important;
color: white !important;
}
</style>
""", unsafe_allow_html=True)

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="ZAPPA Asset Dashboard")

# --- 로그인 설정 시작 (비밀번호 통합 + 모바일 자동 로그인 파라미터 적용) ---
import bcrypt

# 1. Oracle 서버에서 최신 해시 암호 가져오기 시도
fetched_hashed_pw = None
try:
    res_cfg_auth = requests.get("http://168.107.15.252:8000/get_config", timeout=2)
    if res_cfg_auth.status_code == 200:
        fetched_hashed_pw = res_cfg_auth.json().get("ZAPPA_HASHED_PW")
except:
    pass

# 2. 오라클 서버 장애 시, Streamlit Secrets(비밀 금고)에서 백업 암호 가져오기
if not fetched_hashed_pw:
    try:
        fetched_hashed_pw = st.secrets["ZAPPA_HASHED_PW"]
    except:
        # 💡 [패치] 라이브러리 버전 충돌을 방지하기 위해 bcrypt로 직접 안전하게 해싱합니다.
        fetched_hashed_pw = bcrypt.hashpw('andy1234'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

credentials = {
    "usernames": {
        "andy": {
            "name": "Andy",
            "password": fetched_hashed_pw
        }
    }
}

authenticator = stauth.Authenticate(credentials, 'zappa_cookie_v2', 'signature_key', 0)

# 3. 💡 모바일 자동 로그인 (비밀 URL 토큰 감지)
is_auto_login = False
# 주소창에 ?token=andy_zappa_pass 가 있으면 무조건 통과!
if st.query_params.get("token") == "andy_zappa_pass":
    st.session_state["authentication_status"] = True
    is_auto_login = True

# 💡 [패치] 로그인 창을 가둬둘 '빈 상자' 생성
login_box = st.empty()

# 토큰이 없을 때만 빈 상자 안에 정식 로그인 창 띄우기
if not is_auto_login:
    with login_box.container():
        authenticator.login()

if st.session_state.get("authentication_status") is False:
    st.error('❌ 아이디 또는 비밀번호가 일치하지 않습니다.')
elif st.session_state.get("authentication_status") is None:
    st.warning('🔒 대시보드 접속을 위해 비밀번호를 입력해주세요.')
elif st.session_state.get("authentication_status"):
    # 💡 [핵심 패치 1] 로그인이 성공하면 겹쳐있던 로그인 상자를 강제로 폭파시켜 흔적을 지웁니다.
    login_box.empty()
   
    # 💡 [핵심 패치 2] 로그인 직후 디폴트 화면을 '총 운용자산(대시보드)'으로 확실하게 고정합니다.
    if 'current_view' not in st.session_state:
        st.session_state.current_view = '대시보드'

    # =========================================================
    # [ Part 1 ] 공통 설정 및 오리지널 CSS 복원
    # =========================================================
    css = """
<style>
[data-testid="stStatusWidget"] { display: none !important; }
html, body, .stApp, .main, [data-testid="stAppViewContainer"], .block-container { scroll-behavior: smooth !important; }
[data-testid="stSidebarUserContent"] { padding-top: 0.1rem !important; }
section[data-testid="stSidebar"] .block-container { padding-top: 0 !important; margin-top: -110px !important; gap: 0 !important; }
.sidebar-card { transition: transform 0.2s ease, box-shadow 0.2s ease; cursor: pointer; background-color: #ffffff; border-radius: 12px; padding: 12px 14px; border: 1px solid #eaeaea; margin-bottom: 10px; }
.sidebar-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.08) !important; border-color: #ccc !important; }
.sidebar-card-dark { background-color: #1a1a1a !important; color: #ffffff !important; border: none !important; }
.sidebar-card-dark:hover { box-shadow: 0 6px 12px rgba(255,255,255,0.08) !important; }
.block-container { padding-top: 0rem !important; padding-bottom: 7rem !important; }
h3 { font-size: 26px !important; font-weight: bold; margin-bottom: -10px; padding-bottom: 0px; }
.sub-title { font-size: 22px !important; font-weight: bold; margin: 12px 0 10px; }
.main-table { width: 100%; border-collapse: separate !important; border-spacing: 0; border: 1.5px solid #b5b5b5 !important; border-radius: 12px; overflow: hidden; font-size: 15px; text-align: center; margin-bottom: 10px; }
.main-table th { background-color: #f2f2f2; padding: 10px; border-bottom: 1px solid #dcdcdc !important; border-right: 1px solid #dcdcdc !important; font-weight: bold !important; vertical-align: middle; }
.main-table td { padding: 8px; border-bottom: 1px solid #dcdcdc !important; border-right: 1px solid #dcdcdc !important; vertical-align: middle; }
.main-table tr th:last-child, .main-table tr td:last-child { border-right: none !important; }
.main-table tr:last-child th, .main-table tr:last-child td { border-bottom: none !important; }
.main-table th.th-eval { border-right: none !important; }
.main-table th.th-blank { border-bottom: none !important; border-right: none !important; padding: 0 !important; }
.main-table th.th-week { border-left: 1px solid #dcdcdc !important; border-top: 1px solid #dcdcdc !important; font-size: 13.5px; }
.sum-row td { background-color: #fff9e6; font-weight: bold !important; }
.red { color: #D32F2F !important; }
.blue { color: #1976D2 !important; }
.insight-container { display: flex; gap: 20px; align-items: stretch; margin-bottom: 20px; }
.insight-left { flex: 0 0 46%; display: flex; flex-direction: column; }
.insight-right { flex: 1; display: flex; flex-direction: column; }
.card-main { background-color: #fffdf2; border: 2px solid #e8dbad; border-radius: 18px; padding: 18px 22px 15px 22px; position: relative; box-shadow: 0 2px 6px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; }
.card-inner { background-color: #ffffff; border: 1.5px solid #dcdcdc; border-radius: 10px; text-align: right; box-shadow: 0 2px 8px rgba(0,0,0,0.04); transition: all 0.3s ease; cursor: default; }
.card-inner:hover { background-color: #f8f9fa !important; border-color: #bbb !important; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.grid-2x2 { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 15px; height: 100%; }
.card-sub { background: #fff; border: 1.5px solid #dcdcdc; border-radius: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.02); display: flex; flex-direction: column; padding: 10px 15px; transition: background-color 0.2s, border-color 0.2s, transform 0.2s, box-shadow 0.2s; cursor: pointer; }
.card-sub:hover { background-color: #f2f2f2 !important; border-color: #ccc !important; transform: translateY(-1px); box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
.insight-bottom-box { background: #fff; border: 1.5px solid #dcdcdc; border-radius: 18px; padding: 25px; box-shadow: 0 1px 4px rgba(0,0,0,0.02); font-size: 15.5px; line-height: 1.8; color: #333; margin-top: 5px; margin-bottom: 25px; }
.summary-text { font-size: 16px !important; font-weight: bold !important; color: #333; margin-bottom: 10px; }
.summary-val { font-size: 20px !important; }
div[role="radiogroup"] { display: grid !important; grid-template-columns: 1fr 1fr !important; gap: 8px !important; margin-bottom: 0px !important; }
div[role="radiogroup"] label { font-size: 14.5px !important; margin-bottom: 0px !important; }
div[data-testid="stRadio"] { display: none !important; }
div[data-baseweb="select"] { min-height: 34px !important; font-size: 13.5px !important; }
div[data-baseweb="select"] > div { padding: 0px 10px !important; border-radius: 6px !important; min-height: 34px !important; }
div[data-baseweb="select"] span { font-size: 13.5px !important; line-height: 34px !important; }
div[data-testid="stSelectbox"] label { display: none !important; }

/* 🎯 플로팅 배너 CSS 수정 */
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu), div[data-testid="column"]:has(span#zappa-floating-menu) {
    position: fixed !important; top: 15px !important; right: 20px !important; bottom: auto !important; left: auto !important;
    transform: none !important; width: max-content !important; min-width: 0 !important;
    background: rgba(255, 255, 255, 0.95) !important; padding: 6px 12px !important; border-radius: 8px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important; border: 1px solid #e5e7eb !important; z-index: 999999 !important;
    display: flex !important; flex-wrap: nowrap !important; align-items: center !important; justify-content: center !important;
    gap: 0px !important; backdrop-filter: blur(4px);
}
div.element-container:has(span#zappa-floating-menu) { display: none !important; }
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) > div { min-width: 0 !important; width: auto !important; padding: 0 !important; margin: 0 !important; flex: 0 0 auto !important; border-right: none !important; }
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button { margin: 0 !important; padding: 0 3px !important; width: auto !important; background: transparent !important; border: none !important; border-radius: 0 !important; height: 24px !important; min-height: 24px !important; color: #9ca3af !important; font-size: 13.5px !important; font-weight: normal !important; white-space: nowrap !important; box-shadow: none !important; display: flex !important; align-items: center !important; justify-content: center !important; transition: all 0.2s ease !important; }
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button p { color: inherit !important; font-size: 13.5px !important; font-weight: inherit !important; margin: 0 !important; padding: 0 !important; line-height: 1 !important; text-align: center !important; white-space: nowrap !important; }
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button:hover { color: #111111 !important; background-color: #e6f2ff !important; border-radius: 4px !important; }
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button[kind="primary"] { background: transparent !important; border: none !important; color: #111111 !important; font-weight: bold !important; }

/* 💡 [패치] Admin과 Log-out 버튼 수직/수평 정렬 수정 */
/* 1. 투명 앵커 숨기기 */
div.element-container:has(#admin-btn-anchor),
div.element-container:has(#logout-btn-anchor) { display: none !important; }

/* 2. 두 버튼의 컨테이너를 세로로 나란히 배치 (block) 및 전체 스택 위로 당기기 */
div.element-container:has(#admin-btn-anchor) + div.element-container {
    display: block !important;
    width: 100% !important;
    margin-bottom: 6px !important; /* 버튼 사이의 위아래 간격 */
    margin-top: 15px !important; /* 이 부분의 마진을 음수로 주어 버튼 전체를 위로 올립니다. */
}
div.element-container:has(#logout-btn-anchor) + div.element-container {
    display: block !important;
    width: 100% !important;
    margin-bottom: 6px !important;
    margin-top: -14px !important;
}

/* 3. 공통 버튼 디자인 및 좌측 정렬 (마진 삭제하여 박스에 맞춤) */
div.element-container:has(#admin-btn-anchor) + div.element-container button,
div.element-container:has(#logout-btn-anchor) + div.element-container button {
    background: #f4f5f7 !important;
    border: 1px solid #dcdcdc !important;
    border-radius: 6px !important;
    padding: 4px 12px !important;
    min-height: 26px !important;
    height: 28px !important;
    width: max-content !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin-top: 0px !important;
    transition: all 0.2s ease;
}

div.element-container:has(#admin-btn-anchor) + div.element-container button p,
div.element-container:has(#logout-btn-anchor) + div.element-container button p {
    color: #444444 !important; font-size: 12.5px !important; font-weight: 800 !important; margin: 0 !important; line-height: 1 !important;
}

div.element-container:has(#admin-btn-anchor) + div.element-container button:hover,
div.element-container:has(#logout-btn-anchor) + div.element-container button:hover {
    background: #e9ecef !important; border-color: #bbbbbb !important; transform: none !important;
}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)

    # 💡 [패치 1] 사이드바 클릭 연동 JS (DOM 변화 대응을 위해 클릭 시점에 라디오 버튼 동적 탐색)
    components.html("""
<script>
const parentDoc = window.parent.document;
parentDoc.querySelectorAll('a[href^="#"]').forEach(anchor => {
anchor.addEventListener('click', function (e) {
e.preventDefault();
const targetId = this.getAttribute('href').substring(1);
const targetElement = parentDoc.getElementById(targetId);
if (targetElement) { targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
});
});

function bindSidebarClicks() {
const bindClick = (cardId, routeName) => {
const card = parentDoc.getElementById(cardId);
if (card && !card.hasAttribute('data-binded')) {
card.setAttribute('data-binded', 'true');
card.addEventListener('click', () => {
// 👇 핵심: 찰나의 클릭 순간에 최신 메뉴 버튼을 다시 찾도록 안으로 넣었습니다.
const currentLabels = Array.from(parentDoc.querySelectorAll('div[role="radiogroup"] label'));
const target = currentLabels.find(l => l.innerText.includes(routeName));
if(target) target.click();
});
}
};
bindClick('card-total', '대시보드');
bindClick('card-pension', '절세계좌');
bindClick('card-general', '일반계좌');
bindClick('card-crypto', '암호화폐');
bindClick('card-quant', '알고리즘');
bindClick('card-arbi', '차익거래');
}
setInterval(bindSidebarClicks, 300);
</script>
""", height=0)

    GUARANTEED_LOGOS = {
        "알파벳 A": "google.com", "팔란티어 테크": "palantir.com", "TSMC(ADR)": "tsmc.com",
        "테슬라": "tesla.com", "마이크로소프트": "microsoft.com", "애플": "apple.com",
        "엔비디아": "nvidia.com", "아이온큐": "ionq.com", "리케티 컴퓨팅": "rigetti.com",
        "디 웨이브 퀀텀": "dwavesys.com", "아이렌": "iren.com", "피그마": "figma.com",
        "삼성전자": "samsung.com", "현대차": "hyundai.com", "CJ": "cj.net",
        "두산에너빌리티": "doosanenerbility.com", "한화오션": "hanwhaocean.com",
        "한국항공우주": "koreaaero.com", "POSCO홀딩스": "posco.co.kr", "셀트리온": "celltrion.com"
    }

    def get_logo_html(nm):
        if not nm or nm in ["예수금", "[ 합  계 ]", "현금성자산", "현금성자산(예수금)"]: return ""
   
        nm_u = str(nm).upper()
        if any(x in nm_u for x in ['KODEX', 'TIGER', 'PLUS', 'RISE', 'ETF', 'ACE', '미국나스닥', '미국S&P']):
            clean_nm = re.sub(r'[^가-힣a-zA-Z0-9]', '', str(nm))
            fc = clean_nm[:1] if clean_nm else "E"
            colors = ["#e6f2ff", "#e6ffe6", "#ffe6e6", "#fff0e6", "#f0e6ff", "#ffe6f9", "#e6ffff", "#f5ffe6"]
            text_colors = ["#0066cc", "#006600", "#cc0000", "#cc5200", "#5200cc", "#cc00a3", "#00cccc", "#669900"]
            idx = sum(ord(c) for c in fc) % len(colors)
            return f"<span style='display:inline-block; width:18px; height:18px; border-radius:50%; background-color:{colors[idx]}; color:{text_colors[idx]}; text-align:center; line-height:18px; font-size:10px; font-weight:900; margin-right:8px; vertical-align:middle; box-shadow: 0 1px 2px rgba(0,0,0,0.1);'>{fc}</span>"

        domain = GUARANTEED_LOGOS.get(nm)
        if domain:
            return f"<img src='https://www.google.com/s2/favicons?domain={domain}&sz=64' style='width:18px; height:18px; border-radius:50%; vertical-align:middle; margin-right:8px; margin-bottom:2px; box-shadow: 0 1px 2px rgba(0,0,0,0.15); background-color:white; object-fit:contain;'>"
        else:
            clean_nm = re.sub(r'[^가-힣a-zA-Z0-9]', '', str(nm))
            short_str = clean_nm[:1] if clean_nm else "Z"
            colors = ["#e6f2ff", "#e6ffe6", "#ffe6e6", "#fff0e6", "#f0e6ff", "#ffe6f9", "#e6ffff", "#f5ffe6"]
            text_colors = ["#0066cc", "#006600", "#cc0000", "#cc5200", "#5200cc", "#cc00a3", "#00cccc", "#669900"]
            idx = sum(ord(c) for c in short_str) % len(colors)
            return f"<span style='display:inline-block; width:18px; height:18px; border-radius:50%; background-color:{colors[idx]}; color:{text_colors[idx]}; text-align:center; line-height:18px; font-size:10px; font-weight:900; margin-right:8px; vertical-align:middle; box-shadow: 0 1px 2px rgba(0,0,0,0.1);'>{short_str}</span>"

    # Session States
    if 'sort_mode' not in st.session_state: st.session_state.sort_mode = 'init'
    if 'gen_sort_mode' not in st.session_state: st.session_state.gen_sort_mode = 'init'
    if 'show_code' not in st.session_state: st.session_state.show_code = False
    if 'show_change_rate' not in st.session_state: st.session_state.show_change_rate = False
    if 'gen_show_change_rate' not in st.session_state: st.session_state.gen_show_change_rate = False
    if 'current_view' not in st.session_state: st.session_state.current_view = '대시보드'
    if 'usa_show_krw' not in st.session_state: st.session_state.usa_show_krw = True
    if 'usa_show_usd' not in st.session_state: st.session_state.usa_show_usd = False
    # 👇👇👇 [여기서부터 새로 추가된 부분] 👇👇👇
    if 'open_aum' not in st.session_state: st.session_state.open_aum = False
    if 'open_tax' not in st.session_state: st.session_state.open_tax = False
    if 'open_gen' not in st.session_state: st.session_state.open_gen = False
    if 'open_crypto' not in st.session_state: st.session_state.open_crypto = False
    if 'last_sync_time' not in st.session_state: st.session_state.last_sync_time = "업데이트 필요"

    def toggle_usa_krw():
        st.session_state.usa_show_krw = not st.session_state.usa_show_krw
        if not st.session_state.usa_show_krw and not st.session_state.usa_show_usd: st.session_state.usa_show_usd = True

    def toggle_usa_usd():
        st.session_state.usa_show_usd = not st.session_state.usa_show_usd
        if not st.session_state.usa_show_krw and not st.session_state.usa_show_usd: st.session_state.usa_show_krw = True

    def on_menu_change():
        if st.session_state.get('menu_sel') is not None:
            st.session_state.current_view = st.session_state.menu_sel

    def to_kst(time_str):
        if not time_str or time_str in ['업데이트 필요', '자체 집계 모드']:
            return str(time_str)
        try:
            t_str = str(time_str).replace('년 ', '-').replace('월 ', '-').replace('일', '')
            t_str = re.sub(r'\(.\)\s*/\s*', ' ', t_str)
            dt = pd.to_datetime(t_str)
            if dt.tzinfo is not None:
                dt = dt.tz_localize(None)
            wd = {0:'월', 1:'화', 2:'수', 3:'목', 4:'금', 5:'토', 6:'일'}[dt.weekday()]
            return dt.strftime(f"%m/%d({wd}), %H:%M:%S")
        except:
            return str(time_str)

    def safe_float(val):
        try:
            if val in [None, "", "-", "None"]: return 0.0
            if isinstance(val, str):
                val = val.replace(",", "").strip()
                if val == "-": return 0.0
            return float(val)
        except: return 0.0

    def fmt(v, sign=False, decimal=0):
        if v == '-': return '-'
        try:
            f_val = float(v)
            val_str = f"{f_val:,.{decimal}f}" if decimal > 0 else f"{int(round(f_val)):,}"
            return f"+{val_str}" if sign and f_val > 0 else val_str
        except: return str(v)

    def fmt_p(v):
        if v == '-' or v is None: return '-'
        try:
            val = float(v)
            # 💡 삼각형 크기 110% (1.1em) 적용
            tri = "<span style='font-size:1.1em; vertical-align:baseline;'>▲</span>" if val > 0 else "<span style='font-size:1.1em; vertical-align:baseline;'>▼</span>"
            return f"{tri} {abs(val):.2f}%" if val != 0 else "0.00%"
        except: return str(v)

    def fmt_p1(v):
        if v == '-' or v is None: return '-'
        try:
            val = float(v)
            abs_val = abs(val)
            # 💡 삼각형 크기 110% (1.1em) 적용
            tri = "<span style='font-size:1.1em; vertical-align:baseline;'>▲</span>" if val > 0 else "<span style='font-size:1.1em; vertical-align:baseline;'>▼</span>"
            if abs_val < 1.0 and abs_val != 0.0: return f"{tri} {abs_val:.2f}%"
            else: return f"{tri} {abs_val:.1f}%" if val != 0 else "0.0%"
        except: return str(v)

    def col(v):
        try: return "red" if float(v) > 0 else ("blue" if float(v) < 0 else "gray")
        except: return ""

    def short_name(nm):
        return str(nm)

    @st.cache_data(ttl=None)
    def fetch_hybrid_data():
        p_data, g_data = {}, {}
        is_online = False
        ts = int(time.time())
   
        try:
            r_p = requests.get(f"http://168.107.15.252:8000/tax_advantaged?t={ts}", timeout=5)
            r_g = requests.get(f"http://168.107.15.252:8000/taxable?t={ts}", timeout=5)
       
            if r_p.status_code == 200:
                temp_p = r_p.json()
                if isinstance(temp_p, dict) and "error" not in temp_p:
                    p_data = temp_p
                    is_online = True
                    with open('data_tax_advantaged.json', 'w', encoding='utf-8') as f:
                        json.dump(p_data, f, ensure_ascii=False, indent=4)
               
            if r_g.status_code == 200:
                temp_g = r_g.json()
                if isinstance(temp_g, dict) and "error" not in temp_g:
                    g_data = temp_g
                    with open('data_taxable.json', 'w', encoding='utf-8') as f:
                        json.dump(g_data, f, ensure_ascii=False, indent=4)
        except: pass
   
        if not p_data:
            try:
                with open('data_tax_advantaged.json', 'r', encoding='utf-8') as f: p_data = json.load(f)
            except: pass
           
        if not g_data:
            try:
                with open('data_taxable.json', 'r', encoding='utf-8') as f: g_data = json.load(f)
            except: pass
           
        return p_data, g_data, is_online

    data, g_data, is_oracle_online = fetch_hybrid_data()

    def normalize_insight(raw_data):
        if not isinstance(raw_data, dict): return {}
        insight = raw_data.get("_total", raw_data.get("_insight", {}))
   
        if isinstance(insight, dict) and safe_float(insight.get('총 자산', insight.get('총자산', 0))) > 0:
            return {
                '총자산': safe_float(insight.get('총 자산', insight.get('총자산', 0))),
                '총수익': safe_float(insight.get('총 수익', insight.get('총수익', 0))),
                '수익률(%)': safe_float(insight.get('수익률(%)', insight.get('수익률', 0))),
                '원금합': safe_float(insight.get('원금합', insight.get('투자원금', 0))),
                '조회시간': insight.get('조회시간', '업데이트 필요')
            }
        calc_asset, calc_profit, calc_orig = 0, 0, 0
        for k in ['DC', 'IRP', 'PENSION', 'ISA']:
            if k in raw_data and isinstance(raw_data[k], dict):
                acc = raw_data[k]
                calc_asset += safe_float(acc.get('총 자산', acc.get('총자산', 0)))
                calc_profit += safe_float(acc.get('평가손익', acc.get('총 수익', acc.get('총수익', 0))))
                calc_orig += safe_float(acc.get('원금', 0))
           
        calc_rate = (calc_profit / calc_orig * 100) if calc_orig > 0 else 0
        return {'총자산': calc_asset, '총수익': calc_profit, '수익률(%)': calc_rate, '원금합': calc_orig, '조회시간': '실시간 동기화'}

    tot = normalize_insight(data)

    @st.cache_data(ttl=None)
    def get_crypto_data():
        ts = int(time.time())
        url = f"http://168.107.15.252:8000/crypto?t={ts}"
        crypto_d = None
   
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                crypto_d = res.json()
                if isinstance(crypto_d, dict) and "error" not in crypto_d:
                    with open('data_crypto.json', 'w', encoding='utf-8') as f:
                        json.dump(crypto_d, f, ensure_ascii=False, indent=4)
                else:
                    crypto_d = None
        except: pass
       
        if not crypto_d:
            try:
                with open('data_crypto.json', 'r', encoding='utf-8') as f:
                    crypto_d = json.load(f)
            except: pass

        if isinstance(crypto_d, dict):
            ta = safe_float(crypto_d.get('total_asset', 0))
            coins = crypto_d.get('coins', [])
            btc_pct = eth_pct = trx_pct = 0
       
            if ta > 0 and isinstance(coins, list):
                for c in coins:
                    if isinstance(c, dict):
                        if c.get('ticker') == 'BTC': btc_pct = (safe_float(c.get('eval', 0)) / ta) * 100
                        elif c.get('ticker') == 'ETH': eth_pct = (safe_float(c.get('eval', 0)) / ta) * 100
                        elif c.get('ticker') == 'TRX': trx_pct = (safe_float(c.get('eval', 0)) / ta) * 100
       
            crypto_d['btc_pct'] = btc_pct
            crypto_d['eth_pct'] = eth_pct
            crypto_d['trx_pct'] = trx_pct
            return crypto_d
       
        return None

    crypto_data = get_crypto_data()

    p_asset_all = tot.get('총자산', 0)
    p_profit_all = tot.get('총수익', 0)
    p_rate_all = tot.get('수익률(%)', 0)

    p_cash_tot, p_ovs_tot, p_dom_tot = 0, 0, 0
    if isinstance(data, dict):
        for k in ['DC', 'IRP', 'PENSION', 'ISA']:
            if k in data and isinstance(data[k], dict):
                details = data[k].get('상세', [])
                if isinstance(details, list):
                    for item in details:
                        if isinstance(item, dict):
                            if item.get('종목명') == '[ 합  계 ]': continue
                            val = safe_float(item.get('총 자산', item.get('총자산', 0)))
                            nm = str(item.get('종목명', '')).upper()
                            if '현금' in nm or 'MMF' in nm: p_cash_tot += val
                            elif any(kw in nm for kw in ['미국', 'S&P', '나스닥', '필라델피아', '다우지수']): p_ovs_tot += val
                            else: p_dom_tot += val
    p_dom_pct = (p_dom_tot / p_asset_all * 100) if p_asset_all > 0 else 0
    p_ovs_pct = (p_ovs_tot / p_asset_all * 100) if p_asset_all > 0 else 0

    GEN_ACC_ORDER_Q = ['DOM1', 'DOM2', 'USA1', 'USA2']
    g_principals_q = {"DOM1": 110963075, "DOM2": 5208948, "USA1": 257915999, "USA2": 7457930}
    g_orig_all = sum(g_principals_q.values())

    g_asset_all = 0
    g_profit_all = 0
    if isinstance(g_data, dict):
        for k in GEN_ACC_ORDER_Q:
            if k in g_data and isinstance(g_data[k], dict):
                g_asset_all += safe_float(g_data[k].get("총자산_KRW", 0))
                g_profit_all += safe_float(g_data[k].get("총수익_KRW", 0))
    g_rate_all = (g_profit_all / g_orig_all * 100) if g_orig_all > 0 else 0

    g_cash_tot, g_ovs_tot, g_dom_tot = 0, 0, 0
    if isinstance(g_data, dict):
        for k in GEN_ACC_ORDER_Q:
            if k in g_data and isinstance(g_data[k], dict):
                is_usa = 'USA' in k
                fx = safe_float(g_data.get('환율', 1443.1)) if is_usa else 1
                details = g_data[k].get('상세', [])
                if isinstance(details, list):
                    for item in details:
                        if isinstance(item, dict):
                            if item.get('종목명') == '[ 합  계 ]': continue
                            val_krw = safe_float(item.get('총자산', 0)) * fx
                            nm = str(item.get('종목명', '')).upper()
                            if nm == '예수금' or '현금' in nm: g_cash_tot += val_krw
                            elif is_usa: g_ovs_tot += val_krw
                            else: g_dom_tot += val_krw
    g_dom_pct = (g_dom_tot / g_asset_all * 100) if g_asset_all > 0 else 0
    g_ovs_pct = (g_ovs_tot / g_asset_all * 100) if g_asset_all > 0 else 0

    c_tot_sum = crypto_data.get('total_asset', 0) if isinstance(crypto_data, dict) else 0
    c_prof_sum = crypto_data.get('total_profit', 0) if isinstance(crypto_data, dict) else 0
    c_buy_sum = c_tot_sum - c_prof_sum
    c_rate_sum = (c_prof_sum / c_buy_sum * 100) if c_buy_sum > 0 else 0

    total_asset = p_asset_all + g_asset_all + c_tot_sum
    total_profit = p_profit_all + g_profit_all + c_prof_sum
    total_orig = tot.get('원금합', 1) + g_orig_all
    total_rate = (total_profit / total_orig * 100) if total_orig > 0 else 0

    import base64
    import os
    import streamlit as st

    with st.sidebar:
        def get_image_base64(image_name):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            abs_path = os.path.join(base_dir, image_name)
       
            if os.path.exists(abs_path):
                with open(abs_path, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode()
            return ""
   
        robot_b64 = get_image_base64("robot.png")
        if robot_b64:
            robot_img_src = f"data:image/png;base64,{robot_b64}"
        else:
            robot_img_src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

        # 💡 [패치 추가] sealogo1, sealogo2 이미지 Base64 변환
        sea1_b64 = get_image_base64("sealogo1.gif")
        sea2_b64 = get_image_base64("sealogo2.gif")
        sea_src1 = f"data:image/gif;base64,{sea1_b64}" if sea1_b64 else ""
        sea_src2 = f"data:image/gif;base64,{sea2_b64}" if sea2_b64 else ""

        # 💡 [Oracle 시스템 헤더 정밀 패치]
        # 팩트 반영: CHUNCHEON / LINUX 9.7
        # 디자인: 로고 상단 밀착(-20px), 하단 문구와 이격(+30px) 확보
        logo_src = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Oracle_logo.svg/200px-Oracle_logo.svg.png"
        short_p = "<span style='font-size: 10px; vertical-align: 1px; color: #111111; opacity: 0.3; margin: 0 4px;'>|</span>"
       
        status_box_style = "background-color: #1f293a; padding: 4px 12px 4px 8px; border-radius: 8px; display: flex; flex-direction: column; gap: 0px;"
        off_light_style = "filter: grayscale(100%); opacity: 0.35; font-size:12px; margin-right:5px;"
        inactive_text_color = "#555555"

        if is_oracle_online:
            status_indicator = f"<div style='{status_box_style}'><div style='display:flex; align-items:center;'><span style='font-size:12px; margin-right:5px;'>🟢</span><span style='font-size:13.5px; font-weight:700; color:#00c853; letter-spacing:-0.5px;'>LIVE SYNC</span></div><div style='display:flex; align-items:center;'><span style='{off_light_style}'>🔴</span><span style='font-size:13.5px; font-weight:400; color:{inactive_text_color}; letter-spacing:-0.5px;'>OFF LINE</span></div></div>"
        else:
            status_indicator = f"<div style='{status_box_style}'><div style='display:flex; align-items:center;'><span style='{off_light_style}'>🟢</span><span style='font-size:13.5px; font-weight:400; color:{inactive_text_color}; letter-spacing:-0.5px;'>LIVE SYNC</span></div><div style='display:flex; align-items:center;'><span style='font-size:12px; margin-right:5px;'>🔴</span><span style='font-size:13.5px; font-weight:400; color:#ff5252; letter-spacing:-0.5px;'>OFF LINE</span></div></div>"

        # 💡 [Oracle 시스템 헤더 최종 패치 - 하단 영역 바싹 밀착 버전]
        status_html = f"""
<style>
.seal-hover-box {{
position: absolute;
top: -64px;
left: 12px;
width: 75px;
height: 75px;
z-index: 10;
background-image: url('{sea_src1}');
background-size: contain;
background-repeat: no-repeat;
background-position: center bottom;
transition: background-image 0.2s ease-in-out;
cursor: pointer;
}}
.seal-hover-box:hover {{
background-image: url('{sea_src2}');
}}
</style>
<div style='position: relative; margin-top: -15px;'>
<div class='seal-hover-box'></div>
<div style='border: 1px solid #dddddd; border-radius: 15px; padding: 15px 15px 8px 15px; background-color: #ffffff; margin-bottom: 2px; position: relative; z-index: 1;'>
<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 3px;'>

<div style='position: relative; width: 90px; margin-top: -22px;'>
<img src="{logo_src}" width="95" style="display: block;">
<div style='position: absolute; right: 0px; bottom: -28px; font-size: 8px; color: #999; font-weight: 500; letter-spacing: 0.5px; line-height: 1.3; text-align: right; white-space: nowrap;'>
4 OCPU, 24GB RAM<br>47GB SSD, LINUX 9.7
</div>
</div>
{status_indicator}

</div>
<div style='text-align:center; margin-top: 6px; margin-bottom: 6px;'>
<div style='font-size:13px; font-weight:400; color:#888;'>오라클 서버에서 실시간 DATA 집계</div>
</div>
<hr style='margin: 2px 0; border: 0; border-top: 1px solid #eeeeee;'>
<div style='text-align:center; margin-top: 4px; margin-bottom: 4px;'>
<div style='font-size:12.5px; font-weight:600; color:#444;'>KIS{short_p}UPbit{short_p}Binance{short_p}Y! Finance</div>
</div>
</div>
</div>
"""
        st.markdown(status_html, unsafe_allow_html=True)

        # 💡 [패치] 토스트 알림 및 진짜 시계 연동
        st.markdown("<div class='hidden-update-marker'></div>", unsafe_allow_html=True)
        if st.button("TRIGGER_UPDATE_BACKEND"):
            st.toast("📡 오라클 서버에 접속 중입니다...", icon="⏳")
            fetch_hybrid_data.clear()
            get_crypto_data.clear()
            p_tmp, g_tmp, is_ok = fetch_hybrid_data()
            if is_ok:
                # 성공 시에만 시계 갱신
                import pytz
                now_seoul = datetime.now(pytz.timezone('Asia/Seoul'))
                dw_str = ["월", "화", "수", "목", "금", "토", "일"][now_seoul.weekday()]
                st.session_state.last_sync_time = now_seoul.strftime(f"[ %y/%m/%d({dw_str}), %H:%M:%S ]")
                st.toast("✅ 데이터 동기화가 완료되었습니다!", icon="✨")
            else:
                st.toast("⚠️ 서버 연결 실패 (이전 데이터를 유지합니다)", icon="🚨")
            st.rerun()

        components.html("""
<script>
const parent = window.parent.document;
const interval = setInterval(() => {
    const unifiedBtn = parent.getElementById('unified-update-btn');
    if (unifiedBtn && !unifiedBtn.hasAttribute('data-binded')) {
        unifiedBtn.setAttribute('data-binded', 'true');
        unifiedBtn.addEventListener('mouseenter', () => { unifiedBtn.style.color = '#333333'; });
        unifiedBtn.addEventListener('mouseleave', () => { unifiedBtn.style.color = '#111111'; });
        unifiedBtn.addEventListener('click', () => {
            const btns = Array.from(parent.querySelectorAll('button p'));
            const target = btns.find(el => el.innerText.includes('TRIGGER_UPDATE_BACKEND'));
            if (target) target.closest('button').click();
        });
        clearInterval(interval);
    }
}, 500);
</script>
""", height=0)

        st.markdown('<style>div.element-container:has(div[role="radiogroup"]) { margin-top: -55px !important; position: relative; z-index: 50; }</style>', unsafe_allow_html=True)

        # 💡 [패치 1] Zappa Arbi 라디오 메뉴 추가 완료
        menu_options = ["대시보드", "절세계좌", "일반계좌", "암호화폐", "알고리즘", "차익거래"]
        def format_menu(option):
            return "AI 알고리즘" if option == "알고리즘" else option
        st.radio("Menu", menu_options, format_func=format_menu, label_visibility="collapsed", key="menu_sel", on_change=on_menu_change)

        c_btc = crypto_data.get('btc_pct', 0) if isinstance(crypto_data, dict) else 0
        c_eth = crypto_data.get('eth_pct', 0) if isinstance(crypto_data, dict) else 0
       
        c_alts = 0
        if isinstance(crypto_data, dict):
            ta = safe_float(crypto_data.get('total_asset', 0))
            coins = crypto_data.get('coins', [])
            alt_sum = 0
            if ta > 0 and isinstance(coins, list):
                for c in coins:
                    if isinstance(c, dict) and c.get('ticker') not in ['BTC', 'ETH', 'KRW']:
                        alt_sum += safe_float(c.get('eval', 0))
                c_alts = (alt_sum / ta) * 100

        r_btc = int(round(c_btc))
        r_eth = int(round(c_eth))
        r_alts = int(round(c_alts))

        c_tot_asset = safe_float(crypto_data.get('total_asset', 0)) if isinstance(crypto_data, dict) else 0
        c_tot_krw = safe_float(crypto_data.get('total_krw', 0)) if isinstance(crypto_data, dict) else 0
        c_tot_buy = safe_float(crypto_data.get('total_buy', 0)) if isinstance(crypto_data, dict) else 0
       
        c_eval_pure = c_tot_asset - c_tot_krw
        c_buy_pure = c_tot_buy - c_tot_krw
        c_prof_pure = c_eval_pure - c_buy_pure
        c_rate_sum_actual = (c_prof_pure / c_buy_pure * 100) if c_buy_pure > 0 else 0

        try:
            res_cfg_side = requests.get("http://168.107.15.252:8000/get_config", timeout=2)
            cfg_data_side = res_cfg_side.json() if res_cfg_side.status_code == 200 else {}
        except:
            cfg_data_side = {}
           
        p_principal_tot = sum(safe_float(cfg_data_side.get(f"{k}_PRINCIPAL", 0)) for k in ['DC', 'IRP', 'PENSION', 'ISA'])
        p_rate_invested = (p_profit_all / p_principal_tot * 100) if p_principal_tot > 0 else 0

        from datetime import datetime, timedelta, timezone
        now_kst = datetime.now(timezone(timedelta(hours=9)))
        wd_list = ['월', '화', '수', '목', '금', '토', '일']
        date_part_short = now_kst.strftime("%y/%m/%d")
        day_str = wd_list[now_kst.weekday()]
        time_part = now_kst.strftime("%H:%M:%S")

        st.markdown("""
<style>
div.element-container:has(.hidden-update-marker) { display: none !important; }
div.element-container:has(.hidden-update-marker) + div.element-container { display: none !important; }
@keyframes spin { 100% { transform: rotate(360deg); } }
.spin-globe { display: inline-block; animation: spin 5s linear infinite; margin-right: 3px; font-size: 14px; }
</style>
""", unsafe_allow_html=True)
       
        import pytz
        now_seoul = datetime.now(pytz.timezone('Asia/Seoul'))
        d_str = now_seoul.strftime("%y/%m/%d")
        t_str = now_seoul.strftime("%H:%M:%S")
        days_kr = ["월", "화", "수", "목", "금", "토", "일"]
        dw_str = days_kr[now_seoul.weekday()]

        # 💡 [자동 시간 기록] 첫 로딩 시 '업데이트 필요' 문구가 있다면 즉시 현재 시간으로 교체합니다.
        if st.session_state.get('last_sync_time', '업데이트 필요') == '업데이트 필요':
            st.session_state.last_sync_time = now_seoul.strftime(f"[ %y/%m/%d({dw_str}), %H:%M:%S ]")

        try:
            r_b64 = get_image_base64("robot.png")
            r_src = f"data:image/png;base64,{r_b64}" if r_b64 else ""
        except:
            r_src = ""

        # 💡 [로봇 영역 및 시간 정렬]
        st.sidebar.markdown(f"""
<div style='margin-top: 20px;'>
    <div style='display: flex; justify-content: space-between; align-items: flex-end; padding: 0 10px; margin-bottom: 0px;'>
        <img src='{r_src}' style='width: 63px; display: block; margin-bottom: 0px; margin-left: 2px;'>
        <div id='unified-update-btn' style='text-align: right; font-family: sans-serif; padding-bottom: 0px; margin-bottom: 2px; cursor: pointer;' title='클릭하여 데이터 최신화'>
            <div style='font-size: 11px; color: #111111; font-weight: 400; letter-spacing: 0.5px; margin-bottom: 2px; position: relative; top: 2px; padding-right: 7px;'>🔄 UPDATE</div>
            <div style='font-size: 11px; font-weight: 400; color: #111111; letter-spacing: 0.1px; padding-right: 7px;'>{st.session_state.last_sync_time}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

        # =========================================================
        # 💡 [최종] 계좌 및 종목 수 자동 합산 로직
        # =========================================================
        # 1. 절세계좌 카운트
        p_acc_cnt, p_item_cnt = 0, 0
        if isinstance(data, dict):
            for k in ['DC', 'IRP', 'PENSION', 'ISA']:
                if k in data and isinstance(data[k], dict):
                    p_acc_cnt += 1
                    for item in data[k].get('상세', []):
                        nm = str(item.get('종목명', ''))
                        if nm and nm not in ["[ 합  계 ]", "예수금", "현금성자산", "현금성자산(예수금)"] and "현금" not in nm:
                            p_item_cnt += 1

        # 2. 일반계좌 카운트
        g_acc_cnt, g_item_cnt = 0, 0
        if isinstance(g_data, dict):
            for k in ['DOM1', 'DOM2', 'USA1', 'USA2']:
                if k in g_data and isinstance(g_data[k], dict):
                    g_acc_cnt += 1
                    for item in g_data[k].get('상세', []):
                        nm = str(item.get('종목명', ''))
                        if nm and nm not in ["[ 합  계 ]", "예수금", "현금성자산", "현금성자산(예수금)", "외화예수금", "USD", "KRW"]:
                            g_item_cnt += 1

        # 3. 암호화폐 카운트
        c_acc_cnt = 1
        c_item_cnt = 0
        if isinstance(crypto_data, dict):
            for c in crypto_data.get('coins', []):
                if isinstance(c, dict) and c.get('ticker') != 'KRW':
                    c_item_cnt += 1

        # 4. 전체 합산 (AUM용)
        total_acc_cnt = p_acc_cnt + g_acc_cnt + c_acc_cnt
        total_item_cnt = p_item_cnt + g_item_cnt + c_item_cnt
    # =========================================================
    # 💡 사이드바 메뉴 디자인 (CSS)
    # =========================================================
        st.markdown("""
<style>
.zappa-expander {
background-color: #ffffff; border-radius: 12px; border: 1px solid #eaeaea;
margin-bottom: 8px; overflow: hidden;
transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.zappa-expander:not(.zappa-expander-dark):hover {
background-color: #E6F2FF !important; transform: translateY(-2px);
box-shadow: 0 6px 12px rgba(0,0,0,0.08) !important; border-color: #ccc;
}
.zappa-expander-dark { background-color: #1a1a1a !important; border: none !important; }
.zappa-expander-dark:hover {
background-color: #1a1a1a !important; transform: translateY(-2px);
box-shadow: 0 6px 12px rgba(255,255,255,0.08) !important;
}
.zappa-summary {
padding: 12px 14px; font-size: 13px; font-weight: bold; color: #777;
cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: center;
}
.zappa-summary::-webkit-details-marker { display: none; }
.zappa-summary::after {
content: '>'; font-family: monospace; font-weight: 900; font-size: 15px; color: #aaa;
transition: transform 0.2s ease; display: inline-block;
}
.zappa-expander[open] .zappa-summary::after { transform: rotate(90deg); }
.zappa-expander-dark .zappa-summary { color: #aaa; }
.zappa-expander-dark .zappa-summary::after { color: #666; }
.zappa-content { padding: 0px 14px 14px 14px; cursor: pointer; }
</style>
""", unsafe_allow_html=True)

        # 💡 [수정됨] 파이썬 강제 열림 통제 해제 (모두 닫힘이 기본값)
        open_aum = ""
        open_tax = ""
        open_gen = ""
        open_cryp = ""
        open_quant = ""
        open_arbi = ""

        # 💡 [패치 2] 사이드바 카드 렌더링 (전체 메뉴 디자인 통일 및 데이터 동기화)
        st.sidebar.markdown(f"""
<details id='zappa-exp-total' class='zappa-expander zappa-expander-dark' {open_aum} style='margin-top: -16px;'>
<summary class='zappa-summary'>
<span><span class='spin-globe'>🌎</span>&nbsp;총 운용자산<span style='font-size: 13px; font-weight: 500; color: #aaa; margin-left: 4px;'>( <b style='font-weight:700; color:#eee;'>{total_acc_cnt}</b> 계좌, <b style='font-weight:700; color:#eee;'>{total_item_cnt}</b> 종목 )</span></span>
</summary>
<div id='card-total' class='zappa-content'>
<div style='text-align: right;'>
<div style='font-size:24px; font-weight:600; letter-spacing:-0.5px; line-height: 1.1; color:#fff;'>{fmt(total_asset)} <span style='font-size:13px; font-weight:normal; color:#ddd;'>KRW</span></div>
<div style='font-size:17px; margin-top:2px; color:#ff4b4b;'><span class='{col(total_profit)}' style='font-weight:600;'>{fmt(total_profit, True)}</span> <span style='font-size:13.5px; font-weight:normal; color:#ddd;'>({fmt_p1(total_rate)})</span></div>
</div>
<div style='margin-top: 10px; padding-top: 10px; border-top: 1px solid #333;'>
<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;'>
<span style='font-size: 12px; color: #888; font-weight: normal;'>🎯 총 투자자산 <span style='font-size: 13px;'>30</span>억 로드맵</span>
<span style='font-size: 13.5px; font-weight: normal; color: #e8c368;'>{(total_asset / 3000000000 * 100):.1f}%</span>
</div>
<div style='width: 100%; height: 6px; background-color: #444; border-radius: 3px; overflow: hidden;'>
<div style='width: {(total_asset / 3000000000 * 100)}%; height: 100%; background: linear-gradient(90deg, #bfa054, #fceabb);'></div>
</div>
</div>
</div>
</details>

<details id='zappa-exp-tax' class='zappa-expander' {open_tax}>
<summary class='zappa-summary'>
<span>⏳ 절세계좌<span style='font-size: 13px; font-weight: 500; color: #888; margin-left: 4px;'>[ <b style='font-weight:700; color:#444;'>{p_acc_cnt}</b> 계좌, <b style='font-weight:700; color:#444;'>{p_item_cnt}</b> 종목 ]</span></span>
</summary>
<div id='card-pension' class='zappa-content'>
<div style='text-align: right; padding-bottom: 2px;'>
<div style='font-size:21px; font-weight:600; color:#111; letter-spacing:-0.5px; line-height: 1.1;'>{fmt(p_asset_all)} <span style='font-size:12.5px; font-weight:normal; color:#555;'>KRW</span></div>
<div style='font-size:16px; margin-top:3px; color:#555;'><span class='{col(p_profit_all)}' style='font-weight:bold;'>{fmt(p_profit_all, True)}</span> <span style='font-size:12.5px; font-weight:normal; color:#555;'>({fmt_p1(p_rate_invested)})</span></div>
</div>
<div style='width: 100%; height: 1px; background-color: #eee; margin-top: 8px; margin-bottom: 8px;'></div>
<div style='display:flex; justify-content:flex-end; align-items:center; gap:5px; width:100%; margin-bottom: -4px;'>
<span style='font-size:11px;'>🔵</span><span style='font-size:12.5px; font-weight:normal; color:#888; letter-spacing:-0.5px;'>국내 {p_dom_pct:.0f}% / 해외 {p_ovs_pct:.0f}%</span>
</div>
</div>
</details>

<details id='zappa-exp-gen' class='zappa-expander' {open_gen}>
<summary class='zappa-summary'>
<span>🪴 일반계좌<span style='font-size: 13px; font-weight: 500; color: #888; margin-left: 4px;'>[ <b style='font-weight:700; color:#444;'>{g_acc_cnt}</b> 계좌, <b style='font-weight:700; color:#444;'>{g_item_cnt}</b> 종목 ]</span></span>
</summary>
<div id='card-general' class='zappa-content'>
<div style='text-align: right; padding-bottom: 2px;'>
<div style='font-size:21px; font-weight:600; color:#111; letter-spacing:-0.5px; line-height: 1.1;'>{fmt(g_asset_all)} <span style='font-size:12.5px; font-weight:normal; color:#555;'>KRW</span></div>
<div style='font-size:16px; margin-top:3px; color:#555;'><span class='{col(g_profit_all)}' style='font-weight:bold;'>{fmt(g_profit_all, True)}</span> <span style='font-size:12.5px; font-weight:normal; color:#555;'>({fmt_p1(g_rate_all)})</span></div>
</div>
<div style='width: 100%; height: 1px; background-color: #eee; margin-top: 8px; margin-bottom: 8px;'></div>
<div style='display:flex; justify-content:flex-end; align-items:center; gap:5px; width:100%; margin-bottom: -4px;'>
<span style='font-size:11px;'>🔵</span><span style='font-size:12.5px; font-weight:normal; color:#888; letter-spacing:-0.5px;'>국내 {g_dom_pct:.0f}% / 해외 {g_ovs_pct:.0f}%</span>
</div>
</div>
</details>

<details id='zappa-exp-cryp' class='zappa-expander' {open_cryp}>
<summary class='zappa-summary'>
<span>🪙 암호화폐<span style='font-size: 13px; font-weight: 500; color: #888; margin-left: 4px;'>[ <b style='font-weight:700; color:#444;'>{c_acc_cnt}</b> 계좌, <b style='font-weight:700; color:#444;'>{c_item_cnt}</b> 종목 ]</span></span>
</summary>
<div id='card-crypto' class='zappa-content'>
<div style='text-align: right; padding-bottom: 2px;'>
<div style='font-size:21px; font-weight:600; color:#111; letter-spacing:-0.5px; line-height: 1.1;'>{fmt(c_tot_sum)} <span style='font-size:12.5px; font-weight:normal; color:#555;'>KRW</span></div>
<div style='font-size:16px; margin-top:3px; color:#555;'><span class='{col(c_prof_sum)}' style='font-weight:bold;'>{fmt(c_prof_sum, True)}</span> <span style='font-size:12.5px; font-weight:normal; color:#555;'>({fmt_p1(c_rate_sum_actual)})</span></div>
</div>
<div style='width: 100%; height: 1px; background-color: #eee; margin-top: 8px; margin-bottom: 8px;'></div>
<div style='display:flex; justify-content:flex-end; align-items:center; gap:5px; width:100%; margin-bottom: -4px;'>
<span style='font-size:11px;'>🔵</span><span style='font-size:12.5px; font-weight:normal; color:#888; letter-spacing:-0.5px;'>BTC {r_btc}% / ETH {r_eth}% / Alts {r_alts}%</span>
</div>
</div>
</details>
""", unsafe_allow_html=True)

        if 'show_admin_page' not in st.session_state:
            st.session_state['show_admin_page'] = False
   
        import textwrap  
        
        # =========================================================
        # 🪙 Zappa Alpha (알고리즘) 카드 - 상세페이지 동기화 완결
        # =========================================================
        algo_total_seed = 12156000
        algo_total_profit = 3450000
        algo_total_asset = algo_total_seed + algo_total_profit
        algo_total_rate = (algo_total_profit / algo_total_seed) * 100
        algo_win_rate = 89.0
        algo_total_trades = 112

        quant_card_html = f"""
<details id='zappa-exp-quant' class='zappa-expander' {open_quant}>
<summary class='zappa-summary'>
<span>🧩 알고리즘&nbsp; <span style='font-weight: normal;'>[</span> <span style='color:#444;'>Algorithmic T.</span> <span style='font-weight: normal;'>]</span></span>
</summary>
<div id='card-quant' class='zappa-content'>
<table style='width: 100%; border-collapse: collapse; border: none; background: transparent; margin-top: -2px; margin-bottom: 0px;'>
<tr style='background: transparent; border: none;'>
<td style='width: 62px; padding: 10; vertical-align: bottom; background: transparent; border: none;'>
<img src='{robot_img_src}' style='width:45px; height:45px; object-fit:contain; display: block;'>
</td>
<td style='padding: 0; padding-bottom: 2px; vertical-align: bottom; text-align: right; background: transparent; border: none;'>
<div style='font-size:21px; font-weight:600; color:#111; letter-spacing:-0.5px; line-height: 1.1;'>{fmt(algo_total_asset)} <span style='font-size:12.5px; font-weight:normal; color:#555;'>KRW</span></div>
<div style='font-size:16px; margin-top:3px; color:#555;'><span class='{col(algo_total_profit)}' style='font-weight:bold;'>{fmt(algo_total_profit, True)}</span> <span style='font-size:12.5px; font-weight:normal; color:#555;'>({fmt_p1(algo_total_rate)})</span></div>
</td>
</tr>
</table>
<div style='width: 100%; height: 1px; background-color: #eee; margin-top: 8px; margin-bottom: 8px;'></div>
<div style='display:flex; flex-direction:row; justify-content:center; gap:16px; width:100%; margin-bottom: -4px;'>
<div style='display:flex; align-items:center; gap:5px;'>
<span style='font-size:11px;'>🟢</span><span style='font-size:12.5px; font-weight:normal; color:#888; letter-spacing:-0.5px;'>승률 {algo_win_rate:g}%</span>
</div>
<div style='display:flex; align-items:center; gap:5px;'>
<span style='font-size:11px;'>🟡</span><span style='font-size:12.5px; font-weight:normal; color:#888; letter-spacing:-0.5px;'>총 거래 {algo_total_trades}건</span>
</div>
</div>
</div>
</details>
"""
        st.sidebar.markdown(quant_card_html, unsafe_allow_html=True)

        # =========================================================
        # ⚖️ 차익거래 카드 (사이드바) - 고정 UI 및 데이터 동기화
        # =========================================================
        arbi_total_seed = 23080000
        arbi_total_profit = 5920000
        arbi_total_asset = 129000000
        arbi_total_rate = (arbi_total_profit / arbi_total_seed) * 100
        arbi_win_rate = 89.0
        arbi_total_trades = 112

        arbi_card_html = f"""
<details id='zappa-exp-arbi' class='zappa-expander' {open_arbi}>
<summary class='zappa-summary'>
<span>⚖️ 차익거래&nbsp; <span style='font-weight: normal;'>[</span> <span style='color:#444;'>X-Arbitrage T.</span> <span style='font-weight: normal;'>]</span></span>
</summary>
<div id='card-arbi' class='zappa-content'>
<table style='width: 100%; border-collapse: collapse; border: none; background: transparent; margin-top: -2px; margin-bottom: 0px;'>
<tr style='background: transparent; border: none;'>
<td style='width: 62px; padding: 10; vertical-align: bottom; background: transparent; border: none;'>
<img src='{robot_img_src}' style='width:45px; height:45px; object-fit:contain; display: block;'>
</td>
<td style='padding: 0; padding-bottom: 2px; vertical-align: bottom; text-align: right; background: transparent; border: none;'>
<div style='font-size:21px; font-weight:600; color:#111; letter-spacing:-0.5px; line-height: 1.1;'>{fmt(arbi_total_asset)} <span style='font-size:12.5px; font-weight:normal; color:#555;'>KRW</span></div>
<div style='font-size:16px; margin-top:3px; color:#555;'><span class='{col(arbi_total_profit)}' style='font-weight:bold;'>{fmt(arbi_total_profit, True)}</span> <span style='font-size:12.5px; font-weight:normal; color:#555;'>({fmt_p1(arbi_total_rate)})</span></div>
</td>
</tr>
</table>
<div style='width: 100%; height: 1px; background-color: #eee; margin-top: 8px; margin-bottom: 8px;'></div>
<div style='display:flex; flex-direction:row; justify-content:center; gap:16px; width:100%; margin-bottom: -4px;'>
<div style='display:flex; align-items:center; gap:5px;'>
<span style='font-size:11px;'>🟢</span><span style='font-size:12.5px; font-weight:normal; color:#888; letter-spacing:-0.5px;'>승률 {arbi_win_rate:g}%</span>
</div>
<div style='display:flex; align-items:center; gap:5px;'>
<span style='font-size:11px;'>🟡</span><span style='font-size:12.5px; font-weight:normal; color:#888; letter-spacing:-0.5px;'>총 거래 {arbi_total_trades}건</span>
</div>
</div>
</div>
</details>
"""
        st.sidebar.markdown(arbi_card_html, unsafe_allow_html=True)

        # =========================================================    
        # 💡 [핵심 패치] 사이드바 하단 여백 제거 및 메인 상세페이지 상단 끌어올림 통합
        # =========================================================
        st.markdown("""
<style>
/* 우측 메인 상세페이지 전체를 위로 끌어올림 (숫자를 조절하여 높이 맞춤) */
.block-container {
margin-top: -30px !important;
}

/* 사이드바 컨텐츠 자체의 하단 패딩 제거 */
div[data-testid="stSidebarContent"] {
padding-bottom: 0px !important;
}
/* 사이드바 내부 아이템들의 마지막 마진 제거 */
div[data-testid="stSidebarUserContent"] {
padding-bottom: 0px !important;
margin-bottom: -30px !important; /* 더 바짝 올리기 위해 마이너스 마진 사용 */
}
</style>
""", unsafe_allow_html=True)
        # 💡 [패치] margin-top을 -5px로 줄여 위쪽 Zappa 로고 카드와 바짝 붙였습니다.
        master_signature_html = """
<div style='margin-top: -22px; padding-right: 15px; margin-bottom: 10px; display: flex; justify-content: flex-end;'>
<div style='display: flex; flex-direction: column; width: max-content;'>
<div style='font-size: 9.5px; color: #777; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; line-height: 1; margin-bottom: 3px;'>
ALGORITHM &amp; AI Engine <span style='color:#888888; margin:0 4px; font-weight:300;'>|</span> Architect &amp; UI
</div>
<div style='display: flex; justify-content: space-between; align-items: baseline; line-height: 1;'>
<div style='font-size: 9.5px; color: #999999; font-weight: 500; letter-spacing: 1px;'>SINCE 2026,</div>
<div style='font-size: 9.5px; color: #666666; font-weight: 700; letter-spacing: 0.5px;'>BY ANDY</div>
</div>
</div>
</div>
"""
        st.sidebar.markdown(master_signature_html, unsafe_allow_html=True)

        # =========================================================
        # [ Admin 버튼 꽉 찬 박스 (왼쪽으로 강제 이동 패치) ]
        # =========================================================
        st.sidebar.markdown("""
<style>
/* 💡 [패치] 메뉴 5종 전체 - 밝은 하늘색 호버 효과 통합 */
div#card-pension:hover,
div#card-general:hover,
div#card-crypto:hover,
div#card-quant:hover,
div#card-arbi:hover {
background-color: #E6F2FF !important;
cursor: pointer;
}                
div.element-container:has(#admin-btn-anchor) + div.element-container {
margin-top: 2px !important;
margin-bottom: 0px !important; /* 하단 스크롤 방지를 위해 마진 제거 */
padding-left: 16px !important;
}
/* 💡 버튼 외곽 박스 디자인 */
div.element-container:has(#admin-btn-anchor) + div.element-container button {
background: #f4f5f7 !important;
border: 1px solid #dcdcdc !important;
border-radius: 6px !important;
padding: 4px 12px !important;  
min-height: 26px !important;  
height: 28px !important;      
width: fit-content !important;

/* 👇 Streamlit 레이아웃을 무시하고 버튼을 강제로 왼쪽으로 15px 당깁니다 */
margin-left: -15px !important;

box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
display: flex !important;
align-items: center !important;
justify-content: center !important;
}
/* 💡 버튼 내부 글씨 디자인 */
div.element-container:has(#admin-btn-anchor) + div.element-container button p {
color: #444444 !important;
font-size: 12.5px !important;  
font-weight: 800 !important;
margin: 0 !important;
padding: 0 !important;
line-height: 1 !important;    
}
div.element-container:has(#admin-btn-anchor) + div.element-container button:hover {
background: #e9ecef !important;
border-color: #bbbbbb !important;
}
</style>
""", unsafe_allow_html=True)

        # 💡 ADMIN 버튼
        st.sidebar.markdown("<div id='admin-btn-anchor'></div>", unsafe_allow_html=True)
        if st.sidebar.button("🔒\uFE0F Admin", key="admin_final_btn"):
            st.session_state['show_admin_page'] = True
            st.rerun()

        # 💡 LOG-OUT 버튼 (대문 아이콘 적용 & 완전 로그아웃 콜백 적용)
        st.sidebar.markdown("<div id='logout-btn-anchor'></div>", unsafe_allow_html=True)
       
        def process_logout():
            # 1. 주소창의 파라미터(토큰) 완전 삭제
            st.query_params.clear()
           
            # 2. 스트림릿 인증기(Authenticator) 내부 상태 완벽 초기화
            st.session_state["authentication_status"] = None
            st.session_state["name"] = None
            st.session_state["username"] = None
            st.session_state["logout"] = True  # 공식 로그아웃 시그널
            st.session_state['show_admin_page'] = False
           
            # 3. 새로운 쿠키(v2) 강제 파기
            try:
                authenticator.cookie_manager.delete('zappa_cookie_v2')
            except:
                pass

        # 버튼 클릭 시(on_click) 즉시 위 함수를 실행
        st.sidebar.button("🚪 Logout", key="logout_final_btn", on_click=process_logout)

        # =========================================================
        # 👇👇👇 여기서부터 복사해서 맨 아래에 추가해 주세요 👇👇👇
        # =========================================================
        # 💡 [패치] 모든 메뉴 & 버튼 호버 시 '공부하는 여자아이' 이미지 전환 연동
        st.sidebar.markdown(f"""
<style>
/* JS에서 호버 상태일 때 추가할 클래스 (sea_src2 강제 적용) */
.seal-hover-box.active-girl {{ background-image: url('{sea_src2}') !important; }}
</style>
""", unsafe_allow_html=True)

        components.html("""
<script>
const parentDoc = window.parent.document;
function bindGirlHover() {
// 공부하는 여자아이 이미지 박스 찾기
const girlBox = parentDoc.querySelector('.seal-hover-box');
if (!girlBox) return;
// 호버 이벤트를 연결할 타겟 ID 목록
const targetIds = [
'card-total', 'card-pension', 'card-general',
'card-crypto', 'card-quant', 'card-arbi', 'unified-update-btn'
];
let elements = targetIds.map(id => parentDoc.getElementById(id)).filter(el => el);

// Admin 버튼 찾기 (anchor를 통해 추적)
const adminAnchor = parentDoc.getElementById('admin-btn-anchor');
if (adminAnchor) {
const adminContainer = adminAnchor.closest('.element-container').nextElementSibling;
if (adminContainer) {
const adminBtn = adminContainer.querySelector('button');
if (adminBtn) elements.push(adminBtn);
}
}
// 각 요소에 마우스를 올리고 내릴 때 이벤트 부여
elements.forEach(el => {
if (!el.hasAttribute('data-girl-binded')) {
el.setAttribute('data-girl-binded', 'true');
el.addEventListener('mouseenter', () => girlBox.classList.add('active-girl'));
el.addEventListener('mouseleave', () => girlBox.classList.remove('active-girl'));
}
});
}
// 스트림릿 렌더링 지연을 대비하여 1초마다 체크 후 바인딩
setInterval(bindGirlHover, 1000);
</script>
""", height=0)

        # 💡 [추가됨] 사용자가 열고 닫은 상태를 기억하는 JS 추가
        components.html("""
<script>
const parentDoc = window.parent.document;
function maintainExpanderState() {
const details = parentDoc.querySelectorAll('.zappa-expander');
details.forEach(detail => {
const id = detail.id;
if (!id) return;

// 1. 저장된 상태가 있으면 복원 (새로고침 시)
const savedState = sessionStorage.getItem(id);
if (savedState === 'open') { detail.setAttribute('open', ''); }
else if (savedState === 'closed') { detail.removeAttribute('open'); }

// 2. 사용자가 클릭할 때마다 상태 저장
if (!detail.hasAttribute('data-state-binded')) {
detail.setAttribute('data-state-binded', 'true');
detail.addEventListener('toggle', () => {
if (detail.open) { sessionStorage.setItem(id, 'open'); }
else { sessionStorage.setItem(id, 'closed'); }
});
}
});
}
setInterval(maintainExpanderState, 300);
</script>
""", height=0)
 
    # =========================================================
    # 🔒 [Zappa Admin] 통합 자산 관리 패널 (박스 제거 & 디자인 완결판)
    # =========================================================
    if st.session_state.get('show_admin_page', False):
        # 👇 자물쇠 컬러 강제 적용 및 복귀 버튼 복원
        st.markdown("<h3 style='margin-top: 5px;'><span style='font-family: \"Apple Color Emoji\", \"Segoe UI Emoji\", \"Noto Color Emoji\", sans-serif;'>🔒</span> Andy-Zappa Admin</h3>", unsafe_allow_html=True)
       
        if st.button("⬅️ Back to Dashboard"):
            st.session_state['show_admin_page'] = False
            st.rerun()

        # 1. 디자인 스타일 (1px 정밀 조정 및 모든 테두리 제거)
        st.markdown("---")
   
        try:
            res = requests.get("http://168.107.15.252:8000/get_config", timeout=5)
            cfg = res.json() if res.status_code == 200 else {}
        except:
            cfg = {}
       
        # 💡 [패치] 이중 로그인 제거 및 비밀번호 변경 단방향 암호화 적용
        with st.expander("🔑 관리자 비밀번호 변경", expanded=False):
            st.markdown("<div style='font-size:13.5px; color:#666; margin-bottom:10px;'>※ 변경된 비밀번호는 즉시 단방향 암호화(Bcrypt) 처리되어 서버에 안전하게 저장됩니다. 파이썬 코드에 남지 않습니다.</div>", unsafe_allow_html=True)
            col_old, col_new = st.columns(2)
            with col_old: old_pw = st.text_input("현재 비밀번호", type="password", key="pw_change_old")
            with col_new: new_pw = st.text_input("새로운 비밀번호", type="password", key="pw_change_new")
       
            if st.button("비밀번호 변경 실행", use_container_width=True):
                if not old_pw or not new_pw:
                    st.warning("비밀번호를 모두 입력해주세요.")
                else:
                    import bcrypt
                    is_pw_correct = False
                   
                    # 1. 💡 [정상 모드] 이제 서버에 저장된 해시 암호와 입력한 비번을 대조합니다.
                    if fetched_hashed_pw:
                        try:
                            # bcrypt.checkpw는 (입력비번, 서버해시)를 비교해 True/False를 반환합니다.
                            if bcrypt.checkpw(old_pw.encode('utf-8'), fetched_hashed_pw.encode('utf-8')):
                                is_pw_correct = True
                        except Exception:
                            # 만약의 에러를 대비해 텍스트 직접 비교 보조 (마이그레이션용)
                            if old_pw == fetched_hashed_pw:
                                is_pw_correct = True
                   
                    if is_pw_correct:
                        # 2. 신규 비번 해싱 후 서버 덮어쓰기
                        new_hashed_pw = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        cfg["ZAPPA_HASHED_PW"] = new_hashed_pw
                        cfg["ADMIN_PW"] = "" # 평문 기록은 영구 삭제
                       
                        try:
                            res = requests.post("http://168.107.15.252:8000/update_config", json=cfg, timeout=20)
                            if res.status_code == 200:
                                st.success("✅ 비밀번호가 안전하게 변경되었습니다!")
                            else:
                                st.error("❌ 서버 오류로 변경에 실패했습니다.")
                        except Exception as e:
                            st.error(f"❌ 서버 연결 오류 발생: {e}")
                    else:
                        st.error("❌ 현재 비밀번호가 일치하지 않습니다.")
        st.markdown("<br>", unsafe_allow_html=True)
   
        # 💡 [패치] 관리자 인증 과정 생략 (메인 로그인으로 갈음) 후 즉시 자산 관리 렌더링
        col_cat, col_acc = st.columns(2)
        with col_cat: category = st.selectbox("1️⃣ 자산 유형 선택", ["📂절세계좌", "📂일반계좌", "📂암호화폐"])
   
        if category == "📂절세계좌":
            acc_list = {"[ 퇴직연금(DC) (삼성 : 7165962472-28) ]": "DC", "[ 퇴직연금(IRP)계좌 (삼성 : 7164499007-29) ]": "IRP", "[ 연금저축(CMA)계좌 (삼성 : 7169434836-15) ]": "PENSION", "[ ISA(중개형) (키움 : 6448-4934) ]": "ISA"}
        elif category == "📂일반계좌":
            acc_list = {"[ 국내Ⅰ. 키움증권 (위탁종합 : 6312-5329) ]": "DOM1", "[ 국내Ⅱ. 삼성증권 (주식보상 : 7162669785-01) ]": "DOM2", "[ 미국Ⅰ. 키움증권 (위탁종합 : 6312-5329) ]": "USA1", "[ 미국Ⅱ. 키움증권 (위탁종합 : 6443-5993) ]": "USA2"}
        else:
            acc_list = {"[ UPbit 거래소 ]": "CRYPTO"}

           
        with col_acc: sel_acc_label = st.selectbox("2️⃣ 세부 계좌 선택", options=list(acc_list.keys()))
   
        sel_key = acc_list[sel_acc_label]
        is_usa = "USA" in sel_key
        cash_unit = "USD" if is_usa else "KRW"
   
        st.markdown("---")
        st.markdown("<div class='admin-section-title'>1️⃣ 자산정보 요약</div>", unsafe_allow_html=True)
   
        sum_data = {
            "현금성자산(예수금)": [safe_float(cfg.get(f"{sel_key}_CASH", 0))],
            "투자원금": [safe_float(cfg.get(f"{sel_key}_PRINCIPAL", 0))]
        }
        df_sum = pd.DataFrame(sum_data)
   
        sum_cfg = {
            "현금성자산(예수금)": st.column_config.NumberColumn(f"💵 현금성자산 ({cash_unit})", format="%,.4f" if is_usa else "%,.0f", step=0.0001 if is_usa else 1.0),
            "투자원금": st.column_config.NumberColumn("💰 투자원금 (KRW)", format="%,.0f", step=1.0)
        }
   
        edited_sum = st.data_editor(df_sum, use_container_width=True, column_config=sum_cfg, key=f"sum_editor_{sel_key}", hide_index=True)
        new_cash = edited_sum.iloc[0]["현금성자산(예수금)"]
        new_prin = edited_sum.iloc[0]["투자원금"]
   
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='admin-section-title'>2️⃣ 보유종목 리스트</div>", unsafe_allow_html=True)
   
        curr_items = cfg.get(sel_key, [])
        df_items = pd.DataFrame(curr_items)
        rename_map = {"name": "종목명", "ticker": "종목코드", "qty": "보유수량", "avg_price": "매입단가", "코드": "종목코드", "수량": "보유수량", "매입가": "매입단가", "매입금액": "매입단가"}
        if not df_items.empty: df_items.rename(columns=rename_map, inplace=True)
        for col in ["종목명", "종목코드", "보유수량", "매입단가"]:
            if col not in df_items.columns: df_items[col] = None
        df_items = df_items[["종목명", "종목코드", "보유수량", "매입단가"]]
   
        if sel_key == "CRYPTO":
            df_items["보유수량"] = pd.to_numeric(df_items["보유수량"], errors='coerce').fillna(0.0)
            df_items["매입단가"] = pd.to_numeric(df_items["매입단가"], errors='coerce').fillna(0.0)
            col_cfg = {
                "종목명": st.column_config.TextColumn("종목명"),
                "보유수량": st.column_config.NumberColumn("보유수량", format="%.8f", step=1e-8),
                "매입단가": st.column_config.NumberColumn("매입단가 (KRW)", format="%,.2f", step=0.01)
            }
        else:
            df_items["보유수량"] = pd.to_numeric(df_items["보유수량"], errors='coerce').fillna(0.0).astype(float)
            df_items["매입단가"] = pd.to_numeric(df_items["매입단가"], errors='coerce').fillna(0.0).astype(float)
       
            p_format = "%,.4f" if is_usa else "%,.0f"
            p_step = 0.0001 if is_usa else 1.0
       
            col_cfg = {
                "종목명": st.column_config.TextColumn("종목명"),
                "종목코드": st.column_config.TextColumn("종목코드"),
                "보유수량": st.column_config.NumberColumn("보유수량", format=p_format, step=p_step),
                "매입단가": st.column_config.NumberColumn(f"매입단가 ({cash_unit})", format=p_format, step=p_step)
            }
       
        edited_df = st.data_editor(df_items, num_rows="dynamic", use_container_width=True, column_config=col_cfg, key=f"editor_{sel_key}")
   
        if category == "📂절세계좌":
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='admin-section-title'>3️⃣ 안전자산 현황</div>", unsafe_allow_html=True)
            safe_key = f"{sel_key}_SAFE"
            raw_safe = cfg.get(safe_key, [])
            df_safe = pd.DataFrame(raw_safe)
            if df_safe.empty: df_safe = pd.DataFrame(columns=["종목명", "투자원금", "연이율(%)", "매입일자"])
            if "매입일자" in df_safe.columns: df_safe["매입일자"] = pd.to_datetime(df_safe["매입일자"], errors='coerce')
       
            safe_cfg = {
                "종목명": st.column_config.TextColumn("종목명"),
                "투자원금": st.column_config.NumberColumn("투자원금 (KRW)", format="%,.0f", step=1.0),
                "연이율(%)": st.column_config.NumberColumn("연이율(%)", format="%.2f", step=0.01),
                "매입일자": st.column_config.DateColumn("매입일자", format="YYYY-MM-DD")
            }
            edited_safe = st.data_editor(df_safe, num_rows="dynamic", use_container_width=True, column_config=safe_cfg, key=f"safe_{sel_key}")
       
        st.markdown("<br>", unsafe_allow_html=True)
   
        @st.dialog("🚀 실시간 데이터 배포 최종 확인")
        def confirm_deploy_dialog(config_to_save, acc_label, cash_val, prin_val):
            st.warning(f"⚠️ **{acc_label}** 데이터를 오라클 서버로 전송하시겠습니까?")
            st.markdown(f"""
            - **입력된 현금**: {float(cash_val):,}
            - **입력된 원금**: {float(prin_val):,}
            - **배포 버튼 클릭 시 즉시 데이터 정합성이 업데이트됩니다.**
            """)
            st.write("")
       
            c1, c2 = st.columns(2)
            with c1:
                confirm_btn = st.button("✅ 배포 진행 (Confirm)", type="primary", key="btn_confirm_deploy", use_container_width=True)
            with c2:
                if st.button("❌ 취소 (Cancel)", key="btn_cancel_deploy", use_container_width=True):
                    st.rerun()
       
            if confirm_btn:
                try:
                    res = requests.post("http://168.107.15.252:8000/update_config", json=config_to_save, timeout=20)
                    if res.status_code == 200:
                        st.success("✅ 오라클 서버에 성공적으로 배포되었습니다. 1~2초 후 새로고침됩니다.")
                        st.cache_data.clear()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ 서버 배포 실패: {res.text}")
                except Exception as e:
                    st.error(f"❌ 연결 오류:\n{e}")
               
        if st.button(f"🚀 실시간 데이터 배포 (Deploy to Oracle)", type="primary", use_container_width=True):
            save_df = edited_df.copy()
       
            if sel_key == "CRYPTO":
                save_df.rename(columns={"종목명": "name", "종목코드": "ticker", "보유수량": "qty", "매입단가": "avg_price"}, inplace=True)
            else:
                save_df.rename(columns={"종목명": "종목명", "종목코드": "코드", "보유수량": "수량", "매입단가": "매입가"}, inplace=True)
           
            clean_records = []
            for _, row in save_df.iterrows():
                rec = {}
                for k, v in row.items():
                    if pd.isna(v): rec[k] = ""
                    elif isinstance(v, (int, np.integer)): rec[k] = int(v)
                    elif isinstance(v, (float, np.floating)): rec[k] = float(v)
                    else: rec[k] = str(v)
                clean_records.append(rec)
           
            cfg[sel_key] = clean_records
            cfg[f"{sel_key}_CASH"] = float(new_cash) if new_cash else 0.0
            cfg[f"{sel_key}_PRINCIPAL"] = float(new_prin) if new_prin else 0.0
       
            if category == "📂절세계좌":
                safe_df = edited_safe.copy().fillna("")
                safe_records = safe_df.to_dict('records')
                for r in safe_records:
                    date_val = r.get('매입일자')
                    if date_val and str(date_val).strip() != "":
                        r['매입일자'] = date_val.strftime('%Y-%m-%d') if hasattr(date_val, 'strftime') else str(date_val)[:10]
                    else:
                        r['매입일자'] = ""
                cfg[f"{sel_key}_SAFE"] = safe_records
           
            confirm_deploy_dialog(cfg, sel_acc_label, new_cash, new_prin)
       
        st.stop()
    # =========================================================
    # 💡 대시보드 화면 (Treemap & Pie Chart)
    # =========================================================
    if st.session_state.current_view == '대시보드':
        st.markdown("<h3 style='margin-top: 5px; margin-bottom: 25px;'>🧩 총 자산 통합 포트폴리오 분석 (Treemap)</h3>", unsafe_allow_html=True)
   
        try:
            import pandas as pd
            import numpy as np
            import plotly.express as px
            import plotly.graph_objects as go
            HAS_PLOTLY = True
        except ImportError: HAS_PLOTLY = False

        if HAS_PLOTLY:
            def get_category(nm):
                nm_u = nm.upper()
                if any(x in nm_u for x in ['KODEX', 'TIGER', 'PLUS', 'RISE', 'ETF', 'QQQ', 'SOXL']): return 'ETF / 지수'
                if any(x in nm_u for x in ['삼성전자', '엔비디아', 'NVIDIA', 'TSMC', 'TSM', '반도체']): return '반도체'
                if any(x in nm_u for x in ['애플', 'AAPL', '마이크로소프트', 'MSFT', '알파벳', 'GOOGL', '피그마']): return '빅테크'
                if any(x in nm_u for x in ['아이온큐', 'IONQ', '리케티', 'RGTI', '디 웨이브', 'QBTS', '아이렌', 'IREN', '팔란티어', 'PLTR']): return 'AI / 컴퓨팅'
                if any(x in nm_u for x in ['테슬라', 'TSLA', '현대차', '한국항공우주', '한화오션']): return '모빌리티 / 산업재'
                if any(x in nm_u for x in ['예수금', '현금', 'MMF', '이율보증']): return '현금성 자산'
                return '기타 / 금융'

            def wrap_text(name):
                if len(name) > 10 and ' ' not in name:
                    match = re.search(r'\d+', name)
                    if match:
                        idx = match.end()
                        return name[:idx] + '<br>' + name[idx:]
                    return name[:len(name)//2] + '<br>' + name[len(name)//2:]
                return name.replace(" ", "<br>") if len(name) > 12 else name

            all_pension_list = []
            all_gen_list = []
       
            if isinstance(data, dict):
                for k in ['DC', 'IRP', 'PENSION', 'ISA']:
                    if k in data and isinstance(data[k], dict):
                        details = data[k].get('상세', [])
                        if isinstance(details, list):
                            for item in details:
                                if isinstance(item, dict):
                                    nm = str(item.get('종목명', '')).strip()
                                    if nm == '[ 합  계 ]': continue
                                    asset = safe_float(item.get('총 자산', item.get('총자산', 0)))
                                    if asset > 0:
                                        all_pension_list.append({
                                            '카테고리': get_category(nm), '종목명': nm, '자산': asset,
                                            '평가손익': safe_float(item.get('평가손익', 0)), '수익률': safe_float(item.get('수익률(%)', 0)),
                                            '전일비': safe_float(item.get('전일비', 0)), '수량': safe_float(item.get('수량', 0)),
                                            '매입가': safe_float(item.get('매입가', 0)), '현재가': safe_float(item.get('현재가', 0))
                                        })

            if isinstance(g_data, dict):
                for k in ['DOM1', 'DOM2', 'USA1', 'USA2']:
                    if k in g_data and isinstance(g_data[k], dict):
                        fx = safe_float(g_data.get('환율', 1443.1)) if 'USA' in k else 1
                        details = g_data[k].get('상세', [])
                        if isinstance(details, list):
                            for item in details:
                                if isinstance(item, dict):
                                    nm = str(item.get('종목명', '')).strip()
                                    if nm == '[ 합  계 ]': continue
                                    asset = safe_float(item.get('총자산', 0)) * fx
                                    if asset > 0:
                                        all_gen_list.append({
                                            '카테고리': get_category(nm), '종목명': nm, '자산': asset,
                                            '평가손익': safe_float(item.get('평가손익', 0)) * fx, '수익률': safe_float(item.get('수익률(%)', 0)),
                                            '전일비': safe_float(item.get('전일비', 0)), '수량': safe_float(item.get('수량', 0)),
                                            '매입가': safe_float(item.get('매입가', 0)) * fx, '현재가': safe_float(item.get('현재가', 0)) * fx
                                        })

            def render_treemap(data_list, title):
                if not data_list: return None
                df = pd.DataFrame(data_list)
                df = df.groupby(['카테고리', '종목명']).agg({
                    '자산': 'sum', '평가손익': 'sum', '수량': 'sum',
                    '매입가': 'mean', '현재가': 'mean', '전일비': 'mean', '수익률': 'mean'
                }).reset_index()
           
                total_sum = df['자산'].sum()
                labels, parents, values = ["포트폴리오"], [""], [0]
                colors, texts, custom_data = ["#1e222d"], [""], [[0,0,0,0,0,0,0]]

                for cat in df['카테고리'].unique():
                    labels.append(cat); parents.append("포트폴리오"); values.append(0)
                    colors.append("#2a2e39"); texts.append(f"<b style='font-size:14px; color:#e2e8f0;'>{cat}</b>"); custom_data.append([0,0,0,0,0,0,0])

                for _, r in df.iterrows():
                    labels.append(r['종목명']); parents.append(r['카테고리']); values.append(r['자산'])
                    if r['카테고리'] == '현금성 자산': c_color = '#4b5563'
                    elif r['전일비'] > 0: c_color = '#ff7675'
                    elif r['전일비'] < 0: c_color = '#74b9ff'
                    else: c_color = '#616161'
                    colors.append(c_color)

                    nm_wrap = wrap_text(r['종목명'])
                    t_rate = f"▲{r['전일비']:.1f}%" if r['전일비'] > 0 else (f"▼{abs(r['전일비']):.1f}%" if r['전일비'] < 0 else "-")
                    t_asset = f"₩{int(r['자산']):,}"
                    texts.append(f"<span style='font-size:13.5px;'>{nm_wrap}</span><br><span style='font-size:12.5px;'>{t_rate}</span><br><span style='font-size:11.5px; opacity:0.8;'>{t_asset}</span>")
                    pct = (r['자산'] / total_sum) * 100 if total_sum > 0 else 0
                    custom_data.append([pct, r['평가손익'], r['수익률'], r.get('수량',0), r.get('매입가',0), r.get('현재가',0), r['전일비']])

                fig = go.Figure(go.Treemap(
                    labels=labels, parents=parents, values=values, text=texts, textinfo="text",
                    marker_colors=colors, customdata=custom_data,
                    marker=dict(cornerradius=8),
                    hovertemplate=(
                        "<b style='font-size:16px;'>%{label}</b><br><br>"
                        "<b>총자산:</b> %{value:,.0f}원 (비중: %{customdata[0]:.1f}%)<br>"
                        "<b>평가손익:</b> %{customdata[1]:+,.0f}원 (%{customdata[2]:.2f}%)<br>"
                        "<b>등락률:</b> %{customdata[6]:.2f}%<br>"
                        "<b>주식수:</b> %{customdata[3]:,.2f}주<br>"
                        "<b>매입/현재:</b> %{customdata[4]:,.0f} / %{customdata[5]:,.0f}<br><extra></extra>"
                    ),
                    textfont=dict(color='white', family='Arial', size=13), pathbar_textfont=dict(size=14, color='#fff'), root_color="#1e222d"
                ))
                fig.update_layout(margin=dict(t=40, l=10, r=10, b=10), title=dict(text=title, font=dict(size=17, color='#ffffff', family='sans-serif'), x=0.02, y=0.97), paper_bgcolor='#1e222d', plot_bgcolor='#1e222d', height=450)
                return fig

            c1, c2 = st.columns(2)
       
            def get_counts(lst):
                if not lst: return 0, 0
                df_c = pd.DataFrame(lst)
                if df_c.empty: return 0, 0
                df_c = df_c.groupby('종목명')['전일비'].mean().reset_index()
                up_c = len(df_c[df_c['전일비'] > 0])
                dn_c = len(df_c[df_c['전일비'] < 0])
                return up_c, dn_c
           
            pen_up, pen_dn = get_counts(all_pension_list)
            gen_up, gen_dn = get_counts(all_gen_list)

            with c1:
                st.markdown(f"""
<div style='text-align:center; padding:12px; background:#2a2e39; border-radius:10px; color:#e2e8f0; font-size:15px; font-weight:bold; margin-bottom:12px;'>
[지수추종 ETF] &nbsp;&nbsp;
상승↑ : <span style='color: #ff4b4b; font-size: 22px; font-weight: 900;'>{pen_up}</span> 종목 &nbsp; / &nbsp;
하락↓ : <span style='color: #4b8bff; font-size: 22px; font-weight: 900;'>{pen_dn}</span> 종목
</div>
""", unsafe_allow_html=True)
           
                st.markdown("<div style='background-color: #1e222d; padding: 5px; border-radius: 15px; margin-bottom: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); overflow: hidden;'>", unsafe_allow_html=True)
                if all_pension_list: st.plotly_chart(render_treemap(all_pension_list, "⏳ 절세계좌 통합 포트폴리오"), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
           
            with c2:
                st.markdown(f"""
<div style='text-align:center; padding:12px; background:#2a2e39; border-radius:10px; color:#e2e8f0; font-size:15px; font-weight:bold; margin-bottom:12px;'>
[개별종목] &nbsp;&nbsp;
상승↑ : <span style='color: #ff4b4b; font-size: 22px; font-weight: 900;'>{gen_up}</span> 종목 &nbsp; / &nbsp;
하락↓ : <span style='color: #4b8bff; font-size: 22px; font-weight: 900;'>{gen_dn}</span> 종목
</div>
""", unsafe_allow_html=True)
           
                st.markdown("<div style='background-color: #1e222d; padding: 5px; border-radius: 15px; margin-bottom: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); overflow: hidden;'>", unsafe_allow_html=True)
                if all_gen_list: st.plotly_chart(render_treemap(all_gen_list, "🪴 일반계좌 통합 (한국+미국) 포트폴리오"), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 🍩 대시보드 전용: 파이차트 그리기
    # ---------------------------------------------------------
            st.markdown("<h3 style='margin-top: 30px; margin-bottom: 20px;'>🍩 통합 종목별 상세 비중 (Pie Chart)</h3>", unsafe_allow_html=True)
       
            def get_detailed_grouped_df(keys, is_usa=False):
                records = []
                fx = safe_float(g_data.get('환율', 1443.1)) if is_usa else 1
                for k in keys:
                    if k in g_data and isinstance(g_data[k], dict):
                        details = g_data[k].get('상세', [])
                        if isinstance(details, list):
                            for it in details:
                                if not isinstance(it, dict): continue
                                nm = str(it.get('종목명', '')).strip()
                                if nm in ['[ 합  계 ]', '예수금', '현금성자산', 'MMF', '이율보증', '']: continue
                                if nm.upper() == 'FIGMA': nm = '피그마'
                                asset = safe_float(it.get('총자산', 0)) * fx
                                profit = safe_float(it.get('평가손익', 0)) * fx
                                buy_amt = asset - profit
                                qty = safe_float(it.get('수량', 0))
                                records.append({'종목명': nm, '총자산': asset, '평가손익': profit, '매입금액': buy_amt, '수량': qty})
                if not records: return pd.DataFrame()
                df = pd.DataFrame(records)
                df_g = df.groupby('종목명').sum().reset_index()
                df_g['수익률'] = (df_g['평가손익'] / df_g['매입금액'] * 100).fillna(0)
                df_g = df_g.sort_values('총자산', ascending=False).reset_index(drop=True)
                return df_g

            def render_interactive_pie_area(df_pie, title):
                if df_pie.empty: return
                donut_colors = ['#D32F2F','#F57C00','#FBC02D','#388E3C','#1976D2','#7B1FA2', '#0097A7', '#689F38', '#C2185B', '#E64A19', '#303F9F', '#455A64']
                chart_data = [{"value": float(row['총자산']), "name": row['종목명']} for idx, row in df_pie.iterrows()]
                total_asset = df_pie['총자산'].sum()
                items_js = []
                list_html = ""
           
                for i, row in enumerate(df_pie.to_dict('records')):
                    pct = (row['총자산'] / total_asset) * 100 if total_asset > 0 else 0
                    logo = get_logo_html(row['종목명'])
               
                    p_class = "#D32F2F" if row['평가손익'] > 0 else ("#1976D2" if row['평가손익'] < 0 else "#9e9e9e")
                    sign = "+" if row['평가손익'] > 0 else ""
                    c_code = donut_colors[i % len(donut_colors)]
                    qty_str = f"{row['수량']:,.2f}".rstrip('0').rstrip('.') if row['수량'] % 1 != 0 else f"{int(row['수량']):,}"
               
                    items_js.append({"index": i, "name": row['종목명'], "value": float(row['총자산']), "pct": f"{pct:.1f}%", "logo": logo, "asset": fmt(row['총자산']), "profit": f"{sign}{fmt(row['평가손익'])}", "rate": fmt_p(row['수익률']), "p_class": p_class, "color": c_code, "qty": qty_str})
               
                    list_html += f"""
<div id='leg-item-{i}' class='legend-item' data-idx='{i}' style='display:flex; justify-content:space-between; align-items:center; padding:12px 10px; border-bottom:1px solid #2a2e39; border-radius:8px; cursor:pointer; margin-bottom:6px; flex-shrink:0;'>
    <div style='display:flex; flex-direction:column; gap:6px;'>
        <div style='display:flex; align-items:center;'>
            <div style='width:14px; height:14px; border-radius:4px; margin-right:10px; background-color:{c_code}; box-shadow:0 0 3px rgba(0,0,0,0.5);'></div>
            {logo}
            <span style='color:#e2e8f0; font-size:15px; font-weight:bold;'>{row['종목명']}</span>
        </div>
        <div style='padding-left:24px;'>
            <span style='background:#1e293b; color:#94a3b8; font-size:11.5px; padding:3px 6px; border-radius:4px; font-weight:600;'>보유 {qty_str}주</span>
        </div>
    </div>
    <div style='display:flex; flex-direction:column; text-align:right; gap:6px;'>
        <div>
            <span style='color:#f1f5f9; font-size:14.5px; font-weight:bold;'>{fmt(row['총자산'])}원</span>
            <span style='color:#94a3b8; font-size:13px; margin-left:4px;'>({pct:.1f}%)</span>
        </div>
        <div>
            <span style='color:{p_class}; font-size:13.5px; font-weight:normal;'>{sign}{fmt(row['평가손익'])} ({fmt_p(row['수익률'])})</span>
        </div>
    </div>
</div>
"""
               
                html_code = f"""
<html><head><script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script><style>
body {{ margin:0; padding:0; font-family:'Apple SD Gothic Neo',sans-serif; background:transparent; user-select:none; overflow:hidden; }}
.box {{ background:#1a1e28; border-radius:15px; padding:25px; display:flex; flex-direction:column; height:100vh; max-height:560px; border:1px solid #2c3140; box-sizing:border-box; }}
.title {{ color:#fff; font-size:19px; font-weight:bold; margin-bottom:20px; flex-shrink:0; }}
.content {{ display:flex; height:calc(100% - 40px); overflow:hidden; flex-direction:row; }}
.left-panel {{ flex:1.15; display:flex; flex-direction:column; padding-right:15px; border-right:1px solid #2c3140; overflow:hidden; }}
.list-area {{ flex:1; overflow-y:auto; padding-right:10px; scroll-behavior: smooth; }}
.list-area::-webkit-scrollbar {{ width:6px; }}
.list-area::-webkit-scrollbar-thumb {{ background:#4b5563; border-radius:3px; }}
.chart-area {{ flex:1.2; position:relative; }}

.legend-item {{ transition:all 0.2s; border-left:4px solid transparent; }}
.legend-item:hover, .legend-item.active {{ background:#2d3240; transform:translateX(4px); }}

@media screen and (max-width: 750px) {{
    .content {{ flex-direction: column-reverse !important; }}
    .left-panel {{ flex: 1.2 !important; border-right: none !important; border-top: 1px solid #2c3140; padding-right: 0 !important; padding-top: 15px; }}
    .chart-area {{ flex: 1 !important; min-height: 230px; }}
}}
</style></head>
<body><div class="box"><div class="title">{title}</div><div class="content"><div class="left-panel"><div class="list-area">{list_html}</div></div><div class="chart-area" id="pie-chart"></div></div></div>
<script>
    var itemsData = {json.dumps(items_js, ensure_ascii=False)};
    var chart = echarts.init(document.getElementById('pie-chart'));
    chart.setOption({{ tooltip:{{show:false}}, color:{json.dumps(donut_colors)}, series:[{{ type:'pie', radius:['45%','85%'], itemStyle:{{borderColor:'#1a1e28',borderWidth:3}}, label:{{show:true,position:'inside',formatter:'{{d}}%',color:'#fff',fontSize:12,fontWeight:'bold'}}, data:{json.dumps(chart_data, ensure_ascii=False)} }}] }});

    chart.on('mouseover', function(p){{ highlightLegend(p.dataIndex); }});
    chart.on('mouseout', function(){{ highlightLegend(-1); }});

    function highlightLegend(idx){{
        document.querySelectorAll('.legend-item').forEach(el => {{
            el.classList.remove('active');
            el.style.borderLeftColor = 'transparent';
        }});
        if(idx >= 0) {{
            var target = document.getElementById('leg-item-'+idx);
            if(target) {{
                target.classList.add('active');
                target.style.borderLeftColor = itemsData[idx].color;
                target.scrollIntoView({{behavior: "smooth", block: "nearest"}});
            }}
        }}
    }}
</script></body></html>
"""
                components.html(html_code, height=580)

            df_dom_g = get_detailed_grouped_df(['DOM1', 'DOM2'])
            df_usa_g = get_detailed_grouped_df(['USA1', 'USA2'], is_usa=True)
       
            st.markdown("""
<style>
div[data-testid="column"] { padding-bottom: 80px !important; }
</style>
""", unsafe_allow_html=True)
       
            cb1, cb2 = st.columns(2)
       
            flag_kr = "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f1f0-1f1f7.png"
            flag_us = "https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/1f1fa-1f1f8.png"

            with cb1:
                title_kr = f"""
<div style='display: flex; align-items: center; justify-content: center; gap: 8px;'>
    <span style='font-size: 1.35rem; font-weight: bold; color: #eeeeee;'>🪴 일반계좌 통합 상세비중 (</span>
    <img src='{flag_kr}' style='height: 24px; width: 24px; object-fit: contain; margin-top: -3px;'>
    <span style='font-size: 1.35rem; font-weight: bold; color: #eeeeee;'>)</span>
</div>
"""
                try:
                    if not df_dom_g.empty:
                        render_interactive_pie_area(df_dom_g, title_kr)
                    else:
                        st.info("한국 계좌 데이터가 없습니다.")
                except: pass

            with cb2:
                title_us = f"""
<div style='display: flex; align-items: center; justify-content: center; gap: 8px;'>
    <span style='font-size: 1.35rem; font-weight: bold; color: #eeeeee;'>🪴 일반계좌 통합 상세비중 (</span>
    <img src='{flag_us}' style='height: 24px; width: 24px; object-fit: contain; margin-top: -3px;'>
    <span style='font-size: 1.35rem; font-weight: bold; color: #eeeeee;'>)</span>
</div>
"""
                try:
                    if not df_usa_g.empty:
                        render_interactive_pie_area(df_usa_g, title_us)
                    else:
                        st.info("미국 계좌 데이터가 없습니다.")
                except: pass
    
    # =========================================================
    # ⏳ 절세계좌 대시보드 상세 페이지
    # =========================================================
    elif st.session_state.current_view == '절세계좌':
        st.markdown("<h3 style='margin-top: 5px; margin-bottom: 25px;'>🚀 Andy lee님 [금융자산] 통합 대시보드</h3>", unsafe_allow_html=True)
        FIXED_ORDER = ['DC', 'IRP', 'PENSION', 'ISA']
        P_MAP = {'DC': '퇴직연금(DC)계좌', 'IRP': '퇴직연금(IRP)계좌', 'PENSION': '연금저축(CMA)계좌', 'ISA': 'ISA(중개형)계좌'}
        DATE_TAGS = {'DC': '[ 2025.08 ]', 'IRP': '[ 2025.08 ]', 'PENSION': '[ 2025.11 ]', 'ISA': '[ 2025.08 ]'}

        try:
            res_cfg = requests.get("http://168.107.15.252:8000/get_config", timeout=5)
            cfg_data = res_cfg.json() if res_cfg.status_code == 200 else {}
        except:
            cfg_data = {}

        if isinstance(data, dict):
            t_asset = sum(safe_float(data[k].get('총 자산', data[k].get('총자산', 0))) for k in FIXED_ORDER if k in data and isinstance(data[k], dict))
       
            t_principal = sum(safe_float(cfg_data.get(f"{k}_PRINCIPAL", 0)) for k in FIXED_ORDER if k in data and isinstance(data[k], dict))
            t_prof_actual = sum(safe_float(data[k].get('평가손익', 0)) for k in FIXED_ORDER if k in data and isinstance(data[k], dict))
            t_buy_total = t_asset - t_prof_actual
       
            t_prof_1ago = sum(safe_float(data[k].get('평가손익(1일전)', 0)) for k in FIXED_ORDER if k in data and isinstance(data[k], dict))
            t_prof_7ago = sum(safe_float(data[k].get('평가손익(7일전)', 0)) for k in FIXED_ORDER if k in data and isinstance(data[k], dict))
            t_prof_15ago = sum(safe_float(data[k].get('평가손익(15일전)', 0)) for k in FIXED_ORDER if k in data and isinstance(data[k], dict))
            t_prof_30ago = sum(safe_float(data[k].get('평가손익(30일전)', 0)) for k in FIXED_ORDER if k in data and isinstance(data[k], dict))
       
            t_prof_principal = t_prof_actual
            t_rate_principal = (t_prof_principal / t_principal * 100) if t_principal > 0 else 0
       
            t_prof_buy = t_prof_actual
            t_rate_buy = (t_prof_buy / t_buy_total * 100) if t_buy_total > 0 else 0
       
            t_diff_1 = t_prof_buy - t_prof_1ago
            t_diff_7 = t_prof_buy - t_prof_7ago
            t_diff_30 = t_prof_buy - t_prof_30ago
       
            cash_total = p_cash_tot
            ovs_total = p_ovs_tot
            dom_total = p_dom_tot
       
            total_for_bar = max(1, t_asset)
            p_dc = safe_float(data.get('DC', {}).get('총 자산', data.get('DC', {}).get('총자산', 0))) / total_for_bar * 100 if isinstance(data.get('DC'), dict) else 0
            p_irp = safe_float(data.get('IRP', {}).get('총 자산', data.get('IRP', {}).get('총자산', 0))) / total_for_bar * 100 if isinstance(data.get('IRP'), dict) else 0
            p_pen = safe_float(data.get('PENSION', {}).get('총 자산', data.get('PENSION', {}).get('총자산', 0))) / total_for_bar * 100 if isinstance(data.get('PENSION'), dict) else 0
            p_isa = safe_float(data.get('ISA', {}).get('총 자산', data.get('ISA', {}).get('총자산', 0))) / total_for_bar * 100 if isinstance(data.get('ISA'), dict) else 0
       
            p_cash_donut = (cash_total / t_asset * 100) if t_asset > 0 else 0
            p_ovs_donut = (ovs_total / t_asset * 100) if t_asset > 0 else 0
            p_dom_donut = (dom_total / t_asset * 100) if t_asset > 0 else 0
       
            donut_css = f"background: conic-gradient(#ffffff 0% {p_cash_donut}%, #d9d9d9 {p_cash_donut}% {p_cash_donut+p_ovs_donut}%, #8c8c8c {p_cash_donut+p_ovs_donut}% 100%);"
            donut_html = f"<div style='position: relative; width: 120px; height: 120px; border-radius: 50%; {donut_css} box-shadow: inset 0 0 8px rgba(0,0,0,0.1); border: 1px solid #d0d0d0; flex-shrink: 0; margin: 0 auto;'><div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 35%; height: 35%; background-color: #fffdf2; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.05);'></div><div style='position: absolute; top: 0%; left: 50%; transform: translateX(-50%); font-size: 12.5px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_cash_donut:.0f}%<br>현금성자산</div><div style='position: absolute; top: 55px; right: -15px; font-size: 14px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_ovs_donut:.0f}%<br>해외투자</div><div style='position: absolute; bottom: 42px; left: -20px; font-size: 14px; color: #fff; font-weight: bold; text-align: center; line-height: 1.1; text-shadow: 0px 0px 3px rgba(0,0,0,0.5);'>{p_dom_donut:.0f}%<br>국내투자</div></div>"
       
            def render_bar(p, color): return f"<div style='width: {p}%; background-color: {color}; height: 100%; display: flex; align-items: center; justify-content: center; position: relative;'><span style='position: absolute; font-size: 13px; color: #333; z-index: 10; white-space: nowrap;'>{p:.0f}%</span></div>" if p > 0 else ""
       
            st.markdown("<div class='sub-title' style='margin-bottom: 15px;'>⏳ [절세계좌] 자산 현황 요약</div>", unsafe_allow_html=True)
            tax_proj_pct = (t_asset / 1500000000) * 100
       
            html_main = f"""
<div style='text-align: right; font-size: 13px; color: #555; font-weight: bold; margin-bottom: 5px;'>단위 : 원화(KRW)</div>
<div class='insight-container'>
<div class='insight-left'>
<div class='card-main'>
<div style='display: flex; gap: 15px; align-items: stretch; margin-bottom: auto;'>
<div style='flex: 0 0 38%; display: flex; flex-direction: column; align-items: center;'>
<div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 15px; width:100%; text-align:left;'>💡총 자산</div>
{donut_html}
<div style='font-size: 13.5px; color: #333; font-weight: bold; margin-top: 14px;'><span style='font-size: 12.5px; color: #666;'>원금</span> : {fmt(t_principal)}</div>
</div>
<div style='flex: 1; display: flex; flex-direction: column; justify-content: flex-start; padding-top: 5px;'>
<div class='card-inner' style='padding: 10px 12px; margin-bottom: 8px;'>
<div style='font-size: 24px; font-weight: 700 !important; color: #111; letter-spacing: normal; line-height: 1; margin-bottom: 6px;'>{fmt(t_asset)}<span style='font-size: 13.5px; font-weight: normal; margin-left: 3px; letter-spacing: normal;'>KRW</span></div>
<div style='font-size: 13.5px; color: #777; font-weight: normal; line-height: 1;'>[ 전일비 <span class='{col(t_diff_1)}'>{fmt(t_diff_1, True)}</span> / 전주비 <span class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</span> ]</div>
</div>
<div style='display: grid; grid-template-columns: auto auto; row-gap: 12px; column-gap: 30px; justify-content: end; align-items: baseline; width: 100%; padding-right: 12px; margin-top: 8px;'>
<div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>평가금액</div><div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(t_asset - cash_total)}</div>
<div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>현금성(예수금)</div><div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(cash_total)}</div>
<div style='color: #777; font-size: 14px; font-weight: normal; text-align: right; line-height: 20px;'>총 손익</div>
<div style='text-align: right;'>
<div style='font-size: 18px; font-weight: 600; line-height: 1;' class='{col(t_prof_principal)}'>{fmt(t_prof_principal, True)}</div>
<div style='font-size: 13.5px; font-weight: 600; margin-top: 3px; line-height: 1;' class='{col(t_rate_principal)}'>{fmt_p(t_rate_principal)}</div>
</div>
</div>
</div>
</div>
<div style='margin-top: 20px;'>
<div style='display: flex; height: 20px; width: 100%; border-radius: 4px; border: 1px solid #ccc; margin-bottom: 6px; overflow: hidden;'>
{render_bar(p_dc, '#b4a7d6')}{render_bar(p_irp, '#f4b183')}{render_bar(p_pen, '#a9d18e')}{render_bar(p_isa, '#ffd966')}
</div>
<div style='display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #777; padding: 0 2px; margin-bottom: 16px;'>
<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#b4a7d6; border-radius:3px;'></div>퇴직연금(DC)</div>
<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#f4b183; border-radius:3px;'></div>퇴직연금(IRP)</div>
<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#a9d18e; border-radius:3px;'></div>연금저축(CMA)</div>
<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#ffd966; border-radius:3px;'></div>ISA(중개형)</div>
</div>
<div style='padding: 10px 15px; background: rgba(255,255,255,0.5); border-radius: 10px; border: 1px solid #e8dbad;'>
<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>
<span style='font-size: 14px; color: #777; font-weight: normal;'>🎯 절세계좌 (ETF/ELS) 15억 만들기</span>
<div style='text-align: right;'><span style='font-size: 14px; font-weight: bold; color: #4a90e2;'>{tax_proj_pct:.1f}%</span></div>
</div>
<div style='width: 100%; height: 6px; background-color: #e2e2e2; border-radius: 3px; overflow: hidden;'>
<div style='width: {tax_proj_pct}%; height: 100%; background: linear-gradient(90deg, #9bc2e6, #4a90e2);'></div>
</div>
</div>
</div>
</div>
</div>
<div class='insight-right'><div class='grid-2x2'>
"""
       
            for k in FIXED_ORDER:
                if k in data and isinstance(data[k], dict):
                    a = data[k]
                    a_tot = safe_float(a.get('총 자산', a.get('총자산', 0)))
                    a_prin = safe_float(cfg_data.get(f"{k}_PRINCIPAL", 0))
                    a_prof = safe_float(a.get('평가손익', 0))
                    a_rate = (a_prof / a_prin * 100) if a_prin > 0 else 0
               
                    details_for_cnt = a.get('상세', [])
                    item_count = len([i for i in details_for_cnt if isinstance(i, dict) and str(i.get('종목명', '')) != '[ 합  계 ]' and '현금' not in str(i.get('종목명', '')) and '예수금' not in str(i.get('종목명', ''))])
                    k_date = DATE_TAGS.get(k, '')
                    html_main += f"""
<a href='#tax_detail_section' style='text-decoration:none; color:inherit; display:block; height:100%;'>
<div class='card-sub' style='height:100%; justify-content:space-between;'>
<div>
<div style='text-align: right; font-size: 13.5px; color: #888; font-weight: normal; margin-bottom: -2px; line-height: 1;'>{k_date}</div>
<div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 2px;'>{P_MAP[k]}</div>
<div style='border-bottom: 1px solid #eee; margin-bottom: 6px; margin-top: 2px;'></div>
<div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'>
<span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 자산</span>
<span style='font-size: 16px; color: #111; font-weight: normal;'>{fmt(a_tot)}</span>
</div>
<div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'>
<span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 손익</span>
<div style='text-align: right; line-height: 1.2;'>
<div class='{col(a_prof)}' style='font-size: 16px; font-weight: normal;'>{fmt(a_prof, True)}</div>
<div class='{col(a_rate)}' style='font-size: 14px; font-weight: normal; margin-top: 1px;'>{fmt_p(a_rate)}</div>
</div>
</div>
</div>
<div style='font-size: 13.5px; color: #666; font-weight: normal; margin-top: auto; padding-top: 2px; display: flex; justify-content: space-between; align-items: baseline;'>
<span>* <span style='font-size: 12.5px;'>원금</span> : {fmt(a_prin)}</span>
<span><span style='font-size: 16px; font-weight: bold; color: #111;'>{item_count}</span> 종목</span>
</div>
</div>
</a>
"""
            html_main += "</div></div></div>"
            st.markdown(html_main, unsafe_allow_html=True)

            tax_items = []
            for k in FIXED_ORDER:
                if k in data and isinstance(data[k], dict):
                    details = data[k].get('상세', [])
                    if isinstance(details, list):
                        for item in details:
                            if isinstance(item, dict) and item.get('종목명') not in ['[ 합  계 ]', '예수금', '현금성자산'] and '현금' not in str(item.get('종목명', '')):
                                it_copy = item.copy()
                                abbrev_map = {'DC': 'DC', 'IRP': 'IRP', 'PENSION': 'CMA', 'ISA': 'ISA'}
                                it_copy['계좌'] = abbrev_map.get(k, k)
                                tax_items.append(it_copy)
                           
            tax_best = sorted(tax_items, key=lambda x: safe_float(x.get('수익률(%)', 0)), reverse=True)[:5]
            tax_worst = sorted([it for it in tax_items if safe_float(it.get('수익률(%)', 0)) < 5.0], key=lambda x: safe_float(x.get('수익률(%)', 0)))[:5]
            tax_rise_cnt = sum(1 for it in tax_items if safe_float(it.get('전일비', 0)) > 0)
            tax_fall_cnt = sum(1 for it in tax_items if safe_float(it.get('전일비', 0)) < 0)
            tax_flat_cnt = len(tax_items) - tax_rise_cnt - tax_fall_cnt
       
            rise_list = sorted([x for x in tax_items if safe_float(x.get('전일비', 0)) > 0], key=lambda x: safe_float(x.get('전일비', 0)), reverse=True)[:3]
            fall_list = sorted([x for x in tax_items if safe_float(x.get('전일비', 0)) < 0], key=lambda x: safe_float(x.get('전일비', 0)))[:3]
       
            rise_str = ", ".join([f"{short_name(it['종목명'])}({it['계좌']} ▲{safe_float(it['전일비']):.2f}%)" for it in rise_list]) if rise_list else "없음"
            fall_str = ", ".join([f"{short_name(it['종목명'])}({it['계좌']} ▼{abs(safe_float(it['전일비'])):.2f}%)" for it in fall_list]) if fall_list else "없음"
            tax_zappa_html = f"""
<div style='font-size: 14.5px; line-height: 1.85; color: #444; padding-left: 0px;'>
<div style='margin-bottom: 22px;'>
<span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'>
<span style='font-size:11px;'>🔵</span> 계좌 현황 및 종목 분석
</span>
<div>현재 전체 포트폴리오 총 손익은 <span class='{col(t_prof_principal)}'><strong>{fmt(t_prof_principal, True)}</strong> (<span class='{col(t_rate_principal)}'><strong>{fmt_p(t_rate_principal)}</strong></span>)</span> 이며, 퇴직연금(IRP)계좌가 계좌별 수익률 1위를 기록 중입니다. 개별 종목에서는 <strong>{short_name(tax_best[0]['종목명']) if tax_best else '우량주'}</strong>가 효자 역할을 수행 중이나, <strong>{short_name(tax_worst[0]['종목명']) if tax_worst else '일부 종목'}</strong> 등은 단기 조정을 겪고 있습니다.<br>총 <strong>{len(tax_items)}개</strong> 종목 중 전일비 상승종목은 <strong>{tax_rise_cnt}개</strong>, 하락종목은 <strong>{tax_fall_cnt}개</strong>, 보합 <strong>{tax_flat_cnt}개</strong> 입니다.<br><span style='font-size:13.5px; color:#777; font-weight:500;'>※ 상승종목 : {rise_str}</span><br><span style='font-size:13.5px; color:#777; font-weight:500;'>※ 하락종목 : {fall_str}</span></div>
</div>
<div style='margin-bottom: 0px;'>
<span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'>
<span style='font-size:11px;'>🔵</span> 주식 시황 및 향후 대응 전략
</span>
<div>간밤 미국 지표의 끈적한 흐름과 연준의 금리 인하 신중론이 겹치며 변동성이 부각되었습니다. 아웃퍼폼 중인 종목에서 일부 차익 실현하여 현재 <strong>{(p_cash_tot/t_asset*100) if t_asset>0 else 0:.1f}%</strong>인 현금 비중을 선제적으로 확대할 필요가 있습니다.</div>
</div>
</div>
"""
       
            def render_table_rows(items_list):
                rows_html = ""
                for idx, it in enumerate(items_list):
                    c_price = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0))
                    diff_amt = (c_price - (c_price / (1 + d_rate / 100))) if c_price > 0 and d_rate != 0 else 0
                    d_class = col(d_rate)
                    diff_td = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px; font-weight:normal;'>{fmt_p(d_rate)}</div></td>"
               
                    orig_nm = str(it.get('종목명', '')).replace('\n', ' ').replace('\r', '').replace('`', '').strip()
                    clean_nm = re.sub(r'[^가-힣a-zA-Z0-9]', '', orig_nm)
                    fc = clean_nm[:1] if clean_nm else "E"
                    colors = ["#e6f2ff", "#e6ffe6", "#ffe6e6", "#fff0e6", "#f0e6ff", "#ffe6f9", "#e6ffff", "#f5ffe6"]
                    text_colors = ["#0066cc", "#006600", "#cc0000", "#cc5200", "#5200cc", "#cc00a3", "#00cccc", "#669900"]
                    idx_c = sum(ord(c) for c in fc) % len(colors)
                    direct_logo = f"<span style='display:inline-block; width:18px; height:18px; border-radius:50%; background-color:{colors[idx_c]}; color:{text_colors[idx_c]}; text-align:center; line-height:18px; font-size:10px; font-weight:900; margin-right:8px; vertical-align:middle; box-shadow: 0 1px 2px rgba(0,0,0,0.1);'>{fc}</span>"
               
                    nm_td = f"<td style='line-height:1.3; text-align:left; padding-left:10px;'>{direct_logo}{short_name(orig_nm)}<br><span style='font-size:11.5px; color:#888; font-weight:normal; margin-left:26px;'>({it.get('계좌', '')})</span></td>"
               
                    rows_html += f"<tr><td>{idx+1}</td>{nm_td}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td>{diff_td}</tr>"
                return rows_html
           
            st.markdown(f"""
<div class='insight-bottom-box' style='display: flex; gap: 20px; align-items: stretch;'>
<div style='flex: 1; padding-right: 15px; border-right: 1px solid #eaeaea;'>
<div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; letter-spacing: normal;'>📈 손익률 우수종목 (TOP 5)</div>
<table class='main-table' style='margin-bottom: 20px;'><tr><th style='width:40px;'></th><th style='text-align:center;'>종목명</th><th>손익률</th><th>평가손익</th><th>등락률</th></tr>{render_table_rows(tax_best)}</table>
<div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px; letter-spacing: normal;'>📉 손익률 부진종목</div>
<table class='main-table' style='margin-bottom: 0px;'><tr><th style='width:40px;'></th><th style='text-align:center;'>종목명</th><th>손익률</th><th>평가손익</th><th>등락률</th></tr>{render_table_rows(tax_worst)}</table>
</div>
<div style='flex: 1.1; padding-left: 5px;'>
<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 8px;'>
<div style='font-size: 18px; font-weight: bold; color: #111; letter-spacing: normal;'>💡 시황 및 향후 전망</div>
<div style='font-size: 13.5px; color: #888;'>[ -0.2%p < 보합 < +0.2%p ]</div>
</div>
{tax_zappa_html}
</div>
</div>
""", unsafe_allow_html=True)
       
            unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"
       
            # [1], [2]번 표를 위한 별도의 정렬 배열 생성 (sort_mode에 따라 정렬됨)
            sorted_tax_order = list(FIXED_ORDER)
            if st.session_state.sort_mode == 'asset':
                sorted_tax_order.sort(key=lambda k: safe_float(data.get(k, {}).get('총 자산', data.get(k, {}).get('총자산', 0))) if isinstance(data.get(k), dict) else -float('inf'), reverse=True)
            elif st.session_state.sort_mode == 'profit':
                sorted_tax_order.sort(key=lambda k: safe_float(data.get(k, {}).get('평가손익', 0)) if isinstance(data.get(k), dict) else -float('inf'), reverse=True)
            elif st.session_state.sort_mode == 'rate':
                def tax_rate_for_sort(k):
                    if not isinstance(data.get(k), dict): return -float('inf')
                    prin = safe_float(cfg_data.get(f"{k}_PRINCIPAL", 0))
                    prof = safe_float(data[k].get('평가손익', 0))
                    return (prof / prin * 100) if prin > 0 else 0
                sorted_tax_order.sort(key=tax_rate_for_sort, reverse=True)

            st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(t_prof_principal)}'>{fmt(t_prof_principal, True)} ({fmt_p(t_rate_principal)})</span></div></div>", unsafe_allow_html=True)
            h1_table = "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>투자원금</th></tr><tr><th class='th-week'>7일전</th><th class='th-week'>15일전</th><th class='th-week'>30일전</th></tr>"
            h1 = [unit_html, h1_table, f"<tr class='sum-row'><td>[ 합  계 ]</td><td>{fmt(t_asset)}</td><td class='{col(t_prof_principal)}'>{fmt(t_prof_principal, True)}</td><td class='{col(t_prof_7ago)}'>{fmt(t_prof_7ago, True)}</td><td class='{col(t_prof_15ago)}'>{fmt(t_prof_15ago, True)}</td><td class='{col(t_prof_30ago)}'>{fmt(t_prof_30ago, True)}</td><td class='{col(t_rate_principal)}'>{fmt_p(t_rate_principal)}</td><td>{fmt(t_principal)}</td></tr>"]
       
            for k in sorted_tax_order:
                if k in data and isinstance(data[k], dict):
                    a = data[k]
                    a_tot = safe_float(a.get('총 자산', a.get('총자산', 0)))
                    a_prin = safe_float(cfg_data.get(f"{k}_PRINCIPAL", 0))
                    a_prof = safe_float(a.get('평가손익', 0))
                    a_rate = (a_prof / a_prin * 100) if a_prin > 0 else 0
               
                    p7 = safe_float(a.get('평가손익(7일전)', 0))
                    p15 = safe_float(a.get('평가손익(15일전)', 0))
                    p30 = safe_float(a.get('평가손익(30일전)', 0))
                    h1.append(f"<tr><td>{P_MAP[k].split(' ')[0]}</td><td>{fmt(a_tot)}</td><td class='{col(a_prof)}'>{fmt(a_prof, True)}</td><td class='{col(p7)}'>{fmt(p7, True)}</td><td class='{col(p15)}'>{fmt(p15, True)}</td><td class='{col(p30)}'>{fmt(p30, True)}</td><td class='{col(a_rate)}'>{fmt_p(a_rate)}</td><td>{fmt(a_prin)}</td></tr>")
            h1.append("</table>")
            st.markdown("".join(h1), unsafe_allow_html=True)
       
            st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(t_prof_buy)}'>{fmt(t_prof_buy, True)} ({fmt_p(t_rate_buy)})</span></div>", unsafe_allow_html=True)
            h2_table = "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>매입금액</th></tr><tr><th class='th-week'>전일비</th><th class='th-week'>전주비</th><th class='th-week'>전월비</th></tr>"
            h2 = [unit_html, h2_table, f"<tr class='sum-row'><td>[ 합  계 ]</td><td>{fmt(t_asset)}</td><td class='{col(t_prof_buy)}'>{fmt(t_prof_buy, True)}</td><td class='{col(t_diff_1)}'>{fmt(t_diff_1, True)}</td><td class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</td><td class='{col(t_diff_30)}'>{fmt(t_diff_30, True)}</td><td class='{col(t_rate_buy)}'>{fmt_p(t_rate_buy)}</td><td>{fmt(t_buy_total)}</td></tr>"]
       
            for k in sorted_tax_order:
                if k in data and isinstance(data[k], dict):
                    a = data[k]
                    a_tot = safe_float(a.get('총 자산', a.get('총자산', 0)))
                    a_prof = safe_float(a.get('평가손익', 0))
                    a_buy = a_tot - a_prof
                    a_rate = (a_prof / a_buy * 100) if a_buy > 0 else 0
               
                    diff_1_acc = a_prof - safe_float(a.get('평가손익(1일전)', 0))
                    diff_7_acc = a_prof - safe_float(a.get('평가손익(7일전)', 0))
                    diff_30_acc = a_prof - safe_float(a.get('평가손익(30일전)', 0))
               
                    h2.append(f"<tr><td>{P_MAP[k].split(' ')[0]}</td><td>{fmt(a_tot)}</td><td class='{col(a_prof)}'>{fmt(a_prof, True)}</td><td class='{col(diff_1_acc)}'>{fmt(diff_1_acc, True)}</td><td class='{col(diff_7_acc)}'>{fmt(diff_7_acc, True)}</td><td class='{col(diff_30_acc)}'>{fmt(diff_30_acc, True)}</td><td class='{col(a_rate)}'>{fmt_p(a_rate)}</td><td>{fmt(a_buy)}</td></tr>")
            h2.append("</table>")
            st.markdown("".join(h2), unsafe_allow_html=True)
       
        # =========================================================
        # 🛡️ 절세계좌(ISA/IRP/DC) 상세페이지 - [플로팅 메뉴 정밀 튜닝]
        # =========================================================
        st.markdown("<div id='sav_detail_section' style='padding-top: 20px; margin-top: -20px;'></div><div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
       
        # 💡 [안전장치] 변수명 불일치로 인한 렌더링 중단(빈 캡슐 현상) 방지
        if 'sort_mode' not in st.session_state: st.session_state.sort_mode = 'init'
        if 'show_change_rate' not in st.session_state: st.session_state.show_change_rate = False

        # 💡 [핵심 패치] 종목코드의 [ 두께를 기준으로 모든 하이라이트(**) 두께/색상 100% 일치
        st.markdown("""
<style>
/* 모든 버튼 내부의 강조(**) 태그를 검정색 + 표준 굵기(700)로 박제 */
.stButton strong, .stButton b, button strong, button b {
color: #111111 !important;
font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

        s1, s2, s3, s4, s5, s6 = st.columns(6)
       
        with s1:
            st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
            lbl1 = "🔽**정렬 [** 초기화(●)" if st.session_state.sort_mode == 'init' else "🔽**정렬 [** 초기화(○)"
            if st.button(lbl1, type="primary" if st.session_state.sort_mode == 'init' else "secondary", key='sav_btn1', on_click=lambda: setattr(st.session_state, 'sort_mode', 'init')): pass
           
        with s2:
            lbl2 = "총자산(●)" if st.session_state.sort_mode == 'asset' else "총자산(○)"
            if st.button(lbl2, type="primary" if st.session_state.sort_mode == 'asset' else "secondary", key='sav_btn2', on_click=lambda: setattr(st.session_state, 'sort_mode', 'asset')): pass
           
        with s3:
            lbl3 = "평가손익(●)" if st.session_state.sort_mode == 'profit' else "평가손익(○)"
            if st.button(lbl3, type="primary" if st.session_state.sort_mode == 'profit' else "secondary", key='sav_btn3', on_click=lambda: setattr(st.session_state, 'sort_mode', 'profit')): pass
           
        with s4:
            lbl4 = "손익률(●) **]**" if st.session_state.sort_mode == 'rate' else "손익률(○) **]**"
            if st.button(lbl4, type="primary" if st.session_state.sort_mode == 'rate' else "secondary", key='sav_btn4', on_click=lambda: setattr(st.session_state, 'sort_mode', 'rate')): pass
           
        with s5:
            lbl5 = "↕️등락률[+]" if st.session_state.show_change_rate else "↕️등락률[-]"
            if st.button(lbl5, type="primary" if st.session_state.show_change_rate else "secondary", key='sav_btn5', on_click=lambda: setattr(st.session_state, 'show_change_rate', not st.session_state.show_change_rate)): pass
           
        with s6:
            lbl6 = "💻종목코드[+]" if st.session_state.show_code else "💻종목코드[-]"
            if st.button(lbl6, type="primary" if st.session_state.show_code else "secondary", key='sav_btn6', on_click=lambda: setattr(st.session_state, 'show_code', not st.session_state.show_code)): pass

        st.markdown("<br>", unsafe_allow_html=True)


        EXPANDER_MAP = {
            'DC': '퇴직연금(DC)계좌 / (삼성증권 7165962472-28)',
            'IRP': '퇴직연금(IRP)계좌 / (삼성증권 7164499007-29)',
            'PENSION': '연금저축(CMA)계좌 / (삼성증권 7169434836-15)',
            'ISA': 'ISA(중개형)계좌 / (키움증권 6448-4934)'
        }

        # [3]번 섹션은 고정된 순서(FIXED_ORDER)를 그대로 사용
        for k in FIXED_ORDER:
            if k in data and isinstance(data[k], dict):
                a = data[k]
                with st.expander(f"📂 [ {EXPANDER_MAP[k]} ] 종목별 현황", expanded=False):
                    details = a.get('상세', [])

                    if k == 'ISA':
                        has_cash = False
                        isa_cash_val = safe_float(cfg_data.get('ISA_CASH', 0))

                        for i in details:
                            if '현금' in str(i.get('종목명','')) or '예수금' in str(i.get('종목명','')):
                                i['총 자산'] = isa_cash_val; i['평가손익'] = 0; i['수익률(%)'] = 0; has_cash = True; break
                        if not has_cash:
                            details.append({'종목명': '현금성자산(예수금)', '총 자산': isa_cash_val, '평가손익': 0, '수익률(%)': 0, '수량': '-', '매입가': '-', '현재가': '-', '전일비': 0})

                    s_data = next((i for i in details if isinstance(i, dict) and i.get('종목명') == "[ 합  계 ]"), {})
                    s_rate = s_data.get('수익률(%)', 0)

                    total_asset_val = safe_float(a.get('총 자산', a.get('총자산', 0)))
                    safe_asset_val = 0

                    valid_investment_val = 0
                    acc_ovs_val = 0

                    for i in details:
                        if isinstance(i, dict) and i.get('종목명') != '[ 합  계 ]':
                            nm = str(i.get('종목명', '')).upper()
                            v = safe_float(i.get('총 자산', i.get('총자산', 0)))

                            if '현금' in nm or '예수금' in nm or '이율보증' in nm:
                                safe_asset_val += v

                            if '현금성자산' not in nm and '삼성' not in nm and '예수금' not in nm:
                                valid_investment_val += v
                                if any(kw in nm for kw in ['미국', 'S&P', '나스닥', '필라델피아', '다우지수', 'US', '다우존스']):
                                    acc_ovs_val += v

                    safe_pct = (safe_asset_val / total_asset_val * 100) if total_asset_val > 0 else 0
                    risk_pct = 100.0 - safe_pct if total_asset_val > 0 else 0

                    if valid_investment_val > 0:
                        acc_ovs_pct = (acc_ovs_val / valid_investment_val * 100)
                        acc_dom_pct = 100.0 - acc_ovs_pct
                    else:
                        acc_ovs_pct = 0.0
                        acc_dom_pct = 0.0

                    left_y_offset = "-8px"

                    right_block = ""
                    if k in ['DC', 'IRP']:
                        right_block = f"""
<div style='display:flex; flex-direction:column; align-items:flex-start;'>
<div style='font-size:14px; color:#555; font-weight:normal; letter-spacing:-0.3px; line-height:1.2;'>[ 🔴 위험자산 : {risk_pct:.1f}% &nbsp;/&nbsp; 🟢 안전자산 : {safe_pct:.1f}% ]</div>
<div style='display:flex; justify-content:space-between; width:100%; align-items:center; margin-top:4px;'>
<span style='font-size:12.5px; color:#888; font-weight:normal; padding-left:14px;'>국내 {acc_dom_pct:.1f}% / 해외 {acc_ovs_pct:.1f}%</span>
<span style='font-size:12.5px; color:#555; font-weight:bold;'>단위 : 원화(KRW)</span>
</div>
</div>
"""
                    else:
                        right_block = f"""
<div style='display:flex; flex-direction:column; align-items:flex-end;'>
<div style='font-size:14px; line-height:1.2; visibility:hidden;'>[ 🔴 위험자산 ]</div>
<div style='display:flex; justify-content:flex-end; width:100%; align-items:center; gap:15px; margin-top:4px;'>
<span style='font-size:12.5px; color:#888; font-weight:normal;'>국내 {acc_dom_pct:.1f}% / 해외 {acc_ovs_pct:.1f}%</span>
<span style='font-size:12.5px; color:#555; font-weight:bold;'>단위 : 원화(KRW)</span>
</div>
</div>
"""

                    st.markdown(f"""
<div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;'>
<div class='summary-text' style='margin-bottom:0; transform: translateY({left_y_offset});'>
● 총 자산 : <span class='summary-val'>{fmt(a.get('총 자산',0))}</span> KRW / 총 손익 : <span class='summary-val {col(s_data.get('평가손익',0))}'>{fmt(s_data.get('평가손익',0), True)} ({fmt_p(s_rate)})</span>
</div>
{right_block}
</div>
""", unsafe_allow_html=True)

                    code_th = "<th>종목코드</th>" if st.session_state.show_code else ""
                    th_chg = "<th>등락률</th>" if st.session_state.show_change_rate else ""

                    h3 = [f"<table class='main-table'><tr><th style='text-align:center;'>종목명</th>{code_th}<th>비중</th><th>총 자산</th><th>평가손익</th><th>손익률</th><th>주식수</th><th>매입가</th><th>현재가</th>{th_chg}</tr>"]

                    items = [i for i in details if isinstance(i, dict) and i.get('종목명') != "[ 합  계 ]"]

                    if st.session_state.sort_mode == 'asset': items.sort(key=lambda x: safe_float(x.get('총 자산', x.get('총자산', 0))), reverse=True)
                    elif st.session_state.sort_mode == 'profit': items.sort(key=lambda x: safe_float(x.get('평가손익', 0)), reverse=True)
                    elif st.session_state.sort_mode == 'rate': items.sort(key=lambda x: safe_float(x.get('수익률(%)', 0)), reverse=True)

                    for i in ([s_data] + items):
                        if not i: continue
                        is_s = (i.get('종목명') == "[ 합  계 ]")
                        row_cls = "class='sum-row'" if is_s else ""
                                       
                        raw_nm = str(i.get('종목명', '')).replace('\n', ' ')
                        orig_nm = re.sub(r'\s+', ' ', raw_nm).replace('`', '').strip()

                        if is_s:
                            nm_td = f"<td style='text-align:center; padding-left:0px;'>{orig_nm}</td>"
                        else:
                            nm_icon = "<span style='font-size:16px; margin-right:6px; vertical-align:middle;'>💵</span>" if ('예수금' in orig_nm or '현금' in orig_nm) else get_logo_html(orig_nm)
                            nm_td = f"<td style='text-align:left; padding-left:15px;'>{nm_icon}{orig_nm}</td>"

                        if st.session_state.show_code:
                            c_val = str(i.get('코드', i.get('종목코드', i.get('ticker', '-')))).strip()
                            if not c_val or c_val == '' or c_val == 'None':
                                c_val = '-'
                            td_code = f"<td>{'-' if is_s else c_val}</td>"
                        else:
                            td_code = ""

                        chg_rate = safe_float(i.get('전일비', 0))
                        curr_price_detail = safe_float(i.get('현재가', 0))
                       
                        diff_amt_detail = (curr_price_detail - (curr_price_detail / (1 + chg_rate / 100))) if curr_price_detail > 0 and chg_rate != 0 else 0

                        d_class_detail = col(chg_rate)

                        if st.session_state.show_change_rate:
                            if is_s:
                                td_chg = "<td>-</td>"
                            else:
                                td_chg = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class_detail}' style='font-size:13px;'>{fmt(diff_amt_detail, True)}</div><div class='{d_class_detail}' style='font-size:13px; font-weight:normal;'>{fmt_p(chg_rate)}</div></td>"
                        else:
                            td_chg = ""

                        h3.append(f"<tr {row_cls}>{nm_td}{td_code}<td>{i.get('비중',0):.1f}%</td><td>{fmt(i.get('총 자산',0))}</td><td class='{col(i.get('평가손익',0))}'>{fmt(i.get('평가손익',0), True)}</td><td class='{col(i.get('수익률(%)',0))}'>{fmt_p(i.get('수익률(%)',0))}</td><td>{fmt(i.get('수량','-'))}</td><td>{fmt(i.get('매입가','-'))}</td><td>{fmt(i.get('현재가','-'))}</td>{td_chg}</tr>")
                    h3.append("</table>")
                    st.markdown("".join(h3), unsafe_allow_html=True)



    # =========================================================
    # 🪴 일반계좌 대시보드 상세페이지
    # =========================================================
    elif st.session_state.current_view == '일반계좌':
        st.markdown("<h3 style='margin-top: 5px; margin-bottom: 25px;'>🚀 Andy lee님 [금융자산] 통합 대시보드</h3>", unsafe_allow_html=True)

        if not isinstance(g_data, dict):
            st.warning("데이터가 올바르지 않습니다. 좌측 사이드바의 업데이트 버튼을 눌러주세요.")
            st.stop()

        nm_table = {'DOM1': '키움증권(국내Ⅰ)', 'DOM2': '삼성증권(국내Ⅱ)', 'USA1': '키움증권(해외Ⅰ)', 'USA2': '키움증권(해외Ⅱ)'}
        nm_table_expander = {'DOM1': '키움증권(국내Ⅰ) : 6312-5329', 'DOM2': '삼성증권(국내Ⅱ) : 7162669785-01', 'USA1': '키움증권(해외Ⅰ) : 6312-5329', 'USA2': '키움증권(해외Ⅱ) : 6443-5993'}
        principals = {"DOM1": 110963075, "DOM2": 5208948, "USA1": 257915999, "USA2": 7457930}
        GEN_ACC_ORDER = ['DOM1', 'DOM2', 'USA1', 'USA2']
       
        t_asset = sum(safe_float(g_data[k].get("총자산_KRW", 0)) for k in GEN_ACC_ORDER if k in g_data and isinstance(g_data[k], dict))
        t_profit = sum(safe_float(g_data[k].get("총수익_KRW", 0)) for k in GEN_ACC_ORDER if k in g_data and isinstance(g_data[k], dict))
        t_buy_total = sum(safe_float(g_data[k].get("매입금액_KRW", 0)) for k in GEN_ACC_ORDER if k in g_data and isinstance(g_data[k], dict))
       
        t_prof_7ago = sum(safe_float(g_data[k].get("평가손익(7일전)", 0)) for k in GEN_ACC_ORDER if k in g_data and isinstance(g_data[k], dict))
        t_prof_15ago = sum(safe_float(g_data[k].get("평가손익(15일전)", 0)) for k in GEN_ACC_ORDER if k in g_data and isinstance(g_data[k], dict))
        t_prof_30ago = sum(safe_float(g_data[k].get("평가손익(30일전)", 0)) for k in GEN_ACC_ORDER if k in g_data and isinstance(g_data[k], dict))
       
        t_diff_7 = t_profit - t_prof_7ago; t_diff_15 = t_profit - t_prof_15ago; t_diff_30 = t_profit - t_prof_30ago
        t_original_sum = sum(principals.values())
        t_rate = (t_profit / t_original_sum * 100) if t_original_sum > 0 else 0

        cash_total = 0; dom_total = 0; ovs_total = 0
        dom_items = []; ovs_items = []; acc_1d_diff = {}
       
        for k in GEN_ACC_ORDER:
            acc_1d_diff[k] = 0
            if k in g_data and isinstance(g_data[k], dict):
                is_usa = 'USA' in k
                fx = safe_float(g_data.get('환율', 1443.1)) if is_usa else 1
                details = g_data[k].get('상세', [])
                if isinstance(details, list):
                    for item in details:
                        if isinstance(item, dict) and item.get('종목명') != '[ 합  계 ]':
                            it_copy = item.copy(); it_copy['계좌'] = nm_table[k]; it_copy['_k'] = k
                            val_krw = safe_float(item.get('총자산', 0)) * fx
                            nm = str(item.get('종목명', ''))
                            if nm == '예수금' or '현금' in nm: cash_total += val_krw
                            else:
                                c_p = safe_float(it_copy.get('현재가', 0)); qty = safe_float(it_copy.get('수량', 0)); d_rate = safe_float(it_copy.get('전일비', 0))
                                if c_p > 0 and d_rate != 0: acc_1d_diff[k] += ((c_p - (c_p / (1 + d_rate / 100))) * fx * qty)
                                if is_usa: ovs_total += val_krw; ovs_items.append(it_copy)
                                else: dom_total += val_krw; dom_items.append(it_copy)

        t_diff = sum(acc_1d_diff.values())
        goal_amount = 1500000000; progress_pct = (t_asset / goal_amount) * 100 if goal_amount > 0 else 0

        all_tradeable = dom_items + ovs_items
        rise_cnt = sum(1 for it in all_tradeable if safe_float(it.get('전일비', 0)) > 0.5)
        fall_cnt = sum(1 for it in all_tradeable if safe_float(it.get('전일비', 0)) < -0.5)
        flat_cnt = len(all_tradeable) - rise_cnt - fall_cnt
       
        dom_best = sorted(dom_items, key=lambda x: safe_float(x.get('수익률(%)', 0)), reverse=True)[:5]
        dom_worst = sorted([it for it in dom_items if safe_float(it.get('수익률(%)', 0)) < 5.0], key=lambda x: safe_float(x.get('수익률(%)', 0)))[:5]
        ovs_best = sorted(ovs_items, key=lambda x: safe_float(x.get('수익률(%)', 0)), reverse=True)[:5]
        ovs_worst = sorted([it for it in ovs_items if safe_float(it.get('수익률(%)', 0)) < 5.0], key=lambda x: safe_float(x.get('수익률(%)', 0)))[:5]

        total_for_bar = max(1, t_asset)
        p_dom1 = safe_float(g_data.get('DOM1', {}).get('총자산_KRW', 0)) / total_for_bar * 100 if isinstance(g_data.get('DOM1'), dict) else 0
        p_dom2 = safe_float(g_data.get('DOM2', {}).get('총자산_KRW', 0)) / total_for_bar * 100 if isinstance(g_data.get('DOM2'), dict) else 0
        p_usa1 = safe_float(g_data.get('USA1', {}).get('총자산_KRW', 0)) / total_for_bar * 100 if isinstance(g_data.get('USA1'), dict) else 0
        p_usa2 = safe_float(g_data.get('USA2', {}).get('총자산_KRW', 0)) / total_for_bar * 100 if isinstance(g_data.get('USA2'), dict) else 0

        def render_bar(p, color): return f"<div style='width: {p}%; background-color: {color}; height: 100%; display: flex; align-items: center; justify-content: center; position: relative;'><span style='position: absolute; font-size: 13px; color: #333; z-index: 10; white-space: nowrap;'>{p:.0f}%</span></div>" if p > 0 else ""

        acc_rates = sorted([(k, (safe_float(g_data[k].get('총수익_KRW',0)) / principals[k] * 100 if principals[k]>0 else 0)) for k in GEN_ACC_ORDER if k in g_data and isinstance(g_data[k], dict)], key=lambda x: x[1], reverse=True)
        best_acc_name = nm_table.get(acc_rates[0][0], "전체") if acc_rates else "전체"

        zappa_html = f"""
<div style='font-size: 14.5px; line-height: 1.85; color: #444; padding-left: 0px;'>
<div style='margin-bottom: 22px;'>
<span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'>
<span style='font-size:11px;'>🔵</span> [통합] 계좌 현황 요약
</span>
<div>현재 전체 포트폴리오 총 손익은 <span class='{col(t_profit)}'><strong>{fmt(t_profit, True)}</strong></span> (<span class='{col(t_rate)}'><strong>{fmt_p(t_rate)}</strong></span>) 이며, <strong>{best_acc_name}</strong> 계좌가 계좌별 수익률 1위를 기록 중입니다. 총 <strong>{len(all_tradeable)}개</strong> 종목 중 0.5% 초과 상승종목은 <strong>{rise_cnt}개</strong>, 하락종목은 <strong>{fall_cnt}개</strong>, 보합종목은 <strong>{flat_cnt}개</strong> 입니다.</div>
</div>
<div style='margin-bottom: 15px;'>
<span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'>
<span style='font-size:11px;'>🔵</span> [국내] 시황 및 전망
</span>
<div>최근 국내 시장은 <strong>{short_name(dom_best[0]['종목명']) if dom_best else '국내 우량주'}</strong> 등 일부 우수 종목이 상승을 견인하고 있으나, <strong>{short_name(dom_worst[0]['종목명']) if dom_worst else '일부 조정주'}</strong> 등은 조정을 받고 있습니다. 실적 기반의 리밸런싱을 권고합니다.</div>
</div>
<div style='margin-bottom: 0px;'>
<span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'>
<span style='font-size:11px;'>🔵</span> [해외] 시황 및 전망
</span>
<div>미국 증시는 <strong>{short_name(ovs_best[0]['종목명']) if ovs_best else '빅테크 우량주'}</strong> 위주로 긍정적 흐름을 보이나, <strong>{short_name(ovs_worst[0]['종목명']) if ovs_worst else '단기 하락주'}</strong> 등 부진 섹터는 비중 조절이 필요합니다. 현재 <strong>{(cash_total/t_asset*100) if t_asset>0 else 0:.1f}%</strong>인 현금성(예수금) 비중을 유동적으로 관리하시기 바랍니다.</div>
</div>
</div>
"""

        st.markdown("<div class='sub-title' style='margin-bottom: 15px;'>🪴 [일반계좌] 자산 현황 요약</div>", unsafe_allow_html=True)
       
        p_cash_donut = (cash_total/t_asset*100) if t_asset>0 else 0
        p_ovs_donut = (ovs_total/t_asset*100) if t_asset>0 else 0
        p_dom_donut = (dom_total/t_asset*100) if t_asset>0 else 0
       
        donut_css = f"background: conic-gradient(#ffffff 0% {p_cash_donut}%, #d9d9d9 {p_cash_donut}% {p_cash_donut+p_ovs_donut}%, #8c8c8c {p_cash_donut+p_ovs_donut}% 100%);"
        donut_html = f"""
<div style='position: relative; width: 120px; height: 120px; border-radius: 50%; {donut_css} box-shadow: inset 0 0 8px rgba(0,0,0,0.1); border: 1px solid #d0d0d0; flex-shrink: 0; margin: 0 auto;'>
<div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 35%; height: 35%; background-color: #fffdf2; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.05);'></div>
<div style='position: absolute; top: 0%; left: 50%; transform: translateX(-50%); font-size: 12.5px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_cash_donut:.0f}%<br>현금성자산</div>
<div style='position: absolute; top: 55px; right: -15px; font-size: 14px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_ovs_donut:.0f}%<br>해외투자</div>
<div style='position: absolute; bottom: 42px; left: -20px; font-size: 14px; color: #fff; font-weight: bold; text-align: center; line-height: 1.1; text-shadow: 0px 0px 3px rgba(0,0,0,0.5);'>{p_dom_donut:.0f}%<br>국내투자</div>
</div>
"""

        html_parts = []
        html_parts.append("""
<div style='text-align: right; font-size: 13px; color: #555; font-weight: bold; margin-bottom: 5px;'>단위 : 원화(KRW)</div>
<div class='insight-container'>
<div class='insight-left'>
<div class='card-main'>
<div style='display: flex; gap: 15px; align-items: stretch; margin-bottom: auto;'>
<div style='flex: 0 0 38%; display: flex; flex-direction: column; align-items: center;'>
<div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 15px; width:100%; text-align:left;'>💡총 자산</div>
""")
        html_parts.append(donut_html)
        html_parts.append(f"""
<div style='font-size: 13.5px; color: #333; font-weight: bold; margin-top: 14px;'>
<span style='font-size: 12.5px; color: #666;'>원금</span> : {fmt(t_original_sum)}
</div>
</div>
<div style='flex: 1; display: flex; flex-direction: column; justify-content: flex-start; padding-top: 5px;'>
<div class='card-inner' style='padding: 10px 12px; margin-bottom: 8px;'>
<div style='font-size: 24px; font-weight: 700 !important; color: #111; letter-spacing: normal; line-height: 1; margin-bottom: 6px;'>
{fmt(t_asset)}<span style='font-size: 13.5px; font-weight: normal; margin-left: 3px; letter-spacing: normal;'>KRW</span>
</div>
<div style='font-size: 13.5px; color: #777; font-weight: normal; line-height: 1;'>
[ 전일비 <span class='{col(t_diff)}'>{fmt(t_diff, True)}</span> / 전주비 <span class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</span> ]
</div>
</div>
<div style='display: grid; grid-template-columns: auto auto; row-gap: 12px; column-gap: 30px; justify-content: end; align-items: baseline; width: 100%; padding-right: 12px; margin-top: 8px;'>
<div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>평가금액</div>
<div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(t_asset - cash_total)}</div>
<div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>현금성(예수금)</div>
<div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(cash_total)}</div>
<div style='color: #777; font-size: 14px; font-weight: normal; text-align: right; line-height: 20px;'>총 손익</div>
<div style='text-align: right;'>
<div style='font-size: 18px; font-weight: 600; line-height: 1;' class='{col(t_profit)}'>{fmt(t_profit, True)}</div>
<div style='font-size: 13.5px; font-weight: 600; margin-top: 3px; line-height: 1;' class='{col(t_rate)}'>{fmt_p(t_rate)}</div>
</div>
</div>
</div>
</div>
<div style='margin-top: 20px;'>
<div style='display: flex; height: 20px; width: 100%; border-radius: 4px; border: 1px solid #ccc; margin-bottom: 6px; overflow: hidden;'>
{render_bar(p_dom1, '#b4a7d6')}{render_bar(p_dom2, '#f4b183')}{render_bar(p_usa1, '#a9d18e')}{render_bar(p_usa2, '#ffd966')}
</div>
<div style='display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #777; padding: 0 2px; margin-bottom: 16px;'>
<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#b4a7d6; border-radius:3px;'></div>키움증권(국내Ⅰ)</div>
<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#f4b183; border-radius:3px;'></div>삼성증권(국내Ⅱ)</div>
<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#a9d18e; border-radius:3px;'></div>키움증권(해외Ⅰ)</div>
<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#ffd966; border-radius:3px;'></div>키움증권(해외Ⅱ)</div>
</div>
<div style='padding: 10px 15px; background: rgba(255,255,255,0.5); border-radius: 10px; border: 1px solid #e8dbad;'>
<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>
<span style='font-size: 14px; color: #777; font-weight: normal;'>🎯 주식투자 자산 15억 프로젝트</span>
<div style='text-align: right;'><span style='font-size: 14px; font-weight: bold; color: #4a90e2;'>{progress_pct:.1f}%</span></div>
</div>
<div style='width: 100%; height: 6px; background-color: #e2e2e2; border-radius: 3px; overflow: hidden;'>
<div style='width: {progress_pct}%; height: 100%; background: linear-gradient(90deg, #9bc2e6, #4a90e2);'></div>
</div>
</div>
</div>
</div>
</div>
<div class='insight-right'>
<div class='grid-2x2'>
""")
        for k in GEN_ACC_ORDER:
            if k in g_data and isinstance(g_data[k], dict):
                a = g_data[k]
                acc_num_map = {'DOM1': '[ 6312-5329 ]', 'DOM2': '[ 7162669785-01 ]', 'USA1': '[ 6312-5329 ]', 'USA2': '[ 6443-5993 ]'}
                details = a.get('상세', [])
                item_count = len([i for i in details if isinstance(i, dict) and str(i.get('종목명', '')) not in ['[ 합  계 ]', '예수금', '현금성자산', '현금성자산(예수금)']]) if isinstance(details, list) else 0
               
                html_parts.append(f"""
<a href='#gen_detail_section' style='text-decoration:none; color:inherit; display:block; height:100%;'>
<div class='card-sub' style='height:100%; justify-content:space-between;'>
<div>
<div style='text-align: right; font-size: 13.5px; color: #666; font-weight: normal; margin-bottom: -2px; line-height: 1;'>{acc_num_map[k]}</div>
<div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 2px;'>{nm_table[k]}</div>
<div style='border-bottom: 1px solid #eee; margin-bottom: 6px; margin-top: 2px;'></div>
<div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'>
<span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 자산</span>
<span style='font-size: 16px; color: #111; font-weight: normal;'>{fmt(safe_float(a.get('총자산_KRW', 0)))}</span>
</div>
<div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'>
<span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 손익</span>
<div style='text-align: right; line-height: 1.2;'>
<div class='{col(a.get('총수익_KRW', 0))}' style='font-size: 16px; font-weight: normal;'>{fmt(safe_float(a.get('총수익_KRW', 0)), True)}</div>
<div class='{col(safe_float(a.get('총수익_KRW',0))/principals[k]*100 if principals[k] else 0)}' style='font-size: 14px; font-weight: normal; margin-top: 1px;'>{fmt_p(safe_float(a.get('총수익_KRW',0))/principals[k]*100 if principals[k] else 0)}</div>
</div>
</div>
</div>
<div style='font-size: 13.5px; color: #666; font-weight: normal; margin-top: auto; padding-top: 2px; display: flex; justify-content: space-between; align-items: baseline;'>
<span>* <span style='font-size: 12.5px;'>원금</span> : {fmt(principals[k])}</span>
<span><span style='font-size: 16px; font-weight: bold; color: #111;'>{item_count}</span> 종목</span>
</div>
</div>
</a>
""")
        html_parts.append("</div></div></div>")
       
        html_parts.append("""
<div class='insight-bottom-box' style='display: flex; gap: 20px; align-items: stretch;'>
<div style='flex: 1; padding-right: 15px; border-right: 1px solid #eaeaea;'>
<div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; letter-spacing: normal;'>📈 [국내] 손익률 우수종목</div>
<table class='main-table' style='margin-bottom: 20px;'>
<tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>등락률</th></tr>
""")
        for idx, it in enumerate(dom_best):
            c_p = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0)); diff_amt = (c_p - (c_p / (1 + d_rate / 100))) if c_p > 0 and d_rate != 0 else 0
            d_class = col(d_rate); diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
            acc_tag = f"<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({it.get('계좌', '')})</span>"
           
            orig_nm = str(it.get('종목명', '')).replace('\n', '').replace('\r', '').strip()
            disp_nm = short_name(orig_nm); logo_html = get_logo_html(orig_nm)
            nm_html = f"<td style='line-height:1.3; padding-top:6px; padding-bottom:6px; text-align:left; padding-left:10px;'>{logo_html}{disp_nm}{acc_tag}</td>"
            html_parts.append(f"<tr><td>{idx+1}</td>{nm_html}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td>{diff_html}</tr>")
       
        html_parts.append("""
</table>
<div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px; letter-spacing: normal;'>📉 [국내] 손익률 부진종목</div>
<table class='main-table' style='margin-bottom: 25px;'>
<tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>등락률</th></tr>
""")
        for idx, it in enumerate(dom_worst):
            c_p = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0)); diff_amt = (c_p - (c_p / (1 + d_rate / 100))) if c_p > 0 and d_rate != 0 else 0
            d_class = col(d_rate); diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
            acc_tag = f"<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({it.get('계좌', '')})</span>"
           
            orig_nm = str(it.get('종목명', '')).replace('\n', '').replace('\r', '').strip()
            disp_nm = short_name(orig_nm); logo_html = get_logo_html(orig_nm)
            nm_html = f"<td style='line-height:1.3; padding-top:6px; padding-bottom:6px; text-align:left; padding-left:10px;'>{logo_html}{disp_nm}{acc_tag}</td>"
            html_parts.append(f"<tr><td>{idx+1}</td>{nm_html}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td>{diff_html}</tr>")
       
        html_parts.append("""
</table>
<hr style='border:0; border-top:1px dashed #ddd; margin: 25px 0;'>
""")
       
        fx_rate = safe_float(g_data.get('환율', 1443.1))
        html_parts.append("""
<div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; letter-spacing: normal;'>📈 [해외] 손익률 우수종목</div>
<table class='main-table' style='margin-bottom: 20px;'>
<tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익(KRW)</th><th>등락률</th></tr>
""")
        for idx, it in enumerate(ovs_best):
            c_p = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0)); diff_amt = (c_p - (c_p / (1 + d_rate / 100))) * fx_rate if c_p > 0 and d_rate != 0 else 0
            d_class = col(d_rate); diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
            acc_tag = f"<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({it.get('계좌', '')})</span>"
           
            orig_nm = str(it.get('종목명', '')).replace('\n', '').replace('\r', '').strip()
            disp_nm = short_name(orig_nm); logo_html = get_logo_html(orig_nm)
            nm_html = f"<td style='line-height:1.3; padding-top:6px; padding-bottom:6px; text-align:left; padding-left:10px;'>{logo_html}{disp_nm}{acc_tag}</td>"
            html_parts.append(f"<tr><td>{idx+1}</td>{nm_html}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(safe_float(it.get('평가손익', 0))*fx_rate)}'>{fmt(safe_float(it.get('평가손익', 0))*fx_rate, True)}</td>{diff_html}</tr>")
       
        html_parts.append("""
</table>
<div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px; letter-spacing: normal;'>📉 [해외] 손익률 부진종목</div>
<table class='main-table' style='margin-bottom: 0px;'>
<tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익(KRW)</th><th>등락률</th></tr>
""")
        for idx, it in enumerate(ovs_worst):
            c_p = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0)); diff_amt = (c_p - (c_p / (1 + d_rate / 100))) * fx_rate if c_p > 0 and d_rate != 0 else 0
            d_class = col(d_rate); diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
            acc_tag = f"<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({it.get('계좌', '')})</span>"
           
            orig_nm = str(it.get('종목명', '')).replace('\n', '').replace('\r', '').strip()
            disp_nm = short_name(orig_nm); logo_html = get_logo_html(orig_nm)
            nm_html = f"<td style='line-height:1.3; padding-top:6px; padding-bottom:6px; text-align:left; padding-left:10px;'>{logo_html}{disp_nm}{acc_tag}</td>"
            html_parts.append(f"<tr><td>{idx+1}</td>{nm_html}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(safe_float(it.get('평가손익', 0))*fx_rate)}'>{fmt(safe_float(it.get('평가손익', 0))*fx_rate, True)}</td>{diff_html}</tr>")
       
        html_parts.append(f"""
</table>
</div>
<div style='flex: 1.1; padding-left: 5px;'>
<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 8px;'>
<div style='font-size: 18px; font-weight: bold; color: #111; letter-spacing: normal;'>💡 시황 및 향후 전망</div>
<div style='font-size: 13.5px; color: #888;'>[ -0.5%p < 보합 < +0.5%p ]</div>
</div>
{zappa_html}
</div>
</div>
""")
        st.markdown("".join(html_parts), unsafe_allow_html=True)

        unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"

        # [1], [2]번 표를 위한 별도의 정렬 배열 생성 (gen_sort_mode에 따라 정렬됨)
        sorted_gen_order = list(GEN_ACC_ORDER)
        if st.session_state.gen_sort_mode == 'asset':
            sorted_gen_order.sort(key=lambda k: safe_float(g_data.get(k, {}).get('총자산_KRW', 0)) if isinstance(g_data.get(k), dict) else -float('inf'), reverse=True)
        elif st.session_state.gen_sort_mode == 'profit':
            sorted_gen_order.sort(key=lambda k: safe_float(g_data.get(k, {}).get('총수익_KRW', 0)) if isinstance(g_data.get(k), dict) else -float('inf'), reverse=True)
        elif st.session_state.gen_sort_mode == 'rate':
            def gen_rate_for_sort(k):
                if not isinstance(g_data.get(k), dict): return -float('inf')
                prin = principals.get(k, 0)
                prof = safe_float(g_data[k].get('총수익_KRW', 0))
                return (prof / prin * 100) if prin > 0 else 0
            sorted_gen_order.sort(key=gen_rate_for_sort, reverse=True)

        st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(t_profit)}'>{fmt(t_profit, True)} ({fmt_p(t_rate)})</span></div></div>", unsafe_allow_html=True)

        h1_table = """
<table class='main-table'>
<tr>
<th rowspan='2'>계좌 구분</th>
<th rowspan='2'>총 자산</th>
<th rowspan='2' class='th-eval'>평가손익</th>
<th colspan='3' class='th-blank'>&nbsp;</th>
<th rowspan='2'>손익률</th>
<th rowspan='2'>투자원금</th>
</tr>
<tr>
<th class='th-week'>7일전</th>
<th class='th-week'>15일전</th>
<th class='th-week'>30일전</th>
</tr>
"""
        h1 = [unit_html, h1_table, f"""
<tr class='sum-row'>
<td>[ 합  계 ]</td>
<td>{fmt(t_asset)}</td>
<td class='{col(t_profit)}'>{fmt(t_profit, True)}</td>
<td class='{col(t_prof_7ago)}'>{fmt(t_prof_7ago, True)}</td>
<td class='{col(t_prof_15ago)}'>{fmt(t_prof_15ago, True)}</td>
<td class='{col(t_prof_30ago)}'>{fmt(t_prof_30ago, True)}</td>
<td class='{col(t_rate)}'>{fmt_p(t_rate)}</td>
<td>{fmt(t_original_sum)}</td>
</tr>
"""]
        for k in sorted_gen_order:
            if k in g_data and isinstance(g_data[k], dict):
                a = g_data[k]
                a_tot = safe_float(a.get('총자산_KRW',0)); a_prof = safe_float(a.get('총수익_KRW',0))
                p7 = safe_float(a.get('평가손익(7일전)',0)); p15 = safe_float(a.get('평가손익(15일전)',0)); p30 = safe_float(a.get('평가손익(30일전)',0))
                h1.append(f"""
<tr>
<td>{nm_table[k]}</td>
<td>{fmt(a_tot)}</td>
<td class='{col(a_prof)}'>{fmt(a_prof, True)}</td>
<td class='{col(p7)}'>{fmt(p7, True)}</td>
<td class='{col(p15)}'>{fmt(p15, True)}</td>
<td class='{col(p30)}'>{fmt(p30, True)}</td>
<td class='{col(a_prof/principals[k]*100 if principals[k] else 0)}'>{fmt_p(a_prof/principals[k]*100 if principals[k] else 0)}</td>
<td>{fmt(principals[k])}</td>
</tr>
""")
        h1.append("</table>")
        st.markdown("".join(h1), unsafe_allow_html=True)

        ag_tot = t_asset - t_buy_total
        ay_tot = (ag_tot / t_buy_total * 100) if t_buy_total > 0 else 0
        st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(ag_tot)}'>{fmt(ag_tot, True)} ({fmt_p(ay_tot)})</span></div>", unsafe_allow_html=True)

        h2_table = """
<table class='main-table'>
<tr>
<th rowspan='2'>계좌 구분</th>
<th rowspan='2'>총 자산</th>
<th rowspan='2' class='th-eval'>평가손익</th>
<th colspan='3' class='th-blank'>&nbsp;</th>
<th rowspan='2'>손익률</th>
<th rowspan='2'>매입금액</th>
</tr>
<tr>
<th class='th-week'>전일비</th>
<th class='th-week'>전주비</th>
<th class='th-week'>전월비</th>
</tr>
"""
        h2 = [unit_html, h2_table, f"""
<tr class='sum-row'>
<td>[ 합  계 ]</td>
<td>{fmt(t_asset)}</td>
<td class='{col(ag_tot)}'>{fmt(ag_tot, True)}</td>
<td class='{col(t_diff)}'>{fmt(t_diff, True)}</td>
<td class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</td>
<td class='{col(t_diff_30)}'>{fmt(t_diff_30, True)}</td>
<td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td>
<td>{fmt(t_buy_total)}</td>
</tr>
"""]
       
        for k in sorted_gen_order:
            if k in g_data and isinstance(g_data[k], dict):
                a = g_data[k]
                buy_krw = safe_float(a.get('매입금액_KRW', 0))
                ag_acc = safe_float(a.get('총자산_KRW', 0)) - buy_krw
                ay_acc = (ag_acc / buy_krw * 100) if buy_krw > 0 else 0
                a_prof = safe_float(a.get('총수익_KRW', 0))
                diff_7_acc = a_prof - safe_float(a.get('평가손익(7일전)', 0))
                diff_30_acc = a_prof - safe_float(a.get('평가손익(30일전)', 0))
                h2.append(f"""
<tr>
<td>{nm_table[k]}</td>
<td>{fmt(safe_float(a.get('총자산_KRW',0)))}</td>
<td class='{col(ag_acc)}'>{fmt(ag_acc, True)}</td>
<td class='{col(acc_1d_diff.get(k, 0))}'>{fmt(acc_1d_diff.get(k, 0), True)}</td>
<td class='{col(diff_7_acc)}'>{fmt(diff_7_acc, True)}</td>
<td class='{col(diff_30_acc)}'>{fmt(diff_30_acc, True)}</td>
<td class='{col(ay_acc)}'>{fmt_p(ay_acc)}</td>
<td>{fmt(buy_krw)}</td>
</tr>
""")
        h2.append("</table>")
        st.markdown("".join(h2), unsafe_allow_html=True)

         # =========================================================
        # 🪴 일반계좌 [플로팅 메뉴 정밀 튜닝]
        # =========================================================
        st.markdown("<div id='gen_detail_section' style='padding-top: 20px; margin-top: -20px;'></div><div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
       
        # 💡 [안전장치] 변수명 초기화 누락으로 인한 렌더링 중단(빈 캡슐 현상) 완벽 차단
        if 'gen_sort_mode' not in st.session_state: st.session_state.gen_sort_mode = 'init'
        if 'gen_show_change_rate' not in st.session_state: st.session_state.gen_show_change_rate = False

        # 💡 [Andy님 솔루션 적용] CSS 굵기를 700으로 상향하여 Streamlit 활성 버튼 두께와 100% 동기화
        st.markdown("""
<style>
/* 모든 버튼 내부의 강조(**) 태그를 검정색 + Streamlit 네이티브 굵기(700)로 완벽 고정 */
.stButton strong, .stButton b, button strong, button b {
color: #111111 !important;
font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

        b1, b2, b3, b4, b5, b6 = st.columns(6)
       
        with b1:
            st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
            lbl1 = "🔽**정렬 [** 초기화(●)" if st.session_state.gen_sort_mode == 'init' else "🔽**정렬 [** 초기화(○)"
            if st.button(lbl1, type="primary" if st.session_state.gen_sort_mode == 'init' else "secondary", key='gen_btn1', on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'init')): pass
           
        with b2:
            lbl2 = "총자산(●)" if st.session_state.gen_sort_mode == 'asset' else "총자산(○)"
            if st.button(lbl2, type="primary" if st.session_state.gen_sort_mode == 'asset' else "secondary", key='gen_btn2', on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'asset')): pass
           
        with b3:
            lbl3 = "평가손익(●)" if st.session_state.gen_sort_mode == 'profit' else "평가손익(○)"
            if st.button(lbl3, type="primary" if st.session_state.gen_sort_mode == 'profit' else "secondary", key='gen_btn3', on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'profit')): pass
           
        with b4:
            lbl4 = "손익률(●) **]**" if st.session_state.gen_sort_mode == 'rate' else "손익률(○) **]**"
            if st.button(lbl4, type="primary" if st.session_state.gen_sort_mode == 'rate' else "secondary", key='gen_btn4', on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'rate')): pass
           
        with b5:
            # 💡 찌꺼기 방지: 마크다운(**) 제거
            lbl5 = "↕️등락률[+]" if st.session_state.gen_show_change_rate else "↕️등락률[-]"
            if st.button(lbl5, type="primary" if st.session_state.gen_show_change_rate else "secondary", key='gen_btn5', on_click=lambda: setattr(st.session_state, 'gen_show_change_rate', not st.session_state.gen_show_change_rate)): pass
           
        with b6:
            # 💡 찌꺼기 방지: 마크다운(**) 제거
            lbl6 = "💻종목코드[+]" if st.session_state.show_code else "💻종목코드[-]"
            if st.button(lbl6, type="primary" if st.session_state.show_code else "secondary", key='gen_btn6', on_click=lambda: setattr(st.session_state, 'show_code', not st.session_state.show_code)): pass

        st.markdown("<br>", unsafe_allow_html=True)

        # [3]번 섹션은 고정된 순서(GEN_ACC_ORDER)를 그대로 사용
        for k in GEN_ACC_ORDER:
            if k in g_data and isinstance(g_data[k], dict):
                a = g_data[k]
                is_usa = 'USA' in k
                with st.expander(f"📂 [ {nm_table_expander[k]} ] 종목별 현황", expanded=False):
                    details = a.get('상세', [])
                   
                    s_data = next((i for i in details if isinstance(i, dict) and i.get('종목명') == "[ 합  계 ]"), {}) if isinstance(details, list) else {}
                    s_rate = s_data.get('수익률(%)', 0)
                    curr_asset = safe_float(a.get('총자산_KRW', 0)); a_prof = safe_float(a.get('총수익_KRW', 0))
                    rate_val = safe_float(g_data.get('환율', 1443.1))
                   
                    if is_usa:
                        import pytz
                        from datetime import datetime
                        now_seoul = datetime.now(pytz.timezone('Asia/Seoul'))
                        d_str_clean = f"{now_seoul.month}/{now_seoul.day}"
                        dw_str = ["월", "화", "수", "목", "금", "토", "일"][now_seoul.weekday()]
                       
                        st.markdown(f"""
<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:0px;'>
<div class='summary-text' style='margin-bottom:0;'>
● 총 자산 : <span class='summary-val'>{fmt(curr_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(a_prof)}'>{fmt(a_prof, True)} ({fmt_p(s_rate)})</span>
</div>
<div style='font-size:12.5px; color:#555; font-weight:normal; padding-bottom:4px;'>
[ {d_str_clean}({dw_str}), 적용환율 1$ = {rate_val:,.1f} ]
</div>
</div>
""", unsafe_allow_html=True)
                       
                        u_c1, u_c2 = st.columns([8.8, 1.2])
                        with u_c2:
                            currency_mode = st.selectbox("표기단위", options=["[원화(KRW)]", "[달러(USD)]", "[원화/달러]"], index=2, label_visibility="collapsed", key=f"curr_sel_box_{k}")
                    else:
                        currency_mode = "[원화(KRW)]"
                        left_y_offset = "-8px"
                        right_block = f"""
<div style='display:flex; flex-direction:column; align-items:flex-end;'>
<div style='font-size:14px; line-height:1.2; visibility:hidden;'>[ 🔴 위험자산 ]</div>
<div style='display:flex; justify-content:flex-end; width:100%; align-items:center; gap:15px; margin-top:4px;'>
<span style='font-size:12.5px; color:#555; font-weight:bold;'>단위 : 원화(KRW)</span>
</div>
</div>
"""
                       
                        st.markdown(f"""
<div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;'>
<div class='summary-text' style='margin-bottom:0; transform: translateY({left_y_offset});'>
● 총 자산 : <span class='summary-val'>{fmt(curr_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(a_prof)}'>{fmt(a_prof, True)} ({fmt_p(s_rate)})</span>
</div>
{right_block}
</div>
""", unsafe_allow_html=True)
                   
                    code_th = "<th>종목코드</th>" if st.session_state.show_code else ""
                    th_chg = "<th>등락률</th>" if st.session_state.gen_show_change_rate else ""
                   
                    h3 = [f"<table class='main-table'><tr><th style='text-align:center;'>종목명</th>{code_th}<th>비중</th><th>총 자산</th><th>평가손익</th><th>손익률</th><th>주식수</th><th>매입가</th><th>현재가</th>{th_chg}</tr>"]
                   
                    items = [i for i in details if isinstance(i, dict) and i.get('종목명') not in ["[ 합  계 ]", "예수금"]] if isinstance(details, list) else []
                    cash_item = next((i for i in details if isinstance(i, dict) and i.get('종목명') == "예수금"), {"종목명": "예수금", "총자산": 0, "평가손익": 0, "수익률(%)": 0, "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0}) if isinstance(details, list) else {}
                   
                    if st.session_state.gen_sort_mode == 'asset': items.sort(key=lambda x: safe_float(x.get('총자산', 0)), reverse=True)
                    elif st.session_state.gen_sort_mode == 'profit': items.sort(key=lambda x: safe_float(x.get('평가손익', 0)), reverse=True)
                    elif st.session_state.gen_sort_mode == 'rate': items.sort(key=lambda x: safe_float(x.get('수익률(%)', 0)), reverse=True)
                   
                    def fmt_dual(val_raw, sign=False):
                        if val_raw == '-': return '-'
                        if not is_usa: return fmt(val_raw, sign)
                        val_krw = safe_float(val_raw) * rate_val
                        s_krw = fmt(val_krw, sign); s_usd = fmt(safe_float(val_raw), sign, decimal=4)
                        if currency_mode == "[원화/달러]": return f"{s_krw}<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({s_usd})</span>"
                        elif currency_mode == "[달러(USD)]": return s_usd
                        else: return s_krw

                    for i in ([s_data] + items + [cash_item]):
                        if not i: continue
                        if i.get('종목명') == "예수금" and safe_float(i.get('총자산', 0)) == 0 and k != 'USA2' and safe_float(s_data.get('총자산', 0)) > 0:
                            continue
                           
                        is_s = (i.get('종목명') == "[ 합  계 ]")
                        row = f"<tr class='sum-row'>" if is_s else "<tr>"
                       
                        raw_nm = '피그마' if i.get('종목명') == 'Figma' else str(i.get('종목명', ''))
                        orig_nm = raw_nm.replace('\n', ' ').replace('\r', '').replace('`', '').strip()
                       
                        if is_s:
                            row += f"<td style='text-align:center; padding-left:0px;'>{orig_nm}</td>"
                        else:
                            nm_icon = "<span style='font-size:16px; margin-right:6px; vertical-align:middle;'>💵</span>" if ('예수금' in orig_nm or '현금' in orig_nm) else get_logo_html(orig_nm)
                            row += f"<td style='text-align:left; padding-left:15px;'>{nm_icon}{orig_nm}</td>"
                       
                        if st.session_state.show_code: row += f"<td>{'-' if is_s or i.get('코드','-')=='-' else i.get('코드', '')}</td>"
                       
                        ia = fmt_dual(i.get('총자산', 0)); ip = fmt_dual(i.get('평가손익', 0), True)
                        ibuy = fmt_dual(i.get('매입가', '-')); icurr = fmt_dual(i.get('현재가', '-'))
                        s_tot = safe_float(s_data.get('총자산', 1))
                        pct = (safe_float(i.get('총자산', 0)) / s_tot * 100) if s_tot > 0 else 0
                       
                        d_rate = safe_float(i.get('전일비', 0)); curr_price = safe_float(i.get('현재가', 0))
                        diff_amt_raw = (curr_price - (curr_price / (1 + d_rate / 100))) if curr_price > 0 and d_rate != 0 else 0
                        diff_amt_str = fmt_dual(diff_amt_raw, True) if diff_amt_raw != 0 else "0"
                        d_rate_str = "-" if is_s else fmt_p(d_rate); d_class = "" if is_s else col(d_rate)
                       
                        row += f"<td>{pct:.1f}%</td><td>{ia}</td><td class='{col(i.get('평가손익', 0))}'>{ip}</td><td class='{col(i.get('수익률(%)', 0))}'>{fmt_p(i.get('수익률(%)', 0))}</td><td>{fmt(i.get('수량', '-'))}</td><td>{ibuy}</td><td>{icurr}</td>"
                       
                        if st.session_state.gen_show_change_rate:
                            if is_s or i.get('종목명') == '예수금':
                                row += "<td>-</td>"
                            else:
                                row += f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{diff_amt_str}</div><div class='{d_class}' style='font-size:13px; font-weight:normal;'>{d_rate_str}</div></td>"
                        row += "</tr>"
                        h3.append(row)
                    h3.append("</table>")
                    st.markdown("".join(h3), unsafe_allow_html=True)
    # =========================================================
    # 🪙 암호화폐 상세 화면
    # =========================================================
    elif st.session_state.current_view == '암호화폐':
        # 💡 [패치] 암호화폐 전용 세션 상태 초기화
        if 'cryp_sort_mode' not in st.session_state: st.session_state.cryp_sort_mode = 'init'
        if 'cryp_show_change_rate' not in st.session_state: st.session_state.cryp_show_change_rate = False

        st.markdown("<h3 style='margin-top: 5px; margin-bottom: 25px;'>🚀 Andy lee님 [금융자산] 통합 대시보드</h3>", unsafe_allow_html=True)
        st.markdown("<div class='sub-title' style='margin-bottom: 15px;'>🪙 [암호화폐] 자산 현황 요약</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: right; font-size: 13px; color: #555; font-weight: bold; margin-bottom: 5px;'>단위 : 원화(KRW)</div>", unsafe_allow_html=True)

        if isinstance(crypto_data, dict) and 'total_asset' in crypto_data:
            ca = safe_float(crypto_data.get('total_asset', 0))
            ck = safe_float(crypto_data.get('total_krw', 0))
            ce = ca - ck
            cb = safe_float(crypto_data.get('total_buy', 0)) - ck
            cp = ce - cb
            cr = (cp / cb * 100) if cb > 0 else 0
            total_principal = cb + ck

            pie_items = []
            cl = crypto_data.get('coins', [])
            if isinstance(cl, list):
                for c in cl:
                    if isinstance(c, dict) and c.get('ticker') != 'KRW':
                        pie_items.append({'name': c.get('ticker'), 'val': safe_float(c.get('eval', 0))})
            if ck > 0: pie_items.append({'name': 'KRW', 'val': ck})

            order_map = {'BTC': 1, 'ETH': 2, 'SOL': 3, 'XRP': 4, 'KRW': 999}
            def get_sort_key(x):
                nm = x['name']
                if nm in order_map:
                    return (order_map[nm], -x['val'])
                return (500, -x['val'])
           
            pie_items.sort(key=get_sort_key)

            c_m = {'BTC': '#f4b183', 'ETH': '#b4a7d6', 'SOL': '#a9d18e', 'XRP': '#ffd966', 'KRW': '#9bc2e6'}
            d_c = ['#e2d5f8', '#fce5cd', '#d9ead3', '#fff2cc', '#c9daf8']

            grad, leg, labels_html = [], "", ""
            curr_p = 0

            color_idx = 0
            for it in pie_items:
                p = (it['val'] / ca * 100) if ca > 0 else 0
                if it['name'] in c_m: clr = c_m[it['name']]
                else:
                    clr = d_c[color_idx % len(d_c)]
                    color_idx += 1
               
                grad.append(f"{clr} {curr_p}% {curr_p + p}%")
           
                disp_nm_map = {'BTC': '비트코인(BTC)', 'ETH': '이더리움(ETH)', 'SOL': '솔라나(SOL)', 'XRP': '엑스알피(XRP)', 'KRW': '현금성자산'}
                display_name = disp_nm_map.get(it['name'], it['name'])
           
                leg += f"<div style='display:flex; align-items:center; justify-content:space-between; width:165px; font-size:14px; color:#666; font-weight:500; margin-bottom: 4px;'><div style='display:flex; align-items:center; gap:6px;'><div style='width:12px; height:12px; background-color:{clr}; border-radius:3px;'></div>{display_name}</div> <span style='font-weight:600;'>{p:.1f}%</span></div>"
           
                if p > 3:
                    mid_angle = (curr_p + p / 2) / 100 * 360
                    rad = np.radians(mid_angle - 90)
                    x = 80 + 55 * np.cos(rad)
                    y = 80 + 55 * np.sin(rad)
                    f_size = "14px" if it['name'] in ['BTC', 'ETH'] else "12.5px"
                    labels_html += f"<div style='position:absolute; left:{x}px; top:{y}px; transform:translate(-50%, -50%); font-size:{f_size}; font-weight:bold; color:#fff; text-shadow:1px 1px 2px rgba(0,0,0,0.8); z-index:10;'>{p:.1f}%</div>"
                curr_p += p
           
            conic_str = ", ".join(grad)

            donut_html = f"""
<div style='display:flex; flex-direction:row; align-items:flex-start; gap:40px;'>
<div style='display:flex; flex-direction:column; align-items:center;'>
<div style='position: relative; width: 160px; height: 160px; border-radius: 50%; background: conic-gradient({conic_str}); border: 1px solid #ddd; flex-shrink: 0;'>
{labels_html}
<div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 45%; height: 45%; background-color: #fff; border-radius: 50%; display:flex; align-items:center; justify-content:center; text-align:center;'>
<span style='font-size:12.5px; color:#333; font-weight:bold; line-height:1.2;'>보유 비중<br>(%)</span>
</div>
</div>
<div style='font-size:15.5px; font-weight:bold; color:#444; margin-top:15px;'>원금 : {fmt(total_principal)}</div>
</div>
<div style='display:flex; flex-direction:column; justify-content:center; height:160px; gap:4px;'>
{leg}
</div>
</div>
"""

            top_box = f"""
<div class='card-main' style='width:100%; display:flex; flex-direction:row; align-items:stretch; padding:35px 50px; background-color:#ffffff; border:1px solid #ddd; border-radius:15px; margin-bottom:30px;'>
<div style='flex: 1; border-right: 1px solid #eee; padding-right: 30px;'>
<div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 20px;'>📊 암호화폐 비중</div>
{donut_html}
</div>
<div style='flex: 1; padding-left: 40px;'>
<div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 12px; text-align: left;'>💡 총 보유자산</div>
<div class='card-inner' style='padding: 10px 12px; margin-bottom: 15px; text-align: right;'>
<div style='font-size: 24px; font-weight: 700 !important; color: #111; letter-spacing: normal; line-height: 1; margin-bottom: 6px;'>
{fmt(ca)}<span style='font-size: 13.5px; font-weight: normal; margin-left: 3px; letter-spacing: normal;'>KRW</span>
</div>
<div style='font-size: 13.5px; color: #777; font-weight: normal; line-height: 1;'>
[ 총 손익 <span class='{col(cp)}'>{fmt(cp, True)}</span> / 손익률 <span class='{col(cr)}'>{fmt_p(cr)}</span> ]
</div>
</div>
<div style='background:#f9f9f9; padding:18px 20px; border-radius:10px; display:flex; flex-direction:column; gap:14px;'>
<div style='display:flex; justify-content:space-between; align-items:baseline;'>
<span style='color: #777; font-size: 14px; font-weight: normal; line-height: 20px;'>평가금액</span>
<span style='color: #111; font-size: 18px; font-weight: 400; line-height: 20px;'>{fmt(ce)}</span>
</div>
<div style='display:flex; justify-content:space-between; align-items:baseline;'>
<span style='color: #777; font-size: 14px; font-weight: normal; line-height: 20px;'>현금성(예수금)</span>
<span style='color: #111; font-size: 18px; font-weight: 400; line-height: 20px;'>{fmt(ck)}</span>
</div>
<div style='display:flex; justify-content:space-between; align-items:baseline;'>
<span style='color: #777; font-size: 14px; font-weight: normal; line-height: 20px;'>총 손익</span>
<div style='text-align: right;'>
<div style='font-size: 18px; font-weight: 600; line-height: 1;' class='{col(cp)}'>{fmt(cp, True)}</div>
<div style='font-size: 13.5px; font-weight: 600; margin-top: 4px; line-height: 1;' class='{col(cr)}'>{fmt_p(cr)}</div>
</div>
</div>
</div>
</div>
</div>
"""
            st.markdown(top_box, unsafe_allow_html=True)

            st.markdown("""
<style>
/* 모든 버튼 내부의 강조(**) 태그를 검정색 + 표준 굵기(700)로 박제 */
.stButton strong, .stButton b, button strong, button b {
color: #111111 !important;
font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

            st.markdown(f"""
<div id='cryp_detail_section' style='padding-top: 20px; margin-top: -20px;'></div>
<h4 style='margin-bottom:10px; font-weight:bold;'>📂 보유 코인 목록</h4>
<div style='margin-bottom:15px;'>
<div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(ca)}</span> KRW / 총 손익 : <span class='summary-val {col(cp)}'>{fmt(cp, True)} ({fmt_p(cr)})</span></div>
</div>
""", unsafe_allow_html=True)

            cb1, cb2, cb3, cb4, cb5, cb6 = st.columns(6)
           
            with cb1:
                st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
                lbl1 = "🔽**정렬 [** 초기화(●)" if st.session_state.cryp_sort_mode == 'init' else "🔽**정렬 [** 초기화(○)"
                if st.button(lbl1, type="primary" if st.session_state.cryp_sort_mode == 'init' else "secondary", key='cryp_btn1', on_click=lambda: setattr(st.session_state, 'cryp_sort_mode', 'init')): pass
               
            with cb2:
                lbl2 = "총자산(●)" if st.session_state.cryp_sort_mode == 'asset' else "총자산(○)"
                if st.button(lbl2, type="primary" if st.session_state.cryp_sort_mode == 'asset' else "secondary", key='cryp_btn2', on_click=lambda: setattr(st.session_state, 'cryp_sort_mode', 'asset')): pass
               
            with cb3:
                lbl3 = "평가손익(●)" if st.session_state.cryp_sort_mode == 'profit' else "평가손익(○)"
                if st.button(lbl3, type="primary" if st.session_state.cryp_sort_mode == 'profit' else "secondary", key='cryp_btn3', on_click=lambda: setattr(st.session_state, 'cryp_sort_mode', 'profit')): pass
               
            with cb4:
                lbl4 = "손익률(●) **]**" if st.session_state.cryp_sort_mode == 'rate' else "손익률(○) **]**"
                if st.button(lbl4, type="primary" if st.session_state.cryp_sort_mode == 'rate' else "secondary", key='cryp_btn4', on_click=lambda: setattr(st.session_state, 'cryp_sort_mode', 'rate')): pass
               
            with cb5:
                lbl5 = "↕️등락률[+]" if st.session_state.cryp_show_change_rate else "↕️등락률[-]"
                if st.button(lbl5, type="primary" if st.session_state.cryp_show_change_rate else "secondary", key='cryp_btn5', on_click=lambda: setattr(st.session_state, 'cryp_show_change_rate', not st.session_state.cryp_show_change_rate)): pass
               
            with cb6:
                lbl6 = "💻종목코드[+]" if st.session_state.show_code else "💻종목코드[-]"
                if st.button(lbl6, type="primary" if st.session_state.show_code else "secondary", key='cryp_btn6', on_click=lambda: setattr(st.session_state, 'show_code', not st.session_state.show_code)): pass
           
            st.markdown("<div style='text-align:right; font-size:13px; color:#555; font-weight:bold; margin-bottom:5px;'>단위 : 원화(KRW)</div>", unsafe_allow_html=True)
           
            code_th = "<th style='text-align:center;'>종목코드</th>" if st.session_state.show_code else ""
            th_chg = "<th style='text-align:center;'>등락률</th>" if st.session_state.cryp_show_change_rate else ""
           
            t_h = f"<table class='main-table'><tr><th style='text-align:center;'>코인명</th>{code_th}<th style='text-align:center;'>비중</th><th style='text-align:center;'>총 자산</th><th style='text-align:center;'>평가손익</th><th style='text-align:center;'>손익률</th><th style='text-align:center;'>보유량</th><th style='text-align:center;'>매입가</th><th style='text-align:center;'>현재가</th>{th_chg}</tr>"
           
            sum_code_td = "<td style='text-align:center;'>-</td>" if st.session_state.show_code else ""
            sum_chg_td = "<td style='text-align:center;'>-</td>" if st.session_state.cryp_show_change_rate else ""

            t_h += f"""
<tr class='sum-row'>
<td style='text-align:center;'>[ 합  계 ]</td>
{sum_code_td}
<td style='text-align:center;'>-</td>
<td style='text-align:right; padding-right:15px;'>{fmt(ca)}</td>
<td style='text-align:right; padding-right:15px;' class='{col(cp)}'>{fmt(cp, True)}</td>
<td style='text-align:right; padding-right:15px;' class='{col(cr)}'>{fmt_p(cr)}</td>
<td style='text-align:center;'>-</td>
<td style='text-align:center;'>-</td>
<td style='text-align:center;'>-</td>
{sum_chg_td}
</tr>
"""
            c_i = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'TRX': 'tron', 'SOL': 'solana', 'XRP': 'ripple'}
            c_n = {'BTC': '비트코인(BTC)', 'ETH': '이더리움(ETH)', 'TRX': '트론(TRX)', 'SOL': '솔라나(SOL)', 'XRP': '리플(XRP)'}
       
            if isinstance(cl, list):
                s_cl = []
                for p_item in pie_items:
                    if p_item['name'] == 'KRW': continue
                    for c in cl:
                        if isinstance(c, dict) and c.get('ticker') == p_item['name']:
                            s_cl.append(c)
                            break
                           
                if st.session_state.cryp_sort_mode == 'asset': s_cl.sort(key=lambda x: safe_float(x.get('eval', 0)), reverse=True)
                elif st.session_state.cryp_sort_mode == 'profit': s_cl.sort(key=lambda x: safe_float(x.get('profit', 0)), reverse=True)
                elif st.session_state.cryp_sort_mode == 'rate': s_cl.sort(key=lambda x: safe_float(x.get('rate', 0)), reverse=True)

                for c in s_cl:
                    tk = c.get('ticker', '')
                    admin_name = str(c.get('name', '')).strip()
                    nm = admin_name if admin_name else c_n.get(tk, f"{tk}")
               
                    icon = f"https://www.google.com/s2/favicons?domain={c_i.get(tk, 'cryptocompare.com')}.org&sz=64"
                    logo = f"<div style='display:flex; justify-content:flex-start; align-items:center; gap:8px; padding-left:10px;'><img src='{icon}' style='width:20px; height:20px; border-radius:50%;'><span>{nm}</span></div>"
                    c_pct = (safe_float(c.get('eval', 0)) / ca * 100) if ca > 0 else 0
               
                    # 보유량 소수점 8자리 적용
                    qty_val = safe_float(c.get('qty',0))
                    qty_str = f"{qty_val:.8f}".rstrip('0').rstrip('.') if qty_val % 1 != 0 else f"{int(qty_val):,}"
                    qty_td = f"<td style='text-align:right; padding-right:15px;'>{qty_str}</td>" if qty_val > 0 else "<td style='text-align:center;'>-</td>"
                   
                    # 💡 [패치] 매입가 및 현재가 10,000원 미만 시 소수점 1자리 적용
                    raw_avg_p = safe_float(c.get('avg_price',0))
                    avg_p = f"{raw_avg_p:,.1f}" if 0 < raw_avg_p < 10000 else fmt(raw_avg_p)
                    avg_td = f"<td style='text-align:right; padding-right:15px;'>{avg_p}</td>" if raw_avg_p > 0 else "<td style='text-align:center;'>-</td>"
                   
                    raw_curr_p = safe_float(c.get('curr_price',0))
                    curr_p_str = f"{raw_curr_p:,.1f}" if 0 < raw_curr_p < 10000 else fmt(raw_curr_p)
                    curr_td = f"<td style='text-align:right; padding-right:15px;'>{curr_p_str}</td>" if raw_curr_p > 0 else "<td style='text-align:center;'>-</td>"
                   
                    code_td = f"<td style='text-align:center;'>{tk}</td>" if st.session_state.show_code else ""
                   
                    if st.session_state.cryp_show_change_rate:
                        # 💡 로봇이 저장하는 'chg_rate'를 1순위로 찾도록 설정
                        d_rate = safe_float(c.get('chg_rate', c.get('signed_change_rate', c.get('전일비', 0))))
                        raw_curr_p = safe_float(c.get('curr_price', 0))
                        
                        if raw_curr_p > 0 and (d_rate != 0):
                            diff_amt = (raw_curr_p - (raw_curr_p / (1 + d_rate / 100)))
                            d_class = col(d_rate)
                            chg_td = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px; font-weight:normal;'>{fmt_p(d_rate)}</div></td>"
                        else:
                            chg_td = f"<td style='padding: 4px; line-height: 1.3;'><div style='color:#aaa; font-size:13px;'>-</div><div style='color:#aaa; font-size:11.5px; font-weight:normal;'>offline</div></td>"
                    else:
                        chg_td = ""
               
                    t_h += f"""
<tr>
<td style='text-align:center;'>{logo}</td>
{code_td}
<td style='text-align:right; padding-right:15px;'>{c_pct:.1f}%</td>
<td style='text-align:right; padding-right:15px;'>{fmt(c.get('eval',0))}</td>
<td style='text-align:right; padding-right:15px;' class='{col(c.get('profit',0))}'>{fmt(c.get('profit',0), True)}</td>
<td style='text-align:right; padding-right:15px;' class='{col(c.get('rate',0))}'>{fmt_p(c.get('rate',0))}</td>
{qty_td}{avg_td}{curr_td}{chg_td}
</tr>
"""
       
            krw_pct = (ck / ca * 100) if ca > 0 else 0
            t_h += f"""
<tr style='background-color:#fcfcfc;'>
<td style='text-align:center;'>
<div style='display:flex; justify-content:center; align-items:center; gap:8px;'>
<span style='font-size:18px;'>💵</span>
<span style='color:#555;'>현금성자산</span>
</div>
</td>
{sum_code_td}
<td style='text-align:right; padding-right:15px;'>{krw_pct:.1f}%</td>
<td style='text-align:right; padding-right:15px; color:#555;'>{fmt(ck)}</td>
<td style='text-align:center;'>-</td>
<td style='text-align:center;'>-</td>
<td style='text-align:center;'>-</td>
<td style='text-align:center;'>-</td>
<td style='text-align:center;'>-</td>
{sum_chg_td}
</tr>
</table>
"""
            st.markdown(t_h, unsafe_allow_html=True)
       
            st.markdown("<h4 style='margin-bottom:15px; margin-top:35px; font-weight:bold;'>📈 종목별 실시간 시세 추이</h4>", unsafe_allow_html=True)
       
            def get_dynamic_chart_with_link(symbol, coin_id):
                return f"""
<div style="border: 1px solid #eaeaea; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.05); background: #fff; display: flex; flex-direction: column;">
<div class="tradingview-widget-container" style="height: 200px;">
<div class="tradingview-widget-container__widget" style="height: 100%; width: 100%;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
{{
"symbol": "{symbol}",
"width": "100%",
"height": "100%",
"locale": "kr",
"dateRange": "1M",
"colorTheme": "light",
"trendLineColor": "rgba(41, 98, 255, 1)",
"underLineColor": "rgba(41, 98, 255, 0.3)",
"underLineBottomColor": "rgba(41, 98, 255, 0)",
"isTransparent": true,
"autosize": true,
"largeChartUrl": ""
}}
</script>
</div>
<a href="https://upbit.com/exchange?code=CRIX.UPBIT.KRW-{coin_id}" target="_blank" style="display: block; text-align: center; padding: 12px 0; background-color: #f8f9fa; color: #0055ff; font-size: 13.5px; font-weight: bold; text-decoration: none; border-top: 1px solid #eaeaea; letter-spacing: -0.5px; transition: background-color 0.2s;">
업비트 거래소로 이동 ↗
</a>
</div>
"""
            c1, c2, c3, c4 = st.columns(4)
            with c1: components.html(get_dynamic_chart_with_link("UPBIT:BTCKRW", "BTC"), height=255)
            with c2: components.html(get_dynamic_chart_with_link("UPBIT:ETHKRW", "ETH"), height=255)
            with c3: components.html(get_dynamic_chart_with_link("UPBIT:SOLKRW", "SOL"), height=255)
            with c4: components.html(get_dynamic_chart_with_link("UPBIT:XRPKRW", "XRP"), height=255)
        else:
            st.info("🔄 오라클 서버에서 실시간 암호화폐 데이터를 동기화하는 중입니다...")

    # =========================================================
    # 🧩 알고리즘(Zappa Alpha) 대시보드 프론트엔드 UI
    # =========================================================
    elif st.session_state.current_view == '알고리즘':
        
        # 1. 사이드바 카드와 데이터 완벽 동기화 (Sync)
        mock_algo_seed = algo_total_seed
        mock_algo_profit = algo_total_profit
        mock_algo_asset = algo_total_asset
        mock_algo_winrate = algo_win_rate
        mock_algo_trades = algo_total_trades
        mock_algo_mdd = -4.2
        # 상세페이지의 텍스트 상태는 LIVE SYNC와 무관하게 봇의 가동 유무(True/False)로만 판단하도록 유지합니다.
        mock_algo_status = "🟢 ACTIVE (Trading)"
        
        mock_active_positions = [
            {"ticker": "PLTR", "name": "팔란티어", "type": "Long(매수)", "entry": 42.50, "curr": 45.20, "rate": 6.35, "signal": "MACD 골든크로스 & 거래량 급증", "amt": 2500000},
            {"ticker": "TSLA", "name": "테슬라", "type": "Long(매수)", "entry": 245.10, "curr": 241.50, "rate": -1.46, "signal": "볼린저밴드 하단 터치 (과매도)", "amt": 1800000},
            {"ticker": "BTC", "name": "비트코인", "type": "Short(매도)", "entry": 92500, "curr": 91200, "rate": 1.40, "signal": "RSI 80 돌파 (단기 과매수)", "amt": 3000000},
        ]
        
        mock_algo_logs = [
            {"time": "10:15:22", "coin": "NVDA", "type": "청산(Sell)", "reason": "익절 목표가(5%) 도달", "amt": 2000000, "profit": 102000},
            {"time": "09:30:00", "coin": "BTC", "type": "진입(Short)", "reason": "RSI 80 돌파 (단기 과매수)", "amt": 3000000, "profit": "-"},
            {"time": "04:12:45", "coin": "IONQ", "type": "청산(Sell)", "reason": "손절 라인(-3%) 이탈", "amt": 1500000, "profit": -45000},
            {"time": "02:22:10", "coin": "PLTR", "type": "진입(Long)", "reason": "MACD 골든크로스", "amt": 2500000, "profit": "-"},
        ]

        # 2. 상단 타이틀
        st.markdown(f"""
<div style="background-color:#f8f9fa; padding:20px; border-radius:12px; margin-top:10px; border:1px solid #eaeaea; display:flex; align-items:center; gap:15px; margin-bottom: 25px;">
<img src='{r_src}' style='width:48px; height:48px; object-fit:contain;'>
<div>
<h3 style="margin:0; padding:0; color:#1a1a1a; letter-spacing:-0.5px;">Zappa Alpha <span style="font-size:18px; color:#555; font-weight:normal;">(Quant Trading Bot)</span></h3>
<div style="font-size:14.5px; color:#666; margin-top:5px;">💡 감정을 배제하고 사전 정의된 기술적 지표(지수, 거래량, 모멘텀)에 따라 24시간 자동 매매를 수행하는 퀀트 대시보드입니다.</div>
</div>
</div>
""", unsafe_allow_html=True)

        # 3. 상단 핵심 성과 지표 (총 자산 표시로 변경)
        algo_summary_html = f"""
<div class='card-main' style='padding: 25px 30px; margin-bottom: 25px;'>
<div style='display: flex; justify-content: space-between; align-items: stretch;'>
<div style='flex: 1; border-right: 1px solid #e8dbad; padding-right: 20px; display: flex; flex-direction: column; justify-content: center;'>
<div style='font-size: 15px; color: #666; font-weight: bold; margin-bottom: 8px;'>🎯 알고리즘 누적 성과</div>
<div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;'>
<span style='font-size: 14px; color: #555;'>총 자산</span>
<span style='font-size: 24px; font-weight: 800; color: #111;'>{fmt(mock_algo_asset)} <span style='font-size:14px; font-weight:normal;'>KRW</span></span>
</div>
<div style='display: flex; justify-content: space-between; align-items: baseline;'>
<span style='font-size: 14px; color: #555;'>누적 실현 손익</span>
<span style='font-size: 18px; font-weight: 600;' class='{col(mock_algo_profit)}'>{fmt(mock_algo_profit, True)} <span style='font-size:12.5px; font-weight:normal;'>({fmt_p(algo_total_rate)})</span></span>
</div>
</div>
<div style='flex: 1; border-right: 1px solid #e8dbad; padding: 0 20px; display: flex; flex-direction: column; justify-content: center;'>
<div style='font-size: 15px; color: #666; font-weight: bold; margin-bottom: 8px;'>📊 리스크 및 승률 지표</div>
<div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;'>
<span style='font-size: 14px; color: #555;'>승률 (총 {mock_algo_trades}번 거래)</span>
<span style='font-size: 18px; font-weight: 600; color: #111;'>{mock_algo_winrate}%</span>
</div>
<div style='display: flex; justify-content: space-between; align-items: baseline;'>
<span style='font-size: 14px; color: #555;' title='최대 낙폭 (가장 뼈아팠던 손실 구간)'>최대 낙폭 (MDD) ℹ️</span>
<span style='font-size: 18px; font-weight: 600; color: #1976D2;'>{mock_algo_mdd}%</span>
</div>
</div>
<div style='flex: 1; padding-left: 20px; display: flex; flex-direction: column; justify-content: center;'>
<div style='font-size: 15px; color: #666; font-weight: bold; margin-bottom: 8px;'>🤖 알파 봇 상태</div>
<div class='card-inner' style='padding: 12px; text-align: center; margin-bottom: 0;'>
<div style='font-size: 17px; font-weight: 800; color: #388E3C;'>{mock_algo_status}</div>
<div style='font-size: 12.5px; color: #777; margin-top: 4px;'>전략 : 복합 모멘텀 돌파 (V1.2)</div>
</div>
</div>
</div>
</div>
"""
        st.markdown(algo_summary_html, unsafe_allow_html=True)

        # 4. 자산 성장 곡선 (Equity Curve) - Plotly 활용
        st.markdown("<div class='sub-title' style='margin-bottom: 12px;'>📈 자산 성장 곡선 (Equity Curve) & 백테스트 성과</div>", unsafe_allow_html=True)
        
        try:
            # 목업 차트 데이터 생성 (시간 흐름에 따른 시드머니 우상향 시뮬레이션)
            np.random.seed(42)
            days = pd.date_range(end=datetime.today(), periods=60)
            daily_returns = np.random.normal(0.002, 0.015, 60) # 평균 일수익 0.2%, 변동성 1.5%
            cumulative_returns = np.cumprod(1 + daily_returns)
            equity_values = mock_algo_seed * (cumulative_returns / cumulative_returns[-1]) # 마지막 값을 현재 시드머니에 맞춤
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=days, y=equity_values,
                mode='lines',
                line=dict(color='#D32F2F', width=3),
                fill='tozeroy',
                fillcolor='rgba(211, 47, 47, 0.1)',
                name='자산 평가액'
            ))
            fig.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=250,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(248,249,250,0.5)',
                xaxis=dict(showgrid=True, gridcolor='#eaeaea', linecolor='#ccc'),
                yaxis=dict(showgrid=True, gridcolor='#eaeaea', linecolor='#ccc', tickformat=",.0f"),
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("차트를 렌더링하려면 plotly 라이브러리가 필요합니다.")

        # 5. 중단 영역 (좌측: 현재 포지션 / 우측: 봇 조종석)
        c1, c_space, c2 = st.columns([6.5, 0.3, 3.2])

        with c1:
            st.markdown("<div class='sub-title' style='margin-bottom: 12px; margin-top: 10px;'>📡 실시간 진입 포지션 (Active Positions)</div>", unsafe_allow_html=True)
            
            pos_html = "<table class='main-table'><tr><th style='text-align:center;'>종목명</th><th style='text-align:center;'>포지션</th><th style='text-align:center;'>진입 시그널 (근거)</th><th style='text-align:center;'>진입가</th><th style='text-align:center;'>현재가</th><th style='text-align:center;'>수익률</th></tr>"
            
            for p in mock_active_positions:
                logo = get_logo_html(p['name'])
                pos_color = "red" if "Long" in p['type'] else "blue"
                rate_class = col(p['rate'])
                
                pos_html += f"""
<tr>
<td style='text-align:left; padding-left:15px; font-weight:bold;'>{logo}{p['name']} <span style='font-size:11.5px; color:#888; font-weight:normal;'>({p['ticker']})</span></td>
<td style='text-align:center; font-weight:bold;' class='{pos_color}'>{p['type']}</td>
<td style='text-align:left; padding-left:10px; font-size:13.5px; color:#555;'>{p['signal']}</td>
<td style='text-align:right; padding-right:15px;'>{p['entry']:,.2f}</td>
<td style='text-align:right; padding-right:15px; font-weight:bold;'>{p['curr']:,.2f}</td>
<td style='text-align:center; font-weight:bold;' class='{rate_class}'>{fmt_p(p['rate'])}</td>
</tr>
"""
            pos_html += "</table>"
            st.markdown(pos_html, unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='sub-title' style='margin-bottom: 12px; margin-top: 10px;'>⚙️ 알고리즘 조종석</div>", unsafe_allow_html=True)
            
            st.markdown("""
<div style='background:#ffffff; border:1px solid #dcdcdc; border-radius:12px; padding:20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>
<div style='font-size:14px; font-weight:bold; color:#444; margin-bottom:8px;'>🧠 매매 전략 (Strategy) 선택</div>
""", unsafe_allow_html=True)
            algo_strategy = st.selectbox("Strategy", ["안전제일 (변동성 돌파 + 하락장 방어)", "공격적 추세추종 (모멘텀)", "역추세 단기 반등 (RSI/낙폭과대)"], label_visibility="collapsed")
            
            st.markdown(f"""
<div style='font-size:14px; font-weight:bold; color:#444; margin-top:15px; margin-bottom:8px;'>🛡️ 기계적 손절 라인 (%)</div>
""", unsafe_allow_html=True)
            stop_loss = st.slider("Stop Loss", min_value=-10.0, max_value=-1.0, value=-3.0, step=0.5, label_visibility="collapsed")
            
            st.markdown("""
<div style='font-size:14px; font-weight:bold; color:#444; margin-top:15px; margin-bottom:8px;'>💵 1회 진입 최대 금액 (KRW)</div>
""", unsafe_allow_html=True)
            algo_trade_amt = st.number_input("Algo Trade Amt", min_value=100000, max_value=10000000, value=2500000, step=500000, label_visibility="collapsed")
            
            st.markdown("<hr style='margin:20px 0; border:0; border-top:1px dashed #ccc;'>", unsafe_allow_html=True)
            
            algo_toggle = st.toggle("🚀 ZAPPA 알파 봇 가동", value=True)
            
            if algo_toggle:
                st.markdown("<div style='font-size:13px; color:#388E3C; font-weight:bold; text-align:center; margin-top:5px;'>[시스템] 알고리즘이 시장 데이터를 수집 중입니다.</div></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='font-size:13px; color:#D32F2F; font-weight:bold; text-align:center; margin-top:5px;'>[시스템] 모든 매매 로직이 정지되었습니다.</div></div>", unsafe_allow_html=True)

        # 6. 하단 매매 로그 (Trade Logs)
        st.markdown("<div class='sub-title' style='margin-top: 30px; margin-bottom: 12px;'>📝 알고리즘 체결 로그 (Trade History)</div>", unsafe_allow_html=True)
        
        algo_log_html = "<table class='main-table'><tr><th style='text-align:center; width:120px;'>체결 시간</th><th style='text-align:center;'>종목명</th><th style='text-align:center;'>거래 구분</th><th style='text-align:center;'>체결 근거 (Reason)</th><th style='text-align:center;'>거래 금액</th><th style='text-align:center;'>실현 손익</th></tr>"
        
        for log in mock_algo_logs:
            type_color = "red" if "진입" in log['type'] else "blue"
            
            if log['profit'] == "-":
                prof_str = "-"
                prof_class = "gray"
            else:
                prof_str = f"+{fmt(log['profit'])}" if log['profit'] > 0 else f"{fmt(log['profit'])}"
                prof_class = col(log['profit'])
            
            logo = get_logo_html(log['coin'])
            
            algo_log_html += f"""
<tr>
<td style='text-align:center; color:#666;'>{log['time']}</td>
<td style='text-align:left; padding-left:20px; font-weight:bold;'>{logo}{log['coin']}</td>
<td style='text-align:center; font-weight:bold;' class='{type_color}'>{log['type']}</td>
<td style='text-align:left; padding-left:15px; font-size:13.5px; color:#555;'>{log['reason']}</td>
<td style='text-align:right; padding-right:20px;'>{fmt(log['amt'])}</td>
<td style='text-align:right; padding-right:20px; font-weight:bold;' class='{prof_class}'>{prof_str}</td>
</tr>
"""
        algo_log_html += "</table>"
        st.markdown(algo_log_html, unsafe_allow_html=True)

    # =========================================================
    # 💡 [패치] 차익거래 대시보드 메인 페이지 (사이드바 데이터 동기화)
    # =========================================================
    elif st.session_state.current_view == '차익거래':
        
        # 1. 봇 컨트롤 패널용 세션 스테이트 초기화 (초기 셋팅값)
        if 'main_bot_toggle' not in st.session_state:
            st.session_state.main_bot_toggle = True
            
        for c, en, ex, am in [('BTC', 2.5, 1.0, 3000000), ('ETH', 2.5, 1.0, 3000000), ('SOL', 3.0, 1.5, 2000000), ('XRP', 2.0, 0.5, 2000000)]:
            if f'bot_toggle_{c}_sub' not in st.session_state:
                st.session_state[f'bot_toggle_{c}_sub'] = True
            if f'en_{c}' not in st.session_state:
                st.session_state[f'en_{c}'] = float(en)
                st.session_state[f'ex_{c}'] = float(ex)
                st.session_state[f'amt_{c}'] = int(am)

        # 💡 [핵심 로직] 마스터 토글 변경 시 하위 4개 토글 일괄 동기화
        def sync_main_toggle():
            master_state = st.session_state.main_bot_toggle
            for coin in ['BTC', 'ETH', 'SOL', 'XRP']:
                st.session_state[f'bot_toggle_{coin}_sub'] = master_state

        # 2. 📡 [연동] 오라클 서버의 실시간 JSON 읽어오기
        # 상단에 이미 정의해둔 URL 통신 함수(get_live_data)를 재사용합니다.
        robot_data = get_live_data()
        
        if robot_data is None:
            st.error("🚨 [데이터 에러] 오라클 서버에서 데이터를 불러올 수 없습니다.")
        
        # 3. 🔗 [연결] 불러온 데이터를 대시보드 UI 변수에 매핑
        if robot_data and "items" in robot_data:
            # 로봇이 준 실제 데이터 사용
            mock_coins = robot_data["items"]
            mock_fx_rate = robot_data.get("fx", 1450.0)
            
            # UI 호환성을 위한 이름 매핑 (한글명 추가)
            name_map = {'BTC': '비트코인', 'ETH': '이더리움', 'SOL': '솔라나', 'XRP': '리플'}
            for c in mock_coins:
                c['name'] = name_map.get(c['ticker'], c['ticker'])
                # 로봇이 보내주는 진짜 등락률 데이터를 받아옵니다. (없을 때만 0.0 처리)
                c['upbit_chg'] = c.get('upbit_chg', 0.0)
                c['binance_chg'] = c.get('binance_chg', 0.0)
        else:
            # 로봇 데이터가 없을 때의 방어용 기본값
            mock_fx_rate = 1450.0
            mock_coins = [
                {"ticker": "BTC", "name": "비트코인", "upbit": 0, "binance": 0, "gap": 0, "state": "🚨 로봇 연결 대기중"},
                {"ticker": "ETH", "name": "이더리움", "upbit": 0, "binance": 0, "gap": 0, "state": "🚨 로봇 연결 대기중"},
                {"ticker": "SOL", "name": "솔라나", "upbit": 0, "binance": 0, "gap": 0, "state": "🚨 로봇 연결 대기중"},
                {"ticker": "XRP", "name": "리플", "upbit": 0, "binance": 0, "gap": 0, "state": "🚨 로봇 연결 대기중"}
            ]

        # 4. 기존 통계 변수 및 더미 로그 유지 (추후 DB 연동 시 교체할 부분)
        mock_total_seed = arbi_total_seed
        mock_total_profit = arbi_total_profit
        mock_total_asset = arbi_total_asset
        mock_total_rate = arbi_total_rate
        mock_proj_pct = (mock_total_asset / 100000000) * 100
        
        mock_logs = []
        for i in range(1, 31):
            is_entry = (i % 2 != 0)
            mock_logs.append({
                "coin": ["BTC", "ETH", "SOL", "XRP"][i % 4],
                "entry_date": f"2026-04-{(30 - i//2):02d}",
                "entry_time": f"{10 + i%10:02d}:{15 + i*2:02d}:{22 + i:02d}",
                "exit_date": f"2026-04-{(31 - i//2):02d}" if not is_entry else "진행 중",
                "exit_time": f"14:{30 + i%20:02d}:00" if not is_entry else "-",
                "entry_gap": round(2.0 + (i * 0.05), 2),
                "exit_gap": round(1.0 + (i * 0.02), 2) if not is_entry else 0,
                "amt": 500000 + (i%3)*500000,
                "profit": 15000 + i*1000 if not is_entry else 0
            })
        mock_logs.sort(key=lambda x: (x['entry_date'], x['entry_time']), reverse=True)

        c_i = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'XRP': 'ripple'}

        st.markdown("""
<style>
/* 입력창 우측 정렬 */
div[data-testid="stNumberInput"] input { text-align: right !important; font-weight: bold; font-size: 15.5px; padding-right: 12px; color: #111; }

/* 표 테두리 디자인 */
.table-rounded-wrapper { border: 2px solid #a0a0a0 !important; border-radius: 12px !important; overflow: hidden !important; width: 100% !important; margin-bottom: 5px !important; box-shadow: 0 2px 5px rgba(0,0,0,0.03) !important; }
#arbi-monitor-table { border-collapse: collapse !important; width: 100% !important; margin-bottom: 0 !important; border-style: hidden !important; }
#arbi-monitor-table th, #arbi-monitor-table td { border: 1px solid #dcdcdc !important; }

/* ==================================================================== */
/* 💡 [ZAPPA] 봇 컨트롤 패널 디자인 (물리적 공간 확보 & 중앙 관통) */
/* ==================================================================== */

/* 1. 패널 외곽선 및 가로 실선 제거 */
div.element-container:has(.bot-panel-marker) { display: none !important; }
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) {
background-color: #ffffff;
border: 1px solid #dcdcdc;
border-radius: 12px;
padding: 10px 0 !important;
}
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stHorizontalBlock"] {
border-bottom: none !important;
box-shadow: none !important;
align-items: center !important;
}

/* 2. 제목행 밑줄 (허공에 띄운 가짜 선으로 간격 붕괴 원천 차단) */
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stHorizontalBlock"]:first-of-type {
border-bottom: none !important;
padding-bottom: 0 !important;
margin-bottom: 0 !important;
position: relative !important;
}

/* 👇 허공에 빔을 쏴서 선을 그립니다. */
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stHorizontalBlock"]:first-of-type::after {
content: "";
position: absolute;
left: 0;
bottom: -12px;
width: 100%;
height: 2px;
background-color: #eaeaea;
}

/* 💡 맨 아래 나타난 알 수 없는 테두리(가로선) 찌꺼기 완벽 제거 */
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) > div {
border-bottom: none !important;
box-shadow: none !important;
}

/* 3. 2열(토글) 및 3열(코인명) 정렬 (하단 마스터행 제외) */
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stHorizontalBlock"]:not(:has(.bottom-space-cell)) div[data-testid="column"]:nth-of-type(2) {
display: flex !important;
justify-content: center !important;
align-items: center !important;
}

div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stHorizontalBlock"]:not(:has(.bottom-space-cell)) div[data-testid="column"]:nth-of-type(3) {
display: flex !important;
justify-content: center !important;
align-items: center !important;
transform: translateY(-4px) !important;
}

/* 4. 막대그래프 위치 및 전체 높이 조정 */
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stSlider"] label {
display: none !important;
}
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stSlider"] {
margin-top: 12px !important;
transform: translateY(-5px) !important;
}

/* 5. 건당 거래금액 입력창 디자인 */
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stTextInput"] {
transform: translateY(1px) !important;
}
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stTextInput"] div[data-baseweb="input"] {
min-height: 36.5px !important; 
height: 36.5px !important; 
border-radius: 6px !important;
}
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stTextInput"] input {
text-align: right !important;
font-weight: normal !important; 
padding-top: 0px !important;
padding-bottom: 0px !important;
height: 36.5px !important; 
line-height: 36.5px !important; 
}

/* 6. 슬라이더 공통 및 개별 테마 */
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child { height: 16px !important; background-color: #f0f2f6 !important; border-radius: 8px !important; }
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child > div:first-child { background-color: #4b8bff !important; }
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stSlider"] div[role="slider"] { width: 20px !important; height: 20px !important; background-color: #4b8bff !important; border: 2.5px solid #ffffff !important; }
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stSlider"] div[data-baseweb="slider"] div[role="slider"] > div {
background-color: #4b8bff !important; color: #ffffff !important; font-weight: bold !important; font-size: 13px !important; padding: 2px 6px !important; min-width: 40px !important; border-radius: 6px !important; transform: translateY(-7px) !important; text-align: center !important; display: flex !important; justify-content: center !important; align-items: center !important;
}

/* 💡 표적지(exit-target-marker)가 있는 기둥의 슬라이더만 초록색 강제 변경 */
div.element-container:has(.exit-target-marker) { display: none !important; }
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="column"]:has(.exit-target-marker) div[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child > div:first-child { background-color: #00c853 !important; }
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="column"]:has(.exit-target-marker) div[data-testid="stSlider"] div[role="slider"] { background-color: #00c853 !important; border-color: #ffffff !important; }
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="column"]:has(.exit-target-marker) div[data-testid="stSlider"] div[data-baseweb="slider"] div[role="slider"] > div { background-color: #00c853 !important; }

/* 💡 최저/최대값 텍스트의 배경을 투명하게 강제 */
div[data-testid="stTickBarMin"] > div, div[data-testid="stTickBarMax"] > div {
background-color: transparent !important; color: #666 !important; font-weight: 600 !important; box-shadow: none !important; padding: 0 !important;
}

/* 7. 세로 선 강제 생성 */
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stHorizontalBlock"]:not(:has(.bottom-space-cell)) > div[data-testid="column"] {
position: relative !important;
}
                    
/* 8. 봇 가동 토글 붉은색 고정 */
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stCheckbox"] [data-baseweb="checkbox"]:has(input:checked) > div:first-child {
background-color: #ff4b4b !important;
}

/* 우측 허공에 선을 그립니다 */
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stHorizontalBlock"]:not(:has(.bottom-space-cell)) > div[data-testid="column"]:nth-child(2)::after,
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stHorizontalBlock"]:not(:has(.bottom-space-cell)) > div[data-testid="column"]:nth-child(3)::after,
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stHorizontalBlock"]:not(:has(.bottom-space-cell)) > div[data-testid="column"]:nth-child(4)::after,
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stHorizontalBlock"]:not(:has(.bottom-space-cell)) > div[data-testid="column"]:nth-child(5)::after,
div[data-testid="stVerticalBlock"]:has(> div.element-container .bot-panel-marker) div[data-testid="stHorizontalBlock"]:not(:has(.bottom-space-cell)) > div[data-testid="column"]:nth-child(6)::after {
content: "";
position: absolute;
right: -10px;        
top: 25%;            
height: 50%;         
width: 1.5px;        
background-color: #cccccc; 
z-index: 50;
}
/* ==================================================================== */

.sticky-log-wrapper { height: 400px !important; overflow-y: auto !important; border: none !important; margin-top: 5px; margin-bottom: 30px; position: relative; display: block; background: #fff; }
#zappa-trade-log-table { border-collapse: collapse !important; width: 100%; border: none !important; }
#zappa-trade-log-table th { position: sticky !important; top: 0px !important; background-color: #f2f2f2 !important; z-index: 1000 !important; border-bottom: 2px solid #ccc !important; border-top: 1px solid #dcdcdc !important; outline: none !important; }
#zappa-trade-log-table td, #zappa-trade-log-table th { border-right: 1px solid #eaeaea; }
#zappa-trade-log-table td { border-bottom: 1px solid #eaeaea; }
#zappa-trade-log-table tr th:last-child, #zappa-trade-log-table tr td:last-child { border-right: none !important; }
#zappa-trade-log-table tr th:first-child, #zappa-trade-log-table tr td:first-child { border-left: none !important; }

.zappa-arbi-details { background: #ffffff; border: 1px solid #eaeaea; border-radius: 12px; margin-top: 5px; margin-bottom: 25px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
.zappa-arbi-summary { cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: center; font-weight: 700; color: #111; font-size: 16px; padding: 18px 25px; background: #fcfcfc; border-bottom: 1px solid transparent; border-radius: 12px; transition: all 0.2s; }
.zappa-arbi-details[open] .zappa-arbi-summary { border-bottom: 1px solid #eaeaea; border-radius: 12px 12px 0 0; }
.zappa-arbi-summary::-webkit-details-marker { display: none; }
.zappa-arbi-summary::after { content: '>'; font-family: monospace; font-weight: 900; font-size: 18px; color: #888; transition: transform 0.2s ease; }
.zappa-arbi-details[open] .zappa-arbi-summary::after { transform: rotate(90deg); }

/* ---------------------------------------------------------- */
/* 💡 마스터 컨트롤: 고무줄 팽창 방지 및 우측 끝선 절대 고정 */
/* ---------------------------------------------------------- */

/* 1. 토글, 로봇, 뱃지를 감싸는 가로줄(Row)을 통째로 우측 끝에 붙입니다 */
div[data-testid="stHorizontalBlock"]:has(.master-badge-box) {
    display: flex !important;
    justify-content: flex-end !important; 
    align-items: center !important;
    gap: 15px !important; 
    
    /* ❌ 범인: margin-top은 지우세요! (표까지 같이 아래로 밀어냅니다) */
    /* margin-top: 45px !important; */

    /* ✅ 해결책: 물리적 공간은 냅두고 시각적으로만 아래로 끌어내리기 */
    transform: translateY(30px) !important; /* 👈 숫자를 키울수록 아래로 훅훅 내려갑니다 */
    position: relative !important;
    z-index: 99 !important; /* 혹시나 표 뒤로 숨지 않게 층수를 높여줍니다 */
}

/* 2. 스트림릿의 컬럼(%) 자동 팽창 성질을 파괴 */
div[data-testid="stHorizontalBlock"]:has(.master-badge-box) > div[data-testid="column"] {
    flex: 0 0 auto !important; 
    width: auto !important;
    min-width: 0 !important;
    padding: 0 !important;
}

/* 3. 뱃지 기본 디자인 */
.master-badge-box {
    background-color: #202531;
    color: white;
    border-radius: 8px;
    white-space: nowrap;
    display: inline-block;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 4. 토글 스위치 크기 조절 */
div[data-testid="stHorizontalBlock"]:has(.master-badge-box) [data-testid="stCheckbox"] {
    transform: scale(1.3) translateY(2px) !important;
}
</style>
""", unsafe_allow_html=True)

        st.markdown("<span id='zappa-arbi-header'></span><div style='margin-top: 5px; margin-bottom: 25px;'><h3>🚀 Andy lee님 [차익거래] 통합 대시보드</h3><div style='font-size: 14.5px; color: #666; margin-top: 8px; margin-left: 38px;'>💡 업비트 ↔ 바이낸스 간의 실시간 김치 프리미엄(Gap) 및 기대 수익을 분석하는 차익거래 봇 대시보드입니다.</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-title' style='margin-bottom: 15px;'>⚖️ [차익거래] 자산 현황 요약</div>", unsafe_allow_html=True)

        p_btc_donut, p_eth_donut, p_alts_donut = 61, 9, 30
        donut_css = f"background: conic-gradient(#ffffff 0% {p_btc_donut}%, #d9d9d9 {p_btc_donut}% {p_btc_donut+p_eth_donut}%, #8c8c8c {p_btc_donut+p_eth_donut}% 100%);"

        donut_html = f"<div style='position: relative; width: 120px; height: 120px; border-radius: 50%; {donut_css} box-shadow: inset 0 0 8px rgba(0,0,0,0.1); border: 1px solid #d0d0d0; flex-shrink: 0; margin: 0 auto;'><div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 35%; height: 35%; background-color: #fffdf2; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.05);'></div><div style='position: absolute; top: 0%; left: 50%; transform: translateX(-50%); font-size: 12.5px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_btc_donut:.0f}%<br>비트코인</div><div style='position: absolute; top: 55px; right: -15px; font-size: 14px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_eth_donut:.0f}%<br>이더리움</div><div style='position: absolute; bottom: 42px; left: -20px; font-size: 14px; color: #fff; font-weight: bold; text-align: center; line-height: 1.1; text-shadow: 0px 0px 3px rgba(0,0,0,0.5);'>{p_alts_donut:.0f}%<br>Alts</div></div>"

        def render_bar(p, color): return f"<div style='width: {p}%; background-color: {color}; height: 100%; display: flex; align-items: center; justify-content: center; position: relative;'><span style='position: absolute; font-size: 13px; color: #333; z-index: 10; white-space: nowrap;'>{p:.0f}%</span></div>" if p > 0 else ""
        p_btc, p_eth, p_sol, p_xrp = 8500000/29000000*100, 5500000/29000000*100, 2500000/29000000*100, 12500000/29000000*100

        html_main_left = f"<div style='text-align: right; font-size: 13px; color: #555; font-weight: bold; margin-bottom: 5px;'>단위 : 원화(KRW)</div><div class='insight-container'><div class='insight-left'><div class='card-main'><div style='display: flex; gap: 15px; align-items: stretch; margin-bottom: auto;'><div style='flex: 0 0 38%; display: flex; flex-direction: column; align-items: center;'><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 15px; width:100%; text-align:left;'>💡총 자산</div>{donut_html}<div style='font-size: 13.5px; color: #333; font-weight: bold; margin-top: 14px;'><span style='font-size: 12.5px; color: #666;'>시드머니</span> : {fmt(mock_total_seed)}</div></div><div style='flex: 1; display: flex; flex-direction: column; justify-content: flex-start; padding-top: 5px;'><div class='card-inner' style='padding: 10px 12px; margin-bottom: 8px;'><div style='font-size: 24px; font-weight: 700 !important; color: #111; letter-spacing: normal; line-height: 1; margin-bottom: 6px;'>{fmt(mock_total_asset)}<span style='font-size: 13.5px; font-weight: normal; margin-left: 3px; letter-spacing: normal;'>KRW</span></div><div style='font-size: 13.5px; color: #777; font-weight: normal; line-height: 1;'>[ 전일비 <span class='red'>+0</span> / 전주비 <span class='red'>+0</span> ]</div></div><div style='display: grid; grid-template-columns: auto auto; row-gap: 12px; column-gap: 30px; justify-content: end; align-items: baseline; width: 100%; padding-right: 12px; margin-top: 8px;'><div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>평가금액</div><div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(mock_total_asset)}</div><div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>총 누적수익</div><div style='text-align: right;'><div style='font-size: 18px; font-weight: 600; line-height: 1;' class='{col(mock_total_profit)}'>{fmt(mock_total_profit, True)}</div><div style='font-size: 13.5px; font-weight: 600; margin-top: 3px; line-height: 1;' class='{col(mock_total_rate)}'>{fmt_p(mock_total_rate)}</div></div></div></div></div><div style='margin-top: 20px;'><div style='display: flex; height: 20px; width: 100%; border-radius: 4px; border: 1px solid #ccc; margin-bottom: 6px; overflow: hidden;'>{render_bar(p_btc, '#b4a7d6')}{render_bar(p_eth, '#f4b183')}{render_bar(p_sol, '#a9d18e')}{render_bar(p_xrp, '#ffd966')}</div><div style='display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #777; padding: 0 2px; margin-bottom: 16px;'><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#b4a7d6; border-radius:3px;'></div>비트코인</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#f4b183; border-radius:3px;'></div>이더리움</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#a9d18e; border-radius:3px;'></div>솔라나</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#ffd966; border-radius:3px;'></div>리플</div></div><div style='padding: 10px 15px; background: rgba(255,255,255,0.5); border-radius: 10px; border: 1px solid #e8dbad;'><div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'><span style='font-size: 14px; color: #777; font-weight: normal;'>🎯 디지털자산 차익거래 누적 1억 만들기</span><div style='text-align: right;'><span style='font-size: 14px; font-weight: bold; color: #4a90e2;'>{mock_proj_pct:.1f}%</span></div></div><div style='width: 100%; height: 6px; background-color: #e2e2e2; border-radius: 3px; overflow: hidden;'><div style='width: {mock_proj_pct}%; height: 100%; background: linear-gradient(90deg, #9bc2e6, #4a90e2);'></div></div></div></div></div></div>"

        cards_data = [
            {'name': '비트코인(BTC)', 'asset': 8500000, 'profit': 1250000, 'seed': 7250000},
            {'name': '이더리움(ETH)', 'asset': 5500000, 'profit': 850000, 'seed': 4650000},
            {'name': '솔라나(SOL)', 'asset': 2500000, 'profit': 570000, 'seed': 1930000},
            {'name': '리플(XRP)', 'asset': 12500000, 'profit': 3250000, 'seed': 9250000}
        ]

        cards_html = "<div class='insight-right'><div class='grid-2x2'>"
        for cd in cards_data:
            c_rate = (cd['profit'] / cd['seed']) * 100
            cards_html += f"<div class='card-sub' style='height:100%; justify-content:space-between; cursor:default;'><div><div style='text-align: right; font-size: 13.5px; color: #888; font-weight: normal; margin-bottom: -2px; line-height: 1;'>[ 2026.05 ]</div><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 2px;'>{cd['name']}</div><div style='border-bottom: 1px solid #eee; margin-bottom: 6px; margin-top: 2px;'></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 자산</span><span style='font-size: 16px; color: #111; font-weight: normal;'>{fmt(cd['asset'])}</span></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 누적수익</span><div style='text-align: right; line-height: 1.2;'><div class='{col(cd['profit'])}' style='font-size: 16px; font-weight: normal;'>{fmt(cd['profit'], True)}</div><div class='{col(c_rate)}' style='font-size: 14px; font-weight: normal; margin-top: 1px;'>{fmt_p(c_rate)}</div></div></div></div><div style='font-size: 13.5px; color: #666; font-weight: normal; margin-top: auto; padding-top: 2px; display: flex; justify-content: space-between; align-items: baseline;'><span>* <span style='font-size: 12.5px;'>시드머니</span> : {fmt(cd['seed'])}</span><span><span style='font-size: 16px; font-weight: bold; color: #111;'>1</span> 거래</span></div></div>"
        cards_html += "</div></div></div>"
        
        st.markdown(html_main_left + cards_html, unsafe_allow_html=True)
        
        # 1. 제목 (단독으로 윗줄에 배치)
        st.markdown("<div class='sub-title' style='margin-top: 50px; margin-bottom: 10px;'>🛠️ 봇 컨트롤 패널 (종목별 셋팅)</div>", unsafe_allow_html=True)

        # 2. 로봇과 뱃지 (제목 아랫줄에 배치, columns 비율로 우측 밀어내기)
        st.markdown("<div class='master-controls-anchor'>", unsafe_allow_html=True)
        c_space, c_toggle, c_robot, c_badge = st.columns([8.0, 0.4, 0.7, 2.4])
        
        with c_space:
            pass # 빈 공간
            
        with c_toggle:
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            st.toggle("run_master", key="main_bot_toggle", label_visibility="collapsed", on_change=sync_main_toggle)
            
        with c_robot:
            st.markdown(f"<div style='display:flex; justify-content:center;'><img src='{r_src}' style='width:55px;'></div>", unsafe_allow_html=True)
            
        with c_badge:
            if st.session_state.get('main_bot_toggle', True):
                badge_html = """
<div class='master-badge-box' style='padding: 8px 12px; display: flex; flex-direction: column; gap: 4px; width: max-content; margin: 0;'>
<div style='display:flex; align-items:center; line-height: 1.1;'>
<span style='font-size:11px; margin-right:5px;'>🟢</span>
<span style='font-size:13px; font-weight:900; color:#00c853; letter-spacing:-0.5px;'>ACTIVE</span>
<span style='font-size:11px; font-weight:500; color:#ffffff; margin-left:5px;'>(SEARCHING)</span>
</div>
<div style='display:flex; align-items:center; line-height: 1.1;'>
<span style='filter: grayscale(100%); opacity: 0.35; font-size:11px; margin-right:5px;'>🔴</span>
<span style='font-size:13px; font-weight:700; color:#666666; letter-spacing:-0.5px;'>STANDBY</span>
<span style='font-size:11px; font-weight:500; color:#666666; margin-left:5px;'>(OFFLINE)</span>
</div>
</div>
"""
            else:
                badge_html = """
<div class='master-badge-box' style='padding: 8px 12px; display: flex; flex-direction: column; gap: 4px; width: max-content; margin: 0;'>
<div style='display:flex; align-items:center; line-height: 1.1;'>
<span style='filter: grayscale(100%); opacity: 0.35; font-size:11px; margin-right:5px;'>🟢</span>
<span style='font-size:13px; font-weight:700; color:#666666; letter-spacing:-0.5px;'>ACTIVE</span>
<span style='font-size:11px; font-weight:500; color:#666666; margin-left:5px;'>(SEARCHING)</span>
</div>
<div style='display:flex; align-items:center; line-height: 1.1;'>
<span style='font-size:11px; margin-right:5px;'>🔴</span>
<span style='font-size:13px; font-weight:900; color:#ff5252; letter-spacing:-0.5px;'>STANDBY</span>
<span style='font-size:11px; font-weight:500; color:#666666; margin-left:5px;'>(OFFLINE)</span>
</div>
</div>
"""
            # 💡 아래처럼 겉에 div 껍질을 하나 씌워줍니다
            st.markdown(f"<div style='display: flex; justify-content: flex-end;'>{badge_html}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True) 

        with st.container():
            st.markdown("<span class='bot-panel-marker'></span>", unsafe_allow_html=True)
            
            c_ratio = [0.15, 0.20, 0.40, 0.67, 1.0, 1.0, 0.7, 0.1]
            
            st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
            
            cols_h = st.columns(c_ratio)
            h_names = ["", " ", "코인명", "누적거래 / 승률", "🎯 진입목표 [ENTRY]", "🏁 청산목표 [EXIT]", "⚓ 건당 거래금액", ""]
            
            for h_col, name in zip(cols_h, h_names):
                if name: 
                    h_col.markdown(f"""
<div style='text-align:center; transform: translateY(-12px); font-size:14px; font-weight:600; color:#31333F;'>{name}</div>
""", unsafe_allow_html=True)
            
            st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
            
            for coin in ['BTC', 'ETH', 'SOL', 'XRP']:
                c_space_l, c_b1, c_b2, c_new, c_b3, c_b4, c_b5, c_space_r = st.columns(c_ratio)
                
                with c_space_l: 
                    pass 
                    
                with c_b1: 
                    coin_active = st.toggle(f"bot_run_{coin}", key=f"bot_toggle_{coin}_sub", label_visibility="collapsed")
                    
                with c_b2: 
                    icon_url = f"https://www.google.com/s2/favicons?domain={c_i.get(coin, 'cryptocompare.com')}.org&sz=64"
                    st.markdown(f"""
<div style='display:flex; align-items:center; justify-content:center; transform: translateY(-4px);'>
<img src='{icon_url}' style='width:22px; height:22px; border-radius:50%; vertical-align:middle; margin-right:8px;'>
<span style='font-weight:bold; font-size:16px; color:#111;'>{coin}</span>
</div>
""", unsafe_allow_html=True)

                with c_new: 
                    mock_trades = 234
                    mock_win_rate = 98.4
                    
                    st.markdown(f"""
<div style='display:flex; align-items:center; justify-content:center; transform: translateY(-4px); font-size:13.5px; color:#555;'>
[&nbsp;<span style='font-weight:bold; font-size:16.5px; color:#111;'>{mock_trades}</span>&nbsp;]건 &nbsp;/&nbsp; [&nbsp;<span style='font-weight:bold; font-size:16.5px; color:#D32F2F;'>{mock_win_rate}</span>&nbsp;]%
</div>
""", unsafe_allow_html=True)
                
                main_active = st.session_state.get('main_bot_toggle', True)
                is_active = coin_active and main_active
                
                with c_b3: 
                    st.slider(f"sl_en_{coin}", min_value=1.0, max_value=5.0, step=0.1, key=f"en_{coin}", label_visibility="collapsed", disabled=not is_active)
                    
                with c_b4: 
                    st.markdown("<span class='exit-target-marker'></span>", unsafe_allow_html=True)
                    st.slider(f"sl_ex_{coin}", min_value=0.0, max_value=3.0, step=0.1, key=f"ex_{coin}", label_visibility="collapsed", disabled=not is_active)
                    
                with c_b5: 
                    curr_amt = st.session_state.get(f"amt_{coin}", 3000000)
                    str_amt = st.text_input(f"in_amt_{coin}", value=f"{curr_amt:,}", key=f"amt_str_{coin}", label_visibility="collapsed", disabled=not is_active)
                    try: 
                        st.session_state[f"amt_{coin}"] = int(str_amt.replace(",", ""))
                    except ValueError: 
                        pass
                
                with c_space_r:
                    pass
               
                if coin != 'XRP':
                    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        components.html("""
<script>
const parentDoc = window.parent.document;
function overrideStreamlitDOM() {
const table = parentDoc.getElementById('zappa-trade-log-table');
if (table) {
    let parentEl = table.parentElement;
    while (parentEl && parentEl.tagName !== 'BODY') {
        const style = window.getComputedStyle(parentEl);
        if (style.overflow === 'hidden' || style.overflowY === 'hidden') { parentEl.style.setProperty('overflow', 'visible', 'important'); }
        parentEl = parentEl.parentElement;
    }
}

const premBtn = parentDoc.getElementById('premium-update-btn');
if (premBtn && !premBtn.hasAttribute('data-binded')) {
    premBtn.setAttribute('data-binded', 'true');
    premBtn.addEventListener('mouseenter', () => { premBtn.style.backgroundColor = '#f4f5f7'; });
    premBtn.addEventListener('mouseleave', () => { premBtn.style.backgroundColor = '#ffffff'; });
    premBtn.addEventListener('click', () => {
        const btns = Array.from(parentDoc.querySelectorAll('button p'));
        const hiddenTarget = btns.find(el => el.innerText.includes('HIDDEN_PREM_UPD'));
        if (hiddenTarget) hiddenTarget.closest('button').click();
    });
}
}
setInterval(overrideStreamlitDOM, 300);
</script>
""", height=0)

        st.markdown("<hr style='border:0; border-top:1px solid #eee; margin: 30px 0 25px 0;'>", unsafe_allow_html=True)
        
        import pytz
        from datetime import datetime
        now_seoul = datetime.now(pytz.timezone('Asia/Seoul'))
        d_str_clean = f"{now_seoul.month:02d}/{now_seoul.day:02d}"
        dw_str = ["월", "화", "수", "목", "금", "토", "일"][now_seoul.weekday()]

        st.markdown(f"<div class='sub-title' style='margin-top:10px; margin-bottom:15px;'>💻 실시간 Arbitrage 종합 현황</div>", unsafe_allow_html=True)

        info_box_html = """
<details class="zappa-arbi-details" style="margin-bottom: 10px;">
<summary class="zappa-arbi-summary">💡 수익률 계산 공식 및 시뮬레이션 조건</summary>
<div style="display: flex; padding: 25px; align-items: stretch;">
<div style="flex: 1; padding-right: 25px; border-right: 1.5px solid #f0f0f0; display: flex; flex-direction: column;">
<div style="background: #fdfdfd; padding: 18px; border-radius: 10px; border: 1px solid #e0e0e0; height: 100%;">
<div style="font-size: 13.5px; color: #333; margin-bottom: 6px; font-weight: bold;">1. 실제 수익률 (%)</div>
<div style="font-family: monospace; font-size: 14px; color: #1976D2; margin-bottom: 8px; padding-left: 10px; background: #eaf2f8; padding: 8px; border-radius: 6px;">
R_actual = (G_entry - G_exit) - (F_upbit + F_binance + F_funding + S)
</div>
<div style="font-size: 12.5px; color: #666; margin-bottom: 18px; padding-left: 10px; line-height: 1.5;">
* G : 프리미엄(%), S : 슬리피지(호가 오차)<br>
* F_funding : 공매도 포지션 유지 비용 (8시간 단위 변동)
</div>
<div style="font-size: 13.5px; color: #333; margin-bottom: 6px; font-weight: bold;">2. 예상 순수익 (KRW)</div>
<div style="font-family: monospace; font-size: 14px; color: #D32F2F; margin-bottom: 8px; padding-left: 10px; background: #fdeded; padding: 8px; border-radius: 6px;">
P_net = Amount × (R_actual / 100)
</div>
<div style="font-size: 12.5px; color: #666; padding-left: 10px; line-height: 1.5;">
* Amount : 한쪽 거래소에 투입된 원화 기준 거래금액
</div>
</div>
</div>
<div style="flex: 1; padding-left: 25px; display: flex; flex-direction: column; justify-content: space-between;">
<div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
<div style="flex: 1; padding-right: 15px;">
<div style="font-weight: 800; color: #1976D2; font-size: 14.5px; margin-bottom: 6px;">[ 조건 세팅 ]</div>
<div style="font-size: 13px; color: #444; line-height: 1.7;">
• 거래 금액 : 3,000,000원<br>
<span style="color:#888; font-size: 11.5px; padding-left: 10px;">(업비트 300만 매수 + 바이낸스 300만 공매도)</span><br>
• 진입 Gap : 2.5%<br>
• 청산 Gap : 1.0%<br>
<span style="font-weight:bold; color:#111;">• 기대 수익률(δ) : 1.5%p</span>
</div>
</div>
<div style="flex: 1;">
<div style="font-weight: 800; color: #D32F2F; font-size: 14.5px; margin-bottom: 2px;">[ 지불비용 항목 ]</div>
<div style="font-size: 13px; color: #555; font-weight: bold; margin-bottom: 6px;">총 수수료(비용) : 약 0.20%</div>
<div style="font-size: 13px; color: #444; line-height: 1.7;">
• 업비트 수수료 : 왕복 0.10%<br>
<span style="color:#888; font-size: 11.5px; padding-left: 10px;">(매수 0.05% + 매도 0.05%)</span><br>
• 바이낸스 수수료 : 왕복 0.04%<br>
<span style="color:#888; font-size: 11.5px; padding-left: 10px;">(매수 0.02% + 매도 0.02%)</span><br>
• 차입/슬리피지 등 : 약 0.06%
</div>
</div>
</div>
<div style="background: #f8f9fa; padding: 12px 15px; border-radius: 8px; border: 1px solid #eee; margin-top: auto;">
<div style="font-weight: 800; color: #111; font-size: 14px; margin-bottom: 4px;">[ 최종결과 산출 ]</div>
<div style="font-size: 13.5px; color: #333; line-height: 1.5;">
• 실제 수익률 : 1.5% - 0.2% = <b style="color:#1976D2;">1.3%</b><br>
• 예상 순수익 : 3,000,000원 × 1.3% = <b style="color:#D32F2F;">39,000원</b>
</div>
</div>
</div>
</div>
</details>

<details class="zappa-arbi-details" style="margin-top: 0; margin-bottom: 25px;">
<summary class="zappa-arbi-summary">💡 Zappa Bot 진행 단계 : ① 대기중 → ② 갭도달 → ③ 진입포착 → ④ 주문체결 → ⑤ 보유중 → ⑥ 갭축소 → ⑦ 청산포착 → ⑧ 대기중</summary>
<div style="display: flex; padding: 25px; align-items: stretch;">
<div style="flex: 1; padding-right: 25px; border-right: 1.5px solid #f0f0f0; display: flex; flex-direction: column;">
<div style="background: #fdfdfd; padding: 18px; border-radius: 10px; border: 1px solid #e0e0e0; height: 100%;">
<div style="font-size: 14.5px; color: #D32F2F; margin-bottom: 12px; font-weight: 800;">A. 진입타겟 (예: 2.5%)을 노리는 그룹 <span style="font-weight:normal; font-size:13px; color:#666;">[ 미보유 상태 ]</span></div>
<div style="font-size: 13.5px; color: #444; line-height: 1.8; padding-left: 5px;">
<span style="font-weight:bold; color:#757575;">① 대기중:</span> 갭이 타겟보다 한참 모자랄 때 (평상시)<br>
<span style="font-weight:bold; color:#e65100;">② 갭도달:</span> 갭이 진입 타겟에 근접했을 때 (타겟 - 0.1% 이내 진입 시)<br>
<span style="font-weight:bold; color:#c62828;">③ 진입포착:</span> 갭이 2.5%를 돌파했을 때 (매수 주문 발사 직전)<br>
<span style="font-weight:bold; color:#5e35b1;">④ 주문체결:</span> 거래소 API로 매수/공매도가 확정된 찰나의 순간
</div>
</div>
</div>
<div style="flex: 1; padding-left: 25px; display: flex; flex-direction: column;">
<div style="background: #fdfdfd; padding: 18px; border-radius: 10px; border: 1px solid #e0e0e0; height: 100%;">
<div style="font-size: 14.5px; color: #1976D2; margin-bottom: 12px; font-weight: 800;">B. 청산타겟 (예: 1.0%)을 노리는 그룹 <span style="font-weight:normal; font-size:13px; color:#666;">[ 보유중 상태 ]</span></div>
<div style="font-size: 13.5px; color: #444; line-height: 1.8; padding-left: 5px;">
<span style="font-weight:bold; color:#2e7d32;">⑤ 보유중:</span> 진입 후 갭이 아직 넉넉할 때 (평상시)<br>
<span style="font-weight:bold; color:#0277bd;">⑥ 갭축소:</span> 갭이 청산 타겟에 근접했을 때 (타겟 + 0.1% 이내 진입 시)<br>
<span style="font-weight:bold; color:#5e35b1;">⑦ 청산포착:</span> 갭이 1.0% 이하로 떨어졌을 때 (매도/상환 주문 발사 직전)<br>
<span style="font-weight:bold; color:#111;">⑧ 청산완료:</span> 거래소 API로 최종 포지션이 closed 되고 수익이 확정된 상태
</div>
</div>
</div>
</div>
</details>
"""
        st.markdown(info_box_html, unsafe_allow_html=True)

        update_time_str = now_seoul.strftime(f"[ %y/%m/%d({dw_str}), %H:%M:%S ]")

        # 💡 [패치] 테이블 바로 위: 좌측(버튼)과 우측(환율)을 동일한 선상에 배치
        st.markdown(f"""
<div style='display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 8px; margin-top: 10px;'>
<div id='premium-update-btn' style='cursor: pointer; background: #ffffff; border: 1px solid #dcdcdc; border-radius: 8px; padding: 10px 16px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.05); transition: background-color 0.2s; width: max-content;'>
<div style='display:flex; align-items:center; justify-content:center; gap:1.5px; font-size: 13.5px; font-weight: 800; color: #111; margin-bottom: -2px;'>
<span style='font-size:13px; color:#4a90e2;'>🔄</span>KimChi PREMIUM
</div>
<div style='font-size: 11.5px; font-weight: 500; color: #666; text-align: center;'>{update_time_str}</div>
</div>
<div style='font-size:12.5px; color:#555; font-weight:bold; padding-bottom: 5px;'>
[ {update_time_str[2:-2]} ], 적용환율 1$ = {mock_fx_rate:,.1f}원 ] , 단위 : 원화(KRW)
</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<style>
div.element-container:has(.hidden-btn-marker) { display: none !important; }
div.element-container:has(.hidden-btn-marker) + div.element-container { display: none !important; }
</style>
<span class='hidden-btn-marker'></span>
""", unsafe_allow_html=True)

        if st.button("HIDDEN_PREM_UPD", key="hidden_prem_upd"):
            st.toast("📡 실시간 프리미엄 데이터를 갱신합니다.", icon="⏳")
            st.rerun()

        table_html = """
<div class='table-rounded-wrapper'>
<table id='arbi-monitor-table' class='main-table'>
<thead>
<tr>
<th rowspan='2' style='text-align:center; vertical-align:middle; background-color:#f8f9fa;'>코인명</th>
<th rowspan='2' style='text-align:center; vertical-align:middle; background-color:#f8f9fa;'>업비트</th>
<th rowspan='2' style='text-align:center; vertical-align:middle; background-color:#f8f9fa;'>바이낸스</th>
<th rowspan='2' style='text-align:center; vertical-align:middle; background-color:#f8f9fa;'>실시간 Gap</th>
<th rowspan='2' style='text-align:center; vertical-align:middle; background-color:#f8f9fa;'>상태</th>
<th colspan='3' style='text-align:center; vertical-align:middle; background-color:#f8f9fa;'>김치 프리미엄 타겟</th>
<th rowspan='2' style='text-align:center; vertical-align:middle; background-color:#f8f9fa;'>거래금액</th>
<th rowspan='2' style='text-align:center; vertical-align:middle; background-color:#f8f9fa;'>예상순수익</th>
</tr>
<tr>
<th style='text-align:center; vertical-align:middle; background-color:#f8f9fa;'>진입(Entry)</th>
<th style='text-align:center; vertical-align:middle; background-color:#f8f9fa;'>청산(Exit)</th>
<th style='text-align:center; vertical-align:middle; background-color:#f8f9fa;'>기대수익(δ)</th>
</tr>
</thead>
<tbody>
"""
        
        for c in mock_coins:
            ticker = c['ticker']
            icon = f"https://www.google.com/s2/favicons?domain={c_i.get(ticker, 'cryptocompare.com')}.org&sz=64"
            logo = f"<div style='display:flex; justify-content:flex-start; align-items:center; gap:8px; padding-left:10px;'><img src='{icon}' style='width:20px; height:20px; border-radius:50%;'><span style='font-weight:normal; color:#333;'>{c['name']}({ticker})</span></div>"
            
            en_target = st.session_state.get(f'en_{ticker}', 2.5)
            ex_target = st.session_state.get(f'ex_{ticker}', 1.0)
            amt = st.session_state.get(f'amt_{ticker}', 3000000)
            
            gap_val = c['gap']
            delta_val = en_target - ex_target
            net_profit_val = amt * (delta_val - 0.2) / 100
            
            # 💡 [패치] Gap(%) 양수/음수 기호 및 색상 분리 처리
            gap_str = f"+{gap_val:.2f}%" if gap_val > 0 else f"{gap_val:.2f}%"
            gap_color = "red" if gap_val > 0 else ("blue" if gap_val < 0 else "")
            
            # [수정된 부분] 대시보드가 임의로 판단하지 않고, 로봇이 판별한 진짜 상태값을 그대로 가져옵니다.
            real_state = c.get('state', '① 대기중')
            
            if '③ 진입' in real_state or '④ 진입' in real_state:
                status_badge = f"<span style='background:#ffebee; color:#c62828; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold;'>{real_state}</span>"
            elif '② 갭도달' in real_state:
                status_badge = f"<span style='background:#fff3e0; color:#e65100; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold;'>{real_state}</span>"
            elif '⑤ 보유중' in real_state:
                status_badge = f"<span style='background:#e8f5e9; color:#2e7d32; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold;'>{real_state}</span>"
            elif '⑥ 갭축소' in real_state:
                status_badge = f"<span style='background:#e1f5fe; color:#0277bd; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold;'>{real_state}</span>"
            elif '⑦ 청산' in real_state or '⑧ 청산' in real_state:
                status_badge = f"<span style='background:#ede7f6; color:#5e35b1; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold;'>{real_state}</span>"
            else:
                status_badge = f"<span style='background:#f5f5f5; color:#757575; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold;'>{real_state}</span>"

            up_curr, up_d_rate = c.get('upbit', 0), c.get('upbit_chg', 0)
            up_diff = (up_curr - (up_curr / (1 + up_d_rate / 100))) if up_curr > 0 and up_d_rate != 0 else 0
            
            bin_curr, bin_d_rate = c.get('binance', 0), c.get('binance_chg', 0)
            bin_curr_krw = bin_curr * mock_fx_rate
            bin_diff_krw = (bin_curr_krw - (bin_curr_krw / (1 + bin_d_rate / 100))) if bin_curr_krw > 0 and bin_d_rate != 0 else 0
            
            up_chg_str = f"({fmt(up_diff, True)} / {fmt_p(up_d_rate)})"
            
            binance_usd_str = f"${bin_curr:,.3f}" if bin_curr < 10 else f"${bin_curr:,.2f}"
            bin_chg_str = f"({fmt(bin_diff_krw, True)} / {fmt_p(bin_d_rate)})"

            table_html += f"""
<tr>
<td style='text-align:left;'>{logo}</td>
<td style='text-align:right; padding-right:15px; padding-top:8px; padding-bottom:8px;'>
<div style='font-weight:bold; font-size:15.5px; color:#111;'>{fmt(up_curr)}</div>
<div style='font-size:13px; color:{col(up_d_rate)}; margin-top:3px;'>{up_chg_str}</div>
</td>
<td style='text-align:right; padding-right:15px; padding-top:8px; padding-bottom:8px;'>
<div style='font-weight:bold; font-size:15.5px; color:#111;'>{fmt(bin_curr_krw)}</div>
<div style='font-size:13px; color:{col(bin_d_rate)}; margin-top:3px;'>{bin_chg_str}</div>
<div style='font-size:11.5px; color:#888; margin-top:2px;'>{binance_usd_str}</div>
</td>
<td style='text-align:center; font-weight:bold; font-size:15.5px;' class='{gap_color}'>{gap_str}</td>
<td style='text-align:center;'>{status_badge}</td>
<td style='text-align:center; font-weight:bold; font-size:14.5px; color:#111;'>{en_target:.1f}%</td>
<td style='text-align:center; font-weight:bold; font-size:14.5px; color:#111;'>{ex_target:.1f}%</td>
<td style='text-align:center; font-weight:bold; font-size:14.5px; color:#1976D2;'>{delta_val:.1f}%p</td>
<td style='text-align:right; font-weight:bold; font-size:14.5px; color:#111; padding-right:15px;'>{fmt(amt)}</td>
<td style='text-align:right; font-weight:bold; font-size:14.5px; color:#D32F2F; padding-right:15px;'>{fmt(net_profit_val)}</td>
</tr>
"""
        table_html += "</tbody></table></div>"
        
        st.markdown(table_html, unsafe_allow_html=True)

        st.markdown("<hr style='border:0; border-top:1px solid #eee; margin: 40px 0 0px 0;'>", unsafe_allow_html=True)

        col_log_title, col_date = st.columns([7.85, 2.15])
        
        with col_log_title:
            st.markdown("<div class='sub-title' style='margin-bottom: 12px; margin-top: 20px;'>📝 최근 매매 로그 (Trade History)</div>", unsafe_allow_html=True)
            
        with col_date:
            st.markdown("<span class='log-date-marker'></span>", unsafe_allow_html=True)
            st.markdown("<div style='text-align:right; font-size:14px; font-weight:bold; color:#31333F; margin-bottom:-35px; margin-right:2px;'>🗓️ 조회 기간 (시작일 - 종료일)</div>", unsafe_allow_html=True)
            from datetime import timedelta
            st.date_input("date_input_hidden_label", value=[datetime.today() - timedelta(days=7), datetime.today()], key="arbi_log_date", label_visibility="hidden")

        log_html = """<div class='sticky-log-wrapper'><table class='main-table' id='zappa-trade-log-table'><thead><tr><th class='sortable' title='클릭하여 정렬'>코인명 ↕</th><th class='sortable' title='클릭하여 정렬'>진입 일자 ↕</th><th class='sortable' title='클릭하여 정렬'>진입 시간 ↕</th><th class='sortable' title='클릭하여 정렬'>청산 일자 ↕</th><th class='sortable' title='클릭하여 정렬'>청산 시간 ↕</th><th class='sortable' title='클릭하여 정렬'>진입 Gap(%) ↕</th><th class='sortable' title='클릭하여 정렬'>청산 Gap(%) ↕</th><th class='sortable' title='클릭하여 정렬'>거래 금액 ↕</th><th class='sortable' title='클릭하여 정렬'>실현 손익 ↕</th></tr></thead><tbody>"""
        for log in mock_logs:
            prof_str = f"+{fmt(log['profit'])}" if log['profit'] > 0 else (fmt(log['profit']) if log['profit'] != 0 else "-")
            prof_class = "red" if log['profit'] > 0 else ("blue" if log['profit'] < 0 else "gray")
            exit_gap_str = f"+{log['exit_gap']:.2f}%" if log['exit_gap'] > 0 else "-"
            
            log_html += f"<tr><td style='text-align:center; font-weight:bold; font-size:14.5px;'>{log['coin']}</td><td style='text-align:center; color:#666; font-size:13.5px;'>{log['entry_date']}</td><td style='text-align:center; color:#111; font-weight:bold; font-size:13.5px;'>{log['entry_time']}</td><td style='text-align:center; color:#666; font-size:13.5px;'>{log['exit_date']}</td><td style='text-align:center; color:#111; font-weight:bold; font-size:13.5px;'>{log['exit_time']}</td><td style='text-align:center; color:#D32F2F; font-weight:bold;'>+{log['entry_gap']:.2f}%</td><td style='text-align:center; color:#1976D2; font-weight:bold;'>{exit_gap_str}</td><td style='text-align:right; padding-right:20px;'>{fmt(log['amt'])}</td><td style='text-align:right; padding-right:20px; font-weight:bold;' class='{prof_class}'>{prof_str}</td></tr>"
        st.markdown(log_html + "</tbody></table></div>", unsafe_allow_html=True)
