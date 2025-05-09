"""
错误处理模块
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException

class BusinessError(Exception):
    """业务错误基类"""
    def __init__(
        self,
        code: int,
        message: str,
        service: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.service = service
        self.details = details or {}
        super().__init__(message)

class ValidationError(BusinessError):
    """数据验证错误"""
    def __init__(
        self,
        message: str,
        service: str,
        field: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=9001,
            message=f"验证错误: {message}",
            service=service,
            details={"field": field, **(details or {})}
        )

class ResourceNotFoundError(BusinessError):
    """资源不存在错误"""
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        service: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=9002,
            message=f"{resource_type} {resource_id} 不存在",
            service=service,
            details={"resource_type": resource_type, "resource_id": resource_id, **(details or {})}
        )

class ServiceError(BusinessError):
    """服务错误"""
    def __init__(
        self,
        service: str,
        operation: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=9003,
            message=f"服务 {service} 执行 {operation} 时发生错误",
            service=service,
            details={"operation": operation, **(details or {})}
        )

def handle_business_error(error: BusinessError) -> HTTPException:
    """转换业务错误为HTTP异常"""
    return HTTPException(
        status_code=400,
        detail={
            "code": error.code,
            "message": error.message,
            "service": error.service,
            "details": error.details
        }
    ) 