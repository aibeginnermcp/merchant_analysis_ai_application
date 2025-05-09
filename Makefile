# 智能商户经营分析报表生成器 Makefile

.PHONY: help setup dev test lint format clean all build down restart logs

# 变量定义
DOCKER_COMPOSE = docker-compose
PIP = pip
PYTHON = python
PYTEST = pytest
BLACK = black
ISORT = isort

# 默认目标
help:
	@echo "智能商户经营分析报表生成器"
	@echo ""
	@echo "可用命令:"
	@echo "  setup      - 安装依赖"
	@echo "  dev        - 启动开发环境"
	@echo "  test       - 运行测试"
	@echo "  lint       - 运行代码检查"
	@echo "  format     - 格式化代码"
	@echo "  build      - 构建Docker镜像"
	@echo "  up         - 启动所有服务"
	@echo "  down       - 停止所有服务"
	@echo "  restart    - 重启所有服务"
	@echo "  logs       - 查看日志"
	@echo "  clean      - 清理临时文件"
	@echo "  all        - 构建并启动所有服务"

# 安装依赖
setup:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

# 启动开发环境
dev:
	$(DOCKER_COMPOSE) -f docker-compose.dev.yml up -d

# 运行测试
test:
	$(PYTEST) tests/

# 代码检查
lint:
	$(BLACK) --check services/ shared/ tests/
	$(ISORT) --check services/ shared/ tests/

# 格式化代码
format:
	$(BLACK) services/ shared/ tests/
	$(ISORT) services/ shared/ tests/

# 构建Docker镜像
build:
	$(DOCKER_COMPOSE) build

# 启动所有服务
up:
	$(DOCKER_COMPOSE) up -d

# 停止所有服务
down:
	$(DOCKER_COMPOSE) down

# 重启所有服务
restart:
	$(DOCKER_COMPOSE) restart

# 查看日志
logs:
	$(DOCKER_COMPOSE) logs -f

# 清理临时文件
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# 构建并启动所有服务
all: build up 