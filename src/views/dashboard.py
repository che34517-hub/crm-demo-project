"""📊 核心数据监控仪表盘。"""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src import theme
from src.data import FUNNEL, FUNNEL_STAGES, TEAMS, TEAM_PERF, WEEKLY


def render() -> None:
    theme.page_header("核心数据监控仪表盘",
                      "AI 赋能线索运营与开户全流程的实时数据总览")

    # ---- KPI 卡片 ----
    theme.kpi_cards([
        ("线索转化率", "18.6%", "+18%", "AI 智能评分后环比提升", True),
        ("跟进活跃度", "82.4%", "+20%", "智能提醒触发后环比提升", True),
        ("开户完成率", "48.6%", "+5.4%", "较上月提升", True),
        ("成单周期", "14.2 天", "20%", "较上线前缩短", True),
        ("人工核对耗时", "1.5 小时", "75%", "原 6 小时 / 单", True),
    ])
    st.write("")

    col_left, col_right = st.columns([1.25, 1], gap="medium")

    with col_left:
        _render_funnel()
    with col_right:
        _render_activity()

    st.write("")
    _render_team_perf()


def _render_funnel() -> None:
    st.markdown('<div class="sec-title">按销售团队拆解的线索转化漏斗</div>'
                '<div class="sec-sub">从线索到成功开户的逐级转化（可多选团队对比）</div>',
                unsafe_allow_html=True)
    teams = st.multiselect("选择团队", TEAMS, default=TEAMS[:3], key="funnel_teams",
                           label_visibility="collapsed")

    fig = go.Figure()
    for i, team in enumerate(teams):
        fig.add_trace(go.Funnel(
            name=team, y=FUNNEL_STAGES, x=FUNNEL[team],
            textposition="inside", textinfo="value",
            marker=dict(color=theme.SERIES[i], line=dict(color="#ffffff", width=1)),
        ))
    fig = theme.style_fig(fig, height=380)
    st.plotly_chart(fig, config={"displayModeBar": False})


def _render_activity() -> None:
    st.markdown('<div class="sec-title">周跟进活跃度趋势</div>'
                '<div class="sec-sub">AI 智能提醒上线后，跟进活跃度持续攀升</div>',
                unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=WEEKLY["week"], y=WEEKLY["activity"], name="跟进活跃度",
        mode="lines+markers", line=dict(color=theme.ACCENT, width=2),
        marker=dict(size=6, color=theme.ACCENT),
        fill="tozeroy", fillcolor="rgba(42,120,214,0.10)",
    ))
    fig.add_trace(go.Scatter(
        x=WEEKLY["week"], y=WEEKLY["target"], name="目标基准",
        mode="lines", line=dict(color=theme.MUTED_INK, width=1.5, dash="dash"),
    ))
    fig = theme.style_fig(fig, height=380)
    st.plotly_chart(fig, config={"displayModeBar": False})


def _render_team_perf() -> None:
    st.markdown('<div class="sec-title">各团队开户完成率</div>'
                '<div class="sec-sub">单色编码，按完成率从高到低排序</div>',
                unsafe_allow_html=True)

    teams = [t for t, _ in TEAM_PERF]
    rates = [r for _, r in TEAM_PERF]
    fig = go.Figure(go.Bar(
        x=rates, y=teams, orientation="h", marker_color=theme.ACCENT,
        text=[f"{r:.1f}%" for r in rates], textposition="outside",
        marker=dict(cornerradius=4),
    ))
    fig.update_layout(xaxis=dict(range=[0, 65]))
    fig = theme.style_fig(fig, height=250)
    st.plotly_chart(fig, config={"displayModeBar": False})
