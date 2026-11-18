"""全局主题：金融蓝配色、CSS、通用小工具。

图表配色遵循 dataviz 方法（经过 CVD / 对比度校验的参考调色板），
金融蓝主题恰好以 blue（#2a78d6）作为分类首槽位。
"""
from __future__ import annotations

from html import escape

import streamlit as st

# --------------------------------------------------------------------------- #
# UI 主题色（页面 chrome）
# --------------------------------------------------------------------------- #
NAVY = "#0A2540"
PRIMARY = "#1E4E8C"
ACCENT = "#2A78D6"
ACCENT_DARK = "#1E5DBF"
BG = "#F4F7FB"
CARD = "#FFFFFF"
TEXT = "#16223B"
MUTED = "#5B6B85"
BORDER = "#E2E8F0"

# --------------------------------------------------------------------------- #
# 图表调色板（参考调色板实例，已校验）
# --------------------------------------------------------------------------- #
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
          "#e87ba4", "#008300", "#6250d6", "#e34948"]
# 漏斗等“序数”渐变用单色蓝阶（250 -> 700）
BLUE_RAMP = ["#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
             "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281"]

GOOD = "#0ca30c"
WARNING = "#fab219"
SERIOUS = "#ec835a"
CRITICAL = "#d03b3b"

INK = "#16223B"
MUTED_INK = "#898781"
GRID = "#e1e0d9"

# 状态 -> (背景色, 前景色)
STATUS_COLORS = {
    "资质初审中": ("#e8f0fb", "#1E4E8C"),
    "尽调中":     ("#fff4e0", "#b26a00"),
    "合规审查中": ("#ede9fe", "#5b3fd6"),
    "风控评估中": ("#ffe4e8", "#c2263e"),
    "已成功开户": ("#e6f7ec", "#0a7d32"),
    "已驳回":     ("#fdecec", "#c22b2b"),
    "待跟进":     ("#eef2f7", "#5B6B85"),
    "公海":       ("#eef2f7", "#5B6B85"),
}

_CSS = """
<style>
:root{
  --navy:#0A2540; --primary:#1E4E8C; --accent:#2A78D6; --bg:#F4F7FB;
  --text:#16223B; --muted:#5B6B85; --border:#E2E8F0;
}
.stApp{background:var(--bg);}
html, body, [class*="css"]{
  font-family: system-ui, -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  color:var(--text);
}
#MainMenu{visibility:hidden;} footer{visibility:hidden;}
[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:1.6rem; padding-bottom:3rem; max-width:1280px;}

/* ---- 侧边栏 ---- */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#0A2540 0%,#0E3053 100%);
  border-right:1px solid #123556;
}
[data-testid="stSidebar"] *{color:#D7E3F4;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#8FA8C9;}
[data-testid="stSidebar"] [role="radiogroup"]{gap:.35rem;}
[data-testid="stSidebar"] [role="radiogroup"] label{
  padding:.5rem .8rem; border-radius:8px; cursor:pointer; transition:background .15s ease; width:100%;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:rgba(255,255,255,0.08);}

.brand{padding:.5rem 0 1.1rem; border-bottom:1px solid rgba(255,255,255,0.12); margin-bottom:1rem;}
.brand .logo{font-size:1.4rem; font-weight:800; color:#fff; letter-spacing:.5px;}
.brand .sub{color:#8FA8C9; font-size:.76rem; margin-top:.3rem; line-height:1.5;}

/* ---- 顶部标题 ---- */
.page-title{font-size:1.55rem; font-weight:800; color:var(--text); margin-bottom:.2rem;}
.page-sub{font-size:.9rem; color:var(--muted); margin-bottom:1.1rem;}

/* ---- KPI 卡片 ---- */
.kpi-grid{display:flex; flex-wrap:wrap; gap:14px; margin-bottom:6px;}
.kpi-card{
  flex:1 1 180px; min-width:170px; background:#fff; border:1px solid var(--border);
  border-radius:12px; padding:18px 20px; box-shadow:0 1px 2px rgba(16,35,59,.04);
}
.kpi-label{font-size:.8rem; color:var(--muted); margin-bottom:8px;}
.kpi-value{font-size:1.75rem; font-weight:800; color:var(--text); line-height:1.1; font-variant-numeric:tabular-nums;}
.kpi-delta{font-size:.8rem; font-weight:700; margin-top:8px;}
.kpi-delta span{color:var(--muted); font-weight:400; margin-left:4px;}

/* ---- 分区卡片 ---- */
.sec-card{
  background:#fff; border:1px solid var(--border); border-radius:12px;
  padding:20px 22px; box-shadow:0 1px 2px rgba(16,35,59,.04); margin-bottom:16px;
}
.sec-title{font-size:1.02rem; font-weight:700; color:var(--text); margin-bottom:4px;}
.sec-sub{font-size:.82rem; color:var(--muted); margin-bottom:12px;}

/* ---- 按钮 ---- */
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button{
  border-radius:8px; font-weight:600;
}
[data-testid="stButton"] button[kind="primary"], [data-testid="stDownloadButton"] button{
  background:var(--accent); color:#fff;
}
[data-testid="stButton"] button[kind="primary"]:hover{background:#1E5DBF;}

/* ---- 输入 ---- */
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea{
  border-radius:8px; border-color:var(--border);
}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus{
  border-color:var(--accent); box-shadow:0 0 0 1px var(--accent);
}

/* ---- Tabs ---- */
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:4px; border-bottom:1px solid var(--border);}
[data-testid="stTabs"] button[data-baseweb="tab"]{font-weight:600; color:var(--muted); border-radius:8px 8px 0 0;}
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"]{
  color:var(--primary); border-bottom:2px solid var(--accent);
}

/* ---- 文件上传 ---- */
[data-testid="stFileUploader"] section{border-radius:10px; border:1.5px dashed #c4d2e6;}

/* ---- Metric ---- */
[data-testid="stMetric"]{
  background:#fff; border:1px solid var(--border); border-radius:10px; padding:14px 18px;
}

/* ---- 通用 pill ---- */
.pill{display:inline-block; padding:3px 11px; border-radius:999px; font-size:.78rem; font-weight:600; line-height:1.5; white-space:nowrap;}

/* ---- CRM 表格（固定列） ---- */
.crm-table-wrap{overflow-x:auto; border:1px solid var(--border); border-radius:12px; background:#fff; max-height:520px; overflow-y:auto;}
.crm-table{width:100%; border-collapse:separate; border-spacing:0; font-size:13px;}
.crm-table thead th{
  position:sticky; top:0; z-index:4; background:#f2f6fb; color:#3b4a66; font-weight:600;
  text-align:left; padding:12px 14px; white-space:nowrap; border-bottom:1px solid var(--border);
}
.crm-table tbody td{padding:11px 14px; border-bottom:1px solid #eef1f5; white-space:nowrap; color:var(--text);}
.crm-table tbody tr:last-child td{border-bottom:none;}
.crm-table tbody tr:hover td{background:#f7faff;}
.crm-table .pin-l, .crm-table thead th.pin-l{
  position:sticky; left:0; z-index:2; background:#fff; box-shadow:1px 0 0 var(--border);
}
.crm-table thead th.pin-l{z-index:5; background:#f2f6fb;}
.crm-table .pin-r, .crm-table thead th.pin-r{
  position:sticky; right:0; z-index:2; background:#fff; box-shadow:-1px 0 0 var(--border);
}
.crm-table thead th.pin-r{z-index:5; background:#f2f6fb;}
.crm-table .mono{font-family:ui-monospace, SFMono-Regular, Menlo, monospace; color:#3b4a66; letter-spacing:.2px;}
.crm-table .op-pill{display:inline-block; padding:4px 12px; border-radius:999px; font-size:.76rem; font-weight:600; cursor:pointer;}

/* ---- 审批步骤条 ---- */
.stepper{display:flex; align-items:flex-start; margin:10px 0 6px;}
.step{flex:1; text-align:center; position:relative;}
.step .dot{
  width:32px; height:32px; border-radius:50%; margin:0 auto 8px; display:flex; align-items:center;
  justify-content:center; font-size:.85rem; font-weight:700; background:#e6ebf2; color:#8a99b3;
  position:relative; z-index:1;
}
.step.done .dot{background:#e6f7ec; color:#0a7d32;}
.step.current .dot{background:var(--accent); color:#fff; box-shadow:0 0 0 4px rgba(42,120,214,.15);}
.step .t{font-size:.76rem; color:var(--muted); font-weight:600;}
.step.current .t{color:var(--primary); font-weight:700;}
.step::before{content:""; position:absolute; top:16px; left:-50%; width:100%; height:2px; background:#e6ebf2;}
.step:first-child::before{display:none;}
.step.done::before, .step.current::before{background:#9fd6b0;}

/* ---- 审批日志时间线 ---- */
.log-item{display:flex; gap:12px; padding:10px 2px; border-bottom:1px solid #eef1f5;}
.log-item:last-child{border-bottom:none;}
.log-dot{width:10px; height:10px; border-radius:50%; margin-top:5px; flex:0 0 auto;}
.log-body{font-size:.85rem; color:var(--text);}
.log-time{color:var(--muted); font-size:.74rem; margin-top:2px;}

/* ---- 文档预览 ---- */
.doc-frame{border:1px solid var(--border); border-radius:12px; background:#fff;}

h1,h2,h3{color:var(--text);}
</style>
"""


def inject_css() -> None:
    """注入全局 CSS。"""
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="page-title">{escape(title)}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-sub">{escape(subtitle)}</div>', unsafe_allow_html=True)


def sec_card(title: str, subtitle: str = "") -> None:
    """打开一个分区卡片（视觉容器，实际布局仍由 Streamlit 控制）。"""
    st.markdown(f'<div class="sec-title">{escape(title)}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="sec-sub">{escape(subtitle)}</div>', unsafe_allow_html=True)


def pill(text: str, bg: str, fg: str) -> str:
    return f'<span class="pill" style="background:{bg};color:{fg};">{escape(text)}</span>'


def status_pill(status: str) -> str:
    bg, fg = STATUS_COLORS.get(status, ("#eef2f7", TEXT))
    return pill(status, bg, fg)


def kpi_cards(cards) -> None:
    """渲染一排 KPI 卡片。cards: [(label, value, delta, delta_label, positive)]"""
    html = ['<div class="kpi-grid">']
    for label, value, delta, delta_label, positive in cards:
        color = GOOD if positive else CRITICAL
        arrow = "▲" if positive else "▼"
        sign = "" if delta.startswith(("+", "-", "▲", "▼")) else ("+" if positive else "-")
        html.append(
            '<div class="kpi-card">'
            f'<div class="kpi-label">{escape(label)}</div>'
            f'<div class="kpi-value">{escape(value)}</div>'
            f'<div class="kpi-delta" style="color:{color};">{arrow} {sign}{escape(delta)}'
            f'<span>{escape(delta_label)}</span></div>'
            '</div>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Plotly 通用样式
# --------------------------------------------------------------------------- #
def style_fig(fig, height: int = 360):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family='system-ui, -apple-system, "Segoe UI", "PingFang SC", sans-serif',
                  size=12, color=INK),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor=BORDER, font=dict(color=TEXT)),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=GRID, tickfont=dict(color=MUTED_INK))
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, linecolor=GRID, tickfont=dict(color=MUTED_INK))
    return fig
