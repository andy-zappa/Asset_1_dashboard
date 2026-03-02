import streamlit as st
import streamlit.components.v1 as components
import json
import warnings
import andy_pension_v2
import andy_general_v1
import os
import re
import time
from datetime import datetime
import urllib.parse  

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="ZAPPA Asset Dashboard")

# =========================================================
# [ Part 1 ] 공통 설정 및 CSS 디자인
# =========================================================
css = """
<style>
/* 🎯 Streamlit 로딩 텍스트만 숨기고 툴바는 유지 */
[data-testid="stStatusWidget"] { display: none !important; }

/* 🎯 스무스 스크롤 전역 강제 적용 */
html, body, .stApp, .main, [data-testid="stAppViewContainer"], .block-container { 
    scroll-behavior: smooth !important; 
}

/* 🎯 사이드바 최상단 여백 극한으로 끌어올리기 */
[data-testid="stSidebarUserContent"] { padding-top: 1.5rem !important; }
section[data-testid="stSidebar"] .block-container { padding-top: 0 !important; margin-top: -15px !important; gap: 0 !important; }

/* 🎯 사이드바 기본 버튼 스타일링 */
[data-testid="stSidebar"] button[kind="secondary"] {
    background-color: #ffffff;
    border: 1.5px solid #dcdcdc;
    border-radius: 12px;
    transition: all 0.3s ease;
    padding: 10px !important;
    height: auto !important;
    width: 100% !important;
    margin-bottom: 5px !important;
}
[data-testid="stSidebar"] button[kind="secondary"] p {
    font-size: 16px !important;
    font-weight: bold !important;
    color: #111 !important;
}
[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background-color: #f8f9fa !important; 
    border-color: #ccc !important; 
    transform: translateY(-1px); 
    box-shadow: 0 4px 12px rgba(0,0,0,0.08); 
}

/* 🎯 사이드바 카드 호버 및 클릭 액션 추가 */
.sidebar-card { transition: transform 0.2s ease, box-shadow 0.2s ease; cursor: pointer; }
.sidebar-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.12) !important; }
.sidebar-card-dark:hover { box-shadow: 0 6px 12px rgba(255,255,255,0.08) !important; }

.block-container { padding-top: 3rem !important; padding-bottom: 7rem !important; }
h3 { font-size: 26px !important; font-weight: bold; margin-bottom: -10px; padding-bottom: 0px; }
.sub-title { font-size: 22px !important; font-weight: bold; margin: 12px 0 10px; }

/* 🎯 테이블 둥글게 및 내/외부 선 완벽 제어 */
.main-table { width: 100%; border-collapse: separate !important; border-spacing: 0; border: 1.5px solid #b5b5b5 !important; border-radius: 12px; overflow: hidden; font-size: 15px; text-align: center; margin-bottom: 10px; }
.main-table th { background-color: #f2f2f2; padding: 10px; border-bottom: 1px solid #dcdcdc !important; border-right: 1px solid #dcdcdc !important; font-weight: bold !important; vertical-align: middle; }
.main-table td { padding: 8px; border-bottom: 1px solid #dcdcdc !important; border-right: 1px solid #dcdcdc !important; vertical-align: middle; }
.main-table tr th:last-child, .main-table tr td:last-child { border-right: none !important; }
.main-table tr:last-child th, .main-table tr:last-child td { border-bottom: none !important; }
.main-table th.th-eval { border-right: none !important; }
.main-table th.th-blank { border-bottom: none !important; border-right: none !important; padding: 0 !important; }
.main-table th.th-week { border-left: 1px solid #dcdcdc !important; border-top: 1px solid #dcdcdc !important; font-size: 13.5px; }

.sum-row td { background-color: #fff9e6; font-weight: bold !important; }
.red { color: #FF2323 !important; }
.blue { color: #0047EB !important; }

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

/* 🎯 컴팩트 Selectbox CSS */
div[data-baseweb="select"] { min-height: 32px !important; font-size: 12px !important; }
div[data-baseweb="select"] > div { padding: 0px 8px !important; border-radius: 6px !important; min-height: 32px !important; }
div[data-baseweb="select"] span { font-size: 12px !important; line-height: 32px !important; }
div[data-testid="stSelectbox"] label { display: none !important; }

/* 🎯 플로팅 배너 CSS 수정 */
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu), div[data-testid="column"]:has(span#zappa-floating-menu) { 
    position: fixed !important; top: 75px !important; right: 20px !important; bottom: auto !important; left: auto !important; 
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
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button:hover { color: #111111 !important; background-color: #e5e7eb !important; border-radius: 4px !important; }
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button[kind="primary"] { background: transparent !important; border: none !important; color: #111111 !important; font-weight: bold !important; }

/* 🎯 라디오 버튼 영역 완전 숨김 (JavaScript용 트리거) */
div[role="radiogroup"], div[data-testid="stRadio"] { position: absolute !important; width: 0px !important; height: 0px !important; opacity: 0 !important; overflow: hidden !important; pointer-events: none !important; margin: 0 !important; padding: 0 !important; display: none !important; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 🎯 스무스 스크롤 및 사이드바 카드 클릭 라우팅 JS
components.html("""
<script>
const parentDoc = window.parent.document;

// 숨김 라디오 버튼 클릭 트리거 로직
const bindClick = (cardId, labelText) => {
    const card = parentDoc.getElementById(cardId);
    if (card && !card.hasAttribute('data-binded')) {
        card.setAttribute('data-binded', 'true');
        card.addEventListener('click', () => {
            const labels = Array.from(parentDoc.querySelectorAll('label'));
            const target = labels.find(l => l.innerText.includes(labelText));
            if (target) target.click();
        });
    }
};

function bindSidebarClicks() {
    bindClick('card-total', '대시보드');
    bindClick('card-pension', '절세계좌');
    bindClick('card-general', '일반계좌');
}
setInterval(bindSidebarClicks, 1000);
</script>
""", height=0)

# =========================================================
# 🎯 글로벌 로고/아이콘 매핑 로직
# =========================================================
GUARANTEED_LOGOS = {
    "알파벳 A": "google.com", "팔란티어 테크": "palantir.com", "TSMC(ADR)": "tsmc.com",
    "QQQ 레버리지 3X ETF": "invesco.com", "테슬라": "tesla.com", "마이크로소프트": "microsoft.com",
    "애플": "apple.com", "미국 반도체 3X ETF": "direxion.com", "엔비디아": "nvidia.com",
    "아이온큐": "ionq.com", "리케티 컴퓨팅": "rigetti.com", "디 웨이브 퀀텀": "dwavesys.com",
    "아이렌": "iren.com", "피그마": "figma.com",
    "삼성전자": "samsung.com", "현대차": "hyundai.com", "CJ": "cj.net", 
    "두산에너빌리티": "doosanenerbility.com", "한화오션": "hanwhaocean.com",
    "한국항공우주": "koreaaero.com", "POSCO홀딩스": "posco.co.kr", "셀트리온": "celltrion.com",
    "KODEX 레버리지": "samsungfund.com", "KODEX 200": "samsungfund.com",
    "KODEX 미국나스닥100": "samsungfund.com", "KODEX 200타겟위클리커버드콜": "samsungfund.com",
    "KODEX 미국AI테크TOP10타겟": "samsungfund.com", "KODEX 미국나스닥100데일리": "samsungfund.com",
    "TIGER 미국S&P500": "tigeretf.com", "TIGER 미국필라델피아반도체나스닥": "tigeretf.com",
    "TIGER 미국배당다우존스": "tigeretf.com", "PLUS 고배당주": "hanwhafund.com",
    "RISE 200위클리커버드콜": "kbstarfund.com"
}

def get_logo_html(nm):
    if not nm or nm in ["예수금", "[ 합  계 ]"]: return ""
    domain = GUARANTEED_LOGOS.get(nm)
    if domain:
        img_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
        return f"<img src='{img_url}' style='width:18px; height:18px; border-radius:50%; vertical-align:middle; margin-right:8px; margin-bottom:2px; box-shadow: 0 1px 2px rgba(0,0,0,0.15); background-color:white; object-fit:contain;'>"
    else:
        clean_nm = re.sub(r'[^가-힣a-zA-Z0-9]', '', nm)
        short_str = clean_nm[:1] if clean_nm else "Z"
        colors = ["#e6f2ff", "#e6ffe6", "#ffe6e6", "#fff0e6", "#f0e6ff", "#ffe6f9", "#e6ffff", "#f5ffe6"]
        text_colors = ["#0066cc", "#006600", "#cc0000", "#cc5200", "#5200cc", "#cc00a3", "#00cccc", "#669900"]
        idx = sum(ord(c) for c in short_str) % len(colors)
        return f"<span style='display:inline-block; width:18px; height:18px; border-radius:50%; background-color:{colors[idx]}; color:{text_colors[idx]}; text-align:center; line-height:18px; font-size:10px; font-weight:900; margin-right:8px; vertical-align:middle; box-shadow: 0 1px 2px rgba(0,0,0,0.1);'>{short_str}</span>"

if 'sort_mode' not in st.session_state: st.session_state.sort_mode = 'init'
if 'gen_sort_mode' not in st.session_state: st.session_state.gen_sort_mode = 'init'
if 'show_code' not in st.session_state: st.session_state.show_code = False
if 'show_change_rate' not in st.session_state: st.session_state.show_change_rate = False
if 'gen_show_change_rate' not in st.session_state: st.session_state.gen_show_change_rate = False
if 'current_view' not in st.session_state: st.session_state.current_view = '대시보드'

if 'usa_show_krw' not in st.session_state: st.session_state.usa_show_krw = True
if 'usa_show_usd' not in st.session_state: st.session_state.usa_show_usd = False

def toggle_usa_krw():
    st.session_state.usa_show_krw = not st.session_state.usa_show_krw
    if not st.session_state.usa_show_krw and not st.session_state.usa_show_usd:
        st.session_state.usa_show_usd = True

def toggle_usa_usd():
    st.session_state.usa_show_usd = not st.session_state.usa_show_usd
    if not st.session_state.usa_show_krw and not st.session_state.usa_show_usd:
        st.session_state.usa_show_krw = True

def on_menu_change():
    if st.session_state.menu_sel is not None:
        st.session_state.current_view = st.session_state.menu_sel

# 🚨 앱 켜질 때 JSON 파일 안전 동기화
if 'init' not in st.session_state:
    with st.spinner("Andy님의 최신 자산 데이터를 동기화하고 있습니다. 잠시만 기다려주세요... ✨"):
        try: andy_pension_v2.generate_asset_data()
        except: pass
        time.sleep(1.5)
        try: andy_general_v1.generate_general_data()
        except: pass
    st.session_state['init'] = True
    st.cache_data.clear()

@st.cache_data(ttl=60)
def load():
    try:
        if not os.path.exists('assets.json') or os.path.getsize('assets.json') == 0: andy_pension_v2.generate_asset_data()
        with open('assets.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

@st.cache_data(ttl=60)
def load_gen():
    try:
        if not os.path.exists('assets_general.json') or os.path.getsize('assets_general.json') == 0: andy_general_v1.generate_general_data()
        with open('assets_general.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

data = load(); g_data = load_gen(); tot = data.get("_total", {})

def safe_float(val):
    try:
        if val in ['-', '', None]: return 0.0
        return float(val)
    except: return 0.0

def fmt(v, sign=False, decimal=0):
    if v == '-': return '-'
    try:
        f_val = float(v)
        val_str = f"{f_val:,.{decimal}f}" if decimal > 0 else f"{int(round(f_val)):,}"
        if sign and f_val > 0: return f"+{val_str}"
        return val_str
    except: return str(v)

def fmt_p(v):
    try:
        val = float(v)
        return f"▲{val:.2f}%" if val > 0 else (f"▼{abs(val):.2f}%" if val < 0 else "0.00%")
    except: return str(v)

# 🎯 사이드바 카드용 소수점 1자리 스마트 제어 (0.xx% 일때만 2자리)
def fmt_p1(v):
    try:
        val = float(v)
        abs_val = abs(val)
        if abs_val < 1.0 and abs_val != 0.0:
            return f"▲{val:.2f}%" if val > 0 else f"▼{abs_val:.2f}%"
        else:
            return f"▲{val:.1f}%" if val > 0 else (f"▼{abs_val:.1f}%" if val < 0 else "0.0%")
    except: return str(v)

def col(v):
    try:
        val = float(v)
        return "red" if val > 0 else ("blue" if val < 0 else "")
    except: return ""

def short_name(nm): return nm[:13] + "***" if len(nm) > 13 else nm

# =========================================================
# 📍 사이드바 렌더링
# =========================================================
with st.sidebar:
    # 🎯 히든 라디오 
    st.radio("hidden_nav", ("대시보드", "절세계좌", "일반계좌"), label_visibility="collapsed", key="menu_sel", on_change=on_menu_change)
    
    p_asset_all = tot.get('총 자산', 0); p_profit_all = tot.get('총 수익', 0); p_rate_all = tot.get('수익률(%)', 0)
    p_cash_tot, p_ovs_tot, p_dom_tot = 0, 0, 0
    for k in ['DC', 'IRP', 'PENSION', 'ISA']:
        if k in data:
            for item in data[k].get('상세', []):
                if item.get('종목명') == '[ 합  계 ]': continue
                val = item.get('총 자산', 0); nm = item.get('종목명', '').upper()
                if '현금' in nm or 'MMF' in nm: p_cash_tot += val
                elif any(kw in nm for kw in ['미국', 'S&P', '나스닥', '필라델피아', '다우지수']): p_ovs_tot += val
                else: p_dom_tot += val
    
    p_dom_pct = (p_dom_tot / p_asset_all * 100) if p_asset_all > 0 else 0
    p_ovs_pct = (p_ovs_tot / p_asset_all * 100) if p_asset_all > 0 else 0

    GEN_ACC_ORDER_Q = ['DOM1', 'DOM2', 'USA1', 'USA2']
    g_principals_q = {"DOM1": 110963075, "DOM2": 5208948, "USA1": 257915999, "USA2": 7457930}
    g_orig_all = sum(g_principals_q.values())
    g_asset_all = sum(g_data[k].get("총자산_KRW", 0) for k in GEN_ACC_ORDER_Q if k in g_data)
    g_profit_all = sum(g_data[k].get("총수익_KRW", 0) for k in GEN_ACC_ORDER_Q if k in g_data)
    g_rate_all = (g_profit_all / g_orig_all * 100) if g_orig_all > 0 else 0

    g_cash_tot, g_ovs_tot, g_dom_tot = 0, 0, 0
    for k in GEN_ACC_ORDER_Q:
        if k in g_data:
            is_usa = 'USA' in k; fx = g_data.get('환율', 1443.1) if is_usa else 1
            for item in g_data[k].get('상세', []):
                if item.get('종목명') == '[ 합  계 ]': continue
                val_krw = item.get('총자산', 0) * fx; nm = item.get('종목명', '').upper()
                if nm == '예수금' or '현금' in nm: g_cash_tot += val_krw
                elif is_usa: g_ovs_tot += val_krw
                else: g_dom_tot += val_krw
                
    g_dom_pct = (g_dom_tot / g_asset_all * 100) if g_asset_all > 0 else 0
    g_ovs_pct = (g_ovs_tot / g_asset_all * 100) if g_asset_all > 0 else 0

    total_asset = p_asset_all + g_asset_all
    total_profit = p_profit_all + g_profit_all
    total_orig = tot.get('원금합', 1) + g_orig_all
    total_rate = (total_profit / total_orig * 100) if total_orig > 0 else 0

    # 🎯 폰트 사이즈 통일 (KRW와 손익률 사이즈 일치) 및 우측 정렬
    st.markdown(f"<div id='card-total' class='sidebar-card sidebar-card-dark'><div style='font-size:13px; font-weight:bold; color:#aaaaaa; margin-bottom:6px;'>🌎 총 자산 통합</div><div style='text-align: right;'><div style='font-size:24px; font-weight:600; letter-spacing:-0.5px; line-height: 1.2;'>{fmt(total_asset)}<span style='font-size:15px; font-weight:normal; margin-left:4px; color:#ddd;'>KRW</span></div><div style='font-size:15px; margin-top:2px; color:#cccccc;'><span style='font-weight:bold; color: {'#ff4b4b' if total_profit > 0 else '#4b8bf5'};'>{fmt(total_profit, True)}</span> ({fmt_p1(total_rate)})</div></div><div style='margin-top: 15px; padding-top: 12px; border-top: 1px dashed #3a3a3a;'><div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'><span style='font-size: 12.5px; color: #999; font-weight: normal;'>🎯 30억 달성 프로젝트</span><span style='font-size: 13px; font-weight: bold; color: #e8c368;'>{(total_asset / 3000000000 * 100):.1f}%</span></div><div style='width: 100%; height: 6px; background-color: #333; border-radius: 3px; overflow: hidden;'><div style='width: {(total_asset / 3000000000 * 100)}%; height: 100%; background: linear-gradient(90deg, #bfa054, #fceabb);'></div></div></div></div>", unsafe_allow_html=True)
    st.markdown(f"<div id='card-pension' class='sidebar-card'><div style='font-size:13px; font-weight:bold; color:#777; margin-bottom:6px;'>⏳ 절세계좌</div><div style='text-align: right;'><div style='font-size:21px; font-weight:600; color:#111; letter-spacing:-0.5px; line-height: 1.2;'>{fmt(p_asset_all)}<span style='font-size:14px; font-weight:normal; margin-left:3px; color:#555;'>KRW</span></div><div style='font-size:14px; margin-top:2px; color:#555;'><span class='{col(p_profit_all)}' style='font-weight:bold;'>{fmt(p_profit_all, True)}</span> ({fmt_p1(p_rate_all)})</div><div style='font-size:12px; color:#888; font-weight:500; margin-top:8px;'>국내 {p_dom_pct:.0f}% / 해외 {p_ovs_pct:.0f}%</div></div></div>", unsafe_allow_html=True)
    st.markdown(f"<div id='card-general' class='sidebar-card'><div style='font-size:13px; font-weight:bold; color:#777; margin-bottom:6px;'>🌱 일반계좌</div><div style='text-align: right;'><div style='font-size:21px; font-weight:600; color:#111; letter-spacing:-0.5px; line-height: 1.2;'>{fmt(g_asset_all)}<span style='font-size:14px; font-weight:normal; margin-left:3px; color:#555;'>KRW</span></div><div style='font-size:14px; margin-top:2px; color:#555;'><span class='{col(g_profit_all)}' style='font-weight:bold;'>{fmt(g_profit_all, True)}</span> ({fmt_p1(g_rate_all)})</div><div style='font-size:12px; color:#888; font-weight:500; margin-top:8px;'>국내 {g_dom_pct:.0f}% / 해외 {g_ovs_pct:.0f}%</div></div></div>", unsafe_allow_html=True)
    
    # 🎯 가상자산 & 퀀트매매 (세로 배치 및 버튼 클릭 라우팅)
    st.markdown(f"<div id='card-crypto' class='sidebar-card' style='margin-bottom: 12px;'><div style='font-size:13px; font-weight:bold; color:#777; margin-bottom:6px;'>🪙 가상자산</div><div style='text-align: right;'><div style='font-size:21px; font-weight:600; color:#111; letter-spacing:-0.5px; line-height: 1.2;'>10,000,000<span style='font-size:14px; font-weight:normal; margin-left:3px; color:#555;'>KRW</span></div><div style='font-size:14px; margin-top:2px; color:#555;'><span class='red' style='font-weight:bold;'>+242,000</span> (▲23.4%)</div><div style='font-size:12px; color:#888; font-weight:500; margin-top:8px;'>BTC 52% / ETH 31% / XRP 11%</div></div></div>", unsafe_allow_html=True)
    st.markdown(f"<div id='card-quant' class='sidebar-card' style='display:flex; align-items:center; justify-content:center; height: 110px; margin-bottom: 25px;'><div style='font-size:20px; font-weight:bold; color:#111; display:flex; align-items:center; gap:10px;'><img src='https://cdn-icons-png.flaticon.com/512/6134/6134346.png' style='width:36px; height:36px; object-fit:contain;'> 퀀트매매</div></div>", unsafe_allow_html=True)
    
    # Python 클릭 트리거용 숨김 버튼
    col_a, col_b = st.columns(2)
    with col_a: 
        if st.button("c_click", key="btn_c"): st.session_state.current_view = '암호화폐'
    with col_b: 
        if st.button("q_click", key="btn_q"): st.session_state.current_view = '퀀트매매'

    # JS로 카드 클릭 시 숨김 버튼 클릭 실행
    components.html("""
    <script>
    const parentDoc = window.parent.document;
    function bindBottom() {
        const cCard = parentDoc.getElementById('card-crypto');
        if (cCard && !cCard.hasAttribute('bound')) {
            cCard.setAttribute('bound', 'true');
            cCard.addEventListener('click', () => {
                const btns = Array.from(parentDoc.querySelectorAll('button p'));
                const b = btns.find(x => x.innerText === 'c_click'); if(b) b.closest('button').click();
            });
        }
        const qCard = parentDoc.getElementById('card-quant');
        if (qCard && !qCard.hasAttribute('bound')) {
            qCard.setAttribute('bound', 'true');
            qCard.addEventListener('click', () => {
                const btns = Array.from(parentDoc.querySelectorAll('button p'));
                const b = btns.find(x => x.innerText === 'q_click'); if(b) b.closest('button').click();
            });
        }
        
        // Hide ghost buttons
        parentDoc.querySelectorAll('button p').forEach(p => {
            if(p.innerText === 'c_click' || p.innerText === 'q_click') {
                p.closest('div[data-testid="stButton"]').style.display = 'none';
            }
        });
    }
    setInterval(bindBottom, 500);
    </script>
    """, height=0)
