"""
配置管理模块

用于统一管理所有服务的配置信息，包括：
- 数据库配置
- 缓存配置
- 服务发现配置
- 日志配置
- 安全配置
"""

import os
from typing import Dict, Any, Optional, List
from pydantic import BaseSettings, Field, validator
from functools import lru_cache
import json

class BaseConfig(BaseSettings):
    """基础配置类"""
    
    # 环境配置
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    DEBUG: bool = Field(False, env="DEBUG")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    
    # 服务配置
    SERVICE_NAME: str = Field(..., env="SERVICE_NAME")
    SERVICE_HOST: str = Field("0.0.0.0", env="SERVICE_HOST")
    SERVICE_PORT: int = Field(8000, env="SERVICE_PORT")
    
    # MongoDB配置
    MONGODB_URI: str = Field(..., env="MONGODB_URI")
    MONGODB_DATABASE: str = Field(..., env="MONGODB_DATABASE")
    MONGODB_USERNAME: Optional[str] = Field(None, env="MONGODB_USERNAME")
    MONGODB_PASSWORD: Optional[str] = Field(None, env="MONGODB_PASSWORD")
    MONGODB_REPLICA_SET: Optional[str] = Field(None, env="MONGODB_REPLICA_SET")
    
    # Redis配置
    REDIS_URI: str = Field(..., env="REDIS_URI")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    
    # JWT配置
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_EXPIRES_IN: int = Field(3600, env="JWT_EXPIRES_IN")
    
    # 服务发现配置
    CONSUL_HOST: str = Field("localhost", env="CONSUL_HOST")
    CONSUL_PORT: int = Field(8500, env="CONSUL_PORT")
    
    # 监控配置
    PROMETHEUS_PUSHGATEWAY: Optional[str] = Field(None, env="PROMETHEUS_PUSHGATEWAY")
    JAEGER_AGENT_HOST: str = Field("localhost", env="JAEGER_AGENT_HOST")
    JAEGER_AGENT_PORT: int = Field(6831, env="JAEGER_AGENT_PORT")
    
    # 日志配置
    ELASTICSEARCH_HOSTS: List[str] = Field(default_factory=list)
    KIBANA_HOST: Optional[str] = Field(None, env="KIBANA_HOST")
    
    @validator("ELASTICSEARCH_HOSTS", pre=True)
    def parse_elasticsearch_hosts(cls, v: Any) -> List[str]:
        """解析Elasticsearch主机配置
        
        Args:
            v: 配置值
            
        Returns:
            List[str]: 主机列表
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    
    class Config:
        env_file = ".env.dev"

class TestingConfig(BaseConfig):
    """测试环境配置"""
    
    class Config:
        env_file = ".env.test"

class ProductionConfig(BaseConfig):
    """生产环境配置"""
    
    class Config:
        env_file = ".env.prod"

class DataSimulatorConfig(BaseConfig):
    """数据模拟服务配置"""
    
    # 模拟数据配置
    SIMULATION_BATCH_SIZE: int = Field(1000, env="SIMULATION_BATCH_SIZE")
    SIMULATION_THREADS: int = Field(4, env="SIMULATION_THREADS")
    
    class Config:
        env_prefix = "DATA_SIMULATOR_"

class CashFlowConfig(BaseConfig):
    """现金流预测服务配置"""
    
    # 模型配置
    MODEL_PATH: str = Field(..., env="MODEL_PATH")
    PREDICTION_WINDOW: int = Field(30, env="PREDICTION_WINDOW")
    CONFIDENCE_THRESHOLD: float = Field(0.8, env="CONFIDENCE_THRESHOLD")
    
    class Config:
        env_prefix = "CASHFLOW_"

class CostAnalyzerConfig(BaseConfig):
    """成本分析服务配置"""
    
    # 分析配置
    ANALYSIS_THREADS: int = Field(4, env="ANALYSIS_THREADS")
    COST_CATEGORIES: List[str] = Field(default_factory=list)
    
    @validator("COST_CATEGORIES", pre=True)
    def parse_cost_categories(cls, v: Any) -> List[str]:
        """解析成本类别配置
        
        Args:
            v: 配置值
            
        Returns:
            List[str]: 成本类别列表
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v.split(",")
        return v
    
    class Config:
        env_prefix = "COST_ANALYZER_"

class ComplianceConfig(BaseConfig):
    """合规检查服务配置"""
    
    # 规则配置
    RULES_PATH: str = Field(..., env="RULES_PATH")
    UPDATE_INTERVAL: int = Field(3600, env="UPDATE_INTERVAL")
    
    class Config:
        env_prefix = "COMPLIANCE_"

@lru_cache()
def get_config() -> BaseConfig:
    """获取配置实例
    
    Returns:
        BaseConfig: 配置实例
    """
    env = os.getenv("ENVIRONMENT", "development")
    config_class = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig
    }.get(env.lower(), DevelopmentConfig)
    
    return config_class()

@lru_cache()
def get_service_config(service_name: str) -> BaseConfig:
    """获取服务配置实例
    
    Args:
        service_name: 服务名称
        
    Returns:
        BaseConfig: 服务配置实例
    """
    config_class = {
        "data-simulator": DataSimulatorConfig,
        "cashflow": CashFlowConfig,
        "cost-analyzer": CostAnalyzerConfig,
        "compliance": ComplianceConfig
    }.get(service_name)
    
    if not config_class:
        return get_config()
        
    return config_class()

# 导出配置实例
settings = get_config()

# 响应状态码
class StatusCode:
    """统一状态码定义"""
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503

# 错误消息
ERROR_MESSAGES = {
    StatusCode.BAD_REQUEST: "请求参数错误",
    StatusCode.UNAUTHORIZED: "未授权访问",
    StatusCode.FORBIDDEN: "禁止访问",
    StatusCode.NOT_FOUND: "资源不存在",
    StatusCode.INTERNAL_ERROR: "服务器内部错误",
    StatusCode.SERVICE_UNAVAILABLE: "服务不可用"
}

# 分析类型
ANALYSIS_TYPES = {
    "compliance": "合规检查",
    "cost": "成本分析",
    "cashflow": "现金流预测",
    "simulation": "数据模拟"
} 