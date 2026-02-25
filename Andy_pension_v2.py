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
    '퇴직연금(DC)계좌 (▶ Aug. 2025)': 254782039, 
    '연금저축(CMA)계좌 (▶ Nov. 2025)': 78787722, 
    'ISA(중개형)계좌 (▶ Aug. 2025)': 33000000, 
    '퇴직연금(IRP)계좌 (▶ Aug. 2025)': 3000000
}

ACC_MAP = {
    '퇴직연금(DC)계좌 (▶ Aug. 2025)': 'DC', 
    '연금저축(CMA)계좌 (▶ Nov. 2025)': 'PENSION', 
    'ISA(중개형)계좌 (▶ Aug. 2025)': 'ISA', 
    '퇴직연금(IRP)계좌 (▶ Aug. 2025)': 'IRP'
}

def calc_samsungfire_principal():
    # 2026년 2월 25일 자 증권사 앱 기준금액으로 영점 재조정 (당일 이자 선반영 분 포함)
    기준일 = datetime(2026, 2, 25)
    기준금액 = 90304247
    원금 = 90000000
    연이율 = 0.0305
    today_n = datetime.now().replace(tzinfo=None, hour=0, minute=0, second=0, microsecond=0)
    기준일_n = 기준일.replace(tzinfo=None, hour=0, minute=0, second=0, microsecond=0)
    
    n_days = (today_n - 기준일_n).days
    # 기준일 이전이거나 당일이면 업데이트된 기준금액 그대로 반환
    if n_days <= 0:
        return 기준금액
        
    return int(기준금액 + (원금 * 연이율 * n_days / 365))

PORTFOLIO = {
    'DC': [
        ['069500', 635, 49602, 'KODEX 200'], 
        ['161510', 1300, 19285, 'PLUS 고배당주'], 
        ['360750', 1402, 23556, 'TIGER 미국S&P500'], 
        ['379810', 1402, 23465, 'KODEX 미국나스닥100'], 
        ['381180', 996, 25427, 'TIGER 미국필라델피아반도체나스닥'], 
        ['458730', 1353, 12222, 'TIGER 미국배당다우존스'], 
        ['CASH_INS', 1, 90000000, '삼성화재 퇴직연금(3.05%/年)'], 
        ['CASH_ETC', 1, 652933, '현금성자산']
    ],
    'PENSION': [
        ['MMF00004', 1, 97708, "삼성신종MMF"], 
        ['069500', 427, 56911, 'KODEX 200'], 
        ['360750', 361, 25193, 'TIGER 미국S&P500'], 
        ['379810', 341, 25105, 'KODEX 미국나스닥100'], 
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
        return {"c": calc_samsungfire_principal(), "d1": 0, "d7": 0}
    if code.startswith('CASH') or code == 'PENSION_CASH' or code == 'MMF00004': 
        return {"c": int(avg_p), "d1": 0, "d7": 0}
    
    curr = int(avg_p)
    diff_1 = 0
    diff_7 = 0
    
    # 1. 현재가 및 전일비 조회
    headers_curr = {
        "authorization": f"Bearer {token}", 
        "appkey": APP_KEY, 
        "appsecret": APP_SECRET, 
        "tr_id": "FHKST01010100"
    }
    try:
        res = requests.get(
            f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price", 
            headers=headers_curr, 
            params={"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code.zfill(6)}
        )
        out = res.json().get('output', {})
        curr = int(float(out.get('stck_prpr', avg_p)))
        diff_1 = int(float(out.get('prdy_vrss', 0))) # 전일 대비 증감
    except: 
        pass

    # 2. 7일 전 종가 조회 (-7일 전주비 계산 로직)
    headers_hist = {
        "authorization": f"Bearer {token}", 
        "appkey": APP_KEY, 
        "appsecret": APP_SECRET, 
        "tr_id": "FHKST01010400"
    }
    try:
        res_hist = requests.get(
            f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-daily-price", 
            headers=headers_hist, 
            params={
                "FID_COND_MRKT_DIV_CODE": "J", 
                "FID_INPUT_ISCD": code.zfill(6),
                "FID_PERIOD_DIV_CODE": "D",
                "FID_ORG_ADJ_PRC": "0"
            }
        )
        out_hist = res_hist.json().get('output', [])
        
        # 7일 전 날짜 계산
        target_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
        hist_price = curr
        
        # 날짜가 7일 전이거나 그 이전인 가장 최근 거래일의 종가를 확보
        for item in out_hist:
            if item.get('stck_bsop_date', '99999999') <= target_date:
                hist_price = int(float(item.get('stck_clpr', curr)))
                break
        
        diff_7 = curr - hist_price
    except: 
        pass

    return {"c": curr, "d1": diff_1, "d7": diff_7}

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
    t_diff_1 = 0
    t_diff_7 = 0
    assets_json = {}
    
    for acc_label, p_val in ORIGINAL_CAPITAL.items():
        acc_key = ACC_MAP[acc_label]
        a_asset = 0
        a_diff_1 = 0
        a_diff_7 = 0
        sub_info = []
        a_buy_total = 0 
        
        for code, qty, avg_p, title in PORTFOLIO[acc_key]:
            px = get_current_price(code, token, avg_p)
            curr = px['c']
            diff_val_1 = px['d1'] * qty  # 전일비 * 수량
            diff_val_7 = px['d7'] * qty  # 전주비 * 수량
            
            asset = int(qty * curr)
            buy_amt = int(qty * avg_p)
            gain = asset - buy_amt
            
            a_asset += asset
            a_diff_1 += diff_val_1
            a_diff_7 += diff_val_7
            a_buy_total += buy_amt
            
            sub_info.append({
                "종목명": title, 
                "코드": code, 
                "총 자산": asset, 
                "평가손익": gain, 
                "전일비": diff_val_1,
                "전주비": diff_val_7, 
                "수익률(%)": (gain/buy_amt*100) if buy_amt!=0 else 0, 
                "수량": qty, 
                "매입가": avg_p, 
                "현재가": curr
            })
            
        for item in sub_info: 
            item["비중"] = (item["총 자산"] / a_asset * 100) if a_asset > 0 else 0
        
        a_val_gain = sum(i['평가손익'] for i in sub_info)
        sum_row = {
            "종목명": "[ 합계 ]", 
            "코드": "-", 
            "비중": 100.0, 
            "총 자산": a_asset, 
            "평가손익": a_val_gain, 
            "수익률(%)": (a_val_gain/a_buy_total*100) if a_buy_total>0 else 0, 
            "수량": "-", 
            "매입가": "-", 
            "현재가": "-"
        }
        sub_info.insert(0, sum_row)
        
        t_asset += a_asset
        t_p_effective += p_val
        t_diff_1 += a_diff_1
        t_diff_7 += a_diff_7
        
        acc_profit = a_asset - p_val
        acc_rate = (acc_profit / p_val * 100) if p_val > 0 else 0
        
        assets_json[acc_key] = {
            "label": acc_label, 
            "총 자산": a_asset, 
            "원금": p_val, 
            "총 수익": acc_profit, 
            "수익률(%)": acc_rate, 
            "평가손익(전일비)": a_diff_1,
            "평가손익(전주비)": a_diff_7, 
            "상세": sub_info
        }
    
    t_avg_buy = sum(sum(i['수량']*i['매입가'] for i in assets_json[k]['상세'] if i['종목명']!='[ 합계 ]' and isinstance(i['수량'], int)) for k in assets_json if k in ACC_MAP.values())
    
    assets_json["_total"] = {
        "총 자산": t_asset, 
        "원금합": t_p_effective, 
        "총 수익": t_asset-t_p_effective, 
        "수익률(%)": (t_asset-t_p_effective)/t_p_effective*100, 
        "평가손익(전일비)": t_diff_1,
        "평가손익(전주비)": t_diff_7, 
        "매입금액합": t_avg_buy, 
        "조회시간": fetch_time
    }
    
    assets_json["_insight"] = [
        f"조회 기준 시간: {fetch_time}", 
        f"a) 계좌별 증감: 전일 대비 {t_diff_1:+,d}원, 전주 대비 {t_diff_7:+,d}원 변동되었습니다.", 
        f"b) ETF 분석: 전체 수익률 {assets_json['_total']['수익률(%)']:+.2f}% 형성에 미국 지수형 ETF가 기여 중입니다.", 
        "c) 종목 영향: 커버드콜 전략이 하방 경직성을 확보하고 있습니다.", 
        f"d) 원인 파악: 총자본 대비 수익금 {t_asset-t_p_effective:,d}원은 시장 상황이 반영된 결과입니다.", 
        f"e) 향후 전망: 현재 원금 대비 {assets_json['_total']['수익률(%)']:+.2f}% 성과를 유지하며 밸런스를 유지하십시오."
    ]
    
    with open("assets.json", "w", encoding="utf-8") as f: 
        json.dump(assets_json, f, ensure_ascii=False, indent=2)
        
    return assets_json

if __name__ == "__main__": 
    generate_asset_data()
