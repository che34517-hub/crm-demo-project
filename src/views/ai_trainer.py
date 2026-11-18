"""🤖 AI 辅助培训与文档生成器。

优先调用 DeepSeek 大模型（OpenAI 兼容接口）生成结构化 HTML 操作手册 / FAQ；
未配置 API Key 或调用失败时，自动回退到内置规则模板引擎，保证离线可用。
"""
from __future__ import annotations

import datetime
import os
from html import escape

import streamlit as st
from openai import OpenAI

from src import theme

MODULES = ["开户申请流程", "客户信息管理", "审批流调整", "数据清洗与迁移"]
AUDIENCES = ["客户经理", "合规/风控专员", "运营人员", "全员"]

_PROMPT_TEMPLATE = (
    "你是一名金融机构 CRM 培训专家。请根据以下变更需求，生成一份结构化的"
    "《CRM 操作手册与 FAQ》：\n"
    "- 变更标题：{title}\n"
    "- 变更内容：{content}\n"
    "- 目标模块：{module}\n"
    "- 目标受众：{audience}\n"
    "要求：输出 HTML，包含「变更概述 / 操作步骤 / 常见问题 FAQ / 注意事项」四部分，"
    "语言专业、面向一线业务人员。"
)

_SYSTEM_PROMPT = (
    "你是一名资深金融机构 CRM 培训专家，擅长将系统变更转化为面向一线业务人员的操作文档。"
    "请根据用户提供的变更需求，输出一份完整的、可直接渲染的 HTML 文档"
    "（包含 <!DOCTYPE html> 与内联 CSS）。"
    "文档必须包含以下四个部分：变更概述、操作步骤、常见问题 FAQ、注意事项。"
    "风格要求：专业金融蓝主题（主色 #1E4E8C / #2A78D6），白色卡片分区、圆角、"
    "清晰的层级标题、合适的图标点缀，适合内部培训与 FAQ 使用；语言专业、简洁、面向业务人员。"
    "只输出 HTML 代码本身，不要输出任何解释性文字或 Markdown 代码围栏。"
)


# --------------------------------------------------------------------------- #
# DeepSeek 配置读取（仅环境变量，绝不落盘）
# --------------------------------------------------------------------------- #
def _get_config():
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    return api_key, base_url, model


def _extract_html(text: str) -> str:
    t = (text or "").strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t


def _llm_generate(title: str, content: str, module: str, audience: str, prompt: str) -> str:
    api_key, base_url, model = _get_config()
    if not api_key:
        raise RuntimeError("未配置 DeepSeek API Key")
    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
        max_tokens=4000,
    )
    html = _extract_html(resp.choices[0].message.content)
    if "<html" not in html.lower():
        raise RuntimeError("模型未返回有效 HTML")
    return html


# --------------------------------------------------------------------------- #
# 视图
# --------------------------------------------------------------------------- #
def render() -> None:
    theme.page_header("AI 辅助培训与文档生成器",
                      "输入变更需求，由 DeepSeek 大模型生成结构化 HTML 操作手册 / FAQ")

    api_key, _, model = _get_config()
    if api_key:
        st.caption(f"🤖 已接入 DeepSeek 大模型（模型：`{model}`）")
    else:
        st.caption("⚠️ 未检测到 API Key，将使用离线模板引擎生成")

    left, right = st.columns([1, 1], gap="medium")

    with left:
        st.markdown('<div class="sec-title">① 变更需求</div>', unsafe_allow_html=True)
        title = st.text_input("变更标题", value="开户审批流新增「风控评估」节点")
        content = st.text_area(
            "变更内容 / 需求描述",
            value="在合规审查之后、运营归档之前，新增「风控评估」节点，"
                  "由风控专员对大额账户进行反洗钱与风险评级复核；"
                  "驳回时需强制填写批注理由。",
            height=150,
        )
        module = st.selectbox("目标模块", MODULES)
        audience = st.selectbox("目标受众", AUDIENCES)

    with right:
        st.markdown('<div class="sec-title">② Prompt 模板</div>', unsafe_allow_html=True)
        prompt = _PROMPT_TEMPLATE.format(
            title=title, content=content, module=module, audience=audience
        )
        st.text_area("可编辑的 Prompt 模板", value=prompt, height=260)

    st.write("")
    if st.button("✨ 生成操作手册 / FAQ", type="primary", width="stretch"):
        with st.spinner("正在调用 DeepSeek 大模型生成文档…"):
            try:
                html = _llm_generate(title, content, module, audience, prompt)
                mode = "llm"
                error = ""
            except Exception as e:  # noqa: BLE001
                html = generate(title, content, module, audience)
                mode = "template"
                error = str(e)
        st.session_state.generated_html = html
        st.session_state.generated_title = title
        st.session_state.gen_mode = mode
        st.session_state.gen_error = error

    if "generated_html" in st.session_state:
        html = st.session_state.generated_html
        title = st.session_state.generated_title
        mode = st.session_state.gen_mode if "gen_mode" in st.session_state else "template"

        if mode == "llm":
            st.success("✅ 文档已由 DeepSeek 大模型生成")
        else:
            err = st.session_state.gen_error if "gen_error" in st.session_state else ""
            st.warning(f"⚠️ 大模型调用失败，已回退到离线模板引擎（{err}）")

        st.markdown('<div class="sec-title">③ 文档预览</div>', unsafe_allow_html=True)
        st.components.v1.html(html, height=760, scrolling=True)

        with st.expander("查看 HTML 源码", expanded=False):
            st.code(html, language="html")
        st.download_button(
            "⬇️ 下载 HTML 文档", html.encode("utf-8"),
            file_name=f"{title or 'CRM操作手册'}.html", mime="text/html",
            key="dl_doc",
        )


# --------------------------------------------------------------------------- #
# 离线模板引擎（回退方案）
# --------------------------------------------------------------------------- #
_STEPS = {
    "开户申请流程": [
        "登录 CRM 工作台，进入「开户申请」模块并点击「新建申请」",
        "选择机构客户，填写开户类型、账户用途、预计资金规模",
        "上传营业执照、法定代表人身份证明等尽调材料",
        "提交后系统自动流转至「主管初审」，并推送待办提醒",
        "在「审批中心」跟踪各级节点进度与审批批注",
    ],
    "客户信息管理": [
        "进入「客户列表」，通过名称或统一社会信用代码检索目标客户",
        "点击「编辑」维护联系人、联系电话、注册资本等字段",
        "保存后系统自动校验统一社会信用代码格式与重复录入",
        "在「公海管理」中可领取或退回客户，保持归属清晰",
    ],
    "审批流调整": [
        "进入「审批流配置」，选择需要调整的开户审批模板",
        "增删审批节点或调整节点顺序、处理人",
        "配置驳回策略与强制批注规则",
        "保存并发布新版本，历史流程自动留痕",
    ],
    "数据清洗与迁移": [
        "在「数据清洗」页面上传历史 Excel/CSV 文件",
        "系统自动校验代码位数、缺失联系人、重复录入等异常",
        "在异常明细中复核标红记录，确认清洗规则",
        "点击「一键清洗并导出」，下载清洗后的规范数据",
    ],
}

_FAQ = {
    "开户申请流程": [
        ("提交后多久会流转到主管初审？", "提交后系统即时流转，主管端会收到待办提醒。"),
        ("材料不齐可以补交吗？", "可以，在对应节点点击「驳回重提」并批注原因，发起人补齐后重新提交。"),
    ],
    "客户信息管理": [
        ("统一社会信用代码校验规则是什么？", "18 位，由数字与大写字母组成（不含 I、O、Z、S、V）。"),
        ("客户被误退回公海怎么办？", "进入「公海客户」找到该客户，点击「领取」即可重新归属。"),
    ],
    "审批流调整": [
        ("调整审批流会影响进行中的申请吗？", "不影响，已发起的申请沿用旧版本流程，新申请走新版本。"),
        ("可以设置驳回必须填写理由吗？", "可以，开启「强制批注」后驳回必须填写理由。"),
    ],
    "数据清洗与迁移": [
        ("重复录入如何处理？", "系统按统一社会信用代码去重，保留首次录入记录。"),
        ("缺失联系人会怎样处理？", "清洗时自动补全为「待补充」，供业务人员后续维护。"),
    ],
}


def generate(title: str, content: str, module: str, audience: str) -> str:
    """离线规则模板引擎：生成 HTML 操作手册（大模型不可用时的回退方案）。"""
    steps = _STEPS.get(module, _STEPS["开户申请流程"])
    faqs = _FAQ.get(module, _FAQ["开户申请流程"])

    steps_html = "".join(f'<li>{escape(s)}</li>' for s in steps)
    faq_html = "".join(
        '<details><summary>{q}</summary><p>{a}</p></details>'.format(q=escape(q), a=escape(a))
        for q, a in faqs
    )
    content_html = escape(content).replace("\n", "<br>")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{escape(title)}</title>
<style>
  *{{box-sizing:border-box;}}
  body{{margin:0; padding:0; background:#f4f7fb; color:#16223b;
        font-family:system-ui,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
        line-height:1.7;}}
  .wrap{{max-width:820px; margin:0 auto; padding:32px 24px 64px;}}
  header{{background:linear-gradient(135deg,#0a2540,#1e4e8c); color:#fff;
          border-radius:16px; padding:28px 32px; margin-bottom:24px;}}
  header h1{{margin:0 0 8px; font-size:1.6rem;}}
  header .meta{{font-size:.82rem; opacity:.85;}}
  .badge{{display:inline-block; background:#2a78d6; color:#fff; padding:3px 12px;
          border-radius:999px; font-size:.78rem; font-weight:600; margin-bottom:12px;}}
  section{{background:#fff; border:1px solid #e2e8f0; border-radius:14px;
           padding:24px 28px; margin-bottom:20px;}}
  h2{{color:#1e4e8c; font-size:1.15rem; margin:0 0 14px;
      border-left:4px solid #2a78d6; padding-left:12px;}}
  ol{{margin:0; padding-left:22px;}}
  li{{margin-bottom:8px;}}
  details{{border:1px solid #e2e8f0; border-radius:10px; padding:12px 16px; margin-bottom:10px;}}
  summary{{font-weight:600; cursor:pointer; color:#1e4e8c;}}
  details p{{margin:8px 0 0; color:#5b6b85;}}
  .note{{background:#fff8e6; border-left:4px solid #eda100; padding:12px 16px;
         border-radius:8px; font-size:.9rem;}}
  footer{{text-align:center; color:#8a99b3; font-size:.8rem; margin-top:24px;}}
  code{{background:#eef2f7; padding:2px 6px; border-radius:4px; color:#1e4e8c;}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <span class="badge">🤖 AI 生成 · 操作手册</span>
    <h1>{escape(title)}</h1>
    <div class="meta">目标模块：{escape(module)} ｜ 目标受众：{escape(audience)} ｜ 生成时间：{escape(now)}</div>
  </header>

  <section>
    <h2>变更概述</h2>
    <p>{content_html}</p>
  </section>

  <section>
    <h2>操作步骤</h2>
    <ol>{steps_html}</ol>
  </section>

  <section>
    <h2>常见问题 FAQ</h2>
    {faq_html}
  </section>

  <section>
    <h2>注意事项</h2>
    <div class="note">请在正式操作前于测试环境验证流程；涉及审批节点、权限与数据字段的变更，
    需同步知会合规与风控部门，并在系统内完成留痕后方可生效。</div>
  </section>

  <footer>本手册由金融机构 AI 赋能型 CRM 系统自动生成 · 仅供参考，以最新制度为准</footer>
</div>
</body>
</html>"""
