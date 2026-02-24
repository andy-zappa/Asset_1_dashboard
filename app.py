import streamlit as st
import json
import warnings
import google.generativeai as genai
import Andy_pension_v2

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="Andy's Asset Dashboard")

# [수정] UI 디자인 및 버튼 밀착 설정
css = """
<style>
.block-container{padding-top:3rem!important;padding-bottom:5rem!important;}
h3{font-size:26px!important;font-weight:bold;margin-bottom:10px;}
.sub-title{font-size:22px!important;font-weight:bold;margin:25px 0 10px;}
.main-table{width:100%;border-collapse:collapse;font-size:15px;text-align:center;margin-bottom:10px;}
.main-table th{background-color:#f2f2f2;padding:10px;border:1px solid #ddd;font-weight:bold!important;}
.main-table td{padding:8px;border:1px solid #ddd;vertical-align:middle;}
.sum-row td{background-color:#fff9e6;font-weight:bold!important;}
.red{color:#FF2323!important;} .blue{color:#0047EB!important;}
.sidebar-header{display:flex;align-items:center;gap:12px;margin-bottom:20px; font-size:22px;font-weight:bold;}
.insight-box{background-color:#f0f4f8;padding:20px;border-radius:10px;border-left:5px solid #007bff;margin-bottom:25px;}
.box-title{font-size:20px!important;font-weight:bold;margin-bottom:15px;display:block;color:#333;}
div[data-testid='stHorizontalBlock'] { gap: 0 !important; }
div[data-testid='column'] { padding: 0 !important; }
div.stButton>button { font-weight:normal!important; border-radius:3px; padding:0.2rem 0!important; width:100%!important; font-size:13px!important; margin:0!important; white-space:nowrap!important; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 세션 상태 관리
if 'sort_mode' not in st.session_state: st.session_state.sort_mode = 'init'
if 'show_code' not in st.session_state: st.session_state.show_code = False
if 'init' not in st.session_state:
    with st.spinner("데이터 로딩 중..."): Andy_pension_v2.generate_asset_data()
    st.session_state['init'] = True
    st.cache_data.clear()

# [복원] 좌측 ZAPPA AI 코딩창
with st.sidebar:
    st.markdown("<div class='sidebar-header'>🤖 <span>ZAPPA AI 코딩 엔진</span></div>", unsafe_allow_html=True)
    try:
        key = st.secrets.get("GOOGLE_API_KEY")
        if key:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            pmt = st.text_area("AI에게 요청", placeholder="수정할 내용을 입력하세요...")
            if st.button("수정 제안받기"):
                res = model.generate_content("Streamlit 수정: " + pmt)
                st.code(res.text)
    except Exception as e:
        st.error(f"ZAPPA 엔진 로딩 실패: {e}")

def fmt(v, sign=False):
    try:
        val = int(float(v))
        return f"{val:+,d}" if sign and val > 0 else f"{val:,d}"
    except: return str(v)

def fmt_p(v):
    try:
        val = float(v)
        return f"▲{val:.2f}%" if val > 0 else f"▼{abs(val):.2f}%" if val < 0 else "0.00%"
    except: return str(v)

def col(v):
    try:
        val = float(v)
        return "red" if val > 0 else "blue" if val < 0 else ""
    except: return ""

@st.cache_data(ttl=60)
def load():
    try:
        with open('assets.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return None

data = load()
if not data: st.stop()
tot = data.get("_total", {})

# [수정] 타이틀 명칭 변경
c1, c2 = st.columns([8.5, 1.5])
with c1: st.markdown("<h3>🚀 이상혁(Andy lee)님 절세계좌 통합 대시보드</h3>", unsafe_allow_html=True)
with c2:
    if st.button("🔄 업데이트", use_container_width=True):
        Andy_pension_v2.generate_asset_data()
        st.cache_data.clear()
        st.rerun()

st.markdown(f"<div style='text-align:right;font-size:14px;color:#555;margin:-10px 0 10px;'>[{tot.get('조회시간')}]</div>", unsafe_allow_html=True)

# [복원] 금융 자산 보고 요약 박스
if "_insight" in data:
    ins = ["<div class='insight-box'><span class='box-title'><u>금융 자산 보고 요약</u></span>"]
    for line in data["_insight"]:
        if "조회 기준" not in line: ins.append(f"<p style='margin-bottom:5px;'>• {line}</p>")
    ins.append("</div>")
    st.markdown("".join(ins), unsafe_allow_html=True)

unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW), %</div>"

# --- [1] 투자금 대비 자산 현황 ---
st.markdown("<div class='sub-title'>📊 [1] 투자금 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총 자산 : {fmt(tot.get('총 자산',0))} / 총 수익 : <span class='{col(tot.get('총 수익',0))}'>{fmt(tot.get('총 수익',0), True)} ({fmt_p(tot.get('수익률(%)',0))})</span>**", unsafe_allow_html=True)

h1 = [unit_html, "<table class='main-table'><tr><th>계좌 구분</th><th>총 자산</th><th>총 누계손익</th><th>수익률</th><th>최초원금</th></tr>"]
h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(tot['총 자산'])}</td><td class='{col(tot['총 수익'])}'>{fmt(tot['총 수익'],True)}</td><td class='{col(tot['수익률(%)'])}'>{fmt_p(tot['수익률(%)'])}</td><td>{fmt(tot['원금합'])}</td></tr>")
for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        h1.append(f"<tr><td>{a['label']}</td><td>{fmt(a['총 자산'])}</td><td class='{col(a['총 수익'])}'>{fmt(a['총 수익'],True)}</td><td class='{col(a['수익률(%)'])}'>{fmt_p(a['수익률(%)'])}</td><td>{fmt(a['원금'])}</td></tr>")
h1.append("</table>")
st.markdown("".join(h1), unsafe_allow_html=True)

# --- [2] 매입금액 대비 자산 현황 ---
ag_tot = tot.get('총 자산',0) - tot.get('매입금액합',0)
ay_tot = (ag_tot / tot.get('매입금액합',1) * 100) if tot.get('매입금액합',1) > 0 else 0
st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총 자산 : {fmt(tot.get('총 자산'))} / 총 수익 : <span class='{col(ag_tot)}'>{fmt(ag_tot, True)} ({fmt_p(ay_tot)})</span>**", unsafe_allow_html=True)

h2 = [unit_html, "<table class='main-table'><tr><th>계좌 구분</th><th>총 자산</th><th>평가손익</th><th>수익률</th><th>전일비</th><th>매입금액</th></tr>"]
h2.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(tot['총 자산'])}</td><td class='{col(ag_tot)}'>{fmt(ag_tot,True)}</td><td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td><td class='{col(tot['평가손익(전일비)'])}'>{fmt(tot['평가손익(전일비)'],True)}</td><td>{fmt(tot['매입금액합'])}</td></tr>")
for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        ag_acc = sum(i['평가손익'] for i in a['상세'] if i['종목명'] != '[ 합계 ]')
        ap_acc = a['총 자산'] - ag_acc
        ay_acc = (ag_acc/ap_acc*100) if ap_acc > 0 else 0
        h2.append(f"<tr><td>{a['label'].split('(')[0]}</td><td>{fmt(a['총 자산'])}</td><td class='{col(ag_acc)}'>{fmt(ag_acc,True)}</td><td class='{col(ay_acc)}'>{fmt_p(ay_acc)}</td><td class='{col(a['평가손익(전일비)'])}'>{fmt(a['평가손익(전일비)'],True)}</td><td>{fmt(ap_acc)}</td></tr>")
h2.append("</table>")
st.markdown("".join(h2), unsafe_allow_html=True)

# --- [3] 계좌별 상세 내역 ---
st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
# 버튼 우측 정렬 및 간격 밀착
spacer, b1, b2, b3, b4, b5 = st.columns([6.3, 0.7, 0.7, 0.7, 0.7, 0.9])
with b1:
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
for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        with st.expander(f"📂 [ {a['label']} ] 종목별 현황", expanded=False):
            s_data = next(i for i in a['상세'] if i['종목명'] == "[ 합계 ]")
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총 자산 : {fmt(a['총 자산'])} / 총 수익 : <span class='{col(s_data['평가손익'])}'>{fmt(s_data['평가손익'],True)} ({fmt_p(s_data['수익률(%)'])})</span>**", unsafe_allow_html=True)
            h3 = [unit_html, "<table class='main-table'><tr><th>종목명</th>"]
            if st.session_state.show_code: h3.append("<th>종목코드</th>")
            h3.append("<th>비중</th><th>총 자산</th><th>평가손익</th><th>수익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>")
            items = [i for i in a['상세'] if i['종목명'] != "[ 합계 ]"]
            if st.session_state.sort_mode == 'asset': items.sort(key=lambda x: x['총 자산'], reverse=True)
            elif st.session_state.sort_mode == 'profit': items.sort(key=lambda x: x['평가손익'], reverse=True)
            elif st.session_state.sort_mode == 'rate': items.sort(key=lambda x: x['수익률(%)'], reverse=True)
            for i in ([s_data] + items):
                is_s = (i['종목명'] == "[ 합계 ]"); row = f"<tr class='sum-row'>" if is_s else "<tr>"
                row += f"<td>{i['종목명']}</td>"
                if st.session_state.show_code: row += f"<td>{'-' if is_s or i.get('코드','-')=='-' else i['코드']}</td>"
                row += f"<td>{i['비중']:.1f}%</td><td>{fmt(i['총 자산'])}</td><td class='{col(i['평가손익'])}'>{fmt(i['평가손익'],True)}</td><td class='{col(i['수익률(%)'])}'>{fmt_p(i['수익률(%)'])}</td><td>{fmt(i['수량'])}</td><td>{fmt(i['매입가'])}</td><td>{fmt(i['현재가'])}</td></tr>"
                h3.append(row)
            h3.append("</table>")
            st.markdown("".join(h3), unsafe_allow_html=True)
