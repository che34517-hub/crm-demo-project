"""📝 开户线上审批流（4 级状态机）。"""
from __future__ import annotations

from html import escape

import streamlit as st

from src import theme
from src.data import APPROVERS, STAGES


def render() -> None:
    theme.page_header("开户线上审批流",
                      "发起申请 → 主管初审 → 合规审查 → 风控评估 → 运营归档，全程留痕")

    apps = st.session_state.approvals
    labels = [f"{a['id']} · {a['customer']}" for a in apps]
    idx = st.selectbox("选择开户申请单", range(len(apps)), format_func=lambda i: labels[i])

    app = apps[idx]
    stage = app["stage"]

    # ---- 申请单信息 ----
    _app_info(app)

    # ---- 进度条 ----
    st.markdown('<div class="sec-title">审批进度</div>', unsafe_allow_html=True)
    st.markdown(_stepper(stage), unsafe_allow_html=True)
    if stage < len(STAGES):
        st.caption(f"当前节点：**{STAGES[stage]}** · 处理人：{APPROVERS[stage] or '客户经理（发起人）'}")
    else:
        st.success("🎉 该申请已完成全流程审批并归档")

    st.write("")

    # ---- 审批操作区 ----
    st.markdown('<div class="sec-title">审批操作区</div>', unsafe_allow_html=True)
    _action_area(app)

    st.write("")

    # ---- 审批日志 ----
    st.markdown('<div class="sec-title">审批日志留痕</div>', unsafe_allow_html=True)
    st.markdown(_log_timeline(app["logs"]), unsafe_allow_html=True)


def _app_info(app) -> None:
    c = st.columns(5)
    c[0].metric("申请编号", app["id"])
    c[1].metric("客户名称", app["customer"])
    c[2].metric("账户类型", app["type"])
    c[3].metric("发起人", app["applicant"])
    c[4].metric("预计资金(万元)", app["amount"])
    st.write("")


def _action_area(app) -> None:
    stage = app["stage"]

    if stage >= len(STAGES):
        st.info("该申请已归档，无需进一步操作。")
        return

    if stage == 0:
        # 被驳回后，由客户经理重新提交
        if st.button("📤 重新提交申请", type="primary"):
            app["logs"].append(_log_entry("重新提交申请", "发起申请",
                                          "客户经理（发起人）", "已按要求修改并重新提交"))
            app["stage"] = 1
            st.toast("已重新提交，流转至主管初审", icon="📤")
            st.rerun()
        return

    left, right = st.columns([1, 2.4], gap="medium")
    with left:
        ok = st.button("✅ 同意 / 通过", type="primary", width="stretch")
    with right:
        st.markdown("**驳回重提**（需填写理由批注）")
        reason = st.text_area("驳回理由", key=f"reject_reason_{app['id']}",
                              placeholder="请填写驳回原因，便于发起人修改后重新提交…", height=90)
        reject = st.button("⛔ 驳回重提", width="stretch", type="secondary")

    if ok:
        app["logs"].append(_log_entry("同意", STAGES[stage], APPROVERS[stage], ""))
        app["stage"] += 1
        st.toast(f"已通过「{STAGES[stage - 1]}」，流转至下一节点", icon="✅")
        st.rerun()
    if reject:
        if not reason.strip():
            st.warning("驳回需填写理由批注")
        else:
            app["logs"].append(_log_entry("驳回重提", STAGES[stage], APPROVERS[stage], reason.strip()))
            app["stage"] = 0
            st.toast("已驳回至发起人重新提交", icon="⛔")
            st.rerun()


def _log_entry(action, node, actor, reason):
    import datetime
    return {"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "actor": actor, "action": action, "node": node, "reason": reason}


def _stepper(stage: int) -> str:
    parts = []
    for i, s in enumerate(STAGES):
        if i < stage:
            cls, icon = "done", "✓"
        elif i == stage:
            cls, icon = "current", str(i + 1)
        else:
            cls, icon = "", str(i + 1)
        parts.append(f'<div class="step {cls}"><div class="dot">{icon}</div>'
                     f'<div class="t">{escape(s)}</div></div>')
    return '<div class="stepper">' + "".join(parts) + "</div>"


def _log_timeline(logs) -> str:
    if not logs:
        return '<div style="color:#8a99b3;font-size:.85rem;">暂无审批记录</div>'
    color = {"同意": theme.GOOD, "重新提交申请": theme.ACCENT,
             "发起申请": theme.ACCENT, "驳回重提": theme.CRITICAL}
    items = []
    for lg in logs:
        c = color.get(lg["action"], theme.MUTED_INK)
        reason = f'<div style="margin-top:4px;padding:6px 10px;background:#fdecec;border-radius:6px;color:#c22b2b;">驳回理由：{escape(lg["reason"])}</div>' if lg["reason"] else ""
        items.append(
            '<div class="log-item">'
            f'<span class="log-dot" style="background:{c};"></span>'
            '<div class="log-body">'
            f'<b>{escape(lg["action"])}</b> · {escape(lg["node"])} '
            f'<span style="color:{theme.MUTED};">（{escape(lg["actor"])}）</span>'
            f'{reason}'
            f'<div class="log-time">{escape(lg["time"])}</div>'
            '</div></div>'
        )
    return '<div style="background:#fff;border:1px solid %s;border-radius:12px;padding:10px 18px;">%s</div>' % (
        theme.BORDER, "".join(items))
