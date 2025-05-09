#!/bin/bash
# 成本分析服务入口脚本
# 用于初始化环境并启动服务

# 在Docker中，确保错误时输出有用信息但不立即退出
set +e

# 打印环境信息
echo "================================================"
echo "🚀 成本分析服务启动中..."
echo "📅 $(date)"
echo "🔧 环境: $ENVIRONMENT"
echo "🔌 端口: ${PORT:-8001}"
echo "================================================"

# 检查环境变量和默认值设置
if [ -z "$MONGODB_URI" ]; then
    echo "⚠️ 警告: MONGODB_URI环境变量未设置，将使用默认值"
    # 尝试多种可能的MongoDB连接方式
    export MONGODB_URI="mongodb://mongodb:27017/merchant_analytics"
    echo "备用连接: mongodb://host.docker.internal:27017/merchant_analytics"
    echo "备用连接: mongodb://localhost:27017/merchant_analytics"
    echo "备用连接: mongodb://127.0.0.1:27017/merchant_analytics"
fi

# 提取MongoDB主机和端口
if [[ $MONGODB_URI =~ mongodb://([^:]+):([0-9]+) ]]; then
    MONGODB_HOST=${BASH_REMATCH[1]}
    MONGODB_PORT=${BASH_REMATCH[2]}
    echo "📊 MongoDB连接信息: 主机=$MONGODB_HOST, 端口=$MONGODB_PORT"
else
    # 默认值
    MONGODB_HOST="mongodb"
    MONGODB_PORT="27017"
    echo "⚠️ 无法从URI解析MongoDB连接信息，使用默认值"
fi

# 等待依赖服务可用
echo "⏳ 正在等待数据库服务可用..."
MAX_RETRIES=10
RETRY_INTERVAL=3
RETRY_COUNT=0

# 尝试多种方式检查MongoDB连接
check_mongodb() {
    # 使用nc命令检查MongoDB连接
    if command -v nc >/dev/null 2>&1; then
        if nc -z $MONGODB_HOST $MONGODB_PORT >/dev/null 2>&1; then
            return 0
        fi
    fi
    
    # 备选方案：尝试多个主机名
    for host in "mongodb" "localhost" "host.docker.internal" "127.0.0.1"; do
        if command -v nc >/dev/null 2>&1 && nc -z $host $MONGODB_PORT >/dev/null 2>&1; then
            echo "✅ 可以连接到 $host:$MONGODB_PORT"
            export MONGODB_URI="mongodb://$host:27017/merchant_analytics"
            MONGODB_HOST=$host
            return 0
        fi
    done
    
    return 1
}

while ! check_mongodb && [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "⏳ 尝试连接到MongoDB... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep $RETRY_INTERVAL
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "⚠️ 无法连接到MongoDB，超过最大重试次数"
    echo "🔄 将继续启动服务，但功能可能受限..."
    # 设置环境变量，使应用知道MongoDB不可用
    export MONGODB_AVAILABLE="false"
else
    echo "✅ MongoDB连接成功: $MONGODB_URI"
    export MONGODB_AVAILABLE="true"
fi

# 运行服务的函数
run_service() {
    # 启动应用
    echo "🚀 启动成本分析服务..."
    if [ "$DEBUG" = "true" ]; then
        # 开发模式 - 热重载
        echo "🔍 以开发模式启动(启用热重载)..."
        exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001} --reload
    else
        # 生产模式
        echo "🔒 以生产模式启动..."
        exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001} --workers ${WORKERS:-1}
    fi
}

# 启动服务并添加错误处理
run_service || {
    EXIT_CODE=$?
    echo "❌ 服务启动失败，退出码: $EXIT_CODE"
    echo "请检查日志获取更多信息"
    exit $EXIT_CODE
} 