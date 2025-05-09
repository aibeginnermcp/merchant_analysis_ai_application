# 商户智能分析平台

一个集成了现金流预测、成本穿透分析和合规检查的商户经营智能分析平台。

## 项目结构

```
.
├── call_integrated_api.py  # 集成API调用示例
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

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行示例

```bash
python call_integrated_api.py
```

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

欢迎提交Issue或Pull Request来帮助改进项目。

## 许可协议

本项目采用MIT许可协议。 