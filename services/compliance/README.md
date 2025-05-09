# 已弃用 (Deprecated)

此目录已合并至 `services/compliance_checker`，请使用新目录。

This directory has been merged into `services/compliance_checker`, please use the new directory.

# 合规检查服务 API 文档

## 服务概述
合规检查服务提供商户经营合规性检查、预警和建议生成功能。

## API 接口

### 1. 执行合规检查
```http
POST /check
Content-Type: application/json

{
    "request_id": "string",
    "merchant_id": "string",
    "start_date": "2024-01-01T00:00:00",
    "end_date": "2024-01-31T23:59:59",
    "analysis_type": "compliance",
    "parameters": {
        "check_types": ["financial", "operational", "safety"]
    }
}
```

响应：
```json
{
    "request_id": "string",
    "status": "success",
    "data": {
        "metrics": {
            "total_checks": 10,
            "passed_checks": 8,
            "violation_count": 2,
            "high_risk_count": 1,
            "compliance_score": 80.0,
            "trend": 5.0
        },
        "violations": [...],
        "alerts": [...],
        "risk_assessment": "中",
        "improvement_suggestions": [...]
    },
    "error": null
}
```

### 2. 获取预警信息
```http
GET /alerts/{merchant_id}
Query Parameters:
- start_date: 开始日期（可选）
- end_date: 结束日期（可选）
- severity: 严重程度（可选）
```

响应：
```json
[
    {
        "alert_id": "string",
        "merchant_id": "string",
        "timestamp": "2024-01-01T10:00:00",
        "severity": "高",
        "title": "string",
        "description": "string",
        "affected_rules": ["rule_id"],
        "required_actions": ["action1", "action2"]
    }
]
```

### 3. 添加合规规则
```http
POST /rules
Content-Type: application/json

{
    "rule_id": "string",
    "category": "string",
    "name": "string",
    "description": "string",
    "severity": "string",
    "check_method": "string",
    "parameters": {}
}
```

响应：
```json
{
    "message": "规则创建成功",
    "rule_id": "string"
}
```

### 4. 健康检查
```http
GET /health
```

响应：
```json
{
    "status": "healthy",
    "database": "connected",
    "cache": "connected",
    "rule_engine": "initialized",
    "task_manager": "running",
    "timestamp": "2024-01-01T10:00:00"
}
```

## 错误处理
所有接口在发生错误时会返回统一格式的错误响应：
```json
{
    "request_id": "string",
    "status": "error",
    "data": null,
    "error": {
        "code": "string",
        "message": "string",
        "details": {}
    }
}
```

## 使用示例
```python
import requests
import json

# 执行合规检查
response = requests.post(
    "http://localhost:8004/check",
    json={
        "request_id": "req_001",
        "merchant_id": "merchant_001",
        "start_date": "2024-01-01T00:00:00",
        "end_date": "2024-01-31T23:59:59",
        "analysis_type": "compliance"
    }
)

# 获取预警信息
alerts = requests.get(
    "http://localhost:8004/alerts/merchant_001",
    params={
        "start_date": "2024-01-01T00:00:00",
        "severity": "高"
    }
) 