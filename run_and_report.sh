#!/bin/bash
set -e

# 如需build镜像请取消下行注释
# echo "0. 预构建所有服务镜像..."
# docker-compose -p merchant build

echo "1. 启动数据库和缓存..."
docker-compose -p merchant up -d mongodb redis

echo "2. 等待数据库和缓存健康..."
for i in {1..40}
do
  mongo_ok=$(docker-compose -p merchant exec -T mongodb mongosh --eval "db.runCommand('ping').ok" 2>/dev/null | grep 1 || true)
  redis_ok=$(docker-compose -p merchant exec -T redis redis-cli ping 2>/dev/null | grep PONG || true)
  if [[ "$mongo_ok" != "" && "$redis_ok" != "" ]]; then
    echo "数据库和缓存已就绪。"
    break
  fi
  echo "等待数据库和缓存启动中...($i/40)"
  sleep 3
done

echo "3. 启动核心业务服务..."
docker-compose -p merchant up -d data_simulator cashflow_service cost_service compliance_service api_gateway

echo "4. 等待API网关健康启动..."
for i in {1..30}
do
  if curl -fs http://localhost:8000/health > /dev/null; then
    echo "API网关已就绪。"
    break
  fi
  echo "等待API网关启动中...($i/30)"
  sleep 2
done

# 获取JWT Token（如有自动化认证API，可在此处实现）
# TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login -d '{"username":"test","password":"test"}' | jq -r .token)
TOKEN="YOUR_JWT_TOKEN"

echo "5. 触发全链路分析报告生成..."
curl -X POST http://localhost:8000/api/v1/integrated-analysis \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_type": "restaurant",
    "time_range": {
      "start": "2023-01-01",
      "end": "2023-03-31"
    },
    "analysis_types": ["cashflow", "cost", "compliance"]
  }' | tee report.json

echo "6. 报告已生成，保存在 report.json" 
