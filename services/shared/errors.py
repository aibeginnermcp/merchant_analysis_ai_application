"""错误处理模块"""
from typing import Optional, Dict, Any
from enum import Enum

class ErrorCode(str, Enum):
    """错误代码枚举"""
    # 通用错误 (1000-1999)
    UNKNOWN = "1000"  # 未知错误
    INVALID_REQUEST = "1001"  # 无效请求
    SERVICE_UNAVAILABLE = "1002"  # 服务不可用
    TIMEOUT = "1003"  # 超时
    VALIDATION_ERROR = "1004"  # 数据验证错误
    
    # 服务发现错误 (2000-2999)
    SERVICE_NOT_FOUND = "2000"  # 服务未找到
    SERVICE_UNHEALTHY = "2001"  # 服务不健康
    
    # 数据错误 (3000-3999)
    DATA_NOT_FOUND = "3000"  # 数据未找到
    DATA_CONFLICT = "3001"  # 数据冲突
    DATA_INVALID = "3002"  # 数据无效
    
    # 业务错误 (4000-4999)
    ANALYSIS_FAILED = "4000"  # 分析失败
    PREDICTION_FAILED = "4001"  # 预测失败
    COMPLIANCE_CHECK_FAILED = "4002"  # 合规检查失败

class ServiceError(Exception):
    """服务错误基类"""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        service: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """初始化服务错误
        
        Args:
            code: 错误代码
            message: 错误消息
            service: 服务名称
            details: 错误详情
        """
        self.code = code
        self.message = message
        self.service = service
        self.details = details or {}
        super().__init__(message)
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式
        
        Returns:
            Dict[str, Any]: 错误信息字典
        """
        return {
            "code": self.code,
            "message": self.message,
            "service": self.service,
            "details": self.details
        }

class ServiceUnavailableError(ServiceError):
    """服务不可用错误"""
    
    def __init__(
        self,
        service: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=ErrorCode.SERVICE_UNAVAILABLE,
            message=message or f"服务 {service} 不可用",
            service=service,
            details=details
        )

class ServiceTimeoutError(ServiceError):
    """服务超时错误"""
    
    def __init__(
        self,
        service: str,
        timeout: float,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=ErrorCode.TIMEOUT,
            message=message or f"服务 {service} 请求超时 ({timeout}s)",
            service=service,
            details={"timeout": timeout, **(details or {})
        )

class ValidationError(ServiceError):
    """数据验证错误"""
    
    def __init__(
        self,
        errors: Dict[str, str],
        message: Optional[str] = None,
        service: Optional[str] = None
    ):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message or "数据验证失败",
            service=service,
            details={"errors": errors}
        )

class DataNotFoundError(ServiceError):
    """数据未找到错误"""
    
    def __init__(
        self,
        resource: str,
        resource_id: str,
        message: Optional[str] = None,
        service: Optional[str] = None
    ):
        super().__init__(
            code=ErrorCode.DATA_NOT_FOUND,
            message=message or f"{resource} {resource_id} 未找到",
            service=service,
            details={
                "resource": resource,
                "resource_id": resource_id
            }
        )

class AnalysisError(ServiceError):
    """分析错误"""
    
    def __init__(
        self,
        analysis_type: str,
        reason: str,
        message: Optional[str] = None,
        service: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            code=ErrorCode.ANALYSIS_FAILED,
            message=message or f"{analysis_type}分析失败: {reason}",
            service=service,
            details={
                "analysis_type": analysis_type,
                "reason": reason,
                **(details or {})
            }
        )

def handle_service_error(error: Exception) -> ServiceError:
    """处理服务错误
    
    Args:
        error: 原始错误
        
    Returns:
        ServiceError: 标准化的服务错误
    """
    if isinstance(error, ServiceError):
        return error
        
    if isinstance(error, TimeoutError):
        return ServiceTimeoutError(
            service="unknown",
            timeout=30,
            message=str(error)
        )
        
    if isinstance(error, ValueError):
        return ValidationError(
            errors={"value": str(error)}
        )
        
    return ServiceError(
        code=ErrorCode.UNKNOWN,
        message=str(error)
    ) 