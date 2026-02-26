import streamlit as st
import json
import warnings
import google.generativeai as genai
import Andy_pension_v2
import os
import re

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="Andy's Asset Dashboard")

css = """
<style>
.block-container{padding-top:3rem!important;padding-bottom:5rem!important;}
h3{font-size:26px!important;font-weight:bold;margin-bottom:10px;}
.sub-title{font-size:22px!important;font-weight:bold;margin:25px 0 10px;}
.main-table{width:100%;border-collapse:collapse;font-size:15px;text-align:center;margin-bottom:10px;}
.main-table th{background-color:#f2f2f2;padding:10px;border:1px solid #ddd;font-weight:bold!important; vertical-align:middle;}
.main-table td{padding:8px;border:1px solid #ddd;vertical-align:middle;}
.sum-row td{background-color:#fff9e6;font-weight:bold!important;}
.red{color:#FF2323!important;} .blue{color:#0047EB!important;}
.insight-box{background-color:#f0f4f8;padding:20px;border-radius:10px;border-left:5px solid #007bff;margin-bottom:25px;}
.box-title{font-size:20px!important;font-weight:bold;margin-bottom:15px;display:block;color:#333;}
.summary-text {font-size: 16px !important;font-weight: bold !important;color: #333;margin-bottom: 10px;}
.summary-val {font-size: 20px !important;}
.main-table th.th-eval { border-right: none !important; }
.main-table th.th-blank { border-left: none !important; border-bottom: none !important; padding: 0 !important; }
.main-table th.th-week { border-left: 1px solid #ddd !important; border-top: 1px solid #ddd !important; font-size: 13.5px; }
.zappa-icon {font-family: "Segoe UI Emoji", "Apple Color Emoji", sans-serif !important;font-size: 32px !important;}

/* =========================================================
   [진짜 최종] 우측 하단 고정 & 단어 길이 상관없이 완벽한 대칭(1칸) 간격 구현
   ========================================================= */

/* 1. 배너 틀: 우측 하단 고정, 글자 너비에 딱 맞춤(max-content) */
div[data-testid="stColumns"]:has(#zappa-menu),
div[data-testid="stHorizontalBlock"]:has(#zappa-menu) {
    position: fixed !important;
    bottom: 30px !important;
    right: 30px !important; /* 우측 끝으로 이동 */
    left: auto !important; /* 중앙 정렬 속성 해제 */
    transform: none !important; /* 중앙 정렬 속성 해제 */
    width: max-content !important; /* 고정 크기(600px) 버리고 내용물에 딱 맞춤! */
    background: rgba(255, 255, 255, 0.98) !important;
    padding: 8px 10px !important; /* 배너 겉 테두리 여유 공간 */
    border-radius: 8px !important; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important;
    border: 1px solid #e5e7eb !important;
    z-index: 999999 !important;
    display: flex !important;
    align-items: center !important; 
    gap: 0 !important; 
}

/* 2. 유령 공간 완전 소멸 (마커로 인한 레이아웃 틀어짐 방지) */
div.element-container:has(#zappa-menu) {
    display: none !important;
    position: absolute !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* 3. 컬럼 강제 비율(flex:1) 해제, 글자 크기만큼만 공간 차지하게 변경 */
div[data-testid="stColumns"]:has(#zappa-menu) > div[data-testid="column"],
div[data-testid="stHorizontalBlock"]:has(#zappa-menu) > div[data-testid="column"] {
    flex: 0 0 auto !important; 
    width: auto !important;
    min-width: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

div[data-testid="stColumns"]:has(#zappa-menu) div[data-testid="stButton"],
div[data-testid="stHorizontalBlock"]:has(#zappa-menu) div[data-testid="stButton"] {
    margin: 0 !important;
    padding: 0 !important;
    width: auto !important;
}

/* 4. 버튼 본체 & 완벽한 1칸 대칭: 
   글자 양옆으로 정확히 16px씩 패딩을 주면, 파이프(|)가 양쪽 단어 정중앙에 위치하게 됨 */
div[data-testid="stColumns"]:has(#zappa-menu) button,
div[data-testid="stHorizontalBlock"]:has(#zappa-menu) button {
    width: auto !important; 
    background: transparent !important; 
    border: none !important; 
    border-right: 1.5px solid #d1d5db !important; /* 구분선 */
    border-radius: 0 !important; 
    padding: 0 16px !important; /* 양옆 1칸 대칭의 핵심 */
    height: 24px !important; 
    min-height: 24px !important;
    color: #8c8c8c !important; /* 기본 회색 */
    font-size: 15px !important; 
    font-weight: 600 !important; 
    white-space: nowrap !important; 
    box-shadow: none !important; 
    transition: color 0.1s ease !important; 
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* 마지막 버튼(종목코드) 우측 파이프 선 삭제 */
div[data-testid="stColumns"]:has(#zappa-menu) > div[data-testid="column"]:last-child button,
div[data-testid="stHorizontalBlock"]:has(#zappa-menu) > div[data-testid="column"]:last-child button {
    border-right: none !important;
}

/* 5. 내부 텍스트(p) 정렬 및 여백 완전 초기화 */
div[data-testid="stColumns"]:has(#zappa-menu) button p,
div[data-testid="stHorizontalBlock"]:has(#zappa-menu) button p {
    color: inherit !important;
    font-size: 14.5px !important; /* 세련된 사이즈 */
    font-weight: 600 !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
    text-align: center !important;
}

/* 6. 호버(Hover) 시 검은색 텍스트 반응 */
div[data-testid="stColumns"]:has(#zappa-menu) button:hover,
div[data-testid="stHorizontalBlock"]:has(#zappa-menu) button:hover {
    color: #111111 !important; 
    background: transparent !important; 
}

/* 7. 클릭된 상태(Primary) 검은색 텍스트 고정 */
div[data-testid="stColumns"]:has(#zappa-menu) button[kind="primary"],
div[data-testid="stHorizontalBlock"]:has(#zappa-menu) button[kind="primary"] {
    background: transparent !important; 
    border: none !important;
    border-right: 1.5px solid #d1d5db !important; 
    color: #111111 !important; 
}

div[data-testid="stColumns"]:has(#zappa-menu) > div[data-testid="column"]:last-child button[kind="primary"],
div[data-testid="stHorizontalBlock"]:has(#zappa-menu) > div[data-testid="column"]:last-child button[kind="primary"] {
    border-right: none !important;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

if 'sort_mode' not in st.session_state: st.session_state.sort_mode = 'init'
if 'show_code' not in st.session_state: st.session_state.show_code = False
if 'init' not in st.session_state:
    with st.spinner("데이터 업데이트 중..."): Andy_pension_v2.generate_asset_data()
    st.session_state['init'] = True
    st.cache_data.clear()

# ==========================================
# 좌측 ZAPPA 엔진 로직
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style='display:flex; align-items:center; gap:10px; margin-bottom:20px;'>
            <span class='zappa-icon'>🤖</span>
            <span style='font-size:22px; font-weight:bold; color:#333;'>ZAPPA AI 코딩 엔진</span>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        key = st.secrets.get("GOOGLE_API_KEY")
        if key:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            pmt = st.text_area("AI 엔진에게 요청", placeholder="수정 사항을 입력하세요...")
            if st.button("개선 사항 반영하기"):
                res = model.generate_content("Streamlit 수정: " + pmt)
                st.code(res.text)
        else: st.info("API Key 설정 필요")
    except Exception: st.error("엔진 연결 지연")

def fmt(v, sign=False):
    try:
        val = int(float(v))
        if sign and val > 0: return f"+{val:,}"
        return f"{val:,}"
    except: return str(v)

def fmt_p(v):
    try:
        val = float(v)
        return f"▲{val:.2f}%" if val > 0 else (f"▼{abs(val):.2f}%" if val < 0 else "0.00%")
    except: return str(v)

def col(v):
    try:
        val = float(v)
        return "red" if val > 0 else ("blue" if val < 0 else "")
    except: return ""

def clean_label(lbl):
    return re.sub(r'\s*\(\d{2}\.\d+월\)', '', lbl)

@st.cache_data(ttl=60)
def load():
    try:
        with open('assets.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return None

data = load()
if not data: st.stop()
tot = data.get("_total", {})

c1, c2 = st.columns([8.5, 1.5])
with c1: st.markdown("<h3>🚀 이상혁(Andy lee)님 절세계좌 통합 대시보드</h3>", unsafe_allow_html=True)
with c2:
    if st.button("🔄 업데이트", use_container_width=True):
        Andy_pension_v2.generate_asset_data(); st.cache_data.clear(); st.rerun()

st.markdown(f"<div style='text-align:right;font-size:14px;color:#555;margin:-10px 0 10px;'>[{tot.get('조회시간')}]</div>", unsafe_allow_html=True)

if "_insight" in data:
    ins = ["<div class='insight-box'><span class='box-title'><u>💡 절세 자산 현황 요약</u></span>"]
    for line in data["_insight"]:
        if "조회 기준" not in line: ins.append(f"<p style='margin-bottom:5px;'>• {line}</p>")
    ins.append("</div>")
    st.markdown("".join(ins), unsafe_allow_html=True)

unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"

# --- [1] 투자금 대비 자산 현황 ---
st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(tot.get('총 자산',0))}</span> / 총 수익 : <span class='summary-val {col(tot.get('총 수익',0))}'>{fmt(tot.get('총 수익',0), True)} ({fmt_p(tot.get('수익률(%)',0))})</span></div>", unsafe_allow_html=True)

h1 = [unit_html, """
<table class='main-table'>
  <tr>
    <th rowspan='2'>계좌 구분</th>
    <th rowspan='2'>총 자산</th>
    <th rowspan='2' class='th-eval'>평가손익</th>
    <th colspan='3' class='th-blank'>&nbsp;</th>
    <th rowspan='2'>수익률</th>
    <th rowspan='2'>투자원금</th>
  </tr>
  <tr>
    <th class='th-week'>7일전</th>
    <th class='th-week'>15일전</th>
    <th class='th-week'>30일전</th>
  </tr>
"""]

ty, tg, ta, to = tot.get('수익률(%)',0), tot.get('총 수익',0), tot.get('총 자산',0), tot.get('원금합',0)

td7_tot_1 = (ta - tot.get('평가손익(7일전)', 0)) - to
td15_tot_1 = (ta - tot.get('평가손익(15일전)', 0)) - to
td30_tot_1 = (ta - tot.get('평가손익(30일전)', 0)) - to

h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(ta)}</td><td class='{col(tg)}'>{fmt(tg, True)}</td><td class='{col(td7_tot_1)}'>{fmt(td7_tot_1, True)}</td><td class='{col(td15_tot_1)}'>{fmt(td15_tot_1, True)}</td><td class='{col(td30_tot_1)}'>{fmt(td30_tot_1, True)}</td><td class='{col(ty)}'>{fmt_p(ty)}</td><td>{fmt(to)}</td></tr>")
for k in ['DC', 'IRP', 'PENSION', 'ISA']:
    if k in data:
        a = data[k]
        curr_asset = a['총 자산']
        principal = a['원금']
        
        ad7_acc_1 = (curr_asset - a.get('평가손익(7일전)', 0)) - principal
        ad15_acc_1 = (curr_asset - a.get('평가손익(15일전)', 0)) - principal
        ad30_acc_1 = (curr_asset - a.get('평가손익(30일전)', 0)) - principal
        
        h1.append(f"<tr><td>{a['label']}</td><td>{fmt(curr_asset)}</td><td class='{col
