"""🧹 历史数据清洗与迁移工具。"""
from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from src import theme
from src.data import detect_anomalies, _uscc_pattern


def render() -> None:
    theme.page_header("历史数据清洗与迁移工具",
                      "上传 Excel/CSV 自动校验，识别异常并一键清洗导出")

    # ---- 数据源 ----
    uploaded = st.file_uploader("上传历史数据（Excel / CSV）", type=["csv", "xlsx", "xls"])
    if uploaded is not None:
        df = _read_upload(uploaded)
        source_note = f"已读取上传文件：`{uploaded.name}`"
    else:
        df = st.session_state.clean_dirty
        source_note = "当前使用内置示例数据（含 300+ 条异常）"
        st.download_button(
            "⬇️ 下载示例数据（可用作上传模板）",
            _sample_csv_bytes(df), "历史客户数据_示例.csv", "text/csv",
            key="dl_sample",
        )
    st.caption(source_note)

    # ---- 校验 ----
    reasons, counts = detect_anomalies(df)
    anomaly_mask = reasons != ""
    n_total = len(df)
    n_anomaly = int(anomaly_mask.sum())
    n_invalid = counts.get("统一社会信用代码位数/格式错误", 0)
    success_rate = (n_total - n_invalid) / n_total * 100 if n_total else 0.0
    cleaned = _clean(df)

    st.write("")
    theme.kpi_cards([
        ("原始记录数", f"{n_total:,}", "", "", True),
        ("识别异常数据", f"{n_anomaly:,}", "需清洗", "", False),
        ("迁移成功率", f"{success_rate:.1f}%", f"{n_total - n_invalid:,} 条", "成功迁移", True),
        ("清洗后记录数", f"{len(cleaned):,}", "去重+剔除后", "", True),
    ])

    # ---- 异常类型分布 ----
    if counts:
        st.markdown('<div class="sec-title">异常类型分布</div>', unsafe_allow_html=True)
        chips = "".join(
            f'<span class="pill" style="background:#fdecec;color:#c22b2b;margin-right:8px;">'
            f'{k} · {v} 条</span>' for k, v in sorted(counts.items(), key=lambda x: -x[1])
        )
        st.markdown(chips, unsafe_allow_html=True)

    # ---- 高亮异常数据 ----
    st.markdown('<div class="sec-title">异常数据明细（标红高亮）</div>', unsafe_allow_html=True)
    only_bad = st.toggle("仅显示异常数据", value=False)
    disp = df.copy()
    disp["异常原因"] = reasons
    if only_bad:
        disp = disp[anomaly_mask]
    disp = disp.reset_index(drop=True)

    st.dataframe(_styled(disp), height=430, width="stretch", hide_index=True)

    # ---- 清洗并导出 ----
    st.markdown('<div class="sec-title">清洗并导出</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1], gap="medium")
    with c1:
        st.success(
            f"✅ 迁移成功率 **{success_rate:.1f}%**（{n_total - n_invalid:,} / {n_total:,}）。"
            f"补全联系人 {counts.get('缺失联系人', 0)} 条、去重 {counts.get('重复录入', 0)} 条、"
            f"剔除无效代码 {n_invalid} 条。"
        )
    with c2:
        st.download_button(
            "🧹 一键清洗并导出 CSV", _clean_csv_bytes(cleaned),
            "清洗后客户数据.csv", "text/csv", key="dl_clean",
            type="primary", width="stretch",
        )


def _read_upload(uploaded) -> pd.DataFrame:
    name = uploaded.name.lower()
    try:
        if name.endswith(".csv"):
            return pd.read_csv(uploaded, dtype=str)
        return pd.read_excel(uploaded, dtype=str)
    except Exception as e:  # noqa: BLE001
        st.error(f"读取文件失败：{e}")
        return st.session_state.clean_dirty


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    pat = _uscc_pattern()
    out = df[df["统一社会信用代码"].astype(str).str.match(pat)].copy()
    out["统一社会信用代码"] = out["统一社会信用代码"].astype(str).str.strip()
    out["客户名称"] = out["客户名称"].astype(str).str.strip()
    if "联系人" in out.columns:
        out["联系人"] = out["联系人"].fillna("").astype(str).str.strip().replace("", "待补充")
    out = out.drop_duplicates(subset=["统一社会信用代码"], keep="first")
    return out.reset_index(drop=True)


def _styled(df: pd.DataFrame):
    def style_row(row):
        if row["异常原因"]:
            return ["background-color:#fdecec;color:#8a1f1f;"] * len(row)
        return [""] * len(row)
    return df.style.apply(style_row, axis=1)


def _sample_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def _clean_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")
