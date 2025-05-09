"""
数据库连接管理模块
"""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from src.shared.config import settings

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        """初始化数据库管理器"""
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None
        
    async def connect(self):
        """连接数据库"""
        try:
            self._client = AsyncIOMotorClient(settings.MONGODB_URI)
            self._db = self._client[settings.MONGODB_DB_NAME]
            # 验证连接
            await self._client.admin.command('ping')
            print("MongoDB连接成功")
        except ConnectionFailure as e:
            print(f"MongoDB连接失败: {e}")
            raise
            
    async def disconnect(self):
        """断开数据库连接"""
        if self._client:
            self._client.close()
            print("MongoDB连接已关闭")
            
    @property
    def db(self) -> AsyncIOMotorDatabase:
        """获取数据库实例
        
        Returns:
            AsyncIOMotorDatabase: 数据库实例
        """
        if not self._db:
            raise ConnectionError("数据库未连接")
        return self._db
        
    async def get_merchant_collection(self):
        """获取商户集合
        
        Returns:
            Collection: 商户集合
        """
        return self.db.merchants
        
    async def get_transaction_collection(self):
        """获取交易集合
        
        Returns:
            Collection: 交易集合
        """
        return self.db.transactions
        
    async def get_analysis_collection(self):
        """获取分析结果集合
        
        Returns:
            Collection: 分析结果集合
        """
        return self.db.analysis_results

# 创建全局数据库管理器实例
db_manager = DatabaseManager() 