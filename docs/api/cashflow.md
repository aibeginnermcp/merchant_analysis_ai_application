# 现金流预测 API

## 获取预测结果

### 请求

```http
POST /api/v1/cashflow/predict
```

#### 请求参数

```json
{
    "merchant_id": "string",
    "time_range": {
        "start": "2024-01-01T00:00:00Z",
        "end": "2024-01-31T23:59:59Z"
    },
    "granularity": "daily",  // daily, weekly, monthly
    "include_details": true  // 是否包含详细数据
}
```

### 响应

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "merchant_id": "string",
        "predictions": {
            "inflow": [
                {
                    "date": "2024-01-01T00:00:00Z",
                    "amount": 10000.00,
                    "confidence": 0.95
                }
            ],
            "outflow": [
                {
                    "date": "2024-01-01T00:00:00Z",
                    "amount": 8000.00,
                    "confidence": 0.95
                }
            ],
            "net_flow": [
                {
                    "date": "2024-01-01T00:00:00Z",
                    "amount": 2000.00,
                    "confidence": 0.95
                }
            ]
        },
        "risk_assessment": {
            "risk_level": "LOW",
            "risk_factors": [
                {
                    "factor": "seasonal_impact",
                    "severity": "LOW",
                    "description": "季节性影响较小"
                }
            ]
        },
        "recommendations": [
            {
                "type": "CASH_MANAGEMENT",
                "priority": "HIGH",
                "description": "建议在1月15日前储备15000元现金以应对可能的资金缺口",
                "impact": {
                    "probability": 0.85,
                    "benefit": "避免资金链断裂风险"
                }
            }
        ]
    },
    "request_id": "uuid"
}
```

## 获取历史准确率

### 请求

```http
GET /api/v1/cashflow/accuracy/{merchant_id}
```

#### 查询参数

- `start_date`: 开始日期（ISO 8601格式）
- `end_date`: 结束日期（ISO 8601格式）
- `granularity`: 时间粒度（daily/weekly/monthly）

### 响应

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "merchant_id": "string",
        "accuracy_metrics": {
            "overall": 0.92,
            "inflow": 0.94,
            "outflow": 0.90
        },
        "error_distribution": {
            "mean": 0.05,
            "std_dev": 0.02,
            "percentiles": {
                "p50": 0.04,
                "p90": 0.08,
                "p95": 0.10
            }
        },
        "trend_analysis": {
            "trend": "IMPROVING",
            "improvement_rate": 0.02
        }
    },
    "request_id": "uuid"
}
```

## 模拟场景分析

### 请求

```http
POST /api/v1/cashflow/simulate
```

#### 请求参数

```json
{
    "merchant_id": "string",
    "base_date": "2024-01-01T00:00:00Z",
    "scenarios": [
        {
            "name": "收入增长",
            "type": "REVENUE_GROWTH",
            "parameters": {
                "growth_rate": 0.1,
                "duration_months": 3
            }
        },
        {
            "name": "成本上升",
            "type": "COST_INCREASE",
            "parameters": {
                "increase_rate": 0.05,
                "affected_categories": ["原材料", "人工"]
            }
        }
    ]
}
```

### 响应

```json
{
    "code": 0,
    "message": "success",
    "data": {
        "merchant_id": "string",
        "scenarios": [
            {
                "name": "收入增长",
                "impact_analysis": {
                    "cash_position": {
                        "before": 100000.00,
                        "after": 110000.00,
                        "change_percentage": 0.10
                    },
                    "risk_metrics": {
                        "liquidity_ratio": {
                            "before": 1.5,
                            "after": 1.65
                        },
                        "cash_burn_rate": {
                            "before": 20000.00,
                            "after": 18000.00
                        }
                    }
                },
                "recommendations": [
                    {
                        "action": "增加营运资金储备",
                        "reason": "应对业务增长需求",
                        "priority": "HIGH"
                    }
                ]
            }
        ]
    },
    "request_id": "uuid"
}
```

## 错误码

| 错误码 | 描述 | 处理建议 |
|--------|------|----------|
| 1001 | 参数验证失败 | 检查请求参数格式 |
| 1002 | 商户不存在 | 确认商户ID是否正确 |
| 1003 | 数据不足 | 确保有足够的历史数据 |
| 1004 | 预测失败 | 重试或联系技术支持 |
| 1005 | 场景参数无效 | 检查场景配置参数 |

## 数据限制

- 最长预测期限：12个月
- 最小时间粒度：日
- 最大请求数据量：单次1000条
- 历史数据要求：至少6个月
- 置信区间范围：60% - 99% 