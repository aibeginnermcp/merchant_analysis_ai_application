#!/bin/bash

# 创建监控目录
mkdir -p monitoring/prometheus
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards

# 创建Prometheus配置
cat > monitoring/prometheus/prometheus.yml <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'api_gateway'
    static_configs:
      - targets: ['api_gateway:8080']
    metrics_path: /metrics

  - job_name: 'data_simulator'
    static_configs:
      - targets: ['data_simulator:8000']
    metrics_path: /metrics

  - job_name: 'cashflow_predictor'
    static_configs:
      - targets: ['cashflow_predictor:8002']
    metrics_path: /metrics

  - job_name: 'cost_analyzer'
    static_configs:
      - targets: ['cost_analyzer:8001']
    metrics_path: /metrics

  - job_name: 'compliance_checker'
    static_configs:
      - targets: ['compliance_checker:8003']
    metrics_path: /metrics
EOF

# 创建Grafana数据源配置
cat > monitoring/grafana/provisioning/datasources/datasource.yml <<EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# 创建Grafana仪表盘配置
cat > monitoring/grafana/provisioning/dashboards/dashboard.yml <<EOF
apiVersion: 1

providers:
  - name: 'Default'
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /var/lib/grafana/dashboards
EOF

# 启动服务
docker-compose up -d

echo "商户智能分析平台已启动！"
echo "API网关地址: http://localhost:8080"
echo "Prometheus地址: http://localhost:9090"
echo "Grafana地址: http://localhost:3000" 