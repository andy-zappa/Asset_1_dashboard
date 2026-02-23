import streamlit as st
import json
import pandas as pd
import warnings
import google.generativeai as genai
import Andy_pension_v2

# 경고 무시
warnings.filterwarnings("ignore", category=FutureWarning)

st.set_page_config(layout="wide", page_title="Andy's Asset Dashboard")

st.markdown("""
    <style>
    .block-container { padding-top: 3rem !important; padding-bottom: 5rem !important; }
    h3 { font-size: 26px !important; font-weight: bold; margin-top: 0px !important; margin-bottom: 10px; } 
    .sub-title { font-size: 22px !important; font-weight: bold; margin-top: 25px; margin-bottom: 10px; }
    .box-title { font-size: 22px !important; font-weight: bold; margin-bottom: 15px; display: block; color: #333; }
    .main-table { width: 100%; border-collapse: collapse; font-size: 15px; text-align: center; } 
    .main-table th { background-color: #f2f2f2; padding: 10px; border: 1px solid #ddd; font-weight: bold !important; }
    .main-table td { padding: 8px; border: 1px solid #ddd; font-weight: normal !important; }
    .sum-row td { background-color: #fff9e6; font-weight: bold !important; }
    .red { color: #FF2323 !important; }
    .blue { color: #0047EB !important; }
    .sum-row .red, .sum-row .blue { font-weight: bold !important; }
    .insight-box { background-color: #f0f4f8; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 25px; }
    [data-testid="stSidebar"] span { filter: none !important; }
    .sidebar-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
    .sidebar-icon { font-size: 32px; font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji"; }
    .sidebar-text { font-size: 22px; font-weight: bold; }
    div.stButton > button:first-child { font-weight: bold; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

if 'initialized' not in st.session_state:
    with st.spinner("초기 실시간 데이터를 불러오는 중입니다..."):
        Andy_pension_v2.generate_asset_data()
    st.session_state['initialized'] = True; st.cache_data.clear()

api_key = st.secrets.get("GOOGLE_API_KEY")
with st.sidebar:
    st.markdown('<div class="sidebar-header"><span class="sidebar-icon">🤖</span><span class="sidebar-text">ZAPPA AI 코딩 모드</span></div>', unsafe_allow_html=True)
    if api_key:
        try:
            genai.configure(api_key=api_key)
            
            # [궁극의 해결책] 숨바꼭질 종료: 구글에 직접 물어보고 사용 가능한 모델을 자동 선택합니다.
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if available_models:
                # 사용 가능한 모델 중 flash가 있으면 우선적으로 잡고, 없으면 구글이 주는 첫 번째 호환 모델을 강제 지정합니다.
                target_model = next((m for m in available_models if 'flash' in m), available_models[0])
                model = genai.GenerativeModel(target_model)
                
                prompt = st.text_area("AI에게 수정 요청")
                if st.button("코드 수정 제안받기"):
                    res = model.generate_content(f"Streamlit 수정 제안: {prompt}"); st.code(res.text)
            else:
                st.error("사용 가능한 AI 모델 목록이 없습니다. 구글 API 권한을 확인해주세요.")
                
        except Exception as e: st.error(f"AI 시스템 오류: {e}")

def format_comma(val, force_sign=False):
    try: 
        v = int(val); return f"{'+' if force_sign and v > 0 else ''}{v:,}"
    except: return val

@st.cache_data(ttl=60)
def load_data():
    try:
        with open('assets.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return None

data = load_data()
if not data: st.stop()

total = data.get("_total", {})
col1, col2 = st.columns([8, 2])
with col1: st.markdown(f"<h3>📝 이상혁(Andy lee)님 세제혜택 금융상품 자산 현황</h3>", unsafe_allow_html=True)
with col2:
    if st.button("🔄 실시간 업데이트", use_container_width=True):
        with st.spinner("한국투자증권 데이터 갱신 중..."):
            Andy_pension_v2.generate_asset_data(); st.cache_data.clear(); st.rerun()
st.markdown(f"<div style='text-align: right; font-size: 14px; color: #555; margin-bottom: 10px; margin-top: -10px;'>[{total.get('조회시간')}]&nbsp;&nbsp;</div>", unsafe_allow_html=True)

if "_insight" in data:
    filtered = [l for l in data["_insight"] if "조회 기준 시간" not in l]
    content = "".join([f"<p style='margin-bottom:5px;'>• {l}</p>" for l in filtered])
    st.markdown(f"<div class='insight-box'><span class='box-title'>금융 자산 보고 요약</span>{content}</div>", unsafe_allow_html=True)

# --- [1] 투자금 대비 자산 현황 ---
p_color = "red" if total.get('총손익', 0) > 0 else "blue"
st.markdown("<div class='sub-title'>📊 [1] 투자금 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총자산 : {format_comma(total.get('총자산', 0))} (원) / 총수익 : <span class='{p_color}' style='font-weight: bold;'>{format_comma(total.get('총손익', 0), True)} ({total.get('수익률(%)', 0):+.2f}%)</span>**", unsafe_allow_html=True)

html1 = "<table class='main-table'><tr><th>계좌 구분</th><th>총자산</th><th>수익률</th><th>평가금액 (전일比)</th><th>최초원금</th></tr>"
c_t = "red" if total.get('총손익', 0) > 0 else "blue"
html1 += f"<tr class='sum-row'><td>[ 합계 ]</td><td>{format_comma(total.get('총자산'))}</td><td class='{c_t}'>{total.get('수익률(%)'):+.2f}%</td><td class='{c_t}'>{format_comma(total.get('총손익'), True)} ({format_comma(total.get('평가손익(전일비)'), True)})</td><td>{format_comma(total.get('원금합'))}</td></tr>"
for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        acc = data[k]; c = "red" if acc.get('총손익', 0) > 0 else "blue"
        html1 += f"<tr><td>{acc.get('label')}</td><td>{format_comma(acc.get('총자산'))}</td><td class='{c}'>{acc.get('수익률(%)'):+.2f}%</td><td class='{c}'>{format_comma(acc.get('총손익'), True)} ({format_comma(acc.get('평가손익(전일비)'), True)})</td><td>{format_comma(acc.get('원금'))}</td></tr>"
st.markdown(html1 + "</table>", unsafe_allow_html=True)

# --- [2] 매수금액 대비 자산 현황 ---
t_acc_g = total.get('총자산', 0) - total.get('매수금액합', 0); t_acc_y = (t_acc_g / total.get('매수금액합', 1) * 100); pg_c = "red" if t_acc_g > 0 else "blue"
st.markdown("<div class='sub-title'>📈 [2] 매수금액 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총자산 : {format_comma(total.get('총자산'))} (원) / 총수익 : <span class='{pg_c}' style='font-weight: bold;'>{format_comma(t_acc_g, True)} ({t_acc_y:+.2f}%)</span>**", unsafe_allow_html=True)

html2 = "<table class='main-table'><tr><th>계좌 구분</th><th>총자산</th><th>수익률</th><th>평가금액</th><th>매수금액</th></tr>"
html2 += f"<tr class='sum-row'><td>[ 합계 ]</td><td>{format_comma(total.get('총자산'))}</td><td class='{pg_c}'>{t_acc_y:+.2f}%</td><td class='{pg_c}'>{format_comma(t_acc_g, True)}</td><td>{format_comma(total.get('매수금액합'))}</td></tr>"
for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        acc = data[k]; acc_g = sum(i['평가손익'] for i in acc['상세'] if i['종목명'] != '[ 합계 ]'); acc_p = acc.get('총자산', 0) - acc_g; c = "red" if acc_g > 0 else "blue"
        html2 += f"<tr><td>{acc.get('label')}</td><td>{format_comma(acc.get('총자산'))}</td><td class='{c}'>{(acc_g/acc_p*100 if acc_p>0 else 0):+.2f}%</td><td class='{c}'>{format_comma(acc_g, True)}</td><td>{format_comma(acc_p)}</td></tr>"
st.markdown(html2 + "</table>", unsafe_allow_html=True)

# --- [3] 계좌별 상세 내역 ---
st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
for k in ['DC', 'PENSION', 'ISA', 'IRP']:
    if k in data:
        acc = data[k]
        with st.expander(f"📂 [ {acc.get('label')} ] 종목별 현황"):
            sum_row_data = next(i for i in acc['상세'] if i['종목명'] == "[ 합계 ]")
            acc_val_gain = sum_row_data['평가손익']
            acc_val_yield = sum_row_data['수익률(%)']
            c_s = "red" if acc_val_gain > 0 else "blue"
            
            st.markdown(f"&nbsp;&nbsp;&nbsp
