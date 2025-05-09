# 构建阶段
FROM python:3.9-slim AS builder

# 设置工作目录
WORKDIR /build

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --user --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.9-slim AS runner

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH" \
    COST_ANALYSIS_PORT=8002

# 从构建阶段复制安装的依赖
COPY --from=builder /root/.local /root/.local

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE ${COST_ANALYSIS_PORT}

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${COST_ANALYSIS_PORT}/health || exit 1

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"] 