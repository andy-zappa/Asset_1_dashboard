import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정 및 스타일 (Andy님 전용 모바일 최적화)
st.set_page_config(layout="wide", page_title="Andy ZAPPA Dashboard")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Nanum+Gothic', sans-serif; }
    
    /* 큰 폰트 유지 및 ₩ 삭제 반영 */
    .report-title { font-size: 26px !important; font-weight: 800; color: #1E1E1E; }
    .asset-summary-box { 
        background-color: #f8f9fa; padding: 15px; border-radius: 10px; 
        border-left: 5px solid #007bff; margin-bottom: 20px; 
    }
    .total-asset-text { font-size: 22px !important; font-weight: 700; display: flex; align-items: center; gap: 8px; }
    .profit-text { font-size: 18px !important; font-weight: 600; color: #d32f2f; }
    
    /* 테이블 가독성 */
    .stTable { font-size: 16px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상태 관리 (HTML의 프레임 전환 역할)
if 'menu_select' not in st.session_state:
    st.session_state.menu_select = "1630 절세계좌 보고"

# --- [프레임 1: 좌측 사이드바 메뉴] ---
with st.sidebar:
    st.title("🗂️ Andy's Menu")
    if st.button("📊 1630 절세계좌 보고", use_container_width=True):
        st.session_state.menu_select = "1630 절세계좌 보고"
    if st.button("🤖 ZAPPA AI 코딩 엔진", use_container_width=True):
        st.session_state.menu_select = "ZAPPA AI 코딩 엔진"
    if st.button("⚙️ 시스템 설정", use_container_width=True):
        st.session_state.menu_select = "시스템 설정"
    
    st.divider()
    st.caption(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# --- 메인 화면 레이아웃 분할 ---
# 프레임 2(엔진/채팅)와 프레임 3(리포트)를 1:2 비율로 분할
col_engine, col_report = st.columns([1, 2], gap="medium")

# --- [프레임 2 & 3: 내용 출력] ---
if st.session_state.menu_select == "1630 절세계좌 보고":
    
    # [프레임 2: 코딩 엔진 / 채팅창 역할]
    with col_engine:
        st.subheader("🤖 ZAPPA AI")
        st.info("현재 화면의 데이터를 수정하거나 분석을 요청하세요.")
        with st.container(border=True):
            chat_input = st.text_input("수정 명령 입력 (예: ISA 비중 조절해줘)")
            if chat_input:
                st.write(f"💬 '{chat_input}'에 대한 코드를 생성 중...")
            
            st.divider()
            st.button("andy_pension_v2.py 동기화")
            st.button("금일 종가 데이터 갱신")

    # [프레임 3: 실제 리포트 출력 구역]
    with col_report:
        today_str = datetime.now().strftime("%Y-%m-%d")
        st.markdown(f"<div class='report-title'>Andy {today_str} 절세계좌 자산 현황 (1630 보고)</div>", unsafe_allow_html=True)
        
        # [자파의 자산 인사이트] - 지침 준수 (상단 배치)
        st.warning("💡 **자파의 자산 인사이트**: 삼성화재GIC 이자가 일할 반영되었습니다. 전체 수익률이 안정적입니다.")

        # [1] 투자원금 대비 요약
        st.subheader("[1] 투자원금 대비 요약 (25.08)")
        st.markdown(f"""
        <div class='asset-summary-box'>
            <div class='total-asset-text'>💰 총자산 360,769,682 (원)</div>
            <div class='profit-text'>총수익 +7,225,318 (원) (+2.45%)</div>
        </div>
        """, unsafe_allow_html=True)

        # [2] 계좌 상세 (순서 엄수: DC -> 연금 -> ISA -> IRP)
        st.subheader("[2] 계좌별 상세 현황")
        
        with st.expander("퇴직 DC 상세", expanded=True):
            st.markdown("**총자산 245,981,960 (원) / 총수익 +1,500,000 (+0.61%)**")
            # 실제 데이터 테이블 (Andy님 평단가/주식수 기준)
            st.table(pd.DataFrame({"종목": ["TQQQ", "NVDA"], "금액": ["1억", "1.4억"]}))

        with st.expander("연금저축 상세", expanded=True):
            st.markdown("**총자산 78,787,722 (원) / 총수익 +800,000 (+1.01%)**")
            
        with st.expander("ISA 상세 (고정 4종목)", expanded=True):
            st.write("498400, 475720, 494300, 483280 종목 리스트")

elif st.session_state.menu_select == "ZAPPA AI 코딩 엔진":
    st.header("🛠️ 엔진 직접 수정 모드")
    st.code("# andy_pension_v2.py 내부 로직을 여기서 편집할 수 있게 구성 가능", language="python")
