# 商户智能经营分析平台 API 参考文档

## 概述

本文档详细说明了商户智能经营分析平台的API接口规范。该平台提供了一系列RESTful API，用于进行商户经营数据的分析和预测。

## 基础信息

- 基础URL: `http://api.merchant-analysis.com/v1`
- 认证方式: JWT Bearer Token
- 响应格式: JSON
- 字符编码: UTF-8

## 认证

所有API请求都需要在HTTP Header中包含有效的JWT Token：

```http
Authorization: Bearer <your_jwt_token>
```

## 错误处理

### 错误响应格式

```json
{
    "code": "错误代码",
    "message": "错误描述",
    "service": "出错服务名称",
    "details": {
        "额外信息": "值"
    }
}
```

### 错误代码说明

| 代码范围 | 类型 | 说明 |
|---------|------|-----|
| 1000-1999 | 通用错误 | 包括未知错误、无效请求等 |
| 2000-2999 | 服务发现错误 | 服务未找到、服务不健康等 |
| 3000-3999 | 数据错误 | 数据未找到、数据冲突等 |
| 4000-4999 | 业务错误 | 分析失败、预测失败等 |

## API 端点

### 1. 商户分析接口

#### 发起分析请求

```http
POST /merchant/analyze
```

**请求参数：**

```json
{
    "merchant_id": "商户ID",
    "merchant_type": "restaurant/retail/ecommerce/service",
    "time_range": {
        "start": "2023-01-01T00:00:00Z",
        "end": "2023-12-31T23:59:59Z"
    },
    "analysis_modules": [
        "CASH_FLOW",
        "COST",
        "COMPLIANCE"
    ],
    "prediction_days": 30
}
```

**响应示例：**

```json
{
    "merchant_id": "M12345",
    "analysis_date": "2024-03-15T10:30:00Z",
    "status": "COMPLETED",
    "results": {
        "CASH_FLOW": {
            "status": "success",
            "data": {
                "predictions": [...],
                "confidence": 0.95
            }
        },
        "COST": {
            "status": "success",
            "data": {
                "cost_breakdown": {...},
                "optimization_suggestions": [...]
            }
        }
    }
}
```

#### 获取分析结果

```http
GET /merchant/analysis/{analysis_id}
```

**响应示例：**

```json
{
    "analysis_id": "A12345",
    "merchant_id": "M12345",
    "status": "COMPLETED",
    "results": {...}
}
```

#### 获取分析历史

```http
GET /merchant/history
```

**查询参数：**

- `merchant_id`: 商户ID（可选）
- `start_date`: 开始日期（可选）
- `end_date`: 结束日期（可选）
- `page`: 页码（默认1）
- `page_size`: 每页大小（默认20）

**响应示例：**

```json
{
    "total": 100,
    "page": 1,
    "page_size": 20,
    "results": [...]
}
```

## 数据模型

### 商户信息

```json
{
    "merchant_id": "商户ID",
    "name": "商户名称",
    "industry": "行业类型",
    "size": "规模大小",
    "establishment_date": "成立日期",
    "location": {
        "latitude": 纬度,
        "longitude": 经度
    },
    "business_hours": {
        "weekday": "营业时间",
        "weekend": "营业时间"
    },
    "payment_methods": ["支付方式列表"],
    "rating": 评分
}
```

### 交易数据

```json
{
    "date": "交易日期",
    "revenue": 营业收入,
    "transaction_count": 交易笔数,
    "average_transaction_value": 平均客单价,
    "peak_hours": [高峰时段],
    "payment_distribution": {
        "支付方式": 占比
    },
    "channel_distribution": {
        "渠道": 占比
    },
    "refund_amount": 退款金额
}
```

## 最佳实践

### 1. 错误处理

- 始终检查响应状态码
- 实现指数退避重试机制
- 合理设置请求超时时间

### 2. 性能优化

- 使用适当的页大小进行分页查询
- 合理设置缓存策略
- 避免频繁请求相同数据

### 3. 安全建议

- 定期轮换JWT Token
- 使用HTTPS进行通信
- 实施请求频率限制

## 更新日志

### v1.0.0 (2024-03-15)

- 初始版本发布
- 支持基础分析功能
- 实现完整的错误处理机制 