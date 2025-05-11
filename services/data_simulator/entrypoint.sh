#!/bin/bash
# 数据模拟服务入口脚本
# 用于初始化环境并启动服务

set -e

# 打印环境信息
echo "================================================"
echo "🚀 数据模拟服务启动中..."
echo "📅 $(date)"
echo "🔧 环境: $ENVIRONMENT"
echo "🔌 端口: ${PORT:-8000}"
echo "================================================"

# 检查环境变量
if [ -z "$MONGODB_URI" ]; then
    echo "⚠️ 警告: MONGODB_URI环境变量未设置，将使用默认值"
    export MONGODB_URI="mongodb://mongodb:27017/merchant_analytics"
fi

# 等待依赖服务可用
echo "⏳ 正在等待数据库服务可用..."
MAX_RETRIES=30
RETRY_INTERVAL=2
RETRY_COUNT=0

until curl -s $MONGODB_URI > /dev/null || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
    echo "⏳ 等待MongoDB启动... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep $RETRY_INTERVAL
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ 无法连接到MongoDB，超过最大重试次数"
    exit 1
fi

echo "✅ MongoDB连接成功"

# 执行数据库迁移或初始化（如果需要）
echo "🔄 正在检查数据模型更新..."
# 此处添加数据库迁移脚本（如果有）

# 初始化示例数据（如果需要）
if [ "$INIT_DEMO_DATA" = "true" ]; then
    echo "📊 正在初始化示例数据..."
    python -m src.init_demo_data || echo "⚠️ 示例数据初始化失败，但将继续启动服务"
fi

# 启动应用
echo "🚀 启动数据模拟服务..."
if [ "$DEBUG" = "true" ]; then
    # 开发模式 - 热重载
    echo "🔍 以开发模式启动(启用热重载)..."
    exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
else
    # 生产模式
    echo "🔒 以生产模式启动..."
    exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-1}
fi

exec python main.py 