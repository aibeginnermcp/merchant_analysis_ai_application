"""
数据模拟服务类，提供数据生成和查询的API接口
"""
import logging
import uuid
from typing import Dict, List, Optional, Union
import asyncio
from datetime import datetime

from services.data_simulator.models import (
    Transaction, 
    CostItem, 
    SimulationConfig, 
    SimulationResult,
    TimeRange,
    Merchant,
    MerchantType
)
from services.data_simulator.generator import DataGeneratorFactory
from services.data_simulator.storage import MongoDBStorage, BaseStorage

class DataSimulatorService:
    """数据模拟服务类"""
    
    def __init__(self, storage: Optional[BaseStorage] = None):
        """
        初始化服务
        
        Args:
            storage: 数据存储实例，如果为None则创建默认的MongoDB存储
        """
        self.logger = logging.getLogger("data_simulator.service")
        self.storage = storage or MongoDBStorage()
    
    async def simulate_data(self, config: SimulationConfig) -> SimulationResult:
        """
        模拟生成数据
        
        Args:
            config: 模拟配置
            
        Returns:
            模拟结果
        """
        self.logger.info(f"Simulating data for merchant {config.merchant.merchant_id}")
        
        # 保存商户信息
        await self.storage.save_merchant(config.merchant)
        
        # 创建适合的生成器
        generator = DataGeneratorFactory.create_generator(config)
        
        # 运行模拟
        result = generator.run_simulation()
        
        # 保存模拟结果
        simulation_id = await self.storage.save_simulation_result(result)
        self.logger.info(f"Simulation completed with ID: {simulation_id}")
        
        return result
    
    async def get_transactions(self, merchant_id: str, time_range: TimeRange) -> List[Transaction]:
        """
        获取交易数据
        
        Args:
            merchant_id: 商户ID
            time_range: 时间范围
            
        Returns:
            交易记录列表
        """
        self.logger.info(f"Getting transactions for merchant {merchant_id}")
        return await self.storage.get_transactions(merchant_id, time_range)
    
    async def get_costs(self, merchant_id: str, time_range: TimeRange) -> List[CostItem]:
        """
        获取成本数据
        
        Args:
            merchant_id: 商户ID
            time_range: 时间范围
            
        Returns:
            成本记录列表
        """
        self.logger.info(f"Getting costs for merchant {merchant_id}")
        return await self.storage.get_costs(merchant_id, time_range)
    
    async def get_merchant(self, merchant_id: str) -> Optional[Merchant]:
        """
        获取商户信息
        
        Args:
            merchant_id: 商户ID
            
        Returns:
            商户信息，如果不存在则返回None
        """
        return await self.storage.get_merchant(merchant_id)
    
    async def create_merchant(self, 
                             merchant_name: str, 
                             merchant_type: MerchantType, 
                             business_scale: str = "medium",
                             established_date: Optional[str] = None) -> Merchant:
        """
        创建新商户
        
        Args:
            merchant_name: 商户名称
            merchant_type: 商户类型
            business_scale: 业务规模
            established_date: 成立日期，格式：YYYY-MM-DD
            
        Returns:
            创建的商户信息
        """
        merchant_id = f"m_{uuid.uuid4().hex[:8]}"
        
        if established_date is None:
            established_date = "2010-01-01"  # 默认成立日期
        
        merchant = Merchant(
            merchant_id=merchant_id,
            merchant_name=merchant_name,
            merchant_type=merchant_type,
            business_scale=business_scale,
            established_date=established_date
        )
        
        await self.storage.save_merchant(merchant)
        self.logger.info(f"Created new merchant: {merchant_id}")
        
        return merchant
    
    async def simulate_for_all_merchants(self, time_range: TimeRange) -> Dict[str, str]:
        """
        为所有商户生成模拟数据
        
        Args:
            time_range: 时间范围
            
        Returns:
            商户ID到模拟ID的映射
        """
        # 这里假设已经有了获取所有商户ID的方法
        # 在实际实现中需要添加这个方法
        merchant_ids = await self._get_all_merchant_ids()
        
        results = {}
        for merchant_id in merchant_ids:
            merchant = await self.get_merchant(merchant_id)
            if merchant:
                config = SimulationConfig(
                    merchant=merchant,
                    time_range=time_range
                )
                result = await self.simulate_data(config)
                results[merchant_id] = result.merchant_id
                
        return results
        
    async def _get_all_merchant_ids(self) -> List[str]:
        """
        获取所有商户ID
        
        Returns:
            商户ID列表
        """
        # 这只是一个示例实现，实际上需要从数据库获取
        # 这里可以添加存储实现
        return [] 