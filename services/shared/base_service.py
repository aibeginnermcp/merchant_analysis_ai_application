from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from .models.merchant import AnalysisRequest, AnalysisResponse
from .exceptions import ServiceType, AnalysisException, SystemError

class BaseAnalysisService(ABC):
    """
    分析服务基类
    """
    def __init__(self, service_type: ServiceType):
        self.service_type = service_type
        self.start_time = datetime.now()

    @abstractmethod
    async def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        执行分析
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        """
        pass

    async def handle_request(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        统一请求处理
        """
        try:
            # 请求预处理
            await self._preprocess_request(request)
            
            # 执行分析
            response = await self.analyze(request)
            
            # 响应后处理
            await self._postprocess_response(response)
            
            return response
            
        except AnalysisException as e:
            # 已知业务异常，直接转换为响应
            return AnalysisResponse(
                request_id=str(request.merchant_id),
                status="error",
                error=str(e),
                data=None
            )
        except Exception as e:
            # 未知系统异常，包装后返回
            system_error = SystemError(
                message="服务处理异常",
                service=self.service_type,
                details={"error": str(e)}
            )
            return AnalysisResponse(
                request_id=str(request.merchant_id),
                status="error",
                error=str(system_error),
                data=None
            )

    async def _preprocess_request(self, request: AnalysisRequest) -> None:
        """
        请求预处理
        """
        # 可以在子类中重写此方法以添加特定的预处理逻辑
        pass

    async def _postprocess_response(self, response: AnalysisResponse) -> None:
        """
        响应后处理
        """
        # 可以在子类中重写此方法以添加特定的后处理逻辑
        pass

    def get_metrics(self) -> Dict[str, Any]:
        """
        获取服务指标
        """
        return {
            "service_type": self.service_type.value,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "request_count": 0,  # 子类需要实现计数器
            "error_count": 0,    # 子类需要实现计数器
            "average_response_time": 0  # 子类需要实现计时器
        } 