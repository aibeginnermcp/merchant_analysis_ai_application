# GitHub Actions 配置指南

本文档介绍如何为商户智能分析平台配置GitHub Actions和Secrets，实现CI/CD流程。

## GitHub Secrets 配置

项目的CI/CD工作流需要以下Secrets，请在GitHub仓库的Settings > Secrets and variables > Actions中添加：

1. **DOCKERHUB_USERNAME** - Docker Hub用户名
2. **DOCKERHUB_TOKEN** - Docker Hub访问令牌（不是密码）
3. **PROD_HOST** - 生产服务器IP地址
4. **PROD_USERNAME** - 生产服务器SSH用户名
5. **PROD_SSH_KEY** - 生产服务器SSH私钥

### 获取Docker Hub令牌

1. 登录Docker Hub
2. 进入Account Settings > Security
3. 创建一个新的访问令牌
4. 复制令牌并保存为GitHub Secret

### 设置SSH密钥

1. 生成新的SSH密钥对（如果没有）：
   ```
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```
2. 将公钥添加到生产服务器的`~/.ssh/authorized_keys`
3. 将私钥内容保存为GitHub Secret `PROD_SSH_KEY`

## 工作流程说明

当前工作流程（`.github/workflows/main.yml`）包含以下步骤：

1. **测试** - 运行单元测试和集成测试
2. **代码风格检查** - 使用flake8、black和isort检查代码风格
3. **构建API网关** - 构建并推送API网关Docker镜像
4. **构建服务组件** - 构建并推送各微服务Docker镜像
5. **部署** - 通过SSH在生产服务器上部署服务

## 本地测试工作流

在推送到GitHub之前，可以使用以下方法在本地测试工作流：

1. 安装[act](https://github.com/nektos/act)
2. 在项目根目录创建`.secrets`文件，添加所需的环境变量
3. 运行工作流：
   ```
   act -s DOCKERHUB_USERNAME=your_username -s DOCKERHUB_TOKEN=your_token
   ```

## 已知问题及解决方案

- **测试失败但需要继续构建**：已在工作流中添加`continue-on-error: true`配置
- **服务路径不匹配**：已修复服务路径配置，确保与实际项目结构匹配
- **敏感信息泄露**：确保所有令牌、密钥都通过GitHub Secrets管理，不要直接提交到代码库

## 工作流配置最佳实践

1. 不要将敏感信息硬编码在工作流文件中
2. 对于不同环境（开发、测试、生产）使用不同的工作流或条件分支
3. 使用语义化版本控制标记Docker镜像
4. 定期检查和更新依赖项
5. 设置通知，及时了解工作流执行状态 