# 使用多阶段构建 - 构建阶段
FROM python:3.9-slim AS builder

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir --user -r requirements.txt

# 最终镜像
FROM python:3.9-slim

WORKDIR /app

# 复制已安装的依赖
COPY --from=builder /root/.local /root/.local

# 确保脚本路径在PATH中
ENV PATH=/root/.local/bin:$PATH

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV PORT=8002

# 暴露端口
EXPOSE 8002

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# 启动指令，使用uvicorn启动主要文件
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"] 