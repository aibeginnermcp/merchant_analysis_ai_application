# 构建阶段
FROM python:3.9-slim as builder

WORKDIR /build

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --user --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.9-slim

WORKDIR /app

# 复制Python包
COPY --from=builder /root/.local /root/.local

# 设置环境变量
ENV PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000 50051

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "-m", "services.api_gateway.main"] 