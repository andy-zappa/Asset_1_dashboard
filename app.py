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
    
    # 컬럼 좌우 패딩을 3px 수준으로 줄여 버튼 간격 바싹 밀착
    "div[data-testid='column'] { padding: 0 3px !important; }",
    
    # 폰트 사이즈 표기(15px), 볼드 해제, 버튼 상하좌우 패딩 축소
    "div.stButton>button{font-weight:normal!important; border-radius:4px; padding:0.2rem 0.2rem!important; width: 100%; font-size: 15px!important; margin:0!important;}",
    "</style>"
]
st.markdown("".join(css), unsafe_allow_html=True)

# 세션 상태 초기화 (정렬 및 종목코드 토글용)
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

# 포맷팅 함수
def fmt(v):
    try:
        val = int(float(v))
        return f"{val:,}"
    except: return str(v)

# 평가손익, 전일비용 포맷팅 (+, - 사용)
def fmt_money_sign(v):
    try:
        val = int(float(v))
        if val > 0: return f"+{val:,}"
        elif val < 0: return f"{val:,}" # 음수일 경우 '-'가 자동으로 붙습니다.
