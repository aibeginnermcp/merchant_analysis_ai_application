"""
商户智能经营分析平台错误处理模块

定义所有微服务通用的异常类和错误处理机制
"""

from typing import Any, Dict, Optional

class MerchantBIError(Exception):
    """商户智能经营分析平台基础异常类"""
    
    def __init__(
        self,
        message: str,
        code: int,
        service: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化异常
        
        Args:
            message: 错误信息
            code: 错误码
            service: 服务名称
            details: 详细错误信息
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.service = service
        self.details = details or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            Dict[str, Any]: 异常信息字典
        """
        return {
            'code': self.code,
            'message': self.message,
            'service': self.service,
            'details': self.details
        }

class ValidationError(MerchantBIError):
    """数据验证错误"""
    
    def __init__(
        self,
        message: str,
        service: str,
        field: str,
        value: Any,
        constraint: str
    ):
        """
        初始化验证错误
        
        Args:
            message: 错误信息
            service: 服务名称
            field: 验证失败的字段
            value: 验证失败的值
            constraint: 验证约束
        """
        details = {
            'field': field,
            'value': value,
            'constraint': constraint
        }
        super().__init__(message, 9001, service, details)

class BusinessError(MerchantBIError):
    """业务逻辑错误"""
    
    def __init__(
        self,
        message: str,
        code: int,
        service: str,
        operation: str,
        params: Optional[Dict[str, Any]] = None
    ):
        """
        初始化业务错误
        
        Args:
            message: 错误信息
            code: 错误码
            service: 服务名称
            operation: 业务操作
            params: 操作参数
        """
        details = {
            'operation': operation,
            'params': params or {}
        }
        super().__init__(message, code, service, details)

class ResourceNotFoundError(MerchantBIError):
    """资源不存在错误"""
    
    def __init__(
        self,
        resource: str,
        resource_id: str,
        service: str
    ):
        """
        初始化资源不存在错误
        
        Args:
            resource: 资源类型
            resource_id: 资源ID
            service: 服务名称
        """
        message = f'资源不存在: {resource}[{resource_id}]'
        details = {
            'resource': resource,
            'resource_id': resource_id
        }
        super().__init__(message, 9004, service, details)

class ServiceUnavailableError(MerchantBIError):
    """服务不可用错误"""
    
    def __init__(
        self,
        service: str,
        dependency: str,
        reason: str
    ):
        """
        初始化服务不可用错误
        
        Args:
            service: 服务名称
            dependency: 依赖服务
            reason: 不可用原因
        """
        message = f'服务不可用: {dependency} - {reason}'
        details = {
            'dependency': dependency,
            'reason': reason
        }
        super().__init__(message, 9005, service, details)

class AuthenticationError(MerchantBIError):
    """认证错误"""
    
    def __init__(
        self,
        message: str,
        service: str,
        token: Optional[str] = None
    ):
        """
        初始化认证错误
        
        Args:
            message: 错误信息
            service: 服务名称
            token: 认证令牌
        """
        details = {}
        if token:
            details['token'] = token[:10] + '...'  # 只显示令牌前10位
        super().__init__(message, 9002, service, details)

class AuthorizationError(MerchantBIError):
    """授权错误"""
    
    def __init__(
        self,
        message: str,
        service: str,
        user_id: str,
        required_permissions: list[str]
    ):
        """
        初始化授权错误
        
        Args:
            message: 错误信息
            service: 服务名称
            user_id: 用户ID
            required_permissions: 所需权限列表
        """
        details = {
            'user_id': user_id,
            'required_permissions': required_permissions
        }
        super().__init__(message, 9003, service, details) 