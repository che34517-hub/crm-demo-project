"""金融机构 AI 赋能型 CRM 系统 Demo —— 应用入口。

运行：streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from src import theme
from src.data import init_session_state
from src.views import ai_trainer, approval, cleaning, customers, dashboard

st.set_page_config(
    page_title="金融机构 AI 赋能型 CRM 系统",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

theme.inject_css()
init_session_state()

PAGES = {
    "📊 核心数据监控仪表盘": dashboard.render,
    "👥 机构客户与公海管理": customers.render,
    "📝 开户线上审批流": approval.render,
    "🧹 历史数据清洗与迁移": cleaning.render,
    "🤖 AI 辅助培训与文档生成": ai_trainer.render,
}

with st.sidebar:
    st.markdown(
        '<div class="brand">'
        '<div class="logo">🏦 智银 CRM</div>'
        '<div class="sub">金融机构 AI 赋能型<br>客户关系管理系统 · Demo</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    choice = st.radio("功能导航", list(PAGES.keys()), label_visibility="collapsed")
    st.markdown(
        '<div class="brand" style="border-bottom:none;border-top:1px solid '
        'rgba(255,255,255,0.12);padding-top:1rem;margin-top:1rem;">'
        '<div class="sub">基于实习经历构建的演示系统<br>所有数据均为模拟数据</div>'
        "</div>",
        unsafe_allow_html=True,
    )

PAGES[choice]()
