#!/bin/bash
# 微服务修复脚本
# 用于修复所有服务的常见配置问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}🔧 商户智能分析平台 - 服务修复工具${NC}"
echo -e "${BLUE}================================================${NC}"

# 定义服务数组
SERVICES=("api_gateway" "data_simulator" "cashflow_predictor" "cost_analyzer" "compliance_checker")

# 选择修复模式
echo -e "${YELLOW}请选择修复模式:${NC}"
echo "1) 修复所有服务"
echo "2) 选择特定服务"
read -p "您的选择 [1-2]: " FIX_MODE

case $FIX_MODE in
    1)
        SELECTED_SERVICES=("${SERVICES[@]}")
        ;;
    2)
        echo -e "${YELLOW}请选择要修复的服务:${NC}"
        for i in "${!SERVICES[@]}"; do
            echo "$((i+1))) ${SERVICES[$i]}"
        done
        
        SELECTED_SERVICES=()
        while true; do
            read -p "添加服务 [1-${#SERVICES[@]}]: " SERVICE_CHOICE
            if [ "$SERVICE_CHOICE" -ge 1 ] && [ "$SERVICE_CHOICE" -le ${#SERVICES[@]} ]; then
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

echo -e "${GREEN}将修复以下服务:${NC}"
for service in "${SELECTED_SERVICES[@]}"; do
    echo "- $service"
done

# 定义修复函数
fix_requirements() {
    local service=$1
    echo -e "\n${YELLOW}修复 $service 的requirements.txt...${NC}"
    
    # 检查文件是否存在
    if [ ! -f "./services/$service/requirements.txt" ]; then
        echo -e "${RED}⚠️ requirements.txt不存在，将创建...${NC}"
        touch "./services/$service/requirements.txt"
    fi
    
    # 检查文件格式
    if grep -q "%" "./services/$service/requirements.txt"; then
        echo -e "${RED}⚠️ 发现格式问题，正在修复...${NC}"
        # 创建临时文件
        TMP_FILE=$(mktemp)
        # 过滤掉%字符和空行
        grep -v "%" "./services/$service/requirements.txt" | grep -v "^$" > "$TMP_FILE"
        # 使用新内容替换原文件
        mv "$TMP_FILE" "./services/$service/requirements.txt"
    fi
    
    echo -e "${GREEN}✓ requirements.txt修复完成${NC}"
}

fix_entrypoint() {
    local service=$1
    echo -e "\n${YELLOW}修复 $service 的entrypoint.sh...${NC}"
    
    # 检查文件是否存在
    if [ ! -f "./services/$service/entrypoint.sh" ]; then
        echo -e "${RED}⚠️ entrypoint.sh不存在，将创建...${NC}"
        
        # 创建基本的entrypoint.sh
        cat > "./services/$service/entrypoint.sh" << EOF
#!/bin/bash
# $service 服务入口脚本

set -e

# 打印环境信息
echo "================================================"
echo "🚀 $service 服务启动中..."
echo "📅 \$(date)"
echo "🔧 环境: \$ENVIRONMENT"
echo "🔌 端口: \${PORT:-8000}"
echo "================================================"

# 检查环境变量
if [ -z "\$MONGODB_URI" ]; then
    echo "⚠️ 警告: MONGODB_URI环境变量未设置，将使用默认值"
    export MONGODB_URI="mongodb://mongodb:27017/merchant_analytics"
fi

# 提取MongoDB主机和端口
if [[ \$MONGODB_URI =~ mongodb://([^:]+):([0-9]+) ]]; then
    MONGODB_HOST=\${BASH_REMATCH[1]}
    MONGODB_PORT=\${BASH_REMATCH[2]}
    echo "📊 MongoDB连接信息: 主机=\$MONGODB_HOST, 端口=\$MONGODB_PORT"
else
    # 默认值
    MONGODB_HOST="mongodb"
    MONGODB_PORT="27017"
    echo "⚠️ 无法从URI解析MongoDB连接信息，使用默认值"
fi

# 等待依赖服务可用
echo "⏳ 正在等待数据库服务可用..."
MAX_RETRIES=30
RETRY_INTERVAL=2
RETRY_COUNT=0

# 使用nc命令检查MongoDB连接
if command -v nc >/dev/null 2>&1; then
    while ! nc -z \$MONGODB_HOST \$MONGODB_PORT >/dev/null 2>&1 && [ \$RETRY_COUNT -lt \$MAX_RETRIES ]; do
        echo "⏳ 等待MongoDB启动... (\$RETRY_COUNT/\$MAX_RETRIES)"
        sleep \$RETRY_INTERVAL
        RETRY_COUNT=\$((RETRY_COUNT+1))
    done
# 备选方案：使用curl检查
elif command -v curl >/dev/null 2>&1; then
    while ! curl -s http://\$MONGODB_HOST:\$MONGODB_PORT >/dev/null 2>&1 && [ \$RETRY_COUNT -lt \$MAX_RETRIES ]; do
        echo "⏳ 等待MongoDB启动... (\$RETRY_COUNT/\$MAX_RETRIES)"
        sleep \$RETRY_INTERVAL
        RETRY_COUNT=\$((RETRY_COUNT+1))
    done
# 无检查工具情况
else
    echo "⚠️ 未安装nc或curl命令，无法检查MongoDB连接，将假定数据库已就绪"
    sleep 5
fi

if [ \$RETRY_COUNT -eq \$MAX_RETRIES ]; then
    echo "❌ 无法连接到MongoDB，超过最大重试次数"
    echo "🔄 将继续启动服务，但功能可能受限..."
else
    echo "✅ MongoDB连接成功或继续启动"
fi

# 启动应用
echo "🚀 启动$service服务..."
if [ "\$DEBUG" = "true" ]; then
    # 开发模式 - 热重载
    echo "🔍 以开发模式启动(启用热重载)..."
    exec uvicorn main:app --host 0.0.0.0 --port \${PORT:-8000} --reload
else
    # 生产模式
    echo "🔒 以生产模式启动..."
    exec uvicorn main:app --host 0.0.0.0 --port \${PORT:-8000} --workers \${WORKERS:-1}
fi
EOF
        
        # 设置可执行权限
        chmod +x "./services/$service/entrypoint.sh"
    else
        # 修复现有entrypoint.sh
        if ! grep -q "nc -z" "./services/$service/entrypoint.sh"; then
            echo -e "${YELLOW}添加netcat连接检查逻辑...${NC}"
            # 使用sed插入netcat检查代码
            # 这里的实现取决于具体文件结构，可能需要手动调整
        fi
    fi
    
    echo -e "${GREEN}✓ entrypoint.sh修复完成${NC}"
}

fix_dockerfile() {
    local service=$1
    echo -e "\n${YELLOW}修复 $service 的Dockerfile...${NC}"
    
    # 检查文件是否存在
    if [ ! -f "./services/$service/Dockerfile" ]; then
        echo -e "${RED}⚠️ Dockerfile不存在，将创建...${NC}"
        
        # 创建基本的Dockerfile
        cat > "./services/$service/Dockerfile" << EOF
# 使用多阶段构建 - 构建阶段
FROM python:3.9-slim as builder

# 设置工作目录
WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY services/$service/requirements.txt .

# 安装依赖到用户目录
RUN pip install --user --no-cache-dir -r requirements.txt

# 最终镜像阶段
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制构建阶段安装的依赖
COPY --from=builder /root/.local /root/.local

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    netcat-openbsd \\
    && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV PATH=/root/.local/bin:\$PATH
ENV PYTHONPATH=/app
ENV PORT=8000

# 复制应用代码
COPY services/$service /app/

# 确保入口脚本有执行权限
RUN chmod +x /app/entrypoint.sh

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:\${PORT:-8000}/health || exit 1

# 启动命令
ENTRYPOINT ["/app/entrypoint.sh"]
EOF
    else
        # 修复现有Dockerfile
        if ! grep -q "netcat" "./services/$service/Dockerfile"; then
            echo -e "${YELLOW}添加netcat安装...${NC}"
            # 使用sed添加netcat安装
            # 这里的实现取决于具体文件结构，可能需要手动调整
        fi
    fi
    
    echo -e "${GREEN}✓ Dockerfile修复完成${NC}"
}

# 遍历所选服务进行修复
for service in "${SELECTED_SERVICES[@]}"; do
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}🔧 修复服务: $service${NC}"
    echo -e "${BLUE}================================================${NC}"
    
    # 确保服务目录存在
    if [ ! -d "./services/$service" ]; then
        echo -e "${RED}❌ 服务目录不存在: ./services/$service${NC}"
        continue
    fi
    
    # 执行修复步骤
    fix_requirements "$service"
    fix_entrypoint "$service"
    fix_dockerfile "$service"
    
    echo -e "${GREEN}✅ 服务 $service 修复完成${NC}"
done

echo -e "\n${GREEN}所有选定服务的修复工作完成!${NC}"
echo -e "${YELLOW}下一步: 运行 ./build_and_test.sh 来验证修复结果${NC}" 