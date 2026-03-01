import streamlit as st
import json
import warnings
import andy_pension_v2
import andy_general_v1
import os
import re
from datetime import datetime

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="ZAPPA Asset Dashboard")

# =========================================================
# [ Part 1 ] 공통 설정 및 CSS 디자인
# =========================================================
css = """
<style>
.block-container { padding-top: 3rem !important; padding-bottom: 7rem !important; }
h3 { font-size: 26px !important; font-weight: bold; margin-bottom: -10px; padding-bottom: 0px; }
.sub-title { font-size: 22px !important; font-weight: bold; margin: 12px 0 10px; }
.main-table { width: 100%; border-collapse: collapse; font-size: 15px; text-align: center; margin-bottom: 10px; }
.main-table th { background-color: #f2f2f2; padding: 10px; border: 1px solid #ddd; font-weight: bold !important; vertical-align: middle; }
.main-table td { padding: 8px; border: 1px solid #ddd; vertical-align: middle; }
.sum-row td { background-color: #fff9e6; font-weight: bold !important; }
.red { color: #FF2323 !important; }
.blue { color: #0047EB !important; }

.insight-container { display: flex; gap: 20px; align-items: stretch; margin-bottom: 20px; }
.insight-left { flex: 0 0 46%; display: flex; flex-direction: column; }
.insight-right { flex: 1; display: flex; flex-direction: column; }

.card-main { background-color: #fffdf2; border: 2px solid #e8dbad; border-radius: 18px; padding: 18px 22px 15px 22px; position: relative; box-shadow: 0 2px 6px rgba(0,0,0,0.03); height: 100%; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; }
.grid-2x2 { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 15px; height: 100%; }
.card-sub { background: #fff; border: 1.5px solid #ddd; border-radius: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.02); display: flex; flex-direction: column; padding: 10px 15px; transition: background-color 0.2s, border-color 0.2s; cursor: pointer; }
.card-sub:hover { background-color: #f2f2f2 !important; border-color: #ccc !important; }
.insight-bottom-box { background: #fff; border: 1.5px solid #ddd; border-radius: 18px; padding: 25px; box-shadow: 0 1px 4px rgba(0,0,0,0.02); font-size: 15.5px; line-height: 1.8; color: #333; margin-top: 5px; margin-bottom: 25px; }

.summary-text { font-size: 16px !important; font-weight: bold !important; color: #333; margin-bottom: 10px; }
.summary-val { font-size: 20px !important; }

.main-table th.th-eval { border-right: none !important; }
.main-table th.th-blank { border-left: none !important; border-bottom: none !important; padding: 0 !important; }
.main-table th.th-week { border-left: 1px solid #ddd !important; border-top: 1px solid #ddd !important; font-size: 13.5px; }
div[role="radiogroup"] label { font-size: 15.5px !important; margin-bottom: 8px !important; }

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

if 'sort_mode' not in st.session_state: st.session_state.sort_mode = 'init'
if 'gen_sort_mode' not in st.session_state: st.session_state.gen_sort_mode = 'init'
if 'show_code' not in st.session_state: st.session_state.show_code = False
if 'show_change_rate' not in st.session_state: st.session_state.show_change_rate = False
if 'gen_show_change_rate' not in st.session_state: st.session_state.gen_show_change_rate = False

if 'init' not in st.session_state:
    with st.spinner("데이터 업데이트 중..."):
        try: andy_pension_v2.generate_asset_data()
        except: pass
    st.session_state['init'] = True
    st.cache_data.clear()

def safe_float(val):
    try:
        if val in ['-', '', None]: return 0.0
        return float(val)
    except: return 0.0

def fmt(v, sign=False, decimal=0):
    if v == '-': return '-'
    try:
        f_val = float(v)
        val_str = f"{f_val:,.{decimal}f}" if decimal > 0 else f"{int(round(f_val)):,}"
        if sign and f_val > 0: return f"+{val_str}"
        return val_str
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

def short_name(nm): return nm[:13] + "***" if len(nm) > 13 else nm

@st.cache_data(ttl=60)
def load():
    try:
        with open('assets.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

@st.cache_data(ttl=60)
def load_gen():
    try:
        with open('assets_general.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

data = load()
tot = data.get("_total", {})

with st.sidebar:
    st.markdown("<div style='display:flex; align-items:center; gap:10px; margin-bottom:20px;'><span class='zappa-icon'>🤖</span><span style='font-size:24px; font-weight:bold; color:#111;'>ZAPPA MENU</span></div>", unsafe_allow_html=True)
    menu = st.radio("카테고리 선택", ("1. 복합 대시보드", "2. 절세 계좌", "3. 일반 계좌", "4. Quant 매매", "5. 가상자산"), index=1, label_visibility="collapsed")
    st.markdown("<hr style='margin:25px 0 20px 0; border: none; border-top: 1px dashed #ccc;'>", unsafe_allow_html=True)
    
    t_asset_all = tot.get('총 자산', 0)
    t_profit_all = tot.get('총 수익', 0)
    t_rate_all = tot.get('수익률(%)', 0)
    
    quick_view_html = f"<div style='background-color: #f8f9fa; border-radius: 12px; padding: 18px 15px; border: 1px solid #eaeaea;'><div style='font-size:13.5px; font-weight:bold; color:#777; margin-bottom:8px;'>⚡ 퀵 뷰 (전체 자산 현황)</div><div style='font-size:24px; font-weight:600; color:#111; letter-spacing:-0.5px; line-height: 1.1;'>{fmt(t_asset_all)}<span style='font-size:13.5px; font-weight:normal; margin-left:3px; letter-spacing:normal;'>KRW</span></div><div style='font-size:14px; margin-top:8px; color:#555;'>총 손익: <span class='{col(t_profit_all)}' style='font-weight:bold;'>{fmt(t_profit_all, True)}</span> ({fmt_p(t_rate_all)})</div></div>"
    st.markdown(quick_view_html, unsafe_allow_html=True)

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
# [ Part 2 ] 절세 계좌 대시보드
# =========================================================
elif menu == "2. 절세 계좌":
    c1, c2 = st.columns([8.5, 1.5])
    with c1: st.markdown("<h3 style='margin-top: 5px;'>🚀 이상혁(Andy lee)님 [절세계좌] 통합 대시보드</h3>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 업데이트", use_container_width=True):
            with st.spinner("데이터 업데이트 중..."):
                try: andy_pension_v2.generate_asset_data()
                except: pass
            st.cache_data.clear(); st.rerun()

    st.markdown(f"<div style='text-align:right;font-size:14.5px;color:#555;font-weight:normal;margin:-10px 0 15px;'>[ {tot.get('조회시간', '업데이트 필요')} ]</div>", unsafe_allow_html=True)

    FIXED_ACCOUNT_ORDER = ['DC', 'IRP', 'PENSION', 'ISA']
    OPEN_DATES = {'DC': '[ 2025.08 ]', 'IRP': '[ 2025.08 ]', 'PENSION': '[ 2025.11 ]', 'ISA': '[ 2025.08 ]'}
    pension_acc_name_map = {'DC': '퇴직연금(DC)계좌', 'IRP': '퇴직연금(IRP)계좌', 'PENSION': '연금저축(CMA)계좌', 'ISA': 'ISA(중개형)계좌'}

    if data and "_insight" in data:
        t_asset = tot.get('총 자산', 0)
        t_profit = tot.get('총 수익', 0)
        t_buy_total = tot.get('매입금액합', 0)
        
        t_prof_1ago = tot.get('평가손익(1일전)', 0) 
        t_prof_7ago = tot.get('평가손익(7일전)', 0)
        t_prof_15ago = tot.get('평가손익(15일전)', 0)
        t_prof_30ago = tot.get('평가손익(30일전)', 0)
        
        t_diff_1 = t_profit - t_prof_1ago
        t_diff_7 = t_profit - t_prof_7ago
        t_diff_15 = t_profit - t_prof_15ago
        t_diff_30 = t_profit - t_prof_30ago
        
        t_rate = tot.get('수익률(%)', 0)
        t_original_sum = tot.get('원금합', 0)
        
        cash_total = 0; ovs_total = 0; all_items = []
        
        for k in FIXED_ACCOUNT_ORDER:
            if k in data:
                short_acc_name = 'DC' if k == 'DC' else ('IRP' if k == 'IRP' else ('CMA' if k == 'PENSION' else 'ISA'))
                for item in data[k].get('상세', []):
                    if item.get('종목명') == '[ 합계 ]': continue
                    it_copy = item.copy(); it_copy['계좌'] = short_acc_name; all_items.append(it_copy)
                    val = item.get('총 자산', 0)
                    nm = item.get('종목명', '')
                    
                    if '현금' in nm or 'MMF' in nm or 'mmf' in nm.lower():
                        cash_total += val
                    elif any(kw in nm.lower() for kw in ['s&p', '나스닥', '필라델피아', '미국']):
                        ovs_total += val
        
        dom_total = t_asset - (ovs_total + cash_total)

        tradeable_items = [it for it in all_items if not any(kw in it.get("종목명", "") for kw in ["현금성자산", "삼성화재", "MMF", "이율보증"])]
        tradeable_items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
        best_5 = tradeable_items[:5]; worst_5 = tradeable_items[::-1][:5]

        rise_cnt = sum(1 for it in tradeable_items if safe_float(it.get('전일비', 0)) > 0.2)
        fall_cnt = sum(1 for it in tradeable_items if safe_float(it.get('전일비', 0)) < -0.2)
        flat_cnt = len(tradeable_items) - rise_cnt - fall_cnt
        
        tradeable_items_by_day = sorted(tradeable_items, key=lambda x: safe_float(x.get('전일비', 0)), reverse=True)
        rise_list = [f"{short_name(it.get('종목명', ''))}({it.get('계좌', '')} ▲{safe_float(it.get('전일비', 0)):.2f}%)" for it in tradeable_items_by_day if safe_float(it.get('전일비', 0)) > 0.2]
        fall_list = [f"{short_name(it.get('종목명', ''))}({it.get('계좌', '')} ▼{abs(safe_float(it.get('전일비', 0))):.2f}%)" for it in tradeable_items_by_day[::-1] if safe_float(it.get('전일비', 0)) < -0.2]
        str_rise = ", ".join(rise_list[:3]) if rise_list[:3] else "없음"
        str_fall = ", ".join(fall_list[:3]) if fall_list[:3] else "없음"

        total_for_bar = max(1, t_asset)
        p_cash = (cash_total / total_for_bar * 100); p_ovs = (ovs_total / total_for_bar * 100); p_dom = (dom_total / total_for_bar * 100)
        p_dc = data.get('DC', {}).get('총 자산', 0) / total_for_bar * 100
        p_irp = data.get('IRP', {}).get('총 자산', 0) / total_for_bar * 100
        p_pension = data.get('PENSION', {}).get('총 자산', 0) / total_for_bar * 100
        p_isa = data.get('ISA', {}).get('총 자산', 0) / total_for_bar * 100
        
        goal_amount = 1000000000
        progress_pct = (t_asset / goal_amount) * 100 if goal_amount > 0 else 0

        def render_bar(p, color): return f"<div style='width: {p}%; background-color: {color}; height: 100%; display: flex; align-items: center; justify-content: center; position: relative;'><span style='position: absolute; font-size: 13px; color: #333; z-index: 10; white-space: nowrap;'>{p:.0f}%</span></div>" if p > 0 else ""

        acc_rates = sorted([(pension_acc_name_map.get(k, k), data[k].get('수익률(%)', 0)) for k in FIXED_ACCOUNT_ORDER if k in data], key=lambda x: x[1], reverse=True)
        best_acc_name = acc_rates[0][0] if acc_rates else "전체"
        
        # 🎯 수익률 텍스트에 컬러 및 '상승종목', '하락종목', '보합' 명칭 반영 완료
        zappa_html = f"<div style='font-size: 14.5px; line-height: 1.85; color: #444; padding-left: 0px;'><div style='margin-bottom: 22px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> 계좌 현황 및 종목 분석</span><div>현재 전체 포트폴리오 총 손익은 <span class='{col(t_profit)}'><strong>{fmt(t_profit, True)}</strong></span> (<span class='{col(t_rate)}'><strong>{fmt_p(t_rate)}</strong></span>) 이며, <strong>{best_acc_name}</strong>가 계좌별 수익률 1위를 기록 중입니다. 개별 종목에서는 <strong>{short_name(best_5[0]['종목명']) if best_5 else '주도 종목'}</strong>가 효자 역할을 수행 중이나, <strong>{short_name(worst_5[0]['종목명']) if worst_5 else '부진 종목'}</strong> 등은 단기 조정을 겪고 있습니다. 총 <strong>{len(tradeable_items)}개</strong> 종목 중 전일비 상승 <strong>{rise_cnt}개</strong>, 하락 <strong>{fall_cnt}개</strong>, 보합 <strong>{flat_cnt}개</strong> 입니다.<br><span style='font-size:13.5px; color:#555;'>※ 상승종목 : {str_rise}<br>※ 하락종목 : {str_fall}</span></div></div><div style='margin-bottom: 0px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> 주식 시황 및 향후 대응 전략</span><div>간밤 미국 지표의 끈적한 흐름과 연준의 금리 인하 신중론이 겹치며 변동성이 부각되었습니다. 아웃퍼폼 중인 종목에서 일부 차익을 실현하여 <strong>현재 {p_cash:.1f}%인 현금 비중을 선제적으로 확대</strong>할 필요가 있습니다.</div></div></div>"

        st.markdown("<div class='sub-title' style='margin-bottom: 15px;'>💡 ZAPPA의 [절세계좌] 자산 현황 보고</div>", unsafe_allow_html=True)

        donut_css = f"background: conic-gradient(#ffffff 0% {p_cash}%, #d9d9d9 {p_cash}% {p_cash+p_ovs}%, #8c8c8c {p_cash+p_ovs}% 100%);"
        donut_html = f"<div style='position: relative; width: 120px; height: 120px; border-radius: 50%; {donut_css} box-shadow: inset 0 0 8px rgba(0,0,0,0.1); border: 1px solid #d0d0d0; flex-shrink: 0; margin: 0 auto;'><div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 35%; height: 35%; background-color: #fffdf2; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.05);'></div><div style='position: absolute; top: 2%; left: 50%; transform: translateX(-50%); font-size: 12.5px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_cash:.0f}%<br>현금성자산</div><div style='position: absolute; top: 15px; right: -5px; font-size: 13.5px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_ovs:.0f}%<br>해외투자</div><div style='position: absolute; bottom: 0px; left: -2px; font-size: 14px; color: #fff; font-weight: bold; text-align: center; line-height: 1.1; text-shadow: 0px 0px 3px rgba(0,0,0,0.5);'>{p_dom:.0f}%<br>국내투자</div></div>"

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
        html_parts.append("        <div style='background-color: #ffffff; border: 1.5px solid #dcdcdc; border-radius: 8px; padding: 10px 12px; text-align: right; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 8px;'>")
        html_parts.append(f"          <div style='font-size: 24px; font-weight: 700 !important; color: #111; letter-spacing: normal; line-height: 1; margin-bottom: 6px;'>{fmt(t_asset)}<span style='font-size: 13.5px; font-weight: normal; margin-left: 3px; letter-spacing: normal;'>KRW</span></div>")
        html_parts.append(f"          <div style='font-size: 13.5px; color: #777; font-weight: normal; line-height: 1;'>[ 전일비 <span class='{col(t_diff_1)}'>{fmt(t_diff_1, True)}</span> / 전주비 <span class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</span> ]</div>")
        html_parts.append("        </div>")
        html_parts.append("        <div style='display: grid; grid-template-columns: auto auto; row-gap: 12px; column-gap: 30px; justify-content: end; align-items: baseline; width: 100%; padding-right: 12px; margin-top: 8px;'>")
        html_parts.append("          <div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>평가금액</div>")
        html_parts.append(f"          <div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(t_asset - cash_total)}</div>")
        html_parts.append("          <div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>현금성자산</div>")
        html_parts.append(f"          <div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(cash_total)}</div>")
        html_parts.append("          <div style='color: #777; font-size: 14px; font-weight: normal; text-align: right; line-height: 20px;'>총 수익</div>")
        html_parts.append("          <div style='text-align: right;'>")
        html_parts.append(f"            <div style='font-size: 18px; font-weight: 600; line-height: 1;' class='{col(t_profit)}'>{fmt(t_profit, True)}</div>")
        html_parts.append(f"            <div style='font-size: 13.5px; font-weight: 600; margin-top: 3px; line-height: 1;' class='{col(t_rate)}'>{fmt_p(t_rate)}</div>")
        html_parts.append("          </div>")
        html_parts.append("        </div>")
        html_parts.append("      </div>")
        html_parts.append("    </div>") 
        html_parts.append("    <div style='margin-top: 20px;'>")
        html_parts.append("      <div style='display: flex; height: 20px; width: 100%; border-radius: 4px; border: 1px solid #ccc; margin-bottom: 6px; overflow: hidden;'>")
        html_parts.append(f"        {render_bar(p_dc, '#b4a7d6')}{render_bar(p_irp, '#f4b183')}{render_bar(p_pension, '#a9d18e')}{render_bar(p_isa, '#ffd966')}")
        html_parts.append("      </div>")
        html_parts.append("      <div style='display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #777; padding: 0 2px; margin-bottom: 16px;'>")
        html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#b4a7d6;'></div>퇴직연금(DC)</div>")
        html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#f4b183;'></div>퇴직연금(IRP)</div>")
        html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#a9d18e;'></div>연금저축(CMA)</div>")
        html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#ffd966;'></div>ISA(중개형)</div>")
        html_parts.append("      </div>")
        html_parts.append("      <div style='padding: 10px 15px; background: rgba(255,255,255,0.5); border-radius: 10px; border: 1px solid #e8dbad;'>")
        html_parts.append("        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>")
        html_parts.append("          <span style='font-size: 14px; color: #777; font-weight: normal;'>🎯 은퇴자산 10억 로드맵</span>")
        html_parts.append(f"         <div style='text-align: right;'><span style='font-size: 13px; color: #888; font-weight: normal; margin-right: 6px;'>* 원금 : {fmt(t_original_sum)} / </span><span style='font-size: 14px; font-weight: bold; color: #4a90e2;'>{progress_pct:.1f}%</span></div>")
        html_parts.append("        </div>")
        html_parts.append("        <div style='width: 100%; height: 6px; background-color: #e2e2e2; border-radius: 3px; overflow: hidden;'>")
        html_parts.append(f"          <div style='width: {progress_pct}%; height: 100%; background: linear-gradient(90deg, #9bc2e6, #4a90e2);'></div>")
        html_parts.append("        </div>")
        html_parts.append("      </div>")
        html_parts.append("    </div>") 
        html_parts.append("  </div>") 
        html_parts.append("</div>") 
        
        html_parts.append("<div class='insight-right'><div class='grid-2x2'>")
        for k in FIXED_ACCOUNT_ORDER:
            if k in data:
                a = data[k]
                acc_name = pension_acc_name_map.get(k, k)
                acc_asset = a.get('총 자산', 0); acc_profit = a.get('총 수익', 0); acc_rate = a.get('수익률(%)', 0)
                item_count = len([i for i in a.get('상세', []) if i.get('종목명') != '[ 합계 ]' and '현금성자산' not in i.get('종목명', '') and 'MMF' not in i.get('종목명', '') and '이율보증' not in i.get('종목명', '')])
                html_parts.append(f"<a href='#account_detail_section' style='text-decoration:none; color:inherit;'><div class='card-sub'><div><div style='text-align: right; font-size: 13.5px; color: #666; font-weight: normal; margin-bottom: -2px; line-height: 1;'>{OPEN_DATES.get(k, '')}</div><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 2px;'>{acc_name}</div><div style='border-bottom: 1px solid #eee; margin-bottom: 6px; margin-top: 2px;'></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 자산</span><span style='font-size: 16px; color: #111; font-weight: normal;'>{fmt(acc_asset)}</span></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 손익</span><div style='text-align: right; line-height: 1.2;'><div class='{col(acc_profit)}' style='font-size: 16px; font-weight: normal;'>{fmt(acc_profit, True)}</div><div class='{col(acc_rate)}' style='font-size: 14px; font-weight: normal; margin-top: 1px;'>{fmt_p(acc_rate)}</div></div></div></div><div style='font-size: 13.5px; color: #666; font-weight: normal; margin-top: auto; padding-top: 2px; display: flex; justify-content: space-between; align-items: baseline;'><span>* 원금 : {fmt(a.get('원금',0))}</span><span><span style='font-size: 16px; font-weight: bold; color: #111;'>{item_count}</span> 종목</span></div></div></a>")
        html_parts.append("</div></div></div>") 
        
        html_parts.append("<div class='insight-bottom-box' style='display: flex; gap: 20px; align-items: stretch;'>")
        html_parts.append("  <div style='flex: 1; padding-right: 15px; border-right: 1px solid #eaeaea;'>")
        html_parts.append("    <div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; letter-spacing: normal;'>📈 손익률 우수종목 (TOP 5)</div>")
        html_parts.append("    <table class='main-table' style='margin-bottom: 20px; font-size: 13.5px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>등락률</th></tr>")
        for idx, it in enumerate(best_5):
            c_p = safe_float(it.get('현재가', 0))
            d_rate = safe_float(it.get('전일비', 0))
            diff_amt = safe_float(it.get('전일비_금액', 0))
            if diff_amt == 0: diff_amt = (c_p - (c_p / (1 + d_rate / 100))) if c_p > 0 and d_rate != 0 else 0
            d_class = col(d_rate)
            diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
            html_parts.append(f"<tr><td>{idx+1}</td><td>{short_name(it.get('종목명', ''))}</td><td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td>{diff_html}</tr>")
        html_parts.append("    </table>")
        
        html_parts.append("    <div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px; letter-spacing: normal;'>📉 손익률 부진종목</div>")
        html_parts.append("    <table class='main-table' style='margin-bottom: 0px; font-size: 13.5px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>등락률</th></tr>")
        for idx, it in enumerate(worst_5):
            c_p = safe_float(it.get('현재가', 0))
            d_rate = safe_float(it.get('전일비', 0))
            diff_amt = safe_float(it.get('전일비_금액', 0))
            if diff_amt == 0: diff_amt = (c_p - (c_p / (1 + d_rate / 100))) if c_p > 0 and d_rate != 0 else 0
            d_class = col(d_rate)
            diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
            html_parts.append(f"<tr><td>{idx+1}</td><td>{short_name(it.get('종목명', ''))}</td><td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td>{diff_html}</tr>")
        html_parts.append("    </table></div>")
        
        # 🎯 우측 하단 인사이트 '보합' 명칭 반영
        html_parts.append("  <div style='flex: 1.1; padding-left: 5px;'><div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 8px;'><div style='font-size: 18px; font-weight: bold; color: #111;'>💡 시황 및 향후 전망</div><div style='font-size: 13.5px; color: #888;'>[ -0.2%p &lt; 보합 &lt; +0.2%p ]</div></div>")
        html_parts.append(f"    {zappa_html}</div></div>") 
        st.markdown("".join(html_parts), unsafe_allow_html=True)

        unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"
        
        st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> / 총 손익 : <span class='summary-val {col(t_profit)}'>{fmt(t_profit, True)} ({fmt_p(t_rate)})</span></div></div>", unsafe_allow_html=True)

        h1_table = "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>투자원금</th></tr><tr><th class='th-week'>7일전</th><th class='th-week'>15일전</th><th class='th-week'>30일전</th></tr>"
        h1 = [unit_html, h1_table, f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(t_asset)}</td><td class='{col(t_profit)}'>{fmt(t_profit, True)}</td><td class='{col(t_prof_7ago)}'>{fmt(t_prof_7ago, True)}</td><td class='{col(t_prof_15ago)}'>{fmt(t_prof_15ago, True)}</td><td class='{col(t_prof_30ago)}'>{fmt(t_prof_30ago, True)}</td><td class='{col(t_rate)}'>{fmt_p(t_rate)}</td><td>{fmt(t_original_sum)}</td></tr>"]
        for k in [k for k in FIXED_ACCOUNT_ORDER if k in data]:
            a = data.get(k, {})
            prof_7_acc = a.get('평가손익(7일전)', 0)
            prof_15_acc = a.get('평가손익(15일전)', 0)
            prof_30_acc = a.get('평가손익(30일전)', 0)
            h1.append(f"<tr><td>{pension_acc_name_map.get(k, k)}</td><td>{fmt(a.get('총 자산',0))}</td><td class='{col(a.get('총 수익',0))}'>{fmt(a.get('총 수익',0), True)}</td><td class='{col(prof_7_acc)}'>{fmt(prof_7_acc, True)}</td><td class='{col(prof_15_acc)}'>{fmt(prof_15_acc, True)}</td><td class='{col(prof_30_acc)}'>{fmt(prof_30_acc, True)}</td><td class='{col(a.get('수익률(%)',0))}'>{fmt_p(a.get('수익률(%)',0))}</td><td>{fmt(a.get('원금',0))}</td></tr>")
        h1.append("</table>")
        st.markdown("".join(h1), unsafe_allow_html=True)

        ag_tot = t_asset - t_buy_total
        ay_tot = (ag_tot / t_buy_total * 100) if t_buy_total > 0 else 0
        st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> / 총 손익 : <span class='summary-val {col(ag_tot)}'>{fmt(ag_tot, True)} ({fmt_p(ay_tot)})</span></div>", unsafe_allow_html=True)

        h2_table = "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>매입금액</th></tr><tr><th class='th-week'>전일비</th><th class='th-week'>전주비</th><th class='th-week'>전월비</th></tr>"
        h2 = [unit_html, h2_table, f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(t_asset)}</td><td class='{col(ag_tot)}'>{fmt(ag_tot, True)}</td><td class='{col(t_diff_1)}'>{fmt(t_diff_1, True)}</td><td class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</td><td class='{col(t_diff_30)}'>{fmt(t_diff_30, True)}</td><td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td><td>{fmt(t_buy_total)}</td></tr>"]
        for k in [k for k in FIXED_ACCOUNT_ORDER if k in data]:
            a = data.get(k, {})
            ag_acc = sum(i.get('평가손익', 0) for i in a.get('상세', []) if i.get('종목명') != '[ 합계 ]')
            curr_asset = a.get('총 자산', 0)
            ap_acc = curr_asset - ag_acc
            ay_acc = (ag_acc / ap_acc * 100) if ap_acc > 0 else 0
            
            diff_1_acc = a.get('총 수익', 0) - a.get('평가손익(1일전)', 0)
            diff_7_acc = a.get('총 수익', 0) - a.get('평가손익(7일전)', 0)
            diff_30_acc = a.get('총 수익', 0) - a.get('평가손익(30일전)', 0)
            h2.append(f"<tr><td>{pension_acc_name_map.get(k, k)}</td><td>{fmt(curr_asset)}</td><td class='{col(ag_acc)}'>{fmt(ag_acc, True)}</td><td class='{col(diff_1_acc)}'>{fmt(diff_1_acc, True)}</td><td class='{col(diff_7_acc)}'>{fmt(diff_7_acc, True)}</td><td class='{col(diff_30_acc)}'>{fmt(diff_30_acc, True)}</td><td class='{col(ay_acc)}'>{fmt_p(ay_acc)}</td><td>{fmt(ap_acc)}</td></tr>")
        h2.append("</table>")
        st.markdown("".join(h2), unsafe_allow_html=True)

        st.markdown("<div id='account_detail_section' style='padding-top: 20px; margin-top: -20px;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
        
        b1, b2, b3, b4, b5, b6 = st.columns(6)
        with b1:
            st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
            if st.button("🛠️ 초기화 [ ● ]" if st.session_state.sort_mode == 'init' else "🛠️ 초기화 [ ○ ]", type="primary" if st.session_state.sort_mode == 'init' else "secondary", on_click=lambda: setattr(st.session_state, 'sort_mode', 'init')): pass
        with b2:
            if st.button("💰 총 자산 [ ▼ ]" if st.session_state.sort_mode == 'asset' else "💰 총 자산 [ ▽ ]", type="primary" if st.session_state.sort_mode == 'asset' else "secondary", on_click=lambda: setattr(st.session_state, 'sort_mode', 'asset')): pass
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
            a = data[k]
            with st.expander(f"📂 [ {t3_lbl.get(k, a.get('label', ''))} ] 종목별 현황", expanded=False):
                s_data = next((i for i in a.get('상세', []) if i.get('종목명') == "[ 합계 ]"), {})
                extra_info_html = ""
                if k in ['DC', 'IRP']:
                    safe_pct = 0
                    for item in a.get('상세', []):
                        nm = item.get('종목명', '')
                        if '현금' in nm or '삼성화재' in nm or 'MMF' in nm or 'mmf' in nm.lower() or '이율보증' in nm:
                            safe_pct += item.get('비중', 0)
                    extra_info_html = f"<div style='font-size:14.5px; font-weight:normal; color:#555;'>[ 🔴 위험자산 : {100.0 - safe_pct:.1f}%  |  🟢 안전자산 : {safe_pct:.1f}% ]</div>"
                
                st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(a.get('총 자산', 0))}</span> / 총 손익 : <span class='summary-val {col(s_data.get('평가손익', 0))}'>{fmt(s_data.get('평가손익', 0), True)} ({fmt_p(s_data.get('수익률(%)', 0))})</span></div>{extra_info_html}</div>", unsafe_allow_html=True)
                
                if st.session_state.show_change_rate:
                    code_th = "<th rowspan='2'>종목코드</th>" if st.session_state.show_code else ""
                    h3_table_html = f"<table class='main-table'><tr><th rowspan='2'>종목명</th>{code_th}<th rowspan='2'>비중</th><th rowspan='2'>총 자산</th><th rowspan='2'>평가손익</th><th rowspan='2'>손익률</th><th rowspan='2'>주식수</th><th rowspan='2'>매입가</th><th rowspan='2' class='th-eval'>현재가</th><th class='th-blank'>&nbsp;</th></tr><tr><th class='th-week'>등락률</th></tr>"
                else:
                    code_th = "<th>종목코드</th>" if st.session_state.show_code else ""
                    h3_table_html = f"<table class='main-table'><tr><th>종목명</th>{code_th}<th>비중</th><th>총 자산</th><th>평가손익</th><th>손익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>"
                
                h3 = [unit_html, h3_table_html]
                items = [i for i in a.get('상세', []) if i.get('종목명') != "[ 합계 ]"]
                
                if st.session_state.sort_mode == 'asset': items.sort(key=lambda x: x.get('총 자산', 0), reverse=True)
                elif st.session_state.sort_mode == 'profit': items.sort(key=lambda x: x.get('평가손익', 0), reverse=True)
                elif st.session_state.sort_mode == 'rate': items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
                
                for i in ([s_data] + items):
                    is_s = (i.get('종목명') == "[ 합계 ]")
                    row = f"<tr class='sum-row'>" if is_s else "<tr>"
                    row += f"<td>{i.get('종목명', '')}</td>"
                    if st.session_state.show_code: row += f"<td>{'-' if is_s or i.get('코드','-')=='-' else i.get('코드', '')}</td>"
                    
                    d_rate = safe_float(i.get('전일비', 0.0))
                    c_p = safe_float(i.get('현재가', 0))
                    
                    diff_amt = safe_float(i.get('전일비_금액', 0))
                    if diff_amt == 0: diff_amt = (c_p - (c_p / (1 + d_rate / 100))) if c_p > 0 and d_rate != 0 else 0
                        
                    diff_amt_str = fmt(diff_amt, True) if diff_amt != 0 else "0"
                    d_rate_str = "-" if is_s else fmt_p(d_rate); d_class = "" if is_s else col(d_rate)
                    
                    row += f"<td>{i.get('비중', 0):.1f}%</td><td>{fmt(i.get('총 자산', 0))}</td><td class='{col(i.get('평가손익', 0))}'>{fmt(i.get('평가손익', 0), True)}</td><td class='{col(i.get('수익률(%)', 0))}'>{fmt_p(i.get('수익률(%)', 0))}</td><td>{fmt(i.get('수량', '-'))}</td><td>{fmt(i.get('매입가', '-'))}</td><td>{fmt(i.get('현재가', '-'))}</td>"
                    
                    if st.session_state.show_change_rate:
                        if is_s or any(kw in i.get('종목명', '') for kw in ['현금', '삼성화재', '이율보증', 'MMF']): 
                            row += "<td>-</td>"
                        else: 
                            row += f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{diff_amt_str}</div><div class='{d_class}' style='font-size:13px;'>{d_rate_str}</div></td>"
                    row += "</tr>"
                    h3.append(row)
                h3.append("</table>")
                st.markdown("".join(h3), unsafe_allow_html=True)

# =========================================================
# [ Part 3 ] 일반 계좌 대시보드
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
    t_buy_total = sum(g_data[k].get("매입금액_KRW", 0) for k in GEN_ACC_ORDER if k in g_data)
    
    t_prof_7ago = sum(g_data[k].get("평가손익(7일전)", 0) for k in GEN_ACC_ORDER if k in g_data)
    t_prof_15ago = sum(g_data[k].get("평가손익(15일전)", 0) for k in GEN_ACC_ORDER if k in g_data)
    t_prof_30ago = sum(g_data[k].get("평가손익(30일전)", 0) for k in GEN_ACC_ORDER if k in g_data)
    
    t_diff_7 = t_profit - t_prof_7ago
    t_diff_15 = t_profit - t_prof_15ago
    t_diff_30 = t_profit - t_prof_30ago
    
    t_original_sum = sum(principals.values())
    t_rate = (t_profit / t_original_sum * 100) if t_original_sum > 0 else 0

    cash_total = 0; dom_total = 0; ovs_total = 0
    dom_items = []; ovs_items = []; acc_1d_diff = {}
    
    for k in GEN_ACC_ORDER:
        acc_1d_diff[k] = 0
        if k in g_data:
            is_usa = 'USA' in k
            fx = g_data.get('환율', 1443.1) if is_usa else 1
            short_nm = {'DOM1':'국내1.키움', 'DOM2':'국내2.삼성', 'USA1':'해외1.키움', 'USA2':'해외2.키움'}[k]
            
            for item in g_data[k].get('상세', []):
                if item.get('종목명') == '[ 합계 ]': continue
                it_copy = item.copy(); it_copy['계좌'] = short_nm; it_copy['_k'] = k
                
                val_krw = item.get('총자산', 0) * fx
                nm = item.get('종목명', '')
                
                if nm == '예수금': cash_total += val_krw
                else:
                    c_p = safe_float(it_copy.get('현재가', 0))
                    qty = safe_float(it_copy.get('수량', 0))
                    d_rate = safe_float(it_copy.get('전일비', 0))
                    if c_p > 0 and d_rate != 0:
                        diff = (c_p - (c_p / (1 + d_rate / 100))) * fx
                        acc_1d_diff[k] += (diff * qty)
                    
                    if is_usa: 
                        ovs_total += val_krw
                        ovs_items.append(it_copy)
                    else: 
                        dom_total += val_krw
                        dom_items.append(it_copy)

    t_diff = sum(acc_1d_diff.values()) 
    goal_amount = 1000000000
    progress_pct = (t_asset / goal_amount) * 100 if goal_amount > 0 else 0

    all_tradeable = dom_items + ovs_items
    rise_cnt = sum(1 for it in all_tradeable if safe_float(it.get('전일비', 0)) > 0.5)
    fall_cnt = sum(1 for it in all_tradeable if safe_float(it.get('전일비', 0)) < -0.5)
    flat_cnt = len(all_tradeable) - rise_cnt - fall_cnt
    
    dom_best = sorted(dom_items, key=lambda x: x.get('수익률(%)', 0), reverse=True)[:5]
    dom_worst = sorted([it for it in dom_items if it.get('수익률(%)', 0) < 5.0], key=lambda x: x.get('수익률(%)', 0))[:5]
    ovs_best = sorted(ovs_items, key=lambda x: x.get('수익률(%)', 0), reverse=True)[:5]
    ovs_worst = sorted([it for it in ovs_items if it.get('수익률(%)', 0) < 5.0], key=lambda x: x.get('수익률(%)', 0))[:5]

    total_for_bar = max(1, t_asset)
    p_dom1 = g_data.get('DOM1', {}).get('총자산_KRW', 0) / total_for_bar * 100 if 'DOM1' in g_data else 0
    p_dom2 = g_data.get('DOM2', {}).get('총자산_KRW', 0) / total_for_bar * 100 if 'DOM2' in g_data else 0
    p_usa1 = g_data.get('USA1', {}).get('총자산_KRW', 0) / total_for_bar * 100 if 'USA1' in g_data else 0
    p_usa2 = g_data.get('USA2', {}).get('총자산_KRW', 0) / total_for_bar * 100 if 'USA2' in g_data else 0

    def render_bar(p, color): return f"<div style='width: {p}%; background-color: {color}; height: 100%; display: flex; align-items: center; justify-content: center; position: relative;'><span style='position: absolute; font-size: 13px; color: #333; z-index: 10; white-space: nowrap;'>{p:.0f}%</span></div>" if p > 0 else ""

    acc_rates = sorted([(k, (g_data[k].get('총수익_KRW',0) / principals[k] * 100 if principals[k]>0 else 0)) for k in GEN_ACC_ORDER if k in g_data], key=lambda x: x[1], reverse=True)
    best_acc_name = {'DOM1':'국내1. 키움증권', 'DOM2':'국내2. 삼성증권', 'USA1':'해외1. 키움증권', 'USA2':'해외2. 키움증권'}.get(acc_rates[0][0]) if acc_rates else "전체"

    # 🎯 수익률 텍스트에 컬러 및 '상승종목', '하락종목', '보합' 명칭 반영 완료
    zappa_html = f"<div style='font-size: 14.5px; line-height: 1.85; color: #444; padding-left: 0px;'><div style='margin-bottom: 22px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> [통합] 계좌 현황 요약</span><div>현재 전체 포트폴리오 총 손익은 <span class='{col(t_profit)}'><strong>{fmt(t_profit, True)}</strong></span> (<span class='{col(t_rate)}'><strong>{fmt_p(t_rate)}</strong></span>) 이며, <strong>{best_acc_name}</strong> 계좌가 계좌별 수익률 1위를 기록 중입니다. 총 <strong>{len(all_tradeable)}개</strong> 종목 중 0.5% 초과 상승종목은 <strong>{rise_cnt}개</strong>, 하락종목은 <strong>{fall_cnt}개</strong>, 보합종목은 <strong>{flat_cnt}개</strong> 입니다.</div></div><div style='margin-bottom: 15px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> [국내] 시황 및 전망</span><div>최근 국내 시장은 <strong>{short_name(dom_best[0]['종목명']) if dom_best else '국내 우량주'}</strong> 등 일부 우수 종목이 상승을 견인하고 있으나, <strong>{short_name(dom_worst[0]['종목명']) if dom_worst else '일부 조정주'}</strong> 등은 조정을 받고 있습니다. 실적 기반의 리밸런싱을 권고합니다.</div></div><div style='margin-bottom: 0px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> [해외] 시황 및 전망</span><div>미국 증시는 <strong>{short_name(ovs_best[0]['종목명']) if ovs_best else '빅테크 우량주'}</strong> 위주로 긍정적 흐름을 보이나, <strong>{short_name(ovs_worst[0]['종목명']) if ovs_worst else '단기 하락주'}</strong> 등 부진 섹터는 비중 조절이 필요합니다. 현재 <strong>{(cash_total/t_asset*100) if t_asset>0 else 0:.1f}%</strong>인 현금(예수금) 비중을 유동적으로 관리하시기 바랍니다.</div></div></div>"

    st.markdown("<div class='sub-title' style='margin-bottom: 15px;'>💡 ZAPPA의 [일반계좌] 자산 현황 보고</div>", unsafe_allow_html=True)
    
    p_cash_donut = (cash_total/t_asset*100) if t_asset>0 else 0
    p_ovs_donut = (ovs_total/t_asset*100) if t_asset>0 else 0
    p_dom_donut = (dom_total/t_asset*100) if t_asset>0 else 0
    donut_css = f"background: conic-gradient(#ffffff 0% {p_cash_donut}%, #d9d9d9 {p_cash_donut}% {p_cash_donut+p_ovs_donut}%, #8c8c8c {p_cash_donut+p_ovs_donut}% 100%);"
    
    donut_html = f"<div style='position: relative; width: 120px; height: 120px; border-radius: 50%; {donut_css} box-shadow: inset 0 0 8px rgba(0,0,0,0.1); border: 1px solid #d0d0d0; flex-shrink: 0; margin: 0 auto;'><div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 35%; height: 35%; background-color: #fffdf2; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.05);'></div><div style='position: absolute; top: 2%; left: 50%; transform: translateX(-50%); font-size: 12.5px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_cash_donut:.0f}%<br>예수금</div><div style='position: absolute; top: 55%; right: 3%; font-size: 14px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_ovs_donut:.0f}%<br>해외주식</div><div style='position: absolute; bottom: 48%; left: 10%; font-size: 13.5px; color: #fff; font-weight: bold; text-align: center; line-height: 1.1; text-shadow: 0px 0px 3px rgba(0,0,0,0.5);'>{p_dom_donut:.0f}%<br>국내주식</div></div>"

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
    html_parts.append("        <div style='background-color: #ffffff; border: 1.5px solid #dcdcdc; border-radius: 8px; padding: 10px 12px; text-align: right; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 8px;'>")
    html_parts.append(f"          <div style='font-size: 24px; font-weight: 700 !important; color: #111; letter-spacing: normal; line-height: 1; margin-bottom: 6px;'>{fmt(t_asset)}<span style='font-size: 13.5px; font-weight: normal; margin-left: 3px; letter-spacing: normal;'>KRW</span></div>")
    html_parts.append(f"          <div style='font-size: 13.5px; color: #777; font-weight: normal; line-height: 1;'>[ 전일비 <span class='{col(t_diff)}'>{fmt(t_diff, True)}</span> / 전주비 <span class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</span> ]</div>")
    html_parts.append("        </div>")
    html_parts.append("        <div style='display: grid; grid-template-columns: auto auto; row-gap: 12px; column-gap: 30px; justify-content: end; align-items: baseline; width: 100%; padding-right: 12px; margin-top: 8px;'>")
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
    html_parts.append(f"        {render_bar(p_dom1, '#b4a7d6')}{render_bar(p_dom2, '#f4b183')}{render_bar(p_usa1, '#a9d18e')}{render_bar(p_usa2, '#ffd966')}")
    html_parts.append("      </div>")
    html_parts.append("      <div style='display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #777; padding: 0 2px; margin-bottom: 16px;'>")
    html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#b4a7d6;'></div>국내1. 키움</div>")
    html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#f4b183;'></div>국내2. 삼성</div>")
    html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#a9d18e;'></div>해외1. 키움</div>")
    html_parts.append("        <div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#ffd966;'></div>해외2. 키움</div>")
    html_parts.append("      </div>")
    html_parts.append("      <div style='padding: 10px 15px; background: rgba(255,255,255,0.5); border-radius: 10px; border: 1px solid #e8dbad;'>")
    html_parts.append("        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>")
    html_parts.append("          <span style='font-size: 14px; color: #777; font-weight: normal;'>🎯 일반계좌 자산 목표 <strong style='color:#111;'>1,000,000,000</strong> KRW</span>")
    html_parts.append(f"         <div style='text-align: right;'><span style='font-size: 13px; color: #888; font-weight: normal; margin-right: 6px;'>* 원금 : {fmt(t_original_sum)} / </span><span style='font-size: 14px; font-weight: bold; color: #4a90e2;'>{progress_pct:.1f}%</span></div>")
    html_parts.append("        </div>")
    html_parts.append("        <div style='width: 100%; height: 6px; background-color: #e2e2e2; border-radius: 3px; overflow: hidden;'>")
    html_parts.append(f"          <div style='width: {progress_pct}%; height: 100%; background: linear-gradient(90deg, #9bc2e6, #4a90e2);'></div>")
    html_parts.append("        </div>")
    html_parts.append("      </div>")
    html_parts.append("    </div>") 
    html_parts.append("  </div>") 
    html_parts.append("</div>") 
    
    html_parts.append("<div class='insight-right'><div class='grid-2x2'>")
    for k in GEN_ACC_ORDER:
        if k in g_data:
            a = g_data[k]
            acc_name_map = {'DOM1': '국내1. 키움증권', 'DOM2': '국내2. 삼성증권', 'USA1': '해외1. 키움증권', 'USA2': '해외2. 키움증권'}
            acc_num_map = {'DOM1': '[ 6312-5329 ]', 'DOM2': '[ 7162669785-01 ]', 'USA1': '[ 6312-5329 ]', 'USA2': '[ 6443-5993 ]'}
            item_count = len([i for i in a.get('상세', []) if i.get('종목명') not in ['[ 합계 ]', '예수금']])
            html_parts.append(f"<a href='#gen_detail_section' style='text-decoration:none; color:inherit; display:block; height:100%;'><div class='card-sub'><div><div style='text-align: right; font-size: 13.5px; color: #666; font-weight: normal; margin-bottom: -2px; line-height: 1;'>{acc_num_map[k]}</div><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 2px;'>{acc_name_map[k]}</div><div style='border-bottom: 1px solid #eee; margin-bottom: 6px; margin-top: 2px;'></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 자산</span><span style='font-size: 16px; color: #111; font-weight: normal;'>{fmt(a.get('총자산_KRW', 0))}</span></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 손익</span><div style='text-align: right; line-height: 1.2;'><div class='{col(a.get('총수익_KRW', 0))}' style='font-size: 16px; font-weight: normal;'>{fmt(a.get('총수익_KRW', 0), True)}</div><div class='{col(a.get('총수익_KRW',0)/principals[k]*100 if principals[k] else 0)}' style='font-size: 14px; font-weight: normal; margin-top: 1px;'>{fmt_p(a.get('총수익_KRW',0)/principals[k]*100 if principals[k] else 0)}</div></div></div></div><div style='font-size: 13.5px; color: #666; font-weight: normal; margin-top: auto; padding-top: 2px; display: flex; justify-content: space-between; align-items: baseline;'><span>* 원금 : {fmt(principals[k])}</span><span><span style='font-size: 16px; font-weight: bold; color: #111;'>{item_count}</span> 종목</span></div></div></a>")
    html_parts.append("</div></div></div>") 
    
    html_parts.append("<div class='insight-bottom-box' style='display: flex; gap: 20px; align-items: stretch;'>")
    html_parts.append("  <div style='flex: 1; padding-right: 15px; border-right: 1px solid #eaeaea;'>")
    html_parts.append("    <div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; letter-spacing: normal;'>📈 [국내] 손익률 우수종목</div>")
    html_parts.append("    <table class='main-table' style='margin-bottom: 20px; font-size: 13.5px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>등락률</th></tr>")
    for idx, it in enumerate(dom_best): 
        c_p = safe_float(it.get('현재가', 0))
        d_rate = safe_float(it.get('전일비', 0))
        diff_amt = (c_p - (c_p / (1 + d_rate / 100))) if c_p > 0 and d_rate != 0 else 0
        d_class = col(d_rate)
        diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
        html_parts.append(f"<tr><td>{idx+1}</td><td>{short_name(it.get('종목명', ''))}</td><td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td>{diff_html}</tr>")
    html_parts.append("    </table>")
    html_parts.append("    <div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px; letter-spacing: normal;'>📉 [국내] 손익률 부진종목 <span style='font-size:12px; color:#888; font-weight:normal;'>(+5% 미만)</span></div>")
    html_parts.append("    <table class='main-table' style='margin-bottom: 25px; font-size: 13.5px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>등락률</th></tr>")
    for idx, it in enumerate(dom_worst): 
        c_p = safe_float(it.get('현재가', 0))
        d_rate = safe_float(it.get('전일비', 0))
        diff_amt = (c_p - (c_p / (1 + d_rate / 100))) if c_p > 0 and d_rate != 0 else 0
        d_class = col(d_rate)
        diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
        html_parts.append(f"<tr><td>{idx+1}</td><td>{short_name(it.get('종목명', ''))}</td><td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td>{diff_html}</tr>")
    html_parts.append("    </table><hr style='border:0; border-top:1px dashed #ddd; margin: 25px 0;'>")
    
    fx_rate = g_data.get('환율', 1443.1)
    html_parts.append("    <div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; letter-spacing: normal;'>📈 [해외] 손익률 우수종목</div>")
    html_parts.append("    <table class='main-table' style='margin-bottom: 20px; font-size: 13.5px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익(KRW)</th><th>등락률</th></tr>")
    for idx, it in enumerate(ovs_best): 
        c_p = safe_float(it.get('현재가', 0))
        d_rate = safe_float(it.get('전일비', 0))
        diff_amt = (c_p - (c_p / (1 + d_rate / 100))) * fx_rate if c_p > 0 and d_rate != 0 else 0
        d_class = col(d_rate)
        diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
        html_parts.append(f"<tr><td>{idx+1}</td><td>{short_name(it.get('종목명', ''))}</td><td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0)*fx_rate)}'>{fmt(it.get('평가손익', 0)*fx_rate, True)}</td>{diff_html}</tr>")
    html_parts.append("    </table>")
    html_parts.append("    <div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px; letter-spacing: normal;'>📉 [해외] 손익률 부진종목 <span style='font-size:12px; color:#888; font-weight:normal;'>(+5% 미만)</span></div>")
    html_parts.append("    <table class='main-table' style='margin-bottom: 0px; font-size: 13.5px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익(KRW)</th><th>등락률</th></tr>")
    for idx, it in enumerate(ovs_worst): 
        c_p = safe_float(it.get('현재가', 0))
        d_rate = safe_float(it.get('전일비', 0))
        diff_amt = (c_p - (c_p / (1 + d_rate / 100))) * fx_rate if c_p > 0 and d_rate != 0 else 0
        d_class = col(d_rate)
        diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
        html_parts.append(f"<tr><td>{idx+1}</td><td>{short_name(it.get('종목명', ''))}</td><td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0)*fx_rate)}'>{fmt(it.get('평가손익', 0)*fx_rate, True)}</td>{diff_html}</tr>")
    html_parts.append("    </table>")
    html_parts.append("  </div>")
    # 🎯 우측 하단 인사이트 '보합' 명칭 반영
    html_parts.append("  <div style='flex: 1.1; padding-left: 5px;'><div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 8px;'><div style='font-size: 18px; font-weight: bold; color: #111; letter-spacing: normal;'>💡 시황 및 향후 전망</div><div style='font-size: 13.5px; color: #888;'>[ -0.5%p &lt; 보합 &lt; +0.5%p ]</div></div>")
    html_parts.append(f"    {zappa_html}</div></div>") 
    st.markdown("".join(html_parts), unsafe_allow_html=True)

    nm_table = {'DOM1':'국내1. 키움증권(위탁)', 'DOM2':'국내2. 삼성증권(주식보상)', 'USA1':'해외1. 키움증권(위탁)', 'USA2':'해외2. 키움증권(위탁)'}
    
    unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"
    st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총자산 : <span class='summary-val'>{fmt(t_asset)}</span> / 총 손익 : <span class='summary-val {col(t_profit)}'>{fmt(t_profit, True)} ({fmt_p(t_rate)})</span></div></div>", unsafe_allow_html=True)

    h1_table = "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>투자원금</th></tr><tr><th class='th-week'>7일전</th><th class='th-week'>15일전</th><th class='th-week'>30일전</th></tr>"
    h1 = [unit_html, h1_table, f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(t_asset)}</td><td class='{col(t_profit)}'>{fmt(t_profit, True)}</td><td class='{col(t_prof_7ago)}'>{fmt(t_prof_7ago, True)}</td><td class='{col(t_prof_15ago)}'>{fmt(t_prof_15ago, True)}</td><td class='{col(t_prof_30ago)}'>{fmt(t_prof_30ago, True)}</td><td class='{col(t_rate)}'>{fmt_p(t_rate)}</td><td>{fmt(t_original_sum)}</td></tr>"]
    for k in GEN_ACC_ORDER:
        if k in g_data:
            a = g_data[k]
            h1.append(f"<tr><td>{nm_table[k]}</td><td>{fmt(a.get('총자산_KRW',0))}</td><td class='{col(a.get('총수익_KRW',0))}'>{fmt(a.get('총수익_KRW',0), True)}</td><td class='{col(a.get('평가손익(7일전)',0))}'>{fmt(a.get('평가손익(7일전)',0), True)}</td><td class='{col(a.get('평가손익(15일전)',0))}'>{fmt(a.get('평가손익(15일전)',0), True)}</td><td class='{col(a.get('평가손익(30일전)',0))}'>{fmt(a.get('평가손익(30일전)',0), True)}</td><td class='{col(a.get('총수익_KRW',0)/principals[k]*100 if principals[k] else 0)}'>{fmt_p(a.get('총수익_KRW',0)/principals[k]*100 if principals[k] else 0)}</td><td>{fmt(principals[k])}</td></tr>")
    h1.append("</table>")
    st.markdown("".join(h1), unsafe_allow_html=True)

    ag_tot = t_asset - t_buy_total
    ay_tot = (ag_tot / t_buy_total * 100) if t_buy_total > 0 else 0
    st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='summary-text'>● 총자산 : <span class='summary-val'>{fmt(t_asset)}</span> / 총 손익 : <span class='summary-val {col(ag_tot)}'>{fmt(ag_tot, True)} ({fmt_p(ay_tot)})</span></div>", unsafe_allow_html=True)

    h2_table = "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>매입금액</th></tr><tr><th class='th-week'>전일비</th><th class='th-week'>전주비</th><th class='th-week'>전월비</th></tr>"
    h2 = [unit_html, h2_table, f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(t_asset)}</td><td class='{col(ag_tot)}'>{fmt(ag_tot, True)}</td><td class='{col(t_diff)}'>{fmt(t_diff, True)}</td><td class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</td><td class='{col(t_diff_30)}'>{fmt(t_diff_30, True)}</td><td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td><td>{fmt(t_buy_total)}</td></tr>"]
    for k in GEN_ACC_ORDER:
        if k in g_data:
            a = g_data[k]
            ag_acc = a.get('총자산_KRW', 0) - a.get('매입금액_KRW', 0)
            ay_acc = (ag_acc / a.get('매입금액_KRW', 1) * 100) if a.get('매입금액_KRW', 1) > 0 else 0
            diff_7_acc = a.get('총수익_KRW', 0) - a.get('평가손익(7일전)', 0)
            diff_30_acc = a.get('총수익_KRW', 0) - a.get('평가손익(30일전)', 0)
            h2.append(f"<tr><td>{nm_table[k]}</td><td>{fmt(a.get('총자산_KRW',0))}</td><td class='{col(ag_acc)}'>{fmt(ag_acc, True)}</td><td class='{col(acc_1d_diff.get(k, 0))}'>{fmt(acc_1d_diff.get(k, 0), True)}</td><td class='{col(diff_7_acc)}'>{fmt(diff_7_acc, True)}</td><td class='{col(diff_30_acc)}'>{fmt(diff_30_acc, True)}</td><td class='{col(ay_acc)}'>{fmt_p(ay_acc)}</td><td>{fmt(a.get('매입금액_KRW', 0))}</td></tr>")
    h2.append("</table>")
    st.markdown("".join(h2), unsafe_allow_html=True)

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
        if st.button("💻 종목코드 [ + ]" if st.session_state.show_code else "💻 종목코드 [ - ]", type="primary" if st.session_state.show_code else "secondary", on_click=lambda: setattr(st.session_state, 'show_code', not st.session_state.show_code)): pass

    st.markdown("<br>", unsafe_allow_html=True)
    
    for k in GEN_ACC_ORDER:
        if k not in g_data: continue
        a = g_data[k]
        is_usa = 'USA' in k
        nm = {'DOM1':'국내1. 키움증권 (위탁종합 : 6312-5329)', 'DOM2':'국내2. 삼성증권 (주식보상 : 7162669785-01)', 'USA1':'해외1. 키움증권 (위탁종합 : 6312-5329)', 'USA2':'해외2. 키움증권 (위탁종합 : 6443-5993)'}[k]
        
        with st.expander(f"📂 [ {nm} ] 종목별 현황", expanded=False):
            s_data = next((i for i in a.get('상세', []) if i.get('종목명') == "[ 합계 ]"), {})
            curr_asset = a.get('총자산_KRW', 0); a_prof = a.get('총수익_KRW', 0)
            a_rate = (a_prof / principals[k] * 100) if principals[k] else 0
            
            st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총자산 : <span class='summary-val'>{fmt(curr_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(a_prof)}'>{fmt(a_prof, True)} ({fmt_p(a_rate)})</span></div></div>", unsafe_allow_html=True)
            
            mode = "KRW"
            rate_val = g_data.get('환율', 1443.1)
            u_html = f"<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"
            
            if st.session_state.gen_show_change_rate:
                code_th = "<th rowspan='2'>종목코드</th>" if st.session_state.show_code else ""
                h3_table_html = f"<table class='main-table'><tr><th rowspan='2'>종목명</th>{code_th}<th rowspan='2'>비중</th><th rowspan='2'>총 자산</th><th rowspan='2'>평가손익</th><th rowspan='2'>손익률</th><th rowspan='2'>주식수</th><th rowspan='2'>매입가</th><th rowspan='2' class='th-eval'>현재가</th><th class='th-blank'>&nbsp;</th></tr><tr><th class='th-week'>등락률</th></tr>"
            else:
                code_th = "<th>종목코드</th>" if st.session_state.show_code else ""
                h3_table_html = f"<table class='main-table'><tr><th>종목명</th>{code_th}<th>비중</th><th>총 자산</th><th>평가손익</th><th>손익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>"
            
            h3 = [u_html, h3_table_html]
            items = [i for i in a.get('상세', []) if i.get('종목명') not in ["[ 합계 ]", "예수금"]]
            cash_item = next((i for i in a.get('상세', []) if i.get('종목명') == "예수금"), {"종목명": "예수금", "총자산": 0, "평가손익": 0, "수익률(%)": 0, "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0})
            
            if st.session_state.gen_sort_mode == 'asset': items.sort(key=lambda x: x.get('총자산', 0), reverse=True)
            elif st.session_state.gen_sort_mode == 'profit': items.sort(key=lambda x: x.get('평가손익', 0), reverse=True)
            elif st.session_state.gen_sort_mode == 'rate': items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
            
            for i in ([s_data] + items + [cash_item]):
                if i.get('종목명') == "예수금" and i.get('총자산', 0) == 0 and s_data.get('총자산', 0) > 0: continue 
                is_s = (i.get('종목명') == "[ 합계 ]")
                row = f"<tr class='sum-row'>" if is_s else "<tr>"
                row += f"<td>{i.get('종목명', '')}</td>"
                if st.session_state.show_code: row += f"<td>{'-' if is_s or i.get('코드','-')=='-' else i.get('코드', '')}</td>"
                
                def cv(val): return (val * rate_val) if (is_usa and mode == 'KRW' and val != '-') else val
                
                ia = cv(i.get('총자산', 0)); ip = cv(i.get('평가손익', 0))
                ibuy = cv(i.get('매입가', '-')) if i.get('매입가') != '-' else '-'
                icurr = cv(i.get('현재가', '-')) if i.get('현재가') != '-' else '-'
                
                pct = (i.get('총자산', 0) / s_data.get('총자산', 1) * 100) if s_data.get('총자산', 1) > 0 else 0
                d_rate = safe_float(i.get('전일비', 0))
                curr_price = safe_float(i.get('현재가', 0))
                
                diff_amt = cv((curr_price - (curr_price / (1 + d_rate / 100)))) if curr_price > 0 and d_rate != 0 else 0
                diff_amt_str = fmt(diff_amt, True) if diff_amt != 0 else "0"
                d_rate_str = "-" if is_s else fmt_p(d_rate); d_class = "" if is_s else col(d_rate)
                
                row += f"<td>{pct:.1f}%</td><td>{fmt(ia)}</td><td class='{col(ip)}'>{fmt(ip, True)}</td><td class='{col(i.get('수익률(%)', 0))}'>{fmt_p(i.get('수익률(%)', 0))}</td><td>{fmt(i.get('수량', '-'))}</td><td>{fmt(ibuy)}</td><td>{fmt(icurr)}</td>"
                
                if st.session_state.gen_show_change_rate:
                    if is_s or i.get('종목명') == '예수금': row += "<td>-</td>"
                    else: row += f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{diff_amt_str}</div><div class='{d_class}' style='font-size:13px;'>{d_rate_str}</div></td>"
                    
                row += "</tr>"
                h3.append(row)
                
            h3.append("</table>")
            st.markdown("".join(h3), unsafe_allow_html=True)
