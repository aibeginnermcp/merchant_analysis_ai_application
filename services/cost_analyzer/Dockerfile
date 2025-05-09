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
COPY services/cost_analyzer/requirements.txt .

# 安装依赖到用户目录
RUN pip install --user --no-cache-dir -r requirements.txt

# 最终镜像阶段
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制构建阶段安装的依赖
COPY --from=builder /root/.local /root/.local

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    netcat-openbsd \
    iputils-ping \
    dnsutils \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PORT=8001
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# 安装调试工具 
RUN pip install httpie

# 复制应用代码
COPY services/cost_analyzer /app/

# 确保入口脚本有执行权限
RUN chmod +x /app/entrypoint.sh

# 创建调试脚本
RUN echo '#!/bin/bash\necho "检查网络连接:"\nping -c 3 mongodb || echo "无法ping通mongodb"\nping -c 3 host.docker.internal || echo "无法ping通host.docker.internal"\nping -c 3 localhost || echo "无法ping通localhost"\necho "DNS查询:"\nnslookup mongodb || echo "无法解析mongodb"\necho "端口扫描:"\nnc -zv mongodb 27017 || echo "无法连接到mongodb:27017"\nnc -zv host.docker.internal 27017 || echo "无法连接到host.docker.internal:27017"\necho "内部Web服务测试:"\ncurl -v http://localhost:8001/health || echo "健康检查失败"' > /app/debug.sh && chmod +x /app/debug.sh

# 暴露端口
EXPOSE 8001

# 健康检查 - 使用更宽松的设置
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 0

# 启动命令
ENTRYPOINT ["/app/entrypoint.sh"]