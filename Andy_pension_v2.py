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

ORIGINAL_CAPITAL = {
    '퇴직연금(DC)계좌 (25.8월~)': 254782039, 
    '연금저축(CMA)계좌 (25.11월~)': 78787722, 
    'ISA(중개형)계좌 (25.8월~)': 33000000, 
    '퇴직연금(IRP)계좌 (25.8월~)': 3000000
}

ACC_MAP = {
    '퇴직연금(DC)계좌 (25.8월~)': 'DC', 
    '연금저축(CMA)계좌 (25.11월~)': 'PENSION', 
    'ISA(중개형)계좌 (25.8월~)': 'ISA', 
    '퇴직연금(IRP)계좌 (25.8월~)': 'IRP'
}

def calc_samsungfire_principal():
    기준일 = datetime(2026, 2, 21)
    기준금액 = 90267089
    원금 = 90000000
    연이율 = 0.0305
    today_n = datetime.now().replace(tzinfo=None, hour=0, minute=0, second=0, microsecond=0)
    기준일_n = 기준일.replace(tzinfo=None, hour=0, minute=0, second=0, microsecond=0)
    n_days = (today_n - 기준일_n).days
    return int(기준금액 + (원금 * 연이율 * n_days / 365))

PORTFOLIO = {
    'DC': [
        ['069500', 635, 49602, 'KODEX 200'], 
        ['161510', 1300, 19285, 'PLUS 고배당주'], 
        ['360750', 1402, 23556, 'TIGER 미국S&P500'], 
        ['379810', 1402, 23465, 'KODEX 나스닥100'], 
        ['381180', 996, 25427, 'TIGER 미국필라델피아반도체나스닥'], 
        ['458730', 1353, 12222, 'TIGER 미국배당다우존스'], 
        ['CASH_INS', 1, 90000000, '삼성화재 퇴직연금(3.05%/年)'], 
        ['CASH_ETC', 1, 652933, '현금성자산']
    ],
    'PENSION': [
        ['MMF00004', 1, 97708, "삼성신종MMF"], 
        ['069500', 427, 56911, 'KODEX 200'], 
        ['360750', 361, 25193, 'TIGER 미국S&P500'], 
        ['379810', 341, 25105, 'KODEX 나스닥100'], 
        ['381180', 295, 28543, 'TIGER 미국필라델피아반도체나스닥'], 
        ['498400', 2444, 13193, 'KODEX 200타겟위클리커버드콜'], 
        ['PENSION_CASH', 1, 1347241, '현금잔고']
    ],
    'ISA': [
        ['498400', 1176, 12806, 'KODEX 200타겟위클리커버드콜'], 
        ['475720', 894, 10069, 'RISE 200위클리커버드콜'], 
        ['494300', 770, 9878, 'KODEX 나스닥데일리'], 
        ['483280', 260, 12391, 'KODEX AI테크TOP'], 
        ['CASH_ISA', 1, 209746, '현금성자산']
    ],
    'IRP': [
        ['498400', 189, 11080, 'KODEX 200타겟위클리커버드콜'], 
        ['CASH_IRP', 1, 1140906, '현금성자산']
    ]
}

def get_access_token():
    payload = {"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET}
    try: 
        return requests.post(f"{URL_BASE}/oauth2/tokenP", json=payload).json().get("access_token")
    except: 
        return None

def get_current_price(code, token, avg_p):
    if code == 'CASH_INS': 
        return {"c": calc_samsungfire_principal(), "d": 0}
    if code.startswith('CASH') or code == 'PENSION_CASH' or code == 'MMF00004': 
        return {"c": int(avg_p), "d": 0}
    
    headers = {
        "authorization": f"Bearer {token}", 
        "appkey": APP_KEY, 
        "appsecret": APP_SECRET, 
        "tr_id": "FHKST01010100"
    }
    try:
        res = requests.get(
            f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price", 
            headers=headers, 
            params={"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code.zfill(6)}
        )
        out = res.json().get('output', {})
        return {"c": int(float(out.get('stck_prpr', avg_p))), "d": int(float(out.get('prdy_vrss', 0)))}
    except: 
        return {"c": int(avg_p), "d": 0}

def generate_asset_data():
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst)
    days_kr = ['월', '화', '수', '목', '금', '토', '일']
    day_name = days_kr[now_kst.weekday()]
    fetch_time = now_kst.strftime(f"%Y/%m/%d({day_name}) / %H:%M:%S")
    
    token = get_access_token()
    if not token: return None

    t_asset = 0
    t_p_effective = 0
    t_diff = 0
    assets_json = {}
    
    for acc_label, p_val in ORIGINAL_CAPITAL.items():
        acc_key = ACC_MAP[acc_label]
        a_asset = 0
        a_diff = 0
        sub_info = []
        a_buy_total = 0 
        
        for code, qty, avg_p, title in PORTFOLIO[acc_key]:
            px = get_current_price(code, token, avg_p
