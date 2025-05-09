"""
配置模块

管理现金流预测服务的配置项，包括：
- 服务配置
- 数据库配置
- 模型配置
- 预测配置
"""

import os
from typing import Dict, Any
from pydantic import BaseSettings

class BaseConfig(BaseSettings):
    """
    基础配置类
    
    管理所有配置项，支持从环境变量加载
    """
    
    # 服务配置
    SERVICE_NAME: str = "cashflow-predictor"
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8001
    DEBUG: bool = False
    
    # 数据库配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "merchant_analytics"
    MONGODB_USERNAME: str = ""
    MONGODB_PASSWORD: str = ""
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    
    # 模型配置
    MODEL_PATH: str = "models"
    DEFAULT_MODEL: str = "prophet"
    AVAILABLE_MODELS: list = ["prophet", "random_forest", "lstm"]
    
    # 预测配置
    MAX_PREDICTION_DAYS: int = 365
    DEFAULT_GRANULARITY: str = "daily"
    CONFIDENCE_LEVEL: float = 0.95
    
    # 特征配置
    FEATURE_COLUMNS: list = [
        "amount",
        "probability",
        "is_recurring",
        "year",
        "month",
        "day",
        "dayofweek",
        "quarter",
        "is_month_end",
        "is_month_start"
    ]
    
    # 缓存配置
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 1小时
    
    # 监控配置
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 8001
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 安全配置
    API_KEY_HEADER: str = "X-API-Key"
    JWT_SECRET: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        获取配置
        
        Returns:
            配置字典
        """
        return cls().dict()
        
class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
class TestingConfig(BaseConfig):
    """测试环境配置"""
    MONGODB_DB: str = "merchant_analytics_test"
    TESTING: bool = True
    
class ProductionConfig(BaseConfig):
    """生产环境配置"""
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    CACHE_TTL: int = 7200  # 2小时
    
# 环境配置映射
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}

def get_config() -> Dict[str, Any]:
    """
    获取当前环境的配置
    
    Returns:
        配置字典
    """
    env = os.getenv("FLASK_ENV", "development")
    config_class = config_by_name.get(env, DevelopmentConfig)
    return config_class().dict() 