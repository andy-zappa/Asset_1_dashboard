import streamlit as st
import json
import warnings
import google.generativeai as genai
import Andy_pension_v2

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="Andy's Asset Dashboard")

css = [
    "<style>",
    ".block-container{padding-top:3rem!important;padding-bottom:5rem!important;}",
    "h3{font-size:26px!important;font-weight:bold;margin-bottom:10px;}",
    ".sub-title{font-size:22px!important;font-weight:bold;margin:25px 0 10px;}",
    ".main-table{width:100%;border-collapse:collapse;font-size:15px;text-align:center;margin-bottom:10px;}",
    ".main-table th{background-color:#f2f2f2;padding:10px;border:1px solid #ddd;font-weight:bold!important;}",
    ".main-table td{padding:8px;border:1px solid #ddd;vertical-align:middle;}",
    ".sum-row td{background-color:#fff9e6;font-weight:bold!important;}",
    ".red{color:#FF2323!important;} .blue{color:#0047EB!important;}",
    ".sidebar-header{display:flex;align-items:center;gap:12px;margin-bottom:20px; font-size:22px;font-weight:bold;}",
    
    # [핵심] 버튼 간격 완전 밀착 및 13px 고정, 줄바꿈 금지(nowrap)
    "div[data-testid='stHorizontalBlock'] { gap: 0 !important; }",
    "div[data-testid='column'] { padding: 0 !important; }",
    "div.stButton>button { font-weight:normal!important; border-radius:3px; padding:0.2rem 0!important; width:100%!important; font-size:13px!important; margin:0!important; white-space:nowrap!important; }",
    "</style>"
]
st.markdown("".join(css), unsafe_allow_html=True)

if 'sort_mode' not in st.session_state: 
    st.session_state.sort_mode = 'init'
if 'show_code' not in st.session_state: 
    st.session_state.show_code = False
if 'init' not in st.session_state:
    with st.spinner("데이터 로딩 중..."): 
        Andy_pension_v2.generate_asset_data()
    st.session_state['init'] = True
    st.cache_data.clear()

def fmt(v):
    try: return f"{int(float(v)):,}"
    except: return str(v)

def fmt_s(v):
    try:
        val = int(float(v))
        return f"+{val:,}" if val > 0 else (f"{val:,}" if val < 0 else "0")
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

@st.cache_data(ttl=60)
def load():
    try:
        with open('assets.json', 'r', encoding='utf-8') as f: 
            return json.load(f)
    except: return None

data = load()
if not data: st.stop()
tot = data.get("_total", {})

c1, c2 = st.columns([8.5, 1.5])
with c1: 
    st.markdown("<h3>📝 이상혁(Andy lee)님 세제혜택 금융상품 자산 현황</h3>", unsafe_allow_html=True)
with c2:
    if st.button("🔄 업데이트", use_container_width=True):
        Andy_pension_v2.generate_asset_data()
        st.cache_data.clear()
        st.rerun()

st.markdown(f"<div style='text-align:right;font-size:14px;color:#555;margin:-10px 0 10px;'>[{tot.get('조회시간')}]</div>", unsafe_allow_html=True)

unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW), %</div>"

# --- [1] 투자금 대비 자산 현황 ---
st.markdown("<div class='sub-title'>📊 [1] 투자금 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총 자산 : {fmt(tot.get('총 자산',0))} / 총 수익 : <span class='{col(tot.get('총 수익',0))}'>{fmt_s(tot.get('총 수익',0))} ({fmt_p(tot.get('수익률(%)',0))})</span>**", unsafe_allow_html=True)

h1 = [unit_html, "<table class='main-table'><tr><th>계좌 구분</th><th>총 자산</th><th>총 누계손익</th><th>수익률</th><th>최초원금</th></tr>"]
ty, tg, ta, to = tot.get('수익률(%)',0), tot.get('총 수익',0), tot.get('총 자산',0), tot.get('원금합',0)
h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(ta)}</td><td class='{col(tg)}'>{fmt_s(tg)}</td><td class='{col(ty)}'>{fmt_p(ty)}</td><td>{fmt(to)}</td></tr>")

for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        h1.append(f"<tr><td>{a.get('label')}</td><td>{fmt(a.get('총 자산'))}</td><td class='{col(a.get('총 수익',0))}'>{fmt_s(a.get('총 수익',0))}</td><td class='{col(a.get('수익률(%)',0))}'>{fmt_p(a.get('수익률(%)',0))}</td><td>{fmt(a.get('원금'))}</td></tr>")
h1.append("</table>")
st.markdown("".join(h1), unsafe_allow_html=True)

# --- [2] 매입금액 대비 자산 현황 ---
ag_tot = tot.get('총 자산',0) - tot.get('매입금액합',0)
ay_tot = (ag_tot / tot.get('매입금액합',1) * 100) if tot.get('매입금액합',1) > 0 else 0

st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총 자산 : {fmt(tot.get('총 자산'))} / 총 수익 : <span class='{col(ag_tot)}'>{fmt_s(ag_tot)} ({fmt_p(ay_tot)})</span>**", unsafe_allow_html=True)

h2 = [unit_html, "<table class='main-table'><tr><th>계좌 구분</th><th>총 자산</th><th>평가손익</th><th>수익률</th><th>전일비</th><th>매입금액</th></tr>"]
h2.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(tot.get('총 자산'))}</td><td class='{col(ag_tot)}'>{fmt_s(ag_tot)}</td><td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td><td class='{col(tot.get('평가손익(전일비)',0))}'>{fmt_s(tot.get('평가손익(전일비)',0))}</td><td>{fmt(tot.get('매입금액합'))}</td></tr>")

t2_lbl = {'DC':'퇴직연금(DC)계좌', 'PENSION':'연금저축(CMA)계좌', 'ISA':'ISA(중개형)계좌', 'IRP':'퇴직연금(IRP)계좌'}
for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        ag_acc = sum(i.get('평가손익',0) for i in a['상세'] if i['종목명'] != '[ 합계 ]')
        ap_acc = a.get('총 자산',0) - ag_acc
        ay_acc = (ag_acc/ap_acc*100) if ap_acc > 0 else 0
        ad_acc = a.get('평가손익(전일비)', 0)
        h2.append(f"<tr><td>{t2_lbl.get(k, a.get('label'))}</td><td>{fmt(a.get('총 자산'))}</td><td class='{col(ag_acc)}'>{fmt_s(ag_acc)}</td><td class='{col(ay_acc)}'>{fmt_p(ay_acc)}</td><td class='{col(ad_acc)}'>{fmt_s(ad_acc)}</td><td>{fmt(ap_acc)}</td></tr>")
h2.append("</table>")
st.markdown("".join(h2), unsafe_allow_html=True)


# --- [3] 계좌별 상세 내역 ---
st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)

# 5개 버튼 우측 정렬 (여백 없음, 우측 끝선 완벽 일치용 정밀 비율 적용)
spacer, b1, b2, b3, b4, b5 = st.columns([6.5, 0.6, 0.6, 0.6, 0.6, 0.9])
with b1:
    if st.button("초기화 ▲" if st.session_state.sort_mode == 'init' else "초기화 △"): 
        st.session_state.sort_mode = 'init'; st.rerun()
with b2:
    if st.button("총 자산 ▲" if st.session_state.sort_mode == 'asset' else "총 자산 △"): 
        st.session_state.sort_mode = 'asset'; st.rerun()
with b3:
    if st.button("평가손익 ▲" if st.session_state.sort_mode == 'profit' else "평가손익 △"): 
        st.session_state.sort_mode = 'profit'; st.rerun()
with b4:
    if st.button("수익률 ▲" if st.session_state.sort_mode == 'rate' else "수익률 △"): 
        st.session_state.sort_mode = 'rate'; st.rerun()
with b5:
    if st.button("종목코드 [ + ]" if st.session_state.show_code else "종목코드 [ - ]"): 
        st.session_state.show_code = not st.session_state.show_code; st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

t3_lbl = {'DC':'퇴직연금(DC)계좌 / (삼성증권 7165962472-28)', 'PENSION':'연금저축(CMA)계좌 / (삼성증권 7169434836-15)', 'ISA':'ISA(중개형)계좌 / (키움증권 6448-4934)', 'IRP':'퇴직연금(IRP)계좌 / (삼성증권 7164499007-29)'}

for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        with st.expander(f"📂 [ {t3_lbl.get(k, a.get('label'))} ] 종목별 현황", expanded=False):
            s_data = next(i for i in a['상세'] if i['종목명'] == "[ 합계 ]")
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총 자산 : {fmt(a.get('총 자산'))} / 총 수익 : <span class='{col(s_data['평가손익'])}'>{fmt_s(s_data['평가손익'])} ({fmt_p(s_data['수익률(%)'])})</span>**", unsafe_allow_html=True)

            h3 = [unit_html, "<table class='main-table'><tr><th>종목명</th>"]
            if st.session_state.show_code: h3.append("<th>종목코드</th>")
            h3.append("<th>비중</th><th>총 자산</th><th>평가손익</th><th>수익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>")

            items = [i for i in a.get('상세', []) if i['종목명'] != "[ 합계 ]"]
            if st.session_state.sort_mode == 'asset': 
                items.sort(key=lambda x: x.get('총 자산', 0), reverse=True)
            elif st.session_state.sort_mode == 'profit': 
                items.sort(key=lambda x: x.get('평가손익', 0), reverse=True)
            elif st.session_state.sort_mode == 'rate': 
                items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)

            for i in ([s_data] + items):
                is_s = (i['종목명'] == "[ 합계 ]")
                row = f"<tr class='sum-row'>" if is_s else "<tr>"
                row += f"<td>{i['종목명']}</td>"
                
                if st.session_state.show_code: 
                    row += f"<td>{'-' if is_s or i.get('코드','-')=='-' else i.get('코드')}</td>"
                    
                row += f"<td>{i.get('비중',0):.1f}%</td>"
                row += f"<td>{fmt(i.get('총 자산',0))}</td>"
                row += f"<td class='{col(i.get('평가손익',0))}'>{fmt_s(i.get('평가손익',0))}</td>"
                row += f"<td class='{col(i.get('수익률(%)',0))}'>{fmt_p(i.get('수익률(%)',0))}</td>"
                row += f"<td>{fmt(i.get('수량','-'))}</td>"
                row += f"<td>{fmt(i.get('매입가','-'))}</td>"
                row += f"<td>{fmt(i.get('현재가','-'))}</td></tr>"
                h3.append(row)
                
            h3.append("</table>")
            st.markdown("".join(h3), unsafe_allow_html=True)

