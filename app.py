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

/* =========================================================
   [추가 CSS] 요약 텍스트 정밀 디자인
   ========================================================= */
.summary-text {
    font-size: 16px !important;
    font-weight: bold !important;
    color: #333;
    margin-bottom: 10px;
}
.summary-val {
    font-size: 20px !important; 
}

/* =========================================================
   [문제 해결 1] 평가손익 & 기간비용 엑셀 스타일 병합
   ========================================================= */
.main-table th.th-eval { border-right: none !important; }
.main-table th.th-blank { border-left: none !important; border-bottom: none !important; padding: 0 !important; }
.main-table th.th-week { border-left: 1px solid #ddd !important; border-top: 1px solid #ddd !important; font-size: 13.5px; }

/* =========================================================
   [문제 해결 2] 컬러 이모지 강제 주입
   ========================================================= */
.zappa-icon {
    font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif !important;
    font-size: 32px !important;
}

/* =========================================================
   [ZAPPA 플로팅 배너 CSS] 완벽한 픽셀 단위 간격 통일 🔥
   ========================================================= */
div[data-testid="stColumns"]:has(#zappa-floating-menu),
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) {
    position: fixed !important;
    bottom: 30px !important;
    right: 30px !important;
    left: auto !important;
    transform: none !important;
    
    width: max-content !important; 
    
    background: rgba(255, 255, 255, 0.98) !important;
    padding: 10px 25px !important; 
    border-radius: 8px !important; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important;
    border: 1px solid #e5e7eb !important;
    z-index: 999999 !important;
    
    display: flex !important;
    flex-wrap: nowrap !important; 
    align-items: center !important; 
    justify-content: center !important; 
    
    gap: 14px !important; /* 기본 간격 */
}

div.element-container:has(#zappa-floating-menu) { 
    display: none !important; 
    position: absolute !important; 
    width: 0 !important; 
    height: 0 !important; 
    margin: 0 !important; 
    padding: 0 !important; 
}

div[data-testid="stColumns"]:has(#zappa-floating-menu) > div[data-testid="stColumn"],
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) > div[data-testid="stColumn"] { 
    flex: 0 0 auto !important; 
    width: auto !important; 
    min-width: 0 !important; 
    padding: 0 !important; 
    margin: 0 !important; 
    display: flex !important; 
    align-items: center !important; 
    justify-content: center !important; 
    position: relative !important; 
    border-right: none !important; 
}

div[data-testid="stColumns"]:has(#zappa-floating-menu) div[data-testid="stButton"],
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) div[data-testid="stButton"],
div[data-testid="stColumns"]:has(#zappa-floating-menu) button,
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) button { 
    margin: 0 !important; 
    padding: 0 !important; 
    width: auto !important; 
    background: transparent !important; 
    border: none !important; 
    border-radius: 0 !important; 
    height: 24px !important; 
    min-height: 24px !important; 
    color: #9ca3af !important; 
    font-size: 15px !important; 
    font-weight: normal !important; 
    white-space: nowrap !important; 
    box-shadow: none !important; 
    transition: color 0.1s ease !important; 
    display: flex !important; 
    align-items: center !important; 
    justify-content: center !important; 
}

div[data-testid="stColumns"]:has(#zappa-floating-menu) button p,
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) button p { 
    color: inherit !important; 
    font-size: 14.5px !important; 
    font-weight: inherit !important; 
    margin: 0 !important; 
    padding: 0 !important; 
    line-height: 1 !important; 
    text-align: center !important; 
    width: max-content !important; 
    white-space: nowrap !important;
}

div[data-testid="stColumns"]:has(#zappa-floating-menu) button:hover,
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) button:hover { 
    color: #111111 !important; 
    background: transparent !important; 
}

div[data-testid="stColumns"]:has(#zappa-floating-menu) button[kind="primary"],
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) button[kind="primary"] { 
    background: transparent !important; 
    border: none !important; 
    color: #111111 !important; 
    font-weight: bold !important; 
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

# ==========================================
# 좌측 ZAPPA 엔진 로직
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style='display:flex; align-items:center; gap:10px; margin-bottom:20px;'>
            <span class='zappa-icon'>🤖</span>
            <span style='font-size:22px; font-weight:bold; color:#333;'>ZAPPA AI 코딩 엔진</span>
        </div>
    """, unsafe_allow_html=True)
    
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

# [신규] 인사이트 문단용 색상/기호 HTML 포맷 함수
def get_html_val(v, is_percent=False):
    color_class = col(v)
    if is_percent:
        text = fmt_p(v)
    else:
        text = fmt(v, sign=True)
    if color_class:
        return f"<span class='{color_class}'>{text}</span>"
    return str(text)

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

c1, c2 = st.columns([8.5, 1.5])
with c1: st.markdown("<h3>🚀 이상혁(Andy lee)님 [절세계좌] 통합 대시보드</h3>", unsafe_allow_html=True)
with c2:
    if st.button("🔄 업데이트", use_container_width=True):
        andy_pension_v2.generate_asset_data(); st.cache_data.clear(); st.rerun()

st.markdown(f"<div style='text-align:right;font-size:14px;color:#555;margin:-10px 0 10px;'>[{tot.get('조회시간')}]</div>", unsafe_allow_html=True)

# --- 계좌 노출 순서 기본값 ---
FIXED_ACCOUNT_ORDER = ['DC', 'IRP', 'PENSION', 'ISA']

# =====================================================================
# 💡 [핵심 수정부] 자파의 자산 인사이트 생성 로직
# =====================================================================
if "_insight" in data:
    ins = ["<div class='insight-box'><span class='box-title'>💡 자파의 [절세계좌] 자산 현황 보고</span>"]
    
    ag_tot = tot.get('총 자산', 0) - tot.get('매입금액합', 0)
    ay_tot = (ag_tot / tot.get('매입금액합', 1) * 100) if tot.get('매입금액합', 1) > 0 else 0
    origin_yield = tot.get('손익률(%)', 0)

    # 볼드 및 16px 스타일 함수 적용
    def bold_16(text):
        return f"<span style='font-weight:bold; font-size:16px;'>{text}</span>"

    # [문단 1] 자산 총액
    p1_v1 = f"{fmt(tot.get('총 자산',0))}원"
    p1_v2 = f"{get_html_val(tot.get('총 손익',0), False)}원 ({get_html_val(origin_yield, True)})"
    p1_v3 = f"{get_html_val(ag_tot, False)}원({get_html_val(ay_tot, True)})"
    
    # 텍스트 수정: '총 수익' -> '총 손익'
    ins.append(f"<p style='margin-bottom:6px; font-size:15.5px;'>• 현재 총 자산 '{bold_16(p1_v1)}' |  투자원금比 총 손익 '{bold_16(p1_v2)}' | 매입금액比 총 손익 '{bold_16(p1_v3)}'</p>")

    # [문단 2] 손익률 높은 순서
    def format_mil(v):
        abs_v = abs(v)
        if abs_v >= 10000000:
            res = round(v / 1000000, 1)
            txt = f"+{res:.1f}백만" if v > 0 else f"{res:.1f}백만"
        else:
            res = round(v / 1000000, 2)
            txt = f"+{res:.2f}백만" if v > 0 else f"{res:.2f}백만"
        return txt

    order_str = []
    # DC, IRP, CMA, ISA 고정 순서로 나열
    for k in ['DC', 'IRP', 'PENSION', 'ISA']:
        if k in data:
            a = data[k]
            ag_acc = sum(i.get('평가손익',0) for i in a.get('상세', []) if i.get('종목명') != '[ 합계 ]')
            ap_acc = a.get('총 자산',0) - ag_acc
            ay_acc = (ag_acc/ap_acc*100) if ap_acc > 0 else 0
            
            acc_name = '연금저축(CMA)' if k == 'PENSION' else ('ISA(중개형)' if k == 'ISA' else f'퇴직연금({k})')
            
            val_txt = format_mil(ag_acc)
            rate_txt = fmt_p(ay_acc)
            combined_txt = f"{val_txt}({rate_txt})"
            
            color_cls = col(ag_acc)
            colored_txt = f"<span class='{color_cls}'>{combined_txt}</span>" if color_cls else combined_txt
            
            order_str.append(f"{acc_name} '{bold_16(colored_txt)}'")

    rank_str = ", ".join(order_str)
    ins.append(f"<p style='margin-bottom:6px; font-size:15.5px;'>• 계좌별 평가손익 : {rank_str}</p>")

    # [문단 3, 4] 미국/한국 분류 및 종목 순위
    us_kws = ['미국', '나스닥', '다우', 's&p', '필라델피아', '테크']
    us_etfs = []
    stock_dict = {}
    
    for k in FIXED_ACCOUNT_ORDER:
        if k in data:
            acc_lbl = '연금저축(CMA)계좌' if k == 'PENSION' else ('ISA(중개형)계좌' if k == 'ISA' else f'퇴직연금({k})계좌')
            for item in data[k].get('상세', []):
                name = item.get('종목명', '')
                if name == '[ 합계 ]' or not name or any(x in name for x in ['현금', '삼성화재', 'MMF']): continue
                
                y = item.get('손익률(%)', 0)
                p = item.get('평가손익', 0)
                
                if name not in stock_dict: stock_dict[name] = []
                stock_dict[name].append({'acc': acc_lbl, 'y': y, 'p': p})
                
                if any(kw in name.lower() for kw in us_kws):
                    if name not in [x['name'] for x in us_etfs]: us_etfs.append({'name': name, 'y': y})

    us_str = ", ".join([f"{x['name']} {get_html_val(x['y'], True)}" for x in us_etfs])
    if us_str:
        ins.append(f"<p style='margin-bottom:6px; font-size:15.5px;'>• 미국 ETF 장기간 횡보 속에({us_str}) 코스피 등 한국 ETF가 전체 평가 손익을 주도하고 있습니다.</p>")

    sorted_stocks = sorted(stock_dict.items(), key=lambda x: max([info['y'] for info in x[1]]), reverse=True)
    
    def format_stock_info(stock_name, acc_list):
        sorted_accs = sorted(acc_list, key=lambda x: x['y'], reverse=True)
        acc_strs = [f"{info['acc']} {get_html_val(info['y'], True)}({format_mil(info['p'])})" for info in sorted_accs]
        return f"{stock_name} : {', '.join(acc_strs)}"

    if len(sorted_stocks) >= 5:
        top1 = format_stock_info(sorted_stocks[0][0], sorted_stocks[0][1])
        top2 = format_stock_info(sorted_stocks[1][0], sorted_stocks[1][1])
        top3 = format_stock_info(sorted_stocks[2][0], sorted_stocks[2][1])
        bot1 = format_stock_info(sorted_stocks[-2][0], sorted_stocks[-2][1])
        bot2 = format_stock_info(sorted_stocks[-1][0], sorted_stocks[-1][1])
        
        ins.append(f"<p style='margin-bottom:6px; font-size:15.5px; line-height:1.6;'>• 종목별로는 ① {top1}<br>&nbsp;&nbsp;&nbsp;&nbsp;② {top2}<br>&nbsp;&nbsp;&nbsp;&nbsp;③ {top3} 이 우수하고<br>&nbsp;&nbsp;&nbsp;&nbsp;상대적으로 ④ {bot1}<br>&nbsp;&nbsp;&nbsp;&nbsp;⑤ {bot2} 부진합니다.</p>")

    # [문단 5] 정적 분석 코멘트
    fast_ai_text = "• 간밤 미국 기술주와 나스닥 지수가 상승세를 보인 훈풍이 한국 증시로 이어지며, 코스피 관련 ETF 역시 동반 상승하는 강세장을 기록 중입니다. 현재의 긍정적 흐름을 유지하되 많이 오른 종목의 부분 익절을 통한 리밸런싱을 고려해 볼 시점입니다."
    ins.append(f"<p style='margin-bottom:0px; font-size:15.5px;'>{fast_ai_text}</p>")
    
    ins.append("</div>")
    st.markdown("".join(ins), unsafe_allow_html=True)


unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"

# =====================================================================
# (이하 Andy님 원본 1, 2, 3 테이블 출력 로직 100% 동일 보존)
# =====================================================================

# --- [1] 투자금 대비 자산 현황 ---
st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)

st.markdown(f"""
<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'>
    <div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(tot.get('총 자산',0))}</span> / 총 손익 : <span class='summary-val {col(tot.get('총 손익',0))}'>{fmt(tot.get('총 손익',0), True)} ({fmt_p(tot.get('손익률(%)',0))})</span></div>
    <div style='font-size:14.5px; font-weight:normal; color:#555;'>[ 25.8월 : 퇴직연금(DC/IRP), ISA(중개형), 25.11월 : 연금저축(CMA) ]</div>
</div>
""", unsafe_allow_html=True)

h1 = [unit_html, """
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
"""]

ty, tg, ta, to = tot.get('손익률(%)',0), tot.get('총 손익',0), tot.get('총 자산',0), tot.get('원금합',0)
td7_tot_1 = (ta - tot.get('평가손익(7일전)', 0)) - to
td15_tot_1 = (ta - tot.get('평가손익(15일전)', 0)) - to
td30_tot_1 = (ta - tot.get('평가손익(30일전)', 0)) - to

h1.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(ta)}</td><td class='{col(tg)}'>{fmt(tg, True)}</td><td class='{col(td7_tot_1)}'>{fmt(td7_tot_1, True)}</td><td class='{col(td15_tot_1)}'>{fmt(td15_tot_1, True)}</td><td class='{col(td30_tot_1)}'>{fmt(td30_tot_1, True)}</td><td class='{col(ty)}'>{fmt_p(ty)}</td><td>{fmt(to)}</td></tr>")

keys_1 = [k for k in FIXED_ACCOUNT_ORDER if k in data]
if st.session_state.sort_mode == 'asset':
    keys_1.sort(key=lambda k: data[k].get('총 자산', 0), reverse=True)
elif st.session_state.sort_mode == 'profit':
    keys_1.sort(key=lambda k: data[k].get('총 손익', 0), reverse=True)
elif st.session_state.sort_mode == 'rate':
    keys_1.sort(key=lambda k: data[k].get('손익률(%)', 0), reverse=True)

for k in keys_1:
    a = data[k]
    curr_asset = a['총 자산']
    principal = a['원금']
    
    ad7_acc_1 = (curr_asset - a.get('평가손익(7일전)', 0)) - principal
    ad15_acc_1 = (curr_asset - a.get('평가손익(15일전)', 0)) - principal
    ad30_acc_1 = (curr_asset - a.get('평가손익(30일전)', 0)) - principal
    
    h1.append(f"<tr><td>{clean_label(a['label'])}</td><td>{fmt(curr_asset)}</td><td class='{col(a['총 손익'])}'>{fmt(a['총 손익'],True)}</td><td class='{col(ad7_acc_1)}'>{fmt(ad7_acc_1, True)}</td><td class='{col(ad15_acc_1)}'>{fmt(ad15_acc_1, True)}</td><td class='{col(ad30_acc_1)}'>{fmt(ad30_acc_1, True)}</td><td class='{col(a['손익률(%)'])}'>{fmt_p(a['손익률(%)'])}</td><td>{fmt(principal)}</td></tr>")
h1.append("</table>")
st.markdown("".join(h1), unsafe_allow_html=True)

# --- [2] 매입금액 대비 자산 현황 ---
ag_tot = tot.get('총 자산',0) - tot.get('매입금액합',0)
ay_tot = (ag_tot / tot.get('매입금액합',1) * 100) if tot.get('매입금액합',1) > 0 else 0
st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(tot.get('총 자산'))}</span> / 총 손익 : <span class='summary-val {col(ag_tot)}'>{fmt(ag_tot, True)} ({fmt_p(ay_tot)})</span></div>", unsafe_allow_html=True)

h2 = [unit_html, """
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
"""]

td1_tot = tot.get('평가손익(1일전)',0)
td7_tot = tot.get('평가손익(7일전)',0)
td30_tot = tot.get('평가손익(30일전)',0)

h2.append(f"<tr class='sum-row'><td>[ 합계 ]</td><td>{fmt(tot.get('총 자산'))}</td><td class='{col(ag_tot)}'>{fmt(ag_tot, True)}</td><td class='{col(td1_tot)}'>{fmt(td1_tot, True)}</td><td class='{col(td7_tot)}'>{fmt(td7_tot, True)}</td><td class='{col(td30_tot)}'>{fmt(td30_tot, True)}</td><td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td><td>{fmt(tot.get('매입금액합'))}</td></tr>")

sec2_items = []
for k in FIXED_ACCOUNT_ORDER:
    if k in data:
        a = data[k]
        ag_acc = sum(i.get('평가손익',0) for i in a.get('상세', []) if i.get('종목명') != '[ 합계 ]')
        ap_acc = a.get('총 자산',0) - ag_acc
        ay_acc = (ag_acc/ap_acc*100) if ap_acc > 0 else 0
        sec2_items.append({'k': k, 'a': a, 'ag_acc': ag_acc, 'ap_acc': ap_acc, 'ay_acc': ay_acc})

if st.session_state.sort_mode == 'asset':
    sec2_items.sort(key=lambda x: x['a'].get('총 자산', 0), reverse=True)
elif st.session_state.sort_mode == 'profit':
    sec2_items.sort(key=lambda x: x['ag_acc'], reverse=True)
elif st.session_state.sort_mode == 'rate':
    sec2_items.sort(key=lambda x: x['ay_acc'], reverse=True)

for item in sec2_items:
    a = item['a']
    ad1_acc = a.get('평가손익(1일전)', 0)
    ad7_acc = a.get('평가손익(7일전)', 0)
    ad30_acc = a.get('평가손익(30일전)', 0)
    
    h2.append(f"<tr><td>{clean_label(a['label'])}</td><td>{fmt(a['총 자산'])}</td><td class='{col(item['ag_acc'])}'>{fmt(item['ag_acc'], True)}</td><td class='{col(ad1_acc)}'>{fmt(ad1_acc, True)}</td><td class='{col(ad7_acc)}'>{fmt(ad7_acc, True)}</td><td class='{col(ad30_acc)}'>{fmt(ad30_acc, True)}</td><td class='{col(item['ay_acc'])}'>{fmt_p(item['ay_acc'])}</td><td>{fmt(item['ap_acc'])}</td></tr>")
h2.append("</table>")
st.markdown("".join(h2), unsafe_allow_html=True)

# --- [3] 계좌별 상세 내역 ---
st.markdown("<div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)

# ZAPPA 메뉴 버튼들
b1, b2, b3, b4, b5 = st.columns(5)
with b1:
    st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
    is_init = (st.session_state.sort_mode == 'init')
    if st.button("🛠️ 초기화 [ ● ]" if is_init else "🛠️ 초기화 [ ○ ]", type="primary" if is_init else "secondary"): 
        st.session_state.sort_mode = 'init'; st.rerun()
with b2:
    is_asset = (st.session_state.sort_mode == 'asset')
    if st.button("💰 총 자산 [ ● ]" if is_asset else "💰 총 자산 [ ○ ]", type="primary" if is_asset else "secondary"):  
        st.session_state.sort_mode = 'asset'; st.rerun()
with b3:
    is_profit = (st.session_state.sort_mode == 'profit')
    if st.button("📊 평가손익 [ ● ]" if is_profit else "📊 평가손익 [ ○ ]", type="primary" if is_profit else "secondary"): 
        st.session_state.sort_mode = 'profit'; st.rerun()
with b4:
    is_rate = (st.session_state.sort_mode == 'rate')
    if st.button("📈 손익률 [ ● ]" if is_rate else "📈 손익률 [ ○ ]", type="primary" if is_rate else "secondary"): 
        st.session_state.sort_mode = 'rate'; st.rerun()
with b5:
    is_code = st.session_state.show_code
    code_btn_label = "💻 종목코드 [ + ]" if is_code else "💻 종목코드 [ - ]"
    if st.button(code_btn_label, type="primary" if is_code else "secondary"):
        st.session_state.show_code = not st.session_state.show_code; st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

t3_lbl = {'DC':'퇴직연금(DC)계좌 / (삼성증권 7165962472-28)', 'PENSION':'연금저축(CMA)계좌 / (삼성증권 7169434836-15)', 'ISA':'ISA(중개형)계좌 / (키움증권 6448-4934)', 'IRP':'퇴직연금(IRP)계좌 / (삼성증권 7164499007-29)'}

for k in FIXED_ACCOUNT_ORDER:
    if k not in data: continue
    a = data[k]
    with st.expander(f"📂 [ {t3_lbl.get(k, a['label'])} ] 종목별 현황", expanded=False):
        s_data = next(i for i in a['상세'] if i['종목명'] == "[ 합계 ]")
        
        extra_info_html = ""
        if k in ['DC', 'IRP']:
            safe_pct = 0.0
            for item in a.get('상세', []):
                if item.get('종목명') == "[ 합계 ]": 
                    continue
                if k == 'DC' and item.get('종목명') in ['삼성화재 퇴직연금(3.05%/年)', '현금성자산']:
                    safe_pct += item.get('비중', 0)
                elif k == 'IRP' and item.get('종목명') == '현금성자산':
                    safe_pct += item.get('비중', 0)
            
            risky_pct = 100.0 - safe_pct
            extra_info_html = f"<div style='font-size:14.5px; font-weight:normal; color:#555;'>[ 위험자산 : {risky_pct:.1f}% | 안전자산 : {safe_pct:.1f}% ]</div>"
        
        header_html = f"""
        <div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'>
            <div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(a['총 자산'])}</span> / 총 손익 : <span class='summary-val {col(s_data.get('평가손익'))}'>{fmt(s_data.get('평가손익'), True)} ({fmt_p(s_data.get('손익률(%)'))})</span></div>
            {extra_info_html}
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
        
        h3 = [unit_html, "<table class='main-table'><tr><th>종목명</th>"]
        if st.session_state.show_code: h3.append("<th>종목코드</th>")
        
        h3.append("<th>비중</th><th>총 자산</th><th>평가손익</th><th>손익률</th><th>주식수</th><th>매입가</th><th>현재가</th></tr>")
        
        items = [i for i in a.get('상세', []) if i.get('종목명') != "[ 합계 ]"]
        if st.session_state.sort_mode == 'asset': items.sort(key=lambda x: x.get('총 자산', 0), reverse=True)
        elif st.session_state.sort_mode == 'profit': items.sort(key=lambda x: x.get('평가손익', 0), reverse=True)
        elif st.session_state.sort_mode == 'rate': items.sort(key=lambda x: x.get('손익률(%)', 0), reverse=True)
        
        for i in ([s_data] + items):
            is_s = (i.get('종목명') == "[ 합계 ]")
            row = f"<tr class='sum-row'>" if is_s else "<tr>"
            row += f"<td>{i.get('종목명')}</td>"
            if st.session_state.show_code: row += f"<td>{'-' if is_s or i.get('코드','-')=='-' else i.get('코드')}</td>"
            row += f"<td>{i.get('비중',0):.1f}%</td><td>{fmt(i.get('총 자산',0))}</td><td class='{col(i.get('평가손익',0))}'>{fmt(i.get('평가손익',0), True)}</td><td class='{col(i.get('손익률(%)',0))}'>{fmt_p(i.get('손익률(%)',0))}</td><td>{fmt(i.get('수량','-'))}</td><td>{fmt(i.get('매입가','-'))}</td><td>{fmt(i.get('현재가','-'))}</td></tr>"
            h3.append(row)
        h3.append("</table>")
        st.markdown("".join(h3), unsafe_allow_html=True)
