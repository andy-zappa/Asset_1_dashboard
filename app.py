import streamlit as st
import json
import warnings
import google.generativeai as genai
import Andy_pension_v2

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="Andy's Asset Dashboard")

# [핵심] CSS 수정: 우측 정렬 및 아이콘 크기 확대 적용
css = [
    "<style>",
    ".block-container{padding-top:3rem!important;padding-bottom:5rem!important;}",
    "h3{font-size:26px!important;font-weight:bold;margin-bottom:10px;}",
    ".sub-title{font-size:22px!important;font-weight:bold;margin:25px 0 10px;}",
    ".box-title{font-size:22px!important;font-weight:bold;margin-bottom:15px;display:block;color:#333;}",
    ".main-table{width:100%;border-collapse:collapse;font-size:15px;text-align:center;}",
    ".main-table th{background-color:#f2f2f2;padding:10px;border:1px solid #ddd;}",
    ".main-table td{padding:8px;border:1px solid #ddd;vertical-align:middle;}",
    ".sum-row td{background-color:#fff9e6;font-weight:bold!important;}",
    ".red{color:#FF2323!important;font-weight:bold;}",
    ".blue{color:#0047EB!important;font-weight:bold;}",
    ".insight-box{background-color:#f0f4f8;padding:20px;border-radius:10px;border-left:5px solid #007bff;margin-bottom:25px;}",
    ".sidebar-header{display:flex;align-items:center;gap:12px;margin-bottom:20px;}",
    ".sidebar-icon{font-size:32px;}",
    ".sidebar-text{font-size:22px;font-weight:bold;}",
    "div.stButton>button:first-child{font-weight:bold;border-radius:8px;padding:0 0.5rem!important;}",
    
    # 종목코드 열 숨기기 로직
    ".col-toggle-chk{display:none;}",
    ".col-toggle-chk:not(:checked)~.table-container .col-code{display:none!important;}",
    
    # [수정] 버튼 우측 정렬 및 디자인
    ".toggle-wrapper{text-align:right; margin-bottom:8px;}",
    ".col-toggle-label{cursor:pointer;font-size:13px;color:#555;font-weight:bold;display:inline-block;padding:5px 12px;border:1px solid #ccc;border-radius:5px;background:#f9f9f9;user-select:none;}",
    ".col-toggle-label:hover{background:#eee;color:#000;}",
    
    # [수정] 삼각형 아이콘 크게 변경 및 배치
    ".triangle{display:inline-block;transition:transform 0.2s;font-size:16px;margin-left:6px;vertical-align:middle;}",
    ".col-toggle-chk:checked+.col-toggle-label .triangle{transform:rotate(90deg);}",
    "</style>"
]
st.markdown("".join(css), unsafe_allow_html=True)

if 'init' not in st.session_state:
    with st.spinner("데이터 로딩 중..."):
        Andy_pension_v2.generate_asset_data()
    st.session_state['init'] = True
    st.cache_data.clear()

key = st.secrets.get("GOOGLE_API_KEY")
with st.sidebar:
    st.markdown("<div class='sidebar-header'><span class='sidebar-icon'>🤖</span><span class='sidebar-text'>ZAPPA AI 코딩 모드</span></div>", unsafe_allow_html=True)
    if key:
        try:
            genai.configure(api_key=key)
            models = genai.list_models()
            avail = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
            if avail:
                m_name = next((m for m in avail if 'flash' in m), avail[0])
                model = genai.GenerativeModel(m_name)
                pmt = st.text_area("AI에게 요청")
                if st.button("수정 제안받기"):
                    res = model.generate_content("Streamlit 수정: " + pmt)
                    st.code(res.text)
        except Exception as e:
            st.error(str(e))

def fmt(v, sign=False):
    try:
        val = int(v)
        return f"+{val:,}" if sign and val > 0 else f"{val:,}"
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
c1, c2 = st.columns([8.5, 1.5])
with c1:
    st.markdown("<h3>📝 이상혁(Andy lee)님 세제혜택 금융상품 자산 현황</h3>", unsafe_allow_html=True)
with c2:
    if st.button("🔄 업데이트", use_container_width=True):
        Andy_pension_v2.generate_asset_data()
        st.cache_data.clear()
        st.rerun()

st.markdown(f"<div style='text-align:right;font-size:14px;color:#555;margin:-10px 0 10px;'>[{tot.get('조회시간')}]</div>", unsafe_allow_html=True)

if "_insight" in data:
    ins = ["<div class='insight-box'><span class='box-title'><u>금융 자산 보고 요약</u></span>"]
    for line in data["_insight"]:
        if "조회 기준" not in line: ins.append(f"<p style='margin-bottom:5px;'>• {line}</p>")
    ins.append("</div>")
    st.markdown("".join(ins), unsafe_allow_html=True)

# --- [1] 투자금 대비 자산 현황 ---
pc = col(tot.get('총손익',0))
st.markdown("<div class='sub-title'>📊 [1] 투자금 대비 자산 현황</div>", unsafe_allow_html=True)
t1 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총자산 : {fmt(tot.get('총자산',0))} (원) / "
t1 += f"총수익 : <span class='{pc}'>{fmt(tot.get('총손익',0),True)} ({tot.get('수익률(%)',0):+.2f}%)</span>**"
st.markdown(t1, unsafe_allow_html=True)

h1 = ["<table class='main-table'><tr><th>계좌 구분</th><th>총자산</th><th>최초원금</th><th>수익률</th><th>평가금액</th><th>전일비</th></tr>"]
ty, tg, td = tot.get('수익률(%)',0), tot.get('총손익',0), tot.get('평가손익(전일비)',0)
h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(tot.get('총자산'))}</td><td>{fmt(tot.get('원금합'))}</td><td class='{col(ty)}'>{ty:+.2f}%</td><td class='{col(tg)}'>{fmt(tg,True)}</td><td class='{col(td)}'>{fmt(td,True)}</td></tr>")

for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        ay, ag, ad = a.get('수익률(%)',0), a.get('총손익',0), a.get('평가손익(전일비)',0)
        h1.append(f"<tr><td>{a.get('label')}</td><td>{fmt(a.get('총자산'))}</td><td>{fmt(a.get('원금'))}</td><td class='{col(ay)}'>{ay:+.2f}%</td><td class='{col(ag)}'>{fmt(ag,True)}</td><td class='{col(ad)}'>{fmt(ad,True)}</td></tr>")
h1.append("</table>")
st.markdown("".join(h1), unsafe_allow_html=True)

# --- [2] 매수금액 대비 자산 현황 ---
t2_lbl = {'DC':'퇴직연금(DC)계좌', 'PENSION':'연금저축(CMA)계좌', 'ISA':'ISA(중개형)계좌', 'IRP':'퇴직연금(IRP)계좌'}
ag_tot = tot.get('총자산',0) - tot.get('매수금액합',0)
ay_tot = (ag_tot / tot.get('매수금액합',1) * 100) if tot.get('매수금액합',1) > 0 else 0

st.markdown("<div class='sub-title'>📈 [2] 매수금액 대비 자산 현황</div>", unsafe_allow_html=True)
t2 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총자산 : {fmt(tot.get('총자산'))} (원) / "
t2 += f"총수익 : <span class='{col(ag_tot)}'>{fmt(ag_tot,True)} ({ay_tot:+.2f}%)</span>**"
st.markdown(t2, unsafe_allow_html=True)

h2 = ["<table class='main-table'><tr><th>계좌 구분</th><th>총자산</th><th>수익률</th><th>평가금액</th><th>매수금액</th></tr>"]
h2.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(tot.get('총자산'))}</td><td class='{col(ay_tot)}'>{ay_tot:+.2f}%</td><td class='{col(ag_tot)}'>{fmt(ag_tot,True)}</td><td>{fmt(tot.get('매수금액합'))}</td></tr>")

for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        ag = sum(i['평가손익'] for i in a['상세'] if i['종목명'] != '[ 합계 ]')
        ap = a.get('총자산',0) - ag
        ay = (ag/ap*100) if ap > 0 else 0
        h2.append(f"<tr><td>{t2_lbl.get(k, a.get('label'))}</td><td>{fmt(a.get('총자산'))}</td><td class='{col(ay)}'>{ay:+.2f}%</td><td class='{col(ag)}'>{fmt(ag,True)}</td><td>{fmt(ap)}</td></tr>")
h2.append("</table>")
st.markdown("".join(h2), unsafe_allow_html=True)

# --- [3] 계좌별 상세 내역 ---
t3_lbl = {'DC':'퇴직연금(DC)계좌 / (삼성증권 7165962472-28)', 'PENSION':'연금저축(CMA)계좌 / (삼성증권 7169434836-15)', 'ISA':'ISA(중개형)계좌 / (키움증권 6448-4934)', 'IRP':'퇴직연금(IRP)계좌 / (삼성증권 7164499007-29)'}
st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)

for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        with st.expander(f"📂 [ {t3_lbl.get(k, a.get('label'))} ] 종목별 현황"):
            s_data = next(i for i in a['상세'] if i['종목명'] == "[ 합계 ]")
            ag, ay = s_data['평가손익'], s_data['수익률(%)']
            t3 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총자산 : {fmt(a.get('총자산'))} (원) / "
            t3 += f"총수익 : <span class='{col(ag)}'>{fmt(ag,True)} ({ay:+.2f}%)</span>**"
            st.markdown(t3, unsafe_allow_html=True)

            # [수정] 우측 정렬 래퍼 및 아이콘 순서/크기 변경 적용
            h3 = [
                "<div class='toggle-wrapper'>", 
                f"<input type='checkbox' id='chk_{k}' class='col-toggle-chk'>", 
                f"<label for='chk_{k}' class='col-toggle-label'>종목코드 표시 <span class='triangle'>▶</span></label>", 
                "</div>",
                "<div class='table-container'><table class='main-table'><tr><th>종목명</th><th class='col-code'>종목코드</th><th>비중</th><th>총자산(원)</th><th>평가손익(원)</th><th>수익률</th><th>주식수</th><th>평단가</th><th>금일종가</th></tr>"
            ]

            for i in a.get('상세', []):
                is_sum = (i['종목명'] == "[ 합계 ]")
                r_cls = "class='sum-row'" if is_sum else ""
                cv = i.get('코드', '-')
                cdisp = "-" if is_sum or cv == "-" else f"<span>{cv}</span>"
                
                tr = f"<tr {r_cls}><td>{i['종목명']}</td><td class='col-code'>{cdisp}</td><td>{i.get('비중',0):.1f}%</td><td>{fmt(i['평가금액'])}</td><td class='{col(i['평가손익'])}'>{fmt(i['평가손익'],True)}</td><td class='{col(i['수익률(%)'])}'>{i['수익률(%)']:+.2f}%</td><td>{fmt(i['수량'])}</td><td>{fmt(i['평단가'])}</td><td>{fmt(i['가격'])}</td></tr>"
                h3.append(tr)
            h3.append("</table></div>")
            st.markdown("".join(h3), unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
