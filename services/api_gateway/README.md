# API网关服务

## 项目说明
API网关服务提供统一的API访问入口，处理认证、授权、请求路由和响应转换等功能。

## 主要功能
- 统一API入口
- JWT认证
- 访问权限控制
- 请求转发与负载均衡
- 响应格式统一
- 请求日志记录
- 限流与熔断
- 错误处理

## 技术栈
- Python 3.9+
- FastAPI
- Redis (缓存)
- JWT (认证)
- Prometheus (监控)

## 接口服务集成

| 服务名称 | 路径前缀 | 服务说明 |
|---------|---------|---------|
| 数据模拟服务 | /api/v1/simulator | 生成行业模拟数据 |
| 现金流预测服务 | /api/v1/cashflow | 现金流预测分析 |
| 成本穿透分析服务 | /api/v1/cost | 成本结构分析 |
| 合规检查服务 | /api/v1/compliance | 财务合规检查 |
| 集成分析API | /api/v1/integrated | 综合分析接口 |

## 快速开始

### 开发环境
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn src.main:app --reload --port 8000
```

### Docker环境
```bash
# 构建镜像
docker build -t merchant-api-gateway .

# 运行容器
docker run -p 8000:8000 merchant-api-gateway
```

## 配置说明
配置项可通过环境变量或config.yaml文件设置：

```yaml
server:
  port: 8000
  debug: false
  
auth:
  jwt_secret: "your-secret-key"
  token_expire_minutes: 60
  
services:
  simulator_url: "http://data-simulator:8001"
  cashflow_url: "http://cashflow-predictor:8002"
  cost_url: "http://cost-analyzer:8003"
  compliance_url: "http://compliance-checker:8004"
``` 