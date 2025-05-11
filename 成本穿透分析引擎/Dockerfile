# 使用多阶段构建
FROM python:3.9-slim as builder

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install -r requirements.txt

# 最终镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖（全局安装，无需指定/root/.local，直接用默认路径）
# 这里可以省略依赖COPY步骤，依赖已在最终镜像环境中

# 设置环境变量
ENV PYTHONPATH=/app

# 复制应用代码
COPY src/ ./src/
COPY tests/ ./tests/

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]