# 使用多阶段构建 - 构建阶段
FROM python:3.9-slim as builder

# 设置工作目录
WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装依赖到用户目录
RUN pip install --user --no-cache-dir -r requirements.txt

# 最终镜像阶段
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制构建阶段安装的依赖
COPY --from=builder /root/.local /root/.local

# 设置环境变量
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV COST_ANALYZER_PORT=8001
ENV COST_ANALYZER_HOST=0.0.0.0

# 复制应用代码
COPY src/ ./src/
COPY config/ ./config/

# 创建非root用户并切换
RUN useradd -m costanalyzer && \
    chown -R costanalyzer:costanalyzer /app
USER costanalyzer

# 暴露端口
EXPOSE 8001

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]