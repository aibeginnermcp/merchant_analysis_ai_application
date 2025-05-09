# 智能商户经营分析报表生成器 - 常见问题解答(FAQ)

## 基础问题

### Q1: 这个系统适合哪些类型的商户？
智能商户经营分析报表生成器适用于各类商户，包括但不限于餐饮、零售、服务业、制造业等。系统内置不同行业的分析模型，能针对不同行业特点提供定制化分析。

### Q2: 系统需要什么样的硬件配置？
系统基于Docker容器运行，推荐配置为：
- CPU: 4核心以上
- 内存: 8GB以上
- 存储: 10GB可用空间
- 网络: 稳定的网络连接

### Q3: 系统支持哪些操作系统？
支持所有能运行Docker的系统，包括：
- Linux (Ubuntu, CentOS, Debian等)
- macOS
- Windows 10/11 Professional或企业版(需启用Hyper-V)

## 安装与配置

### Q4: 如何更改服务的默认端口？
编辑项目根目录的`.env`文件，修改对应服务的端口配置：
```
API_GATEWAY_PORT=8000
COST_ANALYZER_PORT=8001
CASHFLOW_PREDICTOR_PORT=8002
COMPLIANCE_CHECKER_PORT=8003
DATA_SIMULATOR_PORT=8004
```

### Q5: 如何配置数据库连接？
系统默认使用Docker Compose中配置的PostgreSQL数据库。如需连接外部数据库，请修改`.env`文件中的数据库配置：
```
DB_HOST=your_db_host
DB_PORT=5432
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_db_name
```

### Q6: 如何备份系统数据？
可以使用以下命令备份PostgreSQL数据：
```bash
docker-compose exec postgres pg_dump -U postgres merchant_analytics > backup.sql
```

## 使用问题

### Q7: 如何添加新的商户数据？
可以通过API接口添加新商户：
```bash
curl -X POST http://localhost:8000/api/v1/merchants \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "示例商户",
    "type": "restaurant",
    "address": "北京市朝阳区xxx街道",
    "contact": "13800138000"
  }'
```

### Q8: 系统支持哪些报表格式？
系统支持以下格式导出报表：
- PDF
- Excel (.xlsx)
- CSV
- HTML

### Q9: 如何导入历史财务数据？
系统支持多种方式导入历史数据：
1. API批量导入
   ```bash
   curl -X POST http://localhost:8000/api/v1/data/import \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "merchant_id": "123456",
       "data_type": "financial",
       "data": [...]
     }'
   ```
   
2. Excel/CSV文件上传
   ```bash
   curl -X POST http://localhost:8000/api/v1/data/import-file \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@financial_data.xlsx" \
     -F "merchant_id=123456" \
     -F "data_type=financial"
   ```

### Q10: 如何设置定期自动生成报表？
可以通过API设置报表计划任务：
```bash
curl -X POST http://localhost:8000/api/v1/reports/schedule \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_id": "123456",
    "report_type": "full",
    "schedule": "weekly",
    "delivery": {
      "email": "user@example.com",
      "format": "pdf"
    }
  }'
```

## 技术问题

### Q11: JWT令牌过期后如何刷新？
使用刷新令牌获取新的访问令牌：
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### Q12: 如何查看服务的API文档？
系统提供了Swagger UI界面，访问以下地址查看API文档：
```
http://localhost:8000/docs
```

### Q13: 如何处理"数据库连接失败"错误？
1. 检查数据库服务是否正常运行：`docker-compose ps postgres`
2. 检查数据库配置是否正确：查看`.env`文件中的数据库配置
3. 尝试重启数据库服务：`docker-compose restart postgres`
4. 检查日志文件：`docker-compose logs postgres`

## 性能优化

### Q14: 系统处理大量数据时变慢，如何优化？
1. 增加服务容器的资源限制：编辑`docker-compose.yml`文件，调整资源配置
   ```yaml
   services:
     api_gateway:
       # ...
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 1G
           reservations:
             cpus: '0.5'
             memory: 512M
   ```

2. 优化数据库：增加数据库连接池大小，在各服务配置文件中修改
3. 启用缓存：配置Redis缓存服务，减少数据库查询

### Q15: 如何实现系统的水平扩展？
1. 使用Kubernetes部署：转换docker-compose.yml为Kubernetes配置
2. 配置负载均衡器：在API网关前增加负载均衡
3. 服务实例扩展：`kubectl scale deployment api-gateway --replicas=3`

## 安全问题

### Q16: 系统如何保障数据安全？
1. 所有API通信使用HTTPS加密
2. 身份验证使用JWT令牌
3. 数据库密码等敏感信息通过环境变量注入
4. 服务间通信使用mTLS双向认证
5. 定期备份数据库

### Q17: 如何修改JWT密钥？
1. 在`.env`文件中修改`JWT_SECRET`值
2. 重启API网关服务：`docker-compose restart api_gateway`
3. 注意：修改密钥后，所有已颁发的令牌将失效，用户需要重新登录

## 其他问题

### Q18: 如何获取技术支持？
1. 查阅项目文档：`docs/`目录
2. 提交GitHub Issue：https://github.com/yourusername/merchant-analytics/issues
3. 发送邮件：support@merchant-analytics.example.com

### Q19: 系统是否支持多语言？
是的，系统支持多语言界面。可以通过API请求头设置语言：
```bash
curl -X GET http://localhost:8000/api/v1/reports/list \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Accept-Language: zh-CN"
```

支持的语言包括：
- 简体中文 (zh-CN)
- 英语 (en-US)
- 日语 (ja-JP)
- 韩语 (ko-KR)

### Q20: 系统会自动更新吗？
系统不会自动更新。当有新版本发布时，您需要手动更新：
```bash
# 拉取最新代码
git pull

# 重新构建并启动服务
docker-compose down
docker-compose build
docker-compose up -d
```

---

如有其他问题，请参考[详细使用说明](使用说明.md)或联系技术支持团队。 