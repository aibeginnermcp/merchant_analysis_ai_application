"""日志模块"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("api_gateway")

def setup_logging(app: FastAPI):
    """设置日志"""
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        """日志中间件"""
        # 记录请求开始时间
        start_time = datetime.now()
        
        # 构建请求日志
        request_log = {
            "timestamp": start_time.isoformat(),
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_host": request.client.host,
            "client_port": request.client.port
        }
        
        # 记录请求日志
        logger.info(f"收到请求: {json.dumps(request_log, ensure_ascii=False)}")
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = (datetime.now() - start_time).total_seconds()
            
            # 构建响应日志
            response_log = {
                "status_code": response.status_code,
                "process_time": process_time
            }
            
            # 记录响应日志
            logger.info(f"请求处理完成: {json.dumps(response_log, ensure_ascii=False)}")
            
            return response
            
        except Exception as e:
            # 记录错误日志
            logger.error(f"请求处理失败: {str(e)}", exc_info=True)
            
            # 返回错误响应
            return JSONResponse(
                status_code=500,
                content={"error": "服务器内部错误"}
            ) 