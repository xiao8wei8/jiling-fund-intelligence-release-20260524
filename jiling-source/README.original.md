# 海富通基金营销平台

## 项目简介

海富通基金营销平台是一个专为基金销售和营销人员设计的智能素材生成系统，集成了基金数据获取、AI文案生成、素材管理等功能。

### 核心功能
- 基金数据实时获取与分析
- AI智能文案生成（多种格式和风格）
- 营销素材管理与库
- 团队协作与绩效追踪
- 数据可视化看板

## 技术栈

- **后端**: Python 3.12+, Flask, SQLAlchemy
- **前端**: HTML5, CSS3, Chart.js
- **数据库**: SQLite (可扩展为PostgreSQL/MySQL)
- **外部API**: 东方财富, MiniMax AI

## 快速启动

### 本地开发环境

1. **安装依赖**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑.env文件，填写相关配置
   ```

3. **启动服务**
   ```bash
   source venv/bin/activate
   python app.py
   ```

4. **访问服务**
   - 前端: http://localhost:5002
   - API: http://localhost:5002/api/health

### 服务器部署

详细部署步骤请参考 [部署文档](.trae/documents/fund_marketing_platform_deployment.md)

## 目录结构

```
fund-marketing-platform/
├── backend/             # 后端代码
│   ├── data/           # 数据库和数据文件
│   ├── routes/         # API路由模块
│   ├── services/       # 外部服务集成
│   ├── app.py          # 主应用入口
│   ├── models.py       # 数据库模型
│   ├── config.py       # 系统配置
│   └── requirements.txt # 依赖包
├── frontend/           # 前端代码
│   └── index.html      # 前端单页面应用
├── .env.example        # 环境变量模板
├── maintenance.sh      # 维护脚本
├── manage.sh           # 服务管理脚本
└── README.md           # 项目说明
```

## API 接口

### 基金相关
- `GET /api/fund/list` - 获取基金列表
- `GET /api/fund/search` - 搜索基金
- `GET /api/fund/<code>` - 获取基金详情
- `GET /api/fund/<code>/detail` - 获取基金详细信息
- `GET /api/fund/<code>/full` - 获取基金完整信息
- `GET /api/fund/<code>/hotspots` - 获取基金热点信息
- `GET /api/fund/<code>/nav` - 获取基金净值历史

### 文案生成
- `POST /api/copy/generate` - 生成营销文案
- `GET /api/copy/formats` - 获取文案格式列表

### 素材库
- `GET /api/library/list` - 获取素材列表
- `POST /api/library/save` - 保存素材

### 团队管理
- `GET /api/team/members` - 获取团队成员
- `POST /api/team/add` - 添加团队成员

### 认证
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出

## 配置说明

### 环境变量
- `SECRET_KEY` - 系统密钥
- `MINIMAX_TOKEN` - MiniMax API密钥（可选）
- `PORT` - 服务端口（默认5002）
- `DEBUG` - 调试模式（默认False）

### 配置文件
- `config.py` - 系统配置管理

## 监控与维护

- **日志位置**: `/var/log/fund-marketing-platform.log`
- **维护脚本**: `maintenance.sh` - 定期清理日志和缓存
- **Supervisor配置**: 确保服务自动启动和重启

## 扩展建议

1. **数据库优化**: 生产环境建议使用PostgreSQL或MySQL
2. **缓存优化**: 集成Redis提高性能
3. **负载均衡**: 配置多个实例使用Nginx负载均衡
4. **HTTPS**: 配置SSL证书提高安全性

## 注意事项

1. **API密钥安全**: 不要将API密钥硬编码在代码中
2. **数据库备份**: 定期备份数据库文件
3. **依赖管理**: 使用虚拟环境隔离依赖
4. **安全配置**: 生产环境禁用DEBUG模式

## 紧急联系人

- **系统管理员**: admin@example.com
- **开发人员**: dev@example.com
- **业务负责人**: business@example.com

---

**© 2026 海富通基金**