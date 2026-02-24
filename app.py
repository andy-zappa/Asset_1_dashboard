import streamlit as st
import json
import warnings
import google.generativeai as genai
import Andy_pension_v2

warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", page_title="Andy's Asset Dashboard")

css = [
    "<style>",
    ".block-container{padding-top:3rem!important;padding-bottom:5rem!important;}",
    "h3{font-size:26px!important;font-weight:bold;margin-bottom:10px;}",
    ".sub-title{font-size:22px!important;font-weight:bold;margin:25px 0 10px;}",
    ".main-table{width:100%;border-collapse:collapse;font-size:15px;text-align:center;margin-bottom:10px;}",
    ".main-table th{background-color:#f2f2f2;padding:10px;border:1px solid #ddd;font-weight:bold!important;}",
    ".main-table td{padding:8px;border:1px solid #ddd;vertical-align:middle;}",
    ".sum-row td{background-color:#fff9e6;font-weight:bold!important;}",
    ".red{color:#FF2323!important;} .blue{color:#0047EB!important;}",
    ".sidebar-header{display:flex;align-items:center;gap:12px;margin-bottom:20px; font-size:22px;font-weight:bold;}",
    
    # [핵심] 버튼 간격 완전 밀착 및 13px 고정, 줄바꿈 금지(nowrap)
    "div[data-testid='stHorizontalBlock'] { gap: 0 !important; }",
    "div[data-testid='column'] { padding: 0 !important; }",
    "div.stButton>button { font-weight:normal!important; border-radius:3px; padding:0.2rem 0!important; width:100%!important; font-size:13px!important; margin:0!important; white-space:nowrap!important; }",
    "</style>"
]
st.markdown("".join(css), unsafe_allow_html=True)

if 'sort_mode' not in st.session_state: 
    st.session_state.sort_mode = 'init'
if 'show_code' not in st.session_state: 
    st.session_state.show_code = False
if 'init' not in st.session_state:
    with st.spinner("데이터 로딩
