import json
from datetime import datetime
import time
import os
import yfinance as yf

# =====================================================================
# 🔑 Yahoo Finance API 로직 (프리/애프터마켓 실시간 반영)
# =====================================================================
def get_yfinance_price(code, is_usa=False):
    if code == "-": return None, None
    # 국내 주식은 '.KS'(코스피)를 붙여서 검색, 안되면 '.KQ'(코스닥)
    ticker = code if is_usa else f"{code}.KS"
    
    try:
        t = yf.Ticker(ticker)
        # fast_info가 애프터마켓 포함 가장 최신 가격을 빠르게 가져옵니다.
        curr = t.fast_info.last_price
        prev = t.fast_info.previous_close
        
        # 코스피(.KS)에서 못 찾으면 코스닥(.KQ)으로 재시도 (국내주식)
        if (curr is None or str(curr).lower() == 'nan') and not is_usa:
            ticker = f"{code}.KQ"
            t = yf.Ticker(ticker)
            curr = t.fast_info.last_price
            prev = t.fast_info.previous_close
            
        # fallback: fast_info가 일시적 오류일 경우 history 사용
        if curr is None or str(curr).lower() == 'nan':
            hist = t.history(period="5d")
            if len(hist) >= 2:
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                
        if curr and prev and prev > 0:
            dr = ((curr - prev) / prev) * 100
            return float(curr), float(dr)
    except Exception as e:
        print(f"🔥 {code} 가격 조회 실패: {e}")
        pass
    return None, None

def generate_general_data():
    try:
        usd_krw = 1443.1 
        
        # 🎯 투자 원금 중앙 관리
        PRINCIPALS = {
            "DOM1": 110963075,
            "DOM2": 5208948,
            "USA1": 257915999,
            "USA2": 7457930
        }
        
        print("🔄 ZAPPA: Yahoo Finance 서버와 통신을 시작합니다...")
        
        dom1 = [
            {"종목명": "삼성전자", "코드": "005930", "수량": 170, "매입가": 60094, "현재가": 217500, "전일비": -0.23},
            {"종목명": "KODEX 레버리지", "코드": "122630", "수량": 300, "매입가": 37480, "현재가": 111280, "전일비": -1.97},
            {"종목명": "현대차", "코드": "005380", "수량": 65, "매입가": 464862, "현재가": 672000, "전일비": 10.34},
            {"종목명": "CJ", "코드": "001040", "수량": 50, "매입가": 93380, "현재가": 219500, "전일비": -0.45},
            {"종목명": "두산에너빌리티", "코드": "034020", "수량": 270, "매입가": 83898, "현재가": 106200, "전일비": 2.31},
            {"종목명": "한화오션", "코드": "042660", "수량": 110, "매입가": 121239, "현재가": 141200, "전일비": 0.86},
            {"종목명": "한국항공우주", "코드": "047810", "수량": 35, "매입가": 177646, "현재가": 192600, "전일비": 4.73},
            {"종목명": "POSCO홀딩스", "코드": "005490", "수량": 30, "매입가": 393400, "현재가": 415000, "전일비": 1.84},
            {"종목명": "예수금", "코드": "-", "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0, "예수금액": 4677496} 
        ]

        dom2 = [
            {"종목명": "삼성전자", "코드": "005930", "수량": 36, "매입가": 160500, "현재가": 217500, "전일비": 0.5},
            {"종목명": "예수금", "코드": "-", "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0, "예수금액": 18730}
        ]

        usa1 = [
            {"종목명": "알파벳 A", "코드": "GOOGL", "수량": 80, "매입가": 307.2192, "현재가": 311.7600, "전일비": 1.33},
            {"종목명": "팔란티어 테크", "코드": "PLTR", "수량": 120, "매입가": 93.1779, "현재가": 137.1900, "전일비": 2.10},
            {"종목명": "TSMC(ADR)", "코드": "TSM", "수량": 60, "매입가": 291.1235, "현재가": 374.5800, "전일비": -0.59},
            {"종목명": "QQQ 레버리지 3X ETF", "코드": "TQQQ", "수량": 600, "매입가": 29.8480, "현재가": 49.5200, "전일비": -1.06},
            {"종목명": "테슬라", "코드": "TSLA", "수량": 100, "매입가": 261.7097, "현재가": 402.5100, "전일비": -1.49},
            {"종목명": "마이크로소프트", "코드": "MSFT", "수량": 30, "매입가": 427.6786, "현재가": 392.7400, "전일비": -2.24},
            {"종목명": "애플", "코드": "AAPL", "수량": 70, "매입가": 259.6900, "현재가": 264.1800, "전일비": 1.58},
            {"종목명": "미국 반도체 3X ETF", "코드": "SOXL", "수량": 250, "매입가": 18.1940, "현재가": 62.7700, "전일비": 3.93},
            {"종목명": "엔비디아", "코드": "NVDA", "수량": 140, "매입가": 109.5783, "현재가": 177.1900, "전일비": -4.16},
            {"종목명": "아이온큐", "코드": "IONQ", "수량": 530, "매입가": 26.4780, "현재가": 38.3700, "전일비": -6.14},
            {"종목명": "리케티 컴퓨팅", "코드": "RGTI", "수량": 650, "매입가": 9.4056, "현재가": 17.4200, "전일비": -6.55},
            {"종목명": "디 웨이브 퀀텀", "코드": "QBTS", "수량": 500, "매입가": 5.4390, "현재가": 18.7800, "전일비": -6.75},
            {"종목명": "아이렌", "코드": "IREN", "수량": 150, "매입가": 46.6626, "현재가": 40.9500, "전일비": -7.44},
            {"종목명": "예수금", "코드": "-", "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0, "예수금액": 249.42}
        ]

        usa2 = [
            {"종목명": "피그마", "코드": "FIG", "수량": 100, "매입가": 51.6084, "현재가": 29.3900, "전일비": -2.75},
            {"종목명": "예수금", "코드": "-", "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0, "예수금액": 300.00}
        ]

        def process_and_update(items, is_usa=False):
            processed = []
            sum_asset = 0; sum_profit = 0; sum_buy = 0
            
            for it in items:
                if it["종목명"] == "예수금":
                    asset = it.get("예수금액", 0)
                    sum_asset += asset; sum_buy += asset
                    processed.append({
                        "종목명": "예수금", "코드": "-", "총자산": asset, "평가손익": 0, "수익률(%)": 0, 
                        "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0
                    })
                    continue
                
                cp, dr = get_yfinance_price(it["코드"], is_usa)
                if cp is not None:
                    it["현재가"] = cp
                    it["전일비"] = dr
                
                asset = it['수량'] * it['현재가']
                profit = (it['현재가'] - it['매입가']) * it['수량']
                buy = it['수량'] * it['매입가']
                
                processed.append({
                    "종목명": it["종목명"], "코드": it["코드"], "총자산": asset, "평가손익": profit, 
                    "수익률(%)": (profit / buy * 100) if buy else 0, "수량": it["수량"], 
                    "매입가": it["매입가"], "현재가": it["현재가"], "전일비": it.get("전일비", 0)
                })
                sum_asset += asset; sum_profit += profit; sum_buy += buy
                
            for p in processed:
                p['비중'] = (p['총자산'] / sum_asset * 100) if sum_asset > 0 else 0
                
            processed.append({
                "종목명": "[ 합  계 ]", "코드": "-", "비중": 100.0, "총자산": sum_asset, "평가손익": sum_profit, 
                "수익률(%)": (sum_profit/sum_buy*100) if sum_buy else 0, "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0
            })
            
            krw_profit = (sum_profit * usd_krw) if is_usa else sum_profit
            return {
                "상세": processed,
                "총자산_KRW": (sum_asset * usd_krw) if is_usa else sum_asset,
                "총수익_KRW": krw_profit,
                "매입금액_KRW": (sum_buy * usd_krw) if is_usa else sum_buy,
                "평가손익(7일전)": krw_profit * 0.95, 
                "평가손익(15일전)": krw_profit * 0.90,
                "평가손익(30일전)": krw_profit * 0.85
            }

        now = datetime.now()
        weekdays_kr = ["월", "화", "수", "목", "금", "토", "일"]
        time_str = now.strftime(f"%Y/%m/%d({weekdays_kr[now.weekday()]}) / %H:%M:%S")

        final_data = {
            "DOM1": process_and_update(dom1), 
            "DOM2": process_and_update(dom2),
            "USA1": process_and_update(usa1, True), 
            "USA2": process_and_update(usa2, True),
            "환율": usd_krw, 
            "조회시간": time_str,
            "원금": PRINCIPALS
        }
        
        with open('assets_general.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        print(f"🔥 데이터 생성 오류: {e}")

if __name__ == "__main__":
    generate_general_data()
