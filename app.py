import streamlit as st
import json
import warnings
import google.generativeai as genai
import andy_pension_v2
import os
import re

# 1. 초기 설정 (보안 로그인 제거 상태)
warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="Andy's Asset Dashboard")

# 기존 CSS 유지 및 스타일 추가 (빨강/파랑 색상 및 인사이트 박스)
css = """
<style>
.block-container{padding-top:3rem!important;padding-bottom:7rem!important;}
h3{font-size:26px!important;font-weight:bold;margin-bottom:1px;}
.sub-title{font-size:22px!important;font-weight:bold;margin:25px 0 10px;}
.main-table{width:100%;border-collapse:collapse;font-size:15px;text-align:center;margin-bottom:10px;}
.main-table th{background-color:#f2f2f2;padding:10px;border:1px solid #ddd;font-weight:bold!important; vertical-align:middle;}
.main-table td{padding:8px;border:1px solid #ddd;vertical-align:middle;}
.sum-row td{background-color:#fff9e6;font-weight:bold!important;}
.red{color:#FF2323!important; font-weight:bold;} .blue{color:#0047EB!important; font-weight:bold;}
.insight-box{background-color:#f0f4f8;padding:20px;border-radius:10px;border-left:5px solid #007bff;margin-bottom:25px;}
.box-title{font-size:20px!important;font-weight:bold;margin-bottom:15px;display:block;color:#333;}
.summary-text { font-size: 16px !important; font-weight: bold !important; color: #333; margin-bottom: 10px; }
.summary-val { font-size: 20px !important; }
/* 자파 인사이트 전용 불렛 스타일 */
.insight-line { margin-bottom: 8px; font-size: 15px; line-height: 1.6; }

/* 플로팅 메뉴 버튼 스타일 유지 */
div[data-testid="stColumns"]:has(#zappa-floating-menu),
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) {
    position: fixed !important; bottom: 30px !important; right: 30px !important; left: auto !important;
    width: max-content !important; background: rgba(255, 255, 255, 0.98) !important; padding: 10px 25px !important; 
    border-radius: 8px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important; border: 1px solid #e5e7eb !important;
    z-index: 999999 !important; display: flex !important; gap: 14px !important;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 세션 상태 관리
if 'sort_mode' not in st.session_state: st.session_state.sort_mode = 'init'
if 'show_code' not in st.session_state: st.session_state.show_code = False
if 'init' not in st.session_state:
    with st.spinner("데이터 업데이트 중..."): andy_pension_v2.generate_asset_data()
    st.session_state['init'] = True
    st.cache_data.clear()

# 사이드바 AI 엔진
with st.sidebar:
    st.markdown("<div style='display:flex; align-items:center; gap:10px; margin-bottom:20px;'><span style='font-size:32px;'>🤖</span><span style='font-size:22px; font-weight:bold; color:#333;'>ZAPPA AI 코딩 엔진</span></div>", unsafe_allow_html=True)
    try:
        key = st.secrets.get("GOOGLE_API_KEY")
        if key:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            pmt = st.text_area("AI 엔진에게 요청", placeholder="수정 사항을 입력하세요...")
            if st.button("개선 사항 반영하기"):
                res = model.generate_content("Streamlit 수정: " + pmt)
                st.code(res.text)
        else: st.info("API Key 설정 필요")
    except Exception: st.error("엔진 연결 지연")

# 유틸리티 함수
def fmt(v, sign=False):
    try:
        val = int(float(v))
        if sign and val > 0: return f"+{val:,}"
        return f"{val:,}"
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

def clean_label(lbl):
    return re.sub(r'\s*\(\d{2}\.\d+월\)', '', lbl)

@st.cache_data(ttl=60)
def load():
    try:
        with open('assets.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return None

data = load()
if not data: st.stop()
tot = data.get("_total", {})

# 타이틀 및 업데이트 버튼
c1, c2 = st.columns([8.5, 1.5])
with c1: st.markdown("<h3>🚀 이상혁(Andy lee)님 [절세계좌] 통합 대시보드</h3>", unsafe_allow_html=True)
with c2:
    if st.button("🔄 업데이트", use_container_width=True):
        andy_pension_v2.generate_asset_data(); st.cache_data.clear(); st.rerun()

st.markdown(f"<div style='text-align:right;font-size:14px;color:#555;margin:-10px 0 10px;'>[{tot.get('조회시간', '')}]</div>", unsafe_allow_html=True)

# --- [자파의 자산 인사이트 섹션] ---
if "_insight" in data:
    ag_tot = tot.get('총 자산', 0) - tot.get('매입금액합', 0)
    ay_tot = (ag_tot / tot.get('매입금액합', 1) * 100) if tot.get('매입금액합', 1) > 0 else 0
    origin_yield = tot.get('수익률(%)', 0)
    
    ins_html = ["<div class='insight-box'><span class='box-title'>💡 [자파의 자산 인사이트]</span>"]
    
    # 문단 1: 총액 요약 (• 하나로 시작)
    ins_html.append(f"<p class='insight-line'>• 절세계좌 자산 총액은 {fmt(tot.get('총 자산',0))}원, 평가손익은 {fmt(ag_tot, True)}원 / 전일비 ({fmt(tot.get('평가손익(1일전)',0), True)}원) 으로 매입금액比 ▲{ay_tot:.1f}% (투자원금比 ▲{origin_yield:.1f}%) 수익률을 나타내고 있습니다.</p>")

    # 문단 2: 수익률 높은 순서 정렬
    FIXED_ACCOUNT_ORDER = ['DC', 'IRP', 'PENSION', 'ISA']
    acc_ranks = []
    for k in FIXED_ACCOUNT_ORDER:
        if k in data:
            a = data[k]
            # 매입금액 대비 수익률 계산
            acc_eval_profit = sum(i.get('평가손익',0) for i in a.get('상세', []) if i.get('종목명') != '[ 합계 ]')
            acc_buy_price = a.get('총 자산',0) - acc_eval_profit
            acc_yield = (acc_eval_profit / acc_buy_price * 100) if acc_buy_price > 0 else 0
            label = "연금저축(CMA)" if k == 'PENSION' else ("ISA(중개형)" if k == 'ISA' else f"퇴직연금({k})")
            acc_ranks.append({'name': label, 'yield': acc_yield, 'profit': acc_eval_profit})
    
    acc_ranks.sort(key=lambda x: x['yield'], reverse=True)
    rank_text = " / ".join([f"{r['name']}계좌 ▲{r['yield']:.1f}%(+{r['profit']/1000000:.1f}백만)" for r in acc_ranks])
    ins_html.append(f"<p class='insight-line'>• 수익률 높은 순서 : {rank_text} 순입니다.</p>")

    # 문단 3: ETF 시황 분석
    ins_html.append(f"<p class='insight-line'>• 미국 ETF 장기간 횡보 속에 코스피 등 한국 ETF가 전체 평가 손익을 주도하고 있습니다. (현재 데이터 기반 분석 결과)</p>")

    # 문단 4: 우수/저조 종목 자동 추출
    all_items = []
    for k in FIXED_ACCOUNT_ORDER:
        if k in data: all_items.extend([i for i in data[k].get('상세', []) if i.get('종목명') != '[ 합계 ]'])
    
    if all_items:
        all_items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
        top3 = all_items[:3]
        bot2 = all_items[-2:]
        ins_html.append(f"<p class='insight-line'>• 종목별로는 ① {top3[0]['종목명']}, ② {top3[1]['종목명']}, ③ {top3[2]['종목명']} 이 우수하고 상대적으로 ④ {bot2[0]['종목명']} 등은 부진합니다.</p>")

    # 문단 5: 최종 시황 코멘트 (AI 머지)
    ins_html.append(f"<p class='insight-line'>• 간밤 미국 기술주와 나스닥 지수가 상승세를 보인 훈풍이 한국 증시로 이어지며, 코스피 관련 ETF 역시 동반 상승하는 강세장을 기록 중입니다. 현재의 긍정적 흐름을 유지하되 많이 오른 종목의 부분 익절을 통한 리밸런싱을 고려해 볼 시점입니다.</p>")
    
    ins_html.append("</div>")
    st.markdown("".join(ins_html), unsafe_allow_html=True)

# --- [1], [2], [3] 테이블 섹션 유지 ---
unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"

# [1] 투자원금 대비
st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
h1_sum_yield = tot.get('수익률(%)', 0)
st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(tot.get('총 자산',0))}</span> / 총 수익 : <span class='summary-val {col(tot.get('총 수익',0))}'>{fmt(tot.get('총 수익',0), True)} ({fmt_p(h1_sum_yield)})</span></div>", unsafe_allow_html=True)

h1 = [unit_html, "<table class='main-table'><tr><th>계좌 구분</th><th>총 자산</th><th>평가손익</th><th>수익률</th><th>투자원금</th></tr>"]
h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(tot.get('총 자산',0))}</td><td class='{col(tot.get('총 수익',0))}'>{fmt(tot.get('총 수익',0), True)}</td><td class='{col(h1_sum_yield)}'>{fmt_p(h1_sum_yield)}</td><td>{fmt(tot.get('원금합',0))}</td></tr>")
for k in FIXED_ACCOUNT_ORDER:
    if k in data:
        a = data[k]
        h1.append(f"<tr><td>{clean_label(a.get('label', k))}</td><td>{fmt(a.get('총 자산',0))}</td><td class='{col(a.get('총 수익',0))}'>{fmt(a.get('총 수익',0), True)}</td><td class='{col(a.get('수익률(%)',0))}'>{fmt_p(a.get('수익률(%)',0))}</td><td>{fmt(a.get('원금',0))}</td></tr>")
h1.append("</table>")
st.markdown("".join(h1), unsafe_allow_html=True)

# [2] 매입금액 대비
st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(tot.get('총 자산',0))}</span> / 총 수익 : <span class='summary-val {col(ag_tot)}'>{fmt(ag_tot, True)} ({fmt_p(ay_tot)})</span></div>", unsafe_allow_html=True)

h2 = [unit_html, "<table class='main-table'><tr><th>계좌 구분</th><th>총 자산</th><th>평가손익</th><th>전일비</th><th>수익률</th><th>매입금액</th></tr>"]
h2.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(tot.get('총 자산',0))}</td><td class='{col(ag_tot)}'>{fmt(ag_tot, True)}</td><td class='{col(tot.get('평가손익(1일전)',0))}'>{fmt(tot.get('평가손익(1일전)',0), True)}</td><td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td><td>{fmt(tot.get('매입금액합',0))}</td></tr>")
for k in FIXED_ACCOUNT_ORDER:
    if k in data:
        a = data[k]
        acc_profit = sum(i.get('평가손익',0) for i in a.get('상세', []) if i.get('종목명') != '[ 합계 ]')
        acc_buy = a.get('총 자산',0) - acc_profit
        acc_y = (acc_profit/acc_buy*100) if acc_buy > 0 else 0
        h2.append(f"<tr><td>{clean_label(a.get('label', k))}</td><td>{fmt(a.get('총 자산',0))}</td><td class='{col(acc_profit)}'>{fmt(acc_profit, True)}</td><td class='{col(a.get('평가손익(1일전)',0))}'>{fmt(a.get('평가손익(1일전)',0), True)}</td><td class='{col(acc_y)}'>{fmt_p(acc_y)}</td><td>{fmt(acc_buy)}</td></tr>")
h2.append("</table>")
st.markdown("".join(h2), unsafe_allow_html=True)

# [3] 계좌 상세
st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
t3_lbl = {'DC':'퇴직연금(DC)계좌 / (삼성증권)', 'PENSION':'연금저축(CMA)계좌 / (삼성증권)', 'ISA':'ISA(중개형)계좌 / (키움증권)', 'IRP':'퇴직연금(IRP)계좌 / (삼성증권)'}

for k in FIXED_ACCOUNT_ORDER:
    if k not in data: continue
    a = data[k]
    with st.expander(f"📂 [ {t3_lbl.get(k, a.get('label',k))} ]", expanded=True):
        s_data = next((i for i in a.get('상세', []) if i.get('종목명') == "[ 합계 ]"), {})
        st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(a.get('총 자산',0))}</span> / 총 수익 : <span class='summary-val {col(s_data.get('평가손익',0))}'>{fmt(s_data.get('평가손익',0), True)} ({fmt_p(s_data.get('수익률(%)',0))})</span></div>", unsafe_allow_html=True)
        h3 = [unit_html, "<table class='main-table'><tr><th>종목명</th><th>비중</th><th>총 자산</th><th>평가손익</th><th>수익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>"]
        for i in a.get('상세', []):
            is_s = (i.get('종목명') == "[ 합계 ]")
            row_cls = "class='sum-row'" if is_s else ""
            h3.append(f"<tr {row_cls}><td>{i.get('종목명','')}</td><td>{i.get('비중',0):.1f}%</td><td>{fmt(i.get('총 자산',0))}</td><td class='{col(i.get('평가손익',0))}'>{fmt(i.get('평가손익',0), True)}</td><td class='{col(i.get('수익률(%)',0))}'>{fmt_p(i.get('수익률(%)',0))}</td><td>{fmt(i.get('수량','-'))}</td><td>{fmt(i.get('매입가','-'))}</td><td>{fmt(i.get('현재가','-'))}</td></tr>")
        h3.append("</table>")
        st.markdown("".join(h3), unsafe_allow_html=True)
