#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 服务列表
SERVICES=(
  "api_gateway:8080"
  "data_simulator:8000"
  "cashflow_predictor:8002"
  "cost_analyzer:8001"
  "compliance_checker:8003"
  "mongodb:27017"
  "redis:6379"
  "prometheus:9090"
  "grafana:3000"
)

# 检查Docker容器状态
echo -e "\n${YELLOW}检查Docker容器状态...${NC}"
docker-compose ps

# 检查服务健康状态
echo -e "\n${YELLOW}检查服务健康状态...${NC}"
for SERVICE in "${SERVICES[@]}"; do
  NAME=${SERVICE%%:*}
  PORT=${SERVICE##*:}
  
  # 跳过数据库，因为它们没有健康检查API
  if [[ "$NAME" == "mongodb" || "$NAME" == "redis" ]]; then
    echo -e "${YELLOW}✓ $NAME 容器运行状态: ${NC}$(docker inspect --format='{{.State.Status}}' $NAME)"
    continue
  fi
  
  # 检查API服务健康状态
  if [[ "$NAME" == "api_gateway" || "$NAME" == "data_simulator" || "$NAME" == "cashflow_predictor" || "$NAME" == "cost_analyzer" || "$NAME" == "compliance_checker" ]]; then
    HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/health 2>/dev/null)
    
    if [ "$HEALTH_STATUS" == "200" ]; then
      echo -e "${GREEN}✓ $NAME 健康检查通过 ($PORT)${NC}"
    else
      echo -e "${RED}✗ $NAME 健康检查失败 ($PORT): HTTP 状态码 $HEALTH_STATUS${NC}"
    fi
  else
    # 检查其他服务是否可访问
    nc -z localhost $PORT >/dev/null 2>&1
    
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}✓ $NAME 可访问 ($PORT)${NC}"
    else
      echo -e "${RED}✗ $NAME 不可访问 ($PORT)${NC}"
    fi
  fi
done

# 检查API网关集成
echo -e "\n${YELLOW}检查API网关集成...${NC}"
GATEWAY_HEALTH=$(curl -s http://localhost:8080/health)

echo -e "API网关健康状态: $GATEWAY_HEALTH"

# 检查日志
echo -e "\n${YELLOW}检查关键服务日志...${NC}"
echo "API网关最近日志:"
docker logs api_gateway --tail 10

echo -e "\n${YELLOW}部署检查完成${NC}"
echo "----------------------------------------------------------------"
echo -e "API网关: ${GREEN}http://localhost:8080${NC}"
echo -e "API文档: ${GREEN}http://localhost:8080/docs${NC}"
echo -e "Prometheus: ${GREEN}http://localhost:9090${NC}"
echo -e "Grafana: ${GREEN}http://localhost:3000${NC} (用户名: admin, 密码: admin)"
echo "----------------------------------------------------------------" 