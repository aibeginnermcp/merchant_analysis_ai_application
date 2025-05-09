#!/bin/bash
# 成本分析服务 - 本地测试脚本
# 用于验证成本分析服务的构建和运行

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}🔍 成本分析服务 - 本地构建和测试${NC}"
echo -e "${BLUE}================================================${NC}"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ 未安装Docker，请先安装Docker${NC}"
    exit 1
fi

# 是否使用MongoDB
read -p "是否启动MongoDB用于测试? [y/n]: " USE_MONGODB
if [ "$USE_MONGODB" = "y" ] || [ "$USE_MONGODB" = "Y" ]; then
    USE_MONGODB=true
else
    USE_MONGODB=false
fi

# 构建服务
echo -e "\n${BLUE}================================================${NC}"
echo -e "${BLUE}🔨 构建成本分析服务${NC}"
echo -e "${BLUE}================================================${NC}"

# 输出requirements.txt内容进行验证
echo -e "${YELLOW}验证requirements.txt内容:${NC}"
cat services/cost_analyzer/requirements.txt

# 构建镜像
echo -e "${YELLOW}开始构建...${NC}"
if docker build -t "merchant-cost_analyzer:local" -f "./services/cost_analyzer/Dockerfile" .; then
    echo -e "${GREEN}✅ 成本分析服务构建成功${NC}"
    
    # 创建测试网络（如果不存在）
    docker network inspect merchant_test_network >/dev/null 2>&1 || docker network create merchant_test_network
    
    # 启动MongoDB容器（如果需要）
    if [ "$USE_MONGODB" = true ]; then
        if [ "$(docker ps -aq -f name=mongodb_test)" ]; then
            echo -e "${YELLOW}发现已有的MongoDB测试容器，确保它在运行...${NC}"
            docker start mongodb_test 2>/dev/null || true
        else
            echo -e "${YELLOW}启动MongoDB测试容器...${NC}"
            docker run -d --name mongodb_test \
                --network merchant_test_network \
                -p 27018:27017 \
                mongo:5.0
        fi
        MONGODB_URI="mongodb://mongodb_test:27017/merchant_analytics"
        MONGODB_AVAILABLE="true"
        echo -e "${GREEN}✅ MongoDB配置完成${NC}"
    else
        echo -e "${YELLOW}测试将不使用MongoDB...${NC}"
        MONGODB_URI="mongodb://mongodb:27017/merchant_analytics"
        MONGODB_AVAILABLE="false"
    fi
    
    # 运行成本分析服务容器
    echo -e "${YELLOW}启动成本分析服务...${NC}"
    docker run -d --name cost_analyzer_test \
        --network merchant_test_network \
        -p 8001:8001 \
        -e MONGODB_URI="$MONGODB_URI" \
        -e MONGODB_AVAILABLE="$MONGODB_AVAILABLE" \
        -e DEBUG=true \
        merchant-cost_analyzer:local
    
    # 等待服务启动
    echo -e "${YELLOW}等待服务启动...${NC}"
    sleep 8
    
    # 测试健康检查接口
    echo -e "${YELLOW}测试健康检查接口...${NC}"
    if curl -s http://localhost:8001/health | grep -q "status"; then
        echo -e "${GREEN}✅ 服务健康检查通过${NC}"
        # 显示健康检查结果
        curl -s http://localhost:8001/health | jq . || curl -s http://localhost:8001/health
    else
        echo -e "${RED}❌ 服务健康检查失败${NC}"
    fi
    
    # 测试调试接口
    echo -e "${YELLOW}测试调试接口...${NC}"
    if curl -s http://localhost:8001/debug | grep -q "timestamp"; then
        echo -e "${GREEN}✅ 调试接口测试通过${NC}"
        # 显示调试信息
        curl -s http://localhost:8001/debug | jq . || curl -s http://localhost:8001/debug
    else
        echo -e "${RED}❌ 调试接口测试失败${NC}"
    fi
    
    # 测试API接口
    echo -e "${YELLOW}测试API接口...${NC}"
    RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/analyze \
        -H "Content-Type: application/json" \
        -d '{
            "merchant_id": "test123",
            "start_date": "2023-01-01",
            "end_date": "2023-03-31",
            "analysis_depth": "detailed"
        }')
    
    if echo "$RESPONSE" | grep -q "request_id"; then
        echo -e "${GREEN}✅ API接口测试通过${NC}"
        echo -e "${YELLOW}API响应: ${NC}"
        echo "$RESPONSE" | jq . || echo "$RESPONSE"
    else
        echo -e "${RED}❌ API接口测试失败${NC}"
        echo "$RESPONSE"
    fi
    
    # 显示容器日志
    echo -e "${YELLOW}容器日志:${NC}"
    docker logs cost_analyzer_test
    
    # 清理资源
    echo -e "${YELLOW}是否要清理测试容器?${NC}"
    read -p "清理容器? [y/n]: " CLEAN_UP
    
    if [ "$CLEAN_UP" = "y" ] || [ "$CLEAN_UP" = "Y" ]; then
        echo -e "${BLUE}清理测试容器...${NC}"
        docker stop cost_analyzer_test
        docker rm cost_analyzer_test
        
        if [ "$USE_MONGODB" = true ]; then
            docker stop mongodb_test
        fi
        
        echo -e "${GREEN}✅ 测试容器已清理${NC}"
    fi
else
    echo -e "${RED}❌ 成本分析服务构建失败${NC}"
fi

echo -e "\n${GREEN}测试脚本执行完成${NC}" 