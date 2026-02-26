import streamlit as st
import json
import warnings
import google.generativeai as genai
import andy_pension_v2
import os
import re

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="Andy's Asset Dashboard")

css = """
<style>
.block-container{padding-top:3rem!important;padding-bottom:7rem!important;}
h3{font-size:26px!important;font-weight:bold;margin-bottom:1px;}
.sub-title{font-size:22px!important;font-weight:bold;margin:25px 0 10px;}
.main-table{width:100%;border-collapse:collapse;font-size:15px;text-align:center;margin-bottom:10px;}
.main-table th{background-color:#f2f2f2;padding:10px;border:1px solid #ddd;font-weight:bold!important; vertical-align:middle;}
.main-table td{padding:8px;border:1px solid #ddd;vertical-align:middle;}
.sum-row td{background-color:#fff9e6;font-weight:bold!important;}
.red{color:#FF2323!important;} .blue{color:#0047EB!important;}
.insight-box{background-color:#f0f4f8;padding:20px;border-radius:10px;border-left:5px solid #007bff;margin-bottom:25px;}
.box-title{font-size:20px!important;font-weight:bold;margin-bottom:15px;display:block;color:#333;}

.summary-text { font-size: 16px !important; font-weight: bold !important; color: #333; margin-bottom: 10px; }
.summary-val { font-size: 20px !important; }

/* 평가손익 & 기간비용 병합 스타일 */
.main-table th.th-eval { border-right: none !important; }
.main-table th.th-blank { border-left: none !important; border-bottom: none !important; padding: 0 !important; }
.main-table th.th-week { border-left: 1px solid #ddd !important; border-top: 1px solid #ddd !important; font-size: 13.5px; }

.zappa-icon { font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif !important; font-size: 32px !important; }

/* =========================================================
   [ZAPPA 플로팅 배너 CSS] image_7c8084.png 스타일 완벽 복원 🔥
   ========================================================= */
div[data-testid="stColumns"]:has(#zappa-floating-menu),
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) {
    position: fixed !important;
    bottom: 30px !important;
    right: 50% !important;
    left: auto !important;
    transform: translateX(50%) !important; 
    width: max-content !important; 
    background: #FFFFFF !important; 
    padding: 6px 35px !important; 
    border-radius: 50px !important; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.12) !important;
    border: 1px solid #E5E7EB !important;
    z-index: 999999 !important;
    display: flex !important;
    flex-wrap: nowrap !important; 
    align-items: center !important; 
    justify-content: center !important; 
    gap: 15px !important;
}

div.element-container:has(#zappa-floating-menu) { display: none !important; }

div[data-testid="stColumns"]:has(#zappa-floating-menu) div[data-testid="stButton"] button { 
    background: transparent !important; 
    border: none !important; 
    box-shadow: none !important;
    color: #4B5563 !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    padding: 0 5px !important;
    height: auto !important;
}

div[data-testid="stColumns"]:has(#zappa-floating-menu) button:hover {
    color: #111111 !important;
    background: transparent !important;
}

div[data-testid="stColumns"]:has(#zappa-floating-menu) button[kind="primary"] {
    color: #111111 !important;
    font-weight: 700 !important;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

if 'sort_mode' not in st.session_state: st.session_state.sort_mode = 'init'
if 'show_code' not in st.session_state: st.session_state.show_code = False
if 'init' not in st.session_state:
    with st.spinner("데이터 업데이트 중..."): andy_pension_v2.generate_asset_data()
    st.session_state['init'] = True
    st.cache_data.clear()

# --- 사이드바 ZAPPA 엔진 ---
with st.sidebar:
    st.markdown("""<div style='display:flex; align-items:center; gap:10px; margin-bottom:20px;'><span class='zappa-icon'>🤖</span><span style='font-size:22px; font-weight:bold; color:#333;'>ZAPPA AI 코딩 엔진</span></div>""", unsafe_allow_html=True)
    try:
        key = st.secrets.get("GOOGLE_API_KEY")
        if key:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            pmt = st.text_area("AI 엔진에게 요청", placeholder="수정 사항을 입력하세요...")
            if st.button("개선 사항 반영하기"):
                res = model.generate_content("Streamlit 수정: " + pmt)
                st.code(res.text)
    except Exception: st.error("엔진 연결 지연")

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

# 계좌 고정 순서
FIXED_ACCOUNT_ORDER = ['DC', 'IRP', 'PENSION', 'ISA']

c1, c2 = st.columns([8.5, 1.5])
# 1. 텍스트 수정: 타이틀에 [절세계좌] 추가
with c1: st.markdown("<h3>🚀 이상혁(Andy lee)님 [절세계좌] 통합 대시보드</h3>", unsafe_allow_html=True)
with c2:
    if st.button("🔄 업데이트", use_container_width=True):
        andy_pension_v2.generate_asset_data()
        st.cache_data.clear()
        if 'zappa_insight_text' in st.session_state:
            del st.session_state['zappa_insight_text'] # 업데이트 시 AI 인사이트도 초기화
        st.rerun()

st.markdown(f"<div style='text-align:right;font-size:14px;color:#555;margin:-10px 0 10px;'>[{tot.get('조회시간')}]</div>", unsafe_allow_html=True)

# =========================================================================
# 💡 [절세계좌] 자산 현황 요약 (Gemini 실시간 연동 5개 꼭지)
# =========================================================================
if 'zappa_insight_text' not in st.session_state:
    # 1. AI에게 정확한 수치를 전달하기 위한 파이썬 정밀 사전 계산 (백만원, 투자원금 기준)
    ta = tot.get('총 자산', 0)
    to = tot.get('원금합', 1)
    tb = tot.get('매입금액합', 1)
    ag_tot = ta - tb
    td1_tot = tot.get('평가손익(1일전)', 0)
    ay_tot = (ag_tot / tb) * 100
    py_tot = ((ta - to) / to) * 100

    acc_list = []
    for k in FIXED_ACCOUNT_ORDER:
        if k in data:
            a = data[k]
            prn = a.get('원금', 1)
            asset = a.get('총 자산', 0)
            profit = asset - prn
            rate = (profit / prn) * 100
            acc_list.append({"name": clean_label(a['label']), "rate": rate, "profit": profit})
    # 투자원금 대비 수익률 내림차순 정렬
    acc_list.sort(key=lambda x: x['rate'], reverse=True)
    acc_str = " / ".join([f"{x['name']} {'▲' if x['rate']>0 else '▼' if x['rate']<0 else ''}{abs(x['rate']):.1f}%({'+' if x['profit']>0 else ''}{x['profit']/1000000:.2f}백만)" for x in acc_list])

    # 주도 종목 상세 데이터 추출
    target_etfs = ["KODEX 200", "KODEX 200타켓위클리커버드콜", "PLUS 고배당주", "RISE 200위클리커버드콜"]
    etf_str_list = []
    for etf in target_etfs:
        found = []
        for k in FIXED_ACCOUNT_ORDER:
            if k in data:
                for item in data[k].get('상세', []):
                    if item.get('종목명') == etf:
                        profit = item.get('평가손익', 0)
                        rate = item.get('수익률(%)', 0)
                        found.append(f"{clean_label(data[k]['label'])} {'▲' if rate>0 else '▼' if rate<0 else ''}{abs(rate):.1f}%({'+' if profit>0 else ''}{profit/1000000:.2f}백만)")
        if found: etf_str_list.append(f"①" if etf=="KODEX 200" else f"②" if "타켓" in etf else f"③" if "고배당" in etf else f"④" + f" {etf} : " + ", ".join(found))
    etf_details_str = " ".join(etf_str_list)

    # 미국 및 한국 ETF 동향 파악용 데이터
    us_etfs, kr_etfs = [], []
    for k in FIXED_ACCOUNT_ORDER:
        if k in data:
            for item in data[k].get('상세', []):
                name = item.get('종목명', '')
                if name in ['[ 합계 ]', '현금성자산', '삼성화재 퇴직연금(3.05%/年)']: continue
                rate = item.get('수익률(%)', 0)
                info = f"{name} {'▲' if rate>0 else '▼' if rate<0 else ''}{abs(rate):.1f}%"
                if any(x in name for x in ['미국', '나스닥', 'S&P', '테크', '다우존스']): us_etfs.append(info)
                else: kr_etfs.append(info)

    # 2. Gemini 프롬프트 구성
    zappa_prompt = f"""당신은 Andy님의 자산관리 AI 'ZAPPA'입니다. 
    제공된 사전 계산 데이터를 바탕으로 다음 5개 꼭지의 '[절세계좌] 자산 현황 요약'을 작성하세요.
    수치 오류를 막기 위해 [데이터]의 수치를 그대로 문장에 결합하세요.

    [사전 계산 데이터]
    - 총자산: {fmt(ta)}원 / 매입평가손익: {fmt(ag_tot, True)}원 / 전일비: {fmt(td1_tot, True)}원
    - 매입비수익률: {'▲' if ay_tot>0 else '▼'}{abs(ay_tot):.1f}% / 원금비수익률: {'▲' if py_tot>0 else '▼'}{abs(py_tot):.1f}%
    - 정렬된 계좌수익: {acc_str}
    - 핵심종목상세: {etf_details_str}
    - 미국ETF목록: {", ".join(us_etfs)}

    [출력 양식 규칙] (마크다운 없이 순수 HTML <p>태그만 사용할 것)
    <p style='margin-bottom:10px; line-height: 1.6;'><b>• 현재 절세계좌 자산 총액은 [총자산]원, 평가손익은 [매입평가손익]원 (전일비 [전일비]원)으로 매입금액比 [매입비수익률] (투자원금比 [원금비수익률]) 수익률을 나타내고 있습니다.</b></p>
    <p style='margin-bottom:10px; line-height: 1.6;'><b>• 수익률은 [정렬된 계좌수익 텍스트 그대로 기재] 순으로 나타나고 있습니다.</b></p>
    <p style='margin-bottom:10px; line-height: 1.6;'><b>• 종목별로 보면, 미국 ETF 장기간 횡보 속에([미국ETF목록 중 주요 3~4개만 요약]), 코스피 한국 ETF가 전체 평가 손익을 주도하고 있음.</b></p>
    <p style='margin-bottom:10px; line-height: 1.6;'><b>• 종목별로는 [핵심종목상세 텍스트 그대로 기재]</b></p>
    <p style='margin-bottom:5px; line-height: 1.6;'><b>• (최근 밤 미국 나스닥, S&P500 등 매크로 증시 기사를 요약하고 한국 증시에 미치는 영향과 현금화/리밸런싱 조언을 전문적으로 2~3줄 작성)</b></p>
    """

    try:
        api_key = st.secrets.get("GOOGLE_API_KEY")
    except:
        api_key = None

    if api_key:
        with st.spinner("ZAPPA AI가 실시간 매크로 시황 및 5개 꼭지를 분석 중입니다..."):
            try:
                genai.configure(api_key=api_key)
                z_model = genai.GenerativeModel('gemini-1.5-flash')
                response = z_model.generate_content(zappa_prompt)
                st.session_state.zappa_insight_text = response.text
            except Exception as e:
                st.session_state.zappa_insight_text = "<p>AI 시황 분석을 불러오는 중 오류가 발생했습니다.</p>"
    else:
        st.session_state.zappa_insight_text = "<p>좌측 ZAPPA 엔진에 API Key를 설정해야 5개 꼭지 실시간 요약이 생성됩니다.</p>"

# 화면에 AI 인사이트 렌더링 (밑줄 <u> 태그 제거)
st.markdown(f"""
<div class='insight-box'>
    <span class='box-title'>💡 '[절세계좌] 자산 현황 요약'</span>
    <div style='font-size: 15.5px; color: #2C3E50;'>
        {st.session_state.zappa_insight_text}
    </div>
</div>
""", unsafe_allow_html=True)

unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"

# --- [1] 투자금 대비 자산 현황 ---
st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"""
<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'>
    <div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(tot.get('총 자산',0))}</span> / 총 수익 : <span class='summary-val {col(tot.get('총 수익',0))}'>{fmt(tot.get('총 수익',0), True)} ({fmt_p(tot.get('수익률(%)',0))})</span></div>
    <div style='font-size:14.5px; font-weight:normal; color:#555;'>[ 25.8월 : 퇴직연금(DC/IRP), ISA(중개형), 25.11월 : 연금저축(CMA) ]</div>
</div>
""", unsafe_allow_html=True)

h1 = [unit_html, "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>수익률</th><th rowspan='2'>투자원금</th></tr><tr><th class='th-week'>7일전</th><th class='th-week'>15일전</th><th class='th-week'>30일전</th></tr>"]
ta, to = tot.get('총 자산',0), tot.get('원금합',0)
h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(ta)}</td><td class='{col(tot.get('총 수익'))}'>{fmt(tot.get('총 수익'), True)}</td><td>{fmt((ta-tot.get('평가손익(7일전)',0))-to, True)}</td><td>{fmt((ta-tot.get('평가손익(15일전)',0))-to, True)}</td><td>{fmt((ta-tot.get('평가손익(30일전)',0))-to, True)}</td><td class='{col(tot.get('수익률(%)'))}'>{fmt_p(tot.get('수익률(%)'))}</td><td>{fmt(to)}</td></tr>")

keys_sorted = [k for k in FIXED_ACCOUNT_ORDER if k in data]
if st.session_state.sort_mode == 'asset': keys_sorted.sort(key=lambda k: data[k].get('총 자산', 0), reverse=True)
elif st.session_state.sort_mode == 'profit': keys_sorted.sort(key=lambda k: data[k].get('총 수익', 0), reverse=True)
elif st.session_state.sort_mode == 'rate': keys_sorted.sort(key=lambda k: data[k].get('수익률(%)', 0), reverse=True)

for k in keys_sorted:
    a = data[k]
    cur, prn = a['총 자산'], a['원금']
    h1.append(f"<tr><td>{clean_label(a['label'])}</td><td>{fmt(cur)}</td><td class='{col(a['총 수익'])}'>{fmt(a['총 수익'],True)}</td><td class='{col((cur-a.get('평가손익(7일전)',0))-prn)}'>{fmt((cur-a.get('평가손익(7일전)',0))-prn, True)}</td><td class='{col((cur-a.get('평가손익(15일전)',0))-prn)}'>{fmt((cur-a.get('평가손익(15일전)',0))-prn, True)}</td><td class='{col((cur-a.get('평가손익(30일전)',0))-prn)}'>{fmt((cur-a.get('평가손익(30일전)',0))-prn, True)}</td><td class='{col(a['수익률(%)'])}'>{fmt_p(a['수익률(%)'])}</td><td>{fmt(prn)}</td></tr>")
h1.append("</table>")
st.markdown("".join(h1), unsafe_allow_html=True)

# --- [2] 매입금액 대비 자산 현황 ---
st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(tot.get('총 자산'))}</span> / 총 수익 : <span class='summary-val {col(ta-tot.get('매입금액합'))}'>{fmt(ta-tot.get('매입금액합'), True)} ({fmt_p((ta-tot.get('매입금액합'))/tot.get('매입금액합',1)*100)})</span></div>", unsafe_allow_html=True)

h2 = [unit_html, "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>수익률</th><th rowspan='2'>매입금액</th></tr><tr><th class='th-week'>전일비</th><th class='th-week'>전주비</th><th class='th-week'>전월비</th></tr>"]
h2.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(ta)}</td><td class='{col(ta-tot.get('매입금액합'))}'>{fmt(ta-tot.get('매입금액합'), True)}</td><td>{fmt(tot.get('평가손익(1일전)',0), True)}</td><td>{fmt(tot.get('평가손익(7일전)',0), True)}</td><td>{fmt(tot.get('평가손익(30일전)',0), True)}</td><td class='{col((ta-tot.get('매입금액합'))/tot.get('매입금액합',1)*100)}'>{fmt_p((ta-tot.get('매입금액합'))/tot.get('매입금액합',1)*100)}</td><td>{fmt(tot.get('매입금액합'))}</td></tr>")

for k in keys_sorted:
    a = data[k]
    ag_acc = sum(i.get('평가손익',0) for i in a.get('상세', []) if i.get('종목명') != '[ 합계 ]')
    ap_acc = a.get('총 자산',0) - ag_acc
    h2.append(f"<tr><td>{clean_label(a['label'])}</td><td>{fmt(a['총 자산'])}</td><td class='{col(ag_acc)}'>{fmt(ag_acc, True)}</td><td>{fmt(a.get('평가손익(1일전)',0), True)}</td><td>{fmt(a.get('평가손익(7일전)',0), True)}</td><td>{fmt(a.get('평가손익(30일전)',0), True)}</td><td class='{col(ag_acc/ap_acc*100 if ap_acc>0 else 0)}'>{fmt_p(ag_acc/ap_acc*100 if ap_acc>0 else 0)}</td><td>{fmt(ap_acc)}</td></tr>")
h2.append("</table>")
st.markdown("".join(h2), unsafe_allow_html=True)

# --- [3] 계좌별 상세 내역 (ZAPPA 플로팅 메뉴) ---
st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
b1, b2, b3, b4, b5 = st.columns(5)
with b1:
    st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
    is_init = (st.session_state.sort_mode == 'init')
    if st.button("🛠️ 초기화 [ " + ("●" if is_init else "○") + " ]", type="primary" if is_init else "secondary"): st.session_state.sort_mode = 'init'; st.rerun()
with b2:
    is_asset = (st.session_state.sort_mode == 'asset')
    if st.button("💰 총 자산 [ " + ("●" if is_asset else "○") + " ]", type="primary" if is_asset else "secondary"): st.session_state.sort_mode = 'asset'; st.rerun()
with b3:
    is_profit = (st.session_state.sort_mode == 'profit')
    if st.button("📊 평가손익 [ " + ("●" if is_profit else "○") + " ]", type="primary" if is_profit else "secondary"): st.session_state.sort_mode = 'profit'; st.rerun()
with b4:
    is_rate = (st.session_state.sort_mode == 'rate')
    if st.button("📈 수익률 [ " + ("●" if is_rate else "○") + " ]", type="primary" if is_rate else "secondary"): st.session_state.sort_mode = 'rate'; st.rerun()
with b5:
    is_code = st.session_state.show_code
    if st.button("💻 종목코드 [ " + ("+" if is_code else "-") + " ]", type="primary" if is_code else "secondary"): st.session_state.show_code = not st.session_state.show_code; st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
t3_lbl = {'DC':'퇴직연금(DC)계좌 / (삼성증권 7165962472-28)', 'PENSION':'연금저축(CMA)계좌 / (삼성증권 7169434836-15)', 'ISA':'ISA(중개형)계좌 / (키움증권 6448-4934)', 'IRP':'퇴직연금(IRP)계좌 / (삼성증권 7164499007-29)'}

for k in FIXED_ACCOUNT_ORDER:
    if k not in data: continue
    a = data[k]
    with st.expander(f"📂 [ {t3_lbl.get(k, a['label'])} ] 종목별 현황", expanded=False):
        s_data = next(i for i in a['상세'] if i['종목명'] == "[ 합계 ]")
        safe_pct = sum(item.get('비중', 0) for item in a.get('상세', []) if (k=='DC' and item.get('종목명') in ['삼성화재 퇴직연금(3.05%/年)', '현금성자산']) or (k=='IRP' and item.get('종목명')=='현금성자산'))
        st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(a['총 자산'])}</span> / 총 수익 : <span class='summary-val {col(s_data.get('평가손익'))}'>{fmt(s_data.get('평가손익'), True)} ({fmt_p(s_data.get('수익률(%)'))})</span></div><div style='font-size:14.5px; color:#555;'>[ 위험자산 : {100.0-safe_pct:.1f}% | 안전자산 : {safe_pct:.1f}% ]</div></div>", unsafe_allow_html=True)
        h3 = [unit_html, "<table class='main-table'><tr><th>종목명</th>"]
        if st.session_state.show_code: h3.append("<th>종목코드</th>")
        h3.append("<th>비중</th><th>총 자산</th><th>평가손익</th><th>수익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>")
        
        items = [i for i in a.get('상세', []) if i.get('종목명') != "[ 합계 ]"]
        if st.session_state.sort_mode == 'asset': items.sort(key=lambda x: x.get('총 자산', 0), reverse=True)
        elif st.session_state.sort_mode == 'profit': items.sort(key=lambda x: x.get('평가손익', 0), reverse=True)
        elif st.session_state.sort_mode == 'rate': items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
        
        for i in ([s_data] + items):
            is_s = (i.get('종목명') == "[ 합계 ]")
            row = f"<tr class='sum-row'>" if is_s else "<tr>"
            row += f"<td>{i.get('종목명')}</td>"
            if st.session_state.show_code: row += f"<td>{'-' if is_s or i.get('코드','-')=='-' else i.get('코드')}</td>"
            row += f"<td>{i.get('비중',0):.1f}%</td><td>{fmt(i.get('총 자산',0))}</td><td class='{col(i.get('평가손익',0))}'>{fmt(i.get('평가손익',0), True)}</td><td class='{col(i.get('수익률(%)',0))}'>{fmt_p(i.get('수익률(%)',0))}</td><td>{fmt(i.get('수량','-'))}</td><td>{fmt(i.get('매입가','-'))}</td><td>{fmt(i.get('현재가','-'))}</td></tr>"
            h3.append(row)
        h3.append("</table>")
        st.markdown("".join(h3), unsafe_allow_html=True)
