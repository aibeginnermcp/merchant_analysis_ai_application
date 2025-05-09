"""数据模拟服务配置"""
from typing import Dict, Any
from pydantic import BaseSettings

class SimulatorConfig(BaseSettings):
    """数据模拟服务配置类"""
    
    # 服务配置
    SERVICE_NAME: str = "data-simulator"
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8001
    DEBUG: bool = False
    
    # MongoDB配置
    MONGODB_URL: str = "mongodb://mongodb:27017"
    MONGODB_DB: str = "merchant_analysis"
    MONGODB_COLLECTION: str = "simulated_data"
    
    # Redis配置
    REDIS_URL: str = "redis://redis:6379"
    REDIS_DB: int = 0
    
    # 数据生成配置
    MAX_HISTORY_DAYS: int = 365
    DEFAULT_BATCH_SIZE: int = 100
    
    # 行业模式配置
    INDUSTRY_PATTERNS: Dict[str, Dict[str, Any]] = {
        "restaurant": {
            "revenue_range": (2000, 20000),
            "peak_hours": [11, 12, 13, 17, 18, 19],
            "cost_ratios": {
                "raw_material": (0.3, 0.4),
                "labor": (0.2, 0.3),
                "utility": (0.05, 0.1),
                "rent": (0.1, 0.15),
                "marketing": (0.05, 0.08),
                "logistics": (0.02, 0.05)
            },
            "payment_methods": ["CASH", "CARD", "ALIPAY", "WECHAT"],
            "channels": {
                "dine_in": 0.6,
                "takeaway": 0.3,
                "delivery": 0.1
            }
        },
        "retail": {
            "revenue_range": (5000, 50000),
            "peak_hours": [14, 15, 16, 17, 18, 19],
            "cost_ratios": {
                "raw_material": (0.5, 0.6),
                "labor": (0.1, 0.2),
                "utility": (0.03, 0.07),
                "rent": (0.08, 0.12),
                "marketing": (0.05, 0.1),
                "logistics": (0.03, 0.06)
            },
            "payment_methods": ["CARD", "ALIPAY", "WECHAT"],
            "channels": {
                "offline": 0.7,
                "online": 0.3
            }
        },
        "ecommerce": {
            "revenue_range": (10000, 100000),
            "peak_hours": [10, 11, 14, 15, 20, 21],
            "cost_ratios": {
                "raw_material": (0.6, 0.7),
                "labor": (0.05, 0.1),
                "utility": (0.02, 0.05),
                "rent": (0.05, 0.08),
                "marketing": (0.1, 0.15),
                "logistics": (0.08, 0.12)
            },
            "payment_methods": ["ALIPAY", "WECHAT"],
            "channels": {
                "app": 0.5,
                "web": 0.3,
                "mini_program": 0.2
            }
        },
        "service": {
            "revenue_range": (3000, 30000),
            "peak_hours": [9, 10, 14, 15, 16, 17],
            "cost_ratios": {
                "raw_material": (0.2, 0.3),
                "labor": (0.3, 0.4),
                "utility": (0.05, 0.1),
                "rent": (0.1, 0.15),
                "marketing": (0.05, 0.1),
                "logistics": (0.01, 0.03)
            },
            "payment_methods": ["CARD", "ALIPAY", "WECHAT"],
            "channels": {
                "offline": 0.8,
                "online": 0.2
            }
        }
    }
    
    # 营销活动配置
    MARKETING_PATTERNS: Dict[str, Dict[str, Any]] = {
        "discount": {
            "probability": 0.4,
            "discount_range": (0.7, 0.95)
        },
        "cashback": {
            "probability": 0.3,
            "amount_range": (10, 100)
        },
        "gift": {
            "probability": 0.2,
            "value_range": (20, 200)
        },
        "points": {
            "probability": 0.1,
            "points_range": (100, 1000)
        }
    }
    
    # 合规检查配置
    COMPLIANCE_PATTERNS: Dict[str, Dict[str, Any]] = {
        "regular_inspection": {
            "frequency": 90,  # 天
            "pass_rate": 0.95
        },
        "random_inspection": {
            "probability": 0.01,  # 每天概率
            "pass_rate": 0.9
        },
        "violation_handling": {
            "resolution_time": {
                "min": 3,  # 天
                "max": 30
            },
            "fine_range": (1000, 10000)
        }
    }
    
    # 数据质量控制
    DATA_QUALITY: Dict[str, Any] = {
        "missing_rate": 0.01,
        "anomaly_rate": 0.02,
        "validation_rules": {
            "min_revenue": 0,
            "max_revenue": 1000000,
            "min_transaction_count": 0,
            "max_transaction_count": 10000
        }
    }
    
    class Config:
        env_file = ".env" 