"""
from typing import Dict, Any
from pydantic import BaseSettings

class BaseConfig(BaseSettings):
    """基础配置类"""
    
    # 服务配置
    SERVICE_NAME: str = "cost-analysis-service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API配置
    API_PREFIX: str = "/api/v1"
    API_TITLE: str = "成本穿透分析服务"
    API_DESCRIPTION: str = "提供商户成本结构分析、趋势分析、预警和优化建议等功能"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # 数据库配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "cost_analysis"
    MONGODB_TIMEOUT: int = 5000
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    REDIS_TIMEOUT: int = 3000
    
    # 缓存配置
    CACHE_TTL: int = 3600  # 1小时
    CACHE_PREFIX: str = "cost_analysis:"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    
    # CORS配置
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # 监控配置
    METRICS_ENABLED: bool = True
    METRICS_PATH: str = "/metrics"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "logs/cost_analysis.log"
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"
    
    # 业务配置
    DEFAULT_ANALYSIS_TYPES: list = ["structure", "trend"]
    DEFAULT_GRANULARITY: str = "monthly"
    MAX_SIMULATION_SCENARIOS: int = 5
    COST_ALERT_THRESHOLD: float = 0.1  # 10%
    
    class Config:
        env_prefix = "COST_ANALYSIS_"
        case_sensitive = False

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """获取配置字典"""
        return cls().dict()
""" 