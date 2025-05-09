#!/bin/bash

# 开发环境设置脚本

echo "开始设置开发环境..."

# 创建必要的目录
mkdir -p data/mongodb
mkdir -p data/prometheus
mkdir -p data/grafana

# 安装依赖
echo "安装Python依赖..."
pip install -r services/cashflow_predictor/requirements.txt

# 设置环境变量
export ENVIRONMENT=development
export MONGODB_URI=mongodb://localhost:27017/cashflow
export PROMETHEUS_PUSHGATEWAY=http://localhost:9091
export LOG_LEVEL=DEBUG

# 启动开发环境
echo "启动开发环境..."
docker-compose -f docker-compose.dev.yml up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 运行测试
echo "运行测试..."
pytest tests/

# 检查服务状态
echo "检查服务状态..."
docker-compose -f docker-compose.dev.yml ps

echo "开发环境设置完成！"
echo "访问以下地址查看服务："
echo "- API文档: http://localhost:8001/docs"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3000" 