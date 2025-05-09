#!/bin/bash
# 成本分析服务入口脚本
# 用于初始化环境并启动服务

# 在Docker中，确保错误时输出有用信息但不立即退出
set +e

# 打印环境信息
echo "================================================"
echo "🚀 成本分析服务启动中..."
echo "📅 $(date)"
echo "🔧 环境: ${ENVIRONMENT:-production}"
echo "🔌 端口: ${PORT:-8001}"
echo "================================================"

# 检测是否在CI环境中运行
if [ "$CI" = "true" ] || [ "$GITHUB_ACTIONS" = "true" ]; then
    echo "🔍 检测到CI环境，将启用自动模式"
    export CI_ENVIRONMENT="true"
    # 在CI环境中，自动设置MongoDB为不可用
    export MONGODB_AVAILABLE="false"
    # 快速启动服务
    echo "✅ CI环境准备完成，将跳过MongoDB检查"
else
    export CI_ENVIRONMENT="false"
    
    # 检查环境变量和默认值设置
    if [ -z "$MONGODB_URI" ]; then
        echo "⚠️ 警告: MONGODB_URI环境变量未设置，将使用默认值"
        # 尝试多种可能的MongoDB连接方式
        export MONGODB_URI="mongodb://mongodb:27017/merchant_analytics"
        echo "备用连接: mongodb://host.docker.internal:27017/merchant_analytics"
        echo "备用连接: mongodb://localhost:27017/merchant_analytics"
        echo "备用连接: mongodb://127.0.0.1:27017/merchant_analytics"
    fi

    # 如果明确设置了MONGODB_AVAILABLE=false，则跳过连接检查
    if [ "${MONGODB_AVAILABLE,,}" = "false" ]; then
        echo "⚠️ MongoDB明确设置为不可用，跳过连接检查"
    else
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
            
            # 尝试使用Python直接连接
            if command -v python3 >/dev/null 2>&1; then
                echo "尝试使用Python连接MongoDB..."
                if python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    s.connect(('$MONGODB_HOST', $MONGODB_PORT))
    s.close()
    print('MongoDB连接成功')
    exit(0)
except Exception as e:
    print(f'连接失败: {e}')
    exit(1)
" >/dev/null 2>&1; then
                    return 0
                fi
            fi
            
            return 1
        }

        # 检查MongoDB连接
        if check_mongodb; then
            echo "✅ MongoDB连接成功: $MONGODB_URI"
            export MONGODB_AVAILABLE="true"
        else
            while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
                echo "⏳ 尝试连接到MongoDB... ($RETRY_COUNT/$MAX_RETRIES)"
                sleep $RETRY_INTERVAL
                RETRY_COUNT=$((RETRY_COUNT+1))
                
                if check_mongodb; then
                    echo "✅ MongoDB连接成功: $MONGODB_URI"
                    export MONGODB_AVAILABLE="true"
                    break
                fi
            done
            
            # 超过重试次数仍然连接失败
            if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
                echo "⚠️ 无法连接到MongoDB，超过最大重试次数"
                echo "🔄 将继续启动服务，但功能可能受限..."
                export MONGODB_AVAILABLE="false"
            fi
        fi
    fi
fi

# 诊断信息输出
echo "================================================"
echo "📊 服务诊断信息"
echo "主机名: $(hostname)"
echo "IP地址: $(hostname -I 2>/dev/null || echo '未知')"
echo "MongoDB可用: $MONGODB_AVAILABLE"
echo "MongoDB URI: $MONGODB_URI"
echo "CI环境: $CI_ENVIRONMENT"
echo "调试模式: ${DEBUG:-false}"
echo "================================================"

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
        # 如果是CI环境，使用单worker以减少资源消耗
        if [ "$CI_ENVIRONMENT" = "true" ]; then
            exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001} --workers 1
        else
            exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001} --workers ${WORKERS:-1}
        fi
    fi
}

# 启动服务并添加错误处理
run_service || {
    EXIT_CODE=$?
    echo "❌ 服务启动失败，退出码: $EXIT_CODE"
    echo "请检查日志获取更多信息"
    
    # 在错误时输出更多诊断信息
    echo "===============错误诊断信息================"
    echo "内存使用:"
    free -h 2>/dev/null || echo "无法获取内存信息"
    echo "进程状态:"
    ps aux | grep uvicorn || echo "无法获取进程信息"
    echo "网络连接:"
    netstat -tuln 2>/dev/null || echo "无法获取网络连接信息"
    echo "===========================================" 
    
    exit $EXIT_CODE
} 