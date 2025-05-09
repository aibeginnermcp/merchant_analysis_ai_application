# API 概述

## 简介

商户智能经营分析平台提供了一套完整的RESTful API，用于访问平台的各项功能。本文档详细说明了API的使用方法、认证方式、请求/响应格式等信息。

## 基础信息

- 基础URL: `https://api.merchant-bi.example.com`
- API版本: v1
- 请求格式: JSON
- 响应格式: JSON
- 字符编码: UTF-8

## 通用请求格式

所有API请求都需要包含以下HTTP头：

```http
Authorization: Bearer <access_token>
Content-Type: application/json
Accept: application/json
X-Request-ID: <uuid>
```

## 通用响应格式

所有API响应都遵循以下格式：

```json
{
    "code": 0,           // 响应码，0表示成功
    "message": "success", // 响应消息
    "data": {},          // 响应数据
    "request_id": "uuid" // 请求ID，用于追踪
}
```

## 分页参数

对于返回列表的接口，支持以下分页参数：

- `page`: 页码，从1开始
- `page_size`: 每页记录数，默认20
- `sort`: 排序字段
- `order`: 排序方向（asc/desc）

示例请求：
```http
GET /api/v1/merchants?page=1&page_size=20&sort=created_at&order=desc
```

分页响应格式：
```json
{
    "code": 0,
    "message": "success",
    "data": {
        "items": [],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
    },
    "request_id": "uuid"
}
```

## 时间格式

所有时间字段都使用ISO 8601格式，并统一使用UTC时区：

```
YYYY-MM-DDThh:mm:ssZ
```

示例：
```
2024-01-01T00:00:00Z
```

## 错误处理

当API调用出错时，会返回对应的错误码和错误信息：

```json
{
    "code": 1001,
    "message": "参数验证失败",
    "data": {
        "field": "merchant_id",
        "reason": "不能为空"
    },
    "request_id": "uuid"
}
```

详细的错误码列表请参考[错误码文档](error-codes.md)。

## 限流说明

API接口采用令牌桶算法进行限流保护：

- 普通用户：100次/分钟
- 高级用户：1000次/分钟

超出限制时返回429状态码：

```json
{
    "code": 9429,
    "message": "请求过于频繁，请稍后重试",
    "data": {
        "retry_after": 60
    },
    "request_id": "uuid"
}
```

## API版本控制

- API版本通过URL路径指定：`/api/v1/`
- 当前稳定版本：v1
- 历史版本兼容性维护期：12个月
- 版本更新通知：提前30天发出邮件通知

## 开发者支持

- 开发者社区：[https://developer.merchant-bi.example.com](https://developer.merchant-bi.example.com)
- API控制台：[https://console.merchant-bi.example.com](https://console.merchant-bi.example.com)
- 技术支持：[support@merchant-bi.example.com](mailto:support@merchant-bi.example.com) 