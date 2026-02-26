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
    '퇴직연금(DC)계좌 (25.8월)': 254782039, 
    '연금저축(CMA)계좌 (25.11월)': 78787722, 
    'ISA(중개형)계좌 (25.8월)': 33000000, 
    '퇴직연금(IRP)계좌 (25.8월)': 3000000
}

ACC_MAP = {
    '퇴직연금(DC)계좌 (25.8월)': 'DC', 
    '연금저축(CMA)계좌 (25.11월)': 'PENSION', 
    'ISA(중개형)계좌 (25.8월)': 'ISA', 
    '퇴직연금(IRP)계좌 (25.8월)': 'IRP'
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
        ['483280', 285, 12353, 'KODEX AI테크TOP'],
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
        # 무한 대기 방지를 위해 timeout=5 설정
        return requests.post(f"{URL_BASE}/oauth2/tokenP", json=payload, timeout=5).json().get("access_token")
    except: 
        return None

def get_current_price(code, token, avg_p):
    if code == 'CASH_INS': 
        return {"c": calc_samsungfire_principal(), "d1": 0, "d7": 0, "d15": 0, "d30": 0}
    if code.startswith('CASH') or code == 'PENSION_CASH' or code == 'MMF00004': 
        return {"c": int(avg_p), "d1": 0, "d7": 0, "d15": 0, "d30": 0}
    
    curr = int(avg_p)
    diff_1 = 0
    diff_7 = 0
    diff_15 = 0
    diff_30 = 0
    
    headers_curr = {
        "authorization": f"Bearer {token}", 
        "appkey": APP_KEY, 
        "appsecret": APP_SECRET, 
        "tr_id": "FHKST01010100"
    }
    try:
        # timeout=5 설정 추가
        res = requests.get(
            f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price", 
            headers=headers_curr, 
            params={"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code.zfill(6)},
            timeout=5
        )
        out = res.json().get('output', {})
        curr = int(float(out.get('stck_prpr', avg_p)))
        diff_1 = int(float(out.get('prdy_vrss', 0)))
    except: 
        pass

    headers_hist = {
        "authorization": f"Bearer {token}", 
        "appkey": APP_KEY, 
        "appsecret": APP_SECRET, 
        "tr_id": "FHKST01010400"
    }
    try:
        # timeout=5 설정 추가
        res_hist = requests.get(
            f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-daily-price", 
            headers=headers_hist, 
            params={
                "FID_COND_MRKT_DIV_CODE": "J", 
                "FID_INPUT_ISCD": code.zfill(6),
                "FID_PERIOD_DIV_CODE": "D",
                "FID_ORG_ADJ_PRC": "0"
            },
            timeout=5
        )
        out_hist = res_hist.json().get('output', [])
        
        now_dt = datetime.now()
        t_7 = (now_dt - timedelta(days=7)).strftime("%Y%m%d")
        t_15 = (now_dt - timedelta(days=15)).strftime("%Y%m%d")
        t_30 = (now_dt - timedelta(days=30)).strftime("%Y%m%d")
        
        p_7, p_15, p_30 = curr, curr, curr
        found_7, found_15, found_30 = False, False, False
        
        for item in out_hist:
            dt = item.get('stck_bsop_date', '99999999')
            pr = int(float(item.get('stck_clpr', curr)))
            
            if not found_7 and dt <= t_7:
                p_7 = pr; found_7 = True
            if not found_15 and dt <= t_15:
                p_15 = pr; found_15 = True
            if not found_30 and dt <= t_30:
                p_30 = pr; found_30 = True
                
        diff_7 = curr - p_7
        diff_15 = curr - p_15
        diff_30 = curr - p_30
    except: 
        pass

    return {"c": curr, "d1": diff_1, "d7": diff_7, "d15": diff_15, "d30": diff_30}

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
    t_diff_15 = 0
    t_diff_30 = 0
    assets_json = {}
    
    for acc_label, p_val in ORIGINAL_CAPITAL.items():
        acc_key = ACC_MAP[acc_label]
        a_asset = 0
        a_diff_1 = 0
        a_diff_7 = 0
        a_diff_15 = 0
        a_diff_30 = 0
        sub_info = []
        a_buy_total = 0 
        
        for code, qty, avg_p, title in PORTFOLIO[acc_key]:
            px = get_current_price(code, token, avg_p)
            curr = px['c']
            diff_val_1 = px['d1'] * qty
            diff_val_7 = px['d7'] * qty
            diff_val_15 = px['d15'] * qty
            diff_val_30 = px['d30'] * qty
            
            asset = int(qty * curr)
            buy_amt = int(qty * avg_p)
            gain = asset - buy_amt
            
            a_asset += asset
            a_diff_1 += diff_val_1
            a_diff_7 += diff_val_7
            a_diff_15 += diff_val_15
            a_diff_30 += diff_val_30
            a_buy_total += buy_amt
            
            sub_info.append({
                "종목명": title, 
                "코드": code, 
                "총 자산": asset, 
                "평가손익": gain, 
                "1일전": diff_val_1,
                "7일전": diff_val_7, 
                "15일전": diff_val_15,
                "30일전": diff_val_30,
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
        t_diff_15 += a_diff_15
        t_diff_30 += a_diff_30
        
        acc_profit = a_asset - p_val
        acc_rate = (acc_profit / p_val * 100) if p_val > 0 else 0
        
        assets_json[acc_key] = {
            "label": acc_label, 
            "총 자산": a_asset, 
            "원금": p_val, 
            "총 수익": acc_profit, 
            "수익률(%)": acc_rate, 
            "평가손익(1일전)": a_diff_1,
            "평가손익(7일전)": a_diff_7, 
            "평가손익(15일전)": a_diff_15, 
            "평가손익(30일전)": a_diff_30, 
            "상세": sub_info
        }
    
    t_avg_buy = sum(sum(i['수량']*i['매입가'] for i in assets_json[k]['상세'] if i['종목명']!='[ 합계 ]' and isinstance(i['수량'], int)) for k in assets_json if k in ACC_MAP.values())
    
    assets_json["_total"] = {
        "총 자산": t_asset, 
        "원금합": t_p_effective, 
        "총 수익": t_asset-t_p_effective, 
        "수익률(%)": (t_asset-t_p_effective)/t_p_effective*100, 
        "평가손익(1일전)": t_diff_1,
        "평가손익(7일전)": t_diff_7, 
        "평가손익(15일전)": t_diff_15, 
        "평가손익(30일전)": t_diff_30, 
        "매입금액합": t_avg_buy, 
        "조회시간": fetch_time
    }
    
    # ==========================================
    # [추가/수정] ZAPPA 인사이트 맞춤형 요약 로직
    # ==========================================
    def fmt_mil(val): return round(val / 1000000, 1)
    def fmt_rate(rate): return f"▲{rate:.1f}%" if rate > 0 else (f"▼{abs(rate):.1f}%" if rate < 0 else "0.0%")
    def fmt_profit_mil(val): 
        mil = fmt_mil(val)
        return f"+{mil:.1f}백만" if mil > 0 else (f"{mil:.1f}백만" if mil < 0 else "0.0백만")

    # [1] 전체 요약
    t_buy_profit = t_asset - t_avg_buy
    t_buy_rate = (t_buy_profit / t_avg_buy * 100) if t_avg_buy > 0 else 0
    t_prin_rate = assets_json['_total']['수익률(%)']
    b1 = f"현재 절세계좌 자산 총액은 {t_asset:,}원, 평가손익은 {t_buy_profit:,}원 / 전일비 {t_diff_1:+,}원 으로 매입금액比 {fmt_rate(t_buy_rate)} (투자원금比 {fmt_rate(t_prin_rate)}) 수익률을 나타내고 있습니다."

    # [2] 계좌별 수익률 순위
    acc_list = []
    for k in ACC_MAP.values():
        if k in assets_json:
            clean_name = assets_json[k]['label'].split(' (')[0]
            acc_list.append({
                'name': clean_name,
                'rate': assets_json[k]['수익률(%)'],
                'profit': assets_json[k]['총 수익']
            })
    acc_list.sort(key=lambda x: x['rate'], reverse=True)
    b2_str = " / ".join([f"{x['name']} {fmt_rate(x['rate'])}({fmt_profit_mil(x['profit'])})" for x in acc_list])
    b2 = f"수익률 높은 계좌 순: {b2_str}"

    # [3 & 4] ETF 그룹핑 및 세부 종목 분석을 위한 데이터 준비
    us_etfs = ['TIGER 미국S&P500', 'KODEX 미국나스닥100', 'TIGER 미국필라델피아반도체나스닥', 'TIGER 미국배당다우존스', 'KODEX 나스닥데일리', 'KODEX AI테크TOP']
    kr_etfs = ['KODEX 200', 'PLUS 고배당주', 'KODEX 200타겟위클리커버드콜', 'RISE 200위클리커버드콜']
    
    stock_agg = {}
    stock_acc_details = {}
    
    for k in ACC_MAP.values():
        if k in assets_json:
            acc_clean_name = assets_json[k]['label'].split(' (')[0]
            for item in assets_json[k]['상세']:
                if item['종목명'] == '[ 합계 ]' or '현금' in item['종목명'] or '삼성화재' in item['종목명'] or 'MMF' in item['종목명']: continue
                name = item['종목명']
                
                if name not in stock_agg: stock_agg[name] = {'buy': 0, 'gain': 0, 'd1': 0}
                stock_agg[name]['buy'] += (item['수량'] * item['매입가'])
                stock_agg[name]['gain'] += item['평가손익']
                stock_agg[name]['d1'] += item['1일전']
                
                if name not in stock_acc_details: stock_acc_details[name] = []
                stock_acc_details[name].append((acc_clean_name, item['수익률(%)'], item['평가손익']))

    # [3] 미국 ETF vs 한국 ETF 흐름 비교
    us_stats, kr_stats = [], []
    for name, data in stock_agg.items():
        rate = (data['gain'] / data['buy'] * 100) if data['buy'] > 0 else 0
        if name in us_etfs: us_stats.append((name, rate, data['gain']))
        elif name in kr_etfs: kr_stats.append((name, rate, data['gain']))
        
    us_str = ", ".join([f"{n} {fmt_rate(r)}" for n, r, g in us_stats])
    kr_str = ", ".join([f"{n} {fmt_rate(r)}" for n, r, g in kr_stats])
    
    us_total_gain = sum(g for n,r,g in us_stats)
    kr_total_gain = sum(g for n,r,g in kr_stats)
    leader = "코스피 등 한국" if kr_total_gain >= us_total_gain else "미국"
    b3 = f"종목별 전체 흐름: 미국 ETF 장기간 횡보 속에({us_str}), 한국 ETF({kr_str})를 기록 중이며, {leader} ETF가 전체 평가 손익을 주도하고 있습니다."

    # [4] 상세 종목 수치 요약 (수익률 높은 순 4개 종목 추출)
    sorted_stocks = sorted(stock_acc_details.keys(), key=lambda x: sum(p for a, r, p in stock_acc_details[x]), reverse=True)
    b4_parts = []
    circle_nums = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
    for idx, name in enumerate(sorted_stocks[:4]):
        acc_strs = []
        sorted_accs = sorted(stock_acc_details[name], key=lambda x: x[2], reverse=True)
        for a_name, r, p in sorted_accs:
            acc_strs.append(f"{a_name} {fmt_rate(r)}({fmt_profit_mil(p)})")
        
        circle_num = circle_nums[idx] if idx < len(circle_nums) else str(idx+1)
        if len(acc_strs) > 1:
            b4_parts.append(f"{circle_num} {name} : {', '.join(acc_strs)}")
        else:
            b4_parts.append(f"{circle_num} {name} {acc_strs[0]}")
            
    b4 = f"주요 종목 상세: " + " / ".join(b4_parts)

    # [5] 전일비(d1)를 동적으로 읽어내는 시장 동향 인사이트 분석
    us_d1 = sum(data['d1'] for name, data in stock_agg.items() if name in us_etfs)
    kr_d1 = sum(data['d1'] for name, data in stock_agg.items() if name in kr_etfs)
    
    if us_d1 < 0 and kr_d1 > 0:
        market_flow = "미국 빅테크 및 기술주가 전반적으로 조정을 받는 가운데, 투자자금의 방향 전환으로 한국 코스피 관련 종목이 상승 흐름을 보이고 있습니다."
    elif us_d1 > 0 and kr_d1 < 0:
        market_flow = "미국 빅테크 및 기술주가 견조한 상승세를 이어가는 가운데, 한국 증시는 다소 쉬어가는 흐름을 보이고 있습니다."
    elif us_d1 > 0 and kr_d1 > 0:
        market_flow = "고용지표 및 금리 인하 소식 등 대외 변수 속에서도 미국 기술주와 한국 코스피 종목 모두 동반 상승하며 양호한 시장 흐름을 기록 중입니다."
    else:
        market_flow = "미국과 한국 증시 모두 전반적인 조정을 겪고 있으며, 변동성 확대에 대비한 리스크 관리가 필요한 시점입니다."
        
    b5 = f"시장 동향 및 전망: {market_flow} 한국형 추세 흐름과 동시에 수익이 큰 종목의 현금화 및 리밸런싱 등 주의 깊은 관리가 필요합니다."

    # 최종 병합
    assets_json["_insight"] = [
        f"조회 기준 시간: {fetch_time}", 
        b1, b2, b3, b4, b5
    ]
    
    with open("assets.json", "w", encoding="utf-8") as f: 
        json.dump(assets_json, f, ensure_ascii=False, indent=2)
        
    return assets_json

if __name__ == "__main__": 
    generate_asset_data()
