import streamlit as st
import json
import warnings
import andy_pension_v2
import andy_general_v1
import os
import re

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="ZAPPA Asset Dashboard")

# =========================================================
# [ZAPPA] 전용 디자인 시스템 (CSS)
# =========================================================
css = """
<style>
/* 🔥 Streamlit 내부 컨테이너까지 스무스 스크롤 강제 적용 */
* {
    scroll-behavior: smooth !important;
}
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"], .main {
    scroll-behavior: smooth !important;
}

.block-container {
    padding-top: 3rem !important;
    padding-bottom: 7rem !important;
}
h3 {
    font-size: 26px !important;
    font-weight: bold;
    margin-bottom: -10px;
    padding-bottom: 0px;
}
.sub-title {
    font-size: 22px !important;
    font-weight: bold;
    margin: 12px 0 10px;
}
.main-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 15px;
    text-align: center;
    margin-bottom: 10px;
}
.main-table th {
    background-color: #f2f2f2;
    padding: 10px;
    border: 1px solid #ddd;
    font-weight: bold !important;
    vertical-align: middle;
}
.main-table td {
    padding: 8px;
    border: 1px solid #ddd;
    vertical-align: middle;
}
.sum-row td {
    background-color: #fff9e6;
    font-weight: bold !important;
}
.red {
    color: #FF2323 !important;
}
.blue {
    color: #0047EB !important;
}

/* 레이아웃 및 카드 디자인 */
.insight-container {
    display: flex;
    gap: 20px;
    align-items: stretch;
    margin-bottom: 20px;
}
.insight-left {
    flex: 0 0 49%;
    display: flex;
    flex-direction: column;
}
.insight-right {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.card-main {
    background-color: #fffdf2;
    border: 2px solid #e8dbad;
    border-radius: 18px;
    padding: 18px 22px 15px 22px;
    position: relative;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.grid-2x2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 15px;
    height: 100%;
}

/* 서브 카드: 마우스 오버 시 회색 배경 적용 (클릭 유도) */
.card-sub {
    background: #fff;
    border: 1.5px solid #ddd;
    border-radius: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.02);
    display: flex;
    flex-direction: column;
    padding: 10px 15px;
    transition: background-color 0.2s, border-color 0.2s; 
    cursor: pointer; 
    height: 100%;
}
.card-sub:hover {
    background-color: #f2f2f2 !important; 
    border-color: #ccc !important;
}

.insight-bottom-box {
    background: #fff;
    border: 1.5px solid #ddd;
    border-radius: 18px;
    padding: 25px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.02);
    font-size: 15.5px;
    line-height: 1.8;
    color: #333;
    margin-top: 5px;
    margin-bottom: 25px;
}

.summary-text {
    font-size: 16px !important;
    font-weight: bold !important;
    color: #333;
    margin-bottom: 10px;
}
.summary-val {
    font-size: 20px !important;
}

/* 엑셀 스타일 병합 (중첩 테이블 효과용) */
.main-table th.th-eval {
    border-right: none !important;
}
.main-table th.th-blank {
    border-left: none !important;
    border-bottom: none !important;
    padding: 0 !important;
}
.main-table th.th-week {
    border-left: 1px solid #ddd !important;
    border-top: 1px solid #ddd !important;
    font-size: 13.5px;
}

/* 사이드바 폰트 세팅 */
div[role="radiogroup"] label {
    font-size: 15.5px !important;
    margin-bottom: 8px !important;
}

/* =========================================================
   [ZAPPA 플로팅 배너 CSS]
   ========================================================= */
.zappa-icon { font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif !important; font-size: 32px !important; }

div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu),
div[data-testid="column"]:has(span#zappa-floating-menu) {
    position: fixed !important; bottom: 30px !important; right: 30px !important; left: auto !important; transform: none !important;
    width: max-content !important; min-width: 0 !important; background: rgba(255, 255, 255, 0.98) !important; padding: 10px 25px !important; 
    border-radius: 8px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important; border: 1px solid #e5e7eb !important;
    z-index: 999999 !important; display: flex !important; flex-wrap: nowrap !important; align-items: center !important; justify-content: center !important; gap: 4px !important; 
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

# =========================================================
# Session State 초기화
# =========================================================
if 'sort_mode' not in st.session_state: 
    st.session_state.sort_mode = 'init'
if 'show_code' not in st.session_state: 
    st.session_state.show_code = False
if 'show_change_rate' not in st.session_state: 
    st.session_state.show_change_rate = False
if 'gen_sort_mode' not in st.session_state: 
    st.session_state.gen_sort_mode = 'init'
if 'gen_show_change_rate' not in st.session_state: 
    st.session_state.gen_show_change_rate = False
if 'gen_curr' not in st.session_state: 
    st.session_state.gen_curr = 'KRW'
if 'init' not in st.session_state:
    with st.spinner("데이터 업데이트 중..."):
        try:
            andy_pension_v2.generate_asset_data()
        except: pass
    st.session_state['init'] = True
    st.cache_data.clear()

# =========================================================
# Helper Functions
# =========================================================
def fmt(v, sign=False, decimal=0):
    try:
        if decimal > 0: return f"{float(v):,.{decimal}f}"
        val = int(float(v))
        if sign and val > 0: return f"+{val:,}"
        return f"{val:,}"
    except: 
        return str(v)

def fmt_p(v):
    try:
        val = float(v)
        return f"▲{val:.2f}%" if val > 0 else (f"▼{abs(val):.2f}%" if val < 0 else "0.00%")
    except: 
        return str(v)

def col(v):
    try:
        val = float(v)
        return "red" if val > 0 else ("blue" if val < 0 else "")
    except: 
        return ""

def clean_label(lbl):
    return re.sub(r'\s*\(\d{2}\.\d+월\)', '', lbl)

def short_name(nm):
    return nm[:13] + "***" if len(nm) > 13 else nm

# =========================================================
# Data Load
# =========================================================
@st.cache_data(ttl=60)
def load():
    try:
        with open('assets.json', 'r', encoding='utf-8') as f: 
            return json.load(f)
    except: 
        return {}

@st.cache_data(ttl=60)
def load_gen():
    try:
        with open('assets_general.json', 'r', encoding='utf-8') as f: 
            return json.load(f)
    except: 
        return {}

data = load()
tot = data.get("_total", {})

# =========================================================
# 📍 Left Sidebar Navigation
# =========================================================
with st.sidebar:
    st.markdown(
        "<div style='display:flex; align-items:center; gap:10px; margin-bottom:20px;'>"
        "<span class='zappa-icon'>🤖</span>"
        "<span style='font-size:24px; font-weight:bold; color:#111;'>ZAPPA MENU</span>"
        "</div>", 
        unsafe_allow_html=True
    )
    
    menu = st.radio(
        "카테고리 선택", 
        ("1. 복합 대시보드", "2. 절세 계좌", "3. 일반 계좌", "4. Quant 매매", "5. 가상자산"), 
        index=1, 
        label_visibility="collapsed"
    )
    
    st.markdown("<hr style='margin:25px 0 20px 0; border: none; border-top: 1px dashed #ccc;'>", unsafe_allow_html=True)
    
    t_asset_all = tot.get('총 자산', 0)
    t_profit_all = tot.get('총 수익', 0)
    t_rate_all = tot.get('수익률(%)', 0)
    
    quick_view_html = f"""
    <div style='background-color: #f8f9fa; border-radius: 12px; padding: 18px 15px; border: 1px solid #eaeaea;'>
        <div style='font-size:13.5px; font-weight:bold; color:#777; margin-bottom:8px;'>⚡ 퀵 뷰 (전체 자산 현황)</div>
        <div style='font-size:24px; font-weight:600; color:#111; letter-spacing:-0.5px; line-height: 1.1;'>
            {fmt(t_asset_all)}<span style='font-size:13.5px; font-weight:normal; margin-left:3px; letter-spacing:normal;'>KRW</span>
        </div>
        <div style='font-size:14px; margin-top:8px; color:#555;'>
            총 손익: <span class='{col(t_profit_all)}' style='font-weight:bold;'>{fmt(t_profit_all, True)}</span> ({fmt_p(t_rate_all)})
        </div>
    </div>
    """
    st.markdown(quick_view_html, unsafe_allow_html=True)

# =========================================================
# 🔀 Main Content Routing
# =========================================================
if menu == "1. 복합 대시보드":
    st.markdown("<h3 style='margin-top: 5px;'>📊 복합 대시보드 (Executive Summary)</h3>", unsafe_allow_html=True)
    st.info("💡 Andy님의 전체 자산을 통합 분석하는 Executive Summary 뷰가 구축될 예정입니다.")
elif menu == "4. Quant 매매":
    st.markdown("<h3 style='margin-top: 5px;'>🤖 Quant 매매 (ZAPPA Bot)</h3>", unsafe_allow_html=True)
    st.info("💡 ZAPPA 단기/퀀트 트레이딩 봇의 실시간 매매 현황 및 알고리즘 성과를 모니터링하는 화면입니다.")
elif menu == "5. 가상자산":
    st.markdown("<h3 style='margin-top: 5px;'>🪙 가상자산 (Crypto)</h3>", unsafe_allow_html=True)
    st.info("💡 비트코인 등 가상자산 포트폴리오 모니터링 화면이 구축될 예정입니다.")
    # =========================================================
# [ 2. 절세 계좌 대시보드 ]
# =========================================================
elif menu == "2. 절세 계좌":
    
    c1, c2 = st.columns([8.5, 1.5])
    with c1: 
        st.markdown("<h3 style='margin-top: 5px;'>🚀 이상혁(Andy lee)님 [절세계좌] 통합 대시보드</h3>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 업데이트", use_container_width=True):
            with st.spinner("데이터 업데이트 중..."):
                try: andy_pension_v2.generate_asset_data()
                except: pass
            st.cache_data.clear()
            st.rerun()

    st.markdown(f"<div style='text-align:right;font-size:14.5px;color:#555;font-weight:normal;margin:-10px 0 15px;'>[ {tot.get('조회시간', '업데이트 필요')} ]</div>", unsafe_allow_html=True)

    FIXED_ACCOUNT_ORDER = ['DC', 'IRP', 'PENSION', 'ISA']
    OPEN_DATES = {'DC': '[ 2025.08 ]', 'IRP': '[ 2025.08 ]', 'PENSION': '[ 2025.11 ]', 'ISA': '[ 2025.08 ]'}

    if data and "_insight" in data:
        t_asset = tot.get('총 자산', 0)
        t_profit = tot.get('총 수익', 0)
        t_diff = tot.get('평가손익(1일전)', 0)
        t_diff_7 = tot.get('평가손익(7일전)', 0)
        t_rate = tot.get('수익률(%)', 0)
        t_original_sum = tot.get('원금합', 0)
        
        cash_total = 0
        ovs_total = 0
        dom_total = 0
        all_items = []
        
        for k in FIXED_ACCOUNT_ORDER:
            if k in data:
                short_acc_name = 'DC' if k == 'DC' else ('IRP' if k == 'IRP' else ('CMA' if k == 'PENSION' else 'ISA'))
                for item in data[k].get('상세', []):
                    if item.get('종목명') == '[ 합계 ]': 
                        continue
                    it_copy = item.copy()
                    it_copy['계좌'] = short_acc_name
                    all_items.append(it_copy)
                    val = item.get('총 자산', 0)
                    nm = item.get('종목명', '').lower()
                    if any(kw in nm for kw in ['현금성자산', 'mmf']): 
                        cash_total += val
                    elif any(kw in nm for kw in ['tiger', 's&p', '나스닥', '필라델피아', '다우존스', 'ai테크']): 
                        ovs_total += val
                    else: 
                        dom_total += val

        exclude_kws = ["현금성자산", "삼성화재", "삼성신종종류형"]
        tradeable_items = [it for it in all_items if not any(kw in it.get("종목명", "") for kw in exclude_kws)]
        tradeable_items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
        
        best_5 = tradeable_items[:5]
        worst_5 = tradeable_items[::-1][:5]

        tradeable_items_by_day = sorted(tradeable_items, key=lambda x: float(x.get('전일비', x.get('전일비(%)', 0))), reverse=True)
        rise_cnt = sum(1 for it in tradeable_items_by_day if float(it.get('전일비', it.get('전일비(%)', 0))) > 0.2)
        fall_cnt = sum(1 for it in tradeable_items_by_day if float(it.get('전일비', it.get('전일비(%)', 0))) < -0.2)
        flat_cnt = len(tradeable_items_by_day) - rise_cnt - fall_cnt
        
        rise_list = []
        for it in tradeable_items_by_day:
            d_rate = float(it.get('전일비', it.get('전일비(%)', 0.0)))
            if d_rate > 0.2:
                nm = short_name(it.get('종목명', ''))
                acc = it.get('계좌', '')
                rise_list.append(f"{nm}({acc} <span class='{col(d_rate)}'>{fmt_p(d_rate)}</span>)")
                
        fall_list = []
        for it in tradeable_items_by_day[::-1]:
            d_rate = float(it.get('전일비', it.get('전일비(%)', 0.0)))
            if d_rate < -0.2:
                nm = short_name(it.get('종목명', ''))
                acc = it.get('계좌', '')
                fall_list.append(f"{nm}({acc} <span class='{col(d_rate)}'>{fmt_p(d_rate)}</span>)")
        
        top5_rise = rise_list[:5]
        top3_fall = fall_list[:3]
        
        str_rise = ", ".join(top5_rise) + " 등" if top5_rise else "없음"
        str_fall = ", ".join(top3_fall) + " 등" if top3_fall else "없음"

        p_cash = (cash_total / t_asset * 100) if t_asset > 0 else 0
        p_ovs = (ovs_total / t_asset * 100) if t_asset > 0 else 0
        p_dom = (dom_total / t_asset * 100) if t_asset > 0 else 0

        a_dc = data.get('DC', {}).get('총 자산', 0)
        a_irp = data.get('IRP', {}).get('총 자산', 0)
        a_pension = data.get('PENSION', {}).get('총 자산', 0)
        a_isa = data.get('ISA', {}).get('총 자산', 0)
        
        total_for_bar = max(1, a_dc + a_irp + a_pension + a_isa)
        p_dc = a_dc / total_for_bar * 100
        p_irp = a_irp / total_for_bar * 100
        p_pension = a_pension / total_for_bar * 100
        p_isa = a_isa / total_for_bar * 100
        
        goal_amount = 1000000000
        progress_pct = (t_asset / goal_amount) * 100 if goal_amount > 0 else 0

        def render_bar(p, color):
            return f"<div style='width: {p}%; background-color: {color}; height: 100%; display: flex; align-items: center; justify-content: center; position: relative;'><span style='position: absolute; font-size: 13px; color: #333; z-index: 10; white-space: nowrap;'>{p:.0f}%</span></div>" if p > 0 else ""

        acc_rates = []
        for k in FIXED_ACCOUNT_ORDER:
            if k in data:
                acc_nm = '퇴직연금(DC)' if k == 'DC' else ('퇴직연금(IRP)' if k == 'IRP' else ('연금저축(CMA)' if k == 'PENSION' else 'ISA(중개형)'))
                acc_rates.append((acc_nm, data[k].get('수익률(%)', 0)))
        acc_rates.sort(key=lambda x: x[1], reverse=True)
        best_acc_name = acc_rates[0][0] if acc_rates else "전체"
        best_acc_rate = acc_rates[0][1] if acc_rates else 0

        b1_name = short_name(best_5[0]['종목명']) if best_5 else "주도 종목"
        w1_name = short_name(worst_5[0]['종목명']) if worst_5 else "부진 종목"

        strategy_text = f"간밤 최근 미국 KCE/PCE 물가 지표의 끈적한 흐름과 연준(Fed)의 금리 인하 신중론이 겹치며 변동성이 부각되었습니다. 단기적으로 아웃퍼폼 중인 <strong>{b1_name}</strong> 등에서 일부 차익을 실현하여 현재 <strong>{p_cash:.1f}% 수준인 현금 비중을 선제적으로 확대</strong>할 필요가 있습니다. 향후 빅테크 실적 불확실성이 소화되는 변곡점에서 낙폭 과대 우량주로의 스위칭 리밸런싱을 권고합니다."
        
        zappa_html = f"<div style='font-size: 14.5px; line-height: 1.85; color: #444; padding-left: 0px;'>"
        t_style = "color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;"
        bullet = "<span style='font-size:11px;'>🔵</span>"

        zappa_html += f"<div style='margin-bottom: 22px;'><span style='{t_style}'>{bullet} 계좌 현황 및 종목 분석</span><div>"
        zappa_html += f"현재 <strong>{best_acc_name} 계좌가 전체 수익률(<span class='{col(best_acc_rate)}' style='font-weight:bold;'>{fmt_p(best_acc_rate)}</span>) 1위</strong>를 기록하며 하방을 견인 중입니다. 개별 종목에서는 <strong>{b1_name}</strong>가 시장 트렌드를 주도하며 효자 역할을 수행 중이나, <strong>{w1_name}</strong> 등 일부 섹터는 외부 매크로 요인에 의해 단기 조정을 겪고 있습니다. "
        zappa_html += f"총 <strong>{len(tradeable_items)}개</strong> 종목 중 전일비 상승종목은 <strong>{rise_cnt}개</strong>, 하락종목은 <strong>{fall_cnt}개</strong>, 보합종목은 <strong>{flat_cnt}개</strong> 입니다.<br>"
        zappa_html += f"<span style='font-size:13.5px; color:#555;'>※ 상승종목 : {str_rise}<br>"
        zappa_html += f"※ 하락종목 : {str_fall}</span>"
        zappa_html += "</div></div>"
        zappa_html += f"<div style='margin-bottom: 0px;'><span style='{t_style}'>{bullet} 주식 시황 및 향후 대응 전략</span><div>{strategy_text}</div></div>"
        zappa_html += "</div>"

        st.markdown("<div class='sub-title' style='margin-bottom: 15px;'>💡 ZAPPA의 [절세계좌] 자산 현황 보고</div>", unsafe_allow_html=True)

        donut_css = f"background: conic-gradient(#ffffff 0% {p_cash}%, #d9d9d9 {p_cash}% {p_cash+p_ovs}%, #8c8c8c {p_cash+p_ovs}% 100%);"
        
        donut_html = f"""
        <div style='position: relative; width: 120px; height: 120px; border-radius: 50%; {donut_css} box-shadow: inset 0 0 8px rgba(0,0,0,0.1); border: 1px solid #d0d0d0; flex-shrink: 0; margin: 0 auto;'>
            <div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 35%; height: 35%; background-color: #fffdf2; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.05);'></div>
            <div style='position: absolute; top: 2%; left: 50%; transform: translateX(-50%); font-size: 11.5px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_cash:.0f}%<br>현금성자산</div>
            <div style='position: absolute; top: 28%; right: -7%; font-size: 11.5px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_ovs:.0f}%<br>해외투자</div>
            <div style='position: absolute; bottom: 9%; left: 20%; font-size: 12px; color: #fff; font-weight: bold; text-align: center; line-height: 1.1; text-shadow: 0px 0px 3px rgba(0,0,0,0.5);'>{p_dom:.0f}%<br>국내투자</div>
        </div>
        """

        html_parts = []
        html_parts.append("<div style='text-align: right; font-size: 13px; color: #555; font-weight: bold; margin-bottom: 5px;'>단위 : 원화(KRW)</div>")
        html_parts.append("<div class='insight-container'>")
        
        html_parts.append("<div class='insight-left'>")
        html_parts.append("  <div class='card-main'>")
        
        html_parts.append("    <div style='display: flex; gap: 15px; align-items: stretch; margin-bottom: auto;'>")
        
        html_parts.append("      <div style='flex: 0 0 38%; display: flex; flex-direction: column;'>")
        html_parts.append("        <div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 15px;'>총 자산</div>")
        html_parts.append(donut_html)
        html_parts.append("      </div>")
        
        html_parts.append("      <div style='flex: 1; display: flex; flex-direction: column; justify-content: flex-start; padding-top: 5px;'>")
        
        html_parts.append("        <div style='background-color: #ffffff; border: 1.5px solid #dcdcdc; border-radius: 8px; padding: 10px 12px; text-align: right; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 16px;'>")
        html_parts.append(f"          <div style='font-size: 24px; font-weight: 700 !important; color: #111; letter-spacing: normal; line-height: 1; margin-bottom: 6px;'>{fmt(t_asset)}<span style='font-size: 13.5px; font-weight: normal; margin-left: 3px; letter-spacing: normal;'>KRW</span></div>")
        html_parts.append(f"          <div style='font-size: 13.5px; color: #777; font-weight: normal; line-height: 1;'>[ 전일비 <span class='{col(t_diff)}'>{fmt(t_diff, True)}</span> / 전주비 <span class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</span> ]</div>")
        html_parts.append("        </div>")
        
        # 🔥 [수정] 위쪽 박스와의 간격을 늘리고, 행간도 시원하게 펼침 (상하 밸런스 패치)
        html_parts.append("        <div style='display: grid; grid-template-columns: auto auto; row-gap: 8px; column-gap: 30px; justify-content: end; align-items: baseline; width: 100%; padding-right: 12px; margin-top: 25px;'>")
        html_parts.append("          <div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>평가금액</div>")
        html_parts.append(f"          <div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(t_asset - cash_total)}</div>")
        html_parts.append("          <div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>현금성자산</div>")
        html_parts.append(f"          <div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(cash_total)}</div>")
        html_parts.append("          <div style='color: #777; font-size: 14px; font-weight: normal; text-align: right; line-height: 20px;'>총 손익</div>")
        html_parts.append("          <div style='text-align: right;'>")
        html_parts.append(f"            <div style='font-size: 18px; font-weight: 600; line-height: 1;' class='{col(t_profit)}'>{fmt(t_profit, True)}</div>")
        html_parts.append(f"            <div style='font-size: 13.5px; font-weight: 600; margin-top: 3px; line-height: 1;' class='{col(t_rate)}'>{fmt_p(t_rate)}</div>")
        html_parts.append("          </div>")
        html_parts.append("        </div>")
        html_parts.append("      </div>")
        
        html_parts.append("    </div>") 

        html_parts.append("    <div style='margin-top: 20px;'>")
        html_parts.append("      <div style='display: flex; height: 20px; width: 100%; border-radius: 4px; border: 1px solid #ccc; margin-bottom: 6px; overflow: hidden;'>")
        html_parts.append(f"        {render_bar(p_dc, '#b4a7d6')}")
        html_parts.append(f"        {render_bar(p_irp, '#f4b183')}")
        html_parts.append(f"        {render_bar(p_pension, '#a9d18e')}")
        html_parts.append(f"        {render_bar(p_isa, '#ffd966')}")
        html_parts.append("      </div>")
        
        html_parts.append("      <div style='display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #777; padding: 0 2px; margin-bottom: 16px;'>")
        html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#b4a7d6;'></div>퇴직연금(DC)</div>")
        html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#f4b183;'></div>퇴직연금(IRP)</div>")
        html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#a9d18e;'></div>연금저축(CMA)</div>")
        html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#ffd966;'></div>ISA(중개형)</div>")
        html_parts.append("      </div>")
        
        html_parts.append("      <div style='padding: 10px 15px; background: rgba(255,255,255,0.5); border-radius: 10px; border: 1px solid #e8dbad;'>")
        html_parts.append("        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>")
        html_parts.append("          <span style='font-size: 14px; color: #777; font-weight: normal;'>🎯 은퇴 자산 목표 10억</span>")
        html_parts.append(f"         <div style='text-align: right;'><span style='font-size: 13px; color: #888; font-weight: normal; margin-right: 6px;'>* 원금 : {fmt(t_original_sum)} / </span><span style='font-size: 14px; font-weight: bold; color: #4a90e2;'>{progress_pct:.1f}%</span></div>")
        html_parts.append("        </div>")
        html_parts.append("        <div style='width: 100%; height: 6px; background-color: #e2e2e2; border-radius: 3px; overflow: hidden;'>")
        html_parts.append(f"          <div style='width: {progress_pct}%; height: 100%; background: linear-gradient(90deg, #9bc2e6, #4a90e2);'></div>")
        html_parts.append("        </div>")
        html_parts.append("      </div>")
        html_parts.append("    </div>") 
        html_parts.append("  </div>") 
        html_parts.append("</div>") 
        
        # [2] 서브 카드 4개 (Right)
        html_parts.append("<div class='insight-right'>")
        html_parts.append("  <div class='grid-2x2'>")
        
        for k in FIXED_ACCOUNT_ORDER:
            if k in data:
                a = data[k]
                acc_name = '퇴직연금(DC)' if k == 'DC' else ('퇴직연금(IRP)' if k == 'IRP' else ('연금저축(CMA)' if k == 'PENSION' else 'ISA(중개형)'))
                acc_asset = a.get('총 자산', 0)
                acc_principal = a.get('원금', 0)
                acc_profit = a.get('총 수익', 0)
                acc_rate = a.get('수익률(%)', 0)
                
                acc_items_list = a.get('상세', [])
                valid_items = [i for i in acc_items_list if i.get('종목명') != '[ 합계 ]' and '현금성자산' not in i.get('종목명', '') and '삼성신종종류형' not in i.get('종목명', '')]
                item_count = len(valid_items)
                
                html_parts.append(f"<a href='#account_detail_section' style='text-decoration:none; color:inherit; display:block; height:100%;'>")
                html_parts.append("    <div class='card-sub'>")
                html_parts.append("      <div>")
                html_parts.append(f"        <div style='text-align: right; font-size: 13.5px; color: #666; font-weight: normal; margin-bottom: -2px; line-height: 1;'>{OPEN_DATES.get(k, '')}</div>")
                html_parts.append(f"        <div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 2px;'>{acc_name}</div>")
                html_parts.append("        <div style='border-bottom: 1px solid #eee; margin-bottom: 6px; margin-top: 2px;'></div>")
                html_parts.append(f"        <div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 자산</span><span style='font-size: 16px; color: #111; font-weight: normal;'>{fmt(acc_asset)}</span></div>")
                html_parts.append(f"        <div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 손익</span><div style='text-align: right; line-height: 1.2;'><div class='{col(acc_profit)}' style='font-size: 16px; font-weight: normal;'>{fmt(acc_profit, True)}</div><div class='{col(acc_rate)}' style='font-size: 14px; font-weight: normal; margin-top: 1px;'>{fmt_p(acc_rate)}</div></div></div>")
                html_parts.append("      </div>")
                html_parts.append(f"      <div style='font-size: 13.5px; color: #666; font-weight: normal; margin-top: auto; padding-top: 2px; display: flex; justify-content: space-between; align-items: baseline;'><span>* 원금 : {fmt(acc_principal)}</span><span><span style='font-size: 16px; font-weight: bold; color: #111;'>{item_count}</span> 종목</span></div>")
                html_parts.append("    </div>")
                html_parts.append("</a>")
                
        html_parts.append("  </div>") 
        html_parts.append("</div>") 
        html_parts.append("</div>") 
        
        # [3] 인사이트 박스
        html_parts.append("<div class='insight-bottom-box' style='display: flex; gap: 20px; align-items: stretch;'>")
        
        html_parts.append("  <div style='flex: 1; padding-right: 15px; border-right: 1px solid #eaeaea;'>")
        html_parts.append("    <div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 8px; letter-spacing: normal;'>📈 손익률 우수종목</div>")
        html_parts.append("    <table class='main-table' style='margin-bottom: 20px; font-size: 13.5px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>계좌</th></tr>")
        
        for idx, it in enumerate(best_5):
            rt = it.get('수익률(%)', 0)
            pf = it.get('평가손익', 0)
            s_nm = short_name(it.get('종목명', ''))
            html_parts.append(f"    <tr><td>{idx+1}</td><td>{s_nm}</td><td class='{col(rt)}'>{fmt_p(rt)}</td><td class='{col(pf)}'>{fmt(pf, True)}</td><td>{it.get('계좌','')}</td></tr>")
        html_parts.append("    </table>")
        
        html_parts.append("    <div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px; letter-spacing: normal;'>📉 손익률 부진종목</div>")
        html_parts.append("    <table class='main-table' style='margin-bottom: 0px; font-size: 13.5px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>계좌</th></tr>")
        
        for idx, it in enumerate(worst_5):
            rt = it.get('수익률(%)', 0)
            pf = it.get('평가손익', 0)
            s_nm = short_name(it.get('종목명', ''))
            html_parts.append(f"    <tr><td>{idx+1}</td><td>{s_nm}</td><td class='{col(rt)}'>{fmt_p(rt)}</td><td class='{col(pf)}'>{fmt(pf, True)}</td><td>{it.get('계좌','')}</td></tr>")
        html_parts.append("    </table>")
        html_parts.append("  </div>")
        
        html_parts.append("  <div style='flex: 1.1; padding-left: 5px;'>")
        html_parts.append("    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 8px;'>")
        html_parts.append("      <div style='font-size: 18px; font-weight: bold; color: #111; letter-spacing: normal;'>💡 시황 및 향후 전망</div>")
        html_parts.append("      <div style='font-size: 13.5px; color: #888;'>[ -0.2%p &lt; 횡보 &lt; +0.2%p ]</div>")
        html_parts.append("    </div>")
        html_parts.append(f"    {zappa_html}")
        html_parts.append("  </div>")
        
        html_parts.append("</div>") 
        
        html_str = "".join(html_parts)
        st.markdown(html_str, unsafe_allow_html=True)

        # =====================================================================
        # 하단 상세 데이터 테이블 섹션
        # =====================================================================
        unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"

        st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총자산 : <span class='summary-val'>{fmt(t_asset)}</span> / 총 손익 : <span class='summary-val {col(t_profit)}'>{fmt(t_profit, True)} ({fmt_p(t_rate)})</span></div></div>", unsafe_allow_html=True)

        h1_table = """
        <table class='main-table'>
            <tr>
                <th rowspan='2'>계좌 구분</th>
                <th rowspan='2'>총 자산</th>
                <th rowspan='2' class='th-eval'>평가손익</th>
                <th colspan='3' class='th-blank'>&nbsp;</th>
                <th rowspan='2'>손익률</th>
                <th rowspan='2'>투자원금</th>
            </tr>
            <tr>
                <th class='th-week'>7일전</th>
                <th class='th-week'>15일전</th>
                <th class='th-week'>30일전</th>
            </tr>
        """
        h1_table = re.sub(r'\n\s*', '', h1_table)

        h1 = [unit_html, h1_table]
        h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(t_asset)}</td><td class='{col(t_profit)}'>{fmt(t_profit, True)}</td><td class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</td><td class='{col(tot.get('평가손익(15일전)', 0))}'>{fmt(tot.get('평가손익(15일전)', 0), True)}</td><td class='{col(tot.get('평가손익(30일전)', 0))}'>{fmt(tot.get('평가손익(30일전)', 0), True)}</td><td class='{col(t_rate)}'>{fmt_p(t_rate)}</td><td>{fmt(t_original_sum)}</td></tr>")

        keys_1 = [k for k in FIXED_ACCOUNT_ORDER if k in data]
        if st.session_state.sort_mode == 'asset': 
            keys_1.sort(key=lambda k: data.get(k, {}).get('총 자산', 0), reverse=True)
        elif st.session_state.sort_mode == 'profit': 
            keys_1.sort(key=lambda k: data.get(k, {}).get('총 수익', 0), reverse=True)
        elif st.session_state.sort_mode == 'rate': 
            keys_1.sort(key=lambda k: data.get(k, {}).get('수익률(%)', 0), reverse=True)

        for k in keys_1:
            a = data.get(k, {})
            h1.append(f"<tr><td>{clean_label(a.get('label', ''))}</td><td>{fmt(a.get('총 자산',0))}</td><td class='{col(a.get('총 수익',0))}'>{fmt(a.get('총 수익',0), True)}</td><td class='{col(a.get('평가손익(7일전)',0))}'>{fmt(a.get('평가손익(7일전)',0), True)}</td><td class='{col(a.get('평가손익(15일전)',0))}'>{fmt(a.get('평가손익(15일전)',0), True)}</td><td class='{col(a.get('평가손익(30일전)',0))}'>{fmt(a.get('평가손익(30일전)',0), True)}</td><td class='{col(a.get('수익률(%)',0))}'>{fmt_p(a.get('수익률(%)',0))}</td><td>{fmt(a.get('원금',0))}</td></tr>")

        h1.append("</table>")
        st.markdown("".join(h1), unsafe_allow_html=True)

        ag_tot = t_asset - tot.get('매입금액합', 0)
        ay_tot = (ag_tot / tot.get('매입금액합', 1) * 100) if tot.get('매입금액합', 1) > 0 else 0

        st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-text'>● 총자산 : <span class='summary-val'>{fmt(t_asset)}</span> / 총 손익 : <span class='summary-val {col(ag_tot)}'>{fmt(ag_tot, True)} ({fmt_p(ay_tot)})</span></div>", unsafe_allow_html=True)

        h2_table = """
        <table class='main-table'>
            <tr>
                <th rowspan='2'>계좌 구분</th>
                <th rowspan='2'>총 자산</th>
                <th rowspan='2' class='th-eval'>평가손익</th>
                <th colspan='3' class='th-blank'>&nbsp;</th>
                <th rowspan='2'>손익률</th>
                <th rowspan='2'>매입금액</th>
            </tr>
            <tr>
                <th class='th-week'>전일비</th>
                <th class='th-week'>전주비</th>
                <th class='th-week'>전월비</th>
            </tr>
        """
        h2_table = re.sub(r'\n\s*', '', h2_table)

        h2 = [unit_html, h2_table]
        h2.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(t_asset)}</td><td class='{col(ag_tot)}'>{fmt(ag_tot, True)}</td><td class='{col(t_diff)}'>{fmt(t_diff, True)}</td><td class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</td><td class='{col(tot.get('평가손익(30일전)', 0))}'>{fmt(tot.get('평가손익(30일전)', 0), True)}</td><td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td><td>{fmt(tot.get('매입금액합', 0))}</td></tr>")

        sec2_items = []
        for k in FIXED_ACCOUNT_ORDER:
            if k in data:
                a = data.get(k, {})
                ag_acc = sum(i.get('평가손익', 0) for i in a.get('상세', []) if i.get('종목명') != '[ 합계 ]')
                curr_asset = a.get('총 자산', 0)
                ap_acc = curr_asset - ag_acc
                ay_acc = (ag_acc / ap_acc * 100) if ap_acc > 0 else 0
                sec2_items.append({'k': k, 'a': a, 'ag_acc': ag_acc, 'ap_acc': ap_acc, 'ay_acc': ay_acc, 'curr_asset': curr_asset})

        if st.session_state.sort_mode == 'asset': 
            sec2_items.sort(key=lambda x: x['curr_asset'], reverse=True)
        elif st.session_state.sort_mode == 'profit': 
            sec2_items.sort(key=lambda x: x['ag_acc'], reverse=True)
        elif st.session_state.sort_mode == 'rate': 
            sec2_items.sort(key=lambda x: x['ay_acc'], reverse=True)

        for item in sec2_items:
            a = item['a']
            h2.append(f"<tr><td>{clean_label(a.get('label', ''))}</td><td>{fmt(item['curr_asset'])}</td><td class='{col(item['ag_acc'])}'>{fmt(item['ag_acc'], True)}</td><td class='{col(a.get('평가손익(1일전)',0))}'>{fmt(a.get('평가손익(1일전)',0), True)}</td><td class='{col(a.get('평가손익(7일전)',0))}'>{fmt(a.get('평가손익(7일전)',0), True)}</td><td class='{col(a.get('평가손익(30일전)',0))}'>{fmt(a.get('평가손익(30일전)',0), True)}</td><td class='{col(item['ay_acc'])}'>{fmt_p(item['ay_acc'])}</td><td>{fmt(item['ap_acc'])}</td></tr>")

        h2.append("</table>")
        st.markdown("".join(h2), unsafe_allow_html=True)

        st.markdown("<div id='account_detail_section' style='padding-top: 20px; margin-top: -20px;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
        
        # 🔥 [수정] 플로팅 배너 아이콘 기능별 분리 적용 (상태 토글 vs 정렬 방향)
        b1, b2, b3, b4, b5, b6 = st.columns(6)
        with b1:
            st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
            if st.button("🛠️ 초기화 [ ● ]" if st.session_state.sort_mode == 'init' else "🛠️ 초기화 [ ○ ]", type="primary" if st.session_state.sort_mode == 'init' else "secondary", on_click=lambda: setattr(st.session_state, 'sort_mode', 'init')): pass
        with b2:
            if st.button("💰 총자산 [ ▼ ]" if st.session_state.sort_mode == 'asset' else "💰 총자산 [ ▽ ]", type="primary" if st.session_state.sort_mode == 'asset' else "secondary", on_click=lambda: setattr(st.session_state, 'sort_mode', 'asset')): pass
        with b3:
            if st.button("📊 평가손익 [ ▼ ]" if st.session_state.sort_mode == 'profit' else "📊 평가손익 [ ▽ ]", type="primary" if st.session_state.sort_mode == 'profit' else "secondary", on_click=lambda: setattr(st.session_state, 'sort_mode', 'profit')): pass
        with b4:
            if st.button("📈 손익률 [ ▼ ]" if st.session_state.sort_mode == 'rate' else "📈 손익률 [ ▽ ]", type="primary" if st.session_state.sort_mode == 'rate' else "secondary", on_click=lambda: setattr(st.session_state, 'sort_mode', 'rate')): pass
        with b5:
            if st.button("↕️ 등락률 [ + ]" if st.session_state.show_change_rate else "↕️ 등락률 [ - ]", type="primary" if st.session_state.show_change_rate else "secondary", on_click=lambda: setattr(st.session_state, 'show_change_rate', not st.session_state.show_change_rate)): pass
        with b6:
            if st.button("💻 종목코드 [ + ]" if st.session_state.show_code else "💻 종목코드 [ - ]", type="primary" if st.session_state.show_code else "secondary", on_click=lambda: setattr(st.session_state, 'show_code', not st.session_state.show_code)): pass

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
                
                curr_asset = a.get('총 자산', 0)
                a_prof = s_data.get('평가손익', 0)
                a_rate = s_data.get('수익률(%)', 0)
                
                st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총자산 : <span class='summary-val'>{fmt(curr_asset)}</span> / 총 손익 : <span class='summary-val {col(a_prof)}'>{fmt(a_prof, True)} ({fmt_p(a_rate)})</span></div>{extra_info_html}</div>", unsafe_allow_html=True)
                
                if st.session_state.show_change_rate:
                    code_th = "<th rowspan='2'>종목코드</th>" if st.session_state.show_code else ""
                    h3_table_html = f"""
                    <table class='main-table'>
                        <tr>
                            <th rowspan='2'>종목명</th>
                            {code_th}
                            <th rowspan='2'>비중</th>
                            <th rowspan='2'>총 자산</th>
                            <th rowspan='2'>평가손익</th>
                            <th rowspan='2'>손익률</th>
                            <th rowspan='2'>주식수</th>
                            <th rowspan='2'>매입가</th>
                            <th rowspan='2' class='th-eval'>현재가</th>
                            <th class='th-blank'>&nbsp;</th>
                        </tr>
                        <tr>
                            <th class='th-week'>등락률</th>
                        </tr>
                    """
                    h3_table = re.sub(r'\n\s*', '', h3_table_html)
                else:
                    code_th = "<th>종목코드</th>" if st.session_state.show_code else ""
                    h3_table = f"<table class='main-table'><tr><th>종목명</th>{code_th}<th>비중</th><th>총 자산</th><th>평가손익</th><th>손익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>"
                
                h3 = [unit_html, h3_table]
                items = [i for i in a.get('상세', []) if i.get('종목명') != "[ 합계 ]"]
                
                if st.session_state.sort_mode == 'asset': 
                    items.sort(key=lambda x: x.get('총 자산', 0), reverse=True)
                elif st.session_state.sort_mode == 'profit': 
                    items.sort(key=lambda x: x.get('평가손익', 0), reverse=True)
                elif st.session_state.sort_mode == 'rate': 
                    items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
                
                for i in ([s_data] + items):
                    is_s = (i.get('종목명') == "[ 합계 ]")
                    row = f"<tr class='sum-row'>" if is_s else "<tr>"
                    row += f"<td>{i.get('종목명', '')}</td>"
                    
                    if st.session_state.show_code:
                        row += f"<td>{'-' if is_s or i.get('코드','-')=='-' else i.get('코드', '')}</td>"
                        
                    item_asset = i.get('총 자산', 0)
                    i_rate = i.get('수익률(%)', 0)
                    
                    d_rate_val = i.get('전일비', i.get('전일비(%)', 0.0))
                    d_rate = float(d_rate_val)
                    
                    try:
                        curr_price = float(str(i.get('현재가', 0)).replace(',', ''))
                    except:
                        curr_price = 0
                        
                    if curr_price > 0 and d_rate != 0:
                        prev_price = curr_price / (1 + d_rate / 100)
                        diff_amt = curr_price - prev_price
                    else:
                        diff_amt = 0
                        
                    diff_amt_str = fmt(diff_amt, True) if diff_amt != 0 else "0"
                    d_rate_str = "-" if is_s else fmt_p(d_rate)
                    d_class = "" if is_s else col(d_rate)
                    
                    row += f"<td>{i.get('비중', 0):.1f}%</td>"
                    row += f"<td>{fmt(item_asset)}</td>"
                    row += f"<td class='{col(i.get('평가손익', 0))}'>{fmt(i.get('평가손익', 0), True)}</td>"
                    row += f"<td class='{col(i_rate)}'>{fmt_p(i_rate)}</td>"
                    row += f"<td>{fmt(i.get('수량', '-'))}</td>"
                    row += f"<td>{fmt(i.get('매입가', '-'))}</td>"
                    row += f"<td>{fmt(i.get('현재가', '-'))}</td>"
                    
                    if st.session_state.show_change_rate:
                        if is_s:
                            row += "<td>-</td>"
                        else:
                            row += f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{diff_amt_str}</div><div class='{d_class}' style='font-size:13px;'>{d_rate_str}</div></td>"
                        
                    row += "</tr>"
                    h3.append(row)
                    
                h3.append("</table>")
                st.markdown("".join(h3), unsafe_allow_html=True)
                # =========================================================
# [ 3. 일반 계좌 대시보드 ]
# =========================================================
elif menu == "3. 일반 계좌":
    c1, c2 = st.columns([8.5, 1.5])
    with c1: st.markdown("<h3 style='margin-top: 5px;'>🚀 이상혁(Andy lee)님 [일반계좌] 통합 대시보드</h3>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 업데이트", use_container_width=True, key="btn_update_gen"):
            with st.spinner("데이터 업데이트 중..."):
                try: andy_general_v1.generate_general_data()
                except: pass
            st.cache_data.clear(); st.rerun()

    g_data = load_gen()
    if not g_data:
        st.warning("데이터가 없습니다. 업데이트 버튼을 눌러주세요.")
        st.stop()

    st.markdown(f"<div style='text-align:right;font-size:14.5px;color:#555;font-weight:normal;margin:-10px 0 15px;'>[ {g_data.get('조회시간', '업데이트 필요')} ]</div>", unsafe_allow_html=True)

    principals = {"DOM1": 110963075, "DOM2": 5208948, "USA1": 257915999, "USA2": 7457930}
    GEN_ACC_ORDER = ['DOM1', 'DOM2', 'USA1', 'USA2']
    t_asset = sum(g_data[k].get("총자산_KRW", 0) for k in GEN_ACC_ORDER if k in g_data)
    t_profit = sum(g_data[k].get("총수익_KRW", 0) for k in GEN_ACC_ORDER if k in g_data)
    t_original_sum = sum(principals.values())
    t_rate = (t_profit / t_original_sum * 100) if t_original_sum > 0 else 0

    cash_total = 0; dom_total = 0; ovs_total = 0; all_gen_items = []
    
    for k in GEN_ACC_ORDER:
        if k in g_data:
            short_nm = {'DOM1':'국내1.키움', 'DOM2':'국내2.삼성', 'USA1':'미국1.키움', 'USA2':'미국2.키움'}[k]
            for item in g_data[k].get('상세', []):
                if item.get('종목명') == '[ 합계 ]': continue
                it_copy = item.copy(); it_copy['계좌'] = short_nm; all_gen_items.append(it_copy)
                
                val_krw = item.get('총자산', 0) * (g_data.get('환율', 1443.1) if 'USA' in k else 1)
                nm = item.get('종목명', '')
                
                if nm == '예수금': cash_total += val_krw
                elif 'USA' in k: ovs_total += val_krw
                else: dom_total += val_krw

    tradeable_items = [it for it in all_gen_items if it.get("종목명") != "예수금"]
    tradeable_items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
    best_5 = tradeable_items[:5]; worst_5 = tradeable_items[::-1][:5]

    rise_cnt = sum(1 for it in tradeable_items if float(it.get('전일비', 0)) > 0.2)
    fall_cnt = sum(1 for it in tradeable_items if float(it.get('전일비', 0)) < -0.2)
    flat_cnt = len(tradeable_items) - rise_cnt - fall_cnt
    
    tradeable_items_by_day = sorted(tradeable_items, key=lambda x: float(x.get('전일비', 0)), reverse=True)
    rise_list = [f"{short_name(it.get('종목명', ''))}({it.get('계좌', '')} <span class='{col(float(it.get('전일비', 0)))}'>{fmt_p(float(it.get('전일비', 0)))}</span>)" for it in tradeable_items_by_day if float(it.get('전일비', 0)) > 0.2]
    fall_list = [f"{short_name(it.get('종목명', ''))}({it.get('계좌', '')} <span class='{col(float(it.get('전일비', 0)))}'>{fmt_p(float(it.get('전일비', 0)))}</span>)" for it in tradeable_items_by_day[::-1] if float(it.get('전일비', 0)) < -0.2]
    
    str_rise = ", ".join(rise_list[:5]) + " 등" if rise_list[:5] else "없음"
    str_fall = ", ".join(fall_list[:3]) + " 등" if fall_list[:3] else "없음"

    total_for_bar = max(1, dom_total + ovs_total + cash_total)
    p_dom = dom_total / total_for_bar * 100
    p_ovs = ovs_total / total_for_bar * 100
    p_cash = cash_total / total_for_bar * 100
    def render_bar(p, color): return f"<div style='width: {p}%; background-color: {color}; height: 100%; display: flex; align-items: center; justify-content: center; position: relative;'><span style='position: absolute; font-size: 13px; color: #333; z-index: 10; white-space: nowrap;'>{p:.0f}%</span></div>" if p > 0 else ""

    acc_rates = sorted([(k, (g_data[k].get('총수익_KRW',0) / principals[k] * 100 if principals[k]>0 else 0)) for k in GEN_ACC_ORDER if k in g_data], key=lambda x: x[1], reverse=True)
    best_acc_name = {'DOM1':'국내1.키움', 'DOM2':'국내2.삼성', 'USA1':'미국1.키움', 'USA2':'미국2.키움'}.get(acc_rates[0][0]) if acc_rates else "전체"

    zappa_html = f"<div style='font-size: 14.5px; line-height: 1.85; color: #444; padding-left: 0px;'><div style='margin-bottom: 22px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> 계좌 현황 및 종목 분석</span><div>현재 <strong>{best_acc_name} 계좌가 전체 수익률(<span class='{col(acc_rates[0][1] if acc_rates else 0)}' style='font-weight:bold;'>{fmt_p(acc_rates[0][1] if acc_rates else 0)}</span>) 1위</strong>를 기록 중입니다. 총 <strong>{len(tradeable_items)}개</strong> 종목 중 전일비 상승종목은 <strong>{rise_cnt}개</strong>, 하락종목은 <strong>{fall_cnt}개</strong>, 보합종목은 <strong>{flat_cnt}개</strong> 입니다.<br><span style='font-size:13.5px; color:#555;'>※ 상승종목 : {str_rise}<br>※ 하락종목 : {str_fall}</span></div></div><div style='margin-bottom: 0px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> 주식 시황 및 향후 대응 전략</span><div>최근 시장 변동성에 대비하여 아웃퍼폼 중인 <strong>{short_name(best_5[0]['종목명']) if best_5 else '주도 종목'}</strong> 등에서 일부 차익 실현을 고려할 수 있으며, 현재 <strong>{p_cash:.1f}%</strong>인 현금(예수금) 비중을 유동적으로 관리하시기 바랍니다.</div></div></div>"

    st.markdown("<div class='sub-title' style='margin-bottom: 15px;'>💡 ZAPPA의 [일반계좌] 자산 현황 보고</div>", unsafe_allow_html=True)
    donut_css = f"background: conic-gradient(#ffffff 0% {p_cash}%, #d9d9d9 {p_cash}% {p_cash+p_ovs}%, #8c8c8c {p_cash+p_ovs}% 100%);"
    donut_html = f"<div style='position: relative; width: 120px; height: 120px; border-radius: 50%; {donut_css} box-shadow: inset 0 0 8px rgba(0,0,0,0.1); border: 1px solid #d0d0d0; flex-shrink: 0; margin: 0 auto;'><div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 35%; height: 35%; background-color: #fffdf2; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.05);'></div><div style='position: absolute; top: 2%; left: 50%; transform: translateX(-50%); font-size: 11.5px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_cash:.0f}%<br>예수금</div><div style='position: absolute; top: 28%; right: -7%; font-size: 11.5px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_ovs:.0f}%<br>미국주식</div><div style='position: absolute; bottom: 9%; left: 20%; font-size: 12px; color: #fff; font-weight: bold; text-align: center; line-height: 1.1; text-shadow: 0px 0px 3px rgba(0,0,0,0.5);'>{p_dom:.0f}%<br>국내주식</div></div>"

    html_parts = []
    html_parts.append("<div style='text-align: right; font-size: 13px; color: #555; font-weight: bold; margin-bottom: 5px;'>단위 : 원화(KRW)</div>")
    html_parts.append("<div class='insight-container'>")
    html_parts.append("<div class='insight-left'>")
    html_parts.append("  <div class='card-main'>")
    html_parts.append("    <div style='display: flex; gap: 15px; align-items: stretch; margin-bottom: auto;'>")
    html_parts.append("      <div style='flex: 0 0 38%; display: flex; flex-direction: column;'>")
    html_parts.append("        <div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 15px;'>총 자산</div>")
    html_parts.append(donut_html)
    html_parts.append("      </div>")
    html_parts.append("      <div style='flex: 1; display: flex; flex-direction: column; justify-content: flex-start; padding-top: 5px;'>")
    html_parts.append("        <div style='background-color: #ffffff; border: 1.5px solid #dcdcdc; border-radius: 8px; padding: 10px 12px; text-align: right; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 16px;'>")
    html_parts.append(f"          <div style='font-size: 24px; font-weight: 700 !important; color: #111; letter-spacing: normal; line-height: 1; margin-bottom: 6px;'>{fmt(t_asset)}<span style='font-size: 13.5px; font-weight: normal; margin-left: 3px; letter-spacing: normal;'>KRW</span></div>")
    html_parts.append(f"          <div style='font-size: 13.5px; color: #777; font-weight: normal; line-height: 1;'>[ 전일비 <span class='{col(t_diff)}'>{fmt(t_diff, True)}</span> / 전주비 <span class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</span> ]</div>")
    html_parts.append("        </div>")
    html_parts.append("        <div style='display: grid; grid-template-columns: auto auto; row-gap: 8px; column-gap: 30px; justify-content: end; align-items: baseline; width: 100%; padding-right: 12px; margin-top: 25px;'>")
    html_parts.append("          <div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>평가금액</div>")
    html_parts.append(f"          <div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(t_asset - cash_total)}</div>")
    html_parts.append("          <div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>현금성자산(예수금)</div>")
    html_parts.append(f"          <div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(cash_total)}</div>")
    html_parts.append("          <div style='color: #777; font-size: 14px; font-weight: normal; text-align: right; line-height: 20px;'>총 손익</div>")
    html_parts.append("          <div style='text-align: right;'>")
    html_parts.append(f"            <div style='font-size: 18px; font-weight: 600; line-height: 1;' class='{col(t_profit)}'>{fmt(t_profit, True)}</div>")
    html_parts.append(f"            <div style='font-size: 13.5px; font-weight: 600; margin-top: 3px; line-height: 1;' class='{col(t_rate)}'>{fmt_p(t_rate)}</div>")
    html_parts.append("          </div>")
    html_parts.append("        </div>")
    html_parts.append("      </div>")
    html_parts.append("    </div>") 
    html_parts.append("    <div style='margin-top: 20px;'>")
    html_parts.append("      <div style='display: flex; height: 20px; width: 100%; border-radius: 4px; border: 1px solid #ccc; margin-bottom: 6px; overflow: hidden;'>")
    html_parts.append(f"        {render_bar(p_dom, '#4a90e2')}{render_bar(p_ovs, '#f5a623')}{render_bar(p_cash, '#7ed321')}")
    html_parts.append("      </div>")
    html_parts.append("      <div style='display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #777; padding: 0 4px; margin-bottom: 16px;'>")
    html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#4a90e2; border-radius:2px;'></div>국내주식</div>")
    html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#f5a623; border-radius:2px;'></div>미국주식</div>")
    html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#7ed321; border-radius:2px;'></div>예수금(현금)</div>")
    html_parts.append("      </div>")
    html_parts.append("    </div>") 
    html_parts.append("  </div>") 
    html_parts.append("</div>") 
    
    html_parts.append("<div class='insight-right'>")
    html_parts.append("  <div class='grid-2x2'>")
    for k in GEN_ACC_ORDER:
        if k in g_data:
            a = g_data[k]
            acc_name = {'DOM1':'국내1.키움(5329)', 'DOM2':'국내2.삼성(01)', 'USA1':'미국1.키움(5329)', 'USA2':'미국2.키움(5993)'}[k]
            item_count = len([i for i in a.get('상세', []) if i.get('종목명') not in ['[ 합계 ]', '예수금']])
            html_parts.append(f"<a href='#gen_detail_section' style='text-decoration:none; color:inherit; display:block; height:100%;'><div class='card-sub'><div><div style='text-align: right; font-size: 13.5px; color: #666; font-weight: normal; margin-bottom: -2px; line-height: 1;'>&nbsp;</div><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 2px;'>{acc_name}</div><div style='border-bottom: 1px solid #eee; margin-bottom: 6px; margin-top: 2px;'></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 자산</span><span style='font-size: 16px; color: #111; font-weight: normal;'>{fmt(a.get('총자산_KRW', 0))}</span></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 손익</span><div style='text-align: right; line-height: 1.2;'><div class='{col(a.get('총수익_KRW', 0))}' style='font-size: 16px; font-weight: normal;'>{fmt(a.get('총수익_KRW', 0), True)}</div><div class='{col(a.get('총수익_KRW',0)/principals[k]*100 if principals[k] else 0)}' style='font-size: 14px; font-weight: normal; margin-top: 1px;'>{fmt_p(a.get('총수익_KRW',0)/principals[k]*100 if principals[k] else 0)}</div></div></div></div><div style='font-size: 13.5px; color: #666; font-weight: normal; margin-top: auto; padding-top: 2px; display: flex; justify-content: space-between; align-items: baseline;'><span>* 원금 : {fmt(principals[k])}</span><span><span style='font-size: 16px; font-weight: bold; color: #111;'>{item_count}</span> 종목</span></div></div></a>")
            
    html_parts.append("  </div>") 
    html_parts.append("</div>") 
    html_parts.append("</div>") 
    
    html_parts.append("<div class='insight-bottom-box' style='display: flex; gap: 20px; align-items: stretch;'>")
    html_parts.append("  <div style='flex: 1; padding-right: 15px; border-right: 1px solid #eaeaea;'>")
    html_parts.append("    <div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 8px; letter-spacing: normal;'>📈 손익률 우수종목</div>")
    html_parts.append("    <table class='main-table' style='margin-bottom: 20px; font-size: 13.5px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>계좌</th></tr>")
    for idx, it in enumerate(best_5): html_parts.append(f"<tr><td>{idx+1}</td><td>{short_name(it.get('종목명', ''))}</td><td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0)*(g_data.get('환율',1443.1) if 'USA' in it.get('계좌','') else 1), True)}</td><td>{it.get('계좌','')}</td></tr>")
    html_parts.append("    </table>")
    html_parts.append("    <div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px; letter-spacing: normal;'>📉 손익률 부진종목</div>")
    html_parts.append("    <table class='main-table' style='margin-bottom: 0px; font-size: 13.5px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>계좌</th></tr>")
    for idx, it in enumerate(worst_5): html_parts.append(f"<tr><td>{idx+1}</td><td>{short_name(it.get('종목명', ''))}</td><td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0)*(g_data.get('환율',1443.1) if 'USA' in it.get('계좌','') else 1), True)}</td><td>{it.get('계좌','')}</td></tr>")
    html_parts.append("    </table>")
    html_parts.append("  </div>")
    html_parts.append("  <div style='flex: 1.1; padding-left: 5px;'>")
    html_parts.append("    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 8px;'>")
    html_parts.append("      <div style='font-size: 18px; font-weight: bold; color: #111; letter-spacing: normal;'>💡 시황 및 향후 전망</div>")
    html_parts.append("      <div style='font-size: 13.5px; color: #888;'>[ -0.2%p &lt; 횡보 &lt; +0.2%p ]</div>")
    html_parts.append("    </div>")
    html_parts.append(f"    {zappa_html}")
    html_parts.append("  </div>")
    html_parts.append("</div>") 
    st.markdown("".join(html_parts), unsafe_allow_html=True)

    unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"
    st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총자산 : <span class='summary-val'>{fmt(t_asset)}</span> / 총 손익 : <span class='summary-val {col(t_profit)}'>{fmt(t_profit, True)} ({fmt_p(t_rate)})</span></div></div>", unsafe_allow_html=True)

    h1_table = "<table class='main-table'><tr><th>계좌 구분</th><th>총 자산</th><th>평가손익</th><th>손익률</th><th>투자원금</th></tr>"
    h1 = [unit_html, h1_table, f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(t_asset)}</td><td class='{col(t_profit)}'>{fmt(t_profit, True)}</td><td class='{col(t_rate)}'>{fmt_p(t_rate)}</td><td>{fmt(t_original_sum)}</td></tr>"]
    for k in GEN_ACC_ORDER:
        if k in g_data:
            a = g_data[k]
            nm = {'DOM1':'국내1.키움(5329)', 'DOM2':'국내2.삼성(01)', 'USA1':'미국1.키움(5329)', 'USA2':'미국2.키움(5993)'}[k]
            h1.append(f"<tr><td>{nm}</td><td>{fmt(a.get('총자산_KRW',0))}</td><td class='{col(a.get('총수익_KRW',0))}'>{fmt(a.get('총수익_KRW',0), True)}</td><td class='{col(a.get('총수익_KRW',0)/principals[k]*100 if principals[k] else 0)}'>{fmt_p(a.get('총수익_KRW',0)/principals[k]*100 if principals[k] else 0)}</td><td>{fmt(principals[k])}</td></tr>")
    h1.append("</table>")
    st.markdown("".join(h1), unsafe_allow_html=True)

    st.markdown("<div id='gen_detail_section' style='padding-top: 20px; margin-top: -20px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
    
    b1, b2, b3, b4, b5, b6 = st.columns(6)
    with b1:
        st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
        if st.button("🛠️ 초기화 [ ● ]" if st.session_state.gen_sort_mode == 'init' else "🛠️ 초기화 [ ○ ]", type="primary" if st.session_state.gen_sort_mode == 'init' else "secondary", on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'init')): pass
    with b2:
        if st.button("💰 총자산 [ ▼ ]" if st.session_state.gen_sort_mode == 'asset' else "💰 총자산 [ ▽ ]", type="primary" if st.session_state.gen_sort_mode == 'asset' else "secondary", on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'asset')): pass
    with b3:
        if st.button("📊 평가손익 [ ▼ ]" if st.session_state.gen_sort_mode == 'profit' else "📊 평가손익 [ ▽ ]", type="primary" if st.session_state.gen_sort_mode == 'profit' else "secondary", on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'profit')): pass
    with b4:
        if st.button("📈 손익률 [ ▼ ]" if st.session_state.gen_sort_mode == 'rate' else "📈 손익률 [ ▽ ]", type="primary" if st.session_state.gen_sort_mode == 'rate' else "secondary", on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'rate')): pass
    with b5:
        if st.button("↕️ 등락률 [ + ]" if st.session_state.gen_show_change_rate else "↕️ 등락률 [ - ]", type="primary" if st.session_state.gen_show_change_rate else "secondary", on_click=lambda: setattr(st.session_state, 'gen_show_change_rate', not st.session_state.gen_show_change_rate)): pass
    with b6:
        if st.button("💵 통화 [ KRW ]" if st.session_state.gen_curr == 'USD' else "💵 통화 [ USD ]", type="primary" if st.session_state.gen_curr == 'USD' else "secondary", on_click=lambda: setattr(st.session_state, 'gen_curr', 'KRW' if st.session_state.gen_curr == 'USD' else 'USD')): pass

    st.markdown("<br>", unsafe_allow_html=True)
    
    for k in GEN_ACC_ORDER:
        if k not in g_data: continue
        a = g_data[k]
        is_usa = 'USA' in k
        nm = {'DOM1':'국내1. 키움증권 (위탁종합 : 6312-5329)', 'DOM2':'국내2. 삼성증권 (주식보상 : 7162669785-01)', 'USA1':'미국1. 키움증권 (위탁종합 : 6312-5329)', 'USA2':'미국2. 키움증권 (위탁종합 : 6443-5993)'}[k]
        
        with st.expander(f"📂 [ {nm} ] 종목별 현황", expanded=False):
            s_data = next((i for i in a.get('상세', []) if i.get('종목명') == "[ 합계 ]"), {})
            curr_asset = a.get('총자산_KRW', 0); a_prof = a.get('총수익_KRW', 0)
            a_rate = (a_prof / principals[k] * 100) if principals[k] else 0
            
            st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총자산 : <span class='summary-val'>{fmt(curr_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(a_prof)}'>{fmt(a_prof, True)} ({fmt_p(a_rate)})</span></div></div>", unsafe_allow_html=True)
            
            mode = "KRW" if not is_usa else st.session_state.gen_curr
            rate_val = g_data.get('환율', 1443.1)
            u_html = f"<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : {'달러(USD)' if mode == 'USD' else '원화(KRW)'}</div>"
            
            if st.session_state.gen_show_change_rate:
                code_th = "<th rowspan='2'>종목코드</th>" if st.session_state.show_code else ""
                h3_table_html = f"""
                <table class='main-table'>
                    <tr>
                        <th rowspan='2'>종목명</th>
                        {code_th}
                        <th rowspan='2'>비중</th>
                        <th rowspan='2'>총 자산</th>
                        <th rowspan='2'>평가손익</th>
                        <th rowspan='2'>손익률</th>
                        <th rowspan='2'>주식수</th>
                        <th rowspan='2'>매입가</th>
                        <th rowspan='2' class='th-eval'>현재가</th>
                        <th class='th-blank'>&nbsp;</th>
                    </tr>
                    <tr>
                        <th class='th-week'>등락률</th>
                    </tr>
                """
                h3_table = re.sub(r'\n\s*', '', h3_table_html)
            else:
                code_th = "<th>종목코드</th>" if st.session_state.show_code else ""
                h3_table = f"<table class='main-table'><tr><th>종목명</th>{code_th}<th>비중</th><th>총 자산</th><th>평가손익</th><th>손익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>"
            
            h3 = [u_html, h3_table]
            items = [i for i in a.get('상세', []) if i.get('종목명') not in ["[ 합계 ]", "예수금"]]
            cash_item = next((i for i in a.get('상세', []) if i.get('종목명') == "예수금"), {"종목명": "예수금", "총자산": 0, "평가손익": 0, "수익률(%)": 0, "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0})
            
            if st.session_state.gen_sort_mode == 'asset': items.sort(key=lambda x: x.get('총자산', 0), reverse=True)
            elif st.session_state.gen_sort_mode == 'profit': items.sort(key=lambda x: x.get('평가손익', 0), reverse=True)
            elif st.session_state.gen_sort_mode == 'rate': items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
            
            for i in (items + [cash_item, s_data]):
                if i.get('종목명') == "예수금" and i.get('총자산', 0) == 0 and s_data.get('총자산', 0) > 0: continue 
                is_s = (i.get('종목명') == "[ 합계 ]")
                row = f"<tr class='sum-row'>" if is_s else "<tr>"
                row += f"<td>{i.get('종목명', '')}</td>"
                if st.session_state.show_code: row += f"<td>{'-' if is_s or i.get('코드','-')=='-' else i.get('코드', '')}</td>"
                
                def cv(val): return (val * rate_val) if (is_usa and mode == 'KRW' and val != '-') else val
                dec = 4 if (is_usa and mode == 'USD') else 0
                
                ia = cv(i.get('총자산', 0)); ip = cv(i.get('평가손익', 0))
                ibuy = cv(i.get('매입가', '-')) if i.get('매입가') != '-' else '-'
                icurr = cv(i.get('현재가', '-')) if i.get('현재가') != '-' else '-'
                
                pct = (i.get('총자산', 0) / s_data.get('총자산', 1) * 100) if s_data.get('총자산', 1) > 0 else 0
                d_rate = float(i.get('전일비', 0))
                curr_price = float(i.get('현재가', 0)) if type(i.get('현재가', 0)) in [int, float] else 0
                diff_amt = cv((curr_price - (curr_price / (1 + d_rate / 100))) if curr_price > 0 and d_rate != 0 else 0)
                diff_amt_str = fmt(diff_amt, True, decimal=dec) if diff_amt != 0 else "0"
                d_rate_str = "-" if is_s else fmt_p(d_rate); d_class = "" if is_s else col(d_rate)
                
                row += f"<td>{pct:.1f}%</td><td>{fmt(ia, decimal=2 if is_usa and mode=='USD' else 0)}</td><td class='{col(ip)}'>{fmt(ip, True, decimal=2 if is_usa and mode=='USD' else 0)}</td><td class='{col(i.get('수익률(%)', 0))}'>{fmt_p(i.get('수익률(%)', 0))}</td><td>{fmt(i.get('수량', '-'))}</td><td>{fmt(ibuy, decimal=dec) if ibuy != '-' else '-'}</td><td>{fmt(icurr, decimal=dec) if icurr != '-' else '-'}</td>"
                
                if st.session_state.gen_show_change_rate:
                    if is_s or i.get('종목명') == '예수금': row += "<td>-</td>"
                    else: row += f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{diff_amt_str}</div><div class='{d_class}' style='font-size:13px;'>{d_rate_str}</div></td>"
                    
                row += "</tr>"
                h3.append(row)
                
            h3.append("</table>")
            st.markdown("".join(h3), unsafe_allow_html=True)
