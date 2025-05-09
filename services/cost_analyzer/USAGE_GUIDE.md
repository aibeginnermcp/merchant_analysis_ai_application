# 成本穿透分析服务使用指南

本指南介绍如何在本地开发、测试和部署成本分析服务。

## 1. 本地开发

### 环境准备

1. 安装Python 3.9+
2. 安装Docker和Docker Compose
3. 克隆代码仓库

### 依赖安装

```bash
# 进入成本分析服务目录
cd services/cost_analyzer

# 安装依赖
pip install -r requirements.txt
```

### 本地运行（无Docker）

```bash
# 设置环境变量
export MONGODB_URI="mongodb://localhost:27017/merchant_analytics"
export DEBUG=true
export PORT=8001

# 启动服务
python -m uvicorn main:app --reload
```

服务将在 http://localhost:8001 上启动，并支持热重载。

## 2. 使用Docker进行测试

我们提供了专用的测试脚本，用于在Docker环境下测试服务：

```bash
# 从项目根目录运行
./local_test_cost_analyzer.sh
```

该脚本会：
- 构建Docker镜像
- 可选地启动MongoDB容器
- 运行服务容器并执行基本测试
- 显示测试结果和服务日志

### 关键API测试

服务启动后，可以测试以下端点：

1. **健康检查**：`GET /health`
   ```bash
   curl http://localhost:8001/health
   ```

2. **调试信息**：`GET /debug`
   ```bash
   curl http://localhost:8001/debug
   ```

3. **成本分析**：`POST /api/v1/analyze`
   ```bash
   curl -X POST http://localhost:8001/api/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{
       "merchant_id": "test123",
       "start_date": "2023-01-01",
       "end_date": "2023-03-31",
       "analysis_depth": "detailed"
     }'
   ```

## 3. CI/CD流程

### GitHub Actions

项目配置了自动化CI/CD流程，在以下情况下会触发：

- 推送到`main`分支且修改了成本分析服务相关文件
- 手动触发工作流

查看工作流配置：`.github/workflows/cost_analyzer_test.yml`

### 手动触发测试

1. 进入GitHub仓库
2. 点击"Actions"选项卡
3. 选择"成本穿透分析服务测试"工作流
4. 点击"Run workflow"按钮

## 4. 特性和配置

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| MONGODB_URI | MongoDB连接字符串 | mongodb://mongodb:27017/merchant_analytics |
| PORT | 服务端口 | 8001 |
| DEBUG | 调试模式开关 | false |
| MONGODB_AVAILABLE | 强制设置MongoDB可用状态 | true |
| WORKERS | 生产模式下的工作进程数 | 1 |

### 健壮性功能

- **MongoDB降级运行**：即使MongoDB不可用，服务也能启动，并使用模拟数据
- **重连机制**：使用`/reconnect-mongodb`端点可以在运行时重新连接数据库
- **详细调试**：`/debug`端点提供详细的服务状态信息

## 5. 常见问题排查

### Docker构建失败

检查：
- requirements.txt格式是否正确
- 确保网络连接正常，能够访问PyPI

### 服务启动但API调用失败

检查：
- MongoDB连接状态（通过/debug端点）
- 网络配置是否正确
- 请求格式和参数是否符合规范

### 容器健康检查失败

1. 进入容器执行调试：
   ```bash
   docker exec -it cost_analyzer_test /app/debug.sh
   ```

2. 查看服务日志：
   ```bash
   docker logs cost_analyzer_test
   ```

## 6. 进一步阅读

- 查看`README_BUGFIX.md`了解最近的重要修复
- 查看`MODIFICATIONS.md`获取详细的修改记录
- 参考`tests`目录下的测试用例，了解服务功能和用法 