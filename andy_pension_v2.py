import streamlit as st
import json
import warnings
import google.generativeai as genai
import andy_pension_v2
import os
import re

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="ZAPPA Asset Dashboard")

# [ZAPPA] CSS 최적화 (여백/디자인 규칙 완벽 유지)
css = """<style>.block-container{padding-top:3rem!important;padding-bottom:7rem!important;} h3{font-size:26px!important;font-weight:bold;margin-bottom:0px; padding-bottom:0px;} .sub-title{font-size:22px!important;font-weight:bold;margin:25px 0 10px;} .main-table{width:100%;border-collapse:collapse;font-size:15px;text-align:center;margin-bottom:10px;} .main-table th{background-color:#f2f2f2;padding:10px;border:1px solid #ddd;font-weight:bold!important; vertical-align:middle;} .main-table td{padding:8px;border:1px solid #ddd;vertical-align:middle;} .sum-row td{background-color:#fff9e6;font-weight:bold!important;} .red{color:#FF2323!important;} .blue{color:#0047EB!important;} .insight-container{display:flex; gap:20px; align-items:stretch; margin-bottom:20px;} .insight-left{flex:0 0 46%; display:flex; flex-direction:column;} .insight-right{flex:1; display:flex; flex-direction:column;} .card-main{background-color:#fffdf2; border:2px solid #e8dbad; border-radius:18px; padding:18px 22px 15px 22px; position:relative; box-shadow:0 2px 6px rgba(0,0,0,0.03); height:100%; box-sizing:border-box; display:flex; flex-direction:column; justify-content:space-between;} .grid-2x2{display:grid; grid-template-columns:1fr 1fr; grid-template-rows:1fr 1fr; gap:15px; height:100%;} .card-sub{background:#fff; border:1.5px solid #ddd; border-radius:16px; box-shadow:0 1px 4px rgba(0,0,0,0.02); display:flex; flex-direction:column; padding:10px 15px;} .insight-bottom-box{background:#fff; border:1.5px solid #ddd; border-radius:18px; padding:25px; box-shadow:0 1px 4px rgba(0,0,0,0.02); font-size:15.5px; line-height:1.8; color:#333; margin-top:5px; margin-bottom:25px;} .summary-text{font-size:16px!important; font-weight:bold!important; color:#333; margin-bottom:10px;} .summary-val{font-size:20px!important;} .main-table th.th-eval{border-right:none!important;} .main-table th.th-blank{border-left:none!important; border-bottom:none!important; padding:0!important;} .main-table th.th-week{border-left:1px solid #ddd!important; border-top:1px solid #ddd!important; font-size:13.5px;} div[role="radiogroup"] label{font-size:15.5px!important; margin-bottom:8px!important;} .zappa-icon{font-family:"Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji",sans-serif!important; font-size:32px!important;} div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu), div[data-testid="column"]:has(span#zappa-floating-menu){position:fixed!important; bottom:30px!important; right:30px!important; left:auto!important; transform:none!important; width:max-content!important; min-width:0!important; background:rgba(255,255,255,0.98)!important; padding:10px 25px!important; border-radius:8px!important; box-shadow:0 4px 15px rgba(0,0,0,0.15)!important; border:1px solid #e5e7eb!important; z-index:999999!important; display:flex!important; flex-wrap:nowrap!important; align-items:center!important; justify-content:center!important; gap:14px!important;} div.element-container:has(span#zappa-floating-menu){display:none!important;} div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) > div{min-width:0!important; width:auto!important; padding:0!important; margin:0!important; flex:0 0 auto!important; border-right:none!important;} div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button{margin:0!important; padding:0 5px!important; width:auto!important; background:transparent!important; border:none!important; border-radius:0!important; height:26px!important; min-height:26px!important; color:#9ca3af!important; font-size:15px!important; font-weight:normal!important; white-space:nowrap!important; box-shadow:none!important; display:flex!important; align-items:center!important; justify-content:center!important;} div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button p{color:inherit!important; font-size:14.5px!important; font-weight:inherit!important; margin:0!important; padding:0!important; line-height:1!important; text-align:center!important; white-space:nowrap!important;} div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button:hover{color:#111111!important; background:transparent!important;} div[data-testid="stHorizontalBlock"]:has(span#zappa-floating-menu) button[kind="primary"]{background:transparent!important; border:none!important; color:#111111!important; font-weight:bold!important;}</style>"""
st.markdown(css, unsafe_allow_html=True)

if 'sort_mode' not in st.session_state: st.session_state.sort_mode = 'init'
if 'show_code' not in st.session_state: st.session_state.show_code = False
if 'init' not in st.session_state:
    with st.spinner("데이터 업데이트 중..."): andy_pension_v2.generate_asset_data()
    st.session_state['init'] = True
    st.cache_data.clear()

def fmt(v, sign=False):
    try:
        val = int(float(v))
        return f"+{val:,}" if sign and val > 0 else f"{val:,}"
    except: return str(v)

def fmt_p(v):
    try:
        val = float(v)
        return f"▲{val:.2f}%" if val > 0 else (f"▼{abs(val):.2f}%" if val < 0 else "0.00%")
    except: return str(v)

def col(v):
    try: return "red" if float(v) > 0 else ("blue" if float(v) < 0 else "")
    except: return ""

def clean_label(lbl): return re.sub(r'\s*\(\d{2}\.\d+월\)', '', lbl)
def short_name(nm): return nm[:13] + "***" if len(nm) > 13 else nm

@st.cache_data(ttl=60)
def load():
    try:
        with open('assets.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

data = load()
if not data: st.stop()
tot = data.get("_total", {})

with st.sidebar:
    st.markdown("<div style='display:flex; align-items:center; gap:10px; margin-bottom:20px;'><span class='zappa-icon'>🤖</span><span style='font-size:24px; font-weight:bold; color:#111; letter-spacing: -0.5px;'>ZAPPA MENU</span></div>", unsafe_allow_html=True)
    menu = st.radio("카테고리 선택", ("1. 복합 대시보드", "2. 절세 계좌", "3. 일반 계좌", "4. Quant 매매", "5. 가상자산"), index=1, label_visibility="collapsed")
    st.markdown("<hr style='margin:25px 0 20px 0; border: none; border-top: 1px dashed #ccc;'>", unsafe_allow_html=True)
    
    t_asset_all = tot.get('총 자산', tot.get('총자산', 0)); t_profit_all = tot.get('총 수익', tot.get('총 손익', 0)); t_rate_all = tot.get('수익률(%)', 0)
    st.markdown(f"<div style='background-color: #f8f9fa; border-radius: 12px; padding: 18px 15px; border: 1px solid #eaeaea;'><div style='font-size:13.5px; font-weight:bold; color:#777; margin-bottom:8px;'>⚡ 퀵 뷰 (전체 자산 현황)</div><div style='font-size:24px; font-weight:600; color:#111; letter-spacing:-0.5px; line-height: 1.1;'>{fmt(t_asset_all)}<span style='font-size:16px; font-weight:normal; margin-left:2px;'>원</span></div><div style='font-size:14px; margin-top:8px; color:#555;'>총 손익: <span class='{col(t_profit_all)}' style='font-weight:bold;'>{fmt(t_profit_all, True)}</span> ({fmt_p(t_rate_all)})</div></div>", unsafe_allow_html=True)

if menu != "2. 절세 계좌":
    st.markdown(f"<h3 style='margin-top: 5px;'>🚧 {menu[3:]} (준비 중)</h3>", unsafe_allow_html=True)
    st.info("💡 해당 메뉴의 대시보드가 곧 구축될 예정입니다.")
else:
    c1, c2 = st.columns([8.5, 1.5])
    with c1: st.markdown("<h3 style='margin-top: 5px;'>🚀 이상혁(Andy lee)님 [절세계좌] 통합 대시보드</h3>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 업데이트", use_container_width=True): andy_pension_v2.generate_asset_data(); st.cache_data.clear(); st.rerun()

    st.markdown(f"<div style='text-align:right;font-size:14.5px;color:#555;font-weight:normal;margin:-10px 0 15px;'>[ {tot.get('조회시간', '업데이트 필요')} ]</div>", unsafe_allow_html=True)

    FIXED_ACCOUNT_ORDER = ['DC', 'IRP', 'PENSION', 'ISA']
    OPEN_DATES = {'DC': '[ 2025.08 ]', 'IRP': '[ 2025.08 ]', 'PENSION': '[ 2025.11 ]', 'ISA': '[ 2025.08 ]'}

    if "_insight" in data:
        t_asset = tot.get('총 자산', 0); t_profit = tot.get('총 수익', tot.get('총 손익', 0)); t_diff = tot.get('평가손익(1일전)', 0); t_diff_7 = tot.get('평가손익(7일전)', 0); t_rate = tot.get('수익률(%)', 0); t_original_sum = tot.get('원금합', 0)
        cash_total = 0; ovs_total = 0; dom_total = 0; all_items = []
        
        for k in FIXED_ACCOUNT_ORDER:
            if k in data:
                short_acc_name = 'DC' if k == 'DC' else ('IRP' if k == 'IRP' else ('CMA' if k == 'PENSION' else 'ISA'))
                for item in data[k].get('상세', []):
                    if item.get('종목명') == '[ 합계 ]': continue
                    it_copy = item.copy(); it_copy['계좌'] = short_acc_name; all_items.append(it_copy)
                    val = item.get('총 자산', 0); nm = item.get('종목명', '').lower()
                    if any(kw in nm for kw in ['현금성자산', 'mmf']): cash_total += val
                    elif any(kw in nm for kw in ['tiger', 's&p', '나스닥', '필라델피아', '다우존스', 'ai테크']): ovs_total += val
                    else: dom_total += val

        exclude_kws = ["현금성자산", "삼성화재", "삼성신종종류형"]
        tradeable_items = [it for it in all_items if not any(kw in it.get("종목명", "") for kw in exclude_kws)]
        tradeable_items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
        best_5 = tradeable_items[:5]; worst_5 = tradeable_items[::-1][:5]

        # [핵심 로직] 전일비 상승/하락 카운팅 및 리스트업
        rise_cnt, fall_cnt, flat_cnt = 0, 0, 0
        major_rise_list, major_fall_list = [], []
        for it in tradeable_items:
            d_rate = it.get('전일비(%)', 0.0) 
            nm = short_name(it.get('종목명', ''))
            if d_rate >= 0.5:
                rise_cnt += 1
                if d_rate >= 3.0: major_rise_list.append(f"{nm}(▲{d_rate:.2f}%)")
            elif d_rate <= -0.5:
                fall_cnt += 1
                if d_rate <= -3.0: major_fall_list.append(f"{nm}(▼{abs(d_rate):.2f}%)")
            else: flat_cnt += 1
                
        str_m_rise = ", ".join(major_rise_list) if major_rise_list else "없음"
        str_m_fall = ", ".join(major_fall_list) if major_fall_list else "없음"

        p_cash = (cash_total / t_asset * 100) if t_asset > 0 else 0
        p_ovs = (ovs_total / t_asset * 100) if t_asset > 0 else 0
        p_dom = (dom_total / t_asset * 100) if t_asset > 0 else 0
        p_dc = (data.get('DC', {}).get('총 자산', 0) / t_asset * 100) if t_asset > 0 else 0
        p_irp = (data.get('IRP', {}).get('총 자산', 0) / t_asset * 100) if t_asset > 0 else 0
        p_pension = (data.get('PENSION', {}).get('총 자산', 0) / t_asset * 100) if t_asset > 0 else 0
        p_isa = (data.get('ISA', {}).get('총 자산', 0) / t_asset * 100) if t_asset > 0 else 0
        prog_pct = (t_asset / 1000000000) * 100

        def render_bar(p, color):
            return f"<div style='width: {p}%; background-color: {color}; height: 100%; display: flex; align-items: center; justify-content: center; position: relative;'><span style='position: absolute; font-size: 13px; color: #333; z-index: 10; white-space: nowrap;'>{p:.0f}%</span></div>" if p > 0 else ""

        acc_rates = [(k, data[k].get('수익률(%)', 0)) for k in FIXED_ACCOUNT_ORDER if k in data]
        acc_rates.sort(key=lambda x: x[1], reverse=True)
        b_acc_name = '퇴직연금(IRP)' if acc_rates[0][0]=='IRP' else ('퇴직연금(DC)' if acc_rates[0][0]=='DC' else ('연금저축(CMA)' if acc_rates[0][0]=='PENSION' else 'ISA(중개형)'))
        b_acc_rate = acc_rates[0][1] if acc_rates else 0
        b1_nm = short_name(best_5[0]['종목명']) if best_5 else "주도 종목"
        w1_nm = short_name(worst_5[0]['종목명']) if worst_5 else "부진 종목"

        z_html = f"<div style='font-size: 14.5px; line-height: 1.85; color: #444; padding-left: 0px;'>"
        z_html += f"<div style='margin-bottom: 22px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> 계좌 현황 및 종목 분석</span><div style='letter-spacing: -0.2px;'>"
        z_html += f"총 <strong>{len(tradeable_items)}개</strong> 종목 중 전일비 상승 종목은 <strong>{rise_cnt}개</strong> (▲3%p↑ {len(major_rise_list)}개), 하락 종목은 <strong>{fall_cnt}개</strong>(▼3%p↓ {len(major_fall_list)}개) 이고 <strong>{flat_cnt}개</strong> 종목은 횡보입니다.<br>"
        z_html += f"<span style='font-size:12.5px; color:#888;'>(#전일비 ±0.5%p 이내는 횡보합으로 간주, 0.5%p 이상 상승시 상승 종목, -0.5%p 이하 하락시 하락 종목으로 간주#)</span><br>"
        z_html += f"<span style='font-size:13.5px; color:#555;'>※ ▲3%p↑ 종목 : {str_m_rise}<br>※ ▼3%p↓ 종목 : {str_m_fall}</span><br><br>"
        z_html += f"현재 <strong>{b_acc_name} 계좌</strong>가 전체 수익률(<span class='{col(b_acc_rate)}' style='font-weight:bold;'>{fmt_p(b_acc_rate)}</span>) 1위를 기록하며 하방을 견인 중입니다. 개별 종목에서는 <strong>{b1_nm}</strong>가 시장 트렌드를 주도하며 효자 역할을 수행 중이나, <strong>{w1_nm}</strong> 등 일부 섹터는 외부 매크로 요인에 의해 단기 조정을 겪고 있습니다.</div></div>"
        z_html += f"<div style='margin-bottom: 0px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> 주식 시황 및 향후 대응 전략</span><div style='letter-spacing: -0.2px;'>간밤 최근 미국 KCE/PCE 물가 지표의 끈적한 흐름과 주요 빅테크 기업들의 실적 가이던스 조정이 겹치며 변동성이 발생했으나, 한국 증시는 밸류업 호재로 하방을 지지 중입니다. <strong>현금({p_cash:.0f}%) 비중을 선제적으로 확보</strong>하여 우량주 리밸런싱을 권고합니다.</div></div></div>"

        st.markdown("<div class='sub-title' style='margin-bottom: 15px;'>💡 ZAPPA의 [절세계좌] 자산 현황 보고</div>", unsafe_allow_html=True)
        donut_html = f"<div style='position: relative; width: 130px; height: 130px; border-radius: 50%; background: conic-gradient(#ffffff 0% {p_cash}%, #d9d9d9 {p_cash}% {p_cash+p_ovs}%, #8c8c8c {p_cash+p_ovs}% 100%); box-shadow: inset 0 0 8px rgba(0,0,0,0.1); border: 1px solid #d0d0d0; flex-shrink: 0; margin-top: -12px;'><div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 35%; height: 35%; background-color: #fffdf2; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.05);'></div><div style='position: absolute; top: 3%; left: 50%; transform: translateX(-50%); font-size: 12.5px; color: #333; text-align: center; line-height: 1.2; font-weight: bold;'>{p_cash:.0f}%<br>현금성자산</div><div style='position: absolute; top: 28%; right: -12%; font-size: 12.5px; color: #333; text-align: center; line-height: 1.2; font-weight: bold;'>{p_ovs:.0f}%<br>해외투자</div><div style='position: absolute; bottom: 8%; left: 18%; font-size: 13px; color: #fff; font-weight: bold; text-align: center; line-height: 1.2; text-shadow: 0px 0px 3px rgba(0,0,0,0.5);'>{p_dom:.0f}%<br>국내투자</div></div>"

        html = ["<div style='text-align: right; font-size: 13px; color: #555; font-weight: bold; margin-bottom: 5px;'>단위 : 원화(KRW)</div><div class='insight-container'>"]
        html.append(f"<div class='insight-left'><div class='card-main'><div style='display: flex; flex-direction: column; margin-bottom: auto;'><div style='display: flex; justify-content: space-between; align-items: baseline;'><div style='font-size: 18px; font-weight: bold; color: #111; line-height: 1;'>총 자산</div><div style='font-size: 24px; font-weight: 600 !important; color: #111; line-height: 1;'>{fmt(t_asset)}<span style='font-size: 18px; font-weight: normal; margin-left: 2px;'>원</span></div></div><div style='display: flex; justify-content: flex-end; align-items: baseline; margin-top: 8px;'><div style='font-size: 13.5px; color: #777; font-weight: normal; line-height: 1;'>[ 전일비 <span class='{col(t_diff)}'>{fmt(t_diff, True)}</span> / 전주비 <span class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</span> ]</div></div></div><div style='display: flex; justify-content: space-between; align-items: center; margin-top: 10px; margin-bottom: 22px; padding-left: 15px;'>{donut_html}<div style='display: grid; grid-template-columns: auto auto; row-gap: 8px; column-gap: 15px; justify-content: end; align-items: baseline; width: 100%; margin-top: 18px;'><div style='color: #777; font-size: 14px; text-align: right; line-height: 22px;'>평가금액</div><div style='color: #111; font-size: 18px; font-weight: 400 !important; text-align: right; line-height: 22px;'>{fmt(t_asset - cash_total)}</div><div style='color: #777; font-size: 14px; text-align: right; line-height: 22px;'>현금성자산</div><div style='color: #111; font-size: 18px; font-weight: 400 !important; text-align: right; line-height: 22px;'>{fmt(cash_total)}</div><div style='color: #777; font-size: 14px; font-weight: normal; text-align: right; line-height: 22px;'>총 손익</div><div style='text-align: right;'><div style='font-size: 18px; font-weight: bold; line-height: 1.1;' class='{col(t_profit)}'>{fmt(t_profit, True)}</div><div style='font-size: 14.5px; font-weight: 400 !important; margin-top: 0px; line-height: 1.3;' class='{col(t_rate)}'>{fmt_p(t_rate)}</div></div></div></div><div><div style='display: flex; height: 20px; width: 100%; border-radius: 4px; border: 1px solid #ccc; margin-bottom: 6px; overflow: hidden;'>{render_bar(p_dc, '#b4a7d6')}{render_bar(p_irp, '#f4b183')}{render_bar(p_pension, '#a9d18e')}{render_bar(p_isa, '#ffd966')}</div><div style='display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #777; padding: 0 2px; margin-bottom: 16px;'><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#b4a7d6;'></div>퇴직연금(DC)</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#f4b183;'></div>퇴직연금(IRP)</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#a9d18e;'></div>연금저축(CMA)</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#ffd966;'></div>ISA(중개형)</div></div><div style='padding: 10px 15px; background: rgba(255,255,255,0.5); border-radius: 10px; border: 1px solid #e8dbad;'><div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'><span style='font-size: 14px; color: #777; font-weight: normal;'>🎯 은퇴 자산 목표 10억 달성률 <span style='font-size: 13.5px; color: #888;'>(* 원금 : {fmt(t_original_sum)})</span></span><span style='font-size: 14px; font-weight: bold; color: #4a90e2;'>{prog_pct:.1f}%</span></div><div style='width: 100%; height: 6px; background-color: #e2e2e2; border-radius: 3px; overflow: hidden;'><div style='width: {prog_pct}%; height: 100%; background: linear-gradient(90deg, #9bc2e6, #4a90e2);'></div></div></div></div></div></div>")
        
        html.append("<div class='insight-right'><div class='grid-2x2'>")
        for k in FIXED_ACCOUNT_ORDER:
            if k in data:
                a = data[k]
                a_nm = '퇴직연금(DC)' if k == 'DC' else ('퇴직연금(IRP)' if k == 'IRP' else ('연금저축(CMA)' if k == 'PENSION' else 'ISA(중개형)'))
                cnt = len([i for i in a.get('상세', []) if i.get('종목명') != '[ 합계 ]' and '현금' not in i.get('종목명', '') and '삼성신종' not in i.get('종목명', '')])
                html.append(f"<div class='card-sub'><div><div style='text-align: right; font-size: 13.5px; color: #666; font-weight: normal; margin-bottom: -2px; line-height: 1;'>{OPEN_DATES.get(k, '')}</div><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 2px;'>{a_nm}</div><div style='border-bottom: 1px solid #eee; margin-bottom: 6px; margin-top: 2px;'></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 자산</span><span style='font-size: 16px; color: #111; font-weight: normal;'>{fmt(a.get('총 자산', 0))}</span></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 손익</span><div style='text-align: right; line-height: 1.2;'><div class='{col(a.get('총 수익', 0))}' style='font-size: 16px; font-weight: normal;'>{fmt(a.get('총 수익', 0), True)}</div><div class='{col(a.get('수익률(%)', 0))}' style='font-size: 14px; font-weight: normal; margin-top: 1px;'>{fmt_p(a.get('수익률(%)', 0))}</div></div></div></div><div style='font-size: 13.5px; color: #666; font-weight: normal; margin-top: auto; padding-top: 2px; display: flex; justify-content: space-between; align-items: baseline;'><span>* 원금 : {fmt(a.get('원금', 0))}</span><span><span style='font-size: 16px; font-weight: bold; color: #111;'>{cnt}</span> 종목</span></div></div>")
        html.append("</div></div></div>")
        
        html.append("<div class='insight-bottom-box' style='display: flex; gap: 20px; align-items: stretch;'><div style='flex: 1; padding-right: 15px; border-right: 1px solid #eaeaea;'><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 8px;'>📈 손익률 우수종목 (TOP 5)</div><table class='main-table' style='margin-bottom: 20px; font-size: 13.5px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>계좌</th></tr>")
        for idx, it in enumerate(best_5): html.append(f"<tr><td>{idx+1}</td><td>{short_name(it.get('종목명', ''))}</td><td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td><td>{it.get('계좌','')}</td></tr>")
        html.append("</table><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px;'>📉 손익률 부진종목</div><table class='main-table' style='margin-bottom: 0px; font-size: 13.5px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>계좌</th></tr>")
        for idx, it in enumerate(worst_5): html.append(f"<tr><td>{idx+1}</td><td>{short_name(it.get('종목명', ''))}</td><td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td><td>{it.get('계좌','')}</td></tr>")
        html.append(f"</table></div><div style='flex: 1.1; padding-left: 5px;'><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 8px;'>💡 시황 및 향후 전망</div>{zappa_html}</div></div>")
        st.markdown("".join(html).replace("\n", ""), unsafe_allow_html=True)

    # =====================================================================
    # 하단 상세 데이터 테이블 섹션
    # =====================================================================
    unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"

    st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> / 총 손익 : <span class='summary-val {col(t_profit)}'>{fmt(t_profit, True)} ({fmt_p(t_rate)})</span></div></div>", unsafe_allow_html=True)

    h1_table = """<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>투자원금</th></tr><tr><th class='th-week'>7일전</th><th class='th-week'>15일전</th><th class='th-week'>30일전</th></tr>"""
    h1_table = re.sub(r'\n\s*', '', h1_table)
    h1 = [unit_html, h1_table]
    h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(t_asset)}</td><td class='{col(t_profit)}'>{fmt(t_profit, True)}</td><td class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</td><td class='{col(tot.get('평가손익(15일전)', 0))}'>{fmt(tot.get('평가손익(15일전)', 0), True)}</td><td class='{col(tot.get('평가손익(30일전)', 0))}'>{fmt(tot.get('평가손익(30일전)', 0), True)}</td><td class='{col(t_rate)}'>{fmt_p(t_rate)}</td><td>{fmt(t_original_sum)}</td></tr>")

    keys_1 = [k for k in FIXED_ACCOUNT_ORDER if k in data]
    if st.session_state.sort_mode == 'asset': keys_1.sort(key=lambda k: data.get(k, {}).get('총 자산', 0), reverse=True)
    elif st.session_state.sort_mode == 'profit': keys_1.sort(key=lambda k: data.get(k, {}).get('총 수익', 0), reverse=True)
    elif st.session_state.sort_mode == 'rate': keys_1.sort(key=lambda k: data.get(k, {}).get('수익률(%)', 0), reverse=True)

    for k in keys_1:
        a = data[k]
        h1.append(f"<tr><td>{clean_label(a.get('label', ''))}</td><td>{fmt(a.get('총 자산',0))}</td><td class='{col(a.get('총 수익',0))}'>{fmt(a.get('총 수익',0), True)}</td><td class='{col(a.get('평가손익(7일전)',0))}'>{fmt(a.get('평가손익(7일전)',0), True)}</td><td class='{col(a.get('평가손익(15일전)',0))}'>{fmt(a.get('평가손익(15일전)',0), True)}</td><td class='{col(a.get('평가손익(30일전)',0))}'>{fmt(a.get('평가손익(30일전)',0), True)}</td><td class='{col(a.get('수익률(%)',0))}'>{fmt_p(a.get('수익률(%)',0))}</td><td>{fmt(a.get('원금',0))}</td></tr>")
    h1.append("</table>")
    st.markdown("".join(h1), unsafe_allow_html=True)

    ag_tot = t_asset - tot.get('매입금액합', 0)
    ay_tot = (ag_tot / tot.get('매입금액합', 1) * 100) if tot.get('매입금액합', 1) > 0 else 0

    st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> / 총 손익 : <span class='summary-val {col(ag_tot)}'>{fmt(ag_tot, True)} ({fmt_p(ay_tot)})</span></div>", unsafe_allow_html=True)

    h2_table = """<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>매입금액</th></tr><tr><th class='th-week'>전일비</th><th class='th-week'>전주비</th><th class='th-week'>전월비</th></tr>"""
    h2 = [unit_html, re.sub(r'\n\s*', '', h2_table)]
    h2.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(t_asset)}</td><td class='{col(ag_tot)}'>{fmt(ag_tot, True)}</td><td class='{col(t_diff)}'>{fmt(t_diff, True)}</td><td class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</td><td class='{col(tot.get('평가손익(30일전)',0))}'>{fmt(tot.get('평가손익(30일전)',0), True)}</td><td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td><td>{fmt(tot.get('매입금액합', 0))}</td></tr>")

    sec2_items = []
    for k in FIXED_ACCOUNT_ORDER:
        if k in data:
            a = data[k]; ag_acc = sum(i.get('평가손익', 0) for i in a.get('상세', []) if i.get('종목명') != '[ 합계 ]')
            curr_asset = a.get('총 자산', 0); ap_acc = curr_asset - ag_acc; ay_acc = (ag_acc / ap_acc * 100) if ap_acc > 0 else 0
            sec2_items.append({'k': k, 'a': a, 'ag_acc': ag_acc, 'ap_acc': ap_acc, 'ay_acc': ay_acc, 'curr_asset': curr_asset})

    if st.session_state.sort_mode == 'asset': sec2_items.sort(key=lambda x: x['curr_asset'], reverse=True)
    elif st.session_state.sort_mode == 'profit': sec2_items.sort(key=lambda x: x['ag_acc'], reverse=True)
    elif st.session_state.sort_mode == 'rate': sec2_items.sort(key=lambda x: x['ay_acc'], reverse=True)

    for item in sec2_items:
        a = item['a']
        h2.append(f"<tr><td>{clean_label(a.get('label', ''))}</td><td>{fmt(item['curr_asset'])}</td><td class='{col(item['ag_acc'])}'>{fmt(item['ag_acc'], True)}</td><td class='{col(a.get('평가손익(1일전)',0))}'>{fmt(a.get('평가손익(1일전)',0), True)}</td><td class='{col(a.get('평가손익(7일전)',0))}'>{fmt(a.get('평가손익(7일전)',0), True)}</td><td class='{col(a.get('평가손익(30일전)',0))}'>{fmt(a.get('평가손익(30일전)',0), True)}</td><td class='{col(item['ay_acc'])}'>{fmt_p(item['ay_acc'])}</td><td>{fmt(item['ap_acc'])}</td></tr>")
    h2.append("</table>")
    st.markdown("".join(h2), unsafe_allow_html=True)

    st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
    b1, b2, b3, b4, b5 = st.columns(5)
    with b1: st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True); st.button("🛠️ 초기화 [ ● ]" if st.session_state.sort_mode == 'init' else "🛠️ 초기화 [ ○ ]", type="primary" if st.session_state.sort_mode == 'init' else "secondary", on_click=lambda: setattr(st.session_state, 'sort_mode', 'init'))
    with b2: st.button("💰 총 자산 [ ● ]" if st.session_state.sort_mode == 'asset' else "💰 총 자산 [ ○ ]", type="primary" if st.session_state.sort_mode == 'asset' else "secondary", on_click=lambda: setattr(st.session_state, 'sort_mode', 'asset'))
    with b3: st.button("📊 평가손익 [ ● ]" if st.session_state.sort_mode == 'profit' else "📊 평가손익 [ ○ ]", type="primary" if st.session_state.sort_mode == 'profit' else "secondary", on_click=lambda: setattr(st.session_state, 'sort_mode', 'profit'))
    with b4: st.button("📈 손익률 [ ● ]" if st.session_state.sort_mode == 'rate' else "📈 손익률 [ ○ ]", type="primary" if st.session_state.sort_mode == 'rate' else "secondary", on_click=lambda: setattr(st.session_state, 'sort_mode', 'rate'))
    with b5: st.button("💻 종목코드 [ + ]" if st.session_state.show_code else "💻 종목코드 [ - ]", type="primary" if st.session_state.show_code else "secondary", on_click=lambda: setattr(st.session_state, 'show_code', not st.session_state.show_code))

    st.markdown("<br>", unsafe_allow_html=True)
    t3_lbl = {'DC':'퇴직연금(DC)계좌 / (삼성증권 7165962472-28)', 'PENSION':'연금저축(CMA)계좌 / (삼성증권 7169434836-15)', 'ISA':'ISA(중개형)계좌 / (키움증권 6448-4934)', 'IRP':'퇴직연금(IRP)계좌 / (삼성증권 7164499007-29)'}

    for k in FIXED_ACCOUNT_ORDER:
        if k not in data: continue
        a = data[k]
        with st.expander(f"📂 [ {t3_lbl.get(k, a.get('label', ''))} ] 종목별 현황", expanded=False):
            s_data = next((i for i in a.get('상세', []) if i.get('종목명') == "[ 합계 ]"), {})
            ex_html = ""
            if k in ['DC', 'IRP']:
                safe_pct = sum(item.get('비중', 0) for item in a.get('상세', []) if (k == 'DC' and item.get('종목명') in ['삼성화재 퇴직연금(3.05%/年)', '현금성자산']) or (k == 'IRP' and item.get('종목명') == '현금성자산'))
                ex_html = f"<div style='font-size:14.5px; font-weight:normal; color:#555;'>[ 위험자산 : {100.0 - safe_pct:.1f}% | 안전자산 : {safe_pct:.1f}% ]</div>"
            
            curr_asset = a.get('총 자산', 0); a_prof = s_data.get('평가손익', 0); a_rate = s_data.get('수익률(%)', 0)
            st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(curr_asset)}</span> / 총 손익 : <span class='summary-val {col(a_prof)}'>{fmt(a_prof, True)} ({fmt_p(a_rate)})</span></div>{ex_html}</div>", unsafe_allow_html=True)
            
            h3_table = f"<table class='main-table'><tr><th>종목명</th>{'<th>종목코드</th>' if st.session_state.show_code else ''}<th>비중</th><th>총 자산</th><th>평가손익</th><th>전일비(%)</th><th>손익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>"
            h3 = [unit_html, h3_table]
            items = [i for i in a.get('상세', []) if i.get('종목명') != "[ 합계 ]"]
            
            if st.session_state.sort_mode == 'asset': items.sort(key=lambda x: x.get('총 자산', 0), reverse=True)
            elif st.session_state.sort_mode == 'profit': items.sort(key=lambda x: x.get('평가손익', 0), reverse=True)
            elif st.session_state.sort_mode == 'rate': items.sort(key=lambda x: x.get('수익률(%)', 0), reverse=True)
            
            for i in ([s_data] + items):
                is_s = (i.get('종목명') == "[ 합계 ]")
                row = f"<tr class='sum-row'>" if is_s else "<tr>"
                row += f"<td>{i.get('종목명', '')}</td>"
                if st.session_state.show_code: row += f"<td>{'-' if is_s or i.get('코드','-')=='-' else i.get('코드', '')}</td>"
                row += f"<td>{i.get('비중',0):.1f}%</td><td>{fmt(i.get('총 자산', 0))}</td><td class='{col(i.get('평가손익',0))}'>{fmt(i.get('평가손익',0), True)}</td><td class='{col(i.get('전일비(%)',0))}'>{fmt_p(i.get('전일비(%)',0))}</td><td class='{col(i.get('수익률(%)',0))}'>{fmt_p(i.get('수익률(%)',0))}</td><td>{fmt(i.get('수량','-'))}</td><td>{fmt(i.get('매입가','-'))}</td><td>{fmt(i.get('현재가','-'))}</td></tr>"
                h3.append(row)
            h3.append("</table>")
            st.markdown("".join(h3), unsafe_allow_html=True)
