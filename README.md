# 基灵 Fund Intelligence

基灵是一套面向公募基金从业者的 AI 营销工作台，slogan 为“重新定义 AI 时代下的基金营销新范式”。系统围绕公募基金营销前的市场理解、基金透视、素材生成和自选基金池管理展开，帮助投研、渠道、品牌和销售支持团队更快地把基金数据转化为合规、专业、可复用的营销内容。

## 当前交付内容

```
jiling-fund-intelligence-release-20260524/
├── README.md                 # 本说明文档
├── demo.html                 # 可直接打开的静态展示 demo
├── jiling-source.zip          # 干净源码压缩包
└── source/
    ├── backend/              # Flask 后端源码
    ├── frontend/             # 单页前端源码
    └── tests/                # 静态与脚本语法测试
```

交付包已排除虚拟环境、浏览器缓存、运行日志、SQLite 运行库、备份文件、`__pycache__` 等非源码内容。

## 产品功能

- 登录与品牌首页：基灵品牌 Logo、金融科技蓝视觉、机构账号登录、申请试用提示。
- 素材生成工作台：以 AI 生成窗口为中心，左侧放基金上下文，右侧放生成结果、合规检查和历史素材。
- 基金市场：展示公募市场规模、基金数量、管理机构数量、开放式/封闭式/非货币基金规模，并提供趋势图、结构图、基金公司排名和发行数据。
- 我的基金池：支持从搜索结果和基金卡片加入自选，也支持在自选基金池中删除基金，便于建立机构自己的重点基金池。
- 素材库与团队页面：保留素材管理、团队协作等基础工作台能力。
- 认证接口：复用现有 Flask 登录、登出、状态检查接口。

## 产品优点

- 面向基金营销真实流程：不是泛化聊天工具，而是围绕市场洞察、基金透视、营销素材生成来组织界面。
- 专业感与 AI 感统一：整体采用清透金融科技蓝、玻璃态卡片、数据图表和 AI 生成窗口，适合机构演示。
- 数据来源清晰：基金市场数据以中国证券投资基金业协会公开口径为主，并保留接口刷新能力。
- 前后端轻量：前端暂保持单文件 SPA，后端为 Flask，便于快速演示、二次开发和部署。
- 可渐进扩展：后续可接入更完整的基金数据库、合规审核流、机构权限体系和大模型服务。

## 技术架构

- 前端：HTML5、CSS3、原生 JavaScript、Chart.js。
- 后端：Python、Flask、Flask-CORS、Flask-SQLAlchemy。
- 数据库：SQLite，本地开发默认使用；生产可迁移到 PostgreSQL 或 MySQL。
- 数据服务：东方财富 / 天天基金服务封装，中国证券投资基金业协会公开市场数据。
- AI 服务：预留 MiniMax 服务模块，可替换为其他大模型 API。
- 测试：Node.js 静态结构测试、前端内联脚本语法测试、基金市场接口静态测试。

## 本地运行

1. 进入源码目录：

```bash
cd source/backend
```

2. 创建并启用虚拟环境：

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 启动服务：

```bash
python app.py
```

5. 浏览器访问：

```text
http://localhost:5002
```

当前演示账号：

```text
用户名：ai4leader
密码：ai4leader
```

## 测试

在 `source/` 目录下运行：

```bash
node tests/login-page-static.test.cjs
node tests/index-script-syntax.test.cjs
node tests/market-overview-static.test.cjs
```

本次打包前已通过以上三项测试。

## 部署上线建议

### 小型演示环境

- 使用一台云服务器或内网服务器。
- 安装 Python 3.10+。
- 使用 `venv` 安装依赖。
- 用 `gunicorn` 或 `waitress` 托管 Flask 应用。
- Nginx 反向代理到 Flask 服务端口。
- 配置 HTTPS 证书。

示例：

```bash
pip install gunicorn
gunicorn -w 2 -b 127.0.0.1:5002 app:app
```

Windows Server 可用：

```bash
pip install waitress
waitress-serve --host=127.0.0.1 --port=5002 app:app
```

### 生产环境建议

- 将 SQLite 迁移到 PostgreSQL 或 MySQL。
- 将密钥、模型 API token、数据库连接串放入环境变量或密钥管理服务。
- 关闭 Flask debug。
- 将登录账号体系接入机构统一身份认证或企业微信 / SSO。
- 为 `/api/fund/market-overview` 等外部数据接口增加定时刷新与失败告警。
- 为 AI 生成内容增加合规规则库、敏感词检测、人工复核流和操作留痕。
- 前端后续可迁移到 Vue / React / Next.js，以便支持更复杂的权限、路由和组件复用。

## 重要接口

- `POST /api/auth/login`：登录。
- `POST /api/auth/logout`：退出。
- `GET /api/auth/status`：登录状态。
- `GET /api/fund/search`：基金搜索。
- `GET /api/fund/market-overview`：基金市场总览。
- `POST /api/copy/generate`：AI 营销文案生成。
- `GET /api/library/list`：素材库列表。
- `POST /api/library/save`：保存素材。

## 数据说明

基金市场总览当前使用中国证券投资基金业协会公开数据口径。截至本次交付，页面展示的核心规模数据为 2026 年 3 月公募基金市场数据：公募基金规模 37.53 万亿元、基金数量 13,930 只、管理机构 165 家。

## 后续路线

- 完善基金市场实时拉取和缓存刷新。
- 做基金透视页：收益、回撤、同类排名、持仓风格、风险指标。
- 做基金对比页：多基金横向对比和一键生成对比话术。
- 强化 AI 素材生成：朋友圈、路演提纲、客户问答、海报文案、渠道短文案。
- 增加合规审核和版本管理。
- 增加机构基金池、用户权限和团队协同配置。
