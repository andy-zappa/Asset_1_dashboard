import streamlit as st
import json
import pandas as pd
import warnings
import google.generativeai as genai

# 경고 무시
warnings.filterwarnings("ignore", category=FutureWarning)

# 1. 페이지 설정 및 디자인 고도화
st.set_page_config(layout="wide", page_title="Andy's Asset Dashboard")

# [수정] 상단 여백 및 제목 위치 조정 CSS
st.markdown("""
    <style>
    /* 화면 최상단 여백 완전히 제거 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    h3 { 
        font-size: 26px !important; 
        font-weight: bold; 
        margin-top: -15px !important; /* 제목을 더 위로 올림 */
        margin-bottom: 5px; 
    } 
    .sub-title { font-size: 20px !important; font-weight: bold; margin-top: 20px; margin-bottom: 8px; }
    .main-table { width: 100%; border-collapse: collapse; font-size: 14px; text-align: center; } 
    .main-table th { background-color: #f2f2f2; padding: 10px; border: 1px solid #ddd; }
    .main-table td { padding: 8px; border: 1px solid #ddd; }
    .sum-row { background-color: #fff9e6; font-weight: bold; }
    .red { color: #FF2323 !important; font-weight: bold; }
    .blue { color: #0047EB !important; font-weight: bold; }
    .insight-box { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 20px; font-size: 15px; }
    div[data-testid="stExpander"] summary p { font-size: 16px !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 사이드바 AI 설정 (Secrets 연동)
api_key = st.secrets.get("GOOGLE_API_KEY")

with st.sidebar:
    st.title("🤖 ZAPPA AI 코딩 모드")
    if api_key:
        st.success("API Key 자동 연결됨")
        try:
            genai.configure(api_key=api_key)
            # 모델명은 가장 호환성 좋은 이름으로 고정
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = st.text_area("AI에게 수정 요청")
            if st.button("코드 수정 제안받기"):
                res = model.generate_content(f"Streamlit 수정 제안: {prompt}")
                st.code(res.text)
        except Exception as e: 
            st.error(f"AI 오류: {e}")

# 3. 데이터 로딩 및 포맷팅 함수
def format_comma(val, force_sign=False):
    try: 
        v = int(val)
        if force_sign and v > 0: return f"+{v:,}"
        return f"{v:,}"
    except: return val

@st.cache_data(ttl=60)
def load_data():
    try:
        with open('assets.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return None

data = load_data()
if not data:
    st.warning("데이터를 불러오는 중입니다...")
    st.stop()

total = data.get("_total", {})
fetch_time = total.get('조회시간', '조회 중...')

# 4. 메인 대시보드 출력
# 제목과 조회시간을 최상단에 배치
st.markdown(f"<h3>📝 이상혁(Andy lee)님 세제혜택 금융상품 자산 현황</h3>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align: right; font-size: 14px; color: gray; margin-bottom: 5px;'>[{fetch_time}]</div>", unsafe_allow_html=True)

# [자파의 인사이트] 요약 박스
if "_insight" in data:
    content = "".join([f"<p style='margin-bottom:4px;'>• {line}</p>" for line in data["_insight"]])
    st.markdown(f"<div class='insight-box'><strong>[자파의 자산 인사이트]</strong><br>{content}</div>", unsafe_allow_html=True)

# --- [1] 투자금 대비 자산 현황 ---
p_color = "red" if total.get('총손익', 0) > 0 else "blue"
st.markdown("<div class='sub-title'>📊 [1] 투자금 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총자산 : {format_comma(total.get('총자산', 0))} (원) / 총수익 : <span class='{p_color}'>{format_comma(total.get('총손익', 0), True)} ({total.get('수익률(%)', 0):+.2f}%)</span>**", unsafe_allow_html=True)

html1 = "<table class='main-table'><tr><th>계좌 구분</th><th>총자산</th><th>수익률</th><th>평가금액(전일比)</th><th>최초원금</th></tr>"
t_prin = total.get('원금합', 0); t_asset = total.get('총자산', 0); t_gain = total.get('총손익', 0); t_yield = total.get('수익률(%)', 0); t_diff = total.get('평가손익(전일비)', 0)
c_tot1 = "red" if t_gain > 0 else "blue"
html1 += f"<tr class='sum-row'><td>[ 합계 ]</td><td>{format_comma(t_asset)}</td><td class='{c_tot1}'>{t_yield:+.2f}%</td><td class='{c_tot1}'>{format_comma(t_gain, True)} ({format_comma(t_diff, True)})</td><td>{format_comma(t_prin)}</td></tr>"
for key in ['DC', 'PENSION', 'ISA', 'IRP']:
    if key in data:
        acc = data[key]; c = "red" if acc.get('총손익', 0) > 0 else "blue"
        html1 += f"<tr><td>{acc.get('label')}</td><td>{format_comma(acc.get('총자산', 0))}</td><td class='{c}'>{acc.get('수익률(%)', 0):+.2f}%</td><td class='{c}'>{format_comma(acc.get('총손익', 0), True)} ({format_comma(acc.get('평가손익(전일비)', 0), True)})</td><td>{format_comma(acc.get('원금', 0))}</td></tr>"
st.markdown(html1 + "</table>", unsafe_allow_html=True)

# --- [2] 매수금액 대비 자산 현황 ---
t_acc_g = sum(sum(i['평가손익'] for i in data[k]['상세'] if i['종목명'] != '[ 합계 ]') for k in ['DC', 'PENSION', 'ISA', 'IRP'] if k in data)
t_acc_p = t_asset - t_acc_g; t_acc_yield = (t_acc_g / t_acc_p * 100) if t_acc_p > 0 else 0; pg_color = "red" if t_acc_g > 0 else "blue"
st.markdown("<div class='sub-title'>📈 [2] 매수금액(평단가) 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총자산 : {format_comma(t_asset)} (원) / 총수익 : <span class='{pg_color}'>{format_comma(t_acc_g, True)} ({t_acc_yield:+.2f}%)</span>**", unsafe_allow_html=True)

html2 = "<table class='main-table'><tr><th>계좌 구분</th><th>총자산</th><th>수익률</th><th>평가금액</th><th>매수금액</th></tr>"
c_tot2 = "red" if t_acc_g > 0 else "blue"
html2 += f"<tr class='sum-row'><td>[ 합계 ]</td><td>{format_comma(t_asset)}</td><td class='{c_tot2}'>{t_acc_yield:+.2f}%</td><td class='{c_tot2}'>{format_comma(t_acc_g, True)}</td><td>{format_comma(t_acc_p)}</td></tr>"
for key in ['DC', 'PENSION', 'ISA', 'IRP']:
    if key in data:
        acc = data[key]; acc_g = sum(i['평가손익'] for i in acc['상세'] if i['종목명'] != '[ 합계 ]'); acc_p = acc.get('총자산', 0) - acc_g; c = "red" if acc_g > 0 else "blue"
        html2 += f"<tr><td>{acc.get('label')}</td><td>{format_comma(acc.get('총자산', 0))}</td><td class='{c}'>{(acc_g/acc_p*100 if acc_p>0 else 0):+.2f}%</td><td class='{c}'>{format_comma(acc_g, True)}</td><td>{format_comma(acc_p)}</td></tr>"
st.markdown(html2 + "</table>", unsafe_allow_html=True)

# --- [3] 계좌별 상세 내역 ---
st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
for key in ['DC', 'PENSION', 'ISA', 'IRP']:
    if key in data:
        acc = data[key]
        with st.expander(f"📂 [ {acc.get('label')} ] 종목별 현황"):
            c_sum = "red" if acc.get('총손익', 0) > 0 else "blue"
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**총자산 : {format_comma(acc.get('총자산', 0))} (원) / 총수익 : <span class='{c_sum}'>{format_comma(acc.get('총손익', 0), True)} ({acc.get('수익률(%)', 0):+.2f}%)</span>**", unsafe_allow_html=True)
            html3 = "<table class='main-table'><tr><th>종목명</th><th>비중</th><th>총자산(원)</th><th>평가손익(원)</th><th>수익률</th><th>주식수</th><th>평단가</th><th>금일종가</th></tr>"
            for i in acc.get('상세', []):
                if i['종목명'] == "[ 합계 ]": continue
                c = "red" if i['평가손익'] > 0 else "blue" if i['평가손익'] < 0 else ""
                html3 += f"<tr><td>{i['종목명']}</td><td>{i.get('비중', 0):.1f}%</td><td>{format_comma(i['평가금액'])}</td><td class='{c}'>{format_comma(i['평가손익'], True)}</td><td class='{c}'>{i['수익률(%)']:+.2f}%</td><td>{format_comma(i['수량'])}</td><td>{format_comma(i['평단가'])}</td><td>{format_comma(i['가격'])}</td></tr>"
            st.markdown(html3 + "</table>", unsafe_allow_html=True)
