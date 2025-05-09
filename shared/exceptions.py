#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
异常处理模块 - 定义统一的异常类型和处理方法

定义了系统中所有标准化的异常类型，用于规范化错误处理。
所有自定义异常都应继承自BaseError类。
"""

from typing import Dict, Any, Optional


class ErrorCode:
    """错误代码枚举"""
    # 通用错误码
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST" 
    VALIDATION_ERROR = "VALIDATION_ERROR"
    
    # 认证相关错误码
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    
    # 权限相关错误码
    PERMISSION_DENIED = "PERMISSION_DENIED"
    ACCESS_FORBIDDEN = "ACCESS_FORBIDDEN"
    
    # 资源相关错误码
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_STATE_CONFLICT = "RESOURCE_STATE_CONFLICT"
    
    # 业务相关错误码 (1000-1999)
    # 现金流预测相关
    CASHFLOW_PREDICTION_FAILED = "CASHFLOW_PREDICTION_FAILED"
    INSUFFICIENT_DATA_FOR_PREDICTION = "INSUFFICIENT_DATA_FOR_PREDICTION"
    INVALID_PREDICTION_MODEL = "INVALID_PREDICTION_MODEL"
    
    # 成本分析相关
    COST_ANALYSIS_FAILED = "COST_ANALYSIS_FAILED"
    INVALID_COST_STRUCTURE = "INVALID_COST_STRUCTURE"
    
    # 合规检查相关
    COMPLIANCE_CHECK_FAILED = "COMPLIANCE_CHECK_FAILED"
    RULE_EVALUATION_ERROR = "RULE_EVALUATION_ERROR"
    
    # 外部服务错误码 (2000-2999)
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    CACHE_ERROR = "CACHE_ERROR"
    MESSAGING_ERROR = "MESSAGING_ERROR"


class BaseError(Exception):
    """基础异常类，所有自定义异常都应该继承此类"""
    
    def __init__(
        self, 
        message: str = "发生错误", 
        code: str = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        source: str = "system"
    ):
        """
        初始化异常
        
        Args:
            message: 错误信息
            code: 错误代码
            details: 详细错误信息，可用于调试
            source: 错误来源服务
        """
        self.message = message
        self.code = code
        self.details = details or {}
        self.source = source
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将异常转换为字典格式，用于JSON响应
        
        Returns:
            Dict[str, Any]: 异常信息字典
        """
        error_dict = {
            "message": self.message,
            "code": self.code,
            "source": self.source
        }
        
        if self.details:
            error_dict["details"] = self.details
            
        return error_dict


class ValidationError(BaseError):
    """输入验证错误"""
    
    def __init__(
        self, 
        message: str = "输入数据验证失败",
        details: Optional[Dict[str, Any]] = None,
        source: str = "validation"
    ):
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
            details=details,
            source=source
        )


class AuthError(BaseError):
    """认证错误"""
    
    def __init__(
        self, 
        message: str = "认证失败",
        code: str = ErrorCode.AUTHENTICATION_FAILED,
        details: Optional[Dict[str, Any]] = None,
        source: str = "auth"
    ):
        super().__init__(
            message=message,
            code=code,
            details=details,
            source=source
        )


class TokenExpiredError(AuthError):
    """令牌过期错误"""
    
    def __init__(
        self, 
        message: str = "认证令牌已过期",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.TOKEN_EXPIRED,
            details=details
        )


class InvalidTokenError(AuthError):
    """无效令牌错误"""
    
    def __init__(
        self, 
        message: str = "无效的认证令牌",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_TOKEN,
            details=details
        )


class PermissionDeniedError(BaseError):
    """权限拒绝错误"""
    
    def __init__(
        self, 
        message: str = "权限不足，拒绝访问",
        details: Optional[Dict[str, Any]] = None,
        source: str = "auth"
    ):
        super().__init__(
            message=message,
            code=ErrorCode.PERMISSION_DENIED,
            details=details,
            source=source
        )


class ResourceNotFoundError(BaseError):
    """资源不存在错误"""
    
    def __init__(
        self, 
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        source: str = "data_access"
    ):
        if message is None:
            message = f"找不到{resource_type}: {resource_id}"
            
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_NOT_FOUND,
            details=details or {"resource_type": resource_type, "resource_id": resource_id},
            source=source
        )


class ResourceAlreadyExistsError(BaseError):
    """资源已存在错误"""
    
    def __init__(
        self, 
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        source: str = "data_access"
    ):
        if message is None:
            message = f"{resource_type}已存在: {resource_id}"
            
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_ALREADY_EXISTS,
            details=details or {"resource_type": resource_type, "resource_id": resource_id},
            source=source
        )


class ConfigurationError(BaseError):
    """配置错误"""
    
    def __init__(
        self, 
        message: str = "配置错误",
        details: Optional[Dict[str, Any]] = None,
        source: str = "configuration"
    ):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            details=details,
            source=source
        )


class DatabaseError(BaseError):
    """数据库错误"""
    
    def __init__(
        self, 
        message: str = "数据库操作失败",
        details: Optional[Dict[str, Any]] = None,
        source: str = "database"
    ):
        super().__init__(
            message=message,
            code=ErrorCode.DATABASE_ERROR,
            details=details,
            source=source
        )


class ExternalServiceError(BaseError):
    """外部服务错误"""
    
    def __init__(
        self, 
        service_name: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        if message is None:
            message = f"外部服务{service_name}调用失败"
            
        super().__init__(
            message=message,
            code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            details=details or {"service_name": service_name},
            source=service_name
        )


# 业务相关异常
class CashflowPredictionError(BaseError):
    """现金流预测错误"""
    
    def __init__(
        self, 
        message: str = "现金流预测失败",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.CASHFLOW_PREDICTION_FAILED,
            details=details,
            source="cashflow_predictor"
        )


class CostAnalysisError(BaseError):
    """成本分析错误"""
    
    def __init__(
        self, 
        message: str = "成本分析失败",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.COST_ANALYSIS_FAILED,
            details=details,
            source="cost_analyzer"
        )


class ComplianceCheckError(BaseError):
    """合规检查错误"""
    
    def __init__(
        self, 
        message: str = "合规检查失败",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.COMPLIANCE_CHECK_FAILED,
            details=details,
            source="compliance_checker"
        ) 