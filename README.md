# 🏦 金融机构 AI 赋能型 CRM 系统（Demo）

基于 **Python + Streamlit** 构建的金融机构客户关系管理演示系统，覆盖线索运营、机构客户与公海管理、开户线上审批、历史数据清洗迁移，以及 AI 辅助培训文档生成五大场景。页面采用**专业金融蓝主题**，数据均为内置模拟数据，开箱即用。

## ✨ 功能模块

| 模块 | 说明 |
|---|---|
| 📊 核心数据监控仪表盘 | 5 项核心指标卡片（线索转化率 +18%、跟进活跃度 +20%、开户完成率、成单周期 -20%、人工核对耗时 6h→1.5h）；按销售团队拆解的线索转化漏斗图、周跟进活跃度折线图、各团队开户完成率 |
| 👥 机构客户与公海管理 | 「我的客户 / 公海客户」Tab 切换；客户名称 / 统一社会信用代码高频搜索 + 多维筛选；固定列（客户名称、操作）+ 状态标签；客户详情、公海领取 / 退回 |
| 📝 开户线上审批流 | 4 级状态机（发起申请 → 主管初审 → 合规审查 → 风控评估 → 运营归档）可视化进度条；同意 / 驳回重提（含理由批注）；底部审批日志留痕 |
| 🧹 历史数据清洗与迁移 | 上传 Excel/CSV 自动校验，标红高亮 300+ 条异常（代码位数错误、缺失联系人、重复录入）；一键清洗并导出，展示迁移成功率 98% |
| 🤖 AI 辅助培训与文档生成 | 内置 Prompt 模板输入框；输入变更需求后由 **DeepSeek 大模型**一键生成结构化 HTML 操作手册 / FAQ，支持在线预览、源码查看与下载（未配置 Key 时自动回退离线模板引擎） |

## 🚀 快速开始

```bash
# 1. 创建并激活虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
streamlit run app.py
```

启动后浏览器会自动打开 `http://localhost:8501`。

## 📁 目录结构

```
crm-demo-project/
├── app.py                     # 应用入口（侧边栏导航 + 路由）
├── requirements.txt           # 依赖清单
├── README.md
├── .streamlit/
│   └── config.toml            # 金融蓝主题基础配置
└── src/
    ├── theme.py               # 配色、全局 CSS、图表样式、通用组件
    ├── data.py                # 模拟数据生成 + session_state 初始化
    └── views/
        ├── dashboard.py       # 仪表盘
        ├── customers.py       # 客户与公海管理
        ├── approval.py        # 开户审批流
        ├── cleaning.py        # 数据清洗与迁移
        └── ai_trainer.py      # AI 培训文档生成
```

## 🛠 技术栈

- **Streamlit** — 界面框架与交互
- **Plotly** — 漏斗图 / 折线图 / 条形图
- **Pandas + NumPy** — 数据生成、校验与清洗
- **openpyxl** — Excel 读取

图表配色遵循数据可视化规范（经过 CVD 色盲安全与对比度校验的参考调色板），
金融蓝主题以 blue（`#2a78d6`）为分类首色，状态色（成功/警告/严重/危险）独立保留语义。

## 📝 说明

- **数据为模拟数据**：所有客户、审批单、历史数据均由内置随机种子生成，仅用于功能演示。
- **AI 文档生成**：默认调用 **DeepSeek 大模型**（OpenAI 兼容接口）生成 HTML 手册；
  未配置 API Key 或调用失败时自动回退到「规则模板引擎」，保证离线可用。

### 🔑 DeepSeek 配置（仅环境变量，绝不落盘）

本项目**只通过环境变量**读取 API 密钥，不生成、不读取任何本地配置文件
（无 `secrets.toml`），确保密钥绝不写入磁盘：

```bash
export DEEPSEEK_API_KEY="sk-xxx"                       # 必填
export DEEPSEEK_BASE_URL="https://api.deepseek.com"    # 可选，默认该值
export DEEPSEEK_MODEL="deepseek-chat"                  # 可选，默认该值
streamlit run app.py
```

`DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL` 有默认值，仅 `DEEPSEEK_API_KEY` 必填；
未设置时 AI 文档模块会自动回退到离线模板引擎。

> ⚠️ 请妥善保管 API Key，切勿提交到代码仓库；若已在聊天或日志中泄露，建议尽快在
> DeepSeek 控制台轮换（重新生成）密钥。
- **主题定制**：颜色与样式集中在 `src/theme.py` 与 `.streamlit/config.toml`，可一键换肤。

## 🔧 常见问题

- **端口被占用**：`streamlit run app.py --server.port 8502`
- **无痕预览**：`streamlit run app.py --server.headless true`
- **Excel 上传报错**：确认已安装 `openpyxl`（已包含在 requirements 中）
