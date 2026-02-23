import streamlit as st
import json
import pandas as pd
import warnings
import google.generativeai as genai
import Andy_pension_v2

warnings.filterwarnings("ignore", category=FutureWarning)

st.set_page_config(layout="wide", page_title="Andy's Asset Dashboard")

css = """

<style>
.block-container { padding-top: 3rem !important; }
.block-container { padding-bottom: 5rem !important; }
h3 { font-size: 26px !important; font-weight: bold; }
h3 { margin-top: 0px !important; margin-bottom: 10px; }
.sub-title { font-size: 22px !important; font-weight: bold; }
.sub-title { margin-top: 25px; margin-bottom: 10px; }
.box-title { font-size: 22px !important; font-weight: bold; }
.box-title { margin-bottom: 15px; display: block; color: #333; }
.main-table { width: 100%; border-collapse: collapse; }
.main-table { font-size: 15px; text-align: center; }
.main-table th { background-color: #f2f2f2; padding: 10px; }
.main-table th { border: 1px solid #ddd; font-weight: bold !important; }
.main-table td { padding: 8px; border: 1px solid #ddd; }
.main-table td { font-weight: normal !important; }
.main-table td { vertical-align: middle; }
.sum-row td { background-color: #fff9e6; font-weight: bold !important; }
.red { color: #FF2323 !important; }
.blue { color: #0047EB !important; }
.sum-row .red { font-weight: bold !important; }
.sum-row .blue { font-weight: bold !important; }
.insight-box { background-color: #f0f4f8; padding: 20px; }
.insight-box { border-radius: 10px; border-left: 5px solid #007bff; }
.insight-box { margin-bottom: 25px; }
[data-testid="stSidebar"] span { filter: none !important; }
.sidebar-header { display: flex; align-items: center; gap: 12px; }
.sidebar-header { margin-bottom: 20px; }
.sidebar-icon { font-size: 32px; }
.sidebar-text { font-size: 22px; font-weight: bold; }
div.stButton > button:first-child { font-weight: bold; }
div.stButton > button:first-child { border-radius: 8px; }
div.stButton > button:first-child { padding-left: 0.5rem !important; }
div.stButton > button:first-child { padding-right: 0.5rem !important; }

.col-toggle-chk { display: none; }
.col-toggle-chk:not(:checked) ~ .table-container .col-code {
display: none !important;
}
.col-toggle-label { display: inline-block; margin-bottom: 8px; }
.col-toggle-label { font-size: 13px; color: #555; cursor: pointer; }
.col-toggle-label { font-weight: bold; user-select: none; }
.col-toggle-label:hover { color: #000; }
.triangle { display: inline-block; font-size: 11px; }
.triangle { margin-right: 4px; transition: transform 0.2s; }
.col-toggle-chk:checked + .col-toggle-label .triangle {
transform: rotate(90deg);
}
</style>

"""
st.markdown(css, unsafe_allow_html=True)

if 'initialized' not in st.session_state:
with st.spinner("초기 데이터 로딩 중..."):
Andy_pension_v2.generate_asset_data()
st.session_state['initialized'] = True
st.cache_data.clear()

api_key = st.secrets.get("GOOGLE_API_KEY")
with st.sidebar:
sb_html = "<div class='sidebar-header'>"
sb_html += "<span class='sidebar-icon'>🤖</span>"
sb_html += "<span class='sidebar-text'>ZAPPA AI 코딩 모드</span>"
sb_html += "</div>"
st.markdown(sb_html, unsafe_allow_html=True)

if api_key:
    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        avail = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        if avail:
            t_model = next((m for m in avail if 'flash' in m), avail[0])
            model = genai.GenerativeModel(t_model)
            prompt = st.text_area("AI에게 수정 요청")
            if st.button("코드 수정 제안받기"):
                res = model.generate_content("Streamlit 수정 제안: " + prompt)
                st.code(res.text)
        else:
            st.error("사용 가능한 AI 모델이 없습니다.")
    except Exception as e:
        st.error("AI 오류: " + str(e))
def format_comma(val, force_sign=False):
try:
v = int(val)
s = "+" if force_sign and v > 0 else ""
return f"{s}{v:,}"
except:
return val

def get_color(val):
try:
v = float(val)
if v > 0: return "red"
if v < 0: return "blue"
return ""
except:
return ""

@st.cache_data(ttl=60)
def load_data():
try:
with open('assets.json', 'r', encoding='utf-8') as f:
return json.load(f)
except:
return None

data = load_data()
if not data: st.stop()

total = data.get("_total", {})

col1, col2 = st.columns([8.5, 1.5])
with col1:
title_str = "<h3>📝 이상혁(Andy lee)님 세제혜택 금융상품 자산 현황</h3>"
st.markdown(title_str, unsafe_allow_html=True)
with col2:
if st.button("🔄 실시간 업데이트", use_container_width=True):
with st.spinner("데이터 갱신 중..."):
Andy_pension_v2.generate_asset_data()
st.cache_data.clear()
st.rerun()

time_str = total.get('조회시간', '조회 중...')
time_html = "<div style='text-align: right; font-size: 14px; "
time_html += "color: #555; margin-bottom: 10px; margin-top: -10px;'>"
time_html += f"[{time_str}]  </div>"
st.markdown(time_html, unsafe_allow_html=True)

if "_insight" in data:
in_html = "<div class='insight-box'>"
in_html += "<span class='box-title'><u>금융 자산 보고 요약</u></span>"
for line in data["_insight"]:
if "조회 기준 시간" not in line:
in_html += f"<p style='margin-bottom:5px;'>• {line}</p>"
in_html += "</div>"
st.markdown(in_html, unsafe_allow_html=True)

p_color = get_color(total.get('총손익', 0))
st.markdown("<div class='sub-title'>📊 [1] 투자금 대비 자산 현황</div>", unsafe_allow_html=True)

t1_1 = "            "
t1_2 = f"총자산 : {format_comma(total.get('총자산', 0))} (원) / "
t1_3 = f"총수익 : <span class='{p_color}' style='font-weight: bold;'>"
t1_4 = f"{format_comma(total.get('총손익', 0), True)} "
t1_5 = f"({total.get('수익률(%)', 0):+.2f}%)</span>"
st.markdown(t1_1 + t1_2 + t1_3 + t1_4 + t1_5, unsafe_allow_html=True)

html1 = "<table class='main-table'>"
html1 += "<tr><th>계좌 구분</th><th>총자산</th><th>최초원금</th>"
html1 += "<th>수익률</th><th>평가금액</th><th>전일비</th></tr>"

t_y = total.get('수익률(%)', 0)
t_g = total.get('총손익', 0)
t_d = total.get('평가손익(전일비)', 0)

html1 += "<tr class='sum-row'><td>[ 합계 ]</td>"
html1 += f"<td>{format_comma(total.get('총자산'))}</td>"
html1 += f"<td>{format_comma(total.get('원금합'))}</td>"
html1 += f"<td class='{get_color(t_y)}'>{t_y:+.2f}%</td>"
html1 += f"<td class='{get_color(t_g)}'>{format_comma(t_g, True)}</td>"
html1 += f"<td class='{get_color(t_d)}'>{format_comma(t_d, True)}</td></tr>"

for k in ['DC', 'PENSION', 'ISA', 'IRP']:
if k in data:
acc = data[k]
a_y = acc.get('수익률(%)', 0)
a_g = acc.get('총손익', 0)
a_d = acc.get('평가손익(전일비)', 0)
html1 += "<tr>"
html1 += f"<td>{acc.get('label')}</td>"
html1 += f"<td>{format_comma(acc.get('총자산'))}</td>"
html1 += f"<td>{format_comma(acc.get('원금'))}</td>"
html1 += f"<td class='{get_color(a_y)}'>{a_y:+.2f}%</td>"
html1 += f"<td class='{get_color(a_g)}'>{format_comma(a_g, True)}</td>"
html1 += f"<td class='{get_color(a_d)}'>{format_comma(a_d, True)}</td>"
html1 += "</tr>"

html1 += "</table>"
st.markdown(html1, unsafe_allow_html=True)

t2_labels = {
'DC': '퇴직연금(DC)계좌',
'PENSION': '연금저축(CMA)계좌',
'ISA': 'ISA(중개형)계좌',
'IRP': '퇴직연금(IRP)계좌'
}

t_acc_g = total.get('총자산', 0) - total.get('매수금액합', 0)
t_acc_y = (t_acc_g / total.get('매수금액합', 1) * 100) if total.get('매수금액합', 1) > 0 else 0
pg_c = get_color(t_acc_g)

st.markdown("<div class='sub-title'>📈 [2] 매수금액 대비 자산 현황</div>", unsafe_allow_html=True)

t2_1 = "            "
t2_2 = f"총자산 : {format_comma(total.get('총자산'))} (원) / "
t2_3 = f"총수익 : <span class='{pg_c}' style='font-weight: bold;'>"
t2_4 = f"{format_comma(t_acc_g, True)} ({t_acc_y:+.2f}%)</span>"
st.markdown(t2_1 + t2_2 + t2_3 + t2_4, unsafe_allow_html=True)

html2 = "<table class='main-table'>"
html2 += "<tr><th>계좌 구분</th><th>총자산</th><th>수익률</th>"
html2 += "<th>평가금액</th><th>매수금액</th></tr>"

html2 += "<tr class='sum-row'><td>[ 합계 ]</td>"
html2 += f"<td>{format_comma(total.get('총자산'))}</td>"
html2 += f"<td class='{get_color(t_acc_y)}'>{t_acc_y:+.2f}%</td>"
html2 += f"<td class='{get_color(t_acc_g)}'>{format_comma(t_acc_g, True)}</td>"
html2 += f"<td>{format_comma(total.get('매수금액합'))}</td></tr>"

for k in ['DC', 'PENSION', 'ISA', 'IRP']:
if k in data:
acc = data[k]
acc_g = sum(i['평가손익'] for i in acc['상세'] if i['종목명'] != '[ 합계 ]')
acc_p = acc.get('총자산', 0) - acc_g
acc_y = (acc_g/acc_p*100) if acc_p > 0 else 0

    lbl = t2_labels.get(k, acc.get('label'))
    html2 += "<tr>"
    html2 += f"<td>{lbl}</td>"
    html2 += f"<td>{format_comma(acc.get('총자산'))}</td>"
    html2 += f"<td class='{get_color(acc_y)}'>{acc_y:+.2f}%</td>"
    html2 += f"<td class='{get_color(acc_g)}'>{format_comma(acc_g, True)}</td>"
    html2 += f"<td>{format_comma(acc_p)}</td>"
    html2 += "</tr>"
html2 += "</table>"
st.markdown(html2, unsafe_allow_html=True)

t3_labels = {
'DC': '퇴직연금(DC)계좌 / (삼성증권 7165962472-28)',
'PENSION': '연금저축(CMA)계좌 / (삼성증권 7169434836-15)',
'ISA': 'ISA(중개형)계좌 / (키움증권 6448-4934)',
'IRP': '퇴직연금(IRP)계좌 / (삼성증권 7164499007-29)'
}

st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
for k in ['DC', 'PENSION', 'ISA', 'IRP']:
if k in data:
acc = data[k]
exp_title = f"📂 [ {t3_labels.get(k, acc.get('label'))} ] 종목별 현황"

    with st.expander(exp_title):
        sum_data = next(i for i in acc['상세'] if i['종목명'] == "[ 합계 ]")
        a_gain = sum_data['평가손익']
        a_y = sum_data['수익률(%)']
        c_s = get_color(a_gain)
        
        t3_1 = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        t3_2 = f"**총자산 : {format_comma(acc.get('총자산'))} (원) / "
        t3_3 = f"총수익 : <span class='{c_s}' style='font-weight: bold;'>"
        t3_4 = f"{format_comma(a_gain, True)} ({a_y:+.2f}%)</span>**"
        st.markdown(t3_1 + t3_2 + t3_3 + t3_4, unsafe_allow_html=True)
        
        html3 = "<div>"
        html3 += f"<input type='checkbox' id='chk_{k}' "
        html3 += "class='col-toggle-chk' checked>"
        html3 += f"<label for='chk_{k}' class='col-toggle-label'>"
        html3 += "<span class='triangle'>▶</span> 종목코드 표시</label>"
        html3 += "<div class='table-container'>"
        html3 += "<table class='main-table'>"
        html3 += "<tr><th>종목명</th><th class='col-code'>종목코드</th>"
        html3 += "<th>비중</th><th>총자산(원)</th><th>평가손익(원)</th>"
        html3 += "<th>수익률</th><th>주식수</th><th>평단가</th>"
        html3 += "<th>금일종가</th></tr>"
        
        for i in acc.get('상세', []):
            is_sum = (i['종목명'] == "[ 합계 ]")
            row_cls = "class='sum-row'" if is_sum else ""
            c_g = get_color(i['평가손익'])
            c_y = get_color(i['수익률(%)'])
            
            code_val = i.get('코드', '-')
            if is_sum or code_val == "-":
                code_disp = "-"
            else:
                code_disp = f"<span style='color:#0047EB; font-weight:bold;'>"
                code_disp += f"{code_val}</span>"
            
            html3 += f"<tr {row_cls}>"
            html3 += f"<td>{i['종목명']}</td>"
            html3 += f"<td class='col-code'>{code_disp}</td>"
            html3 += f"<td>{i.get('비중', 0):.1f}%</td>"
            html3 += f"<td>{format_comma(i['평가금액'])}</td>"
            html3 += f"<td class='{c_g}'>{format_comma(i['평가손익'], True)}</td>"
            html3 += f"<td class='{c_y}'>{i['수익률(%)']:+.2f}%</td>"
            html3 += f"<td>{format_comma(i['수량'])}</td>"
            html3 += f"<td>{format_comma(i['평단가'])}</td>"
            html3 += f"<td>{format_comma(i['가격'])}</td>"
            html3 += "</tr>"
        
        html3 += "</table></div></div>"
        st.markdown(html3, unsafe_allow_html=True)
st.markdown("



", unsafe_allow_html=True)
