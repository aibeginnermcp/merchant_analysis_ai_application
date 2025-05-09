# 商户智能分析平台 API 文档

## 基础信息

### 服务地址
- **开发环境**：`http://localhost:8080`
- **测试环境**：`https://api-test.merchant-analytics.com`
- **生产环境**：`https://api.merchant-analytics.com`

### API版本
当前版本：`v1`

### 认证方式
所有API请求需要通过JWT令牌进行认证，令牌通过身份认证接口获取。

## 接口列表

### 1. 获取访问令牌

**接口**：`/api/v1/token`

**方法**：`POST`

**说明**：获取用于API认证的JWT令牌

**请求头**：
```
Content-Type: application/x-www-form-urlencoded
```

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**请求示例**：
```bash
curl -X POST "http://localhost:8080/api/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"
```

**响应示例**：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 2. 集成分析

**接口**：`/api/v1/integrated-analysis`

**方法**：`POST`

**说明**：获取商户的综合分析报告，包括现金流预测、成本穿透和合规性检查

**请求头**：
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| merchant_id | string | 是 | 商户ID |
| time_range | object | 是 | 分析时间范围 |
| time_range.start_date | string | 是 | 开始日期（YYYY-MM-DD） |
| time_range.end_date | string | 是 | 结束日期（YYYY-MM-DD） |
| analysis_types | array | 是 | 分析类型数组，可选值：cashflow、cost、compliance |
| parameters | object | 否 | 分析参数 |
| parameters.prediction_days | integer | 否 | 现金流预测天数，默认30天 |
| parameters.confidence_level | float | 否 | 预测置信度，取值0-1，默认0.95 |
| parameters.analysis_depth | string | 否 | 分析深度，可选值：simple、normal、detailed，默认normal |

**请求示例**：
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

**响应参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| request_id | string | 请求ID |
| status | string | 请求状态：success、error |
| error | object | 错误信息（仅当status为error时存在） |
| data | object | 分析结果数据 |
| data.merchant_id | string | 商户ID |
| data.report_id | string | 报告ID |
| data.time_range | object | 分析时间范围 |
| data.summary | object | 商户健康状况摘要 |
| data.cashflow_analysis | object | 现金流分析结果（如请求时包含cashflow） |
| data.cost_analysis | object | 成本分析结果（如请求时包含cost） |
| data.compliance_analysis | object | 合规分析结果（如请求时包含compliance） |
| data.integrated_insights | array | 综合分析洞察 |

**响应示例**：
```json
{
  "request_id": "req_20240509001234",
  "status": "success",
  "data": {
    "merchant_id": "m123456",
    "report_id": "rpt_20240509001234",
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
    "cashflow_analysis": {
      "prediction": [
        {"date": "2023-04-01", "value": 4520.25, "lower_bound": 4125.75, "upper_bound": 4915.50},
        {"date": "2023-04-02", "value": 4615.10, "lower_bound": 4210.30, "upper_bound": 5019.90}
      ],
      "metrics": {
        "mape": 4.5,
        "rmse": 215.3,
        "model_type": "arima",
        "parameters": {"p": 2, "d": 1, "q": 2}
      }
    },
    "cost_analysis": {
      "total_cost": 152635.80,
      "cost_breakdown": [
        {"category": "labor", "amount": 58623.45, "percentage": 38.4},
        {"category": "raw_material", "amount": 42523.75, "percentage": 27.9}
      ]
    },
    "compliance_analysis": {
      "overall_status": "needs_review",
      "type_status": {
        "tax": "compliant",
        "accounting": "needs_review",
        "licensing": "non_compliant",
        "labor": "compliant"
      },
      "risk_score": 42.5
    },
    "integrated_insights": [
      {
        "category": "profitability",
        "trend": "positive",
        "insight": "收入增长率(8.5%)超过成本增长率(4.2%),利润率改善",
        "recommendation": "继续当前的成本控制措施,同时进一步扩大高利润率产品线"
      }
    ]
  }
}
```

### 3. 现金流预测

**接口**：`/api/v1/cashflow/predict`

**方法**：`POST`

**说明**：获取商户的现金流预测分析

**请求头**：
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| merchant_id | string | 是 | 商户ID |
| time_range | object | 是 | 分析时间范围 |
| time_range.start_date | string | 是 | 开始日期（YYYY-MM-DD） |
| time_range.end_date | string | 是 | 结束日期（YYYY-MM-DD） |
| prediction_days | integer | 否 | 预测天数，默认30天 |
| confidence_level | float | 否 | 预测置信度，取值0-1，默认0.95 |
| model_type | string | 否 | 预测模型类型，可选值：arima、prophet、lstm，默认根据数据特性自动选择 |

**响应参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| request_id | string | 请求ID |
| status | string | 请求状态：success、error |
| data | object | 分析结果数据 |
| data.merchant_id | string | 商户ID |
| data.prediction | array | 预测数据点数组 |
| data.metrics | object | 模型评估指标 |

### 4. 成本穿透分析

**接口**：`/api/v1/cost/analyze`

**方法**：`POST`

**说明**：获取商户的成本结构分析

**请求头**：
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| merchant_id | string | 是 | 商户ID |
| time_range | object | 是 | 分析时间范围 |
| time_range.start_date | string | 是 | 开始日期（YYYY-MM-DD） |
| time_range.end_date | string | 是 | 结束日期（YYYY-MM-DD） |
| granularity | string | 否 | 分析粒度，可选值：daily、weekly、monthly，默认monthly |
| include_benchmarks | boolean | 否 | 是否包含行业基准比较，默认false |
| categories | array | 否 | 需分析的成本类别数组，默认分析所有类别 |

**响应参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| request_id | string | 请求ID |
| status | string | 请求状态：success、error |
| data | object | 分析结果数据 |
| data.merchant_id | string | 商户ID |
| data.total_cost | number | 总成本金额 |
| data.cost_breakdown | array | 成本明细数组 |
| data.trends | object | 成本变化趋势 |
| data.benchmarks | object | 行业基准比较（如请求包含） |

### 5. 合规检查

**接口**：`/api/v1/compliance/check`

**方法**：`POST`

**说明**：获取商户的财务合规检查结果

**请求头**：
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| merchant_id | string | 是 | 商户ID |
| time_range | object | 是 | 分析时间范围 |
| time_range.start_date | string | 是 | 开始日期（YYYY-MM-DD） |
| time_range.end_date | string | 是 | 结束日期（YYYY-MM-DD） |
| check_types | array | 否 | 需检查的合规类型数组，默认检查所有类型 |
| detail_level | string | 否 | 结果详细程度，可选值：summary、detailed，默认summary |

**响应参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| request_id | string | 请求ID |
| status | string | 请求状态：success、error |
| data | object | 分析结果数据 |
| data.merchant_id | string | 商户ID |
| data.overall_status | string | 总体合规状态 |
| data.type_status | object | 各类型合规状态 |
| data.risk_score | number | 风险评分 |
| data.issues | array | 发现的合规问题列表 |
| data.recommendations | array | 改进建议 |

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（无效令牌） |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁（限流） |
| 500 | 服务器内部错误 |

## 限流策略

API采用令牌桶限流算法，默认限制如下：

- 基础级别用户：10次请求/分钟
- 专业级别用户：30次请求/分钟
- 企业级别用户：100次请求/分钟

超出限制将返回429状态码。

## 错误响应格式

当发生错误时，响应格式如下：

```json
{
  "request_id": "req_20240509001234",
  "status": "error",
  "error": {
    "code": "invalid_parameter",
    "message": "无效的商户ID格式",
    "details": [
      {
        "field": "merchant_id",
        "issue": "格式不符合要求"
      }
    ]
  }
}
```

## SDK支持

商户智能分析平台提供以下编程语言的SDK支持：

- Python: [merchant-analytics-python](https://github.com/merchant-analytics/python-sdk)
- JavaScript/Node.js: [merchant-analytics-js](https://github.com/merchant-analytics/js-sdk)
- Java: [merchant-analytics-java](https://github.com/merchant-analytics/java-sdk)

## 客户支持

如有API相关问题，请联系：

- 电子邮件：api-support@merchant-analytics.com
- 技术支持热线：400-123-4567 