"""
异常处理模块，定义了系统中使用的所有自定义异常类
"""
from enum import Enum
from typing import Optional, Dict, Any

class ErrorCode(Enum):
    """错误码枚举"""
    UNKNOWN = "UNKNOWN"
    INVALID_REQUEST = "INVALID_REQUEST"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATA_NOT_FOUND = "DATA_NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    VALIDATION_ERROR = "VALIDATION_ERROR"

class ServiceType(Enum):
    """服务类型枚举"""
    API_GATEWAY = "api_gateway"
    DATA_SIMULATOR = "data_simulator"
    CASHFLOW_PREDICTOR = "cashflow_predictor"
    COST_ANALYZER = "cost_analyzer"
    COMPLIANCE_CHECKER = "compliance_checker"

class AnalysisException(Exception):
    """分析服务基础异常类"""
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN,
        service: ServiceType = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.service = service
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "message": self.message,
            "error_code": self.error_code.value,
            "service": self.service.value if self.service else None,
            "details": self.details
        }

class ValidationException(AnalysisException):
    """输入验证异常"""
    def __init__(self, message: str, service: ServiceType = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            service=service,
            details=details
        )

class ServiceUnavailableException(AnalysisException):
    """服务不可用异常"""
    def __init__(self, message: str, service: ServiceType = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            service=service,
            details=details
        )

class DataNotFoundException(AnalysisException):
    """数据未找到异常"""
    def __init__(self, message: str, service: ServiceType = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATA_NOT_FOUND,
            service=service,
            details=details
        )

class PermissionDeniedException(AnalysisException):
    """权限拒绝异常"""
    def __init__(self, message: str, service: ServiceType = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.PERMISSION_DENIED,
            service=service,
            details=details
        ) 