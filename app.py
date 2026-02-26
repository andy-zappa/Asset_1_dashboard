import streamlit as st
import json
import warnings
import google.generativeai as genai
import Andy_pension_v2
import os
import re

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="Andy's Asset Dashboard")

css = ""
<style>
.block-container{padding-top:3rem!important;padding-bottom:5rem!important;}
h3{font-size:26px!important;font-weight:bold;margin-bottom:10px;}
.sub-title{font-size:22px!important;font-weight:bold;margin:25px 0 10px;}
.main-table{width:100%;border-collapse:collapse;font-size:15px;text-align:center;margin-bottom:10px;}
.main-table th{background-color:#f2f2f2;padding:10px;border:1px solid #ddd;font-weight:bold!important; vertical-align:middle;}
.main-table td{padding:8px;border:1px solid #ddd;vertical-align:middle;}
.sum-row td{background-color:#fff9e6;font-weight:bold!important;}
.red{color:#FF2323!important;} .blue{color:#0047EB!important;}
.insight-box{background-color:#f0f4f8;padding:20px;border-radius:10px;border-left:5px solid #007bff;margin-bottom:25px;}
.box-title{font-size:20px!important;font-weight:bold;margin-bottom:15px;display:block;color:#333;}

/* 요약 텍스트 정밀 디자인 */
.summary-text {
    font-size: 16px !important;
    font-weight: bold !important;
    color: #333;
    margin-bottom: 10px;
}
.summary-val {
    font-size: 20px !important; 
}

/* 엑셀 스타일 병합 지원 */
.main-table th.th-eval { border-right: none !important; }
.main-table th.th-blank { border-left: none !important; border-bottom: none !important; padding: 0 !important; }
.main-table th.th-week { border-left: 1px solid #ddd !important; border-top: 1px solid #ddd !important; font-size: 13.5px; }

/* 이모지 지원 */
.zappa-icon {
    font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif !important;
    font-size: 32px !important;
}

/* =========================================================
   [최종 해결 7] 마커 재배치 및 유령 공간 완벽 삭제 & 배너 디자인
   ========================================================= */

/* 1. 배너 틀: 직사각형에 모서리만 살짝 둥글게(8px) */
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) {
    position: fixed !important;
    bottom: 30px !important;
    left: 50% !important; 
    transform: translateX(-50%) !important; 
    background: rgba(255, 255, 255, 0.98) !important;
    padding: 10px 15px !important; 
    border-radius: 8px !important; /* 모서리 살짝 둥근 직사각형 */
    box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important;
    border: 1px solid #e5e7eb !important;
    z-index: 999999 !important;
    display: flex !important;
    justify-content: center !important; 
    align-items: center !important; 
    gap: 0 !important; 
    width: max-content !important; 
}

/* 2. 유령 공간(초기화 버튼 찌그러짐 원인) 완전히 소멸시키기 */
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) div.element-container:has(#zappa-floating-menu) {
    display: none !important;
    position: absolute !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* 3. Streamlit 컬럼 분할 속성 강제 고정 (가운데 정렬) */
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) > div[data-testid="column"] {
    flex: 0 0 auto !important; 
    width: auto !important;
    min-width: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) div[data-testid="stButton"] {
    margin: 0 !important;
    padding: 0 !important;
}

/* 4. 버튼 본체: 투명 배경, 우측 파이프(|), 좌우 2칸 여백 */
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) button {
    background: transparent !important; 
    border: none !important; 
    border-right: 1.5px solid #d1d5db !important; /* 파이프(|) 구분선 */
    border-radius: 0 !important; 
    padding: 0 16px !important; /* 글자 양옆으로 정확히 2칸 여백 */
    height: 24px !important; 
    min-height: 24px !important;
    color: #8c8c8c !important; /* 기본 컬러: 회색 */
    font-size: 15px !important; 
    font-weight: 600 !important; 
    white-space: nowrap !important; 
    box-shadow: none !important; 
    transition: color 0.1s ease !important; 
    display: flex !important;
    align-items: center !important;
}

/* 마지막 '종목코드' 버튼은 우측 파이프(|) 선 제거 */
div[data-testid="stHorizontalBlock"]:has(#zappa-floating-menu) > div[data-testid="column"]:last-child button {
    border-right

