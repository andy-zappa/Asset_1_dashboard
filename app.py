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
h3{font-size:26px!important;font-weight:bold;margin-bottom:0px; padding-bottom:0px;}
.sub-title{font-size:22px!important;font-weight:bold;margin:25px 0 10px;}
.main-table{width:100%;border-collapse:collapse;font-size:15px;text-align:center;margin-bottom:10px;}
.main-table th{background-color:#f2f2f2;padding:10px;border:1px solid #ddd;font-weight:bold!important; vertical-align:middle;}
.main-table td{padding:8px;border:1px solid #ddd;vertical-align:middle;}
.sum-row td{background-color:#fff9e6;font-weight:bold!important;}
.red{color:#FF2323!important;} .blue{color:#0047EB!important;}

.insight-container { display: flex; gap: 20px; align-items: stretch; margin-bottom: 20px; }
.insight-left { flex: 0 0 46%; display: flex; flex-direction: column; }
.insight-right { flex: 1; display: flex; flex-direction: column; }

.card-main { background-color: #fffdf2; border: 2px solid #e8dbad; border-radius: 18px; padding: 18px 22px 15px 22px; position: relative; box-shadow: 0 2px 6px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; }
.grid-2x2 { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 15px; height: 100%; }

.card-sub { background: #fff; border: 1.5px solid #ddd; border-radius: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.02); display: flex; flex-direction: column; }

.insight-bottom-box { background: #fff; border: 1.5px solid #ddd; border-radius: 18px; padding: 25px; box-shadow: 0 1px 4px rgba(0,0,0,0.02); font-size: 15.5px; line-height: 1.8; color: #333; margin-top: 5px; margin-bottom: 25px; }
.insight-bottom-box p { margin-bottom: 12px; }

.summary-text { font-size: 16px !important; font-weight: bold !important; color: #333; margin-bottom: 10px; }
.summary-val { font-size: 20px !important; }

.main-table th.th-eval { border-right: none !important; }
.main-table th.th-blank { border-left: none !important; border-bottom: none !important; padding: 0 !important; }
.main-table th.th-week { border-left: 1px solid #ddd !important; border-top: 1px solid #ddd !important; font-size: 13.5px; }

.zappa-icon { font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif !important; font-size: 32px !important; }

div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu),
div[data-testid="column"]:has(span#zappa-floating-menu) {
    position: fixed !important; bottom: 30px !important; right: 30px !important; left: auto !important; transform: none !important;
    width: max-content !important; min-width: 0 !important; background: rgba(255, 255, 255, 0.98) !important; padding: 10px 25px !important; 
    border-radius: 8px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important; border: 1px solid #e5e7eb !important;
    z-index: 999999 !important; display: flex !important; flex-wrap: nowrap !important; align-items: center !important; justify-content: center !important; gap: 14px !important; 
}
div.element-container:has(span#zappa-floating-menu) { display: none !important; }
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) > div { min-width: 0 !important; width: auto !important; padding: 0 !important; margin: 0 !important; flex: 0 0 auto !important; border-right: none !important; }
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button { margin: 0 !important; padding: 0 5px !important; width: auto !important; background: transparent !important; border: none !important; border-radius: 0 !important; height: 26px !important; min-height: 26px !important; color: #9ca3af !important; font-size: 15px !important; font-weight: normal !important; white-space: nowrap !important; box-shadow: none !important; display: flex !important; align-items: center !important; justify-content: center !important; }
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button p { color: inherit !important; font-size: 14.5px !important; font-weight: inherit !important; margin: 0 !important; padding: 0 !important; line-height: 1 !important; text-align: center !important; white-space: nowrap !important; }
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button:hover { color: #111111 !important; background: transparent !important; }
div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button[kind="primary"] { background: transparent !important; border: none !important; color: #111111 !important; font-weight: bold !important; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

if 'sort_mode' not in st.session_state: st.session_state.sort_mode = 'init'
if 'show_code' not in st.session_state: st.session_state.show_code = False
if 'init' not in st.session_state:
    with st.spinner("데이터 업데이트 중..."): andy_pension_v2.generate_asset_data()
    st.session_state['init'] = True
    st.cache_data.clear()

with st.sidebar:
    st.markdown("<div style='display:flex; align-items:center; gap:10px; margin-bottom:20px;'><span class='zappa-icon'>🤖</span><span style='font-size:22px; font-weight:bold; color:#333;'>ZAPPA AI 코딩 엔진</span></div>", unsafe_allow_html=True)
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
    except: return {}

data = load()
if not data: st.stop()
tot = data.get("_total", {})

c1, c2 = st.columns([8.5, 1.5])
with c1: 
    st.markdown("<h3 style='margin-top: 5px;'>🚀 이상혁(Andy lee)님 [절세계좌] 통합 대시보드</h3>", unsafe_allow_html=True)
with c2:
    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 업데이트", use_container_width=True):
        andy_pension_v2.generate_asset_data(); st.cache_data.clear(); st.rerun()

st.markdown(f"<div style='text-align:right;font-size:14.5px;color:#555;font-weight:normal;margin:-10px 0 15px;'>[ {tot.get('조회시간', '업데이트 필요')} ]</div>", unsafe_allow_html=True)

FIXED_ACCOUNT_ORDER = ['DC', 'IRP', 'PENSION', 'ISA']
OPEN_DATES = {'DC': '[ 2025.08 ]', 'IRP': '[ 2025.08 ]', 'PENSION': '[ 2025.11 ]', 'ISA': '[ 2025.08 ]'}

if "_insight" in data:
    t_asset = tot.get('총 자산', tot.get('총자산', 0))
    t_profit = tot.get('총 수익', tot.get('총 손익', tot.get('평가손익', 0)))
    t_diff = tot.get('평가손익(1일전)', tot.get('1일전', 0))
    t_diff_7 = tot.get('평가손익(7일전)', 0)
    t_rate = tot.get('수익률(%)', tot.get('손익률(%)', 0))
    
    cash_total = 0
    ovs_total = 0
    dom_total = 0
    
    cash_kws = ['현금성자산', 'mmf']
    ovs_kws = ['tiger', 's&p', '나스닥', '필라델피아', '다우존스', 'ai테크']
    
    for k in FIXED_ACCOUNT_ORDER:
        if k in data:
            for item in data[k].get('상세', []):
                name = item.get('종목명', '')
                if name == '[ 합계 ]': continue
                val = item.get('총 자산', item.get('총자산', 0))
                name_lower = name.lower()
                if any(kw in name_lower for kw in cash_kws):
                    cash_total += val
                elif any(kw in name_lower for kw in ovs_kws):
                    ovs_total += val
                else:
                    dom_total += val

    dom_total = t_asset - cash_total - ovs_total
    p_cash = (cash_total / t_asset * 100) if t_asset > 0 else 0
    p_ovs = (ovs_total / t_asset * 100) if t_asset > 0 else 0
    p_dom = (dom_total / t_asset * 100) if t_asset > 0 else 0

    a_dc = data.get('DC', {}).get('총 자산', data.get('DC', {}).get('총자산', 0))
    a_irp = data.get('IRP', {}).get('총 자산', data.get('IRP', {}).get('총자산', 0))
    a_pension = data.get('PENSION', {}).get('총 자산', data.get('PENSION', {}).get('총자산', 0))
    a_isa = data.get('ISA', {}).get('총 자산', data.get('ISA', {}).get('총자산', 0))
    
    total_for_bar = a_dc + a_irp + a_pension + a_isa
    if total_for_bar == 0: total_for_bar = 1 

    p_dc = a_dc / total_for_bar * 100
    p_irp = a_irp / total_for_bar * 100
    p_pension = a_pension / total_for_bar * 100
    p_isa = a_isa / total_for_bar * 100

    goal_amount = 1000000000
    progress_pct = (t_asset / goal_amount) * 100 if goal_amount > 0 else 0

    def render_bar(p, color):
        if p < 5: return f"<div style='width: {p}%; background-color: {color}; height: 100%; margin-bottom: 4px;'></div>"
        return f"<div style='width: {p}%; background-color: {color}; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 13.5px; font-weight: normal; color: #333; margin-bottom: 4px;'>{p:.0f}%</div>"

    insight_texts = data.get("_insight", [])
    bottom_html = ""
    for text in insight_texts:
        if "조회 기준 시간" in text: continue
        bottom_html += f"<p>{text}</p>"

    st.markdown("<div class='sub-title' style='margin-bottom: 15px;'>💡 자파의 [절세계좌] 자산 현황 보고</div>", unsafe_allow_html=True)

    stop1 = p_cash
    stop2 = p_cash + p_ovs
    donut_css = f"background: conic-gradient(#ffffff 0% {stop1}%, #d9d9d9 {stop1}% {stop2}%, #8c8c8c {stop2}% 100%);"
    
    donut_html = f"""
    <div style='position: relative; width: 130px; height: 130px; border-radius: 50%; {donut_css} box-shadow: inset 0 0 8px rgba(0,0,0,0.1); border: 1px solid #d0d0d0; margin-left: 5px; flex-shrink: 0;'>
        <div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 35%; height: 35%; background-color: #fffdf2; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.05);'></div>
        <div style='position: absolute; top: 6%; left: 50%; transform: translateX(-50%); font-size: 12.5px; color: #333; text-align: center; line-height: 1.2; font-weight: bold;'>{p_cash:.0f}%<br>현금성자산</div>
        <div style='position: absolute; top: 35%; right: -12%; font-size: 12.5px; color: #333; text-align: center; line-height: 1.2; font-weight: bold;'>{p_ovs:.0f}%<br>해외투자</div>
        <div style='position: absolute; bottom: 8%; left: 12%; font-size: 13px; color: #fff; font-weight: bold; text-align: center; line-height: 1.2; text-shadow: 0px 0px 3px rgba(0,0,0,0.5);'>{p_dom:.0f}%<br>국내투자</div>
    </div>
    """

    html_parts = []
    html_parts.append("<div style='text-align: right; font-size: 13px; color: #555; font-weight: bold; margin-bottom: 5px;'>단위 : 원화(KRW)</div>")
    html_parts.append("<div class='insight-container'>")
    html_parts.append("<div class='insight-left'>")
    html_parts.append("<div class='card-main'>")
    
    html_parts.append("<div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: auto;'>")
    html_parts.append("<div style='font-size: 22px; font-weight: bold; color: #111;'>총 자산</div>")
    html_parts.append("<div style='text-align: right; line-height: 1.1;'>")
    html_parts.append(f"<div style='font-size: 30px; font-weight: bold; color: #111;'>{fmt(t_asset)}</div>")
    html_parts.append(f"<div style='font-size: 13.5px; color: #777; font-weight: normal; margin-top: 6px;'>[ 전일비 <span class='{col(t_diff)}'>{fmt(t_diff, True)}</span> / 전주비 <span class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</span> ]</div>")
    html_parts.append("</div>")
    html_parts.append("</div>")

    html_parts.append("<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;'>")
    html_parts.append(donut_html)
    
    html_parts.append("<div style='display: grid; grid-template-columns: auto auto; row-gap: 8px; column-gap: 15px; justify-content: end; align-items: start; width: 100%;'>")
    html_parts.append("<div style='color: #777; font-size: 18px; text-align: right; line-height: 22px;'>평가금액</div>")
    html_parts.append(f"<div style='color: #111; font-size: 22px; font-weight: 400 !important; text-align: right; line-height: 22px;'>{fmt(t_asset - cash_total)}</div>")
    html_parts.append("<div style='color: #777; font-size: 18px; text-align: right; line-height: 22px;'>현금성자산</div>")
    html_parts.append(f"<div style='color: #111; font-size: 22px; font-weight: 400 !important; text-align: right; line-height: 22px;'>{fmt(cash_total)}</div>")
    html_parts.append("<div style='color: #777; font-size: 18px; font-weight: normal; text-align: right; line-height: 22px;'>총 손익</div>")
    # [수정] 총 손익 숫자도 900에서 bold(700)로 낮춰 통일감 부여
    html_parts.append(f"<div style='text-align: right;'><div style='font-size: 22px; font-weight: bold; line-height: 22px;' class='{col(t_profit)}'>{fmt(t_profit, True)}</div><div style='font-size: 15.5px; font-weight: 400 !important; margin-top: 4px;' class='{col(t_rate)}'>{fmt_p(t_rate)}</div></div>")
    html_parts.append("</div>")
    html_parts.append("</div>")

    html_parts.append("<div>")
    html_parts.append("<div style='display: flex; height: 20px; width: 100%; border-radius: 4px; overflow: hidden; border: 1px solid #ccc; margin-bottom: 8px;'>")
    html_parts.append(render_bar(p_dc, '#8eaadb'))
    html_parts.append(render_bar(p_irp, '#f4b183'))
    html_parts.append(render_bar(p_pension, '#a9d18e'))
    html_parts.append(render_bar(p_isa, '#ffd966'))
    html_parts.append("</div>")
    html_parts.append("<div style='display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #777; padding: 0 2px; margin-bottom: 24px;'>")
    html_parts.append("<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#8eaadb;'></div>퇴직연금(DC)</div>")
    html_parts.append("<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#f4b183;'></div>퇴직연금(IRP)</div>")
    html_parts.append("<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#a9d18e;'></div>연금저축(CMA)</div>")
    html_parts.append("<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#ffd966;'></div>ISA(중개형)</div>")
    html_parts.append("</div>")
    html_parts.append("<div style='padding: 12px 15px; background: rgba(255,255,255,0.5); border-radius: 10px; border: 1px solid #e8dbad;'>")
    html_parts.append("<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>")
    html_parts.append("<span style='font-size: 15px; color: #777; font-weight: normal;'>🎯 은퇴 자산 목표 10억 달성률</span>")
    html_parts.append(f"<span style='font-size: 15px; font-weight: bold; color: #4a90e2;'>{progress_pct:.1f}%</span>")
    html_parts.append("</div>")
    html_parts.append("<div style='width: 100%; height: 6px; background-color: #e2e2e2; border-radius: 3px; overflow: hidden;'>")
    html_parts.append(f"<div style='width: {progress_pct}%; height: 100%; background: linear-gradient(90deg, #8eaadb, #4a90e2);'></div>")
    html_parts.append("</div>")
    html_parts.append("</div>")
    html_parts.append("</div>") 
    html_parts.append("</div>") 
    html_parts.append("</div>") 
    
    html_parts.append("<div class='insight-right'>")
    html_parts.append("<div class='grid-2x2'>")
    for k in FIXED_ACCOUNT_ORDER:
        if k in data:
            a = data.get(k, {})
            acc_name = '퇴직연금(DC)' if k == 'DC' else ('퇴직연금(IRP)' if k == 'IRP' else ('연금저축(CMA)' if k == 'PENSION' else 'ISA(중개형)'))
            acc_asset = a.get('총 자산', a.get('총자산', 0))
            acc_principal = a.get('원금', 0)
            acc_profit = a.get('총 수익', a.get('총 손익', a.get('평가손익', 0)))
            acc_rate = a.get('수익률(%)', a.get('손익률(%)', 0))
            html_parts.append("<div class='card-sub' style='padding: 12px 18px;'>")
            html_parts.append(f"<div style='text-align: right; font-size: 14px; color: #555; font-weight: bold; margin-bottom: 0px;'>{OPEN_DATES.get(k, '')}</div>")
            html_parts.append(f"<div style='font-size: 20px; font-weight: bold; color: #111; margin-bottom: 2px; margin-top: -3px;'>{acc_name}</div>")
            html_parts.append("<div style='border-bottom: 1px solid #eee; margin-bottom: 10px;'></div>")
            html_parts.append("<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>")
            html_parts.append("<span style='font-size: 15px; color: #777; font-weight: normal;'>총 자산</span>")
            html_parts.append(f"<span style='font-size: 16.5px; color: #111; font-weight: normal;'>{fmt(acc_asset)}</span>")
            html_parts.append("</div>")
            html_parts.append("<div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;'>")
            html_parts.append("<span style='font-size: 15px; color: #777; font-weight: normal;'>총 손익</span>")
            html_parts.append(f"<div style='text-align: right; line-height: 1.25;'><div class='{col(acc_profit)}' style='font-size: 16.5px; font-weight: normal;'>{fmt(acc_profit, True)}</div><div class='{col(acc_rate)}' style='font-size: 15px; font-weight: 400 !important; margin-top: 2px;'>{fmt_p(acc_rate)}</div></div>")
            html_parts.append("</div>")
            principal_label = "* 원금"
            html_parts.append(f"<div style='font-size: 14.5px; color: #555; font-weight: bold; margin-top: auto;'>{principal_label} : {fmt(acc_principal)}</div>")
            html_parts.append("</div>")
    html_parts.append("</div>") 
    html_parts.append("</div>") 
    html_parts.append("</div>") 
    
    html_parts.append("<div class='insight-bottom-box'>")
    html_parts.append(bottom_html)
    html_parts.append("</div>")
    
    html_str = "".join(html_parts).replace("\n", "")
    st.markdown(html_str, unsafe_allow_html=True)

unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"

st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"<div style='margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(tot.get('총 자산', tot.get('총자산',0)))}</span> / 총 손익 : <span class='summary-val {col(tot.get('총 수익', tot.get('총 손익', 0)))}'>{fmt(tot.get('총 수익', tot.get('총 손익', 0)), True)} ({fmt_p(tot.get('수익률(%)', tot.get('손익률(%)', 0)))})</span></div></div>", unsafe_allow_html=True)

h1_table = """<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>투자원금</th></tr><tr><th class='th-week'>7일전</th><th class='th-week'>15일전</th><th class='th-week'>30일전</th></tr>"""
h1_table = re.sub(r'\n\s*', '', h1_table)

ty = tot.get('수익률(%)', tot.get('손익률(%)', 0))
tg = tot.get('총 수익', tot.get('총 손익', tot.get('평가손익', 0)))
ta = tot.get('총 자산', tot.get('총자산', 0))
to = tot.get('원금합', 0)
td7_tot_1 = (ta - tot.get('평가손익(7일전)', 0)) - to
td15_tot_1 = (ta - tot.get('평가손익(15일전)', 0)) - to
td30_tot_1 = (ta - tot.get('평가손익(30일전)', 0)) - to

h1 = [unit_html, h1_table]
h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(ta)}</td><td class='{col(tg)}'>{fmt(tg, True)}</td><td class='{col(td7_tot_1)}'>{fmt(td7_tot_1, True)}</td><td class='{col(td15_tot_1)}'>{fmt(td15_tot_1, True)}</td><td class='{col(td30_tot_1)}'>{fmt(td30_tot_1, True)}</td><td class='{col(ty)}'>{fmt_p(ty)}</td><td>{fmt(to)}</td></tr>")

keys_1 = [k for k in FIXED_ACCOUNT_ORDER if k in data]
if st.session_state.sort_mode == 'asset': keys_1.sort(key=lambda k: data.get(k, {}).get('총 자산', 0), reverse=True)
elif st.session_state.sort_mode == 'profit': keys_1.sort(key=lambda k: data.get(k, {}).get('총 수익', 0), reverse=True)
elif st.session_state.sort_mode == 'rate': keys_1.sort(key=lambda k: data.get(k, {}).get('수익률(%)', 0), reverse=True)

for k in keys_1:
    a = data.get(k, {})
    curr_asset = a.get('총 자산', 0); principal = a.get('원금', 0)
    a_prof = a.get('총 수익', 0); a_rate = a.get('수익률(%)', 0)
    ad7_acc_1 = (curr_asset - a.get('평가손익(7일전)', 0)) - principal
    ad15_acc_1 = (curr_asset - a.get('평가손익(15일전)', 0)) - principal
    ad30_acc_1 = (curr_asset - a.get('평가손익(30일전)', 0)) - principal
    h1.append(f"<tr><td>{clean_label(a.get('label', ''))}</td><td>{fmt(curr_asset)}</td><td class='{col(a_prof)}'>{fmt(a_prof, True)}</td><td class='{col(ad7_acc_1)}'>{fmt(ad7_acc_1, True)}</td><td class='{col(ad15_acc_1)}'>{fmt(ad15_acc_1, True)}</td><td class='{col(ad30_acc_1)}'>{fmt(ad30_acc_1, True)}</td><td class='{col(a_rate)}'>{fmt_p(a_rate)}</td><td>{fmt(principal)}</td></tr>")
h1.append("</table>")
st.markdown("".join(h1), unsafe_allow_html=True)

ag_tot = ta - tot.get('매입금액합',0)
ay_tot = (ag_tot / tot.get('매입금액합',1) * 100) if tot.get('매입금액합',1) > 0 else 0
st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(ta)}</span> / 총 손익 : <span class='summary-val {col(ag_tot)}'>{fmt(ag_tot, True)} ({fmt_p(ay_tot)})</span></div>", unsafe_allow_html=True)

h2_table = """<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>매입금액</th></tr><tr><th class='th-week'>전일비</th><th class='th-week'>전주비</th><th class='th-week'>전월비</th></tr>"""
h2_table = re.sub(r'\n\s*', '', h2_table)
td1_tot = tot.get('평가손익(1일전)',0); td7_tot = tot.get('평가손익(7일전)',0); td30_tot = tot.get('평가손익(30일전)',0)

h2 = [unit_html, h2_table]
h2.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(ta)}</td><td class='{col(ag_tot)}'>{fmt(ag_tot, True)}</td><td class='{col(td1_tot)}'>{fmt(td1_tot, True)}</td><td class='{col(td7_tot)}'>{fmt(td7_tot, True)}</td><td class='{col(td30_tot)}'>{fmt(td30_tot, True)}</td><td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td><td>{fmt(tot.get('매입금액합', 0))}</td></tr>")

sec2_items = []
for k in FIXED_ACCOUNT_ORDER:
    if k in data:
        a = data.get(k, {}); ag_acc = sum(i.get('평가손익',0) for i in a.get('상세', []) if i.get('종목명') != '[ 합계 ]')
        ap_acc = a.get('총 자산', 0) - ag_acc; ay_acc = (ag_acc/ap_acc*100) if ap_acc > 0 else 0
        sec2_items.append({'k': k, 'a': a, 'ag_acc': ag_acc, 'ap_acc': ap_acc, 'ay_acc': ay_acc})

if st.session_state.sort_mode == 'asset': sec2_items.sort(key=lambda x: x['a'].get('총 자산', 0), reverse=True)
elif st.session_state.sort_mode == 'profit': sec2_items.sort(key=lambda x: x['ag_acc'], reverse=True)
elif st.session_state.sort_mode == 'rate': sec2_items.sort(key=lambda x: x['ay_acc'], reverse=True)

for item in sec2_items:
    a = item['a']; ad1_acc = a.get('평가손익(1일전)', 0); ad7_acc = a.get('평가손익(7일전)', 0); ad30_acc = a.get('평가손익(30일전)', 0)
    h2.append(f"<tr><td>{clean_label(a.get('label', ''))}</td><td>{fmt(a.get('총 자산', 0))}</td><td class='{col(item['ag_acc'])}'>{fmt(item['ag_acc'], True)}</td><td class='{col(ad1_acc)}'>{fmt(ad1_acc, True)}</td><td class='{col(ad7_acc)}'>{fmt(ad7_acc, True)}</td><td class='{col(ad30_acc)}'>{fmt(ad30_acc, True)}</td><td class='{col(item['ay_acc'])}'>{fmt_p(item['ay_acc'])}</td><td>{fmt(item['ap_acc'])}</td></tr>")
h2.append("</table>")
st.markdown("".join(h2), unsafe_allow_html=True)

st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
b1, b2, b3, b4, b5 = st.columns(5)
with b1:
    st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
    is_init = (st.session_state.sort_mode == 'init')
    if st.button("🛠️ 초기화 [ ● ]" if is_init else "🛠️ 초기화 [ ○ ]", type="primary" if is_init else "secondary"): st.session_state.sort_mode = 'init'; st.rerun()
with b2:
    is_asset = (st.session_state.sort_mode == 'asset')
    if st.button("💰 총 자산 [ ● ]" if is_asset else "💰 총 자산 [ ○ ]", type="primary" if is_asset else "secondary"): st.session_state.sort_mode = 'asset'; st.rerun()
with b3:
    is_profit = (st.session_state.sort_mode == 'profit')
    if st.button("📊 평가손익 [ ● ]" if is_profit else "📊 평가손익 [ ○ ]", type="primary" if is_profit else "secondary"): st.session_state.sort_mode = 'profit'; st.rerun()
with b4:
    is_rate = (st.session_state.sort_mode == 'rate')
    if st.button("📈 손익률 [ ● ]" if is_rate else "📈 손익률 [ ○ ]", type="primary" if is_rate else "secondary"): st.session_state.sort_mode = 'rate'; st.rerun()
with b5:
    is_code = st.session_state.show_code
    code_btn_label = "💻 종목코드 [ + ]" if is_code else "💻 종목코드 [ - ]"
    if st.button(code_btn_label, type="primary" if is_code else "secondary"): st.session_state.show_code = not st.session_state.show_code; st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
t3_lbl = {'DC':'퇴직연금(DC)계좌 / (삼성증권 7165962472-28)', 'PENSION':'연금저축(CMA)계좌 / (삼성증권 7169434836-15)', 'ISA':'ISA(중개형)계좌 / (키움증권 6448-4934)', 'IRP':'퇴직연금(IRP)계좌 / (삼성증권 7164499007-29)'}

for k in FIXED_ACCOUNT_ORDER:
    if k not in data: continue
    a = data.get(k, {})
    with st.expander(f"📂 [ {t3_lbl.get(k, a.get('label', ''))} ] 종목별 현황", expanded=False):
        s_data = next((i for i in a.get('상세', []) if i.get('종목명') == "[ 합계 ]"), {})
        extra_info_html = ""
        if k in ['DC', 'IRP']:
            safe_pct = sum(item.get('비중', 0) for item in a.get('상세', []) if (k == 'DC' and item.get('종목명') in ['삼성화재 퇴직연금(3.05%/年)', '현금성자산']) or (k == 'IRP' and item.get('종목명') == '현금성자산'))
            risky_pct = 100.0 - safe_pct
            extra_info_html = f"<div style='font-size:14.5px; font-weight:normal; color:#555;'>[ 위험자산 : {risky_pct:.1f}% | 안전자산 : {safe_pct:.1f}% ]</div>"
        a_prof = s_data.get('평가손익', 0); a_rate = s_data.get('수익률(%)', 0)
        st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(a.get('총 자산', 0))}</span> / 총 손익 : <span class='summary-val {col(a_prof)}'>{fmt(a_prof, True)} ({fmt_p(a_rate)})</span></div>{extra_info_html}</div>", unsafe_allow_html=True)
        h3_table = f"<table class='main-table'><tr><th>종목명</th>{'<th>종목코드</th>' if st.session_state.show_code else ''}<th>비중</th><th>총 자산</th><th>평가손익</th><th>손익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>"
        h3 = [unit_html, h3_table]
        items = [i for i in a.get('상세', []) if i.get('종목명') != "[ 합계 ]"]
        if st.session_state.sort_mode == 'asset': items.sort(key=lambda x: x.get('총 자산', 0), reverse=True)
        elif st.session_state.sort_mode == 'profit': items.sort(key=lambda x: x.get('평가손익', 0), reverse=True)
        elif st.session_state.sort_mode == 'rate': items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
        for i in ([s_data] + items):
            is_s = (i.get('종목명') == "[ 합계 ]"); row = f"<tr class='sum-row'>" if is_s else "<tr>"
            row += f"<td>{i.get('종목명', '')}</td>"
            if st.session_state.show_code: row += f"<td>{'-' if is_s or i.get('코드','-')=='-' else i.get('코드', '')}</td>"
            i_rate = i.get('수익률(%)', 0)
            row += f"<td>{i.get('비중',0):.1f}%</td><td>{fmt(i.get('총 자산', 0))}</td><td class='{col(i.get('평가손익',0))}'>{fmt(i.get('평가손익',0), True)}</td><td class='{col(i_rate)}'>{fmt_p(i_rate)}</td><td>{fmt(i.get('수량','-'))}</td><td>{fmt(i.get('매입가','-'))}</td><td>{fmt(i.get('현재가','-'))}</td></tr>"
            h3.append(row)
        h3.append("</table>"); st.markdown("".join(h3), unsafe_allow_html=True)
