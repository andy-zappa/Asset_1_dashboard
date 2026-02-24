import streamlit as st
import json
import warnings
import google.generativeai as genai
import Andy_pension_v2

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="Andy's Asset Dashboard")

css = """
<style>
.block-container { padding-top:3rem!important; padding-bottom:5rem!important; }
h3 { font-size:26px!important; font-weight:bold; margin-bottom:10px; }
.sub-title { font-size:22px!important; font-weight:bold; margin:25px 0 10px; }
.main-table { width:100%; border-collapse:collapse; font-size:15px; text-align:center; margin-bottom:10px; }
.main-table th { background-color:#f2f2f2; padding:10px; border:1px solid #ddd; font-weight:bold!important; }
.main-table td { padding:8px; border:1px solid #ddd; vertical-align:middle; }
.sum-row td { background-color:#fff9e6; font-weight:bold!important; }
.red { color:#FF2323!important; } 
.blue { color:#0047EB!important; }
.sidebar-header { display:flex; align-items:center; gap:12px; margin-bottom:20px; font-size:22px; font-weight:bold; }

/* [핵심] 버튼을 1픽셀의 틈도 없이 바싹 붙이는 마법의 CSS */
div[data-testid='stHorizontalBlock'] { gap: 0px !important; }
div[data-testid='column'] { padding: 0px !important; }
div.stButton>button { 
    font-weight:normal!important; 
    border-radius:0px!important; 
    padding:0.2rem 0.5rem!important; 
    font-size:13px!important; 
    margin-left:-1px!important; /* 테두리가 겹치도록 당김 */
    white-space:nowrap!important; 
    border:1px solid #ccc!important; 
}
/* 첫 번째, 마지막 버튼의 바깥쪽 모서리만 둥글게 처리 */
div[data-testid='column']:first-child div.stButton>button {
    border-top-left-radius: 4px !important;
    border-bottom-left-radius: 4px !important;
    margin-left: 0 !important;
}
div[data-testid='column']:last-child div.stButton>button {
    border-top-right-radius: 4px !important;
    border-bottom-right-radius: 4px !important;
}
div.stButton>button:hover { 
    border-color:#ff4b4b!important; 
    z-index:1; 
    position:relative; 
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

if 'sort_mode' not in st.session_state: 
    st.session_state.sort_mode = 'init'
if 'show_code' not in st.session_state: 
    st.session_state.show_code = False
if 'init' not in st.session_state:
    with st.spinner("데이터 로딩 중..."): 
        Andy_pension_v2.generate_asset_data()
    st.session_state['init'] = True
    st.cache_data.clear()

# ==========================================
# [안전장치] 에러가 나도 ZAPPA 엔진은 절대 안 날아가게 보호
# ==========================================
with st.sidebar:
    st.markdown(
        "<div class='sidebar-header'>"
        "<span class='sidebar-icon'>🤖</span>"
        "<span class='sidebar-text'>ZAPPA AI 코딩 모드</span>"
        "</div>", 
        unsafe_allow_html=True
    )
    try:
        key = st.secrets.get("GOOGLE_API_KEY") if "GOOGLE_API_KEY" in st.secrets else None
        if key:
            genai.configure(api_key=key)
            models = genai.list_models()
            avail = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
            if avail:
                m_name = next((m for m in avail if 'flash' in m), avail[0])
                model = genai.GenerativeModel(m_name)
                pmt = st.text_area("AI에게 요청", placeholder="요청 사항을 입력하세요...")
                if st.button("수정 제안받기"):
                    res = model.generate_content("Streamlit 수정: " + pmt)
                    st.code(res.text)
        else:
            st.info("API Key가 설정되지 않았습니다.")
    except Exception as e:
        st.error(f"ZAPPA 엔진 연결 지연 (기본 기능은 정상 작동합니다)")

# ==========================================
# 포맷팅 함수
# ==========================================
def fmt(v, sign=False):
    try:
        val = int(float(v))
        if sign and val > 0:
            return f"+{val:,}"
        return f"{val:,}"
    except:
        return str(v)

def col(v):
    try:
        val = float(v)
        return "red" if val > 0 else ("blue" if val < 0 else "")
    except:
        return ""

@st.cache_data(ttl=60)
def load():
    try:
        with open('assets.json', 'r', encoding='utf-8') as f: 
            return json.load(f)
    except:
        return None

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

time_str = f"<div style='text-align:right;font-size:14px;color:#555;margin:-10px 0 10px;'>[{tot.get('조회시간')}]</div>"
st.markdown(time_str, unsafe_allow_html=True)

unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW), %</div>"

# --- [1] 투자금 대비 자산 현황 ---
st.markdown("<div class='sub-title'>📊 [1] 투자금 대비 자산 현황</div>", unsafe_allow_html=True)

t1_str = (
    "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    f"**총 자산 : {fmt(tot.get('총자산',0))} / "
    f"총 수익 : <span class='{col(tot.get('총손익',0))}'>"
    f"{fmt(tot.get('총손익',0), True)} "
    f"({'▲' if tot.get('수익률(%)',0)>0 else '▼' if tot.get('수익률(%)',0)<0 else ''}{abs(tot.get('수익률(%)',0)):.2f}%)</span>**"
)
st.markdown(t1_str, unsafe_allow_html=True)

h1 = [
    unit_html, 
    "<table class='main-table'><tr><th>계좌 구분</th><th>총 자산</th>"
    "<th>총 누계손익</th><th>수익률</th><th>최초원금</th></tr>"
]

ty, tg, ta, to = tot.get('수익률(%)',0), tot.get('총손익',0), tot.get('총자산',0), tot.get('원금합',0)

ty_str = f"{'▲' if ty>0 else '▼' if ty<0 else ''}{abs(ty):.2f}%"
h1.append(
    f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(ta)}</td>"
    f"<td class='{col(tg)}'>{fmt(tg, True)}</td><td class='{col(ty)}'>{ty_str}</td>"
    f"<td>{fmt(to)}</td></tr>"
)

for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        ay, ag = a.get('수익률(%)',0), a.get('총손익',0)
        ay_str = f"{'▲' if ay>0 else '▼' if ay<0 else ''}{abs(ay):.2f}%"
        row = (
            f"<tr><td>{a.get('label')}</td><td>{fmt(a.get('총자산'))}</td>"
            f"<td class='{col(ag)}'>{fmt(ag, True)}</td><td class='{col(ay)}'>{ay_str}</td>"
            f"<td>{fmt(a.get('원금'))}</td></tr>"
        )
        h1.append(row)
h1.append("</table>")
st.markdown("".join(h1), unsafe_allow_html=True)


# --- [2] 매수금액 대비 자산 현황 ---
ag_tot = tot.get('총자산',0) - tot.get('매수금액합',0)
ay_tot = (ag_tot / tot.get('매수금액합',1) * 100) if tot.get('매수금액합',1) > 0 else 0

st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)

t2_str = (
    "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    f"**총 자산 : {fmt(tot.get('총자산'))} / "
    f"총 수익 : <span class='{col(ag_tot)}'>{fmt(ag_tot, True)} "
    f"({'▲' if ay_tot>0 else '▼' if ay_tot<0 else ''}{abs(ay_tot):.2f}%)</span>**"
)
st.markdown(t2_str, unsafe_allow_html=True)

h2 = [
    unit_html, 
    "<table class='main-table'><tr><th>계좌 구분</th><th>총 자산</th>"
    "<th>평가손익</th><th>수익률</th><th>전일비</th><th>매입금액</th></tr>"
]

ay_tot_str = f"{'▲' if ay_tot>0 else '▼' if ay_tot<0 else ''}{abs(ay_tot):.2f}%"
td_tot = tot.get('평가손익(전일비)',0)

h2.append(
    f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(tot.get('총자산'))}</td>"
    f"<td class='{col(ag_tot)}'>{fmt(ag_tot, True)}</td><td class='{col(ay_tot)}'>{ay_tot_str}</td>"
    f"<td class='{col(td_tot)}'>{fmt(td_tot, True)}</td><td>{fmt(tot.get('매수금액합'))}</td></tr>"
)

t2_lbl = {
    'DC':'퇴직연금(DC)계좌', 'PENSION':'연금저축(CMA)계좌', 
    'ISA':'ISA(중개형)계좌', 'IRP':'퇴직연금(IRP)계좌'
}

for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        ag_acc = sum(i['평가손익'] for i in a['상세'] if i['종목명'] != '[ 합계 ]')
        ap_acc = a.get('총자산',0) - ag_acc
        ay_acc = (ag_acc/ap_acc*100) if ap_acc > 0 else 0
        ay_acc_str = f"{'▲' if ay_acc>0 else '▼' if ay_acc<0 else ''}{abs(ay_acc):.2f}%"
        ad_acc = a.get('평가손익(전일비)', 0)
        
        row = (
            f"<tr><td>{t2_lbl.get(k, a.get('label'))}</td>"
            f"<td>{fmt(a.get('총자산'))}</td><td class='{col(ag_acc)}'>{fmt(ag_acc, True)}</td>"
            f"<td class='{col(ay_acc)}'>{ay_acc_str}</td><td class='{col(ad_acc)}'>{fmt(ad_acc, True)}</td>"
            f"<td>{fmt(ap_acc)}</td></tr>"
        )
        h2.append(row)
h2.append("</table>")
st.markdown("".join(h2), unsafe_allow_html=True)


# --- [3] 계좌별 상세 내역 ---
st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)

# 5개 버튼 우측 정렬 및 간격 완벽 밀착! (표 끝선과 일치)
spacer, b1, b2, b3, b4, b5 = st.columns([5.8, 0.8, 0.8, 0.8, 0.8, 1.0])
with b1:
    if st.button("초기화 ▲" if st.session_state.sort_mode == 'init' else "초기화 △", use_container_width=True): 
        st.session_state.sort_mode = 'init'; st.rerun()
with b2:
    if st.button("총 자산 ▲" if st.session_state.sort_mode == 'asset' else "총 자산 △", use_container_width=True): 
        st.session_state.sort_mode = 'asset'; st.rerun()
with b3:
    if st.button("평가손익 ▲" if st.session_state.sort_mode == 'profit' else "평가손익 △", use_container_width=True): 
        st.session_state.sort_mode = 'profit'; st.rerun()
with b4:
    if st.button("수익률 ▲" if st.session_state.sort_mode == 'rate' else "수익률 △", use_container_width=True): 
        st.session_state.sort_mode = 'rate'; st.rerun()
with b5:
    if st.button("종목코드 [ + ]" if st.session_state.show_code else "종목코드 [ - ]", use_container_width=True): 
        st.session_state.show_code = not st.session_state.show_code; st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

t3_lbl = {
    'DC':'퇴직연금(DC)계좌 / (삼성증권 7165962472-28)', 
    'PENSION':'연금저축(CMA)계좌 / (삼성증권 7169434836-15)', 
    'ISA':'ISA(중개형)계좌 / (키움증권 6448-4934)', 
    'IRP':'퇴직연금(IRP)계좌 / (삼성증권 7164499007-29)'
}

for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        with st.expander(f"📂 [ {t3_lbl.get(k, a.get('label'))} ] 종목별 현황", expanded=False):
            s_data = next(i for i in a['상세'] if i['종목명'] == "[ 합계 ]")
            
            t3_str = (
                "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                f"**총 자산 : {fmt(a.get('총자산'))} / "
                f"총 수익 : <span class='{col(s_data['평가손익'])}'>"
                f"{fmt(s_data['평가손익'], True)} "
                f"({'▲' if s_data['수익률']>0 else '▼' if s_data['수익률']<0 else ''}{abs(s_data['수익률']):.2f}%)</span>**"
            )
            st.markdown(t3_str, unsafe_allow_html=True)

            h3 = [unit_html, "<table class='main-table'><tr><th>종목명</th>"]
            if st.session_state.show_code: 
                h3.append("<th>종목코드</th>")
            h3.append("<th>비중</th><th>총 자산</th><th>평가손익</th><th>수익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>")

            items = [i for i in a.get('상세', []) if i['종목명'] != "[ 합계 ]"]
            if st.session_state.sort_mode == 'asset': 
                items.sort(key=lambda x: x.get('총자산', 0), reverse=True)
            elif st.session_state.sort_mode == 'profit': 
                items.sort(key=lambda x: x.get('평가손익', 0), reverse=True)
            elif st.session_state.sort_mode == 'rate': 
                items.sort(key=lambda x: x.get('수익률', 0), reverse=True)

            for i in ([s_data] + items):
                is_s = (i['종목명'] == "[ 합계 ]")
                row = f"<tr class='sum-row'>" if is_s else "<tr>"
                row += f"<td>{i['종목명']}</td>"
                
                if st.session_state.show_code: 
                    code_val = i.get('코드','-')
                    cdisp = '-' if is_s or code_val == '-' else code_val
                    row += f"<td>{cdisp}</td>"
                    
                rate_val = i.get('수익률', 0)
                icon = '▲' if rate_val > 0 else '▼' if rate_val < 0 else ''
                rate_str = f"{icon}{abs(rate_val):.2f}%"

                row += f"<td>{i.get('비중',0):.1f}%</td>"
                row += f"<td>{fmt(i.get('총자산',0))}</td>"
                row += f"<td class='{col(i.get('평가손익',0))}'>{fmt(i.get('평가손익',0), True)}</td>"
                row += f"<td class='{col(rate_val)}'>{rate_str}</td>"
                row += f"<td>{fmt(i.get('주식수','-'))}</td>"
                row += f"<td>{fmt(i.get('평단가','-'))}</td>"
                row += f"<td>{fmt(i.get('금일종가','-'))}</td></tr>"
                h3.append(row)
                
            h3.append("</table>")
            st.markdown("".join(h3), unsafe_allow_html=True)
