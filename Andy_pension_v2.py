import pandas as pd
import requests
import json
from datetime import datetime, timedelta, timezone

# ==========================================
# 1. 설정 및 고정 데이터 (핵심 계산 로직)
# ==========================================
APP_KEY = "PSEk5DTSWQoYXgdxMMo4N8PHGGmNo0RG83cp".strip()
APP_SECRET = "5gBB/ztuZ3U2vP1pWl64HvBJGXvFaWddBeslA9NMu0jhqq4oAPqdac4ptcACuXsTHCMr+Zux19lmpDQDsaXZpHj0XpKal9m0isO2lYIJxg+mRoIsX6ncgwlwMdNkGfWa4Bo+syi+wRA2ceJmu2d1ysJBx3DimSY8tze8fHOV1B6b8+LYwns=".strip()
URL_BASE = "https://openapi.koreainvestment.com:9443"

# [수정] 1번 테이블 요청 라벨로 수정
ORIGINAL_CAPITAL = {
    '퇴직연금(DC)계좌 (25.8월~)': 254782039, 
    '연금저축(CMA)계좌 (25.11월~)': 78787722, 
    'ISA(중개형)계좌 (25.8월~)': 33000000, 
    '퇴직연금(IRP)계좌 (25.8월~)': 3000000
}
DC_FIXED_GAIN = 47989921
DC_FIXED_RATE = 18.82

ACC_MAP = {
    '퇴직연금(DC)계좌 (25.8월~)': 'DC', 
    '연금저축(CMA)계좌 (25.11월~)': 'PENSION', 
    'ISA(중개형)계좌 (25.8월~)': 'ISA', 
    '퇴직연금(IRP)계좌 (25.8월~)': 'IRP'
}

def calc_samsungfire_principal():
    기준일 = datetime(2026, 2, 21); 기준금액 = 90267089; 원금 = 90000000; 연이율 = 0.0305
    today_n = datetime.now().replace(tzinfo=None, hour=0, minute=0, second=0, microsecond=0)
    기준일_n = 기준일.replace(tzinfo=None, hour=0, minute=0, second=0, microsecond=0)
    n_days = (today_n - 기준일_n).days
    return int(기준금액 + (원금 * 연이율 * n_days / 365))

PORTFOLIO = {
    'DC': [
        ['069500', 635, 49602, 'KODEX 200'], ['161510', 1300, 19285, 'PLUS 고배당주'], 
        ['360750', 1402, 23556, 'TIGER 미국S&P500'], ['379810', 1402, 23465, 'KODEX 나스닥100'], 
        ['381180', 996, 25427, 'TIGER 미국필라델피아반도체나스닥'], ['458730', 1353, 12222, 'TIGER 미국배당다우존스'], 
        ['CASH_INS', 1, 90000000, '삼성화재 퇴직연금(3.05%/年)'], ['CASH_ETC', 1, 652933, '현금성자산']
    ],
    'PENSION': [
        ['MMF00004', 1, 97708, "삼성신종MMF"], ['069500', 427, 56911, 'KODEX 200'], 
        ['360750', 361, 25193, 'TIGER 미국S&P500'], ['379810', 341, 25105, 'KODEX 나스닥100'], 
        ['381180', 295, 28543, 'TIGER 미국필라델피아반도체나스닥'], ['498400', 2444, 13193, 'KODEX 200타겟위클리커버드콜'], 
        ['PENSION_CASH', 1, 1347241, '현금잔고']
    ],
    'ISA': [
        ['498400', 1176, 12806, 'KODEX 200타겟위클리커버드콜'], ['475720', 894, 10069, 'RISE 200위클리커버드콜'], 
        ['494300', 770, 9878, 'KODEX 나스닥데일리'], ['483280', 260, 12391, 'KODEX AI테크TOP'], 
        ['CASH_ISA', 1, 209746, '현금성자산']
    ],
    'IRP': [
        ['498400', 189, 11080, 'KODEX 200타겟위클리커버드콜'], ['CASH_IRP', 1, 1140906, '현금성자산']
    ]
}

def get_access_token():
    payload = {"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET}
    try: return requests.post(f"{URL_BASE}/oauth2/tokenP", json=payload).json().get("access_token")
    except: return None

def get_current_price(code, token, avg_p):
    if code == 'CASH_INS': return {"c": calc_samsungfire_principal(), "d": 0}
    if code.startswith('CASH') or code == 'PENSION_CASH' or code == 'MMF00004': return {"c": int(avg_p), "d": 0}
    headers = {"authorization": f"Bearer {token}", "appkey": APP_KEY, "appsecret": APP_SECRET, "tr_id": "FHKST01010100"}
    try:
        res = requests.get(f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price", headers=headers, params={"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code.zfill(6)})
        out = res.json().get('output', {})
        return {"c": int(float(out.get('stck_prpr', avg_p))), "d": int(float(out.get('prdy_vrss', 0)))}
    except: return {"c": int(avg_p), "d": 0}

def generate_asset_data():
    kst = timezone(timedelta(hours=9)); now_kst = datetime.now(kst)
    days_kr = ['월', '화', '수', '목', '금', '토', '일']
    day_name = days_kr[now_kst.weekday()]
    
    fetch_time = now_kst.strftime(f"%Y/%m/%d({day_name}) / %H:%M:%S")
    
    token = get_access_token()
    if not token: return None

    t_asset, t_p_effective, t_diff, assets_json = 0, 0, 0, {}
    for acc_label, p_val in ORIGINAL_CAPITAL.items():
        acc_key = ACC_MAP[acc_label]; a_asset, a_diff, sub_info = 0, 0, []
        a_buy_total = 0 
        for code, qty, avg_p, title in PORTFOLIO[acc_key]:
            px = get_current_price(code, token, avg_p); curr, diff_val = px['c'], px['d'] * qty
            asset = int(qty * curr); buy_amt = int(qty * avg_p); gain = asset - buy_amt
            a_asset += asset; a_diff += diff_val; a_buy_total += buy_amt
            sub_info.append({"종목명": title, "평가금액": asset, "평가손익": gain, "전일비": diff_val, "수익률(%)": (gain/buy_amt*100) if buy_amt!=0 else 0, "수량": qty, "평단가": avg_p, "가격": curr})
        for item in sub_info: item["비중"] = (item["평가금액"] / a_asset * 100) if a_asset > 0 else 0
        
        a_val_gain = sum(i['평가손익'] for i in sub_info)
        sum_row = {"종목명": "[ 합계 ]", "비중": 100.0, "평가금액": a_asset, "평가손익": a_val_gain, "수익률(%)": (a_val_gain/a_buy_total*100) if a_buy_total>0 else 0, "수량": "-", "평단가": "-", "가격": "-"}
        sub_info.insert(0, sum_row)
        
        t_asset += a_asset; t_p_effective += p_val; t_diff += a_diff
        assets_json[acc_key] = {"label": acc_label, "총자산": a_asset, "원금": p_val, "총손익": (a_asset-p_val) if acc_key!='DC' else DC_FIXED_GAIN, "수익률(%)": (DC_FIXED_RATE if acc_key=='DC' else (a_asset-p_val)/p_val*100), "평가손익(전일비)": a_diff, "상세": sub_info}
    
    t_avg_buy = sum(sum(i['수량']*i['평단가'] for i in assets_json[k]['상세'] if i['종목명']!='[ 합계 ]' and isinstance(i['수량'], int)) for k in assets_json if k in ACC_MAP.values())
    assets_json["_total"] = {"총자산": t_asset, "원금합": t_p_effective, "총손익": t_asset-t_p_effective, "수익률(%)": (t_asset-t_p_effective)/t_p_effective*100, "평가손익(전일비)": t_diff, "매수금액합": t_avg_buy, "조회시간": fetch_time}
    assets_json["_insight"] = [f"조회 기준 시간: {fetch_time}", f"a) 계좌별 증감: 금일 전체 자산은 {t_diff:+,d}원 변동되었습니다.", f"b) ETF 분석: 전체 수익률 {assets_json['_total']['수익률(%)']:+.2f}% 형성에 미국 지수형 ETF가 기여 중입니다.", "c) 종목 영향: 커버드콜 전략이 하방 경직성을 확보하고 있습니다.", f"d) 원인 파악: 총자본 대비 수익금 {t_asset-t_p_effective:,d}원은 시장 상황이 반영된 결과입니다.", f"e) 향후 전망: 현재 원금 대비 {assets_json['_total']['수익률(%)']:+.2f}% 성과를 유지하며 밸런스를 유지하십시오."]
    
    with open("assets.json", "w", encoding="utf-8") as f: json.dump(assets_json, f, ensure_ascii=False, indent=2)
    return assets_json

if __name__ == "__main__": generate_asset_data()
