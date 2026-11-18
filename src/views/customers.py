"""👥 机构客户与公海管理。"""
from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from src import theme
from src.data import TEAMS


def render() -> None:
    theme.page_header("机构客户与公海管理",
                      "高频检索、多维筛选与状态标签，公海客户一键领取")

    df: pd.DataFrame = st.session_state.customers
    tab_mine, tab_sea = st.tabs(["👤 我的客户", "🌊 公海客户"])

    with tab_mine:
        _render_tab(df, mine=True)
    with tab_sea:
        _render_tab(df, mine=False)


def _render_tab(df: pd.DataFrame, mine: bool) -> None:
    subset = df[df["is_mine"] == mine].copy()
    total = len(subset)

    col_metric1, col_metric2 = st.columns(2)
    col_metric1.metric("客户数量", f"{total} 家")
    col_metric2.metric(
        "高价值客户（注册资本 ≥ 1 亿）",
        f"{int((subset['注册资本(万元)'] >= 10000).sum())} 家",
    )

    # ---- 检索 + 筛选 ----
    c1, c2, c3 = st.columns([1.4, 1, 1])
    with c1:
        keyword = st.text_input("🔍 搜索", placeholder="输入客户名称 / 统一社会信用代码",
                                key=f"kw_{mine}")
    with c2:
        industry = st.multiselect("行业", sorted(df["行业"].unique()), key=f"ind_{mine}")
    with c3:
        team = st.multiselect("归属团队", TEAMS, key=f"team_{mine}")

    status = st.multiselect("状态", sorted(df["状态"].unique()), key=f"st_{mine}")

    filtered = subset
    if keyword.strip():
        kw = keyword.strip().upper()
        filtered = filtered[
            filtered["客户名称"].str.contains(keyword.strip(), case=False)
            | filtered["统一社会信用代码"].str.upper().str.contains(kw, na=False)
        ]
    if industry:
        filtered = filtered[filtered["行业"].isin(industry)]
    if team:
        filtered = filtered[filtered["归属团队"].isin(team)]
    if status:
        filtered = filtered[filtered["状态"].isin(status)]

    # ---- 操作台 ----
    with st.container():
        oc1, oc2, oc3 = st.columns([2, 1, 1], vertical_alignment="bottom")
        names = filtered["客户名称"].tolist()
        with oc1:
            selected = st.selectbox("选择要操作的客户", names, key=f"sel_{mine}") if names else None
        with oc2:
            if st.button("📋 查看详情", key=f"detail_{mine}", disabled=not names,
                         width="stretch"):
                _show_detail(filtered, selected)
        with oc3:
            if mine:
                if st.button("↩️ 退回公海", key=f"release_{mine}", disabled=not names,
                             width="stretch", type="secondary"):
                    _release(selected)
            else:
                if st.button("🎯 领取客户", key=f"claim_{mine}", disabled=not names,
                             width="stretch", type="primary"):
                    _claim(selected)

    st.caption(f"共 {len(filtered)} 条 · 客户名称列与操作列为固定列，可左右滚动查看")

    # ---- 表格（HTML，固定列 + 状态标签） ----
    st.markdown(_table_html(filtered, mine), unsafe_allow_html=True)


def _show_detail(df: pd.DataFrame, name: str) -> None:
    row = df[df["客户名称"] == name].iloc[0]
    with st.expander(f"客户详情 · {name}", expanded=True):
        c1, c2 = st.columns(2)
        c1.markdown(f"**统一社会信用代码**\n\n`{row['统一社会信用代码']}`")
        c1.markdown(f"**行业**\n\n{row['行业']}")
        c1.markdown(f"**归属团队**\n\n{row['归属团队']}")
        c2.markdown(f"**联系人 / 电话**\n\n{row['联系人']} · {row['联系电话']}")
        c2.markdown(f"**注册资本**\n\n{row['注册资本(万元)']:,} 万元")
        c2.markdown(f"**状态**\n\n{theme.status_pill(row['状态'])}", unsafe_allow_html=True)


def _claim(name: str) -> None:
    df = st.session_state.customers
    idx = df[df["客户名称"] == name].index[0]
    st.session_state.customers.loc[idx, "is_mine"] = True
    st.session_state.customers.loc[idx, "状态"] = "待跟进"
    st.toast(f"已领取「{name}」，转入我的客户", icon="🎯")


def _release(name: str) -> None:
    df = st.session_state.customers
    idx = df[df["客户名称"] == name].index[0]
    st.session_state.customers.loc[idx, "is_mine"] = False
    st.session_state.customers.loc[idx, "状态"] = "公海"
    st.toast(f"已将「{name}」退回公海", icon="↩️")


def _table_html(df: pd.DataFrame, mine: bool) -> str:
    cols = ["客户名称", "统一社会信用代码", "行业", "归属团队", "状态",
            "联系人", "联系电话", "注册资本(万元)", "录入日期"]

    head = ["客户名称", "统一社会信用代码", "行业", "归属团队", "状态",
            "联系人", "联系电话", "注册资本(万元)", "录入日期", "操作"]

    thead = "<tr>" + "".join(
        f'<th class="{"pin-l" if c == "客户名称" else ("pin-r" if c == "操作" else "")}">{c}</th>'
        for c in head
    ) + "</tr>"

    rows = []
    for _, r in df.iterrows():
        if mine:
            op = '<span class="op-pill" style="background:#eef2f7;color:#5B6B85;">查看 / 退回</span>'
        else:
            op = '<span class="op-pill" style="background:#e8f0fb;color:#1E4E8C;">🎯 领取</span>'
        td = [
            f'<td class="pin-l" style="font-weight:600;color:{theme.PRIMARY};">{escape(r["客户名称"])}</td>',
            f'<td class="mono">{escape(r["统一社会信用代码"])}</td>',
            f'<td>{escape(r["行业"])}</td>',
            f'<td>{escape(r["归属团队"])}</td>',
            f'<td>{theme.status_pill(r["状态"])}</td>',
            f'<td>{escape(r["联系人"])}</td>',
            f'<td class="mono">{escape(r["联系电话"])}</td>',
            f'<td style="text-align:right;">{r["注册资本(万元)"]:,}</td>',
            f'<td>{r["录入日期"].strftime("%Y-%m-%d")}</td>',
            f'<td class="pin-r">{op}</td>',
        ]
        rows.append("<tr>" + "".join(td) + "</tr>")

    if not rows:
        rows.append('<tr><td colspan="10" style="text-align:center;color:#8a99b3;padding:28px;">'
                    "暂无匹配的客户数据</td></tr>")

    return (f'<div class="crm-table-wrap"><table class="crm-table">'
            f"<thead>{thead}</thead><tbody>{''.join(rows)}</tbody></table></div>")
