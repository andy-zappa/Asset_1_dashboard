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
    ".box-title{font-size:22px!important;font-weight:bold;margin-bottom:15px;display:block;color:#333;}",
    ".main-table{width:100%;border-collapse:collapse;font-size:15px;text-align:center;margin-bottom:10px;}",
    ".main-table th{background-color:#f2f2f2;padding:10px;border:1px solid #ddd;font-weight:bold!important;}",
    ".main-table td{padding:8px;border:1px solid #ddd;vertical-align:middle;font-weight:normal!important;}",
    ".sum-row td{background-color:#fff9e6;font-weight:bold!important;}",
    ".red{color:#FF2323!important;}",
    ".blue{color:#0047EB!important;}",
    ".sum-row .red, .sum-row .blue{font-weight:bold!important;}",
    ".insight-box{background-color:#f0f4f8;padding:20px;border-radius:10px;border-left:5px solid #007bff;margin-bottom:25px;}",
    ".sidebar-header{display:flex;align-items:center;gap:12px;margin-bottom:20px;}",
    ".sidebar-icon{font-size:32px;}",
    ".sidebar-text{font-size:22px;font-weight:bold;}",
    
    # [버튼 UI 완벽 수정] 패딩 0으로 붙이고, 줄바꿈 강제 차단(nowrap)
    "div[data-testid='column'] { padding: 0 !important; }",
    "div.stButton>button { font-weight:normal!important; border-radius:4px; padding:0.2rem 0.1rem!important; width:100%; font-size:15px!important; margin:0!important; white-space:nowrap!important; }",
    "</style>"
]
st.markdown("".join(css), unsafe_allow_html=True)

# 세션 상태 초기화
if 'sort_mode' not in st.session_state: st.session_state.sort_mode = 'init'
if 'show_code' not in st.session_state: st.session_state.show_code = False

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

# ==========================================
# 포맷팅 함수 (에러 안나도록 깔끔하게 인라인 정리)
# ==========================================
def fmt(v):
    try: return f"{int(float(v)):,}"
    except: return str(v)

def fmt_money_sign(v):
    try:
        val = int(float(v))
        return f"+{val:,}" if val > 0 else f"{val:,}" if val < 0 else "0"
    except: return str(v)

def fmt_pct(v):
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

# 상단 헤더부
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

unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW), %</div>"

# --- [1] 투자금 대비 자산 현황 ---
st.markdown("<div class='sub-title'>📊 [1] 투자금 대비 자산 현황</div>", unsafe_allow_html=True)
t1 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총 자산 : {fmt(tot.get('총 자산',0))} / "
t1 += f"총 수익 : <span class='{col(tot.get('총 수익',0))}' style='font-weight:bold;'>{fmt_money_sign(tot.get('총 수익',0))} ({fmt_pct(tot.get('수익률(%)',0))})</span>**"
st.markdown(t1, unsafe_allow_html=True)

h1 = [unit_html, "<table class='main-table'><tr><th>계좌 구분</th><th>총 자산</th><th>총 누계손익</th><th>수익률</th><th>최초원금</th></tr>"]
ty, tg, t_asset, t_orig = tot.get('수익률(%)',0), tot.get('총 수익',0), tot.get('총 자산',0), tot.get('원금합',0)
h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(t_asset)}</td><td class='{col(tg)}'>{fmt_money_sign(tg)}</td><td class='{col(ty)}'>{fmt_pct(ty)}</td><td>{fmt(t_orig)}</td></tr>")

for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        ay, ag = a.get('수익률(%)',0), a.get('총 수익',0)
        h1.append(f"<tr><td>{a.get('label')}</td><td>{fmt(a.get('총 자산'))}</td><td class='{col(ag)}'>{fmt_money_sign(ag)}</td><td class='{col(ay)}'>{fmt_pct(ay)}</td><td>{fmt(a.get('원금'))}</td></tr>")
h1.append("</table>")
st.markdown("".join(h1), unsafe_allow_html=True)


# --- [2] 매수금액 대비 자산 현황 ---
t2_lbl = {'DC':'퇴직연금(DC)계좌', 'PENSION':'연금저축(CMA)계좌', 'ISA':'ISA(중개형)계좌', 'IRP':'퇴직연금(IRP)계좌'}
ag_tot = tot.get('총 자산',0) - tot.get('매입금액합',0)
ay_tot = (ag_tot / tot.get('매입금액합',1) * 100) if tot.get('매입금액합',1) > 0 else 0

st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
t2 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총 자산 : {fmt(tot.get('총 자산'))} / "
t2 += f"총 수익 : <span class='{col(ag_tot)}' style='font-weight:bold;'>{fmt_money_sign(ag_tot)} ({fmt_pct(ay_tot)})</span>**"
st.markdown(t2, unsafe_allow_html=True)

h2 = [unit_html, "<table class='main-table'><tr><th>계좌 구분</th><th>총 자산</th><th>평가손익</th><th>수익률</th><th>전일비</th><th>매입금액</th></tr>"]
td_tot = tot.get('평가손익(전일비)',0)
h2.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(tot.get('총 자산'))}</td><td class='{col(ag_tot)}'>{fmt_money_sign(ag_tot)}</td><td class='{col(ay_tot)}'>{fmt_pct(ay_tot)}</td><td class='{col(td_tot)}'>{fmt_money_sign(td_tot)}</td><td>{fmt(tot.get('매입금액합'))}</td></tr>")

for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        ag_acc = sum(i.get('평가손익',0) for i in a['상세'] if i['종목명'] != '[ 합계 ]')
        ap_acc = a.get('총 자산',0) - ag_acc
        ay_acc = (ag_acc/ap_acc*100) if ap_acc > 0 else 0
        ad_acc = a.get('평가손익(전일비)', 0)
        h2.append(f"<tr><td>{t2_lbl.get(k, a.get('label'))}</td><td>{fmt(a.get('총 자산'))}</td><td class='{col(ag_acc)}'>{fmt_money_sign(ag_acc)}</td><td class='{col(ay_acc)}'>{fmt_pct(ay_acc)}</td><td class='{col(ad_acc)}'>{fmt_money_sign(ad_acc)}</td><td>{fmt(ap_acc)}</td></tr>")
h2.append("</table>")
st.markdown("".join(h2), unsafe_allow_html=True)


# --- [3] 계좌별 상세 내역 ---
t3_lbl = {'DC':'퇴직연금(DC)계좌 / (삼성증권 7165962472-28)', 'PENSION':'연금저축(CMA)계좌 / (삼성증권 7169434836-15)', 'ISA':'ISA(중개형)계좌 / (키움증권 6448-4934)', 'IRP':'퇴직연금(IRP)계좌 / (삼성증권 7164499007-29)'}
st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)

# [수정] 박스 찌그러짐을 방지하기 위해 각 버튼 열에 조금 더 넉넉한 비율 부여 (총 너비 합은 우측 정렬 유지)
spacer, b1, b2, b3, b4, b5 = st.columns([4.2, 0.9, 0.9, 0.9, 0.9, 1.3])
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

for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        a = data[k]
        with st.expander(f"📂 [ {t3_lbl.get(k, a.get('label'))} ] 종목별 현황", expanded=False):
            s_data = next(i for i in a['상세'] if i['종목명'] == "[ 합계 ]")
            ag_acc, ay_acc = s_data['평가손익'], s_data['수익률(%)']
            t3 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총 자산 : {fmt(a.get('총 자산'))} / "
            t3 += f"총 수익 : <span class='{col(ag_acc)}' style='font-weight:bold;'>{fmt_money_sign(ag_acc)} ({fmt_pct(ay_acc)})</span>**"
            st.markdown(t3, unsafe_allow_html=True)

            h3 = [unit_html, "<table class='main-table'><tr><th>종목명</th>"]
            if st.session_state.show_code:
                h3.append("<th>종목코드</th>")
            h3.append("<th>비중</th><th>총 자산</th><th>평가손익</th><th>수익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>")

            raw_items = a.get('상세', [])
            sum_row = next((i for i in raw_items if i['종목명'] == "[ 합계 ]"), None)
            items = [i for i in raw_items if i['종목명'] != "[ 합계 ]"]
            
            if st.session_state.sort_mode == 'asset':
                items.sort(key=lambda x: x.get('총 자산', 0), reverse=True)
            elif st.session_state.sort_mode == 'profit':
                items.sort(key=lambda x: x.get('평가손익', 0), reverse=True)
            elif st.session_state.sort_mode == 'rate':
                items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)

            disp_list = ([sum_row] if sum_row else []) + items

            for i in disp_list:
                is_sum = (i['종목명'] == "[ 합계 ]")
                r_cls = "class='sum-row'" if is_sum else ""
                
                row_html = f"<tr {r_cls}><td>{i['종목명']}</td>"
                if st.session_state.show_code:
                    cdisp = "-" if (is_sum or i.get('코드', '-') == "-") else i.get('코드', '-')
                    row_html += f"<td>{cdisp}</td>"
                    
                row_html += f"<td>{i.get('비중',0):.1f}%</td>"
                row_html += f"<td>{fmt(i.get('총 자산',0))}</td>"
                row_html += f"<td class='{col(i.get('평가손익',0))}'>{fmt_money_sign(i.get('평가손익',0))}</td>"
                row_html += f"<td class='{col(i.get('수익률(%)',0))}'>{fmt_pct(i.get('수익률(%)',0))}</td>"
                row_html += f"<td>{fmt(i.get('수량','-'))}</td>"
                row_html += f"<td>{fmt(i.get('매입가','-'))}</td>"
                row_html += f"<td>{fmt(i.get('현재가','-'))}</td></tr>"
                h3.append(row_html)
                
            h3.append("</table>")
            st.markdown("".join(h3), unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
