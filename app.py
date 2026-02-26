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

.summary-text { font-size: 16px !important; font-weight: bold !important; color: #333; margin-bottom: 10px; }
.summary-val { font-size: 20px !important; }
.main-table th.th-eval { border-right: none !important; }
.main-table th.th-blank { border-left: none !important; border-bottom: none !important; padding: 0 !important; }
.main-table th.th-week { border-left: 1px solid #ddd !important; border-top: 1px solid #ddd !important; font-size: 13.5px; }
.zappa-icon { font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif !important; font-size: 32px !important; }

/* =========================================================
   [Andy 가이드 반영] 플로팅 배너 광폭화 및 우측 정렬 로직
   ========================================================= */
div[data-testid="stColumns"]:has(#zappa-floating-menu),
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) {
    position: fixed !important;
    bottom: 30px !important;
    right: 30px !important;
    background: rgba(255, 255, 255, 0.98) !important;
    
    /* 1. 배너 사이즈 강제 광폭화 (800px) */
    width: 800px !important; 
    height: 50px !important;
    
    padding: 0 30px !important; 
    border-radius: 8px !important; 
    box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important; 
    border: 1px solid #d1d5db !important; 
    z-index: 999999 !important;
    
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important; 
    
    /* 2. 항목들을 우측으로 밀어버리고 여백 확보 */
    justify-content: flex-end !important; 
    gap: 0 !important; 
}

div.element-container:has(#zappa-floating-menu) { display: none !important; }

/* 3. 각 항목 슬롯: 텍스트 길이에 상관없이 동일한 공간(110px) 할당 */
div[data-testid="stColumns"]:has(#zappa-floating-menu) > div[data-testid="column"],
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) > div[data-testid="column"] { 
    flex: 0 0 110px !important; 
    width: 110px !important;
    display: flex !important; 
    align-items: center !important; 
    justify-content: center !important; 
    border-right: 1px solid #d1d5db !important;
}

/* 마지막 종목코드 슬롯 뒤에 여백을 아주 많이 남기기 위해 padding 추가 및 선 제거 */
div[data-testid="stColumns"]:has(#zappa-floating-menu) > div[data-testid="column"]:last-child,
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) > div[data-testid="column"]:last-child { 
    border-right: none !important;
    flex: 0 0 130px !important; /* 마지막 칸은 조금 더 넓게 */
    width: 130px !important;
    margin-right: 40px !important; /* [가이드 반영] 종목코드 뒤에 큰 여백 확보 */
}

div[data-testid="stColumns"]:has(#zappa-floating-menu) button,
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) button { 
    background: transparent !important; 
    border: none !important; 
    box-shadow: none !important;
    color: #8c8c8c !important; 
    font-size: 15px !important; 
}

div[data-testid="stColumns"]:has(#zappa-floating-menu) button[kind="primary"],
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) button[kind="primary"] { 
    color: #111111 !important; 
    font-weight: 500 !important; 
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

# --- 데이터 로드 ---
def fmt(v, sign=False):
    try:
        val = int(float(v)); return f"+{val:,}" if sign and val > 0 else f"{val:,}"
    except: return str(v)
def fmt_p(v):
    try:
        val = float(v); return f"▲{val:.2f}%" if val > 0 else (f"▼{abs(val):.2f}%" if val < 0 else "0.00%")
    except: return str(v)
def col(v):
    try:
        val = float(v); return "red" if val > 0 else ("blue" if val < 0 else "")
    except: return ""
def clean_label(lbl): return re.sub(r'\s*\(\d{2}\.\d+월\)', '', lbl)

@st.cache_data(ttl=60)
def load():
    try:
        with open('assets.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return None

data = load()
if not data: st.stop()
tot = data.get("_total", {})

# --- 대시보드 상단 ---
c1, c2 = st.columns([8.5, 1.5])
with c1: st.markdown("<h3>🚀 이상혁(Andy lee)님 절세계좌 통합 대시보드</h3>", unsafe_allow_html=True)
with c2:
    if st.button("🔄 업데이트", use_container_width=True):
        Andy_pension_v2.generate_asset_data(); st.cache_data.clear(); st.rerun()

st.markdown(f"<div style='text-align:right;font-size:14px;color:#555;margin:-10px 0 10px;'>[{tot.get('조회시간')}]</div>", unsafe_allow_html=True)

# --- [1] 투자원금 대비 ---
st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"""
<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'>
    <div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(tot.get('총 자산',0))}</span> / 총 수익 : <span class='summary-val {col(tot.get('총 수익',0))}'>{fmt(tot.get('총 수익',0), True)} ({fmt_p(tot.get('수익률(%)',0))})</span></div>
    <div style='font-size:14.5px; font-weight:normal; color:#555;'>[ 25.8월 : 퇴직연금(DC/IRP), ISA(중개형), 25.11월 : 연금저축(CMA) ]</div>
</div>
""", unsafe_allow_html=True)

h1 = ["<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>수익률</th><th rowspan='2'>투자원금</th></tr><tr><th class='th-week'>7일전</th><th class='th-week'>15일전</th><th class='th-week'>30일전</th></tr>"]
ty, tg, ta, to = tot.get('수익률(%)',0), tot.get('총 수익',0), tot.get('총 자산',0), tot.get('원금합',0)
td7, td15, td30 = (ta - tot.get('평가손익(7일전)', 0)) - to, (ta - tot.get('평가손익(15일전)', 0)) - to, (ta - tot.get('평가손익(30일전)', 0)) - to
h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(ta)}</td><td class='{col(tg)}'>{fmt(tg, True)}</td><td class='{col(td7)}'>{fmt(td7, True)}</td><td class='{col(td15)}'>{fmt(td15, True)}</td><td class='{col(td30)}'>{fmt(td30, True)}</td><td class='{col(ty)}'>{fmt_p(ty)}</td><td>{fmt(to)}</td></tr>")

keys = ['DC', 'IRP', 'PENSION', 'ISA']
if st.session_state.sort_mode == 'asset': keys.sort(key=lambda k: data[k].get('총 자산', 0), reverse=True)
elif st.session_state.sort_mode == 'profit': keys.sort(key=lambda k: data[k].get('총 수익', 0), reverse=True)
elif st.session_state.sort_mode == 'rate': keys.sort(key=lambda k: data[k].get('수익률(%)', 0), reverse=True)

for k in keys:
    if k in data:
        a = data[k]; curr, princ = a['총 자산'], a['원금']
        d7, d15, d30 = (curr - a.get('평가손익(7일전)', 0)) - princ, (curr - a.get('평가손익(15일전)', 0)) - princ, (curr - a.get('평가손익(30일전)', 0)) - princ
        h1.append(f"<tr><td>{clean_label(a['label'])}</td><td>{fmt(curr)}</td><td class='{col(a['총 수익'])}'>{fmt(a['총 수익'],True)}</td><td class='{col(d7)}'>{fmt(d7, True)}</td><td class='{col(d15)}'>{fmt(d15, True)}</td><td class='{col(d30)}'>{fmt(d30, True)}</td><td class='{col(a['수익률(%)'])}'>{fmt_p(a['수익률(%)'])}</td><td>{fmt(princ)}</td></tr>")
st.markdown("".join(h1)+"</table>", unsafe_allow_html=True)

# --- 플로팅 메뉴 ---
b1, b2, b3, b4, b5 = st.columns(5)
with b1:
    st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
    if st.button("초기화△", type="primary" if st.session_state.sort_mode=='init' else "secondary"): st.session_state.sort_mode='init'; st.rerun()
with b2:
    if st.button("총자산△", type="primary" if st.session_state.sort_mode=='asset' else "secondary"): st.session_state.sort_mode='asset'; st.rerun()
with b3:
    if st.button("평가손익△", type="primary" if st.session_state.sort_mode=='profit' else "secondary"): st.session_state.sort_mode='profit'; st.rerun()
with b4:
    if st.button("수익률△", type="primary" if st.session_state.sort_mode=='rate' else "secondary"): st.session_state.sort_mode='rate'; st.rerun()
with b5:
    if st.button("종목코드[-]" if st.session_state.show_code else "종목코드[+]", type="primary" if st.session_state.show_code else "secondary"): st.session_state.show_code = not st.session_state.show_code; st.rerun()

# --- [3] 상세 내역 ---
st.markdown("<br><div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
t3_lbl = {'DC':'퇴직연금(DC) / 삼성증권', 'PENSION':'연금저축(CMA) / 삼성증권', 'ISA':'ISA(중개형) / 키움증권', 'IRP':'퇴직연금(IRP) / 삼성증권'}
for k in keys:
    if k in data:
        a = data[k]
        with st.expander(f"📂 {t3_lbl.get(k, a['label'])}", expanded=False):
            s_data = next(i for i in a['상세'] if i['종목명'] == "[ 합계 ]")
            st.markdown(f"<div class='summary-text'>● 총 자산 : {fmt(a['총 자산'])} / 총 수익 : <span class='{col(s_data['평가손익'])}'>{fmt(s_data['평가손익'], True)} ({fmt_p(s_data['수익률(%)'])})</span></div>", unsafe_allow_html=True)
            h3 = ["<table class='main-table'><tr><th>종목명</th>"]
            if st.session_state.show_code: h3.append("<th>코드</th>")
            h3.append("<th>비중</th><th>총자산</th><th>평가손익</th><th>수익률</th><th>수량</th><th>현재가</th></tr>")
            items = [i for i in a['상세'] if i['종목명'] != "[ 합계 ]"]
            for i in ([s_data] + items):
                row_cls = " class='sum-row'" if i['종목명']=="[ 합계 ]" else ""
                h3.append(f"<tr{row_cls}><td>{i['종목명']}</td>")
                if st.session_state.show_code: h3.append(f"<td>{i.get('코드','-')}</td>")
                h3.append(f"<td>{i['비중']:.1f}%</td><td>{fmt(i['총 자산'])}</td><td class='{col(i['평가손익'])}'>{fmt(i['평가손익'], True)}</td><td class='{col(i['수익률(%)'])}'>{fmt_p(i['수익률(%)'])}</td><td>{fmt(i['수량'])}</td><td>{fmt(i['현재가'])}</td></tr>")
            st.markdown("".join(h3)+"</table>", unsafe_allow_html=True)
