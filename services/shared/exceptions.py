from typing import Optional, Dict, Any
from enum import Enum
from fastapi import HTTPException

class ServiceType(Enum):
    """
    服务类型枚举
    """
    GATEWAY = "gateway"
    DATA_SIMULATOR = "data_simulator"
    CASH_FLOW = "cash_flow"
    COST_ANALYSIS = "cost_analysis"
    COMPLIANCE = "compliance"

class ErrorCode(Enum):
    """
    错误码枚举
    """
    # 业务错误 (4xxx)
    VALIDATION_ERROR = 4001
    BUSINESS_RULE_VIOLATION = 4002
    RESOURCE_NOT_FOUND = 4003
    PERMISSION_DENIED = 4004
    
    # 系统错误 (5xxx)
    SERVICE_UNAVAILABLE = 5001
    DEPENDENCY_TIMEOUT = 5002
    INTERNAL_ERROR = 5003

class AnalysisException(Exception):
    """
    分析服务统一异常类
    """
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        service: ServiceType,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.service = service
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        """
        return {
            "code": self.code.value,
            "message": self.message,
            "service": self.service.value,
            "details": self.details
        }

class ValidationError(AnalysisException):
    """
    数据验证错误
    """
    def __init__(self, message: str, service: ServiceType, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            service=service,
            details=details
        )

class BusinessError(AnalysisException):
    """
    业务规则错误
    """
    def __init__(self, message: str, service: ServiceType, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            message=message,
            service=service,
            details=details
        )

class ResourceNotFoundError(AnalysisException):
    """
    资源不存在错误
    """
    def __init__(self, message: str, service: ServiceType, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.RESOURCE_NOT_FOUND,
            message=message,
            service=service,
            details=details
        )

class SystemError(AnalysisException):
    """
    系统内部错误
    """
    def __init__(self, message: str, service: ServiceType, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.INTERNAL_ERROR,
            message=message,
            service=service,
            details=details
        )

"""
统一异常处理模块
"""
class BusinessError(Exception):
    """业务异常基类"""
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class SystemError(Exception):
    """系统异常基类"""
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class ValidationError(BusinessError):
    """参数验证错误"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="2-0001",
            message=message,
            status_code=400,
            details=details
        )

class AuthenticationError(BusinessError):
    """认证错误"""
    def __init__(self, message: str = "未授权访问"):
        super().__init__(
            code="2-0002",
            message=message,
            status_code=401
        )

class ResourceNotFoundError(BusinessError):
    """资源不存在错误"""
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code="2-0003",
            message=f"{resource} {resource_id} 不存在",
            status_code=404
        )

class DatabaseError(SystemError):
    """数据库错误"""
    def __init__(self, message: str = "数据库连接失败"):
        super().__init__(
            code="3-0001",
            message=message,
            status_code=500
        )

class CacheError(SystemError):
    """缓存错误"""
    def __init__(self, message: str = "缓存服务异常"):
        super().__init__(
            code="3-0002",
            message=message,
            status_code=500
        ) 