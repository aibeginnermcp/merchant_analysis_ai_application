# 已弃用 (Deprecated)

此目录已合并至 `services/compliance_checker`，请使用新目录。

This directory has been merged into `services/compliance_checker`, please use the new directory.

# 商户合规检查服务

## 项目说明
该服务提供商户经营合规性检查功能，包括:
- 财务合规检查
- 经营资质检查
- 风险预警
- 合规报告生成

## 目录结构
```
compliance_service/
├── api/                    # API接口层
│   ├── __init__.py
│   ├── routes.py          # 路由定义
│   └── schemas.py         # 请求/响应模型
├── core/                   # 核心业务逻辑
│   ├── __init__.py
│   ├── models.py          # 数据模型
│   ├── checker.py         # 检查器实现
│   └── rule_engine.py     # 规则引擎
├── utils/                  # 工具函数
│   ├── __init__.py
│   ├── cache.py          # 缓存实现
│   └── logger.py         # 日志工具
├── tests/                 # 测试用例
├── config.py             # 配置文件
├── main.py               # 应用入口
└── README.md             # 项目文档
```

## 技术栈
- Python 3.9+
- FastAPI
- MongoDB
- Redis
- Docker

## 开发环境设置
1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 启动服务:
```bash
uvicorn main:app --reload
```

## API文档
启动服务后访问: http://localhost:8000/docs 