"""错误处理模块"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Union

class ServiceError(Exception):
    """服务错误基类"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code

class ServiceUnavailableError(ServiceError):
    """服务不可用错误"""
    def __init__(self, service_name: str):
        super().__init__(
            message=f"服务 {service_name} 当前不可用",
            status_code=503
        )

def setup_error_handlers(app: FastAPI):
    """设置错误处理器"""
    @app.exception_handler(ServiceError)
    async def service_error_handler(request: Request, exc: ServiceError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message}
        )

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "服务器内部错误"}
        ) 