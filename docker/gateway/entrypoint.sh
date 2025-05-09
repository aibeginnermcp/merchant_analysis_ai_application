#!/bin/bash
set -e

# 等待依赖服务就绪
wait_for_service() {
    local host="$1"
    local port="$2"
    local service="$3"
    
    echo "等待 $service 就绪..."
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    echo "$service 已就绪"
}

# 检查必要的环境变量
check_env_vars() {
    local required_vars=(
        "MONGODB_URI"
        "REDIS_URI"
        "RABBITMQ_URI"
        "CONSUL_HOST"
    )

    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo "错误: 缺少必要的环境变量 $var"
            exit 1
        fi
    done
}

# 主函数
main() {
    check_env_vars

    # 从环境变量中提取主机和端口
    MONGODB_HOST=$(echo "$MONGODB_URI" | awk -F[/:] '{print $4}')
    MONGODB_PORT=$(echo "$MONGODB_URI" | awk -F[/:] '{print $5}')
    
    REDIS_HOST=$(echo "$REDIS_URI" | awk -F[/:] '{print $4}')
    REDIS_PORT=$(echo "$REDIS_URI" | awk -F[/:] '{print $5}')
    
    RABBITMQ_HOST=$(echo "$RABBITMQ_URI" | awk -F[/:] '{print $4}')
    RABBITMQ_PORT=5672

    # 等待所有依赖服务就绪
    wait_for_service "$MONGODB_HOST" "$MONGODB_PORT" "MongoDB"
    wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"
    wait_for_service "$RABBITMQ_HOST" "$RABBITMQ_PORT" "RabbitMQ"
    wait_for_service "$CONSUL_HOST" 8500 "Consul"

    # 执行数据库迁移（如果需要）
    if [ -n "$RUN_MIGRATIONS" ]; then
        echo "运行数据库迁移..."
        python -m src.gateway.db.migrations
    fi

    # 注册服务到Consul
    python -m src.gateway.scripts.register_service

    # 启动应用
    echo "启动API网关服务..."
    exec "$@"
}

# 启动主函数
main "$@" 