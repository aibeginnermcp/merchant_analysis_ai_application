#!/bin/bash
# 成本分析服务入口脚本
# 用于初始化环境并启动服务

set -e

# 打印环境信息
echo "================================================"
echo "🚀 成本分析服务启动中..."
echo "📅 $(date)"
echo "🔧 环境: $ENVIRONMENT"
echo "🔌 端口: ${PORT:-8001}"
echo "================================================"

# 检查环境变量
if [ -z "$MONGODB_URI" ]; then
    echo "⚠️ 警告: MONGODB_URI环境变量未设置，将使用默认值"
    export MONGODB_URI="mongodb://mongodb:27017/merchant_analytics"
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
MAX_RETRIES=30
RETRY_INTERVAL=2
RETRY_COUNT=0

# 使用nc命令检查MongoDB连接
if command -v nc >/dev/null 2>&1; then
    while ! nc -z $MONGODB_HOST $MONGODB_PORT >/dev/null 2>&1 && [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        echo "⏳ 等待MongoDB启动... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
        RETRY_COUNT=$((RETRY_COUNT+1))
    done
# 备选方案：使用curl检查
elif command -v curl >/dev/null 2>&1; then
    while ! curl -s http://$MONGODB_HOST:$MONGODB_PORT >/dev/null 2>&1 && [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        echo "⏳ 等待MongoDB启动... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
        RETRY_COUNT=$((RETRY_COUNT+1))
    done
# 无检查工具情况
else
    echo "⚠️ 未安装nc或curl命令，无法检查MongoDB连接，将假定数据库已就绪"
    sleep 5
fi

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ 无法连接到MongoDB，超过最大重试次数"
    echo "🔄 将继续启动服务，但功能可能受限..."
else
    echo "✅ MongoDB连接成功或继续启动"
fi

# 执行数据库迁移或初始化（如果需要）
echo "🔄 正在检查数据模型更新..."
# 此处添加数据库迁移脚本（如果有）

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