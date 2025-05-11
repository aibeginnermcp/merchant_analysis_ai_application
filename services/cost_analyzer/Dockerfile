# 使用多阶段构建 - 构建阶段
FROM python:3.9-slim as builder

# 构建参数 - CI环境变量
ARG CI=false
ARG GITHUB_ACTIONS=false
ARG MONGODB_AVAILABLE=true
ARG DEBUG=false

# 环境变量设置
ENV CI=$CI \
    GITHUB_ACTIONS=$GITHUB_ACTIONS \
    MONGODB_AVAILABLE=$MONGODB_AVAILABLE \
    DEBUG=$DEBUG \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app/build

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 确保requirements.txt格式正确
RUN if grep -q "[^a-zA-Z0-9>=<._\n\r -]" requirements.txt; then \
    echo "清理requirements.txt中的非法字符"; \
    sed -i 's/[^a-zA-Z0-9>=<._\n\r -]//g' requirements.txt; \
    fi

# 安装依赖到全局（去除--user参数）
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 最终镜像阶段
FROM python:3.9-slim

# 构建参数 - CI环境变量（确保在最终镜像中也设置）
ARG CI=false
ARG GITHUB_ACTIONS=false
ARG MONGODB_AVAILABLE=true 
ARG DEBUG=false

# 环境变量设置
ENV CI=$CI \
    GITHUB_ACTIONS=$GITHUB_ACTIONS \
    MONGODB_AVAILABLE=$MONGODB_AVAILABLE \
    DEBUG=$DEBUG \
    PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app \
    PORT=8001 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# 设置工作目录
WORKDIR /app

# 安装运行时必要的依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 复制应用代码
COPY . /app/

# 创建必要的目录
RUN mkdir -p /app/data /app/output /app/logs

# 确保入口脚本有执行权限
RUN chmod +x /app/entrypoint.sh

# 添加简化的健康检查脚本
RUN echo '#!/bin/sh\ncurl -sf http://localhost:8001/health || exit 1' > /app/health-check.sh && \
    chmod +x /app/health-check.sh

# 创建CI模式下的简化入口点
RUN echo '#!/bin/sh\n\necho "CI环境检测:"\necho "CI=${CI:-false}"\necho "GITHUB_ACTIONS=${GITHUB_ACTIONS:-false}"\n\nif [ "$CI" = "true" ] || [ "$GITHUB_ACTIONS" = "true" ]; then\n  echo "在CI环境中运行，使用简化模式"\n  export MONGODB_AVAILABLE=false\n  exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001} --workers 1\nelse\n  echo "在标准环境中运行，使用正常入口脚本"\n  exec /app/entrypoint.sh\nfi' > /app/ci-entrypoint.sh && \
    chmod +x /app/ci-entrypoint.sh

# 暴露端口
EXPOSE 8001

# 健康检查 - 使用更宽松的设置
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD /app/health-check.sh

# 启动命令 - 根据环境选择入口点
CMD ["/app/ci-entrypoint.sh"]