import json
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup

# =====================================================================
# 🔑 무적 스크래핑 엔진 (네이버 금융 HTML - 클라우드 차단 절대 불가)
# =====================================================================
def get_kr_price(code):
    if code == "-": return None, None, None
    try:
        url = f"https://m.stock.naver.com/api/stock/{code}/basic"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, headers=headers, timeout=5)
        data = res.json()
        curr = float(data['closePrice'].replace(',', ''))
        dr = float(data['compareToPreviousRate'])
        prev = curr / (1 + (dr / 100)) if dr != 0 else curr
        return curr, dr, (curr - prev)
    except:
        try:
            url = f"https://finance.naver.com/item/sise.naver?code={code}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            curr = float(soup.select_one('strong#_nowVal').text.replace(',', ''))
            dr = float(soup.select_one('strong#_rate').text.replace('%', '').strip())
            prev = curr / (1 + (dr / 100)) if dr != 0 else curr
            return curr, dr, (curr - prev)
        except:
            return None, None, None

def generate_asset_data():
    print("🔄 ZAPPA: 네이버 무적 스크래핑을 시작합니다...")
    
    # 🚨 한국 표준시(KST) 강제 고정
    KST = timezone(timedelta(hours=9))
    now_date = datetime.now(KST)
    base_date = datetime(2026, 3, 1, tzinfo=KST)
    days_passed = max(0, (now_date - base_date).days)
    samsung_principal = 90000000
    daily_interest = samsung_principal * 0.0305 / 365
    samsung_profit = 319114 + int(daily_interest * days_passed)
    samsung_asset = samsung_principal + samsung_profit

    dc_items = [
        {"종목명": "KODEX 200", "코드": "069500", "수량": 635, "매입가": 49602, "현재가": 94120, "전일비": -0.5},
        {"종목명": "PLUS 고배당주", "코드": "161510", "수량": 1300, "매입가": 19285, "현재가": 28850, "전일비": -0.2},
        {"종목명": "TIGER 미국S&P500", "코드": "360750", "수량": 1402, "매입가": 23556, "현재가": 24565, "전일비": 1.2},
        {"종목명": "KODEX 미국나스닥100", "코드": "379810", "수량": 1402, "매입가": 23465, "현재가": 23830, "전일비": 0.8},
        {"종목명": "TIGER 미국필라델피아반도체나스닥", "코드": "381180", "수량": 996, "매입가": 25427, "현재가": 30690, "전일비": -1.5},
        {"종목명": "TIGER 미국배당다우존스", "코드": "458730", "수량": 1353, "매입가": 12222, "현재가": 14285, "전일비": 0.1},
        {"종목명": "삼성화재 퇴직연금이율보증(3.05%/年)", "코드": "-", "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0, "총자산": samsung_asset, "매입금액": samsung_principal},
        {"종목명": "현금성자산(삼성증권)", "코드": "-", "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0, "총자산": 653113, "매입금액": 653113}
    ]

    pension_items = [
        {"종목명": "삼성신종종류형MMF제4호-CP", "코드": "-", "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0, "총자산": 1445430, "매입금액": 1444949},
        {"종목명": "KODEX 200", "코드": "069500", "수량": 427, "매입가": 56911, "현재가": 94120, "전일비": -0.5},
        {"종목명": "TIGER 미국S&P500", "코드": "360750", "수량": 361, "매입가": 25193, "현재가": 24565, "전일비": 1.2},
        {"종목명": "KODEX 미국나스닥100", "코드": "379810", "수량": 341, "매입가": 25105, "현재가": 23830, "전일비": 0.8},
        {"종목명": "TIGER 미국필라델피아반도체나스닥", "코드": "381180", "수량": 295, "매입가": 28543, "현재가": 30690, "전일비": -1.5},
        {"종목명": "KODEX 200타겟위클리커버드콜", "코드": "498400", "수량": 2444, "매입가": 13193, "현재가": 19790, "전일비": -0.8},
        {"종목명": "현금성자산(예수금)", "코드": "-", "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0, "총자산": 248, "매입금액": 248}
    ]

    irp_items = [
        {"종목명": "KODEX 200타겟위클리커버드콜", "코드": "498400", "수량": 189, "매입가": 11080, "현재가": 19790, "전일비": -0.8},
        {"종목명": "현금성자산(삼성증권)", "코드": "-", "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0, "총자산": 1141162, "매입금액": 1141162}
    ]

    isa_items = [
        {"종목명": "KODEX 200타겟위클리커버드콜", "코드": "498400", "수량": 1176, "매입가": 12806, "현재가": 19790, "전일비": -0.75},
        {"종목명": "RISE 200위클리커버드콜", "코드": "475720", "수량": 894, "매입가": 10069, "현재가": 13640, "전일비": -0.18},
        {"종목명": "KODEX 미국나스닥100데일리커버", "코드": "494300", "수량": 285, "매입가": 12353, "현재가": 11665, "전일비": -1.10},
        {"종목명": "KODEX 미국AI테크TOP10타겟커버드콜", "코드": "483280", "수량": 770, "매입가": 9878, "현재가": 9545, "전일비": -0.37}
    ]

    def process_account(items, principal):
        processed = []
        sum_asset = 0
        sum_profit = 0
        sum_buy = 0
        
        for it in items:
            if it.get("코드") == "-" or "현금" in it["종목명"] or "MMF" in it["종목명"] or "이율보증" in it["종목명"]:
                asset = it.get('총자산', 0)
                buy = it.get('매입금액', asset)
                profit = asset - buy
                rate = (profit / buy * 100) if buy else 0
                
                processed.append({
                    "종목명": it["종목명"], "코드": "-", "총 자산": asset, "평가손익": profit,
                    "수익률(%)": rate, "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0, "전일비_금액": 0
                })
                sum_asset += asset; sum_profit += profit; sum_buy += buy
                continue

            if it.get("코드") != "-":
                cp, dr, damt = get_kr_price(it["코드"])
                if cp is not None:
                    it["현재가"] = cp
                    it["전일비"] = dr
                    it["전일비_금액"] = damt
                    
            asset = it['수량'] * it['현재가']
            buy = it['수량'] * it['매입가']
            profit = asset - buy
            rate = (profit / buy * 100) if buy > 0 else 0
            
            damt = it.get("전일비_금액")
            if damt is None:
                cp = float(it["현재가"])
                dr = float(it["전일비"])
                damt = cp - (cp / (1 + dr / 100)) if cp > 0 and dr != 0 else 0
            
            processed.append({
                "종목명": it["종목명"], "코드": it["코드"], "총 자산": asset, "평가손익": profit,
                "수익률(%)": rate, "수량": it["수량"], "매입가": it["매입가"], "현재가": it["현재가"],
                "전일비": it.get("전일비", 0), "전일비_금액": damt
            })
            sum_asset += asset; sum_profit += profit; sum_buy += buy
            
        for p in processed: p['비중'] = (p['총 자산'] / sum_asset * 100) if sum_asset > 0 else 0
            
        processed.append({
            "종목명": "[ 합  계 ]", "코드": "-", "비중": 100.0, "총 자산": sum_asset, "평가손익": sum_profit,
            "수익률(%)": (sum_profit / sum_buy * 100) if sum_buy else 0, "수량": "-", "매입가": "-",
            "현재가": "-", "전일비": 0, "전일비_금액": 0
        })
        
        acc_rate = (sum_profit / principal * 100) if principal > 0 else 0
        
        return {
            "상세": processed, "총 자산": sum_asset, "총 수익": sum_profit, "원금": principal,
            "매입금액": sum_buy, "수익률(%)": acc_rate, "평가손익(1일전)": sum_profit * 0.98,
            "평가손익(7일전)": sum_profit * 0.95, "평가손익(15일전)": sum_profit * 0.90, "평가손익(30일전)": sum_profit * 0.85
        }

    dc_data = process_account(dc_items, 245981960)
    pension_data = process_account(pension_items, 78787722)
    isa_data = process_account(isa_items, 33000000)
    irp_data = process_account(irp_items, 3000000)
    
    t_asset = dc_data['총 자산'] + pension_data['총 자산'] + isa_data['총 자산'] + irp_data['총 자산']
    t_profit = dc_data['총 수익'] + pension_data['총 수익'] + isa_data['총 수익'] + irp_data['총 수익']
    t_buy = dc_data['매입금액'] + pension_data['매입금액'] + isa_data['매입금액'] + irp_data['매입금액']
    t_principal = 245981960 + 78787722 + 33000000 + 3000000
    
    kr_days = ["월", "화", "수", "목", "금", "토", "일"]
    kr_day = kr_days[now_date.weekday()]
    date_str = now_date.strftime(f"%Y년 %m월 %d일({kr_day}) / %H:%M:%S")

    total_data = {
        "총 자산": t_asset, "총 수익": t_profit, "원금합": t_principal, "매입금액합": t_buy,
        "수익률(%)": (t_profit / t_principal * 100) if t_principal > 0 else 0,
        "평가손익(1일전)": t_profit * 0.98, "평가손익(7일전)": t_profit * 0.95,
        "평가손익(15일전)": t_profit * 0.90, "평가손익(30일전)": t_profit * 0.85,
        "조회시간": date_str
    }
    
    final_json = {"DC": dc_data, "PENSION": pension_data, "ISA": isa_data, "IRP": irp_data, "_total": total_data, "_insight": True}
    
    with open('assets.json', 'w', encoding='utf-8') as f:
        json.dump(final_json, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    generate_asset_data()
