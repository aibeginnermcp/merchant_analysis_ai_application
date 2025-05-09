# 商户智能分析平台

一个集成了现金流预测、成本穿透分析和合规检查的商户经营智能分析平台。

## 项目结构

```
.
├── call_integrated_api.py  # 集成API调用示例
├── services/               # 微服务组件
│   ├── api_gateway/        # API网关
│   ├── cashflow_predictor/ # 现金流预测服务
│   ├── cost_analyzer/      # 成本分析服务
│   ├── compliance_checker/ # 合规检查服务
│   └── data_simulator/     # 数据模拟服务
└── README.md               # 项目说明文档
```

## 功能特性

- **现金流预测**：基于历史数据预测未来现金流趋势
- **成本穿透分析**：细分各类成本占比，发现优化空间
- **合规检查**：自动检查商户经营中的合规风险点
- **集成分析API**：统一接口返回全方位经营分析报告

## 快速开始

### 环境要求

- Python 3.8+
- 必要的第三方库 (详见requirements.txt)
- Docker (可选，用于容器化部署)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行示例

```bash
python call_integrated_api.py
```

### Docker 部署

使用 Docker Compose 启动所有服务:

```bash
docker-compose up -d
```

## CI/CD 配置

项目已配置 GitHub Actions 实现自动化测试、构建和部署流程:

- **自动测试**: 每次提交代码时自动运行单元测试
- **代码质量检查**: 使用 flake8、black 和 isort 进行代码风格检查
- **Docker 镜像构建**: 自动构建并推送服务镜像到 Docker Hub
- **自动部署**: 在测试和构建成功后自动部署到生产环境

详细配置说明请查看 [GitHub Actions 配置指南](docs/GITHUB_ACTIONS_SETUP.md)。

## API文档

### 集成分析API

**请求格式:**

```json
{
  "merchant_id": "m123456",
  "time_range": {
    "start_date": "2023-01-01",
    "end_date": "2023-03-31"
  },
  "analysis_types": ["cashflow", "cost", "compliance"],
  "parameters": {
    "prediction_days": 30,
    "confidence_level": 0.95,
    "analysis_depth": "detailed"
  }
}
```

**响应格式:**

```json
{
  "request_id": "req_20230401123456",
  "status": "success",
  "data": {
    "merchant_id": "m123456",
    "report_id": "rpt_20230401123456",
    "time_range": {
      "start_date": "2023-01-01",
      "end_date": "2023-03-31"
    },
    "summary": {
      "health_score": 78.5,
      "revenue_trend": "increasing",
      "cost_efficiency": "moderate",
      "compliance_status": "needs_review",
      "cash_position": "healthy"
    },
    "cashflow_analysis": { ... },
    "cost_analysis": { ... },
    "compliance_analysis": { ... },
    "integrated_insights": [ ... ]
  }
}
```

## 开发计划

- [ ] 添加用户认证服务
- [ ] 开发Web界面
- [ ] 支持更多分析模块
- [ ] 微服务架构改造

## 贡献指南

欢迎提交Issue或Pull Request来帮助改进项目。提交代码前，请确保:

1. 通过所有单元测试
2. 遵循项目的代码风格规范
3. 更新相关文档

## 许可协议

本项目采用MIT许可协议。 