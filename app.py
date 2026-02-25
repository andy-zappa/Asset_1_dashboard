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
/* 헤더 글씨가 위아래 정중앙에 오도록 vertical-align 적용 */
.main-table th{background-color:#f2f2f2;padding:10px;border:1px solid #ddd;font-weight:bold!important; vertical-align:middle;}
.main-table td{padding:8px;border:1px solid #ddd;vertical-align:middle;}
.sum-row td{background-color:#fff9e6;font-weight:bold!important;}
.red{color:#FF2323!important;} .blue{color:#0047EB!important;}
.insight-box{background-color:#f0f4f8;padding:20px;border-radius:10px;border-left:5px solid #007bff;margin-bottom:25px;}
.box-title{font-size:20px!important;font-weight:bold;margin-bottom:15px;display:block;color:#333;}

/* =========================================================
   [문제 해결 1] 평가손익 & 전주비 엑셀 스타일 병합 (역 L자 테두리 제거)
   ========================================================= */
.main-table th.th-eval { border-right: none !important; }
.main-table th.th-blank { border-left: none !important; border-bottom: none !important; padding: 0 !important; }
.main-table th.th-week { border-left: 1px solid #ddd !important; border-top: 1px solid #ddd !important; }

/* =========================================================
   [문제 해결 2] 윈도우 환경 흑백 이모지 파괴 (컬러 폰트 강제 주입)
   ========================================================= */
.zappa-icon {
    font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif !important;
    font-size: 32px !important;
}

/* =========================================================
   [문제 해결 3] 완벽한 플로팅 배너 (가변폭 100% 무력화)
   ========================================================= */
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) {
    position: fixed !important;
    bottom: 30px !important;
    right: 30px !important;
    background: rgba(255, 255, 255, 0.95) !important;
    padding: 10px 15px !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.15) !important;
    border: 1px solid #e5e7eb !important;
    z-index: 999999 !important;
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 5px !important;
    width: max-content !important;
}

div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) > div[data-testid="column"] {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
    padding: 0 !important;
}

div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) button {
    border-radius: 6px !important;
    padding: 6px 12px !important;
    height: 38px !important;
    font-size: 14px !important;
    font-weight: bold !important;
    background: white !important;
    border: 1px solid #d1d5db !important;
    color: #374151 !important;
    margin: 0 !important;
    white-space: nowrap !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) button:hover {
    border-color: #000 !important;
    color: #000 !important;
    background: #f8f9fa !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
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

def fmt_label(lbl):
    style = "font-size:13px; color:#555;"
    return lbl.replace("(▶ Aug. 2025)", f"<span style='{style}'>(▶ Aug. 2025)</span>").replace("(▶ Nov. 2025)", f"<span style='{style}'>(▶ Nov. 2025)</span>")

def clean_label(lbl):
    # 정규식을 이용해 (▶ ...) 형태의 날짜 텍스트를 완전히 제거
    return re.sub(r'\s*\(▶.*?\)', '', lbl)

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
st.markdown("<div class='sub-title'>📊 [1] '투자원금' 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"**총 자산 : {fmt(tot.get('총 자산',0))} / 총 수익 : <span class='{col(tot.get('총 수익',0))}'>{fmt(tot.get('총 수익',0), True)} ({fmt_p(tot.get('수익률(%)',0))})</span>**", unsafe_allow_html=True)

h1 = [unit_html, "<table class='main-table'><tr><th>계좌 구분</th><th>총 자산</th><th>총 손익</th><th>수익률</th><th>투자원금</th></tr>"]
ty, tg, ta, to = tot.get('수익률(%)',0), tot.get('총 수익',0), tot.get('총 자산',0), tot.get('원금합',0)
h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(ta)}</td><td class='{col(tg)}'>{fmt(tg, True)}</td><td class='{col(ty)}'>{fmt_p(ty)}</td><td>{fmt(to)}</td></tr>")
for k in ['DC', 'IRP', 'PENSION', 'ISA']:
    if k in data:
        a = data[k]
        h1.append(f"<tr><td>{fmt_label(a['label'])}</td><td>{fmt(a['총 자산'])}</td><td class='{col(a['총 수익'])}'>{fmt(a['총 수익'],True)}</td><td class='{col(a['수익률(%)'])}'>{fmt_p(a['수익률(%)'])}</td><td>{fmt(a['원금'])}</td></tr>")
h1.append("</table>")
st.markdown("".join(h1), unsafe_allow_html=True)

# --- [2] 매입금액 대비 자산 현황 ---
ag_tot = tot.get('총 자산',0) - tot.get('매입금액합',0)
ay_tot = (ag_tot / tot.get('매입금액합',1) * 100) if tot.get('매입금액합',1) > 0 else 0
st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"**총 자산 : {fmt(tot.get('총 자산'))} / 총 수익 : <span class='{col(ag_tot)}'>{fmt(ag_tot, True)} ({fmt_p(ay_tot)})</span>**", unsafe_allow_html=True)

# ==========================================
# [디자인 완벽 구현] 엑셀 스타일 역 L자 헤더 (전일비/전주비 병합)
# ==========================================
h2 = [unit_html, """
<table class='main-table'>
  <tr>
    <th rowspan='2'>계좌 구분</th>
    <th rowspan='2'>총 자산</th>
    <th rowspan='2' class='th-eval'>평가손익</th>
    <th colspan='2' class='th-blank'>&nbsp;</th>
    <th rowspan='2'>수익률</th>
    <th rowspan='2'>매입금액</th>
  </tr>
  <tr>
    <th class='th-week'>전일비</th>
    <th class='th-week'>전주비</th>
  </tr>
"""]

td1_tot = tot.get('평가손익(전일비)',0)
td7_tot = tot.get('평가손익(전주비)',0)
h2.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(tot.get('총 자산'))}</td><td class='{col(ag_tot)}'>{fmt(ag_tot, True)}</td><td class='{col(td1_tot)}'>{fmt(td1_tot, True)}</td><td class='{col(td7_tot)}'>{fmt(td7_tot, True)}</td><td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td><td>{fmt(tot.get('매입금액합'))}</td></tr>")
for k in ['DC', 'IRP', 'PENSION', 'ISA']:
    if k in data:
        a = data[k]
        ag_acc = sum(i.get('평가손익',0) for i in a.get('상세', []) if i.get('종목명') != '[ 합계 ]')
        ap_acc = a.get('총 자산',0) - ag_acc
        ay_acc = (ag_acc/ap_acc*100) if ap_acc > 0 else 0
        ad1_acc = a.get('평가손익(전일비)', 0)
        ad7_acc = a.get('평가손익(전주비)', 0)
        h2.append(f"<tr><td>{clean_label(a['label'])}</td><td>{fmt(a['총 자산'])}</td><td class='{col(ag_acc)}'>{fmt(ag_acc, True)}</td><td class='{col(ad1_acc)}'>{fmt(ad1_acc, True)}</td><td class='{col(ad7_acc)}'>{fmt(ad7_acc, True)}</td><td class='{col(ay_acc)}'>{fmt_p(ay_acc)}</td><td>{fmt(ap_acc)}</td></tr>")
h2.append("</table>")
st.markdown("".join(h2), unsafe_allow_html=True)

# --- [3] 계좌별 상세 내역 ---
st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)

b1, b2, b3, b4, b5 = st.columns(5)
with b1:
    st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
    if st.button("초기화 ▲" if st.session_state.sort_mode == 'init' else "초기화 △"): st.session_state.sort_mode = 'init'; st.rerun()
with b2:
    if st.button("총 자산 ▲" if st.session_state.sort_mode == 'asset' else "총 자산 △"): st.session_state.sort_mode = 'asset'; st.rerun()
with b3:
    if st.button("평가손익 ▲" if st.session_state.sort_mode == 'profit' else "평가손익 △"): st.session_state.sort_mode = 'profit'; st.rerun()
with b4:
    if st.button("수익률 ▲" if st.session_state.sort_mode == 'rate' else "수익률 △"): st.session_state.sort_mode = 'rate'; st.rerun()
with b5:
    if st.button("종목코드 [ + ]" if st.session_state.show_code else "종목코드 [ - ]"): st.session_state.show_code = not st.session_state.show_code; st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

t3_lbl = {'DC':'퇴직연금(DC)계좌 / (삼성증권 7165962472-28)', 'PENSION':'연금저축(CMA)계좌 / (삼성증권 7169434836-15)', 'ISA':'ISA(중개형)계좌 / (키움증권 6448-4934)', 'IRP':'퇴직연금(IRP)계좌 / (삼성증권 7164499007-29)'}
for k in ['DC', 'IRP', 'PENSION', 'ISA']:
    if k in data:
        a = data[k]
        with st.expander(f"📂 [ {t3_lbl.get(k, a['label'])} ] 종목별 현황", expanded=False):
            s_data = next(i for i in a['상세'] if i['종목명'] == "[ 합계 ]")
            st.markdown(f"**총 자산 : {fmt(a['총 자산'])} / 총 수익 : <span class='{col(s_data.get('평가손익'))}'>{fmt(s_data.get('평가손익'), True)} ({fmt_p(s_data.get('수익률(%)'))})</span>**", unsafe_allow_html=True)
            
            h3 = [unit_html, "<table class='main-table'><tr><th>종목명</th>"]
            if st.session_state.show_code: h3.append("<th>종목코드</th>")
            h3.append("<th>비중</th><th>총 자산</th><th>평가손익</th><th>수익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>")
            
            items = [i for i in a.get('상세', []) if i.get('종목명') != "[ 합계 ]"]
            if st.session_state.sort_mode == 'asset': items.sort(key=lambda x: x.get('총 자산', 0), reverse=True)
            elif st.session_state.sort_mode == 'profit': items.sort(key=lambda x: x.get('평가손익', 0), reverse=True)
            elif st.session_state.sort_mode == 'rate': items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
            
            for i in ([s_data] + items):
                is_s = (i.get('종목명') == "[ 합계 ]")
                row = f"<tr class='sum-row'>" if is_s else "<tr>"
                row += f"<td>{i.get('종목명')}</td>"
                if st.session_state.show_code: row += f"<td>{'-' if is_s or i.get('코드','-')=='-' else i.get('코드')}</td>"
                row += f"<td>{i.get('비중',0):.1f}%</td><td>{fmt(i.get('총 자산',0))}</td><td class='{col(i.get('평가손익',0))}'>{fmt(i.get('평가손익',0), True)}</td><td class='{col(i.get('수익률(%)',0))}'>{fmt_p(i.get('수익률(%)',0))}</td><td>{fmt(i.get('수량','-'))}</td><td>{fmt(i.get('매입가','-'))}</td><td>{fmt(i.get('현재가','-'))}</td></tr>"
                h3.append(row)
            h3.append("</table>")
            st.markdown("".join(h3), unsafe_allow_html=True)
