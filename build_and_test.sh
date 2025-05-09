#!/bin/bash
# 商户智能分析平台 - 构建和测试脚本
# 用于在本地环境验证所有服务的构建和基本功能

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}🔍 商户智能分析平台 - 本地构建和测试${NC}"
echo -e "${BLUE}================================================${NC}"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ 未安装Docker，请先安装Docker${NC}"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ 未安装Docker Compose，请先安装Docker Compose${NC}"
    exit 1
fi

# 定义服务数组
SERVICES=("api_gateway" "data_simulator" "cashflow_predictor" "cost_analyzer" "compliance_checker")

# 统计
TOTAL_SERVICES=${#SERVICES[@]}
SUCCESSFUL_BUILDS=0
FAILED_BUILDS=0

# 显示构建选项
echo -e "${YELLOW}请选择构建模式:${NC}"
echo "1) 构建所有服务"
echo "2) 选择特定服务"
read -p "您的选择 [1-2]: " BUILD_MODE

case $BUILD_MODE in
    1)
        SELECTED_SERVICES=("${SERVICES[@]}")
        ;;
    2)
        echo -e "${YELLOW}请选择要构建的服务:${NC}"
        for i in "${!SERVICES[@]}"; do
            echo "$((i+1))) ${SERVICES[$i]}"
        done
        echo "$((TOTAL_SERVICES+1))) 返回"
        
        SELECTED_SERVICES=()
        while true; do
            read -p "添加服务 [1-$((TOTAL_SERVICES+1))]: " SERVICE_CHOICE
            if [ "$SERVICE_CHOICE" -eq $((TOTAL_SERVICES+1)) ]; then
                break
            elif [ "$SERVICE_CHOICE" -ge 1 ] && [ "$SERVICE_CHOICE" -le $TOTAL_SERVICES ]; then
                SELECTED_SERVICES+=("${SERVICES[$((SERVICE_CHOICE-1))]}")
                echo -e "${GREEN}已添加: ${SERVICES[$((SERVICE_CHOICE-1))]}${NC}"
            else
                echo -e "${RED}无效选择${NC}"
            fi
            
            if [ ${#SELECTED_SERVICES[@]} -gt 0 ]; then
                read -p "继续添加服务? [y/n]: " CONTINUE
                if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
                    break
                fi
            fi
        done
        ;;
    *)
        echo -e "${RED}无效选择，退出${NC}"
        exit 1
        ;;
esac

# 如果没有选择服务，退出
if [ ${#SELECTED_SERVICES[@]} -eq 0 ]; then
    echo -e "${RED}未选择任何服务，退出${NC}"
    exit 1
fi

echo -e "${GREEN}将构建以下服务:${NC}"
for service in "${SELECTED_SERVICES[@]}"; do
    echo "- $service"
done

# 构建选定的服务
for service in "${SELECTED_SERVICES[@]}"; do
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}🔨 构建服务: $service${NC}"
    echo -e "${BLUE}================================================${NC}"
    
    # 检查Dockerfile是否存在
    if [ ! -f "./services/$service/Dockerfile" ]; then
        echo -e "${RED}❌ 服务 $service 的Dockerfile不存在${NC}"
        FAILED_BUILDS=$((FAILED_BUILDS+1))
        continue
    fi
    
    # 构建服务
    echo -e "${YELLOW}开始构建...${NC}"
    if docker build -t "merchant-$service:local" -f "./services/$service/Dockerfile" .; then
        echo -e "${GREEN}✅ 服务 $service 构建成功${NC}"
        SUCCESSFUL_BUILDS=$((SUCCESSFUL_BUILDS+1))
    else
        echo -e "${RED}❌ 服务 $service 构建失败${NC}"
        FAILED_BUILDS=$((FAILED_BUILDS+1))
    fi
done

# 显示构建统计
echo -e "\n${BLUE}================================================${NC}"
echo -e "${BLUE}📊 构建统计${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "总服务数: ${TOTAL_SERVICES}"
echo -e "选择构建: ${#SELECTED_SERVICES[@]}"
echo -e "${GREEN}成功构建: ${SUCCESSFUL_BUILDS}${NC}"
echo -e "${RED}失败构建: ${FAILED_BUILDS}${NC}"

# 询问是否要启动服务
if [ $SUCCESSFUL_BUILDS -gt 0 ]; then
    echo -e "\n${YELLOW}是否要使用Docker Compose启动服务?${NC}"
    read -p "启动服务? [y/n]: " START_SERVICES
    
    if [ "$START_SERVICES" = "y" ] || [ "$START_SERVICES" = "Y" ]; then
        echo -e "${BLUE}启动服务...${NC}"
        docker-compose up -d
        
        # 等待服务启动
        echo -e "${YELLOW}等待服务启动...${NC}"
        sleep 5
        
        # 检查服务状态
        docker-compose ps
        
        echo -e "\n${GREEN}✅ 服务已启动${NC}"
        echo -e "API网关地址: http://localhost:8080"
        echo -e "Grafana监控: http://localhost:3000 (用户名: admin, 密码: admin)"
        echo -e "Prometheus: http://localhost:9090"
    else
        echo -e "${BLUE}跳过服务启动${NC}"
    fi
fi

echo -e "\n${GREEN}构建和测试脚本执行完成${NC}" 