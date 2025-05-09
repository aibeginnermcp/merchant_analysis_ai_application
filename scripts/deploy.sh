#!/bin/bash
# 智能商户经营分析报表生成器部署脚本
# 支持一键部署整个系统到Kubernetes环境
# 使用方法: ./scripts/deploy.sh [环境] [版本标签]
# 例如: ./scripts/deploy.sh dev v1.0.0

set -e

# 默认值
ENV=${1:-"dev"}
VERSION=${2:-"latest"}
NAMESPACE="merchant-analytics"
DOCKER_REGISTRY="merchant-registry.example.com"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印帮助信息
print_usage() {
    echo -e "${BLUE}智能商户经营分析报表生成器部署脚本${NC}"
    echo "使用方法: $0 [环境] [版本标签]"
    echo "环境选项: dev, test, staging, prod"
    echo "版本标签: 例如 v1.0.0, latest"
    echo ""
    echo "示例:"
    echo "  $0 dev v1.0.0     # 部署v1.0.0版本到开发环境"
    echo "  $0 prod latest    # 部署最新版本到生产环境"
}

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
    
    # 检查docker
    if ! command -v docker &> /dev/null; then
        log_error "未找到docker命令，请先安装docker"
        exit 1
    fi
    
    # 检查kustomize
    if ! command -v kustomize &> /dev/null; then
        log_warning "未找到kustomize命令，尝试使用kubectl kustomize替代"
    fi
    
    log "依赖检查完成"
}

# 检查kubectl是否可以连接到Kubernetes集群
check_kubernetes_connection() {
    log "检查Kubernetes连接..."
    
    if ! kubectl get ns &> /dev/null; then
        log_error "无法连接到Kubernetes集群，请检查您的kubeconfig配置"
        exit 1
    fi
    
    log "Kubernetes集群连接正常"
}

# 创建命名空间（如果不存在）
create_namespace() {
    log "确保命名空间${NAMESPACE}存在..."
    
    if ! kubectl get namespace ${NAMESPACE} &> /dev/null; then
        kubectl create namespace ${NAMESPACE}
        log "已创建命名空间${NAMESPACE}"
    else
        log "命名空间${NAMESPACE}已存在"
    fi
}

# 替换kustomization.yaml中的镜像标签
update_image_tags() {
    local env_file="k8s/overlays/${ENV}/kustomization.yaml"
    
    log "更新镜像标签为${VERSION}..."
    
    if [ ! -f ${env_file} ]; then
        log_error "找不到环境配置文件: ${env_file}"
        exit 1
    fi
    
    # 设置环境变量供kustomize使用
    export IMAGE_TAG=${VERSION}
    export DOCKER_REGISTRY=${DOCKER_REGISTRY}
    
    log "已更新镜像标签"
}

# 应用Kubernetes配置
apply_kubernetes_config() {
    log "部署应用到${ENV}环境..."
    
    # 使用kustomize生成配置并应用
    kubectl apply -k k8s/overlays/${ENV}
    
    log "部署命令已执行"
}

# 构建和推送镜像（用于开发环境）
build_and_push_images() {
    if [ "${ENV}" == "dev" ]; then
        log "为开发环境构建和推送镜像..."
        
        # 构建并推送API网关
        log "构建API网关镜像..."
        docker build -t ${DOCKER_REGISTRY}/merchant-analytics-api-gateway:${VERSION} -f services/api_gateway/Dockerfile services/api_gateway
        docker push ${DOCKER_REGISTRY}/merchant-analytics-api-gateway:${VERSION}
        
        # 构建并推送数据模拟服务
        log "构建数据模拟服务镜像..."
        docker build -t ${DOCKER_REGISTRY}/merchant-analytics-data-simulator:${VERSION} -f services/data_simulator/Dockerfile services/data_simulator
        docker push ${DOCKER_REGISTRY}/merchant-analytics-data-simulator:${VERSION}
        
        # 构建并推送现金流预测服务
        log "构建现金流预测服务镜像..."
        docker build -t ${DOCKER_REGISTRY}/merchant-analytics-cashflow-predictor:${VERSION} -f services/cashflow_predictor/Dockerfile services/cashflow_predictor
        docker push ${DOCKER_REGISTRY}/merchant-analytics-cashflow-predictor:${VERSION}
        
        # 构建并推送成本分析服务
        log "构建成本分析服务镜像..."
        docker build -t ${DOCKER_REGISTRY}/merchant-analytics-cost-analyzer:${VERSION} -f services/cost_analyzer/Dockerfile services/cost_analyzer
        docker push ${DOCKER_REGISTRY}/merchant-analytics-cost-analyzer:${VERSION}
        
        # 构建并推送合规检查服务
        log "构建合规检查服务镜像..."
        docker build -t ${DOCKER_REGISTRY}/merchant-analytics-compliance-checker:${VERSION} -f services/compliance_checker/Dockerfile services/compliance_checker
        docker push ${DOCKER_REGISTRY}/merchant-analytics-compliance-checker:${VERSION}
        
        log "所有服务镜像已构建并推送"
    else
        log "跳过镜像构建(非开发环境)"
    fi
}

# 检查部署状态
check_deployment_status() {
    log "检查部署状态..."
    
    # 等待所有部署完成
    kubectl rollout status deployment -n ${NAMESPACE} --timeout=300s || true
    
    # 检查Pod状态
    local running_pods=$(kubectl get pods -n ${NAMESPACE} --field-selector=status.phase=Running --no-headers | wc -l)
    local total_pods=$(kubectl get pods -n ${NAMESPACE} --no-headers | wc -l)
    
    log "运行中的Pod: ${running_pods}/${total_pods}"
    
    if [ "${running_pods}" -eq "${total_pods}" ]; then
        log "所有Pod运行正常"
    else
        log_warning "部分Pod未正常运行，请检查详细状态:"
        kubectl get pods -n ${NAMESPACE}
    fi
}

# 输出访问信息
print_access_info() {
    log "部署完成！"
    
    # 获取API网关服务信息
    local api_gateway_service=$(kubectl get svc -n ${NAMESPACE} api-gateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -z "${api_gateway_service}" ]; then
        api_gateway_service="<pending>"
    fi
    
    echo -e "${BLUE}==================================================${NC}"
    echo -e "${BLUE}|       智能商户经营分析报表生成器              |${NC}"
    echo -e "${BLUE}==================================================${NC}"
    echo -e "环境: ${ENV}"
    echo -e "版本: ${VERSION}"
    echo -e "API网关: http://${api_gateway_service}:8080"
    echo -e "API文档: http://${api_gateway_service}:8080/docs"
    echo -e "${BLUE}==================================================${NC}"
    
    if [ "${ENV}" == "prod" ]; then
        log_warning "您已部署到生产环境，请确保安全策略已正确配置"
    fi
}

# 主流程
main() {
    # 显示参数
    if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
        print_usage
        exit 0
    fi
    
    log "开始部署流程 - 环境: ${ENV}, 版本: ${VERSION}"
    
    # 检查依赖
    check_dependencies
    
    # 检查Kubernetes连接
    check_kubernetes_connection
    
    # 创建命名空间
    create_namespace
    
    # 更新镜像标签
    update_image_tags
    
    # 构建和推送镜像（仅开发环境）
    build_and_push_images
    
    # 应用Kubernetes配置
    apply_kubernetes_config
    
    # 检查部署状态
    check_deployment_status
    
    # 打印访问信息
    print_access_info
}

# 执行主函数
main "$@" 