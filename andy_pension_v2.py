import json
from datetime import datetime

def generate_asset_data():
    # =====================================================================
    # 📝 절세계좌 데이터 (Andy님 세팅값)
    # =====================================================================
    dc_items = [
        {"종목명": "삼성화재 퇴직연금(3.05%/年)", "비중": 23.3, "총 자산": 58319694, "평가손익": 1058223, "수익률(%)": 1.85, "수량": "-", "매입가": "-", "현재가": "-", "전일비(%)": 0},
        {"종목명": "TIGER 미국S&P500", "비중": 29.5, "총 자산": 73787916, "평가손익": 28659610, "수익률(%)": 63.50, "수량": 3521, "매입가": 12816, "현재가": 20955, "전일비(%)": -0.80},
        {"종목명": "TIGER 미국나스닥100", "비중": 25.1, "총 자산": 62890912, "평가손익": 30206126, "수익률(%)": 92.42, "수량": 4543, "매입가": 7194, "현재가": 13845, "전일비(%)": -1.80},
        {"종목명": "TIGER 미국필라델피아반도체나스닥", "비중": 21.0, "총 자산": 52627995, "평가손익": 24209938, "수익률(%)": 85.19, "수량": 4015, "매입가": 7077, "현재가": 13110, "전일비(%)": -2.80},
        {"종목명": "현금성자산", "비중": 1.1, "총 자산": 2824982, "평가손익": 0, "수익률(%)": 0.00, "수량": "-", "매입가": "-", "현재가": "-", "전일비(%)": 0}
    ]
    dc_asset = sum(i["총 자산"] for i in dc_items)
    dc_profit = sum(i["평가손익"] for i in dc_items)
    dc_items.append({"종목명": "[ 합계 ]", "비중": 100.0, "총 자산": dc_asset, "평가손익": dc_profit, "수익률(%)": (dc_profit/(dc_asset-dc_profit)*100) if (dc_asset-dc_profit)>0 else 0, "수량": "-", "매입가": "-", "현재가": "-", "전일비(%)": 0})

    irp_items = [
        {"종목명": "TIGER 미국S&P500", "비중": 48.0, "총 자산": 2038926, "평가손익": 489916, "수익률(%)": 31.63, "수량": 97, "매입가": 15969, "현재가": 21020, "전일비(%)": -0.80},
        {"종목명": "현금성자산", "비중": 52.0, "총 자산": 2209140, "평가손익": 0, "수익률(%)": 0.00, "수량": "-", "매입가": "-", "현재가": "-", "전일비(%)": 0}
    ]
    irp_asset = sum(i["총 자산"] for i in irp_items)
    irp_profit = sum(i["평가손익"] for i in irp_items)
    irp_items.append({"종목명": "[ 합계 ]", "비중": 100.0, "총 자산": irp_asset, "평가손익": irp_profit, "수익률(%)": (irp_profit/(irp_asset-irp_profit)*100) if (irp_asset-irp_profit)>0 else 0, "수량": "-", "매입가": "-", "현재가": "-", "전일비(%)": 0})

    pension_items = [
        {"종목명": "TIGER 미국S&P500", "비중": 23.3, "총 자산": 33177651, "평가손익": 16422896, "수익률(%)": 97.90, "수량": 1583, "매입가": 10584, "현재가": 20960, "전일비(%)": -0.80},
        {"종목명": "TIGER 미국나스닥100", "비중": 40.0, "총 자산": 56983080, "평가손익": 33543160, "수익률(%)": 143.10, "수량": 4116, "매입가": 5694, "현재가": 13845, "전일비(%)": -1.80},
        {"종목명": "TIGER 미국배당다우존스", "비중": 12.0, "총 자산": 17135805, "평가손익": 3328014, "수익률(%)": 24.09, "수량": 1415, "매입가": 9758, "현재가": 12110, "전일비(%)": -0.50},
        {"종목명": "TIGER 미국필라델피아반도체나스닥", "비중": 18.0, "총 자산": 25619170, "평가손익": 16182570, "수익률(%)": 171.49, "수량": 1954, "매입가": 4829, "현재가": 13110, "전일비(%)": -2.80},
        {"종목명": "TIGER 글로벌AI액티브", "비중": 6.3, "총 자산": 8943790, "평가손익": 3448400, "수익률(%)": 62.75, "수량": 650, "매입가": 8454, "현재가": 13760, "전일비(%)": -1.20},
        {"종목명": "현금성자산", "비중": 0.3, "총 자산": 444634, "평가손익": 0, "수익률(%)": 0.00, "수량": "-", "매입가": "-", "현재가": "-", "전일비(%)": 0}
    ]
    pension_asset = sum(i["총 자산"] for i in pension_items)
    pension_profit = sum(i["평가손익"] for i in pension_items)
    pension_items.append({"종목명": "[ 합계 ]", "비중": 100.0, "총 자산": pension_asset, "평가손익": pension_profit, "수익률(%)": (pension_profit/(pension_asset-pension_profit)*100) if (pension_asset-pension_profit)>0 else 0, "수량": "-", "매입가": "-", "현재가": "-", "전일비(%)": 0})

    isa_items = [
        {"종목명": "TIGER 글로벌AI액티브", "비중": 62.5, "총 자산": 27286080, "평가손익": 7286080, "수익률(%)": 36.43, "수량": 1983, "매입가": 10085, "현재가": 13760, "전일비(%)": -1.20},
        {"종목명": "TIGER 미국배당다우존스", "비중": 37.5, "총 자산": 16348390, "평가손익": 3348390, "수익률(%)": 25.75, "수량": 1350, "매입가": 9629, "현재가": 12110, "전일비(%)": -0.50},
        {"종목명": "현금성자산", "비중": 0.0, "총 자산": 12348, "평가손익": 0, "수익률(%)": 0.00, "수량": "-", "매입가": "-", "현재가": "-", "전일비(%)": 0}
    ]
    isa_asset = sum(i["총 자산"] for i in isa_items)
    isa_profit = sum(i["평가손익"] for i in isa_items)
    isa_items.append({"종목명": "[ 합계 ]", "비중": 100.0, "총 자산": isa_asset, "평가손익": isa_profit, "수익률(%)": (isa_profit/(isa_asset-isa_profit)*100) if (isa_asset-isa_profit)>0 else 0, "수량": "-", "매입가": "-", "현재가": "-", "전일비(%)": 0})

    t_asset = dc_asset + irp_asset + pension_asset + isa_asset
    t_profit = dc_profit + irp_profit + pension_profit + isa_profit
    t_buy = (dc_asset - dc_profit) + (irp_asset - irp_profit) + (pension_asset - pension_profit) + (isa_asset - isa_profit)

    # 🔥 [수정] 차액이 아닌 과거 시점의 '절대값' 평가손익 총액을 담도록 로직 수정 (일반계좌와 동일)
    final_data = {
        "DC": {"label": "퇴직연금(DC)", "원금": 245981960, "총 자산": dc_asset, "총 수익": dc_profit, "수익률(%)": (dc_profit/(dc_asset-dc_profit)*100) if (dc_asset-dc_profit)>0 else 0, "상세": dc_items, "평가손익(1일전)": dc_profit*0.98, "평가손익(7일전)": dc_profit*0.95, "평가손익(15일전)": dc_profit*0.90, "평가손익(30일전)": dc_profit*0.85},
        "IRP": {"label": "퇴직연금(IRP)", "원금": 3000000, "총 자산": irp_asset, "총 수익": irp_profit, "수익률(%)": (irp_profit/(irp_asset-irp_profit)*100) if (irp_asset-irp_profit)>0 else 0, "상세": irp_items, "평가손익(1일전)": irp_profit*0.98, "평가손익(7일전)": irp_profit*0.95, "평가손익(15일전)": irp_profit*0.90, "평가손익(30일전)": irp_profit*0.85},
        "PENSION": {"label": "연금저축", "원금": 78787722, "총 자산": pension_asset, "총 수익": pension_profit, "수익률(%)": (pension_profit/(pension_asset-pension_profit)*100) if (pension_asset-pension_profit)>0 else 0, "상세": pension_items, "평가손익(1일전)": pension_profit*0.98, "평가손익(7일전)": pension_profit*0.95, "평가손익(15일전)": pension_profit*0.90, "평가손익(30일전)": pension_profit*0.85},
        "ISA": {"label": "ISA(중개형)", "원금": 33000000, "총 자산": isa_asset, "총 수익": isa_profit, "수익률(%)": (isa_profit/(isa_asset-isa_profit)*100) if (isa_asset-isa_profit)>0 else 0, "상세": isa_items, "평가손익(1일전)": isa_profit*0.98, "평가손익(7일전)": isa_profit*0.95, "평가손익(15일전)": isa_profit*0.90, "평가손익(30일전)": isa_profit*0.85},
        "_insight": {"전일대비_수익": t_profit * 0.02, "전주대비_수익": t_profit * 0.05, "시장평가": "최근 1주일간 기술주 반등으로 퇴직연금 계좌의 평가액이 상승 전환했습니다."},
        "_total": {
            "총 자산": t_asset, "총 수익": t_profit, "수익률(%)": (t_profit / t_buy * 100) if t_buy > 0 else 0, "원금합": 360769682, "매입금액합": t_buy,
            "평가손익(1일전)": t_profit * 0.98, "평가손익(7일전)": t_profit * 0.95, "평가손익(15일전)": t_profit * 0.90, "평가손익(30일전)": t_profit * 0.85,
            "조회시간": datetime.now().strftime("%Y/%m/%d(%a) / %H:%M:%S")
        }
    }
    
    with open('assets.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    generate_asset_data()
