"""服务客户端模块"""
import json
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from .circuit_breaker import CircuitBreaker
from .service_discovery import ServiceDiscovery
from shared.errors import (
    ServiceError,
    ServiceUnavailableError,
    ServiceTimeoutError,
    handle_service_error
)

class BaseServiceClient:
    """基础服务客户端"""
    
    def __init__(self, service_name: str):
        """初始化客户端
        
        Args:
            service_name: 服务名称
        """
        self.service_name = service_name
        self.discovery = ServiceDiscovery()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            retry_timeout=5
        )
        
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30
    ) -> Dict[str, Any]:
        """发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: 接口路径
            data: 请求数据
            params: 查询参数
            timeout: 超时时间（秒）
            
        Returns:
            Dict[str, Any]: 响应数据
            
        Raises:
            ServiceError: 服务调用错误
        """
        try:
            # 获取服务地址
            service_url = await self.discovery.get_service_url(self.service_name)
            if not service_url:
                raise ServiceUnavailableError(
                    service=self.service_name,
                    message=f"服务 {self.service_name} 不可用或未注册"
                )
                
            url = f"{service_url}{endpoint}"
            
            # 使用断路器包装请求
            async with self.circuit_breaker:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.request(
                            method=method,
                            url=url,
                            json=data,
                            params=params,
                            timeout=timeout
                        ) as response:
                            if response.status >= 400:
                                error_data = await response.json()
                                raise ServiceError(
                                    code=error_data.get("code", "UNKNOWN"),
                                    message=error_data.get("message", "未知错误"),
                                    service=self.service_name,
                                    details=error_data.get("details")
                                )
                            return await response.json()
                except asyncio.TimeoutError:
                    raise ServiceTimeoutError(
                        service=self.service_name,
                        timeout=timeout
                    )
                except aiohttp.ClientError as e:
                    raise ServiceUnavailableError(
                        service=self.service_name,
                        message=str(e)
                    )
                    
        except Exception as e:
            raise handle_service_error(e)

class DataSimulatorClient(BaseServiceClient):
    """数据模拟服务客户端"""
    
    def __init__(self):
        super().__init__("data-simulator")
        
    async def generate_data(
        self,
        merchant_id: str,
        start_date: datetime,
        end_date: datetime,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成模拟数据
        
        Args:
            merchant_id: 商户ID
            start_date: 开始日期
            end_date: 结束日期
            industry: 行业类型
            
        Returns:
            Dict[str, Any]: 模拟数据
        """
        return await self._request(
            method="POST",
            endpoint="/generate",
            data={
                "merchant_id": merchant_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "industry": industry
            }
        )

class CashFlowClient(BaseServiceClient):
    """现金流预测服务客户端"""
    
    def __init__(self):
        super().__init__("cashflow-predictor")
        
    async def predict(
        self,
        merchant_id: str,
        historical_data: List[Dict[str, Any]],
        prediction_days: int = 30
    ) -> Dict[str, Any]:
        """预测现金流
        
        Args:
            merchant_id: 商户ID
            historical_data: 历史数据
            prediction_days: 预测天数
            
        Returns:
            Dict[str, Any]: 预测结果
        """
        return await self._request(
            method="POST",
            endpoint="/predict",
            data={
                "merchant_id": merchant_id,
                "historical_data": historical_data,
                "prediction_days": prediction_days
            }
        )

class CostAnalysisClient(BaseServiceClient):
    """成本分析服务客户端"""
    
    def __init__(self):
        super().__init__("cost-analyzer")
        
    async def analyze(
        self,
        merchant_id: str,
        cost_data: List[Dict[str, Any]],
        industry: str
    ) -> Dict[str, Any]:
        """分析成本
        
        Args:
            merchant_id: 商户ID
            cost_data: 成本数据
            industry: 行业类型
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        return await self._request(
            method="POST",
            endpoint="/analyze",
            data={
                "merchant_id": merchant_id,
                "cost_data": cost_data,
                "industry": industry
            }
        )

class ComplianceClient(BaseServiceClient):
    """合规检查服务客户端"""
    
    def __init__(self):
        super().__init__("compliance-checker")
        
    async def check(
        self,
        merchant_id: str,
        profile: Dict[str, Any],
        compliance_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """检查合规性
        
        Args:
            merchant_id: 商户ID
            profile: 商户信息
            compliance_records: 合规记录
            
        Returns:
            Dict[str, Any]: 检查结果
        """
        return await self._request(
            method="POST",
            endpoint="/check",
            data={
                "merchant_id": merchant_id,
                "profile": profile,
                "compliance_records": compliance_records
            }
        ) 