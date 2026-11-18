"""模拟数据与 session_state 初始化。

所有数据在首次加载时生成并缓存到 st.session_state，保证跨模块切换、
跨 rerun 的一致性与状态可变更（如公海领取、审批推进）。
"""
from __future__ import annotations

import random

import pandas as pd
import streamlit as st

TEAMS = ["企业金融一部", "企业金融二部", "同业金融部", "华南大区团队"]

STAGES = ["发起申请", "主管初审", "合规审查", "风控评估", "运营归档"]
APPROVERS = ["", "主管 · 李志强", "合规 · 王雪", "风控 · 赵鹏", "运营 · 陈静"]

VALID_CODE_CHARS = "0123456789ABCDEFGHJKLMNPQRTUWXY"

# --------------------------------------------------------------------------- #
# 基础随机工具
# --------------------------------------------------------------------------- #
_CITIES = ["北京", "上海", "深圳", "广州", "杭州", "苏州", "南京", "成都",
           "武汉", "西安", "青岛", "宁波", "厦门", "长沙", "重庆", "郑州"]
_PREFIX = ["华信", "中天", "恒润", "金鼎", "瑞丰", "银泰", "宏远", "德盛",
           "鼎盛", "润泽", "博远", "华创", "中晟", "国泰", "富达", "启明"]
_SUFFIX = ["科技有限公司", "实业有限公司", "集团有限公司", "股份有限公司",
           "控股有限公司", "投资有限公司", "贸易有限公司", "信息科技有限公司"]
_SURNAMES = ["张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴",
             "徐", "孙", "马", "朱", "胡", "郭", "何", "林"]
_GIVEN = ["伟", "芳", "娜", "敏", "静", "磊", "军", "洋", "勇", "艳",
          "杰", "涛", "明", "超", "秀英", "霞", "平", "刚", "桂英"]
_INDUSTRIES = ["制造业", "信息技术", "医药生物", "房地产", "批发零售",
               "金融业", "建筑业", "能源", "交通运输", "农林牧渔"]


def _uscc(rng: random.Random) -> str:
    return ("91"
            + "".join(rng.choices("0123456789", k=6))
            + "".join(rng.choices(VALID_CODE_CHARS, k=9))
            + str(rng.randint(0, 9)))


def _company_name(rng: random.Random, used: set) -> str:
    while True:
        name = f"{rng.choice(_CITIES)}{rng.choice(_PREFIX)}{rng.choice(_SUFFIX)}"
        if name not in used:
            used.add(name)
            return name


def _contact(rng: random.Random) -> str:
    return rng.choice(_SURNAMES) + rng.choice(_GIVEN)


def _phone(rng: random.Random) -> str:
    return "1" + rng.choice("3456789") + "".join(rng.choices("0123456789", k=9))


def _capital(rng: random.Random) -> int:
    return rng.randint(100, 50000)


# --------------------------------------------------------------------------- #
# 机构客户（我的客户 / 公海）
# --------------------------------------------------------------------------- #
def _make_customers(rng: random.Random) -> pd.DataFrame:
    n_mine, n_sea = 38, 22
    used = set()
    rows = []
    for i in range(n_mine + n_sea):
        is_mine = i < n_mine
        if is_mine:
            status = rng.choices(
                ["资质初审中", "尽调中", "合规审查中", "风控评估中",
                 "已成功开户", "已驳回", "待跟进"],
                weights=[18, 14, 12, 12, 30, 6, 8], k=1)[0]
        else:
            status = "公海"
        rows.append({
            "客户名称": _company_name(rng, used),
            "统一社会信用代码": _uscc(rng),
            "行业": rng.choice(_INDUSTRIES),
            "归属团队": rng.choice(TEAMS),
            "状态": status,
            "联系人": _contact(rng),
            "联系电话": _phone(rng),
            "注册资本(万元)": _capital(rng),
            "录入日期": pd.Timestamp("2026-01-01") + pd.Timedelta(days=rng.randint(0, 288)),
            "is_mine": is_mine,
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# 仪表盘数据
# --------------------------------------------------------------------------- #
FUNNEL_STAGES = ["线索", "有效线索", "商机", "开户申请", "成功开户"]
FUNNEL = {
    "企业金融一部": [1200, 980, 640, 380, 210],
    "企业金融二部": [980, 810, 520, 300, 168],
    "同业金融部": [760, 640, 410, 250, 140],
    "华南大区团队": [640, 520, 340, 200, 112],
}

WEEKLY = {
    "week": [f"第{i}周" for i in range(1, 13)],
    "activity": [58, 62, 60, 66, 68, 72, 70, 76, 78, 80, 82, 84],
    "target": [70] * 12,
}

TEAM_PERF = [
    ("企业金融一部", 55.2),
    ("企业金融二部", 52.8),
    ("同业金融部", 47.1),
    ("华南大区团队", 45.6),
]


# --------------------------------------------------------------------------- #
# 开户审批申请
# --------------------------------------------------------------------------- #
def _make_approvals():
    def logs_for(stage: int, applicant: str):
        logs = [{"time": "2026-10-12 09:12", "actor": applicant,
                 "action": "发起申请", "node": "发起申请", "reason": ""}]
        for i in range(1, stage):
            logs.append({"time": f"2026-10-1{min(i, 5)} 1{i}:2{i}",
                         "actor": APPROVERS[i], "action": "同意",
                         "node": STAGES[i], "reason": ""})
        return logs

    apps = [
        {"id": "KH-2026-1012-001", "customer": "北京华信科技有限公司", "type": "基本存款账户",
         "applicant": "客户经理 · 张伟", "amount": "200", "stage": 1},
        {"id": "KH-2026-1011-008", "customer": "上海中天实业有限公司", "type": "一般存款账户",
         "applicant": "客户经理 · 刘洋", "amount": "1200", "stage": 2},
        {"id": "KH-2026-1010-013", "customer": "深圳恒润集团有限公司", "type": "基本存款账户",
         "applicant": "客户经理 · 陈静", "amount": "5000", "stage": 3},
        {"id": "KH-2026-1009-005", "customer": "杭州金鼎股份有限公司", "type": "专用存款账户",
         "applicant": "客户经理 · 王芳", "amount": "800", "stage": 4},
    ]
    for a in apps:
        a["logs"] = logs_for(a["stage"], a["applicant"])
    return apps


# --------------------------------------------------------------------------- #
# 历史数据清洗样本
# --------------------------------------------------------------------------- #
_DIRTY_INDUSTRY = ["制造业", "信息技术", "医药生物", "批发零售", "金融业", "建筑业"]


def _make_dirty_data(rng: random.Random) -> pd.DataFrame:
    n = 1500
    used = set()
    names = []
    for _ in range(n):
        base = f"{rng.choice(_CITIES)}{rng.choice(_PREFIX)}{rng.choice(_SUFFIX)}"
        j = 2
        name = base
        while name in used:
            name = f"{base}{j}"
            j += 1
        used.add(name)
        names.append(name)

    df = pd.DataFrame({
        "客户名称": names,
        "统一社会信用代码": [_uscc(rng) for _ in range(n)],
        "联系人": [_contact(rng) for _ in range(n)],
        "联系电话": [_phone(rng) for _ in range(n)],
        "行业": [rng.choice(_DIRTY_INDUSTRY) for _ in range(n)],
        "注册资本(万元)": [rng.randint(100, 50000) for _ in range(n)],
        "录入日期": [pd.Timestamp("2024-01-01") + pd.Timedelta(days=rng.randint(0, 700))
                    for _ in range(n)],
    })

    # 1) 统一社会信用代码位数错误（30 条 -> 清洗时剔除）
    for i in range(30):
        df.loc[i, "统一社会信用代码"] = df.loc[i, "统一社会信用代码"][:15]
    # 2) 缺失联系人（200 条 -> 清洗时补全）
    for i in range(30, 230):
        df.loc[i, "联系人"] = ""
    # 3) 重复录入（90 条 -> 清洗时去重）
    for i in range(230, 320):
        df.loc[i, "统一社会信用代码"] = df.loc[i - 200, "统一社会信用代码"]

    return df


# --------------------------------------------------------------------------- #
# 数据校验（统一社会信用代码 / 联系人 / 重复）
# --------------------------------------------------------------------------- #
_USCC_RE = None


def _uscc_pattern():
    global _USCC_RE
    if _USCC_RE is None:
        import re
        # 18 位：登记管理部门(1) + 机构类别(1) + 行政区划(6) + 组织机构代码(9) + 校验码(1)
        _USCC_RE = re.compile(r"^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$")
    return _USCC_RE


def detect_anomalies(df: pd.DataFrame):
    """返回 (异常原因 Series, 各原因计数)。"""
    code_col = "统一社会信用代码"
    pat = _uscc_pattern()
    codes = df[code_col].astype(str)
    n = len(df)

    invalid = (~codes.str.match(pat)).tolist()
    if "联系人" in df.columns:
        missing = (df["联系人"].isna()
                   | (df["联系人"].astype(str).str.strip() == "")).tolist()
    else:
        missing = [False] * n
    dup = codes.duplicated(keep="first").tolist()

    reason_list = []
    for pos in range(n):
        parts = []
        if invalid[pos]:
            parts.append("统一社会信用代码位数/格式错误")
        if missing[pos]:
            parts.append("缺失联系人")
        if dup[pos] and not invalid[pos]:
            parts.append("重复录入")
        reason_list.append("、".join(parts))

    reasons = pd.Series(reason_list, index=df.index, dtype=object)
    counts = {}
    for r in reasons[reasons != ""]:
        for part in r.split("、"):
            counts[part] = counts.get(part, 0) + 1
    return reasons, counts


# --------------------------------------------------------------------------- #
# 初始化入口
# --------------------------------------------------------------------------- #
def init_session_state() -> None:
    if "customers" not in st.session_state:
        st.session_state.customers = _make_customers(random.Random(42))
    if "approvals" not in st.session_state:
        st.session_state.approvals = _make_approvals()
    if "clean_dirty" not in st.session_state:
        st.session_state.clean_dirty = _make_dirty_data(random.Random(7))
