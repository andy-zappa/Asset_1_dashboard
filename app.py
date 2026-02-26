import streamlit as st
import json
import warnings
import google.generativeai as genai
import Andy_pension_v2
import os
import re

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="Andy's Asset Dashboard")

# [1] 세션 상태 초기화 및 공통 변수 정의
if 'sort_mode' not in st.session_state: st.session_state.sort_mode = 'init'
if 'show_code' not in st.session_state: st.session_state.show_code = False
if 'init' not in st.session_state:
    with st.spinner("데이터 업데이트 중..."): Andy_pension_v2.generate_asset_data()
    st.session_state['init'] = True
    st.cache_data.clear()

# 전역에서 사용할 공통 HTML 단위 표기
unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"

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

/* 플로팅 배너: 좌측 정렬 및 구분선(/) 디자인 */
div[data-testid="stColumns"]:has(#zappa-floating-menu),
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) {
    position: fixed !important;
    bottom: 30px !important;
    right: 30px !important;
    background: rgba(255, 255, 255, 0.98) !important;
    width: 800px !important; 
    height: 54px !important;
    padding: 0 15px !important;
    border-radius: 8px !important; 
    box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important; 
    border: 1px solid #d1d5db !important; 
    z-index: 999999 !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important; 
    justify-content: flex-start !important; 
}
div.element-container:has(#zappa-floating-menu) { display: none !important; }

div[data-testid="stColumns"]:has(#zappa-floating-menu) > div[data-testid="column"],
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) > div[data-testid="column"] { 
    flex: 0 0 auto !important; 
    width: max-content !important;
    padding: 0 5px !important;
    display: flex !important; 
    align-items: center !important; 
}

/* 슬래시(/) 구분선 */
div[data-testid="stColumns"]:has(#zappa-floating-menu) > div[data-testid="column"]:not(:last-child):after,
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) > div[data-testid="column"]:not(:last-child):after {
    content: "/" !important;
    color: #d1d5db !important;
    margin-left: 5px !important;
    font-size: 16px !important;
}

div[data-testid="stColumns"]:has(#zappa-floating-menu) button { 
    background: transparent !important; 
    border: none !important; 
    box-shadow: none !important;
    color: #8c8c8c !important; 
    font-size: 15px !important; 
    padding: 0 8px !important;
    transition: color 0.2s;
}

div[data-testid="stColumns"]:has(#zappa-floating-menu) button:hover { color: #111111 !important; }
div[data-testid="stColumns"]:has(#zappa-floating-menu) button[kind="primary"] { 
    color: #111111 !important; 
    font-weight: 500 !important; 
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# [2] 사이드바 ZAPPA AI 엔진
with st.sidebar:
    st.markdown("""<div style='display:flex; align-items:center; gap:10px; margin-bottom:20px;'><span class='zappa-icon'>🤖</span><span style='font-size:22px; font-weight:bold; color:#333;'>ZAPPA AI 코딩 엔진</span></div>""", unsafe_allow_html=True)
    try:
        key = st.secrets.get("GOOGLE_API_KEY")
        if key:
            genai.configure(api_key=key); model = genai.GenerativeModel('gemini-1.5-flash')
            pmt = st.text_area("AI 엔진에게 요청", placeholder="수정 사항을 입력하세요...")
            if st.button("개선 사항 반영하기"):
                res = model.generate_content("Streamlit 수정: " + pmt)
                st.code(res.text)
    except Exception: st.error("엔진 연결 지연")

# [3] 유틸리티 함수
def fmt(v, sign=False):
    try: val = int(float(v)); return f"+{val:,}" if sign and val > 0 else f"{val:,}"
    except: return str(v)
def fmt_p(v):
    try: val = float(v); return f"▲{val:.2f}%" if val > 0 else (f"▼{abs(val):.2f}%" if val < 0 else "0.00%")
    except: return str(v)
def col(v):
    try: val = float(v); return "red" if val > 0 else ("blue" if val < 0 else "")
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

# [4] 대시보드 메인 레이아웃
c1, c2 = st.columns([8.5, 1.5])
with c1: st.markdown("<h3>🚀 이상혁(Andy lee)님 절세계좌 통합 대시보드</h3>", unsafe_allow_html=True)
with c2:
    if st.button("🔄 업데이트", use_container_width=True):
        Andy_pension_v2.generate_asset_data(); st.cache_data.clear(); st.rerun()

st.markdown(f"<div style='text-align:right;font-size:14px;color:#555;margin:-10px 0 10px;'>[{tot.get('조회시간')}]</div>", unsafe_allow_html=True)

# --- [1] 투자원금 대비 자산 현황 ---
st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"""
<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'>
    <div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(tot.get('총 자산',0))}</span> / 총 수익 : <span class='summary-val {col(tot.get('총 수익',0))}'>{fmt(tot.get('총 수익',0), True)} ({fmt_p(tot.get('수익률(%)',0))})</span></div>
    <div style='font-size:14.5px; font-weight:normal; color:#555;'>[ 25.8월 : 퇴직연금(DC/IRP), ISA(중개형), 25.11월 : 연금저축(CMA) ]</div>
</div>
""", unsafe_allow_html=True)

h1 = [unit_html, "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>수익률</th><th rowspan='2'>투자원금</th></tr><tr><th class='th-week'>7일전</th><th class='th-week'>15일전</th><th class='th-week'>30일전</th></tr>"]
ta, tg, ty, to = tot.get('총 자산',0), tot.get('총 수익',0), tot.get('수익률(%)',0), tot.get('원금합',0)
td7, td15, td30 = (ta - tot.get('평가손익(7일전)', 0)) - to, (ta - tot.get('평가손익(15일전)', 0)) - to, (ta - tot.get('평가손익(30일전)', 0)) - to
h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(ta)}</td><td class='{col(tg)}'>{fmt(tg, True)}</td><td class='{col(td7)}'>{fmt(td7, True)}</td><td class='{col(td15)}'>{fmt(td15, True)}</td><td class='{col(td30)}'>{fmt(td30, True)}</td><td class='{col(ty)}'>{fmt_p(ty)}</td><td>{fmt(to)}</td></tr>")

# 계좌 노출 순서 고정: DC -> IRP -> PENSION -> ISA
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

# --- [2] 매입금액 대비 자산 현황 (복구 완료) ---
ag_tot = tot.get('총 자산',0) - tot.get('매입금액합',0)
ay_tot = (ag_tot / tot.get('매입금액합',1) * 100) if tot.get('매입금액합',1) > 0 else 0
st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(tot.get('총 자산'))}</span> / 총 수익 : <span class='summary-val {col(ag_tot)}'>{fmt(ag_tot, True)} ({fmt_p(ay_tot)})</span></div>", unsafe_allow_html=True)

h2 = [unit_html, "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>수익률</th><th rowspan='2'>매입금액</th></tr><tr><th class='th-week'>전일비</th><th class='th-week'>전주비</th><th class='th-week'>전월비</th></tr>"]
h2.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(tot.get('총 자산'))}</td><td class='{col(ag_tot)}'>{fmt(ag_tot, True)}</td><td>{fmt(tot.get('평가손익(1일전)',0), True)}</td><td>{fmt(tot.get('평가손익(7일전)',0), True)}</td><td>{fmt(tot.get('평가손익(30일전)',0), True)}</td><td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td><td>{fmt(tot.get('매입금액합'))}</td></tr>")

sec2_items = []
for k in ['DC', 'IRP', 'PENSION', 'ISA']:
    if k in data:
        a = data[k]; ag = sum(i.get('평가손익',0) for i in a.get('상세', []) if i.get('종목명') != '[ 합계 ]')
        ap = a.get('총 자산',0) - ag; ay = (ag/ap*100) if ap > 0 else 0
        sec2_items.append({'k': k, 'a': a, 'ag': ag, 'ap': ap, 'ay': ay})
if st.session_state.sort_mode == 'asset': sec2_items.sort(key=lambda x: x['a'].get('총 자산', 0), reverse=True)
elif st.session_state.sort_mode == 'profit': sec2_items.sort(key=lambda x: x['ag'], reverse=True)
elif st.session_state.sort_mode == 'rate': sec2_items.sort(key=lambda x: x['ay'], reverse=True)

for item in sec2_items:
    a = item['a']
    h2.append(f"<tr><td>{clean_label(a['label'])}</td><td>{fmt(a['총 자산'])}</td><td class='{col(item['ag'])}'>{fmt(item['ag'], True)}</td><td>{fmt(a.get('평가손익(1일전)', 0), True)}</td><td>{fmt(a.get('평가손익(7일전)', 0), True)}</td><td>{fmt(a.get('평가손익(30일전)', 0), True)}</td><td class='{col(item['ay'])}'>{fmt_p(item['ay'])}</td><td>{fmt(item['ap'])}</td></tr>")
st.markdown("".join(h2)+"</table>", unsafe_allow_html=True)

# --- [3] 계좌별 상세 내역 및 플로팅 배너 ---
st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)

# 스마트 플로팅 배너 (●/○ 표시 및 좌측 정렬)
b1, b2, b3, b4, b5 = st.columns(5)
with b1:
    st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
    is_sel = (st.session_state.sort_mode == 'init')
    if st.button(f"초기화[{'●' if is_sel else '○'}]", type="primary" if is_sel else "secondary"): st.session_state.sort_mode = 'init'; st.rerun()
with b2:
    is_sel = (st.session_state.sort_mode == 'asset')
    if st.button(f"총자산[{'●' if is_sel else '○'}]", type="primary" if is_sel else "secondary"): st.session_state.sort_mode = 'asset'; st.rerun()
with b3:
    is_sel = (st.session_state.sort_mode == 'profit')
    if st.button(f"평가손익[{'●' if is_sel else '○'}]", type="primary" if is_sel else "secondary"): st.session_state.sort_mode = 'profit'; st.rerun()
with b4:
    is_sel = (st.session_state.sort_mode == 'rate')
    if st.button(f"수익률[{'●' if is_sel else '○'}]", type="primary" if is_sel else "secondary"): st.session_state.sort_mode = 'rate'; st.rerun()
with b5:
    is_sel = st.session_state.show_code
    if st.button(f"종목코드[{'+' if is_sel else '-'}]", type="primary" if is_sel else "secondary"): st.session_state.show_code = not st.session_state.show_code; st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

t3_lbl = {'DC':'퇴직연금(DC)계좌 / 삼성증권', 'PENSION':'연금저축(CMA)계좌 / 삼성증권', 'ISA':'ISA(중개형)계좌 / 키움증권', 'IRP':'퇴직연금(IRP)계좌 / 삼성증권'}
for k in keys:
    if k in data:
        a = data[k]; s_data = next(i for i in a['상세'] if i['종목명'] == "[ 합계 ]")
        with st.expander(f"📂 [ {t3_lbl.get(k, a['label'])} ]", expanded=False):
            # 위험/안전자산 비중 계산 (복구 완료)
            safe = sum(item.get('비중', 0) for item in a.get('상세', []) if item.get('종목명') in ['삼성화재 퇴직연금(3.05%/年)', '현금성자산', '현금잔고'])
            extra = f"<div style='font-size:14.5px; color:#555;'>[ 위험자산 : {100-safe:.1f}% | 안전자산 : {safe:.1f}% ]</div>" if k in ['DC', 'IRP'] else ""
            st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:flex-end;'><div>● 총 자산 : {fmt(a['총 자산'])} / 총 수익 : <span class='{col(s_data['평가손익'])}'>{fmt(s_data['평가손익'], True)} ({fmt_p(s_data['수익률(%)'])})</span></div>{extra}</div>", unsafe_allow_html=True)
            
            h3 = [unit_html, "<table class='main-table'><tr><th>종목명</th>"]
            if st.session_state.show_code: h3.append("<th>코드</th>")
            h3.append("<th>비중</th><th>총 자산</th><th>평가손익</th><th>수익률</th><th>수량</th><th>현재가</th></tr>"]
            items = sorted([i for i in a['상세'] if i['종목명'] != "[ 합계 ]"], key=lambda x: x.get('총 자산', 0), reverse=True)
            for i in ([s_data] + items):
                r_cls = " class='sum-row'" if i['종목명'] == "[ 합계 ]" else ""
                h3.append(f"<tr{r_cls}><td>{i['종목명']}</td>")
                if st.session_state.show_code: h3.append(f"<td>{i.get('코드','-')}</td>")
                h3.append(f"<td>{i['비중']:.1f}%</td><td>{fmt(i['총 자산'])}</td><td class='{col(i['평가손익'])}'>{fmt(i['평가손익'], True)}</td><td class='{col(i['수익률(%)'])}'>{fmt_p(i['수익률(%)'])}</td><td>{fmt(i.get('수량','-'))}</td><td>{fmt(i.get('현재가','-'))}</td></tr>")
            st.markdown("".join(h3)+"</table>", unsafe_allow_html=True)



