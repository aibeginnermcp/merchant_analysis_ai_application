"""
餐饮行业配置文件
包含餐饮行业特有的业务参数和规则配置
"""

from .base_config import TIME_CONFIG, VOLUME_CONFIG, USER_ATTRIBUTES

# 餐厅类型配置
RESTAURANT_TYPE_CONFIG = {
    'type_distribution': {
        'fast_food': 0.3,      # 快餐店
        'casual_dining': 0.4,  # 休闲餐厅
        'fine_dining': 0.2,    # 高档餐厅
        'buffet': 0.1         # 自助餐厅
    },
    'price_level': {
        'fast_food': {
            'low': {'min': 20, 'max': 50},
            'medium': {'min': 30, 'max': 80},
            'high': {'min': 40, 'max': 100}
        },
        'casual_dining': {
            'low': {'min': 50, 'max': 100},
            'medium': {'min': 80, 'max': 150},
            'high': {'min': 100, 'max': 200}
        },
        'fine_dining': {
            'low': {'min': 150, 'max': 300},
            'medium': {'min': 250, 'max': 500},
            'high': {'min': 400, 'max': 800}
        },
        'buffet': {
            'low': {'min': 80, 'max': 120},
            'medium': {'min': 120, 'max': 200},
            'high': {'min': 180, 'max': 300}
        }
    }
}

# 菜品配置
DISH_CONFIG = {
    'categories': {
        'appetizer': {'weight': 0.2, 'avg_price_multiplier': 0.6},
        'main_course': {'weight': 0.4, 'avg_price_multiplier': 1.0},
        'dessert': {'weight': 0.15, 'avg_price_multiplier': 0.5},
        'beverage': {'weight': 0.15, 'avg_price_multiplier': 0.3},
        'special': {'weight': 0.1, 'avg_price_multiplier': 1.2}
    },
    'combo_probability': 0.3,  # 套餐概率
    'combo_discount': 0.85,    # 套餐折扣
    'special_requirement_probability': 0.2  # 特殊要求概率
}

# 用餐时长配置（分钟）
DINING_DURATION_CONFIG = {
    'fast_food': {'min': 15, 'max': 45},
    'casual_dining': {'min': 45, 'max': 90},
    'fine_dining': {'min': 60, 'max': 150},
    'buffet': {'min': 60, 'max': 120}
}

# 促销活动配置
PROMOTION_CONFIG = {
    'types': {
        'discount': {'probability': 0.4, 'avg_discount': 0.85},
        'cash_off': {'probability': 0.3, 'avg_amount': 20},
        'free_dish': {'probability': 0.2, 'max_value': 30},
        'member_exclusive': {'probability': 0.1, 'extra_discount': 0.95}
    },
    'seasonal_factors': {
        'spring_festival': {'multiplier': 1.5, 'duration': 15},
        'national_day': {'multiplier': 1.3, 'duration': 7},
        'summer_holiday': {'multiplier': 1.2, 'duration': 30}
    }
}

# 服务质量配置
SERVICE_QUALITY_CONFIG = {
    'rating_weights': {
        'food_taste': 0.4,
        'service_attitude': 0.3,
        'environment': 0.2,
        'price_performance': 0.1
    },
    'rating_distribution': {
        5: 0.3,
        4: 0.4,
        3: 0.2,
        2: 0.07,
        1: 0.03
    },
    'complaint_types': {
        'food_quality': 0.35,
        'service_attitude': 0.25,
        'waiting_time': 0.2,
        'environment': 0.1,
        'price': 0.1
    },
    'resolution_time': {
        'immediate': {
            'time': 15,
            'probability': 0.3
        },
        'quick': {
            'time': 30,
            'probability': 0.4
        },
        'normal': {
            'time': 60,
            'probability': 0.2
        },
        'delayed': {
            'time': 120,
            'probability': 0.1
        }
    }
}

# 外卖配置
DELIVERY_CONFIG = {
    'platforms': {
        'meituan': 0.45,
        'eleme': 0.35,
        'own_platform': 0.2
    },
    'delivery_fee': {
        'base_fee': 5.0,
        'distance_fee': 1.0,  # 每公里加价
        'peak_hour_multiplier': 1.5
    },
    'delivery_time': {
        'normal': {
            'min': 30,
            'max': 45
        },
        'peak_hour': {
            'min': 45,
            'max': 60
        },
        'bad_weather': {
            'min': 50,
            'max': 75
        }
    },
    'commission_rate': {
        'meituan': 0.18,
        'eleme': 0.18,
        'own_platform': 0.05
    }
}

# 营业时间配置
BUSINESS_HOURS_CONFIG = {
    'fast_food': {
        'all_day': {'start': '10:00', 'end': '22:00'}
    },
    'casual_dining': {
        'lunch': {'start': '11:00', 'end': '14:00'},
        'dinner': {'start': '17:00', 'end': '21:30'}
    },
    'fine_dining': {
        'lunch': {'start': '11:30', 'end': '14:30'},
        'dinner': {'start': '17:30', 'end': '22:00'}
    },
    'buffet': {
        'lunch': {'start': '11:30', 'end': '14:00'},
        'dinner': {'start': '17:30', 'end': '21:30'}
    }
}

# 会员体系配置
MEMBERSHIP_CONFIG = {
    'levels': {
        'bronze': {
            'spending_threshold': 0,
            'discount': 0.98,
            'point_rate': 1
        },
        'silver': {
            'spending_threshold': 2000,
            'discount': 0.95,
            'point_rate': 1.2
        },
        'gold': {
            'spending_threshold': 5000,
            'discount': 0.92,
            'point_rate': 1.5
        },
        'platinum': {
            'spending_threshold': 20000,
            'discount': 0.88,
            'point_rate': 2.0
        }
    },
    'points_system': {
        'exchange_rate': 100,  # 100积分=1元
        'expiration': 365     # 积分有效期（天）
    }
} 