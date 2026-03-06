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

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="ZAPPA Asset Dashboard")

# =========================================================
# [ Part 1 ] 공통 설정 및 오리지널 CSS 복원
# =========================================================
css = """
<style>
[data-testid="stStatusWidget"] { display: none !important; }
html, body, .stApp, .main, [data-testid="stAppViewContainer"], .block-container { scroll-behavior: smooth !important; }
[data-testid="stSidebarUserContent"] { padding-top: 1.5rem !important; }
section[data-testid="stSidebar"] .block-container { padding-top: 0 !important; margin-top: -15px !important; gap: 0 !important; }
.sidebar-card { transition: transform 0.2s ease, box-shadow 0.2s ease; cursor: pointer; background-color: #f8f9fa; border-radius: 12px; padding: 15px; border: 1px solid #eaeaea; margin-bottom: 12px; }
.sidebar-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.08) !important; border-color: #ccc !important; }
.sidebar-card-dark { background-color: #1a1a1a !important; color: #ffffff !important; border: none !important; }
.sidebar-card-dark:hover { box-shadow: 0 6px 12px rgba(255,255,255,0.08) !important; }
.block-container { padding-top: 3rem !important; padding-bottom: 7rem !important; }
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
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button:hover { color: #111111 !important; background-color: #e5e7eb !important; border-radius: 4px !important; }
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button[kind="primary"] { background: transparent !important; border: none !important; color: #111111 !important; font-weight: bold !important; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

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
    const labels = Array.from(parentDoc.querySelectorAll('div[role="radiogroup"] label'));
    const bindClick = (cardId, routeName) => {
        const card = parentDoc.getElementById(cardId);
        if (card && !card.hasAttribute('data-binded')) {
            card.setAttribute('data-binded', 'true');
            card.addEventListener('click', () => {
                const target = labels.find(l => l.innerText.includes(routeName));
                if(target) target.click();
            });
        }
    };
    bindClick('card-total', '대시보드');
    bindClick('card-pension', '절세계좌');
    bindClick('card-general', '일반계좌');
    bindClick('card-crypto', '가상자산');
    bindClick('card-quant', '퀀트매매');
}
setInterval(bindSidebarClicks, 1000);
</script>
""", height=0)

GUARANTEED_LOGOS = {
    "알파벳 A": "google.com", "팔란티어 테크": "palantir.com", "TSMC(ADR)": "tsmc.com",
    "QQQ 레버리지 3X ETF": "invesco.com", "테슬라": "tesla.com", "마이크로소프트": "microsoft.com",
    "애플": "apple.com", "미국 반도체 3X ETF": "direxion.com", "엔비디아": "nvidia.com",
    "아이온큐": "ionq.com", "리케티 컴퓨팅": "rigetti.com", "디 웨이브 퀀텀": "dwavesys.com",
    "아이렌": "iren.com", "피그마": "figma.com", "삼성전자": "samsung.com", "현대차": "hyundai.com",
    "CJ": "cj.net", "두산에너빌리티": "doosanenerbility.com", "한화오션": "hanwhaocean.com",
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
        return f"<img src='https://www.google.com/s2/favicons?domain={domain}&sz=64' style='width:18px; height:18px; border-radius:50%; vertical-align:middle; margin-right:8px; margin-bottom:2px; box-shadow: 0 1px 2px rgba(0,0,0,0.15); background-color:white; object-fit:contain;'>"
    else:
        clean_nm = re.sub(r'[^가-힣a-zA-Z0-9]', '', nm)
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

def toggle_usa_krw():
    st.session_state.usa_show_krw = not st.session_state.usa_show_krw
    if not st.session_state.usa_show_krw and not st.session_state.usa_show_usd: st.session_state.usa_show_usd = True

def toggle_usa_usd():
    st.session_state.usa_show_usd = not st.session_state.usa_show_usd
    if not st.session_state.usa_show_krw and not st.session_state.usa_show_usd: st.session_state.usa_show_krw = True

def on_menu_change():
    if st.session_state.menu_sel is not None:
        st.session_state.current_view = st.session_state.menu_sel

# =========================================================
# 🎯 통합 헬퍼 함수 모음 (시간 포맷 오류 수정 완료)
# =========================================================
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
    try: return float(val) if val not in ['-', '', None] else 0.0
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
        return f"▲{val:.2f}%" if val > 0 else (f"▼{abs(val):.2f}%" if val < 0 else "0.00%")
    except: return str(v)

def fmt_p1(v):
    if v == '-' or v is None: return '-'
    try:
        val = float(v)
        abs_val = abs(val)
        if abs_val < 1.0 and abs_val != 0.0: return f"▲{val:.2f}%" if val > 0 else f"▼{abs_val:.2f}%"
        else: return f"▲{val:.1f}%" if val > 0 else (f"▼{abs_val:.1f}%" if val < 0 else "0.0%")
    except: return str(v)

def col(v):
    try: return "red" if float(v) > 0 else ("blue" if float(v) < 0 else "gray")
    except: return ""

def short_name(nm):
    nm = str(nm)
    map_dict = {'TIGER 미국S&P500': '미국S&P500', 'TIGER 미국나스닥100': '미국나스닥100', 'KODEX 200': 'KODEX200'}
    for k, v in map_dict.items():
        if k in nm: return v
    return nm[:13] + "***" if len(nm) > 13 else nm

# =========================================================
# 🌟 [데이터 로드 엔진] 하이브리드 통신 및 캐시 무력화
# =========================================================
@st.cache_data(ttl=60)
def fetch_hybrid_data():
    p_data, g_data = {}, {}
    is_online = False
    ts = int(time.time())
    try:
        r_p = requests.get(f"http://158.179.172.40:8000/tax_advantaged?t={ts}", timeout=5)
        r_g = requests.get(f"http://158.179.172.40:8000/taxable?t={ts}", timeout=5)
        
        if r_p.status_code == 200:
            p_data = r_p.json()
            is_online = True
            with open('data_tax-advantaged.json', 'w', encoding='utf-8') as f:
                json.dump(p_data, f, ensure_ascii=False, indent=4)
                
        if r_g.status_code == 200:
            g_data = r_g.json()
            with open('data_taxable.json', 'w', encoding='utf-8') as f:
                json.dump(g_data, f, ensure_ascii=False, indent=4)
    except: pass
    
    if not is_online or not p_data:
        try:
            with open('data_tax-advantaged.json', 'r', encoding='utf-8') as f: p_data = json.load(f)
        except: pass
            
    if not g_data:
        try:
            with open('data_taxable.json', 'r', encoding='utf-8') as f: g_data = json.load(f)
        except: pass
            
    return p_data, g_data, is_online

data, g_data, is_oracle_online = fetch_hybrid_data()

# =========================================================
# 🛡️ [데이터 전처리 레이어] 
# =========================================================
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
            calc_asset += safe_float(raw_data[k].get('총 자산', raw_data[k].get('총자산', 0)))
            calc_profit += safe_float(raw_data[k].get('총 수익', raw_data[k].get('총수익', 0)))
            calc_orig += safe_float(raw_data[k].get('원금', 0))
            
    calc_rate = (calc_profit / calc_orig * 100) if calc_orig > 0 else 0
    return {'총자산': calc_asset, '총수익': calc_profit, '수익률(%)': calc_rate, '원금합': calc_orig, '조회시간': '자체 집계 모드'}

tot = normalize_insight(data)

# =========================================================
# 🪙 가상자산 오라클 로드 로직
# =========================================================
@st.cache_data(ttl=60)
def get_crypto_data():
    ts = int(time.time())
    url = f"http://158.179.172.40:8000/crypto?t={ts}"
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

# =========================================================
# 🚨 NameError 및 크래시 방지를 위한 철벽 사전 계산 로직
# =========================================================
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

# =========================================================
# 📍 사이드바 렌더링 (연동 상태 박스 디자인 일체화)
# =========================================================
with st.sidebar:
    # 💡 사이드바 카드와 동일한 디자인의 연동 상태 박스
    if is_oracle_online:
        status_html = f"""
        <div class='sidebar-card' style='background-color: #e6f4ea; border-color: #34a853; padding: 12px; margin-bottom: 20px; cursor: default;'>
            <div style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
                <span style='font-size: 18px;'>🟢</span>
                <span style='color: #1e8e3e; font-size: 14.5px; font-weight: 800; letter-spacing: -0.5px;'>실시간 데이터 연동 중 (오라클)</span>
            </div>
        </div>
        """
    else:
        status_html = f"""
        <div class='sidebar-card' style='background-color: #fce8e6; border-color: #ea4335; padding: 12px; margin-bottom: 20px; cursor: default;'>
            <div style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
                <span style='font-size: 18px;'>🔴</span>
                <span style='color: #d93025; font-size: 14.5px; font-weight: 800; letter-spacing: -0.5px;'>로컬 백업 데이터 표출 중</span>
            </div>
        </div>
        """
    st.markdown(status_html, unsafe_allow_html=True)

    # 현재 화면에 맞는 시간 가져오기 (기존 로직 유지)
    upd_time = "업데이트 필요"
    if st.session_state.current_view == '절세계좌': upd_time = tot.get('조회시간', '업데이트 필요')
    elif st.session_state.current_view == '일반계좌': upd_time = g_data.get('조회시간', '업데이트 필요') if isinstance(g_data, dict) else '업데이트 필요'
    elif st.session_state.current_view == '가상자산': upd_time = crypto_data.get('update_time', '업데이트 필요') if isinstance(crypto_data, dict) else '업데이트 필요'


    # 현재 화면에 맞는 시간 가져오기
    upd_time = "업데이트 필요"
    if st.session_state.current_view == '절세계좌': upd_time = tot.get('조회시간', '업데이트 필요')
    elif st.session_state.current_view == '일반계좌': upd_time = g_data.get('조회시간', '업데이트 필요') if isinstance(g_data, dict) else '업데이트 필요'
    elif st.session_state.current_view == '가상자산': upd_time = crypto_data.get('update_time', '업데이트 필요') if isinstance(crypto_data, dict) else '업데이트 필요'

    time_str = to_kst(upd_time)

    # 💡 [화면 깨짐 방지] Streamlit 순정 버튼을 CSS로 꾸며서 버튼 글씨 밑에 시간을 새겨넣는 마술!
    st.markdown(f"""
    <style>
    div[data-testid="stSidebar"] button[kind="primary"] {{
        border: 1.5px solid #a0a0a0 !important;
        border-radius: 12px !important;
        background-color: white !important;
        color: #111 !important;
        padding: 12px 15px 36px 15px !important; /* 시간 텍스트가 들어갈 하단 여백 확보 */
        position: relative !important;
        display: block !important;
        width: 100% !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease !important;
        margin-bottom: 15px !important;
    }}
    div[data-testid="stSidebar"] button[kind="primary"]:hover {{
        border-color: #4285F4 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
    }}
    div[data-testid="stSidebar"] button[kind="primary"] p {{
        font-size: 20px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    /* 버튼 글씨 안쪽에 아이콘 추가 */
    div[data-testid="stSidebar"] button[kind="primary"] p::before {{
        content: '🔄 ';
        margin-right: 5px;
    }}
    /* 버튼 껍데기 하단에 날짜/시간을 강제로 렌더링 */
    div[data-testid="stSidebar"] button[kind="primary"]::after {{
        content: '{time_str}';
        position: absolute !important;
        bottom: 12px !important;
        left: 0 !important;
        right: 0 !important;
        text-align: center !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #333 !important;
        letter-spacing: -0.2px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # 순정 버튼 사용으로 화면 터짐 100% 방지
    if st.button("업데이트", key="sidebar_btn_update", type="primary", use_container_width=True):
        fetch_hybrid_data.clear()
        get_crypto_data.clear()
        st.rerun()

    st.radio("카테고리 선택", ("대시보드", "절세계좌", "일반계좌", "가상자산", "퀀트매매"), label_visibility="collapsed", key="menu_sel", on_change=on_menu_change)
    
    # 💡 1. 가상자산 비중 추출 (카드 그리기 전 필수!)
    c_btc = crypto_data.get('btc_pct', 0) if isinstance(crypto_data, dict) else 0
    c_eth = crypto_data.get('eth_pct', 0) if isinstance(crypto_data, dict) else 0
    c_trx = crypto_data.get('trx_pct', 0) if isinstance(crypto_data, dict) else 0

    st.markdown(f"""
    <div id='card-total' class='sidebar-card sidebar-card-dark'>
        <div style='font-size:13px; font-weight:bold; color:#aaaaaa; margin-bottom:6px;'>🌎 총 자산 통합</div>
        <div style='text-align: right;'>
            <div style='font-size:24px; font-weight:600; letter-spacing:-0.5px; line-height: 1.2;'>{fmt(total_asset)} <span style='font-size:13px; font-weight:normal; color:#ddd;'>KRW</span></div>
            <div style='font-size:18px; margin-top:4px; color:#ff4b4b;'><span class='{col(total_profit)}' style='font-weight:bold;'>{fmt(total_profit, True)}</span> <span style='font-size:13.5px; font-weight:normal; color:#ddd;'>({fmt_p1(total_rate)})</span></div>
        </div>
        <div style='margin-top: 15px; padding-top: 12px; border-top: 1px dashed #3a3a3a;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>
                <span style='font-size: 12.5px; color: #999; font-weight: 500;'>🎯 금융자산 <span style='font-size: 13px;'>30</span>억 목표</span>
                <span style='font-size: 13.5px; font-weight: bold; color: #e8c368;'>{(total_asset / 3000000000 * 100):.1f}%</span>
            </div>
            <div style='width: 100%; height: 6px; background-color: #333; border-radius: 3px; overflow: hidden;'>
                <div style='width: {(total_asset / 3000000000 * 100)}%; height: 100%; background: linear-gradient(90deg, #bfa054, #fceabb);'></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div id='card-pension' class='sidebar-card'>
        <div style='font-size:13px; font-weight:bold; color:#777; margin-bottom:6px;'>⏳ 절세계좌</div>
        <div style='text-align: right;'>
            <div style='font-size:21px; font-weight:600; color:#111; letter-spacing:-0.5px; line-height: 1.2;'>{fmt(p_asset_all)} <span style='font-size:12.5px; font-weight:normal; color:#555;'>KRW</span></div>
            <div style='font-size:16px; margin-top:4px; color:#555;'><span class='{col(p_profit_all)}' style='font-weight:bold;'>{fmt(p_profit_all, True)}</span> <span style='font-size:12.5px; font-weight:normal; color:#555;'>({fmt_p1(p_rate_all)})</span></div>
            <div style='font-size:12.5px; color:#888; font-weight:500; margin-top:10px;'>국내 {p_dom_pct:.0f}% / 해외 {p_ovs_pct:.0f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div id='card-general' class='sidebar-card'>
        <div style='font-size:13px; font-weight:bold; color:#777; margin-bottom:6px;'>🌱 일반계좌</div>
        <div style='text-align: right;'>
            <div style='font-size:21px; font-weight:600; color:#111; letter-spacing:-0.5px; line-height: 1.2;'>{fmt(g_asset_all)} <span style='font-size:12.5px; font-weight:normal; color:#555;'>KRW</span></div>
            <div style='font-size:16px; margin-top:4px; color:#555;'><span class='{col(g_profit_all)}' style='font-weight:bold;'>{fmt(g_profit_all, True)}</span> <span style='font-size:12.5px; font-weight:normal; color:#555;'>({fmt_p1(g_rate_all)})</span></div>
            <div style='font-size:12.5px; color:#888; font-weight:500; margin-top:10px;'>국내 {g_dom_pct:.0f}% / 해외 {g_ovs_pct:.0f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div id='card-crypto' class='sidebar-card'>
        <div style='font-size:13px; font-weight:bold; color:#777; margin-bottom:6px;'>🪙 가상자산</div>
        <div style='text-align: right;'>
            <div style='font-size:21px; font-weight:600; color:#111; letter-spacing:-0.5px; line-height: 1.2;'>{fmt(c_tot_sum)} <span style='font-size:12.5px; font-weight:normal; color:#555;'>KRW</span></div>
            <div style='font-size:16px; margin-top:4px; color:#555;'><span class='{col(c_prof_sum)}' style='font-weight:bold;'>{fmt(c_prof_sum, True)}</span> <span style='font-size:12.5px; font-weight:normal; color:#555;'>({fmt_p1(c_rate_sum)})</span></div>
            <div style='font-size:12.5px; color:#888; font-weight:500; margin-top:10px;'>BTC {c_btc:.1f}% / ETH {c_eth:.1f}% / TRX {c_trx:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div id='card-quant' class='sidebar-card' style='display:flex; flex-direction:row; align-items:center; justify-content:center; height: 80px; margin-bottom: 25px;'>
        <div style='font-size:20px; font-weight:800; color:#2c3e50; display:flex; align-items:center; gap:12px; letter-spacing: -0.5px;'>
            <img src='https://cdn-icons-png.flaticon.com/512/4712/4712139.png' style='width:36px; height:36px; object-fit:contain;'>
            퀀트매매
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# 🍩 일반계좌 파이차트 함수 (대시보드에서 사용)
# =========================================================
def draw_pie_charts(g_data):
    if not isinstance(g_data, dict): return
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
                        qty = safe_float(it.get('수량', 0)) # 💡 보유량 추가
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
            p_class = "#FF5252" if row['평가손익'] > 0 else ("#448AFF" if row['평가손익'] < 0 else "#9e9e9e")
            sign = "+" if row['평가손익'] > 0 else ""
            c_code = donut_colors[i % len(donut_colors)]
            qty_str = f"{row['수량']:,.2f}".rstrip('0').rstrip('.') if row['수량'] % 1 != 0 else f"{int(row['수량']):,}" # 보유량 포맷팅
            
            # 💡 items_js에 qty 정보 삽입
            items_js.append({"index": i, "name": row['종목명'], "value": float(row['총자산']), "pct": f"{pct:.1f}%", "logo": logo, "asset": fmt(row['총자산']), "profit": f"{sign}{fmt(row['평가손익'])}", "rate": fmt_p(row['수익률']), "p_class": p_class, "color": c_code, "qty": qty_str})
            list_html += f"<div id='leg-item-{i}' class='legend-item' data-idx='{i}' style='display:flex; justify-content:space-between; align-items:center; padding:10px 12px; border-bottom:1px solid #2a2e39; border-radius:8px; cursor:pointer; margin-bottom:4px;'><div class='leg-left' style='display:flex; align-items:center;'><div class='leg-color' style='width:14px; height:14px; border-radius:4px; margin-right:10px; background-color:{c_code};'></div>{logo}<span class='leg-name' style='color:#e2e8f0; font-size:15px; font-weight:500;'>{row['종목명']}</span></div><span class='leg-pct' style='color:#94a3b8; font-size:15px; font-weight:bold;'>{pct:.1f}%</span></div>"
            
        html_code = f"""
        <html><head><script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script><style>body {{ margin:0; padding:0; font-family:'Apple SD Gothic Neo',sans-serif; background:transparent; user-select:none; }}.box {{ background:#1a1e28; border-radius:15px; padding:25px; display:flex; flex-direction:column; height:500px; border:1px solid #2c3140; box-sizing:border-box; }}.title {{ color:#fff; font-size:19px; font-weight:bold; margin-bottom:20px; }}.content {{ display:flex; height:100%; }}.left-panel {{ flex:1.1; display:flex; flex-direction:column; padding-right:20px; border-right:1px solid #2c3140; }}.hover-panel {{ min-height:100px; margin-bottom:15px; border-bottom:1px dashed #3a3f50; display:flex; flex-direction:column; justify-content:center; }}.list-area {{ flex:1; overflow-y:auto; padding-right:10px; }}.list-area::-webkit-scrollbar {{ width:6px; }}.list-area::-webkit-scrollbar-thumb {{ background:#4b5563; border-radius:3px; }}.chart-area {{ flex:1.2; position:relative; }}.legend-item {{ transition:all 0.2s; }}.legend-item:hover, .legend-item.active {{ background:#2d3240; transform:translateX(5px); border-left:3px solid #4CAF50; }}</style></head>
        <body><div class="box"><div class="title">{title}</div><div class="content"><div class="left-panel"><div class="hover-panel" id="hover-info"><div style='color:#64748b; font-size:13px; text-align:center;'>마우스를 올리면 상세 정보가 표시됩니다.</div></div><div class="list-area">{list_html}</div></div><div class="chart-area" id="pie-chart"></div></div></div>
        <script>
            var itemsData = {json.dumps(items_js, ensure_ascii=False)};
            var chart = echarts.init(document.getElementById('pie-chart'));
            chart.setOption({{ tooltip:{{show:false}}, color:{json.dumps(donut_colors)}, series:[{{ type:'pie', radius:['45%','85%'], itemStyle:{{borderColor:'#1a1e28',borderWidth:3}}, label:{{show:true,position:'inside',formatter:'{{d}}%',color:'#fff',fontSize:12,fontWeight:'bold'}}, data:{json.dumps(chart_data, ensure_ascii=False)} }}] }});
            chart.on('mouseover', function(p){{ updateHover(p.dataIndex); highlightLegend(p.dataIndex); }});
            chart.on('mouseout', function(){{ clearHover(); highlightLegend(-1); }});
            function updateHover(idx){{ 
                var d=itemsData[idx]; 
                // 💡 첨부 이미지처럼 타이틀 밑에 보유 주식수(qty) 라벨 추가
                document.getElementById('hover-info').innerHTML = `<div style='display:flex;align-items:center;margin-bottom:8px;'>${{d.logo}}<span style='color:#fff;font-size:17px;font-weight:bold;'>${{d.name}}</span><span style='margin-left:8px; padding:3px 6px; background:#1e293b; color:#94a3b8; border-radius:4px; font-size:11.5px; font-weight:bold;'>보유 ${{d.qty}}주</span></div><div style='text-align:right;'><span style='color:#f1f5f9;font-size:20px;font-weight:bold;'>${{d.asset}}</span>원<br><span style='color:${{d.p_class}};font-size:14px;font-weight:bold;'>${{d.profit}} (${{d.rate}})</span></div>`; 
            }}
            function clearHover(){{ document.getElementById('hover-info').innerHTML = "<div style='color:#64748b;font-size:13px;text-align:center;'>마우스를 올리면 상세 정보가 표시됩니다.</div>"; }}
            function highlightLegend(idx){{ document.querySelectorAll('.legend-item').forEach(el=>el.classList.remove('active')); if(idx>=0) document.getElementById('leg-item-'+idx).classList.add('active'); }}
        </script></body></html>
        """
        components.html(html_code, height=520)

    st.markdown("<h3 style='margin-top: 30px; margin-bottom: 20px;'>🍩 통합 종목별 상세 비중 (Pie Chart)</h3>", unsafe_allow_html=True)
    df_dom_g = get_detailed_grouped_df(['DOM1', 'DOM2'])
    df_usa_g = get_detailed_grouped_df(['USA1', 'USA2'], is_usa=True)
    
    cb1, cb2 = st.columns(2)
    with cb1: render_interactive_pie_area(df_dom_g, "🌱 일반계좌 통합 상세비중 (한국)")
    with cb2: render_interactive_pie_area(df_usa_g, "🌱 일반계좌 통합 상세비중 (해외)")

# =========================================================
# 🔀 라우팅 제어 로직 (대시보드 화면)
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
                elif r['전일비'] > 0: c_color = '#ff7675' # 💡 고급스러운 밝은 파스텔 레드 (상승)
                elif r['전일비'] < 0: c_color = '#74b9ff' # 💡 고급스러운 밝은 파스텔 블루 (하락)
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
            # 💡 카운트 박스를 Treemap 차트 위로 배치
            st.markdown(f"<div style='text-align:center; padding:12px; background:#2a2e39; border-radius:10px; color:#e2e8f0; font-size:15px; font-weight:bold; margin-bottom:12px;'>상승종목 : <span style='color:#ff7675;'>{pen_up}개</span> &nbsp;&nbsp;|&nbsp;&nbsp; 하락종목 : <span style='color:#74b9ff;'>{pen_dn}개</span></div>", unsafe_allow_html=True)
            st.markdown("<div style='background-color: #1e222d; padding: 5px; border-radius: 15px; margin-bottom: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); overflow: hidden;'>", unsafe_allow_html=True)
            if all_pension_list: st.plotly_chart(render_treemap(all_pension_list, "⏳ 절세계좌 통합 포트폴리오"), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            # 💡 카운트 박스를 Treemap 차트 위로 배치
            st.markdown(f"<div style='text-align:center; padding:12px; background:#2a2e39; border-radius:10px; color:#e2e8f0; font-size:15px; font-weight:bold; margin-bottom:12px;'>상승종목 : <span style='color:#ff7675;'>{gen_up}개</span> &nbsp;&nbsp;|&nbsp;&nbsp; 하락종목 : <span style='color:#74b9ff;'>{gen_dn}개</span></div>", unsafe_allow_html=True)
            st.markdown("<div style='background-color: #1e222d; padding: 5px; border-radius: 15px; margin-bottom: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); overflow: hidden;'>", unsafe_allow_html=True)
            if all_gen_list: st.plotly_chart(render_treemap(all_gen_list, "🌱 일반계좌 통합 (한국+미국) 포트폴리오"), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        draw_pie_charts(g_data)
# =========================================================
# 퀀트매매 화면
# =========================================================
elif st.session_state.current_view == '퀀트매매':
    st.markdown("""
        <div style="background-color:#f8f9fa; padding:20px; border-radius:12px; margin-top:10px; border:1px solid #eaeaea; display:flex; align-items:center; gap:15px;">
            <img src='https://cdn-icons-png.flaticon.com/512/4712/4712139.png' style='width:45px; height:45px;'>
            <div>
                <h3 style="margin:0; padding:0; color:#1a1a1a; letter-spacing:-0.5px;">Quant Trading <span style="font-size:18px; color:#555; font-weight:normal;">(with ZAPPA Bot)</span></h3>
                <div style="font-size:14.5px; color:#666; margin-top:5px;">💡 ZAPPA 단기/퀀트 트레이딩 봇의 실시간 매매 현황 및 알고리즘 성과를 모니터링하는 화면입니다.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# =========================================================
# 🪙 가상자산 상세 화면
# =========================================================
elif st.session_state.current_view == '가상자산':
    st.markdown("""
        <div style="background-color:#f8f9fa; padding:20px; border-radius:12px; margin-top:10px; margin-bottom: 25px; border:1px solid #eaeaea; display:flex; align-items:center; gap:15px;">
            <div style="font-size:40px;">🪙</div>
            <div>
                <h3 style="margin:0; padding:0; color:#1a1a1a; letter-spacing:-0.5px;">가상자산 포트폴리오 <span style="font-size:18px; color:#555; font-weight:normal;">(Oracle 실시간 연동)</span></h3>
                <div style="font-size:14.5px; color:#666; margin-top:5px;">오라클 서버에서 실시간으로 수집하여 렌더링하는 업비트 계좌 데이터입니다.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

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
        pie_items.sort(key=lambda x: x['val'], reverse=True)
        
        c_m = {'KRW': '#d870ad', 'BTC': '#8bc34a', 'ETH': '#00bcd4', 'TRX': '#673ab7'}
        d_c = ['#ff9800', '#f44336', '#9c27b0']
        grad, leg, labels_html = [], "", ""
        curr_p = 0
        
        for idx, it in enumerate(pie_items):
            p = (it['val'] / ca * 100) if ca > 0 else 0
            clr = c_m.get(it['name'], d_c[idx % len(d_c)])
            grad.append(f"{clr} {curr_p}% {curr_p + p}%")
            
            leg += f"<div style='display:flex; align-items:center; gap:6px; font-size:14.5px; color:#333; font-weight:bold;'><div style='width:12px; height:12px; background-color:{clr}; border-radius:50%;'></div>{it['name']} <span style='margin-left:4px;'>{p:.1f}%</span></div>"
            
            if p > 3:
                mid_angle = (curr_p + p / 2) / 100 * 360
                rad = np.radians(mid_angle - 90)
                x = 80 + 55 * np.cos(rad)
                y = 80 + 55 * np.sin(rad)
                labels_html += f"<div style='position:absolute; left:{x}px; top:{y}px; transform:translate(-50%, -50%); font-size:12px; font-weight:bold; color:#fff; text-shadow:1px 1px 2px rgba(0,0,0,0.8); z-index:10;'>{p:.1f}%</div>"
            curr_p += p
            
        conic_str = ", ".join(grad)
        donut_html = f"<div style='display:flex; flex-direction:row; align-items:center; gap:25px;'><div style='display:flex; flex-direction:column; align-items:center;'><div style='position: relative; width: 160px; height: 160px; border-radius: 50%; background: conic-gradient({conic_str}); border: 1px solid #ddd; flex-shrink: 0;'>{labels_html}<div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 45%; height: 45%; background-color: #fff; border-radius: 50%; display:flex; align-items:center; justify-content:center; text-align:center;'><span style='font-size:12.5px; color:#333; font-weight:bold; line-height:1.2;'>보유 비중<br>(%)</span></div></div><div style='font-size:15.5px; font-weight:bold; color:#444; margin-top:15px;'>원금 : {fmt(total_principal)}</div></div><div style='display:flex; flex-direction:column; gap:8px;'>{leg}</div></div>"
        
        top_box = f"<div class='card-main' style='width:100%; display:flex; flex-direction:row; align-items:center; padding:35px 50px; background-color:#ffffff; border:1px solid #ddd; border-radius:15px; margin-bottom:30px;'><div style='flex: 1; border-right: 1px solid #eee; padding-right: 30px;'><div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 20px;'>📊 총 보유자산 비중</div>{donut_html}</div><div style='flex: 1.2; padding-left: 50px;'><div style='text-align:right; margin-bottom:30px;'><div style='font-size: 15px; color: #666; font-weight: bold; margin-bottom:5px;'>총 보유자산</div><div style='font-size: 42px; font-weight: 800; color: #111; line-height: 1;'>{fmt(ca)} <span style='font-size: 22px;'>KRW</span></div><div style='font-size: 18px; font-weight: bold; margin-top: 10px;' class='{col(cp)}'>{fmt(cp, True)} <span style='font-size:16px;'>({fmt_p(cr)})</span></div></div><div style='background:#f9f9f9; padding:20px; border-radius:10px; display:flex; flex-direction:column; gap:12px;'><div style='display:flex; justify-content:space-between;'><span style='color:#666; font-size:15px;'>평가금액</span><span style='color:#111;'>{fmt(ce)}</span></div><div style='display:flex; justify-content:space-between;'><span style='color:#666; font-size:15px;'>현금성(예수금)</span><span style='color:#111;'>{fmt(ck)}</span></div><div style='display:flex; justify-content:space-between;'><span style='color:#666; font-size:15px;'>총 손익</span><span class='{col(cp)}'>{fmt(cp, True)}</span></div></div></div></div>"
        st.markdown(top_box, unsafe_allow_html=True)
        
        st.markdown(f"<h4 style='margin-bottom:10px; font-weight:bold;'>📂 보유 코인 목록</h4><div style='margin-bottom:15px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(ca)}</span> KRW / 총 손익 : <span class='summary-val {col(cp)}'>{fmt(cp, True)} ({fmt_p(cr)})</span></div></div><div style='text-align:right; font-size:13px; color:#555; font-weight:bold; margin-bottom:5px;'>단위 : 원화(KRW)</div>", unsafe_allow_html=True)
        
        t_h = "<table class='main-table'><tr>"
        headers = ['코인명', '비중', '평가금액', '평가손익', '손익률', '보유량', '매입가', '현재가']
        for h in headers: t_h += f"<th style='text-align:center;'>{h}</th>"
        t_h += "</tr>"
        
        t_h += f"<tr class='sum-row'><td style='text-align:center;'>[ 합  계 ]</td><td style='text-align:right; padding-right:15px;'>-</td><td style='text-align:right; padding-right:15px;'>{fmt(ce)}</td><td style='text-align:right; padding-right:15px;' class='{col(cp)}'>{fmt(cp, True)}</td><td style='text-align:right; padding-right:15px;' class='{col(cr)}'>{fmt_p(cr)}</td><td style='text-align:right; padding-right:15px;'>-</td><td style='text-align:right; padding-right:15px;'>-</td><td style='text-align:right; padding-right:15px;'>-</td></tr>"
        
        c_i = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'TRX': 'tron'}
        c_n = {'BTC': '비트코인(BTC)', 'ETH': '이더리움(ETH)', 'TRX': '트론(TRX)'}
        
        if isinstance(cl, list):
            s_cl = sorted([c for c in cl if isinstance(c, dict) and c.get('ticker') != 'KRW'], key=lambda x: safe_float(x.get('eval', 0)), reverse=True)
            for c in s_cl:
                tk = c.get('ticker', '')
                nm = c_n.get(tk, f"{c.get('name', tk)}({tk})")
                icon = f"https://www.google.com/s2/favicons?domain={c_i.get(tk, 'cryptocompare.com')}.org&sz=64"
                logo = f"<div style='display:flex; justify-content:center; align-items:center; gap:8px;'><img src='{icon}' style='width:20px; height:20px; border-radius:50%;'><span>{nm}</span></div>"
                c_pct = (safe_float(c.get('eval', 0)) / ca * 100) if ca > 0 else 0
                
                t_h += f"<tr><td style='text-align:center;'>{logo}</td><td style='text-align:right; padding-right:15px;'>{c_pct:.1f}%</td><td style='text-align:right; padding-right:15px;'>{fmt(c.get('eval',0))}</td><td style='text-align:right; padding-right:15px;' class='{col(c.get('profit',0))}'>{fmt(c.get('profit',0), True)}</td><td style='text-align:right; padding-right:15px;' class='{col(c.get('rate',0))}'>{fmt_p(c.get('rate',0))}</td><td style='text-align:right; padding-right:15px;'>{safe_float(c.get('qty',0)):.6f}</td><td style='text-align:right; padding-right:15px;'>{fmt(c.get('avg_price',0))}</td><td style='text-align:right; padding-right:15px;'>{fmt(c.get('curr_price',0))}</td></tr>"
        
        krw_pct = (ck / ca * 100) if ca > 0 else 0
        t_h += f"<tr style='background-color:#fcfcfc;'><td style='text-align:center;'><div style='display:flex; justify-content:center; align-items:center; gap:8px;'><span style='font-size:18px;'>💵</span><span style='color:#555;'>현금성자산</span></div></td><td style='text-align:right; padding-right:15px;'>{krw_pct:.1f}%</td><td style='text-align:right; padding-right:15px; color:#555;'>{fmt(ck)}</td><td style='text-align:right; padding-right:15px;'>-</td><td style='text-align:right; padding-right:15px;'>-</td><td style='text-align:right; padding-right:15px;'>-</td><td style='text-align:right; padding-right:15px;'>-</td><td style='text-align:right; padding-right:15px;'>-</td></tr></table>"
        st.markdown(t_h, unsafe_allow_html=True)
    else:
        st.info("🔄 오라클 서버에서 실시간 가상자산 데이터를 동기화하는 중입니다...")

# =========================================================
# ⏳ 절세계좌 상세 화면 (Andy님 오더: 상단 대시보드 및 시황/우수종목 완벽 복구)
# =========================================================
elif st.session_state.current_view == '절세계좌':
    st.markdown("<h3 style='margin-top: 5px; margin-bottom: 25px;'>🚀 Andy lee님 [절세계좌] 통합 대시보드 수정</h3>", unsafe_allow_html=True)

    FIXED_ORDER = ['DC', 'IRP', 'PENSION', 'ISA']
    P_MAP = {'DC': '퇴직연금(DC)계좌', 'IRP': '퇴직연금(IRP)계좌', 'PENSION': '연금저축(CMA)계좌', 'ISA': 'ISA(중개형)계좌'}
    
    # Hardcoded item counts requested by user
    ITEM_COUNTS = {'DC': 6, 'PENSION': 5, 'IRP': 1, 'ISA': 4}
    DATE_TAGS = {'DC': '[ 2025.08 ]', 'IRP': '[ 2025.08 ]', 'PENSION': '[ 2025.11 ]', 'ISA': '[ 2025.08 ]'}

    if isinstance(data, dict):
        t_asset = sum(safe_float(data[k].get('총 자산', data[k].get('총자산', 0))) for k in FIXED_ORDER if k in data and isinstance(data[k], dict))
        t_principal = sum(safe_float(data[k].get('원금', 0)) for k in FIXED_ORDER if k in data and isinstance(data[k], dict))
        t_buy_total = sum(safe_float(data[k].get('매입금액', 0)) for k in FIXED_ORDER if k in data and isinstance(data[k], dict))
        
        t_prof_1ago = sum(safe_float(data[k].get('평가손익(1일전)', 0)) for k in FIXED_ORDER if k in data and isinstance(data[k], dict))
        t_prof_7ago = sum(safe_float(data[k].get('평가손익(7일전)', 0)) for k in FIXED_ORDER if k in data and isinstance(data[k], dict))
        t_prof_15ago = sum(safe_float(data[k].get('평가손익(15일전)', 0)) for k in FIXED_ORDER if k in data and isinstance(data[k], dict))
        t_prof_30ago = sum(safe_float(data[k].get('평가손익(30일전)', 0)) for k in FIXED_ORDER if k in data and isinstance(data[k], dict))

        t_prof_principal = t_asset - t_principal
        t_rate_principal = (t_prof_principal / t_principal * 100) if t_principal > 0 else 0

        t_prof_buy = t_asset - t_buy_total
        t_rate_buy = (t_prof_buy / t_buy_total * 100) if t_buy_total > 0 else 0
        
        t_diff_1 = t_prof_buy - t_prof_1ago
        t_diff_7 = t_prof_buy - t_prof_7ago
        t_diff_30 = t_prof_buy - t_prof_30ago

        # ---------------------------------------------------------
        # 💡 [1] 절세계좌 상단 오리지널 UI (도넛 차트 + 15억 프로젝트)
        # ---------------------------------------------------------
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

        st.markdown("<div class='sub-title' style='margin-bottom: 15px;'>💡 ZAPPA의 [절세계좌] 자산 현황 보고</div>", unsafe_allow_html=True)
        
        tax_proj_pct = (t_asset / 1500000000) * 100
        
        html_parts = []
        html_parts.append("<div style='text-align: right; font-size: 13px; color: #555; font-weight: bold; margin-bottom: 5px;'>단위 : 원화(KRW)</div><div class='insight-container'><div class='insight-left'><div class='card-main'><div style='display: flex; gap: 15px; align-items: stretch; margin-bottom: auto;'><div style='flex: 0 0 38%; display: flex; flex-direction: column; align-items: center;'><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 15px; width:100%; text-align:left;'>총 자산</div>")
        html_parts.append(donut_html)
        html_parts.append(f"<div style='font-size: 13.5px; color: #333; font-weight: bold; margin-top: 14px;'><span style='font-size: 12.5px; color: #666;'>원금</span> : {fmt(t_principal)}</div></div><div style='flex: 1; display: flex; flex-direction: column; justify-content: flex-start; padding-top: 5px;'><div class='card-inner' style='padding: 10px 12px; margin-bottom: 8px;'><div style='font-size: 24px; font-weight: 700 !important; color: #111; letter-spacing: normal; line-height: 1; margin-bottom: 6px;'>{fmt(t_asset)}<span style='font-size: 13.5px; font-weight: normal; margin-left: 3px; letter-spacing: normal;'>KRW</span></div><div style='font-size: 13.5px; color: #777; font-weight: normal; line-height: 1;'>[ 전일비 <span class='{col(t_diff_1)}'>{fmt(t_diff_1, True)}</span> / 전주비 <span class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</span> ]</div></div><div style='display: grid; grid-template-columns: auto auto; row-gap: 12px; column-gap: 30px; justify-content: end; align-items: baseline; width: 100%; padding-right: 12px; margin-top: 8px;'><div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>평가금액</div><div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(t_asset - cash_total)}</div><div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>현금성(예수금)</div><div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(cash_total)}</div><div style='color: #777; font-size: 14px; font-weight: normal; text-align: right; line-height: 20px;'>총 손익</div><div style='text-align: right;'><div style='font-size: 18px; font-weight: 600; line-height: 1;' class='{col(t_prof_principal)}'>{fmt(t_prof_principal, True)}</div><div style='font-size: 13.5px; font-weight: 600; margin-top: 3px; line-height: 1;' class='{col(t_rate_principal)}'>{fmt_p(t_rate_principal)}</div></div></div></div></div><div style='margin-top: 20px;'><div style='display: flex; height: 20px; width: 100%; border-radius: 4px; border: 1px solid #ccc; margin-bottom: 6px; overflow: hidden;'>{render_bar(p_dc, '#b4a7d6')}{render_bar(p_irp, '#f4b183')}{render_bar(p_pen, '#a9d18e')}{render_bar(p_isa, '#ffd966')}</div><div style='display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #777; padding: 0 2px; margin-bottom: 16px;'><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#b4a7d6; border-radius:3px;'></div>퇴직연금(DC)</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#f4b183; border-radius:3px;'></div>퇴직연금(IRP)</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#a9d18e; border-radius:3px;'></div>연금저축(CMA)</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#ffd966; border-radius:3px;'></div>ISA(중개형)</div></div><div style='padding: 10px 15px; background: rgba(255,255,255,0.5); border-radius: 10px; border: 1px solid #e8dbad;'><div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'><span style='font-size: 14px; color: #777; font-weight: normal;'>🎯 은퇴자산 목표 15억 프로젝트</span><div style='text-align: right;'><span style='font-size: 14px; font-weight: bold; color: #4a90e2;'>{tax_proj_pct:.1f}%</span></div></div><div style='width: 100%; height: 6px; background-color: #e2e2e2; border-radius: 3px; overflow: hidden;'><div style='width: {tax_proj_pct}%; height: 100%; background: linear-gradient(90deg, #9bc2e6, #4a90e2);'></div></div></div></div></div></div><div class='insight-right'><div class='grid-2x2'>")
        
        for k in FIXED_ORDER:
            if k in data and isinstance(data[k], dict):
                a = data[k]
                a_tot = safe_float(a.get('총 자산', a.get('총자산', 0)))
                a_prin = safe_float(a.get('원금', 0))
                a_prof = a_tot - a_prin
                a_rate = (a_prof / a_prin * 100) if a_prin > 0 else 0
                
                item_count = ITEM_COUNTS.get(k, 0)
                k_date = DATE_TAGS.get(k, '')
                
                html_parts.append(f"<a href='#tax_detail_section' style='text-decoration:none; color:inherit; display:block; height:100%;'><div class='card-sub' style='height:100%; justify-content:space-between;'><div><div style='text-align: right; font-size: 13.5px; color: #888; font-weight: normal; margin-bottom: -2px; line-height: 1;'>{k_date}</div><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 2px;'>{P_MAP[k]}</div><div style='border-bottom: 1px solid #eee; margin-bottom: 6px; margin-top: 2px;'></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 자산</span><span style='font-size: 16px; color: #111; font-weight: normal;'>{fmt(a_tot)}</span></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 손익</span><div style='text-align: right; line-height: 1.2;'><div class='{col(a_prof)}' style='font-size: 16px; font-weight: normal;'>{fmt(a_prof, True)}</div><div class='{col(a_rate)}' style='font-size: 14px; font-weight: normal; margin-top: 1px;'>{fmt_p(a_rate)}</div></div></div></div><div style='font-size: 13.5px; color: #666; font-weight: normal; margin-top: auto; padding-top: 2px; display: flex; justify-content: space-between; align-items: baseline;'><span>* <span style='font-size: 12.5px;'>원금</span> : {fmt(a_prin)}</span><span><span style='font-size: 16px; font-weight: bold; color: #111;'>{item_count}</span> 종목</span></div></div></a>")
        html_parts.append("</div></div></div>")

        # ---------------------------------------------------------
        # 💡 [2] 절세계좌 중단 UI (손익률 우수/부진 종목 및 시황 요약)
        # ---------------------------------------------------------
        tax_items = []
        for k in FIXED_ORDER:
            if k in data and isinstance(data[k], dict):
                details = data[k].get('상세', [])
                if isinstance(details, list):
                    for item in details:
                        if isinstance(item, dict) and item.get('종목명') not in ['[ 합  계 ]', '예수금']:
                            it_copy = item.copy()
                            # Map full account name to abbreviated version for tags
                            abbrev_map = {'DC': 'DC', 'IRP': 'IRP', 'PENSION': 'CMA', 'ISA': 'ISA'}
                            it_copy['계좌'] = abbrev_map.get(k, k)
                            tax_items.append(it_copy)

        tax_best = sorted(tax_items, key=lambda x: safe_float(x.get('수익률(%)', 0)), reverse=True)[:5]
        tax_worst = sorted([it for it in tax_items if safe_float(it.get('수익률(%)', 0)) < 5.0], key=lambda x: safe_float(x.get('수익률(%)', 0)))[:5]

        tax_rise_cnt = sum(1 for it in tax_items if safe_float(it.get('전일비', 0)) > 0.5)
        tax_fall_cnt = sum(1 for it in tax_items if safe_float(it.get('전일비', 0)) < -0.5)
        tax_flat_cnt = len(tax_items) - tax_rise_cnt - tax_fall_cnt

        tax_zappa_html = f"<div style='font-size: 14.5px; line-height: 1.85; color: #444; padding-left: 0px;'><div style='margin-bottom: 22px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> 계좌 현황 및 종목 분석</span><div>현재 전체 포트폴리오 총 손익은 <span class='{col(t_prof_principal)}'><strong>{fmt(t_prof_principal, True)}</strong></span> (<span class='{col(t_rate_principal)}'><strong>{fmt_p(t_rate_principal)}</strong></span>) 이며, <strong>퇴직연금(IRP)계좌</strong>가 계좌별 수익률 1위를 기록 중입니다. 개별 종목에서는 <strong>{short_name(tax_best[0]['종목명']) if tax_best else '우량주'}</strong>가 효자 역할을 수행 중이나, <strong>{short_name(tax_worst[0]['종목명']) if tax_worst else '일부 종목'}</strong> 등은 단기 조정을 겪고 있습니다. 총 <strong>{len(tax_items)}개</strong> 종목 중 전일비 상승종목은 <strong>{tax_rise_cnt}개</strong>, 하락종목은 <strong>{tax_fall_cnt}개</strong>, 보합 <strong>{tax_flat_cnt}개</strong> 입니다.</div></div><div style='margin-bottom: 0px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> 주식 시황 및 향후 대응 전략</span><div>간밤 미국 지표의 끈적한 흐름과 연준의 금리 인하 신중론이 겹치며 변동성이 부각되었습니다. 아웃퍼폼 중인 종목에서 일부 차익 실현하여 현재 <strong>{(p_cash_tot/t_asset*100) if t_asset>0 else 0:.1f}%</strong>인 현금 비중을 선제적으로 확대할 필요가 있습니다.</div></div></div>"

        html_parts.append("<div class='insight-bottom-box' style='display: flex; gap: 20px; align-items: stretch;'><div style='flex: 1; padding-right: 15px; border-right: 1px solid #eaeaea;'><div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; letter-spacing: normal;'>📈 손익률 우수종목 (TOP 5)</div><table class='main-table' style='margin-bottom: 20px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>등락률</th></tr>")
        for idx, it in enumerate(tax_best):
            c_p = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0)); diff_amt = (c_p - (c_p / (1 + d_rate / 100))) if c_p > 0 and d_rate != 0 else 0
            d_class = col(d_rate); diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
            acc_tag = f"<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({it.get('계좌', '')})</span>"
            orig_nm = it.get('종목명', ''); disp_nm = short_name(orig_nm); logo_html = get_logo_html(orig_nm)
            nm_html = f"<td style='line-height:1.3; padding-top:6px; padding-bottom:6px; text-align:left; padding-left:10px;'>{logo_html}{disp_nm}{acc_tag}</td>"
            html_parts.append(f"<tr><td>{idx+1}</td>{nm_html}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td>{diff_html}</tr>")
        html_parts.append("</table><div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px; letter-spacing: normal;'>📉 손익률 부진종목</div><table class='main-table' style='margin-bottom: 0px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>등락률</th></tr>")
        for idx, it in enumerate(tax_worst):
            c_p = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0)); diff_amt = (c_p - (c_p / (1 + d_rate / 100))) if c_p > 0 and d_rate != 0 else 0
            d_class = col(d_rate); diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
            acc_tag = f"<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({it.get('계좌', '')})</span>"
            orig_nm = it.get('종목명', ''); disp_nm = short_name(orig_nm); logo_html = get_logo_html(orig_nm)
            nm_html = f"<td style='line-height:1.3; padding-top:6px; padding-bottom:6px; text-align:left; padding-left:10px;'>{logo_html}{disp_nm}{acc_tag}</td>"
            html_parts.append(f"<tr><td>{idx+1}</td>{nm_html}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td>{diff_html}</tr>")
        html_parts.append(f"</table></div><div style='flex: 1.1; padding-left: 5px;'><div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 8px;'><div style='font-size: 18px; font-weight: bold; color: #111; letter-spacing: normal;'>💡 시황 및 향후 전망</div><div style='font-size: 13.5px; color: #888;'>[ -0.2%p < 보합 < +0.2%p ]</div></div>{tax_zappa_html}</div></div>")
        
        st.markdown("".join(html_parts), unsafe_allow_html=True)

        # ---------------------------------------------------------
        # 📊 기존 테이블 (투자원금 대비 및 매입금액 대비 요약)
        # ---------------------------------------------------------
        st.markdown("<div class='sub-title' style='margin-top:20px;'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(t_prof_principal)}'>{fmt(t_prof_principal, True)} ({fmt_p(t_rate_principal)})</span></div><div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>", unsafe_allow_html=True)

        h1 = ["<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>투자원금</th></tr><tr><th class='th-week'>7일전</th><th class='th-week'>15일전</th><th class='th-week'>30일전</th></tr>"]
        h1.append(f"<tr class='sum-row'><td>[ 합  계 ]</td><td>{fmt(t_asset)}</td><td class='{col(t_prof_principal)}'>{fmt(t_prof_principal, True)}</td><td class='{col(t_prof_7ago)}'>{fmt(t_prof_7ago, True)}</td><td class='{col(t_prof_15ago)}'>{fmt(t_prof_15ago, True)}</td><td class='{col(t_prof_30ago)}'>{fmt(t_prof_30ago, True)}</td><td class='{col(t_rate_principal)}'>{fmt_p(t_rate_principal)}</td><td>{fmt(t_principal)}</td></tr>")
        
        for k in FIXED_ORDER:
            if k in data and isinstance(data[k], dict):
                a = data[k]
                a_tot = safe_float(a.get('총 자산', 0))
                a_prin = safe_float(a.get('원금', 0))
                a_prof = a_tot - a_prin
                a_rate = (a_prof / a_prin * 100) if a_prin > 0 else 0
                
                p7 = safe_float(a.get('평가손익(7일전)', 0))
                p15 = safe_float(a.get('평가손익(15일전)', 0))
                p30 = safe_float(a.get('평가손익(30일전)', 0))
                
                h1.append(f"<tr><td>{P_MAP[k]}</td><td>{fmt(a_tot)}</td><td class='{col(a_prof)}'>{fmt(a_prof, True)}</td><td class='{col(p7)}'>{fmt(p7, True)}</td><td class='{col(p15)}'>{fmt(p15, True)}</td><td class='{col(p30)}'>{fmt(p30, True)}</td><td class='{col(a_rate)}'>{fmt_p(a_rate)}</td><td>{fmt(a_prin)}</td></tr>")
        h1.append("</table>")
        st.markdown("".join(h1), unsafe_allow_html=True)

        st.markdown("<div class='sub-title' style='margin-top:30px;'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(t_prof_buy)}'>{fmt(t_prof_buy, True)} ({fmt_p(t_rate_buy)})</span></div><div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>", unsafe_allow_html=True)

        h2 = ["<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>매입금액</th></tr><tr><th class='th-week'>전일비</th><th class='th-week'>전주비</th><th class='th-week'>전월비</th></tr>"]
        h2.append(f"<tr class='sum-row'><td>[ 합  계 ]</td><td>{fmt(t_asset)}</td><td class='{col(t_prof_buy)}'>{fmt(t_prof_buy, True)}</td><td class='{col(t_diff_1)}'>{fmt(t_diff_1, True)}</td><td class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</td><td class='{col(t_diff_30)}'>{fmt(t_diff_30, True)}</td><td class='{col(t_rate_buy)}'>{fmt_p(t_rate_buy)}</td><td>{fmt(t_buy_total)}</td></tr>")
        
        for k in FIXED_ORDER:
            if k in data and isinstance(data[k], dict):
                a = data[k]
                a_tot = safe_float(a.get('총 자산', 0))
                a_buy = safe_float(a.get('매입금액', 0))
                a_prof = a_tot - a_buy
                a_rate = (a_prof / a_buy * 100) if a_buy > 0 else 0
                
                diff1 = a_prof - safe_float(a.get('평가손익(1일전)', 0))
                diff7 = a_prof - safe_float(a.get('평가손익(7일전)', 0))
                diff30 = a_prof - safe_float(a.get('평가손익(30일전)', 0))
                
                h2.append(f"<tr><td>{P_MAP[k]}</td><td>{fmt(a_tot)}</td><td class='{col(a_prof)}'>{fmt(a_prof, True)}</td><td class='{col(diff1)}'>{fmt(diff1, True)}</td><td class='{col(diff7)}'>{fmt(diff7, True)}</td><td class='{col(diff30)}'>{fmt(diff30, True)}</td><td class='{col(a_rate)}'>{fmt_p(a_rate)}</td><td>{fmt(a_buy)}</td></tr>")
        h2.append("</table>")
        st.markdown("".join(h2), unsafe_allow_html=True)
# ---------------------------------------------------------
        # 🔍 [3] 계좌별 상세 내역 (수정된 플로팅 정렬 배너 - 종목코드 추가)
        # ---------------------------------------------------------
        st.markdown("<div id='tax_detail_section' style='padding-top: 20px; margin-top: -20px;'></div><div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
        
        # 💡 6개의 컬럼으로 나누어 일반계좌와 동일하게 맞춤
        tb1, tb2, tb3, tb4, tb5, tb6 = st.columns(6)
        with tb1:
            st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
            lbl1 = "📊정렬 [ 초기화(●)" if st.session_state.sort_mode == 'init' else "📊정렬 [ 초기화(○)"
            if st.button(lbl1, type="primary" if st.session_state.sort_mode == 'init' else "secondary", key='tax_btn1', on_click=lambda: setattr(st.session_state, 'sort_mode', 'init')): pass
        with tb2:
            lbl2 = "총자산(▼)" if st.session_state.sort_mode == 'asset' else "총자산(▽)"
            if st.button(lbl2, type="primary" if st.session_state.sort_mode == 'asset' else "secondary", key='tax_btn2', on_click=lambda: setattr(st.session_state, 'sort_mode', 'asset')): pass
        with tb3:
            lbl3 = "평가손익(▼)" if st.session_state.sort_mode == 'profit' else "평가손익(▽)"
            if st.button(lbl3, type="primary" if st.session_state.sort_mode == 'profit' else "secondary", key='tax_btn3', on_click=lambda: setattr(st.session_state, 'sort_mode', 'profit')): pass
        with tb4:
            lbl4 = "손익률(▼) ]" if st.session_state.sort_mode == 'rate' else "손익률(▽) ]"
            if st.button(lbl4, type="primary" if st.session_state.sort_mode == 'rate' else "secondary", key='tax_btn4', on_click=lambda: setattr(st.session_state, 'sort_mode', 'rate')): pass
        with tb5:
            lbl5 = "↕️등락률[-]" if st.session_state.show_change_rate else "↕️등락률[+]"
            if st.button(lbl5, type="primary" if st.session_state.show_change_rate else "secondary", key='tax_btn5', on_click=lambda: setattr(st.session_state, 'show_change_rate', not st.session_state.show_change_rate)): pass
        with tb6:
            lbl6 = "💻종목코드[-]" if st.session_state.show_code else "💻종목코드[+]"
            if st.button(lbl6, type="primary" if st.session_state.show_code else "secondary", key='tax_btn6', on_click=lambda: setattr(st.session_state, 'show_code', not st.session_state.show_code)): pass
        st.markdown("<br>", unsafe_allow_html=True)

        for k in FIXED_ORDER:
            if k in data and isinstance(data[k], dict):
                a = data[k]
                with st.expander(f"📂 [ {P_MAP[k]} ] 종목별 현황", expanded=False):
                    details = a.get('상세', [])
                    s_data = next((i for i in details if isinstance(i, dict) and i.get('종목명') == "[ 합  계 ]"), {})
                    st.markdown(f"<div class='summary-text'>● 총 자산 : {fmt(a.get('총 자산',0))} KRW / 수익 : <span class='{col(s_data.get('평가손익',0))}'>{fmt(s_data.get('평가손익',0), True)}</span></div>", unsafe_allow_html=True)
                    
                    # 💡 종목코드 및 등락률 헤더 로직
                    code_th = "<th>종목코드</th>" if st.session_state.show_code else ""
                    th_chg = "<th>등락률</th>" if st.session_state.show_change_rate else ""
                    h3 = [f"<table class='main-table'><tr><th>종목명</th>{code_th}<th>비중</th><th>총 자산</th><th>평가손익</th><th>손익률</th><th>주식수</th><th>매입가</th><th>현재가</th>{th_chg}</tr>"]
                    
                    items = [i for i in details if isinstance(i, dict) and i.get('종목명') != "[ 합  계 ]"]
                    
                    # 정렬 로직 적용
                    if st.session_state.sort_mode == 'asset': items.sort(key=lambda x: safe_float(x.get('총 자산', x.get('총자산', 0))), reverse=True)
                    elif st.session_state.sort_mode == 'profit': items.sort(key=lambda x: safe_float(x.get('평가손익', 0)), reverse=True)
                    elif st.session_state.sort_mode == 'rate': items.sort(key=lambda x: safe_float(x.get('수익률(%)', 0)), reverse=True)

                    for i in ([s_data] + items):
                        if not i: continue
                        is_s = (i.get('종목명') == "[ 합  계 ]")
                        row_cls = "class='sum-row'" if is_s else ""
                        
                        # 종목코드 및 등락률 데이터 반영 로직
                        td_code = f"<td>{'-' if is_s or i.get('코드','-')=='-' else i.get('코드', '')}</td>" if st.session_state.show_code else ""
                        
                        chg_rate = safe_float(i.get('전일비', 0))
                        td_chg = f"<td class='{col(chg_rate)}' style='font-weight:bold;'>{fmt_p(chg_rate)}</td>" if st.session_state.show_change_rate else ""
                        if is_s and st.session_state.show_change_rate: td_chg = "<td>-</td>"

                        h3.append(f"<tr {row_cls}><td>{get_logo_html(i.get('종목명'))}{i.get('종목명','')}</td>{td_code}<td>{i.get('비중',0):.1f}%</td><td>{fmt(i.get('총 자산',0))}</td><td class='{col(i.get('평가손익',0))}'>{fmt(i.get('평가손익',0), True)}</td><td>{fmt_p(i.get('수익률(%)',0))}</td><td>{fmt(i.get('수량','-'))}</td><td>{fmt(i.get('매입가','-'))}</td><td>{fmt(i.get('현재가','-'))}</td>{td_chg}</tr>")
                    h3.append("</table>")
                    st.markdown("".join(h3), unsafe_allow_html=True)

# =========================================================
# [ Part 4 ] 일반계좌 대시보드
# =========================================================
elif st.session_state.current_view == '일반계좌':
    st.markdown("<h3 style='margin-top: 5px; margin-bottom: 25px;'>🚀 Andy lee님 [일반계좌] 통합 대시보드 수정</h3>", unsafe_allow_html=True)

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

    zappa_html = f"<div style='font-size: 14.5px; line-height: 1.85; color: #444; padding-left: 0px;'><div style='margin-bottom: 22px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> [통합] 계좌 현황 요약</span><div>현재 전체 포트폴리오 총 손익은 <span class='{col(t_profit)}'><strong>{fmt(t_profit, True)}</strong></span> (<span class='{col(t_rate)}'><strong>{fmt_p(t_rate)}</strong></span>) 이며, <strong>{best_acc_name}</strong> 계좌가 계좌별 수익률 1위를 기록 중입니다. 총 <strong>{len(all_tradeable)}개</strong> 종목 중 0.5% 초과 상승종목은 <strong>{rise_cnt}개</strong>, 하락종목은 <strong>{fall_cnt}개</strong>, 보합종목은 <strong>{flat_cnt}개</strong> 입니다.</div></div><div style='margin-bottom: 15px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> [국내] 시황 및 전망</span><div>최근 국내 시장은 <strong>{short_name(dom_best[0]['종목명']) if dom_best else '국내 우량주'}</strong> 등 일부 우수 종목이 상승을 견인하고 있으나, <strong>{short_name(dom_worst[0]['종목명']) if dom_worst else '일부 조정주'}</strong> 등은 조정을 받고 있습니다. 실적 기반의 리밸런싱을 권고합니다.</div></div><div style='margin-bottom: 0px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> [해외] 시황 및 전망</span><div>미국 증시는 <strong>{short_name(ovs_best[0]['종목명']) if ovs_best else '빅테크 우량주'}</strong> 위주로 긍정적 흐름을 보이나, <strong>{short_name(ovs_worst[0]['종목명']) if ovs_worst else '단기 하락주'}</strong> 등 부진 섹터는 비중 조절이 필요합니다. 현재 <strong>{(cash_total/t_asset*100) if t_asset>0 else 0:.1f}%</strong>인 현금성(예수금) 비중을 유동적으로 관리하시기 바랍니다.</div></div></div>"

    st.markdown("<div class='sub-title' style='margin-bottom: 15px;'>💡 ZAPPA의 [일반계좌] 자산 현황 보고</div>", unsafe_allow_html=True)
    
    p_cash_donut = (cash_total/t_asset*100) if t_asset>0 else 0
    p_ovs_donut = (ovs_total/t_asset*100) if t_asset>0 else 0
    p_dom_donut = (dom_total/t_asset*100) if t_asset>0 else 0
    
    donut_css = f"background: conic-gradient(#ffffff 0% {p_cash_donut}%, #d9d9d9 {p_cash_donut}% {p_cash_donut+p_ovs_donut}%, #8c8c8c {p_cash_donut+p_ovs_donut}% 100%);"
    donut_html = f"<div style='position: relative; width: 120px; height: 120px; border-radius: 50%; {donut_css} box-shadow: inset 0 0 8px rgba(0,0,0,0.1); border: 1px solid #d0d0d0; flex-shrink: 0; margin: 0 auto;'><div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 35%; height: 35%; background-color: #fffdf2; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.05);'></div><div style='position: absolute; top: 0%; left: 50%; transform: translateX(-50%); font-size: 12.5px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_cash_donut:.0f}%<br>현금성자산</div><div style='position: absolute; top: 55px; right: -15px; font-size: 14px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_ovs_donut:.0f}%<br>해외투자</div><div style='position: absolute; bottom: 42px; left: -20px; font-size: 14px; color: #fff; font-weight: bold; text-align: center; line-height: 1.1; text-shadow: 0px 0px 3px rgba(0,0,0,0.5);'>{p_dom_donut:.0f}%<br>국내투자</div></div>"

    html_parts = []
    html_parts.append("<div style='text-align: right; font-size: 13px; color: #555; font-weight: bold; margin-bottom: 5px;'>단위 : 원화(KRW)</div><div class='insight-container'><div class='insight-left'><div class='card-main'><div style='display: flex; gap: 15px; align-items: stretch; margin-bottom: auto;'><div style='flex: 0 0 38%; display: flex; flex-direction: column; align-items: center;'><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 15px; width:100%; text-align:left;'>총 자산</div>")
    html_parts.append(donut_html)
    html_parts.append(f"<div style='font-size: 13.5px; color: #333; font-weight: bold; margin-top: 14px;'><span style='font-size: 12.5px; color: #666;'>원금</span> : {fmt(t_original_sum)}</div></div><div style='flex: 1; display: flex; flex-direction: column; justify-content: flex-start; padding-top: 5px;'><div class='card-inner' style='padding: 10px 12px; margin-bottom: 8px;'><div style='font-size: 24px; font-weight: 700 !important; color: #111; letter-spacing: normal; line-height: 1; margin-bottom: 6px;'>{fmt(t_asset)}<span style='font-size: 13.5px; font-weight: normal; margin-left: 3px; letter-spacing: normal;'>KRW</span></div><div style='font-size: 13.5px; color: #777; font-weight: normal; line-height: 1;'>[ 전일비 <span class='{col(t_diff)}'>{fmt(t_diff, True)}</span> / 전주비 <span class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</span> ]</div></div><div style='display: grid; grid-template-columns: auto auto; row-gap: 12px; column-gap: 30px; justify-content: end; align-items: baseline; width: 100%; padding-right: 12px; margin-top: 8px;'><div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>평가금액</div><div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(t_asset - cash_total)}</div><div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>현금성(예수금)</div><div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(cash_total)}</div><div style='color: #777; font-size: 14px; font-weight: normal; text-align: right; line-height: 20px;'>총 손익</div><div style='text-align: right;'><div style='font-size: 18px; font-weight: 600; line-height: 1;' class='{col(t_profit)}'>{fmt(t_profit, True)}</div><div style='font-size: 13.5px; font-weight: 600; margin-top: 3px; line-height: 1;' class='{col(t_rate)}'>{fmt_p(t_rate)}</div></div></div></div></div><div style='margin-top: 20px;'><div style='display: flex; height: 20px; width: 100%; border-radius: 4px; border: 1px solid #ccc; margin-bottom: 6px; overflow: hidden;'>{render_bar(p_dom1, '#b4a7d6')}{render_bar(p_dom2, '#f4b183')}{render_bar(p_usa1, '#a9d18e')}{render_bar(p_usa2, '#ffd966')}</div><div style='display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #777; padding: 0 2px; margin-bottom: 16px;'><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#b4a7d6; border-radius:3px;'></div>키움증권(국내Ⅰ)</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#f4b183; border-radius:3px;'></div>삼성증권(국내Ⅱ)</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#a9d18e; border-radius:3px;'></div>키움증권(해외Ⅰ)</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#ffd966; border-radius:3px;'></div>키움증권(해외Ⅱ)</div></div><div style='padding: 10px 15px; background: rgba(255,255,255,0.5); border-radius: 10px; border: 1px solid #e8dbad;'><div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'><span style='font-size: 14px; color: #777; font-weight: normal;'>🎯 주식투자 자산 15억 프로젝트</span><div style='text-align: right;'><span style='font-size: 14px; font-weight: bold; color: #4a90e2;'>{progress_pct:.1f}%</span></div></div><div style='width: 100%; height: 6px; background-color: #e2e2e2; border-radius: 3px; overflow: hidden;'><div style='width: {progress_pct}%; height: 100%; background: linear-gradient(90deg, #9bc2e6, #4a90e2);'></div></div></div></div></div></div><div class='insight-right'><div class='grid-2x2'>")
    for k in GEN_ACC_ORDER:
        if k in g_data and isinstance(g_data[k], dict):
            a = g_data[k]
            acc_num_map = {'DOM1': '[ 6312-5329 ]', 'DOM2': '[ 7162669785-01 ]', 'USA1': '[ 6312-5329 ]', 'USA2': '[ 6443-5993 ]'}
            details = a.get('상세', [])
            item_count = len([i for i in details if isinstance(i, dict) and i.get('종목명') not in ['[ 합  계 ]', '예수금']]) if isinstance(details, list) else 0
            html_parts.append(f"<a href='#gen_detail_section' style='text-decoration:none; color:inherit; display:block; height:100%;'><div class='card-sub' style='height:100%; justify-content:space-between;'><div><div style='text-align: right; font-size: 13.5px; color: #666; font-weight: normal; margin-bottom: -2px; line-height: 1;'>{acc_num_map[k]}</div><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 2px;'>{nm_table[k]}</div><div style='border-bottom: 1px solid #eee; margin-bottom: 6px; margin-top: 2px;'></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 자산</span><span style='font-size: 16px; color: #111; font-weight: normal;'>{fmt(safe_float(a.get('총자산_KRW', 0)))}</span></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 손익</span><div style='text-align: right; line-height: 1.2;'><div class='{col(a.get('총수익_KRW', 0))}' style='font-size: 16px; font-weight: normal;'>{fmt(safe_float(a.get('총수익_KRW', 0)), True)}</div><div class='{col(safe_float(a.get('총수익_KRW',0))/principals[k]*100 if principals[k] else 0)}' style='font-size: 14px; font-weight: normal; margin-top: 1px;'>{fmt_p(safe_float(a.get('총수익_KRW',0))/principals[k]*100 if principals[k] else 0)}</div></div></div></div><div style='font-size: 13.5px; color: #666; font-weight: normal; margin-top: auto; padding-top: 2px; display: flex; justify-content: space-between; align-items: baseline;'><span>* <span style='font-size: 12.5px;'>원금</span> : {fmt(principals[k])}</span><span><span style='font-size: 16px; font-weight: bold; color: #111;'>{item_count}</span> 종목</span></div></div></a>")
    html_parts.append("</div></div></div>")
    
    html_parts.append("<div class='insight-bottom-box' style='display: flex; gap: 20px; align-items: stretch;'><div style='flex: 1; padding-right: 15px; border-right: 1px solid #eaeaea;'><div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; letter-spacing: normal;'>📈 [국내] 손익률 우수종목</div><table class='main-table' style='margin-bottom: 20px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>등락률</th></tr>")
    for idx, it in enumerate(dom_best):
        c_p = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0)); diff_amt = (c_p - (c_p / (1 + d_rate / 100))) if c_p > 0 and d_rate != 0 else 0
        d_class = col(d_rate); diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
        acc_tag = f"<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({it.get('계좌', '')})</span>"
        orig_nm = it.get('종목명', ''); disp_nm = short_name(orig_nm); logo_html = get_logo_html(orig_nm)
        nm_html = f"<td style='line-height:1.3; padding-top:6px; padding-bottom:6px; text-align:left; padding-left:10px;'>{logo_html}{disp_nm}{acc_tag}</td>"
        html_parts.append(f"<tr><td>{idx+1}</td>{nm_html}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td>{diff_html}</tr>")
    html_parts.append("</table><div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px; letter-spacing: normal;'>📉 [국내] 손익률 부진종목</div><table class='main-table' style='margin-bottom: 25px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>등락률</th></tr>")
    for idx, it in enumerate(dom_worst):
        c_p = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0)); diff_amt = (c_p - (c_p / (1 + d_rate / 100))) if c_p > 0 and d_rate != 0 else 0
        d_class = col(d_rate); diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
        acc_tag = f"<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({it.get('계좌', '')})</span>"
        orig_nm = it.get('종목명', ''); disp_nm = short_name(orig_nm); logo_html = get_logo_html(orig_nm)
        nm_html = f"<td style='line-height:1.3; padding-top:6px; padding-bottom:6px; text-align:left; padding-left:10px;'>{logo_html}{disp_nm}{acc_tag}</td>"
        html_parts.append(f"<tr><td>{idx+1}</td>{nm_html}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td>{diff_html}</tr>")
    html_parts.append("</table><hr style='border:0; border-top:1px dashed #ddd; margin: 25px 0;'>")
    
    fx_rate = safe_float(g_data.get('환율', 1443.1))
    html_parts.append("<div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; letter-spacing: normal;'>📈 [해외] 손익률 우수종목</div><table class='main-table' style='margin-bottom: 20px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익(KRW)</th><th>등락률</th></tr>")
    for idx, it in enumerate(ovs_best):
        c_p = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0)); diff_amt = (c_p - (c_p / (1 + d_rate / 100))) * fx_rate if c_p > 0 and d_rate != 0 else 0
        d_class = col(d_rate); diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
        acc_tag = f"<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({it.get('계좌', '')})</span>"
        orig_nm = it.get('종목명', ''); disp_nm = short_name(orig_nm); logo_html = get_logo_html(orig_nm)
        nm_html = f"<td style='line-height:1.3; padding-top:6px; padding-bottom:6px; text-align:left; padding-left:10px;'>{logo_html}{disp_nm}{acc_tag}</td>"
        html_parts.append(f"<tr><td>{idx+1}</td>{nm_html}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(safe_float(it.get('평가손익', 0))*fx_rate)}'>{fmt(safe_float(it.get('평가손익', 0))*fx_rate, True)}</td>{diff_html}</tr>")
    html_parts.append("</table><div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px; letter-spacing: normal;'>📉 [해외] 손익률 부진종목</div><table class='main-table' style='margin-bottom: 0px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익(KRW)</th><th>등락률</th></tr>")
    for idx, it in enumerate(ovs_worst):
        c_p = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0)); diff_amt = (c_p - (c_p / (1 + d_rate / 100))) * fx_rate if c_p > 0 and d_rate != 0 else 0
        d_class = col(d_rate); diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
        acc_tag = f"<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({it.get('계좌', '')})</span>"
        orig_nm = it.get('종목명', ''); disp_nm = short_name(orig_nm); logo_html = get_logo_html(orig_nm)
        nm_html = f"<td style='line-height:1.3; padding-top:6px; padding-bottom:6px; text-align:left; padding-left:10px;'>{logo_html}{disp_nm}{acc_tag}</td>"
        html_parts.append(f"<tr><td>{idx+1}</td>{nm_html}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(safe_float(it.get('평가손익', 0))*fx_rate)}'>{fmt(safe_float(it.get('평가손익', 0))*fx_rate, True)}</td>{diff_html}</tr>")
    html_parts.append("</table></div><div style='flex: 1.1; padding-left: 5px;'><div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 8px;'><div style='font-size: 18px; font-weight: bold; color: #111; letter-spacing: normal;'>💡 시황 및 향후 전망</div><div style='font-size: 13.5px; color: #888;'>[ -0.5%p < 보합 < +0.5%p ]</div></div>{zappa_html}</div></div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)

    # ---------------- 일반계좌 요약 테이블 ----------------
    unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"
    st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(t_profit)}'>{fmt(t_profit, True)} ({fmt_p(t_rate)})</span></div></div>", unsafe_allow_html=True)

    h1_table = "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>투자원금</th></tr><tr><th class='th-week'>7일전</th><th class='th-week'>15일전</th><th class='th-week'>30일전</th></tr>"
    h1 = [unit_html, h1_table, f"<tr class='sum-row'><td>[ 합  계 ]</td><td>{fmt(t_asset)}</td><td class='{col(t_profit)}'>{fmt(t_profit, True)}</td><td class='{col(t_prof_7ago)}'>{fmt(t_prof_7ago, True)}</td><td class='{col(t_prof_15ago)}'>{fmt(t_prof_15ago, True)}</td><td class='{col(t_prof_30ago)}'>{fmt(t_prof_30ago, True)}</td><td class='{col(t_rate)}'>{fmt_p(t_rate)}</td><td>{fmt(t_original_sum)}</td></tr>"]
    for k in GEN_ACC_ORDER:
        if k in g_data and isinstance(g_data[k], dict):
            a = g_data[k]
            a_tot = safe_float(a.get('총자산_KRW',0)); a_prof = safe_float(a.get('총수익_KRW',0))
            p7 = safe_float(a.get('평가손익(7일전)',0)); p15 = safe_float(a.get('평가손익(15일전)',0)); p30 = safe_float(a.get('평가손익(30일전)',0))
            h1.append(f"<tr><td>{nm_table[k]}</td><td>{fmt(a_tot)}</td><td class='{col(a_prof)}'>{fmt(a_prof, True)}</td><td class='{col(p7)}'>{fmt(p7, True)}</td><td class='{col(p15)}'>{fmt(p15, True)}</td><td class='{col(p30)}'>{fmt(p30, True)}</td><td class='{col(a_prof/principals[k]*100 if principals[k] else 0)}'>{fmt_p(a_prof/principals[k]*100 if principals[k] else 0)}</td><td>{fmt(principals[k])}</td></tr>")
    h1.append("</table>")
    st.markdown("".join(h1), unsafe_allow_html=True)

    ag_tot = t_asset - t_buy_total
    ay_tot = (ag_tot / t_buy_total * 100) if t_buy_total > 0 else 0
    st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(ag_tot)}'>{fmt(ag_tot, True)} ({fmt_p(ay_tot)})</span></div>", unsafe_allow_html=True)

    h2_table = "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>매입금액</th></tr><tr><th class='th-week'>전일비</th><th class='th-week'>전주비</th><th class='th-week'>전월비</th></tr>"
    h2 = [unit_html, h2_table, f"<tr class='sum-row'><td>[ 합  계 ]</td><td>{fmt(t_asset)}</td><td class='{col(ag_tot)}'>{fmt(ag_tot, True)}</td><td class='{col(t_diff)}'>{fmt(t_diff, True)}</td><td class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</td><td class='{col(t_diff_30)}'>{fmt(t_diff_30, True)}</td><td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td><td>{fmt(t_buy_total)}</td></tr>"]
    
    for k in GEN_ACC_ORDER:
        if k in g_data and isinstance(g_data[k], dict):
            a = g_data[k]
            buy_krw = safe_float(a.get('매입금액_KRW', 0))
            ag_acc = safe_float(a.get('총자산_KRW', 0)) - buy_krw
            ay_acc = (ag_acc / buy_krw * 100) if buy_krw > 0 else 0
            a_prof = safe_float(a.get('총수익_KRW', 0))
            diff_7_acc = a_prof - safe_float(a.get('평가손익(7일전)', 0))
            diff_30_acc = a_prof - safe_float(a.get('평가손익(30일전)', 0))
            h2.append(f"<tr><td>{nm_table[k]}</td><td>{fmt(safe_float(a.get('총자산_KRW',0)))}</td><td class='{col(ag_acc)}'>{fmt(ag_acc, True)}</td><td class='{col(acc_1d_diff.get(k, 0))}'>{fmt(acc_1d_diff.get(k, 0), True)}</td><td class='{col(diff_7_acc)}'>{fmt(diff_7_acc, True)}</td><td class='{col(diff_30_acc)}'>{fmt(diff_30_acc, True)}</td><td class='{col(ay_acc)}'>{fmt_p(ay_acc)}</td><td>{fmt(buy_krw)}</td></tr>")
    h2.append("</table>")
    st.markdown("".join(h2), unsafe_allow_html=True)

    # ---------------- 일반계좌 상세 ----------------
    st.markdown("<div id='gen_detail_section' style='padding-top: 20px; margin-top: -20px;'></div><div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
    b1, b2, b3, b4, b5, b6 = st.columns(6)
    with b1:
        st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
        lbl1 = "📊정렬 [ 초기화(●)" if st.session_state.gen_sort_mode == 'init' else "📊정렬 [ 초기화(○)"
        if st.button(lbl1, type="primary" if st.session_state.gen_sort_mode == 'init' else "secondary", on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'init')): pass
    with b2:
        lbl2 = "총자산(▼)" if st.session_state.gen_sort_mode == 'asset' else "총자산(▽)"
        if st.button(lbl2, type="primary" if st.session_state.gen_sort_mode == 'asset' else "secondary", on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'asset')): pass
    with b3:
        lbl3 = "평가손익(▼)" if st.session_state.gen_sort_mode == 'profit' else "평가손익(▽)"
        if st.button(lbl3, type="primary" if st.session_state.gen_sort_mode == 'profit' else "secondary", on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'profit')): pass
    with b4:
        lbl4 = "손익률(▼) ]" if st.session_state.gen_sort_mode == 'rate' else "손익률(▽) ]"
        if st.button(lbl4, type="primary" if st.session_state.gen_sort_mode == 'rate' else "secondary", on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'rate')): pass
    with b5:
        lbl5 = "↕️등락률[-]" if st.session_state.gen_show_change_rate else "↕️등락률[+]"
        if st.button(lbl5, type="primary" if st.session_state.gen_show_change_rate else "secondary", on_click=lambda: setattr(st.session_state, 'gen_show_change_rate', not st.session_state.gen_show_change_rate)): pass
    with b6:
        lbl6 = "💻종목코드[-]" if st.session_state.show_code else "💻종목코드[+]"
        if st.button(lbl6, type="primary" if st.session_state.show_code else "secondary", on_click=lambda: setattr(st.session_state, 'show_code', not st.session_state.show_code)): pass
    st.markdown("<br>", unsafe_allow_html=True)

    for k in GEN_ACC_ORDER:
        if k in g_data and isinstance(g_data[k], dict):
            a = g_data[k]
            is_usa = 'USA' in k
            with st.expander(f"📂 [ {nm_table_expander[k]} ] 종목별 현황", expanded=False):
                details = a.get('상세', [])
                s_data = next((i for i in details if isinstance(i, dict) and i.get('종목명') == "[ 합  계 ]"), {}) if isinstance(details, list) else {}
                curr_asset = safe_float(a.get('총자산_KRW', 0)); a_prof = safe_float(a.get('총수익_KRW', 0))
                a_rate = (a_prof / principals[k] * 100) if principals[k] else 0
                
                st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(curr_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(a_prof)}'>{fmt(a_prof, True)} ({fmt_p(a_rate)})</span></div></div>", unsafe_allow_html=True)
                
                rate_val = safe_float(g_data.get('환율', 1443.1))
                
                if is_usa:
                    u_c1, u_c2 = st.columns([8.8, 1.2])
                    with u_c2:
                        currency_mode = st.selectbox("표기단위", options=["[원화(KRW)]", "[달러(USD)]", "[원화/달러]"], index=2, label_visibility="collapsed", key=f"curr_sel_box_{k}")
                    u_html = ""
                else:
                    currency_mode = "[원화(KRW)]"
                    u_html = f"<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"
                
                code_th = "<th>종목코드</th>" if st.session_state.show_code else ""
                h3_table_html = f"<table class='main-table'><tr><th>종목명</th>{code_th}<th>비중</th><th>총 자산</th><th>평가손익</th><th>손익률</th><th>주식수</th><th>매입가</th><th>현재가</th>" + ("<th>등락률</th>" if st.session_state.gen_show_change_rate else "") + "</tr>"
                h3 = [u_html, h3_table_html]
                
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
                    if not i or (i.get('종목명') == "예수금" and safe_float(i.get('총자산', 0)) == 0 and safe_float(s_data.get('총자산', 0)) > 0): continue
                    is_s = (i.get('종목명') == "[ 합  계 ]")
                    row = f"<tr class='sum-row'>" if is_s else "<tr>"
                    orig_nm = '피그마' if i.get('종목명') == 'Figma' else str(i.get('종목명', ''))
                    
                    if is_s: row += f"<td>{orig_nm}</td>"
                    elif '예수금' in orig_nm or '현금' in orig_nm: row += f"<td style='text-align:left; padding-left:15px;'><span style='font-size:16px; margin-right:6px; vertical-align:middle;'>💵</span>{orig_nm}</td>"
                    else: row += f"<td style='text-align:left; padding-left:15px;'>{get_logo_html(orig_nm)}{orig_nm}</td>"
                    
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
                        if is_s or i.get('종목명') == '예수금': row += "<td>-</td>"
                        else: row += f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{diff_amt_str}</div><div class='{d_class}' style='font-size:13px;'>{d_rate_str}</div></td>"
                    row += "</tr>"
                    h3.append(row)
                h3.append("</table>")
                st.markdown("".join(h3), unsafe_allow_html=True)















