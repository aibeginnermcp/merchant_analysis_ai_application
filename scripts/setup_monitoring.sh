#!/bin/bash
# 监控系统设置脚本
# 配置Prometheus、Grafana和EFK日志系统
# 使用方法: ./scripts/setup_monitoring.sh [环境]
# 例如: ./scripts/setup_monitoring.sh dev

set -e

# 默认值
ENV=${1:-"dev"}
NAMESPACE="merchant-analytics-monitoring"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印信息
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log "检查依赖工具..."
    
    # 检查kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "未找到kubectl命令，请先安装kubectl"
        exit 1
    fi
    
    # 检查helm
    if ! command -v helm &> /dev/null; then
        log_error "未找到helm命令，请先安装helm"
        exit 1
    fi
    
    log "依赖检查完成"
}

# 创建命名空间
create_namespace() {
    log "创建监控命名空间: ${NAMESPACE}..."
    
    if ! kubectl get namespace ${NAMESPACE} &> /dev/null; then
        kubectl create namespace ${NAMESPACE}
        log "已创建命名空间: ${NAMESPACE}"
    else
        log "命名空间已存在: ${NAMESPACE}"
    fi
}

# 添加和更新Helm仓库
setup_helm_repos() {
    log "配置Helm仓库..."
    
    # 添加Prometheus仓库
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    
    # 添加Grafana仓库
    helm repo add grafana https://grafana.github.io/helm-charts
    
    # 添加ELK仓库
    helm repo add elastic https://helm.elastic.co
    
    # 更新仓库
    helm repo update
    
    log "Helm仓库配置完成"
}

# 部署Prometheus
deploy_prometheus() {
    log "部署Prometheus..."
    
    # 检查是否已安装
    if helm status prometheus -n ${NAMESPACE} &> /dev/null; then
        log "更新Prometheus..."
        helm upgrade prometheus prometheus-community/kube-prometheus-stack \
            -n ${NAMESPACE} \
            -f monitoring/prometheus/values-${ENV}.yaml
    else
        log "安装Prometheus..."
        helm install prometheus prometheus-community/kube-prometheus-stack \
            -n ${NAMESPACE} \
            -f monitoring/prometheus/values-${ENV}.yaml
    fi
    
    log "Prometheus部署完成"
}

# 部署Grafana
deploy_grafana() {
    log "部署Grafana..."
    
    # 检查Grafana是否已安装
    if helm status grafana -n ${NAMESPACE} &> /dev/null; then
        log "更新Grafana..."
        helm upgrade grafana grafana/grafana \
            -n ${NAMESPACE} \
            -f monitoring/grafana/values-${ENV}.yaml
    else
        log "安装Grafana..."
        helm install grafana grafana/grafana \
            -n ${NAMESPACE} \
            -f monitoring/grafana/values-${ENV}.yaml
    fi
    
    # 导入仪表盘
    log "导入Grafana仪表盘..."
    
    # 等待Grafana Pod运行
    kubectl rollout status deployment grafana -n ${NAMESPACE} --timeout=180s
    
    # 获取Grafana管理员密码
    GRAFANA_PASSWORD=$(kubectl get secret -n ${NAMESPACE} grafana -o jsonpath="{.data.admin-password}" | base64 --decode)
    
    # 获取Grafana服务URL
    GRAFANA_URL="http://grafana.${NAMESPACE}.svc.cluster.local"
    
    # 创建仪表盘导入工作
    kubectl create job --from=cronjob/grafana-dashboard-importer grafana-import-dashboards -n ${NAMESPACE} || true
    
    log "Grafana部署完成"
    log "Grafana默认用户名: admin"
    log "Grafana默认密码: ${GRAFANA_PASSWORD}"
}

# 部署EFK (Elasticsearch, Fluentd, Kibana)
deploy_efk() {
    log "部署EFK日志系统..."
    
    # 部署Elasticsearch
    if helm status elasticsearch -n ${NAMESPACE} &> /dev/null; then
        log "更新Elasticsearch..."
        helm upgrade elasticsearch elastic/elasticsearch \
            -n ${NAMESPACE} \
            -f monitoring/elasticsearch/values-${ENV}.yaml
    else
        log "安装Elasticsearch..."
        helm install elasticsearch elastic/elasticsearch \
            -n ${NAMESPACE} \
            -f monitoring/elasticsearch/values-${ENV}.yaml
    fi
    
    # 等待Elasticsearch准备就绪
    log "等待Elasticsearch准备就绪..."
    kubectl rollout status statefulset elasticsearch-master -n ${NAMESPACE} --timeout=300s || true
    
    # 部署Kibana
    if helm status kibana -n ${NAMESPACE} &> /dev/null; then
        log "更新Kibana..."
        helm upgrade kibana elastic/kibana \
            -n ${NAMESPACE} \
            -f monitoring/kibana/values-${ENV}.yaml
    else
        log "安装Kibana..."
        helm install kibana elastic/kibana \
            -n ${NAMESPACE} \
            -f monitoring/kibana/values-${ENV}.yaml
    fi
    
    # 部署Fluentd
    if helm status fluentd -n ${NAMESPACE} &> /dev/null; then
        log "更新Fluentd..."
        helm upgrade fluentd grafana/fluentd \
            -n ${NAMESPACE} \
            -f monitoring/fluentd/values-${ENV}.yaml
    else
        log "安装Fluentd..."
        helm install fluentd grafana/fluentd \
            -n ${NAMESPACE} \
            -f monitoring/fluentd/values-${ENV}.yaml
    fi
    
    log "EFK日志系统部署完成"
}

# 配置服务发现
configure_service_discovery() {
    log "配置服务发现..."
    
    # 创建ServiceMonitor资源以发现应用服务指标
    kubectl apply -f monitoring/prometheus/service-monitors.yaml
    
    log "服务发现配置完成"
}

# 打印访问信息
print_access_info() {
    log "监控系统部署完成！"
    
    # 获取访问URL
    local prom_host=$(kubectl get svc -n ${NAMESPACE} prometheus-operated -o jsonpath='{.spec.clusterIP}')
    local grafana_host=$(kubectl get svc -n ${NAMESPACE} grafana -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    local kibana_host=$(kubectl get svc -n ${NAMESPACE} kibana-kibana -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    
    # 设置默认值
    if [ -z "${grafana_host}" ]; then
        grafana_host="<pending>"
    fi
    
    if [ -z "${kibana_host}" ]; then
        kibana_host="<pending>"
    fi
    
    # 获取Grafana管理员密码
    local grafana_password=$(kubectl get secret -n ${NAMESPACE} grafana -o jsonpath="{.data.admin-password}" | base64 --decode 2>/dev/null)
    
    if [ -z "${grafana_password}" ]; then
        grafana_password="<未找到>"
    fi
    
    echo -e "${BLUE}==================================================${NC}"
    echo -e "${BLUE}|       监控系统访问信息                         |${NC}"
    echo -e "${BLUE}==================================================${NC}"
    echo -e "Prometheus: http://${prom_host}:9090"
    echo -e "Grafana: http://${grafana_host}"
    echo -e "  - 用户名: admin"
    echo -e "  - 密码: ${grafana_password}"
    echo -e "Kibana: http://${kibana_host}:5601"
    echo -e "${BLUE}==================================================${NC}"
    
    log_warning "请注意：在生产环境中，应当配置适当的安全措施来保护这些地址"
}

# 主函数
main() {
    log "开始配置监控系统 - 环境: ${ENV}"
    
    # 检查依赖
    check_dependencies
    
    # 创建命名空间
    create_namespace
    
    # 设置Helm仓库
    setup_helm_repos
    
    # 部署Prometheus
    deploy_prometheus
    
    # 部署Grafana
    deploy_grafana
    
    # 部署EFK
    deploy_efk
    
    # 配置服务发现
    configure_service_discovery
    
    # 打印访问信息
    print_access_info
    
    log "监控系统设置完成!"
}

# 执行主函数
main "$@" 