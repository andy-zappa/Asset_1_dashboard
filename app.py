import streamlit as st
import json
import warnings
import google.generativeai as genai
import andy_pension_v2
import os
import re

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="ZAPPA Asset Dashboard")

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

/* =========================================================
   [ZAPPA] 대시보드 디자인 (Squeeze 및 Baseline 정렬 최적화)
   ========================================================= */
.insight-container { display: flex; gap: 20px; align-items: stretch; margin-bottom: 20px; }
.insight-left { flex: 0 0 46%; display: flex; flex-direction: column; }
.insight-right { flex: 1; display: flex; flex-direction: column; }

.card-main { background-color: #fffdf2; border: 2px solid #e8dbad; border-radius: 18px; padding: 18px 22px 15px 22px; position: relative; box-shadow: 0 2px 6px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; }
.grid-2x2 { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 15px; height: 100%; }

.card-sub { background: #fff; border: 1.5px solid #ddd; border-radius: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.02); display: flex; flex-direction: column; padding: 10px 15px; }

.insight-bottom-box { background: #fff; border: 1.5px solid #ddd; border-radius: 18px; padding: 25px; box-shadow: 0 1px 4px rgba(0,0,0,0.02); font-size: 15.5px; line-height: 1.8; color: #333; margin-top: 5px; margin-bottom: 25px; }

.summary-text { font-size: 16px !important; font-weight: bold !important; color: #333; margin-bottom: 10px; }
.summary-val { font-size: 20px !important; }

/* 엑셀 스타일 병합 */
.main-table th.th-eval { border-right: none !important; }
.main-table th.th-blank { border-left: none !important; border-bottom: none !important; padding: 0 !important; }
.main-table th.th-week { border-left: 1px solid #ddd !important; border-top: 1px solid #ddd !important; font-size: 13.5px; }

/* =========================================================
   [ZAPPA 플로팅 배너 CSS] 
   ========================================================= */
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
    t_original_sum = tot.get('원금합', 0)
    
    cash_total = 0; ovs_total = 0; dom_total = 0; all_items = []
    
    for k in FIXED_ACCOUNT_ORDER:
        if k in data:
            short_acc_name = 'DC' if k == 'DC' else ('IRP' if k == 'IRP' else ('CMA' if k == 'PENSION' else 'ISA'))
            for item in data[k].get('상세', []):
                name = item.get('종목명', '')
                if name == '[ 합계 ]': continue
                item_copy = item.copy(); item_copy['계좌'] = short_acc_name; all_items.append(item_copy)
                val = item.get('총 자산', item.get('총자산', 0)); name_lower = name.lower()
                cash_kws = ['현금성자산', 'mmf']; ovs_kws = ['tiger', 's&p', '나스닥', '필라델피아', '다우존스', 'ai테크']
                if any(kw in name_lower for kw in cash_kws): cash_total += val
                elif any(kw in name_lower for kw in ovs_kws): ovs_total += val
                else: dom_total += val

    # [수정] 현금성자산은 BEST/WORST 랭킹 대상에서 제외
    tradeable_items = [it for it in all_items if "현금성자산" not in it.get("종목명", "")]
    tradeable_items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
    best_5 = tradeable_items[:5]
    worst_5 = tradeable_items[::-1][:5]

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
        if p == 0: return ""
        return f"<div style='width: {p}%; background-color: {color}; height: 100%; display: flex; align-items: center; justify-content: center; position: relative;'><span style='position: absolute; font-size: 13px; color: #333; z-index: 10; white-space: nowrap;'>{p:.0f}%</span></div>"

    # =====================================================================
    # 🧠 ZAPPA 동적 시황 분석 알고리즘 (여백 최소화 & 섹션 병합 패치)
    # =====================================================================
    try:
        acc_rates = []
        for k in FIXED_ACCOUNT_ORDER:
            if k in data:
                acc_name_str = '퇴직연금(DC)' if k == 'DC' else ('퇴직연금(IRP)' if k == 'IRP' else ('연금저축(CMA)' if k == 'PENSION' else 'ISA(중개형)'))
                rt = data[k].get('수익률(%)', 0); acc_rates.append((acc_name_str, rt))
        acc_rates.sort(key=lambda x: x[1], reverse=True)
        best_acc_name, best_acc_rate = acc_rates[0] if acc_rates else ("전체", 0)

        b1_name = best_5[0]['종목명'] if len(best_5) > 0 else "주도 종목"
        b1_rate = best_5[0].get('수익률(%)', 0) if len(best_5) > 0 else 0
        w1_name = worst_5[0]['종목명'] if len(worst_5) > 0 else "부진 종목"
        w1_rate = worst_5[0].get('수익률(%)', 0) if len(worst_5) > 0 else 0

        market_lead_txt = "한국 주식형 ETF의 견조한 상승세가 미국 ETF 실적을 상회하며" if p_dom >= p_ovs else "미국 기술주 및 지수 추종 ETF가 든든하게 시장을 견인하며"

        # [수정] margin-left: -15px 적용하여 2칸 더 들여쓰기 (좌측 밀착)
        zappa_html = f"<div style='font-size: 14.5px; line-height: 1.85; color: #444; letter-spacing: -0.2px; padding-left: 0px; margin-left: -15px;'>"
        t_style = "color:#111; font-size:15px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;"
        bullet = "<span style='font-size:11px;'>🔵</span>"
        
        def rate_span(v): return f"<span class='{col(v)}' style='font-weight:bold;'>{fmt_p(v)}</span>"

        # [수정] 계좌 분석과 종목 분석을 하나로 병합하여 공간 창출
        zappa_html += f"<div style='margin-bottom: 22px;'><span style='{t_style}'>{bullet} 계좌 현황 및 종목 분석</span>최근 코스피의 꾸준한 반등 흐름 속에 <strong>{market_lead_txt}</strong> 전체 평가 손익을 주도하며 <strong>{best_acc_name} 계좌가 전체 수익률({rate_span(best_acc_rate)}) 1위</strong>를 기록 중입니다. 개별 종목으로는 <strong>{b1_name} ({rate_span(b1_rate)})</strong>가 시장 트렌드에 부합하여 강력한 효자 역할을 하는 반면, <strong>{w1_name} ({rate_span(w1_rate)})</strong> 등 일부 종목은 매크로 환경 변화로 상대적으로 부진한 흐름입니다.</div>"

        zappa_html += f"<div style='margin-bottom: 0px;'><span style='{t_style}'>{bullet} 거시 경제 및 향후 대응 전략</span>간밤 미 빅테크 실적 및 주요 지표 변화로 변동성이 예상되나 코스피는 견조한 흐름을 유지하고 있습니다. <strong>수익이 큰 종목은 일부 익절을 통해 현금({p_cash:.0f}%) 비중을 확보하고 리밸런싱을 고려</strong>하며 시장에 대응할 것을 권장합니다.</div>"

        zappa_html += "</div>"
    except Exception: zappa_html = "<p>ZAPPA 엔진 데이터를 분석하는 중입니다...</p>"

    st.markdown("<div class='sub-title' style='margin-bottom: 15px;'>💡 자파의 [절세계좌] 자산 현황 보고</div>", unsafe_allow_html=True)
    donut_css = f"background: conic-gradient(#ffffff 0% {p_cash}%, #d9d9d9 {p_cash}% {p_cash+p_ovs}%, #8c8c8c {p_cash+p_ovs}% 100%);"
    donut_html = f"<div style='position: relative; width: 130px; height: 130px; border-radius: 50%; {donut_css} box-shadow: inset 0 0 8px rgba(0,0,0,0.1); border: 1px solid #d0d0d0; flex-shrink: 0; margin-top: -12px;'><div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 35%; height: 35%; background-color: #fffdf2; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.05);'></div><div style='position: absolute; top: 3%; left: 50%; transform: translateX(-50%); font-size: 12.5px; color: #333; text-align: center; line-height: 1.2; font-weight: bold;'>{p_cash:.0f}%<br>현금성자산</div><div style='position: absolute; top: 28%; right: -12%; font-size: 12.5px; color: #333; text-align: center; line-height: 1.2; font-weight: bold;'>{p_ovs:.0f}%<br>해외투자</div><div style='position: absolute; bottom: 8%; left: 18%; font-size: 13px; color: #fff; font-weight: bold; text-align: center; line-height: 1.2; text-shadow: 0px 0px 3px rgba(0,0,0,0.5);'>{p_dom:.0f}%<br>국내투자</div></div>"

    html_parts = ["<div style='text-align: right; font-size: 13px; color: #555; font-weight: bold; margin-bottom: 5px;'>단위 : 원화(KRW)</div>", "<div class='insight-container'>", "<div class='insight-left'>", "<div class='card-main'>", "<div style='display: flex; flex-direction: column; margin-bottom: auto;'>"]
    
    # [수정] 총 자산 라벨 폰트를 19px로, 금액 폰트를 27px로 조정하여 디자인 밸런스 최적화
    html_parts.append("<div style='display: flex; justify-content: space-between; align-items: baseline;'>")
    html_parts.append("<div style='font-size: 19px; font-weight: bold; color: #111; line-height: 1;'>총 자산</div>")
    html_parts.append(f"<div style='font-size: 27px; font-weight: bold; color: #111; line-height: 1;'>{fmt(t_asset)}</div>")
    html_parts.append("</div>")
    
    html_parts.append("<div style='display: flex; justify-content: flex-end; align-items: baseline; margin-top: 8px;'>")
    html_parts.append(f"<div style='font-size: 13.5px; color: #777; font-weight: normal; line-height: 1;'>[ 전일비 <span class='{col(t_diff)}'>{fmt(t_diff, True)}</span> / 전주비 <span class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</span> ]</div>")
    html_parts.append("</div>", "</div>", f"<div style='display: flex; justify-content: space-between; align-items: center; margin-top: 10px; margin-bottom: 22px; padding-left: 15px;'>", donut_html, "<div style='display: grid; grid-template-columns: auto auto; row-gap: 8px; column-gap: 15px; justify-content: end; align-items: baseline; width: 100%; margin-top: 18px;'>", "<div style='color: #777; font-size: 15px; text-align: right; line-height: 22px;'>평가금액</div>", f"<div style='color: #111; font-size: 22px; font-weight: 400 !important; text-align: right; line-height: 22px;'>{fmt(t_asset - cash_total)}</div>", "<div style='color: #777; font-size: 15px; text-align: right; line-height: 22px;'>현금성자산</div>", f"<div style='color: #111; font-size: 22px; font-weight: 400 !important; text-align: right; line-height: 22px;'>{fmt(cash_total)}</div>", "<div style='color: #777; font-size: 15px; font-weight: normal; text-align: right; line-height: 22px;'>총 손익</div>", f"<div style='text-align: right;'><div style='font-size: 22px; font-weight: bold; line-height: 22px;' class='{col(t_profit)}'>{fmt(t_profit, True)}</div><div style='font-size: 15.5px; font-weight: 400 !important; margin-top: 4px;' class='{col(t_rate)}'>{fmt_p(t_rate)}</div></div>", "</div>", "</div>", "<div>", "<div style='display: flex; height: 20px; width: 100%; border-radius: 4px; border: 1px solid #ccc; margin-bottom: 6px; overflow: hidden;'>", render_bar(p_dc, '#8eaadb'), render_bar(p_irp, '#f4b183'), render_bar(p_pension, '#a9d18e'), render_bar(p_isa, '#ffd966'), "</div>", "<div style='display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #777; padding: 0 2px; margin-bottom: 16px;'>", "<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#8eaadb;'></div>퇴직연금(DC)</div>", "<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#f4b183;'></div>퇴직연금(IRP)</div>", "<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#a9d18e;'></div>연금저축(CMA)</div>", "<div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#ffd966;'></div>ISA(중개형)</div>", "</div>", "<div style='padding: 10px 15px; background: rgba(255,255,255,0.5); border-radius: 10px; border: 1px solid #e8dbad;'>", "<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>", f"<span style='font-size: 15px; color: #777; font-weight: normal;'>🎯 은퇴 자산 목표 10억 달성률 <span style='font-size: 13.5px; color: #888;'>(* 원금 : {fmt(t_original_sum)})</span></span>", f"<span style='font-size: 15px; font-weight: bold; color: #4a90e2;'>{progress_pct:.1f}%</span>", "</div>", f"<div style='width: 100%; height: 6px; background-color: #e2e2e2; border-radius: 3px; overflow: hidden;'><div style='width: {progress_pct}%; height: 100%; background: linear-gradient(90deg, #8eaadb, #4a90e2);'></div></div>", "</div>", "</div>", "</div>", "</div>", "<div class='insight-right'>", "<div class='grid-2x2'>")
    
    for k in FIXED_ACCOUNT_ORDER:
        if k in data:
            a = data[k]; acc_name = '퇴직연금(DC)' if k == 'DC' else ('퇴직연금(IRP)' if k == 'IRP' else ('연금저축(CMA)' if k == 'PENSION' else 'ISA(중개형)'))
            acc_asset = a.get('총 자산', a.get('총자산', 0)); acc_principal = a.get('원금', 0); acc_profit = a.get('총 수익', a.get('총 손익', a.get('평가손익', 0))); acc_rate = a.get('수익률(%)', a.get('수익률(%)', 0))
            html_parts.extend(["<div class='card-sub' style='padding: 10px 15px; display: flex; flex-direction: column; justify-content: space-between; height: 100%;'>", "<div>", f"<div style='text-align: right; font-size: 13.5px; color: #666; font-weight: normal; margin-bottom: -2px; line-height: 1;'>{OPEN_DATES.get(k, '')}</div>", f"<div style='font-size: 19px; font-weight: bold; color: #111; margin-bottom: 2px;'>{acc_name}</div>", "<div style='border-bottom: 1px solid #eee; margin-bottom: 6px; margin-top: 2px;'></div>", f"<div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 자산</span><span style='font-size: 16px; color: #111; font-weight: normal;'>{fmt(acc_asset)}</span></div>", f"<div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 손익</span><div style='text-align: right; line-height: 1.2;'><div class='{col(acc_profit)}' style='font-size: 16px; font-weight: normal;'>{fmt(acc_profit, True)}</div><div class='{col(acc_rate)}' style='font-size: 14px; font-weight: normal; margin-top: 1px;'>{fmt_p(acc_rate)}</div></div></div>", "</div>", f"<div style='font-size: 13.5px; color: #666; font-weight: normal; margin-top: auto; padding-top: 2px;'>* 원금 : {fmt(acc_principal)}</div>", "</div>"])
    
    html_parts.extend(["</div>", "</div>", "</div>", "<div class='insight-bottom-box' style='display: flex; gap: 30px; align-items: stretch;'>", "<div style='flex: 1; padding-right: 15px; border-right: 1px solid #eaeaea;'>", "<div style='font-size: 19px; font-weight: bold; color: #111; margin-bottom: 8px;'>📈 손익률 BEST 5</div>", "<table class='main-table' style='margin-bottom: 20px; font-size: 13.5px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>계좌</th></tr>"])
    for idx, it in enumerate(best_5): html_parts.append(f"<tr><td>{idx+1}</td><td>{it.get('종목명','')}</td><td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td><td>{it.get('계좌','')}</td></tr>")
    html_parts.extend(["</table>", "<div style='font-size: 19px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px;'>📉 손익률 WORST 5</div>", "<table class='main-table' style='margin-bottom: 0px; font-size: 13.5px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>계좌</th></tr>"])
    for idx, it in enumerate(worst_5): html_parts.append(f"<tr><td>{idx+1}</td><td>{it.get('종목명','')}</td><td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td><td>{it.get('계좌','')}</td></tr>")
    html_parts.extend(["</table>", "</div>", "<div style='flex: 1; padding-left: 10px;'>", "<div style='font-size: 19px; font-weight: bold; color: #111; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 8px;'>💡 시황 및 향후 전망</div>", zappa_html, "</div>", "</div>"])
    st.markdown("".join(html_parts).replace("\n", ""), unsafe_allow_html=True)

unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"
st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"<div style='margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> / 총 손익 : <span class='summary-val {col(t_profit)}'>{fmt(t_profit, True)} ({fmt_p(t_rate)})</span></div></div>", unsafe_allow_html=True)
h1 = [unit_html, "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>투자원금</th></tr><tr><th class='th-week'>7일전</th><th class='th-week'>15일전</th><th class='th-week'>30일전</th></tr>"]
td7_tot_1 = (t_asset - tot.get('평가손익(7일전)', 0)) - t_original_sum; td15_tot_1 = (t_asset - tot.get('평가손익(15일전)', 0)) - t_original_sum; td30_tot_1 = (t_asset - tot.get('평가손익(30일전)', 0)) - t_original_sum
h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(t_asset)}</td><td class='{col(t_profit)}'>{fmt(t_profit, True)}</td><td class='{col(td7_tot_1)}'>{fmt(td7_tot_1, True)}</td><td class='{col(td15_tot_1)}'>{fmt(td15_tot_1, True)}</td><td class='{col(td30_tot_1)}'>{fmt(td30_tot_1, True)}</td><td class='{col(t_rate)}'>{fmt_p(t_rate)}</td><td>{fmt(t_original_sum)}</td></tr>")
for k in FIXED_ACCOUNT_ORDER:
    if k in data:
        a = data[k]; curr = a.get('총 자산', 0); princ = a.get('원금', 0); prof = a.get('총 수익', 0); rate = a.get('수익률(%)', 0); d7 = (curr - a.get('평가손익(7일전)', 0)) - princ; d15 = (curr - a.get('평가손익(15일전)', 0)) - princ; d30 = (curr - a.get('평가손익(30일전)', 0)) - princ
        h1.append(f"<tr><td>{clean_label(a.get('label', ''))}</td><td>{fmt(curr)}</td><td class='{col(prof)}'>{fmt(prof, True)}</td><td class='{col(d7)}'>{fmt(d7, True)}</td><td class='{col(d15)}'>{fmt(d15, True)}</td><td class='{col(d30)}'>{fmt(d30, True)}</td><td class='{col(rate)}'>{fmt_p(rate)}</td><td>{fmt(princ)}</td></tr>")
h1.append("</table>"); st.markdown("".join(h1), unsafe_allow_html=True)

ag_tot = t_asset - tot.get('매입금액합',0); ay_tot = (ag_tot / tot.get('매입금액합',1) * 100) if tot.get('매입금액합',1) > 0 else 0
st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> / 총 손익 : <span class='summary-val {col(ag_tot)}'>{fmt(ag_tot, True)} ({fmt_p(ay_tot)})</span></div>", unsafe_allow_html=True)
h2 = [unit_html, "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>매입금액</th></tr><tr><th class='th-week'>전일비</th><th class='th-week'>전주비</th><th class='th-week'>전월비</th></tr>"]
h2.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(t_asset)}</td><td class='{col(ag_tot)}'>{fmt(ag_tot, True)}</td><td class='{col(tot.get('평가손익(1일전)',0))}'>{fmt(tot.get('평가손익(1일전)',0), True)}</td><td class='{col(tot.get('평가손익(7일전)',0))}'>{fmt(tot.get('평가손익(7일전)',0), True)}</td><td class='{col(tot.get('평가손익(30일전)',0))}'>{fmt(tot.get('평가손익(30일전)',0), True)}</td><td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td><td>{fmt(tot.get('매입금액합', 0))}</td></tr>")
for k in FIXED_ACCOUNT_ORDER:
    if k in data:
        a = data[k]; ag_acc = sum(i.get('평가손익',0) for i in a.get('상세', []) if i.get('종목명') != '[ 합계 ]'); ap_acc = a.get('총 자산', 0) - ag_acc; ay_acc = (ag_acc/ap_acc*100) if ap_acc > 0 else 0
        h2.append(f"<tr><td>{clean_label(a.get('label', ''))}</td><td>{fmt(a.get('총 자산', 0))}</td><td class='{col(ag_acc)}'>{fmt(ag_acc, True)}</td><td class='{col(a.get('평가손익(1일전)', 0))}'>{fmt(a.get('평가손익(1일전)', 0), True)}</td><td class='{col(a.get('평가손익(7일전)', 0))}'>{fmt(a.get('평가손익(7일전)', 0), True)}</td><td class='{col(a.get('평가손익(30일전)', 0))}'>{fmt(a.get('평가손익(30일전)', 0), True)}</td><td class='{col(ay_acc)}'>{fmt_p(ay_acc)}</td><td>{fmt(ap_acc)}</td></tr>")
h2.append("</table>"); st.markdown("".join(h2), unsafe_allow_html=True)

st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
b1, b2, b3, b4, b5 = st.columns(5)
with b1:
    st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
    if st.button("🛠️ 초기화 [ " + ("●" if st.session_state.sort_mode == 'init' else "○") + " ]", type="primary" if st.session_state.sort_mode == 'init' else "secondary"): st.session_state.sort_mode = 'init'; st.rerun()
with b2:
    if st.button("💰 총 자산 [ " + ("●" if st.session_state.sort_mode == 'asset' else "○") + " ]", type="primary" if st.session_state.sort_mode == 'asset' else "secondary"): st.session_state.sort_mode = 'asset'; st.rerun()
with b3:
    if st.button("📊 평가손익 [ " + ("●" if st.session_state.sort_mode == 'profit' else "○") + " ]", type="primary" if st.session_state.sort_mode == 'profit' else "secondary"): st.session_state.sort_mode = 'profit'; st.rerun()
with b4:
    if st.button("📈 손익률 [ " + ("●" if st.session_state.sort_mode == 'rate' else "○") + " ]", type="primary" if st.session_state.sort_mode == 'rate' else "secondary"): st.session_state.sort_mode = 'rate'; st.rerun()
with b5:
    if st.button("💻 종목코드 [ " + ("+" if st.session_state.show_code else "-") + " ]", type="primary" if st.session_state.show_code else "secondary"): st.session_state.show_code = not st.session_state.show_code; st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
t3_lbl = {'DC':'퇴직연금(DC)계좌 / (삼성증권 7165962472-28)', 'PENSION':'연금저축(CMA)계좌 / (삼성증권 7169434836-15)', 'ISA':'ISA(중개형)계좌 / (키움증권 6448-4934)', 'IRP':'퇴직연금(IRP)계좌 / (삼성증권 7164499007-29)'}
for k in FIXED_ACCOUNT_ORDER:
    if k in data:
        a = data[k]
        with st.expander(f"📂 [ {t3_lbl.get(k, a.get('label', ''))} ] 종목별 현황", expanded=False):
            s_data = next((i for i in a.get('상세', []) if i.get('종목명') == "[ 합계 ]"), {})
            safe_pct = sum(item.get('비중', 0) for item in a.get('상세', []) if (k == 'DC' and item.get('종목명') in ['삼성화재 퇴직연금(3.05%/年)', '현금성자산']) or (k == 'IRP' and item.get('종목명') == '현금성자산'))
            st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(a.get('총 자산', 0))}</span> / 총 손익 : <span class='summary-val {col(s_data.get('평가손익', 0))}'>{fmt(s_data.get('평가손익', 0), True)} ({fmt_p(s_data.get('수익률(%)', 0))})</span></div><div style='font-size:14.5px; font-weight:normal; color:#555;'>[ 위험자산 : {100.0-safe_pct:.1f}% | 안전자산 : {safe_pct:.1f}% ]</div></div>", unsafe_allow_html=True)
            h3 = [unit_html, f"<table class='main-table'><tr><th>종목명</th>{'<th>종목코드</th>' if st.session_state.show_code else ''}<th>비중</th><th>총 자산</th><th>평가손익</th><th>손익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>"]
            items = [i for i in a.get('상세', []) if i.get('종목명') != "[ 합계 ]"]
            if st.session_state.sort_mode == 'asset': items.sort(key=lambda x: x.get('총 자산', 0), reverse=True)
            elif st.session_state.sort_mode == 'profit': items.sort(key=lambda x: x.get('평가손익', 0), reverse=True)
            elif st.session_state.sort_mode == 'rate': items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
            for i in ([s_data] + items):
                is_s = (i.get('종목명') == "[ 합계 ]"); r = f"<tr class='sum-row'>" if is_s else "<tr>"
                h3.append(r + f"<td>{i.get('종목명', '')}</td>" + (f"<td>{'-' if is_s or i.get('코드','-')=='-' else i.get('코드', '')}</td>" if st.session_state.show_code else "") + f"<td>{i.get('비중',0):.1f}%</td><td>{fmt(i.get('총 자산', 0))}</td><td class='{col(i.get('평가손익',0))}'>{fmt(i.get('평가손익',0), True)}</td><td class='{col(i.get('수익률(%)', 0))}'>{fmt_p(i.get('수익률(%)', 0))}</td><td>{fmt(i.get('수량','-'))}</td><td>{fmt(i.get('매입가','-'))}</td><td>{fmt(i.get('현재가','-'))}</td></tr>")
            h3.append("</table>"); st.markdown("".join(h3), unsafe_allow_html=True)
