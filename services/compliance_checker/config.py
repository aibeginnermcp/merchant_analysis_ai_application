"""
合规检查服务配置
"""
from typing import Dict, Any
from pydantic import BaseSettings

class Settings(BaseSettings):
    """服务配置类"""
    
    # 服务基本配置
    SERVICE_NAME: str = "compliance-service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API配置
    API_V1_PREFIX: str = "/api/v1"
    
    # 服务端口配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # MongoDB配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "compliance_service"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    
    # 规则引擎配置
    DEFAULT_RULE_TYPES: list = ["financial", "qualification", "risk"]
    RISK_LEVEL_WEIGHTS: Dict[str, float] = {
        "high": 1.0,
        "medium": 0.6,
        "low": 0.3
    }
    
    # 缓存配置
    CACHE_TTL: int = 3600  # 缓存过期时间(秒)
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        """配置元数据"""
        case_sensitive = True
        env_file = ".env"
        
# 创建全局配置实例
settings = Settings()

# 风险评分阈值
RISK_SCORE_THRESHOLDS = {
    "high_risk": 70,
    "medium_risk": 30
}

# 默认规则参数
DEFAULT_RULE_PARAMS = {
    "registered_capital": {
        "min_capital": 100000  # 最低注册资本
    },
    "business_scope": {
        "required_items": ["零售", "批发"]  # 必需经营范围
    },
    "establishment_period": {
        "min_years": 2  # 最短成立年限
    }
}

# API响应消息
RESPONSE_MESSAGES = {
    "rule_not_found": "规则不存在",
    "rule_creation_failed": "创建规则失败",
    "check_failed": "合规检查失败",
    "invalid_rule_type": "无效的规则类型",
    "invalid_parameters": "无效的规则参数"
} 